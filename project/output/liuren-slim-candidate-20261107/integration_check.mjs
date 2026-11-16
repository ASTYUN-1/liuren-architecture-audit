// Native plugin in an isolated candidate. Mock host sessions; never call a model.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {registerHooks} from 'node:module';
import {execFileSync} from 'node:child_process';
import {randomUUID} from 'node:crypto';
import assert from 'node:assert/strict';
const folder=path.dirname(fileURLToPath(import.meta.url));
const project=path.resolve(folder,'../..');
const root=path.join(folder,'candidate');
registerHooks({resolve(specifier,context,next){
 if(specifier==='@opencode-ai/plugin')return next(pathToFileURL(path.join(project,'.opencode/node_modules/@opencode-ai/plugin/dist/index.js')).href,context);
 return next(specifier,context);
}});
const {default:plugin}=await import('./candidate/.opencode/plugins/liuren-adjudication.ts');
const {packet}=await import('./candidate/tools/tests/fixtures/liuren-adjudication-v2.mjs');
const {runResolvedChart}=await import('./candidate/tools/liuren-resolved-chart.mjs');
const {prepareFoundation}=await import('./candidate/tools/liuren-deterministic-io.mjs');
const {loadShenshaPolicy,resolveShensha}=await import('./candidate/tools/liuren-shensha.mjs');
const pointer=JSON.parse(await fs.readFile(path.join(root,'.opencode/liuren-active.json'),'utf8'));
const manifest=JSON.parse(await fs.readFile(path.join(root,pointer.runtime,'manifest.json'),'utf8'));
const checks=[];const record=(name,detail={})=>checks.push({check:name,passed:true,...detail});
const runID=randomUUID(),parent='slim_parent_'+runID,child='slim_child_'+runID;let saved;
const parentParts=[],childParts=[];
const client={session:{get:async()=>({data:{parentID:parent}}),messages:async({path:{id}})=>({data:id===parent?[{info:{role:'user'},parts:[{type:'text',text:'姐姐的女儿参加转校考试，能否转入？'}]},{info:{role:'assistant'},parts:parentParts}]:[{info:{role:'user'},parts:[{type:'text',text:saved?.task_prompt}]},{info:{role:'assistant'},parts:childParts}]})}};
let hooks=await plugin({directory:root,client});
const context={agent:'liuren',sessionID:parent};
const childContext={agent:'liuren-adjudicator',sessionID:child};
const parse=v=>typeof v==='string'?JSON.parse(v):JSON.parse(v.output);
async function help(){return parse(await hooks.tool.liuren_tool_help.execute({topic:'workflow',domains:['exam']},context));}
let current=await help();
assert.equal(current.tool_contract,'liuren-tools-25');
assert.deepEqual(new Set(current.readiness.missing),new Set([...manifest.required.filter(k=>k!=='report'),'exam']));
record('实际工具门禁使用候选7项准备加考试，不要求旧6项');
async function readMethod(module){
 const request=JSON.stringify({action:'method',module});
 const output=execFileSync('python',['-X','utf8',path.join(root,'tools/liuren-materials.py'),'--request',request],{cwd:root,encoding:'utf8',maxBuffer:2*1024*1024});
 parentParts.push({type:'tool',tool:'liuren_materials',state:{status:'completed',output}});
 await hooks['tool.execute.after']({tool:'liuren_materials',sessionID:context.sessionID,callID:'read_'+module},{output,metadata:{}});
}
for(const key of current.readiness.required)if(key!=='void')await readMethod(key);
current=await help();assert.deepEqual(current.readiness.missing,['void']);record('已读回执复用，缺一项只要求补一项');
await readMethod('void');assert.equal((await help()).readiness.ready,true);
const chart=await runResolvedChart({datetime:'2026-10-18T13:22'},{persist:false});assert.equal(chart.ok,true);
record('候选固定排盘与神煞policy可正常载入');
const basePolicy=JSON.parse(await fs.readFile(path.join(project,'runtime/liuren/20261106-performance-25/references/shensha-policy.json'),'utf8'));
const candidatePolicy=await loadShenshaPolicy(root);
const selectedA=resolveShensha(chart.facts,basePolicy,'same-policy-content');
const selectedB=resolveShensha(chart.facts,candidatePolicy.policy,'same-policy-content');
// The release field is an identity, not a computed placement.
function placements(v){const x=structuredClone(v);delete x.release;delete x.policy_release;return x;}
assert.deepEqual(placements(selectedA),placements(selectedB));record('同一真实程序盘的全部神煞计算与采用状态一致');
const p=packet();p.request_id='slim_candidate_native';p.chart={source:'合成工程检查所用真实程序盘；无预测判断',facts:chart.facts};
p.questions[0]={...p.questions[0],id:'Q1',text:'能否转入',domain:'exam',subject:'实际考生',tasks:['outcome'],task_basis:[{task:'outcome',origin:'user_requested',request_quote:'能否转入',reason:'原问录取结果'}]};
p.entities[0].branch=chart.facts.day_stem;delete p.entities[0].position;p.entities[0].referent='考生';
p.method_modules=['positioning','liqi','structure','void','shensha-use','movement','exam'];
saved=parse(await hooks.tool.liuren_adjudication_packet.execute({packet:hooks.tool.liuren_adjudication_packet.args.packet.parse(p)},context));
const assembled=JSON.parse(await fs.readFile(saved.file_path,'utf8')).packet;
assert.equal(assembled.method_modules,undefined);
assert.ok(assembled.material_aliases.some(a=>a.id==='M_EVENT_POSITIONING'));
assert.ok(assembled.material_aliases.some(a=>a.id==='M_DOMAIN_exam'));
assert.ok(!assembled.method_materials.some(m=>/AUTO_TIMING|AUTO_QUANTITY/.test(m.id)));
for(const key of p.method_modules){assert.ok(assembled.method_materials.some(m=>m.id==='M_'+key));}
record('7份专业全文原样装配，定位与专项自动项去重，不自动加应期取数',{materialCount:assembled.method_materials.length,aliases:assembled.material_aliases.length});
const taskEvent={tool:'task',sessionID:context.sessionID,callID:'slim_dispatch'};
await hooks['tool.execute.before'](taskEvent,{args:{subagent_type:'liuren-adjudicator',prompt:saved.task_prompt}});
// Binding is normally done by the host's task callback; simulate its visible child result later.
const {store}=await import('./candidate/tools/liuren-flow-control.mjs');
const flow=await store(root);await flow.bind(context.sessionID,child,{file_path:saved.file_path,sha256:saved.sha256},taskEvent.callID);
let args={file_path:saved.file_path,sha256:saved.sha256,page:1,page_count:4};const texts=[];let calls=0;
do{
 const response=await hooks.tool.liuren_adjudication_read.execute(args,childContext);const value=parse(response);calls++;
 texts.push(value.content);
 childParts.push({type:'tool',tool:'liuren_adjudication_read',state:{status:'completed',input:args,output:typeof response==='string'?response:response.output}});
 args=value.next_call?.arguments;
}while(args);
assert.equal(texts.join(''),await fs.readFile(saved.file_path,'utf8'));record('裁决文件多页全文与hash完整接续读取',{readCalls:calls,fileChars:texts.join('').length});
const markdown='# 合成接口检查报告\n\n仅检查传输、领取和交付，不提供考试判断。';
const submitted=parse(await hooks.tool.liuren_adjudication_submit.execute({result:markdown},childContext));
assert.equal(submitted.status,'completed');
const taskOutput={output:JSON.stringify(submitted),metadata:{sessionId:child}};
await hooks['tool.execute.after'](taskEvent,taskOutput);
const receipt=JSON.parse(taskOutput.output);assert.equal(receipt.task_id,child);
const ackEvent={tool:'task_result',sessionID:context.sessionID,callID:'slim_ack'};
await hooks['tool.execute.before'](ackEvent,{args:{task_id:child}});
await hooks['tool.execute.after'](ackEvent,{output:'saved receipt',metadata:{}});
let failed=false;try{await hooks.tool.liuren_adjudication_result.execute({action:'deliver',task_id:child},context);}catch(error){failed=/MISSING_METHODS/.test(error.message);}
assert.ok(failed);record('report交付前门禁仍阻止缺读交付');
await readMethod('report');
hooks=await plugin({directory:root,client});
const delivered=parse(await hooks.tool.liuren_adjudication_result.execute({action:'deliver',task_id:child},context));
assert.equal(delivered.report_markdown,markdown);record('自由正文保存、领取、重启复用及deliver原文一致');
const q=packet();q.chart={source:'同盘任务触发工程检查',facts:chart.facts};q.entities[0].branch='丑';delete q.entities[0].position;
q.questions[0].tasks=['outcome','timing','quantity'];q.questions[0].domain='finance';
const expanded=await prepareFoundation(root,q);
for(const id of ['M_AUTO_TIMING','M_AUTO_QUANTITY','M_AUTO_NUMBERS'])assert.ok(expanded.method_materials.some(m=>m.id===id));
record('实际tasks触发完整应期与取数专法自动装配');
await fs.writeFile(path.join(folder,'integration-verification.json'),JSON.stringify({checks,syntheticOnly:true,modelCalls:0,predictiveValidationCount:0},null,2)+'\n');
console.log(JSON.stringify({passed:checks.length,checks},null,2));
