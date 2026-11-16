import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,mkdtemp,mkdir,copyFile,cp,rm} from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {registerHooks} from 'node:module';
import {packet,moduleURL,methodMessages} from './fixtures/liuren-adjudication-v2.mjs';
const ROOT=fileURLToPath(new URL('../../',import.meta.url));
registerHooks({resolve(specifier,context,next){
 if(specifier==='@opencode-ai/plugin')return next(pathToFileURL(path.join(ROOT,'.opencode/node_modules/@opencode-ai/plugin/dist/index.js')).href,context);
 return next(specifier,context);
}});
const {tool}=await import('@opencode-ai/plugin');const s=tool.schema;
const {createComputeSchemas,CALENDAR_EXAMPLE}=await import(moduleURL('tools/liuren-compute-schema.mjs'));
const {calendar}=await import(moduleURL('tools/liuren-deterministic-calendar.mjs'));
const {default:plugin}=await import(moduleURL('.opencode/plugins/liuren-adjudication.ts'));
const schemas=createComputeSchemas(s);
const native=await plugin({directory:ROOT,client:{session:{get:async()=>{throw new Error('calendar must not request a model session');}}}});
const base=structuredClone(CALENDAR_EXAMPLE.calendar);

test('archive schema accepts complete chart references while rejecting unrelated or malformed fields',()=>{
 const archive={path:'C:/test/chart.json',sha256:'a'.repeat(64),raw_sha256:'b'.repeat(64)};
 assert.deepEqual(schemas.parse({action:'chart',archive}).archive,archive);
 assert.deepEqual(schemas.parse({action:'life',archive,life:{age:21,sex:'女',age_basis:'虚岁-已核'}}).archive,archive);
 assert.throws(()=>schemas.parse({action:'chart',archive:{...archive,raw_sha256:'wrong'}}),/raw_sha256/);
 assert.throws(()=>schemas.parse({action:'chart',archive:{...archive,unknown:true}}),/Unrecognized key/);
});

test('wire JSON Schema exposes every calendar key, requirement and exact boundary enum',()=>{
 const json=s.toJSONSchema(s.object(native.tool.liuren_compute.args));
 const c=json.properties.calendar;
 assert.equal(c.type,'object');assert.deepEqual(c.required,['start','end','timezone','day_boundary']);
 assert.deepEqual(c.properties.day_boundary.enum,['civil-midnight','zi-hour']);
 assert.equal(c.properties.timezone.const,'Asia/Shanghai');assert.equal(c.additionalProperties,false);
 assert.match(c.description,/最小调用/);assert.match(native.tool.liuren_compute.description,/civil-midnight/);
 assert.ok(JSON.stringify(json).length<18000,'recursive expression schema must stay compact');
});

test('quantity expression exposes node syntax and validates nested expressions during execution',()=>{
 const json=s.toJSONSchema(s.object(native.tool.liuren_compute.args));
 assert.ok(JSON.stringify(json).includes('"multiply"'));assert.ok(JSON.stringify(json).includes('"sheng"'));
 const expression={op:'multiply',args:[{table:'branch',symbol:'丑'},{op:'add',args:[{value:3},{value:3}]}]};
 assert.deepEqual(schemas.parse({action:'quantity',expression}).expression,expression);
 assert.throws(()=>schemas.parse({action:'quantity',expression:{formula:'8*6'}}),/expression/);
});

test('all three observed calendar failures are rejected with legal spelling and a complete example',async()=>{
 const failures=JSON.parse(await readFile(path.join(ROOT,'output/liuren-compute-interface-20261106/observed-calendar-failures.json'),'utf8')).calls;
 assert.equal(failures.length,3);
 for(const call of failures){
  assert.throws(()=>schemas.parse(call.input),e=>/calendar.day_boundary/.test(e.message)&&/civil-midnight/.test(e.message)&&/最小调用/.test(e.message));
  await assert.rejects(()=>native.tool.liuren_compute.execute(call.input,{agent:'liuren',sessionID:'schema-regression'}),e=>/calendar.day_boundary/.test(e.message)&&/zi-hour/.test(e.message));
  assert.throws(()=>calendar(call.input.calendar),e=>/calendar.day_boundary/.test(e.message)&&/civil-midnight/.test(e.message));
 }
});

test('corrected screenshot call succeeds through the native tool with schema parsing',async()=>{
 const args=s.object(native.tool.liuren_compute.args).parse(CALENDAR_EXAMPLE);
 const output=JSON.parse(await native.tool.liuren_compute.execute(args,{agent:'liuren',sessionID:'calendar-regression'}));
 assert.equal(output.rows.length,22);assert.equal(output.rows[0].date,'2024-01-15');assert.equal(output.rows[0].day,'戊寅');
 assert.equal(output.rows.at(-1).date,'2024-02-05');assert.equal(output.rows.at(-1).day,'己亥');
 assert.equal(output.query.day_boundary,'civil-midnight');
});

test('both explicit boundaries work without silently changing the requested convention',async()=>{
 for(const [day_boundary,day] of [['civil-midnight','辛巳'],['zi-hour','壬午']]){
  const args={action:'calendar',calendar:{...base,start:'2026-11-03',end:'2026-11-03',hour:23,day_boundary}};
  const output=JSON.parse(await native.tool.liuren_compute.execute(args,{agent:'liuren',sessionID:'boundary-regression'}));
  assert.equal(output.rows[0].day,day);assert.equal(output.query.day_boundary,day_boundary);
 }
});

test('wrong field names, an absent action payload, and irrelevant payloads cannot be silently ignored',async()=>{
 for(const input of [{action:'calendar'},{action:'quantity'},{action:'calendar',calendar:{...base,start_date:base.start}},
  {action:'calendar',calendar:base,lookup:{subject:'丑'}},{action:'calendar',calendar:base,archive:{path:'ignored',sha256:'ignored'}}]){
  assert.throws(()=>schemas.parse(input),/LIUREN_COMPUTE_ARGUMENTS/);
 }
 assert.throws(()=>calendar({...base,start_date:base.start}),/calendar.start_date/);
});

test('direct and packet requests share the same visible calendar schema',()=>{
 const p=packet();p.computation_requests=[{id:'C_date',...structuredClone(CALENDAR_EXAMPLE)}];
 const parsed=native.tool.liuren_adjudication_packet.args.packet.parse(p);
 assert.deepEqual(parsed.computation_requests,p.computation_requests);
 delete p.computation_requests[0].calendar.day_boundary;
 assert.throws(()=>native.tool.liuren_adjudication_packet.args.packet.parse(p),/day_boundary/);
 const json=s.toJSONSchema(native.tool.liuren_adjudication_packet.args.packet);
 assert.ok(JSON.stringify(json.properties.computation_requests).includes('calendar')||json.$defs);
});

test('calendar JSON syntax errors do not lead to hand calculation or implicit defaults',()=>{
 assert.throws(()=>calendar({...base,day_boundary:'midnight'}),/expected string "civil-midnight" or "zi-hour"/);
 assert.throws(()=>calendar({...base,day_boundary:undefined}),/day_boundary/);
 assert.throws(()=>calendar({...base,timezone:'UTC'}),/calendar.timezone/);
 assert.throws(()=>calendar({...base,start:'2024-02-30'}),/calendar.start/);
 assert.throws(()=>calendar({...base,pillars:[null]}),/invalid branch\/pillar/);
});

test('native quantity computation still uses the exact expression schema and arithmetic',async()=>{
 const request={action:'quantity',expression:{op:'multiply',args:[{table:'branch',symbol:'丑'},{value:6}]}};
 const output=JSON.parse(await native.tool.liuren_compute.execute(schemas.parse(request),{agent:'liuren',sessionID:'quantity-regression'}));
 assert.equal(output.value,48);assert.deepEqual(output.exact_fraction,{numerator:'48',denominator:'1'});
});

test('native source loads a verified active runtime method without fabricated line boundaries',async()=>{
 const active=JSON.parse(await readFile(path.join(ROOT,'.opencode/liuren-active.json'),'utf8'));
 const args=s.object(native.tool.liuren_compute.args).parse({action:'source',source:{id:'M_NATIVE',title:'完整应期方法',source_path:active.runtime+'/methods/timing.md'}});
 const output=JSON.parse(await native.tool.liuren_compute.execute(args,{agent:'liuren',sessionID:'source-regression'}));
 assert.equal(output.line_start,1);assert.ok(output.quote.includes('竞争轮次'));
 assert.equal(output.quote.trim(),(await readFile(path.join(ROOT,active.runtime,'methods/timing.md'),'utf8')).replaceAll('\r\n','\n').trim());
});

test('bound child can call the same calendar tool without an archive or a new model call',async t=>{
 const temp=await mkdtemp(path.join(os.tmpdir(),'liuren-calendar-child-'));
 t.after(async()=>{assert.equal(path.dirname(path.resolve(temp)),path.resolve(os.tmpdir()));await rm(temp,{recursive:true,force:true});});
 const active=JSON.parse(await readFile(path.join(ROOT,'.opencode/liuren-active.json'),'utf8'));
 const registry=JSON.parse(await readFile(path.join(ROOT,'tools/liuren-method-registry.json'),'utf8'));
 const bookPaths=[...new Set([...registry.quantity,...registry.imagery].map(m=>m.source.path))];
 for(const rel of ['.opencode/liuren-active.json','tools/liuren-direct/legacy-engine-manifest.json','排盘工具魔改/js/lunar.js',active.runtime+'/manifest.json',active.runtime+'/references/shensha-policy.json',active.runtime+'/references/judgment-core.md',active.runtime+'/domains/finance.md',...bookPaths]){
  const dst=path.join(temp,rel);await mkdir(path.dirname(dst),{recursive:true});await copyFile(path.join(ROOT,rel),dst);
 }
  await cp(path.join(ROOT,active.runtime),path.join(temp,active.runtime),{recursive:true});
 const {runResolvedChart}=await import('../liuren-resolved-chart.mjs');
 const chart=await runResolvedChart({datetime:'2026-10-18T13:22'},{persist:false});
 const p=packet();p.chart={source:'program chart for interface regression',facts:chart.facts};p.questions[0].tasks=['outcome'];p.entities[0].branch='丑';delete p.entities[0].position;
 p.questions[0].task_basis=[{task:'outcome',origin:'user_requested',request_quote:'合成接口问题',reason:'合成原问'}];
 let prompt;
 active.eventPositioning={enabled:false};active.consistencyAudit={enabled:false};await (await import('node:fs/promises')).writeFile(path.join(temp,'.opencode/liuren-active.json'),JSON.stringify(active));
 const hooks=await plugin({directory:temp,client:{session:{get:async()=>({data:{parentID:'parent'}}),messages:async({path:{id}})=>({data:id==='parent'?await methodMessages(ROOT):[{info:{role:'user'},parts:[{type:'text',text:prompt}]}]})}}});
 const saved=JSON.parse(await hooks.tool.liuren_adjudication_packet.execute({packet:p},{agent:'liuren',sessionID:'parent'}));prompt=saved.task_prompt;
 await hooks['tool.execute.before']({tool:'task',sessionID:'parent',callID:'calendar-child'},{args:{subagent_type:'liuren-adjudicator',prompt}});
 const first=JSON.parse(await hooks.tool.liuren_adjudication_read.execute({file_path:saved.file_path,sha256:saved.sha256,page:1},{agent:'liuren-adjudicator',sessionID:'child'}));
 for(let page=2;page<=first.pages;page++)await hooks.tool.liuren_adjudication_read.execute({file_path:saved.file_path,sha256:saved.sha256,page},{agent:'liuren-adjudicator',sessionID:'child'});
 const output=JSON.parse(await hooks.tool.liuren_compute.execute(CALENDAR_EXAMPLE,{agent:'liuren-adjudicator',sessionID:'child'}));
 assert.equal(output.rows.length,22);assert.equal(output.rows[0].day,'戊寅');
  const strengthRequest={action:'strength',strength:{mode:'selected_relations',season_profile:'quarter-earth',season_basis:'合成工具传输固定口径',review:true,
  actors:[{id:'T:酉',role:'假设助方',basis:'传输测试指定'},{id:'T:子',role:'假设类神',basis:'传输测试指定'}],
  links:[{source:'T:酉',target:'T:子',basis:'传输测试假设金生水，不是实际占断'}]}};
  const parsedStrength=schemas.parse(strengthRequest);
  const strengthResult=JSON.parse(await hooks.tool.liuren_compute.execute(parsedStrength,{agent:'liuren-adjudicator',sessionID:'child'}));
 const {compute}=await import('../liuren-deterministic-io.mjs');
 const {loadPacket}=await import('../liuren-adjudication-files.mjs');
 const bound=await loadPacket(temp,{file_path:saved.file_path,sha256:saved.sha256});
  assert.deepEqual(strengthResult,compute(parsedStrength,bound.envelope.packet.chart.facts));
 assert.equal(strengthResult.scope,'selected_relations');
  assert.equal(strengthResult.review.schema,'liuren-strength-review-v1');
 const catalogue=JSON.parse(await hooks.tool.liuren_compute.execute({action:'methods',methods:{kind:'quantity'}},{agent:'liuren-adjudicator',sessionID:'child'}));
  assert.equal(catalogue.methods.length,5);assert.ok(catalogue.methods.some(x=>x.id==='LF3329-class-ground'));
 const methodRequest={action:'quantity',quantity_method:{id:'WY67-shenjiang-base',target:'T:'+chart.facts.transmissions[0].diZhi,basis:'合成传输验证，非数量预测'}};
 const quantity=JSON.parse(await hooks.tool.liuren_compute.execute(methodRequest,{agent:'liuren-adjudicator',sessionID:'child'}));
 assert.deepEqual(quantity,compute(methodRequest,chart.facts,{root:ROOT}));assert.equal(quantity.stage,'base-only');
 const imageryRequest={action:'imagery',imagery:{id:'DF449-growth',target:methodRequest.quantity_method.target,reference:'ground',basis:'合成传输验证'}};
 assert.deepEqual(JSON.parse(await hooks.tool.liuren_compute.execute(imageryRequest,{agent:'liuren-adjudicator',sessionID:'child'})),compute(imageryRequest,chart.facts,{root:ROOT}));
 const evaluationRequest={action:'evaluation',evaluation:{calendar:{...base,start:'2026-10-18',end:'2026-10-18'},strength:{...strengthRequest.strength,mode:'single_palace',links:[]},void_policy:'original'}};
 const parsedEvaluation=schemas.parse(evaluationRequest);
 assert.deepEqual(JSON.parse(await hooks.tool.liuren_compute.execute(parsedEvaluation,{agent:'liuren-adjudicator',sessionID:'child'})),compute(parsedEvaluation,bound.envelope.packet.chart.facts,{root:ROOT}));
});

test('named method schema rejects mixed formulas and publishes all upgraded actions without broken refs',async()=>{
 const method={action:'quantity',quantity_method:{id:'WY244-month',target:'T:卯',number_table:'branch',basis:'示例'}};
 assert.equal(schemas.parse(method).quantity_method.id,'WY244-month');
 assert.throws(()=>schemas.parse({...method,expression:{value:8}}),/not used/);
 const result=JSON.parse(await native.tool.liuren_compute.execute({action:'methods',methods:{kind:'imagery'}},{agent:'liuren',sessionID:'method-main'}));
 assert.equal(result.methods.length,3);
 const json=s.toJSONSchema(s.object(native.tool.liuren_compute.args));
 for(const action of ['methods','imagery','evaluation'])assert.ok(json.properties.action.enum.includes(action));
 assert.ok(!JSON.stringify(json).includes('"$ref"'));
});

test('strength native schema exposes selected actors and basis without caller-assigned weights',()=>{
 const json=s.toJSONSchema(s.object(native.tool.liuren_compute.args));
 assert.ok(json.properties.action.enum.includes('strength'));
 assert.ok(json.properties.strength.required.includes('actors'));
 assert.equal(json.properties.strength.properties.links.items.additionalProperties,false);
 assert.throws(()=>schemas.parse({action:'strength'}),/strength/);
 assert.throws(()=>schemas.parse({action:'strength',strength:{mode:'single_palace',season_profile:'quarter-earth',season_basis:'test',actors:[{id:'T:子',role:'类神',basis:'测试'}],weight:2}}),/weight/);
});


test('packet wire schema requires a domain on every question and documents reusable source references',()=>{
 const json=s.toJSONSchema(native.tool.liuren_adjudication_packet.args.packet);
 assert.ok(json.properties.questions.items.required.includes('domain'));
 assert.ok(json.properties.questions.items.properties.domain.enum.includes('illness'));
 const p=packet();delete p.questions[0].domain;
 assert.throws(()=>native.tool.liuren_adjudication_packet.args.packet.parse(p),/domain/);
 assert.match(json.properties.method_materials.description,/handoff/);
 assert.match(s.toJSONSchema(s.object(native.tool.liuren_compute.args)).properties.source.description,/绝对路径/);
});
