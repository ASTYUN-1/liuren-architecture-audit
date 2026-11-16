// Local interface audit only. No model, network, OpenCode session or active-file mutation.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {registerHooks} from 'node:module';
import {packet,result} from '../../tools/tests/fixtures/liuren-adjudication-v2.mjs';
import {runResolvedChart} from '../../tools/liuren-resolved-chart.mjs';
import {loadPacket} from '../../tools/liuren-adjudication-files.mjs';
import {validateOutput} from '../../tools/liuren-adjudication-contract.mjs';
import {finalizeFoundation} from '../../tools/liuren-deterministic-io.mjs';
const root=fileURLToPath(new URL('../../',import.meta.url));
const out=path.join(root,'output/liuren-flow-audit-20261106');
registerHooks({resolve(specifier,context,next){
 if(specifier==='@opencode-ai/plugin')return next(pathToFileURL(path.join(root,'.opencode/node_modules/@opencode-ai/plugin/dist/index.js')).href,context);
 return next(specifier,context);
}});
const {default:plugin}=await import('../../.opencode/plugins/liuren-adjudication.ts');
const active=JSON.parse(await fs.readFile(path.join(root,'.opencode/liuren-active.json'),'utf8'));
const work=await fs.mkdtemp(path.join(out,'probe-workspace-'));
for(const rel of ['tools/liuren-direct/legacy-engine-manifest.json','排盘工具魔改/js/lunar.js',active.runtime+'/manifest.json',active.runtime+'/references/shensha-policy.json',active.runtime+'/methods/timing.md',active.runtime+'/methods/quantity.md',active.runtime+'/references/quantity-sources.md']){
 const target=path.join(work,rel);await fs.mkdir(path.dirname(target),{recursive:true});await fs.copyFile(path.join(root,rel),target);
}
await fs.mkdir(path.join(work,'.opencode'),{recursive:true});
await fs.writeFile(path.join(work,'.opencode/liuren-active.json'),JSON.stringify(active));
const chart=await runResolvedChart({datetime:'2026-10-18T13:22'},{persist:false});assert.equal(chart.ok,true);
const report={release:active.release,scope:'local offline; no real model; no activation',probes:[]};
const prompts=new Map();
const init=()=>plugin({directory:work,client:{session:{get:async()=>({data:{parentID:'parent'}}),messages:async({path:{id}})=>({data:[{info:{role:'user'},parts:[{type:'text',text:prompts.get(id)}]}]})}}});
const hooks=await init();
function input(tasks=['outcome']){
 const p=packet();p.chart={source:'actual engine generated synthetic interface fixture; no prediction',facts:structuredClone(chart.facts)};
 p.questions[0].tasks=tasks;p.entities[0].branch='丑';delete p.entities[0].position;return p;
}
function output(p){
 const r=result();r.entity_checks[0].branch='丑';
 for(const k of ['position','five_qi','twelve_states','site_yin','shenjiang'])delete r.entity_checks[0][k];
 r.relation_checks[0].application={object:'合成对象',mechanism:'合成接口作用',stage:'合成阶段',goal_effect:'只检查接口',alternative_resolution:'合成限制'};
 r.special_methods=[];r.calculations=[];return r;
}
async function save(p){return JSON.parse(await hooks.tool.liuren_adjudication_packet.execute({packet:hooks.tool.liuren_adjudication_packet.args.packet.parse(p)},{agent:'liuren',sessionID:'parent'}));}
async function start(saved,callID,child){
 prompts.set(child,saved.task_prompt);
 const event={tool:'task',sessionID:'parent',callID};
 await hooks['tool.execute.before'](event,{args:{subagent_type:'liuren-adjudicator',prompt:saved.task_prompt}});
 return event;
}
async function read(saved,child,h=hooks){
 const get=page=>h.tool.liuren_adjudication_read.execute({file_path:saved.file_path,sha256:saved.sha256,page},{agent:'liuren-adjudicator',sessionID:child});
 const a=JSON.parse(await get(1));for(let i=2;i<=a.pages;i++)await get(i);return a.pages;
}
async function finish(event,child,r){const out={output:JSON.stringify(r),metadata:{sessionId:child}};await hooks['tool.execute.after'](event,out);return out;}
async function check(name,fn){try{const evidence=await fn();report.probes.push({name,assertion:'passed',...evidence});}catch(error){report.probes.push({name,assertion:'FAILED',error:String(error)});}}
try{
 await check('normal_active_foundation_path',async()=>{
  const saved=await save(input()),event=await start(saved,'normal','child-normal');const pages=await read(saved,'child-normal');
  const p=(await loadPacket(work,{file_path:saved.file_path,sha256:saved.sha256})).envelope.packet;
  const o=await finish(event,'child-normal',output(p));assert.equal(JSON.parse(o.output).status,'completed');assert.equal(o.metadata.liurenAdjudication.contractChecked,true);
  return {finding:'normal path works',pages};
 });
 await check('native_schema_allows_missing_tasks_but_save_rejects',async()=>{
  const p=input();delete p.questions[0].tasks;hooks.tool.liuren_adjudication_packet.args.packet.parse(p);
  await assert.rejects(()=>save(p),/tasks must declare/);return {finding:'schema/runtime mismatch reproduced'};
 });
 await check('native_schema_allows_forbidden_verification_value',async()=>{
  const p=input();p.observations[0].verification='chart_checked';hooks.tool.liuren_adjudication_packet.args.packet.parse(p);
  await assert.rejects(()=>save(p),/program-owned/);return {finding:'schema/runtime mismatch reproduced'};
 });
 await check('invalid_output_returns_generic_error_without_recovery_artifact',async()=>{
  const saved=await save(input()),event=await start(saved,'invalid','child-invalid');await read(saved,'child-invalid');
  const r=output();r.entity_checks[0].branch='丑（初传）';const o=await finish(event,'child-invalid',r),e=JSON.parse(o.output);
  assert.equal(e.status,'invalid_output');assert.ok(!e.error.includes('entity_checks[0]'));assert.ok(!e.error.includes('S1'));
  assert.deepEqual(Object.keys(e).sort(),['action','error','request_id','schema','status'].sort());
  report.failedTask={saved,child:'child-invalid',raw:r};return {finding:'original report overwritten in return; no field path or artifact reference',error:e.error};
 });
 await check('task_result_bypasses_liuren_output_validation',async()=>{
  const {raw:r,child}=report.failedTask;const o={output:JSON.stringify(r),metadata:{sessionId:child}},before=structuredClone(o);
  await hooks['tool.execute.before']({tool:'task_result',sessionID:'parent',callID:'retrieve'},{args:{task_id:child}});
  await hooks['tool.execute.after']({tool:'task_result',sessionID:'parent',callID:'retrieve'},o);
  assert.deepEqual(o,before);assert.ok(!o.metadata.liurenAdjudication);
  return {finding:'custom plugin does not inspect retrieved result; current main permission still lacks explicit allow'};
 });
 await check('same_packet_can_pass_custom_before_hook_three_times',async()=>{
  const {saved}=report.failedTask;
  for(let i=1;i<=3;i++)await start(saved,'retry-'+i,'child-retry-'+i);
  return {finding:'no custom retry budget or same-material guard; slim may separately block'};
 });
 await check('required_main_method_reads_not_checked_before_dispatch',async()=>{
  const saved=await save(input());await start(saved,'no-method-receipt','child-no-method-receipt');
  return {finding:'dispatch succeeds without any main-agent method-read receipt; does not prove professional coverage'};
 });
 await check('process_restart_loses_file_authorization',async()=>{
  const {saved,child}=report.failedTask;const newHooks=await init();
  await assert.rejects(()=>read(saved,child,newHooks),/UNAUTHORIZED_FILE/);
  return {finding:'binding/pending/page receipt are in-memory, not restart recoverable'};
 });
 await check('all_three_tasks_auto_load_and_validate_minimal_complete_records',async()=>{
  const saved=await save(input(['outcome','timing','quantity']));
  const p=(await loadPacket(work,{file_path:saved.file_path,sha256:saved.sha256})).envelope.packet,r=output(p);
  r.calculations=[{id:'C_date',action:'calendar',calendar:{start:'2026-11-03',end:'2026-11-03',timezone:'Asia/Shanghai',day_boundary:'civil-midnight'}},{id:'C_amount',action:'quantity',expression:{op:'multiply',args:[{value:8},{value:6}]}}];
  r.special_methods=[
   {question_id:'Q1',kind:'timing',status:'completed',target:'合成完成时间',basis_ids:['M_AUTO_TIMING'],calculation_ids:['C_date'],alternatives:[],limits:[],record:{event:'合成完成',stage:'完成',scale:'日',start:'合成占时',count_rule:'当日',trigger:'合成触发',selected_method:'仅校接口',round_comparison:'只检查结构',candidates:[{date:'2026-11-03',day:'辛巳',event:'合成完成'}]}},
   {question_id:'Q1',kind:'quantity',status:'completed',target:'合成金额',basis_ids:['M_AUTO_QUANTITY'],calculation_ids:['C_amount'],alternatives:[],limits:[],record:{object:'合成部件',position:'合成初传',number_table:'原法常数',operation:'8乘6',adjustments:'无',magnitude:'未扩倍',unit:'元',precision:'接口测试值',value:48}}
  ];
  assert.equal(validateOutput(finalizeFoundation(work,r,p),p).status,'completed');
  r.special_methods[1].record.value=480;assert.throws(()=>validateOutput(finalizeFoundation(work,r,p),p),/differs from computed/);
  return {finding:'special methods not removed; auto sources and date/amount checks work',method_ids:p.method_materials.map(m=>m.id)};
 });
 await check('unknowns_text_is_not_an_enforced_needs_input_gate',async()=>{
  const p=input();p.unknowns=['合成：本问关键实际起算日尚缺'];const saved=await save(p);
  const packet=(await loadPacket(work,{file_path:saved.file_path,sha256:saved.sha256})).envelope.packet;
  assert.equal(validateOutput(finalizeFoundation(work,output(),packet),packet).status,'completed');
  return {finding:'semantic necessity of unknowns remains model judgment; no program-derived requirement'};
 });
 await check('missing_whole_question_is_rejected',async()=>{
  const saved=await save(input()),p=(await loadPacket(work,{file_path:saved.file_path,sha256:saved.sha256})).envelope.packet,r=output();r.answers=[];
  assert.throws(()=>validateOutput(finalizeFoundation(work,r,p),p),/answers invalid array/);return {finding:'question presence enforced'};
 });
 delete report.failedTask;
 report.failed=report.probes.filter(p=>p.assertion!=='passed').length;
 await fs.writeFile(path.join(out,'full-flow-probes.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify(report,null,2));if(report.failed)process.exitCode=1;
}finally{
 const resolved=path.resolve(work);assert.equal(path.dirname(resolved),path.resolve(out));assert.ok(path.basename(resolved).startsWith('probe-workspace-'));
 await fs.rm(resolved,{recursive:true,force:true});
}
