import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {registerHooks} from 'node:module';
import {runResolvedChart} from '../liuren-resolved-chart.mjs';
import {buildFacts,canonicalEntity,xunFacts,relations,growth,kin,seasonal,calculate,ZHI,GAN,hash} from '../liuren-deterministic.mjs';
import {calendar} from '../liuren-deterministic-calendar.mjs';
import {prepareFoundation,finalizeFoundation,sourceMaterial,compute} from '../liuren-deterministic-io.mjs';
import {validateInput,validateOutput} from '../liuren-adjudication-contract.mjs';
import {savePacket,loadPacket} from '../liuren-adjudication-files.mjs';
import {packet,result,methodMessages} from './fixtures/liuren-adjudication-v2.mjs';
const ROOT=fileURLToPath(new URL('../../',import.meta.url));
const chart=await runResolvedChart({datetime:'2026-10-18T13:22'},{persist:false});
const facts=chart.facts,d=buildFacts(facts);
let temp;
test.before(async()=>{
 temp=await fs.mkdtemp(path.join(os.tmpdir(),'liuren-foundation-test-'));
 const active=JSON.parse(await fs.readFile(path.join(ROOT,'.opencode/liuren-active.json'),'utf8'));
 active.deterministicFoundation={enabled:true};active.eventPositioning={enabled:false};active.compactHandoff={enabled:false}; // Legacy foundation protocol; compact transport has its own complete fixture.
 for(const rel of ['tools/liuren-direct/legacy-engine-manifest.json','排盘工具魔改/js/lunar.js',active.runtime+'/manifest.json',active.runtime+'/references/shensha-policy.json',active.runtime+'/methods/timing.md',active.runtime+'/methods/quantity.md',active.runtime+'/references/quantity-sources.md']){
  const dst=path.join(temp,rel);await fs.mkdir(path.dirname(dst),{recursive:true});await fs.copyFile(path.join(ROOT,rel),dst);
 }
 await fs.mkdir(path.join(temp,'.opencode'),{recursive:true});
 await fs.writeFile(path.join(temp,'.opencode/liuren-active.json'),JSON.stringify(active));
 await fs.mkdir(path.join(temp,'books'),{recursive:true});
 await fs.writeFile(path.join(temp,'books/source.txt'),'前段条件\r\n第一行\r\n\r\n第二段前提\r\n适用条件\r\n\r\n结尾\r\n');
});
test.after(async()=>{assert.equal(path.dirname(path.resolve(temp)),path.resolve(os.tmpdir()));assert.ok(path.basename(temp).startsWith('liuren-foundation-test-'));await fs.rm(temp,{recursive:true,force:true});});
function input(tasks=['outcome']){const p=packet();p.chart={source:'real engine test fixture; no predictive assertion',facts:structuredClone(facts)};p.questions[0].tasks=tasks;p.entities[0].branch='丑';delete p.entities[0].position;return p;}
async function prepared(tasks){return validateInput(await prepareFoundation(temp,input(tasks)));}
function output(p){const r=result();r.entity_checks[0].branch='丑';r.entity_checks[0].position=p.entities[0].position;
 for(const k of ['five_qi','twelve_states','site_yin','shenjiang'])delete r.entity_checks[0][k];
 r.relation_checks[0].application={object:'测试故障部件',mechanism:'合成作用，仅检查字段',stage:'过程',goal_effect:'待核功能恢复',alternative_resolution:'保留其他解释'};
 r.special_methods=[];r.calculations=[];return r;}
test('engine facts are read without mutation; coordinates and direct yin distinguish earth upper',()=>{
 const old=JSON.stringify(facts),n=d.nodes.find(n=>n.symbol==='丑');assert.equal(n.ground,'辰');assert.equal(n.general,'腾蛇');assert.equal(n.direct_yin,'戌');
 assert.equal(d.nodes.find(n=>n.symbol==='未').direct_yin,'辰');assert.equal(d.anchors.day_yin,'戌');assert.equal(JSON.stringify(facts),old);
 assert.equal(d.engine_inventory.references.growth,'chart.facts.growth');assert.deepEqual(d.structure.engine_types,facts.chart_types);
});

test('strict coordinates accept real charts across twelve months and all ten day stems',async()=>{
 const months=new Set(),stems=new Set();
 for(let month=1;month<=12;month++){
  const date='2026-'+String(month).padStart(2,'0')+'-'+String(10+month%10).padStart(2,'0')+'T'+String((month*2)%24).padStart(2,'0')+':22';
  const sample=await runResolvedChart({datetime:date},{persist:false});
  assert.ok(sample.ok);buildFacts(sample.facts);months.add(sample.facts.month_branch);stems.add(sample.facts.day_stem);
  for(const [state,place] of Object.entries(sample.facts.growth.day_stem))assert.equal(growth(sample.facts.day_stem,place),state);
 }
 for(let day=10;stems.size<10&&day<30;day++){
  const sample=await runResolvedChart({datetime:'2026-10-'+day+'T13:22'},{persist:false});
  assert.ok(sample.ok);buildFacts(sample.facts);stems.add(sample.facts.day_stem);
  for(const [state,place] of Object.entries(sample.facts.growth.day_stem))assert.equal(growth(sample.facts.day_stem,place),state);
 }
 assert.equal(months.size,12);assert.equal(stems.size,10);
});
test('all 60 sexagenary days produce ten assigned stems and exactly two voids',()=>{
 for(let i=0;i<60;i++){const x=xunFacts(GAN[i%10]+ZHI[i%12]);assert.equal(Object.values(x.xungan).filter(v=>v==='空').length,2);assert.equal(x.xungan[ZHI[i%12]],GAN[i%10]);}
 assert.throws(()=>xunFacts('甲丑'),/invalid/);
});
test('stem growth follows engine yin/yang cycles while branch/general growth uses element cycles',()=>{
 assert.equal(growth('乙','辰'),'冠带');assert.equal(facts.growth.day_stem.冠带,'辰');
 assert.equal(growth('丁','未'),'冠带');assert.equal(growth('火','未'),'衰');
 assert.equal(growth('白虎','申'),'临官');assert.equal(growth('申','午'),'沐浴');
 assert.equal(d.day.growth.profile,'stem-yang-forward-yin-reverse');
 assert.equal(d.day.growth.upper,growth(d.day.symbol,d.day.upper));
 assert.equal(growth('丑','辰'),'墓');assert.equal(kin('乙','丑'),'妻财');assert.equal(kin('丑','乙'),'官鬼');
 assert.equal(seasonal('丑','戌','four-seasons'),'休');assert.equal(seasonal('丑','戌','quarter-earth'),'旺');
 assert.equal(d.nodes.find(n=>n.symbol==='丑').seasonal.profiles['quarter-earth'],'旺');
});
test('directional relationships do not turn into efficacy or transformations',()=>{
 assert.equal(relations('甲','巳')[0].value,'生');assert.equal(relations('巳','甲')[0].value,'被生');
 assert.ok(relations('丑','未').some(r=>r.type==='六冲'));assert.ok(relations('丑','戌').some(r=>r.type==='刑'));assert.ok(!relations('戌','丑').some(r=>r.type==='刑'));
 assert.ok(relations('巳','申').some(r=>r.type==='六合'));assert.ok(relations('巳','申').some(r=>r.type==='六破'));
 const selfXing=relations('辰','辰').find(r=>r.type==='自刑候选');
 assert.equal(selfXing.requires_distinct_occurrences,undefined);assert.ok(selfXing.occurrence_scope.includes('single occurrence'));
 assert.equal(d.structure.triple_member_candidates.length,0);
});
for(const [name,change] of [
 ['yin source plate',c=>c.heaven_earth[0].tian='丑'],['four lesson order',c=>c.lessons.reverse()],
 ['lesson upper',c=>c.lessons[0].tianpan='寅'],['wrong transmission general',c=>c.transmissions[0].tianjiang='朱雀'],
 ['void',c=>c.void_branches=['子','丑']],['month general',c=>c.month_general='亥'],['day duplicate',c=>c.day_stem='甲'],
 ['general ordering',c=>{const a=c.heaven_earth[0].tianjiang;c.heaven_earth[0].tianjiang=c.heaven_earth[1].tianjiang;c.heaven_earth[1].tianjiang=a;}]
])test('reject inconsistent '+name,()=>{const c=structuredClone(facts);change(c);assert.throws(()=>buildFacts(c),/LIUREN_DETERMINISTIC/);});
test('legacy engine mismatches are visible and never silently overwrite its original bytes',()=>{
 const c=structuredClone(facts);c.heaven_earth.find(r=>r.tian==='丑').xungan='丙';c.transmissions[0].liuqin='父母';const b=buildFacts(c);
 assert.ok(b.warnings.some(w=>w.code==='ENGINE_XUNGAN_DIFFERENCE'));assert.ok(b.warnings.some(w=>w.code==='ENGINE_KIN_DIFFERENCE'));assert.equal(c.transmissions[0].liuqin,'父母');
});
test('calendar includes both rounds, with correct dates and no original chart mutation',()=>{
 const c=calendar({start:'2026-10-18',end:'2026-11-04',timezone:'Asia/Shanghai',day_boundary:'civil-midnight',branches:['辰','巳']});
 assert.deepEqual(c.rows.map(r=>[r.date,r.day,r.round_for_branch]),[['2026-10-21','戊辰',1],['2026-10-22','己巳',1],['2026-11-02','庚辰',2],['2026-11-03','辛巳',2]]);
 assert.deepEqual(facts.void_branches,['戌','亥']);
});
test('calendar rejects invalid dates, omitted convention, inverted range and invalid pillar',()=>{
 const base={start:'2026-11-01',end:'2026-11-04',timezone:'Asia/Shanghai',day_boundary:'civil-midnight'};
 for(const extra of [{start:'2026-02-30'},{end:'2026-10-01'},{timezone:'UTC'},{day_boundary:undefined},{pillars:['甲丑']},{end:'2100-11-01'}])assert.throws(()=>calendar({...base,...extra}),/LIUREN_CALENDAR/);
});
test('23h boundary is explicit; leap day and year transition calculate',()=>{
 const base={start:'2026-11-03',end:'2026-11-03',timezone:'Asia/Shanghai',hour:23};
 assert.equal(calendar({...base,day_boundary:'civil-midnight'}).rows[0].day,'辛巳');assert.equal(calendar({...base,day_boundary:'zi-hour'}).rows[0].day,'壬午');
 assert.equal(calendar({start:'2028-02-28',end:'2028-03-01',timezone:'Asia/Shanghai',day_boundary:'civil-midnight'}).rows.length,3);
});
test('number tables and arithmetic execute explicitly without inferred decimal magnitude',()=>{
 const c=calculate({op:'multiply',args:[{table:'branch',symbol:'丑'},{value:6}]});assert.equal(c.value,48);
 assert.equal(calculate({op:'add',args:[{value:0.1},{value:0.2}]}).value,0.3);
 assert.equal(calculate({op:'add',args:[{table:'branch',symbol:'丑'},{table:'branch',symbol:'戌'},{table:'branch',symbol:'未'}]}).value,21);
 for(const e of [{table:'general',symbol:'腾蛇'},{table:'__proto__',symbol:'toString'},{op:'divide',args:[{value:2},{value:0}]},{value:Infinity},{op:'eval',args:[]}])assert.throws(()=>calculate(e),/LIUREN_DETERMINISTIC/);
});
test('life uses only explicitly verified nominal age; never infers from birth pillar',()=>{
 const r=compute({action:'life',life:{age:96,sex:'男',age_basis:'虚岁-已核'}},facts);assert.equal(r.xingnian,'辛丑');
 assert.equal(compute({action:'life',life:{age:97,sex:'男',age_basis:'虚岁-已核'}},facts).xingnian,'壬寅');
 assert.equal(compute({action:'life',life:{age:21,sex:'女',age_basis:'虚岁-已核'}},facts).xingnian,'壬子');
 assert.throws(()=>compute({action:'life',life:{birth_pillar:'丙戌',sex:'男'}},facts),/requires/);
});
test('arbitrary lookup requires a registered profile and preserves reference',()=>{
 const r=compute({action:'lookup',lookup:{subject:'朱雀',place:'巳',reference:'乙'}},facts);assert.equal(r.growth,'临官');assert.equal(r.kin,'子孙');
 const stem=compute({action:'lookup',lookup:{subject:'丁',place:'未'}},facts);assert.equal(stem.growth,'冠带');assert.equal(stem.growth_profile,'stem-yang-forward-yin-reverse');
 assert.throws(()=>compute({action:'lookup',lookup:{subject:'丑',profile:'guess'}},facts),/unregistered/);
});
test('source material uses exact continuous line spans, hashes and paragraph context',async()=>{
 const r=await sourceMaterial(temp,{id:'M1',title:'source fixture',source_path:'books/source.txt',line_start:5,line_end:5,line_mode:'universal'});
 assert.equal(r.quote,'第二段前提\n适用条件');assert.equal(r.line_start,4);
 await assert.rejects(()=>sourceMaterial(temp,{...r,quote:'虚构引文'}),/differs/);
 await assert.rejects(()=>sourceMaterial(temp,{...r,sha256:'0'.repeat(64)}),/changed/);
 await assert.rejects(()=>sourceMaterial(temp,{...r,source_path:'经验日志/anything.md'}),/outside/);
 await assert.rejects(()=>sourceMaterial(temp,{...r,source_path:'../books/source.txt'}),/outside/);
});

test('manifest-verified runtime method references load whole text without invented line counts',async()=>{
 const active=JSON.parse(await fs.readFile(path.join(temp,'.opencode/liuren-active.json'),'utf8'));
 const source_path=active.runtime+'/methods/timing.md',raw=await fs.readFile(path.join(temp,source_path),'utf8');
 const material=await sourceMaterial(temp,{id:'M_RUNTIME',title:'完整应期',source_path,sha256:hash(raw)});
 assert.equal(material.quote.trim(),raw.replaceAll('\r\n','\n').trim());assert.equal(material.line_start,1);
 await assert.rejects(()=>sourceMaterial(temp,{id:'M_BAD',title:'bad',source_path,sha256:'0'.repeat(64)}),/sha256 changed/);
 await assert.rejects(()=>sourceMaterial(temp,{id:'M_BOOK',title:'book',source_path:'books/source.txt'}),/method_materials\[id=M_BOOK\].*line_start\/line_end.*actual start=undefined/);
 await assert.rejects(()=>sourceMaterial(temp,{id:'M_RANGE',title:'range',source_path,line_start:1,line_end:99999}),/id=M_RANGE.*expected integers.*actual start=1, end=99999/);
});

test('Chinese expanded packets above the previous byte limit save and reload without truncation',async()=>{
 const p=input();p.request_id='20261106-large-file';p.unknowns=Array.from({length:22},()=> '材'.repeat(5500));
 const saved=await savePacket(temp,p,'parent');assert.ok((await fs.stat(saved.file_path)).size>300000);
 const loaded=await loadPacket(temp,saved);assert.deepEqual(loaded.envelope.packet.unknowns,p.unknowns);
});
test('program generates packet positions; raw chart_checked and wrong copied coordinates fail',async()=>{
 const p=await prepared();assert.match(p.entities[0].position,/天盘临辰/);assert.equal(p.deterministic.nodes.length,12);
 assert.equal(p.deterministic.adopted_shensha.schema,'liuren-shensha-resolution-v1');
 const wrong=input();wrong.entities[0].position='初传丑临寅';await assert.rejects(()=>prepareFoundation(temp,wrong),/program-owned/);
 const observed=input();observed.observations[0].verification='chart_checked';await assert.rejects(()=>prepareFoundation(temp,observed),/program-owned/);
 const missing=input();delete missing.questions[0].tasks;await assert.rejects(()=>prepareFoundation(temp,missing),/tasks/);
});

test('source aliases preserve every old ID and never combine different line ranges',async()=>{
 const p=input();p.method_materials=[
  {id:'M_A',title:'same A',source_path:'books/source.txt',line_start:1,line_end:2,line_mode:'universal'},
  {id:'M_B',title:'same B',source_path:'books/source.txt',line_start:1,line_end:2,line_mode:'universal'},
  {id:'M_C',title:'different span',source_path:'books/source.txt',line_start:4,line_end:5,line_mode:'universal'}
 ];
 const result=validateInput(await prepareFoundation(temp,p));
 assert.equal(result.method_materials.length,2);assert.equal(result.material_aliases.length,1);assert.equal(result.material_aliases[0].id,'M_B');assert.equal(result.material_aliases[0].canonical_id,'M_A');assert.ok(result.method_materials.some(m=>m.id==='M_C'));
 const wrong=structuredClone(result);wrong.material_aliases[0].line_end=5;assert.throws(()=>validateInput(wrong),/differs from canonical/);
});
test('forged deterministic content is rejected both before save and after preparation',async()=>{
 const bad=input();bad.deterministic={};await assert.rejects(()=>prepareFoundation(temp,bad),/generated/);
 const p=await prepared();p.deterministic.nodes[0].direct_yin='寅';assert.throws(()=>validateInput(p),/changed/);
});
test('normalization fills exact facts; fabricated output position/yin cannot be returned',async()=>{
 const p=await prepared(),r=finalizeFoundation(temp,output(p),p);assert.equal(validateOutput(r,p).status,'completed');assert.match(r.entity_checks[0].site_yin,/阴神戌/);
 const bad=output(p);bad.entity_checks[0].site_yin='阴神寅';assert.throws(()=>finalizeFoundation(temp,bad,p),/wrong/);
 const tampered=structuredClone(r);tampered.entity_checks[0].site_yin='阴神寅';assert.throws(()=>validateOutput(tampered,p),/wrong computed/);
});
test('decisive relation requires object, mechanism, stage, goal effect and alternative',async()=>{
 const p=await prepared(),r=output(p);delete r.relation_checks[0].application;assert.throws(()=>validateOutput(finalizeFoundation(temp,r,p),p),/application chain/);
});
test('timing and quantity source texts are auto-included unchanged and records are required',async()=>{
 const p=await prepared(['outcome','timing','quantity']);assert.equal(p.method_materials.length,3);assert.equal(p.deterministic.special_requirements.length,2);
 assert.ok(p.method_materials.find(m=>m.id==='M_AUTO_TIMING').quote.includes('竞争轮次'));
 assert.throws(()=>validateOutput(finalizeFoundation(temp,output(p),p),p),/missing special/);
});

test('a concrete needs_input response need not fabricate completed special-method records',async()=>{
 const p=await prepared(['timing','quantity']),r=output(p);
 r.status='needs_input';r.scope_review.mapping_status='needs_input';r.answers[0].precision='unresolved';
 r.missing_inputs=['测试缺项：实际问事起算日期未给'];delete r.special_methods;
 assert.equal(validateOutput(finalizeFoundation(temp,r,p),p).status,'needs_input');
});
test('complete quantity record must match a deterministic arithmetic value',async()=>{
 const p=await prepared(['quantity']),r=output(p);r.calculations=[{id:'C_amount',action:'quantity',expression:{op:'multiply',args:[{table:'branch',symbol:'丑'},{value:6}]}}];
 r.special_methods=[{question_id:'Q1',kind:'quantity',status:'completed',target:'合成金额',basis_ids:['M_AUTO_QUANTITY'],calculation_ids:['C_amount'],limits:[],alternatives:[],record:{object:'部件',position:'初传',number_table:'branch',operation:'乘6，合成测试',adjustments:'无',magnitude:'本例不作实占量级验证',unit:'元',precision:'近似',value:48}}];
 assert.equal(validateOutput(finalizeFoundation(temp,r,p),p).status,'completed');r.special_methods[0].record.value=480;assert.throws(()=>validateOutput(finalizeFoundation(temp,r,p),p),e=>/differs/.test(e.message)&&e.path==='/special_methods/0/record/value');
});
test('complete timing record verifies candidate day and date instead of trusting text',async()=>{
 const p=await prepared(['timing']),r=output(p);
 r.calculations=[{id:'C_date',action:'calendar',calendar:{start:'2026-10-18',end:'2026-11-04',timezone:'Asia/Shanghai',day_boundary:'civil-midnight',branches:['巳']}}];
 r.special_methods=[{question_id:'Q1',kind:'timing',status:'completed',target:'合成事件',basis_ids:['M_AUTO_TIMING'],calculation_ids:['C_date'],limits:[],alternatives:[],record:{event:'完成',stage:'完成',scale:'日',start:'占时',count_rule:'不含当日',trigger:'合成触发',selected_method:'合成测试，不验证择法',round_comparison:'两轮均列，选择仅为接口测试',candidates:[{date:'2026-11-03',day:'辛巳',event:'完成'}]}}];
 assert.equal(validateOutput(finalizeFoundation(temp,r,p),p).status,'completed');r.special_methods[0].record.candidates[0].date='2026-10-25';assert.throws(()=>validateOutput(finalizeFoundation(temp,r,p),p),/calendar dates/);
});
test('active foundation saves original chart plus program facts, and enforces full read protocol',async()=>{
 const saved=await savePacket(temp,input(),'parent'),loaded=await loadPacket(temp,{file_path:saved.file_path,sha256:saved.sha256});
 assert.deepEqual(loaded.envelope.packet.chart.facts,facts);assert.equal(loaded.envelope.packet.deterministic.schema,'liuren-deterministic-v1');assert.ok(loaded.pages>=2);
});

test('all three tasks fit the existing packet limit without dropping source or engine fields',async()=>{
 const saved=await savePacket(temp,input(['outcome','timing','quantity']),'parent');
 const loaded=await loadPacket(temp,{file_path:saved.file_path,sha256:saved.sha256});
 const p=loaded.envelope.packet;
 assert.ok(JSON.stringify(p).length<=100000);assert.deepEqual(p.chart.facts,facts);
 assert.equal(p.method_materials.length,3);assert.equal(p.deterministic.special_requirements.length,2);
});
test('new native tool is callable by main and child with the current bound chart',async()=>{
 registerHooks({resolve(specifier,context,next){if(specifier==='@opencode-ai/plugin')return next(pathToFileURL(path.join(ROOT,'.opencode/node_modules/@opencode-ai/plugin/dist/index.js')).href,context);return next(specifier,context);}});
 const {default:plugin}=await import('../../.opencode/plugins/liuren-adjudication.ts');let prompt;const receipts=[];
 const h=await plugin({directory:temp,client:{session:{get:async()=>({data:{parentID:'parent'}}),messages:async({path:{id}})=>({data:id==='parent'?await methodMessages(ROOT):[{info:{role:'user'},parts:[{type:'text',text:prompt}]},{info:{role:'assistant'},parts:receipts}]})}}});
 const nativeInput=input();nativeInput.questions[0].task_basis=[{task:'outcome',origin:'user_requested',request_quote:'合成接口问题',reason:'合成原问'}];
 const parsed=h.tool.liuren_adjudication_packet.args.packet.parse(nativeInput);
 const saved=JSON.parse(await h.tool.liuren_adjudication_packet.execute({packet:parsed},{agent:'liuren',sessionID:'parent'}));prompt=saved.task_prompt;
 const ti={tool:'task',sessionID:'parent',callID:'foundation1'};await h['tool.execute.before'](ti,{args:{subagent_type:'liuren-adjudicator',prompt}});
 const read=async page=>{const raw=await h.tool.liuren_adjudication_read.execute({file_path:saved.file_path,sha256:saved.sha256,page},{agent:'liuren-adjudicator',sessionID:'child'});receipts.push({type:'tool',tool:'liuren_adjudication_read',state:{status:'completed',output:raw}});return JSON.parse(raw);};
 const first=await read(1);
 for(let page=2;page<=first.pages;page++)await read(page);
 const query=JSON.parse(await h.tool.liuren_compute.execute({action:'chart',symbols:['丑']},{agent:'liuren-adjudicator',sessionID:'child'}));assert.equal(query.nodes[0].direct_yin,'戌');assert.equal(query.adopted_shensha.schema,'liuren-shensha-resolution-v1');
 await assert.rejects(()=>h.tool.liuren_compute.execute({action:'source',source:{}},{agent:'liuren-adjudicator',sessionID:'child'}),/PRIMARY_ONLY/);
 const loaded=(await loadPacket(temp,{file_path:saved.file_path,sha256:saved.sha256})).envelope.packet;
 const out={output:JSON.stringify(output(loaded)),metadata:{sessionId:'child'}};await h['tool.execute.after'](ti,out);assert.equal(JSON.parse(out.output).status,'completed');const checked=JSON.parse(await h.tool.liuren_adjudication_result.execute({action:'read',task_id:'child'},{agent:'liuren',sessionID:'parent'}));assert.deepEqual(checked.result,output(loaded));assert.equal(checked.execution_receipt.professionalContentChecked,false);
});


test('tool-returned absolute source paths normalize without losing scope or hash validation',async()=>{
 const active=JSON.parse(await fs.readFile(path.join(temp,'.opencode/liuren-active.json'),'utf8'));
 const rel=active.runtime+'/methods/timing.md';
 const raw=await fs.readFile(path.join(temp,rel),'utf8');
 const ref={id:'M_ABSOLUTE',title:'应期',source_path:path.resolve(temp,rel),sha256:hash(raw)};
 const result=await sourceMaterial(temp,ref);
 assert.equal(result.source_path,rel);assert.equal(result.sha256,ref.sha256);
 assert.equal((await sourceMaterial(temp,{...ref,source_path:ref.source_path.replaceAll('\\','/')})).quote,result.quote);
 await assert.rejects(()=>sourceMaterial(temp,{...ref,sha256:'0'.repeat(64)}),/sha256 changed/);
 for(const source_path of [path.resolve(temp,'..','outside.md'),path.resolve(temp,'经验日志','source.md'),path.resolve(temp,'runtime/liuren/old/methods/timing.md'),active.runtime+'/methods/../methods/timing.md']){
  await assert.rejects(()=>sourceMaterial(temp,{...ref,source_path}),e=>/method_materials\[id=M_ABSOLUTE\].source_path/.test(e.message)&&/received=/.test(e.message)&&/handoff/.test(e.message));
 }
});
