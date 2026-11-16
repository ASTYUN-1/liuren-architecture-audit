import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile,mkdtemp,mkdir,copyFile,rm} from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {registerHooks} from 'node:module';
import {packet,moduleURL} from './fixtures/liuren-adjudication-v2.mjs';
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

test('wire JSON Schema exposes every calendar key, requirement and exact boundary enum',()=>{
 const json=s.toJSONSchema(s.object(native.tool.liuren_compute.args));
 const c=json.properties.calendar;
 assert.equal(c.type,'object');assert.deepEqual(c.required,['start','end','timezone','day_boundary']);
 assert.deepEqual(c.properties.day_boundary.enum,['civil-midnight','zi-hour']);
 assert.equal(c.properties.timezone.const,'Asia/Shanghai');assert.equal(c.additionalProperties,false);
 assert.match(c.description,/最小调用/);assert.match(native.tool.liuren_compute.description,/civil-midnight/);
 assert.ok(JSON.stringify(json).length<18000,'recursive expression schema must stay compact');
});

test('quantity expression is also a visible, recursive schema rather than an untyped hole',()=>{
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

test('bound child can call the same calendar tool without an archive or a new model call',async t=>{
 const temp=await mkdtemp(path.join(os.tmpdir(),'liuren-calendar-child-'));
 t.after(async()=>{assert.equal(path.dirname(path.resolve(temp)),path.resolve(os.tmpdir()));await rm(temp,{recursive:true,force:true});});
 const active=JSON.parse(await readFile(path.join(ROOT,'.opencode/liuren-active.json'),'utf8'));
 for(const rel of ['.opencode/liuren-active.json','tools/liuren-direct/legacy-engine-manifest.json','排盘工具魔改/js/lunar.js',active.runtime+'/manifest.json',active.runtime+'/references/shensha-policy.json']){
  const dst=path.join(temp,rel);await mkdir(path.dirname(dst),{recursive:true});await copyFile(path.join(ROOT,rel),dst);
 }
 const {runResolvedChart}=await import('../liuren-resolved-chart.mjs');
 const chart=await runResolvedChart({datetime:'2026-10-18T13:22'},{persist:false});
 const p=packet();p.chart={source:'program chart for interface regression',facts:chart.facts};p.questions[0].tasks=['outcome'];p.entities[0].branch='丑';delete p.entities[0].position;
 let prompt;
 const hooks=await plugin({directory:temp,client:{session:{get:async()=>({data:{parentID:'parent'}}),messages:async()=>({data:[{info:{role:'user'},parts:[{type:'text',text:prompt}]}]})}}});
 const saved=JSON.parse(await hooks.tool.liuren_adjudication_packet.execute({packet:p},{agent:'liuren',sessionID:'parent'}));prompt=saved.task_prompt;
 await hooks['tool.execute.before']({tool:'task',sessionID:'parent',callID:'calendar-child'},{args:{subagent_type:'liuren-adjudicator',prompt}});
 const first=JSON.parse(await hooks.tool.liuren_adjudication_read.execute({file_path:saved.file_path,sha256:saved.sha256,page:1},{agent:'liuren-adjudicator',sessionID:'child'}));
 for(let page=2;page<=first.pages;page++)await hooks.tool.liuren_adjudication_read.execute({file_path:saved.file_path,sha256:saved.sha256,page},{agent:'liuren-adjudicator',sessionID:'child'});
 const output=JSON.parse(await hooks.tool.liuren_compute.execute(CALENDAR_EXAMPLE,{agent:'liuren-adjudicator',sessionID:'child'}));
 assert.equal(output.rows.length,22);assert.equal(output.rows[0].day,'戊寅');
});
