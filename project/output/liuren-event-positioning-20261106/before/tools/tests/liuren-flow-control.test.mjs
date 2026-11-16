import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {registerHooks} from 'node:module';
import {createHash} from 'node:crypto';
import {packet,result} from './fixtures/liuren-adjudication-v2.mjs';
import {runResolvedChart} from '../liuren-resolved-chart.mjs';
import {store} from '../liuren-flow-control.mjs';
import {checkSubmission} from '../liuren-adjudication-output.mjs';
const root=fileURLToPath(new URL('../../',import.meta.url));
registerHooks({resolve(specifier,context,next){if(specifier==='@opencode-ai/plugin')return next(pathToFileURL(path.join(root,'.opencode/node_modules/@opencode-ai/plugin/dist/index.js')).href,context);return next(specifier,context);}});
const {default:plugin}=await import('../../.opencode/plugins/liuren-adjudication.ts');
const hash=s=>createHash('sha256').update(s).digest('hex');
const active=JSON.parse(await fs.readFile(path.join(root,'.opencode/liuren-active.json'),'utf8'));
const manifest=JSON.parse(await fs.readFile(path.join(root,active.runtime,'manifest.json'),'utf8'));
const chart=await runResolvedChart({datetime:'2026-10-18T13:22'},{persist:false});
async function harness(t,{missing=[],text='姐姐的女儿参加转校考试，能否转入？'}={}){
 const folder=await fs.mkdtemp(path.join(os.tmpdir(),'liuren-flow-test-'));
 t.after(async()=>{assert.equal(path.dirname(path.resolve(folder)),path.resolve(os.tmpdir()));assert.ok(path.basename(folder).startsWith('liuren-flow-test-'));await fs.rm(folder,{recursive:true,force:true});});
 const pointer={...active,flowControl:{enabled:true}};
 for(const rel of ['tools/liuren-direct/legacy-engine-manifest.json','排盘工具魔改/js/lunar.js',active.runtime+'/manifest.json',active.runtime+'/references/shensha-policy.json',active.runtime+'/references/adjudicator-book-evidence.json',active.runtime+'/methods/timing.md',active.runtime+'/methods/quantity.md',active.runtime+'/references/quantity-sources.md']){const dst=path.join(folder,rel);await fs.mkdir(path.dirname(dst),{recursive:true});await fs.copyFile(path.join(root,rel),dst);}
 await fs.mkdir(path.join(folder,'.opencode'),{recursive:true});await fs.writeFile(path.join(folder,'.opencode/liuren-active.json'),JSON.stringify(pointer));
 const methodParts=[];
 for(const id of manifest.required.filter(id=>!missing.includes(id))){
  const body=(await fs.readFile(path.join(root,active.runtime,manifest.modules[id].file),'utf8')).replaceAll('\r\n','\n');
  const meta={module:id,release:active.release,fileSha256:manifest.files[manifest.modules[id].file],textSha256:hash(body)};
  methodParts.push({type:'tool',tool:'liuren_materials',state:{status:'completed',output:'LIUREN_METHOD_BEGIN '+JSON.stringify(meta)+'\n'+body+'\nLIUREN_METHOD_END '+JSON.stringify({module:id,textSha256:hash(body)})}});
 }
 const childParts=[],client={session:{get:async()=>({data:{parentID:'parent'}}),messages:async({path:{id}})=>({data:id==='parent'?[{info:{role:'user'},parts:[{type:'text',text}]},{info:{role:'assistant'},parts:methodParts}]:[{info:{role:'user'},parts:[{type:'text',text:saved?.task_prompt}]},{info:{role:'assistant'},parts:childParts}]})}};
 let hooks=await plugin({directory:folder,client}),saved;
 const input=()=>{const p=packet();p.chart={source:'synthetic live engine test',facts:structuredClone(chart.facts)};p.entities[0].branch='丑';delete p.entities[0].position;p.questions[0].task_basis=[{task:'outcome',origin:'user_requested',request_quote:'能否转入',reason:'原问成败'}];return p;};
 const output=()=>{const r=result();r.entity_checks[0].branch='丑';for(const k of ['position','five_qi','twelve_states','site_yin','shenjiang'])delete r.entity_checks[0][k];r.special_methods=[];r.calculations=[];r.relation_checks[0].application={object:'合成',mechanism:'合成',stage:'合成',goal_effect:'合成',alternative_resolution:'合成'};return r;};
 const save=async(p=input())=>saved=JSON.parse(await hooks.tool.liuren_adjudication_packet.execute({packet:hooks.tool.liuren_adjudication_packet.args.packet.parse(p)},{agent:'liuren',sessionID:'parent'}));
 const event={tool:'task',sessionID:'parent',callID:'first'};
 const start=()=>hooks['tool.execute.before'](event,{args:{subagent_type:'liuren-adjudicator',prompt:saved.task_prompt}});
 const read=async()=>{let pages=1;for(let page=1;page<=pages;page++){const a={file_path:saved.file_path,sha256:saved.sha256,page};const raw=await hooks.tool.liuren_adjudication_read.execute(a,{agent:'liuren-adjudicator',sessionID:'child'});pages=JSON.parse(raw).pages;childParts.push({type:'tool',tool:'liuren_adjudication_read',state:{status:'completed',input:a,output:raw}});}return pages;};
 const submit=async(r=output())=>JSON.parse(await hooks.tool.liuren_adjudication_submit.execute({result:hooks.tool.liuren_adjudication_submit.args.result.parse(r)},{agent:'liuren-adjudicator',sessionID:'child'}));
 const finish=async(r)=>{const o={output:JSON.stringify(r),metadata:{sessionId:'child'}};await hooks['tool.execute.after'](event,o);return o;};
 const get=async(action='read')=>JSON.parse(await hooks.tool.liuren_adjudication_result.execute({action,task_id:'child'},{agent:'liuren',sessionID:'parent'}));
 const acknowledge=async()=>{const event={tool:'task_result',sessionID:'parent',callID:'ack'};await hooks['tool.execute.before'](event,{args:{task_id:'child'}});await hooks['tool.execute.after'](event,{output:'Existing task result',metadata:{}});};
 const restart=async()=>{hooks=await plugin({directory:folder,client});};
 return {get hooks(){return hooks;},folder,input,output,save,start,read,submit,finish,get,restart,event,childParts,acknowledge,client};
}
test('current native packet rejects missing tasks and manual chart_checked at entry',async t=>{
 const h=await harness(t),p=h.input();delete p.questions[0].tasks;assert.throws(()=>h.hooks.tool.liuren_adjudication_packet.args.packet.parse(p));
 p.questions[0].tasks=['outcome'];p.observations[0].verification='chart_checked';assert.throws(()=>h.hooks.tool.liuren_adjudication_packet.args.packet.parse(p));
});
test('preparation reports the precise missing module before saving/dispatch',async t=>{const h=await harness(t,{missing:['engine-shensha-output']});await assert.rejects(()=>h.save(),/MISSING_METHODS.*engine-shensha-output/);});
test('original kinship label cannot silently become a different family relation',async t=>{const h=await harness(t),p=h.input();p.questions[0].subject='侄女';await assert.rejects(()=>h.save(p),/INPUT_PREFLIGHT.*外甥女/);});
test('a supplied divination date is not an explicit timing question',async t=>{const h=await harness(t,{text:'能否转入？时间：2024年1月15日15:23'}),p=h.input();p.questions[0].tasks.push('timing');p.questions[0].task_basis.push({task:'timing',origin:'user_requested',request_quote:'时间：2024年1月15日15:23',reason:'测算时间'});await assert.rejects(()=>h.save(p),/INPUT_PREFLIGHT/);});
test('normal scoped file -> structured submit -> receipt -> checked result -> full report',async t=>{
 const h=await harness(t);const saved=await h.save();const raw=await fs.readFile(saved.file_path,'utf8');assert.equal(raw.includes('\n  '),false);
 await h.start();await h.read();const receipt=await h.submit();assert.equal(receipt.status,'completed');
 const done=await h.finish(receipt);assert.equal(JSON.parse(done.output).status,'completed');assert.equal(done.metadata.liurenAdjudication.contractChecked,true);
 await h.acknowledge();const deliver=await h.get('deliver');assert.match(deliver.report_markdown,/接口测试通过/);assert.ok(deliver.report_ref.sha256);assert.ok(deliver.result_ref.sha256);
});
test('native submit rejects mixed branch explanations before committing a report',async t=>{const h=await harness(t),r=h.output();r.entity_checks[0].branch='丑（初传）';assert.throws(()=>h.hooks.tool.liuren_adjudication_submit.args.result.parse(r),/branch/);});
test('all identifiable format errors are reported together, without changing a verdict',()=>{
 const p=packet(),r=result();r.entity_checks[0].branch='丑（寅宫）';r.entity_checks.push({...r.entity_checks[0],id:'J1',branch:'午带申'});r.special_methods=[{kind:'timing',status:'completed',record:{}}];
 const checked=checkSubmission(root,r,p);assert.equal(checked.ok,false);assert.ok(checked.issues.length>5);assert.equal(r.answers[0].verdict,'接口测试通过');assert.ok(checked.issues.some(e=>e.path==='/entity_checks/1/branch'));
});
test('local syntax retry stays in the same child, without re-reading or re-adjudication',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();const bad=h.output();bad.issue_resolutions=[];
 const failed=await h.submit(bad);assert.equal(failed.status,'invalid_output');assert.ok(failed.result_ref);assert.ok(failed.issues.length);
 const fixed=await h.submit(h.output());assert.equal(fixed.task_id,failed.task_id);assert.equal(fixed.status,'completed');await h.finish(fixed);
});
test('same-material completed or invalid work cannot be dispatched again',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();const bad=h.output();bad.entity_checks[0].branch='丑（寅宫）';await h.finish(bad);
 await h.acknowledge();const again=await h.save();await assert.rejects(()=>h.hooks['tool.execute.before']({...h.event,callID:'second'},{args:{subagent_type:'liuren-adjudicator',prompt:again.task_prompt}}),/NO_DUPLICATE_ADJUDICATION/);
});
test('task_result cannot bypass validation of a previously rejected report',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();const bad=h.output();bad.entity_checks[0].branch='丑（寅宫）';await h.finish(bad);
 const event={tool:'task_result',sessionID:'parent',callID:'retrieve'};await h.hooks['tool.execute.before'](event,{args:{task_id:'child'}});const o={output:JSON.stringify(bad),metadata:{}};
 await h.hooks['tool.execute.after'](event,o);assert.equal(JSON.parse(o.output).status,'invalid_output');assert.equal(o.metadata.liurenAdjudication.contractChecked,false);
});
test('verified result and ownership survive plugin restart',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();await h.finish(await h.submit());await h.restart();assert.equal((await h.get()).result.status,'completed');});
test('result artifacts are hash checked when retrieved',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();await h.finish(await h.submit());const r=await h.get();await fs.appendFile(r.execution_receipt.result_ref.path,' ');await assert.rejects(()=>h.get(),/ARTIFACT_CHANGED/);});
test('deliver requires the report guide, while dispatch does not require it early',async t=>{const h=await harness(t,{missing:['report']});await h.save();await h.start();await h.read();await h.finish(await h.submit());await h.acknowledge();await assert.rejects(()=>h.get('deliver'),/MISSING_METHODS.*report/);});
test('no silent unbounded format-repair loop',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();const bad=h.output();bad.issue_resolutions=[];for(let i=0;i<3;i++)await h.submit(bad);await assert.rejects(()=>h.submit(bad),/FORMAT_REPAIR_LIMIT/);});

test('a completed result must be acknowledged before delivery',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();await h.finish(await h.submit());await assert.rejects(()=>h.get('deliver'),/TASK_RESULT_ACK_REQUIRED/);});

test('a successful submission survives wrapper noise and cannot be replaced',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();await h.submit();const done=await h.finish({extra:'unexpected final prose wrapper'});assert.equal(JSON.parse(done.output).status,'completed');const r=h.output();r.answers[0].verdict='不得覆盖';await assert.rejects(()=>h.submit(r),/RESULT_ALREADY_ACCEPTED/);assert.equal((await h.get()).result.answers[0].verdict,'接口测试通过');});

test('an active child resumes its scoped read authorization after plugin restart',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();await h.restart();assert.equal((await h.submit()).status,'completed');});

test('a missing-input result permits one evidenced recheck and no third round',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();const r=h.output();r.status='needs_input';r.missing_inputs=['合成必要材料'];await h.finish(await h.submit(r));await h.acknowledge();
 const retry=h.input();retry.retry_context={previous_task_id:'child',reason:'补充合成必要材料'};
 const unchanged=await h.save(retry);await assert.rejects(()=>h.hooks['tool.execute.before']({...h.event,callID:'without-new'},{args:{subagent_type:'liuren-adjudicator',prompt:unchanged.task_prompt}}),/RETRY_WITHOUT_NEW_MATERIAL/);
 retry.facts.push({id:'F1',text:'合成新增事实',source:'测试用户'});const saved=await h.save(retry);
 await h.hooks['tool.execute.before']({...h.event,callID:'second'},{args:{subagent_type:'liuren-adjudicator',prompt:saved.task_prompt}});
 const f=await store(h.folder),p=JSON.parse(await fs.readFile(saved.file_path,'utf8')).packet;
 await f.bind('parent','child2',{file_path:saved.file_path,sha256:saved.sha256},'second');await f.saveResult('parent','child2',p,{},r,{pagesVerified:true});await f.acknowledge('parent','child2');
 retry.retry_context.previous_task_id='child2';retry.facts.push({id:'F2',text:'另一个新增事实',source:'测试用户'});const third=await h.save(retry);
 await assert.rejects(()=>h.hooks['tool.execute.before']({...h.event,callID:'third'},{args:{subagent_type:'liuren-adjudicator',prompt:third.task_prompt}}),/NO_DUPLICATE_ADJUDICATION/);
});

test('a completed factual recheck needs a real error path and new evidence',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();await h.finish(await h.submit());await h.acknowledge();
 const p=h.input();p.retry_context={previous_task_id:'child',reason:'具体实体错误',error_path:'/entity_checks/9/branch'};p.facts.push({id:'F1',text:'合成新事实',source:'测试用户'});let saved=await h.save(p);
 await assert.rejects(()=>h.hooks['tool.execute.before']({...h.event,callID:'bad-path'},{args:{subagent_type:'liuren-adjudicator',prompt:saved.task_prompt}}),/RECHECK_ERROR_PATH_UNKNOWN/);
 p.retry_context.error_path='/entity_checks/0/branch';saved=await h.save(p);await h.hooks['tool.execute.before']({...h.event,callID:'evidenced'},{args:{subagent_type:'liuren-adjudicator',prompt:saved.task_prompt}});
});

test('an unbound host failure releases only the dispatch slot, retaining the failure',async t=>{
 const h=await harness(t);const saved=await h.save();await h.start();const out={output:'Synthetic host failure before child creation',metadata:{}};await h.hooks['tool.execute.after'](h.event,out);assert.equal(JSON.parse(out.output).status,'dispatch_failed');
 await h.hooks['tool.execute.before']({...h.event,callID:'retry-dispatch'},{args:{subagent_type:'liuren-adjudicator',prompt:saved.task_prompt}});
 const state=await (await store(h.folder)).read('parent');assert.equal(state.attempts[0].status,'dispatch_failed');assert.equal(state.attempts[1].status,'dispatching');
});

test('overlapping dispatch hooks cannot reserve the same objective twice',async t=>{const h=await harness(t);const saved=await h.save();const results=await Promise.allSettled(['parallel1','parallel2'].map(callID=>h.hooks['tool.execute.before']({...h.event,callID},{args:{subagent_type:'liuren-adjudicator',prompt:saved.task_prompt}})));assert.equal(results.filter(x=>x.status==='fulfilled').length,1);assert.equal(results.filter(x=>x.status==='rejected').length,1);});

test('legacy final text recovers only with verified full-page content receipts',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();h.childParts.push({type:'text',text:JSON.stringify(h.output())});await h.restart();assert.equal((await h.get()).status,'completed');});

test('a failed historical read is not a page receipt',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();h.childParts[0].state.output='An error, not file content';h.childParts.push({type:'text',text:JSON.stringify(h.output())});await h.restart();await assert.rejects(()=>h.get(),/FILE_NOT_FULLY_READ/);});

test('ordinary Build task_result output remains outside the Liuren hook',async t=>{const h=await harness(t);h.client.session.messages=async()=>({data:[{info:{role:'user'},parts:[{type:'text',text:'A regular Build task'}]}]});const event={tool:'task_result',sessionID:'parent',callID:'ordinary'};await h.hooks['tool.execute.before'](event,{args:{task_id:'build-child'}});const out={output:'Original Build result',metadata:{}};await h.hooks['tool.execute.after'](event,out);assert.equal(out.output,'Original Build result');});

test('delivery retains the actual book evidence locator used by adjudication',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();const r=h.output();r.relation_checks[0].basis_ids=['E01'];await h.finish(await h.submit(r));await h.acknowledge();assert.match((await h.get('deliver')).report_markdown,/E01：书籍库\/北海闲人\/理法简易.txt:2125-2150/);});

test('main-visible task receipt retains the child ID without requiring metadata or full report',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();const receipt=await h.submit();const done=await h.finish(receipt),visible=JSON.parse(done.output);assert.equal(visible.schema,'liuren-adjudication-receipt-v1');assert.equal(visible.task_id,'child');assert.deepEqual(visible.next_call,{tool:'task_result',arguments:{task_id:'child'}});assert.equal(visible.answers,undefined);assert.ok(done.output.length<2000);await h.acknowledge();const located=JSON.parse(await h.hooks.tool.liuren_adjudication_result.execute({action:'locate'},{agent:'liuren',sessionID:'parent'}));assert.equal(located.task_id,'child');assert.equal(located.next_call.arguments.action,'deliver');});

test('missing task ID can locate exactly one owned result after restart',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();await h.finish(await h.submit());await h.restart();const out=JSON.parse(await h.hooks.tool.liuren_adjudication_result.execute({action:'read'},{agent:'liuren',sessionID:'parent'}));assert.equal(out.task_id,'child');assert.equal(out.result.status,'completed');});

test('a request ID cannot be mistaken for the task ID and the error names owned candidates',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();await h.finish(await h.submit());await assert.rejects(()=>h.hooks.tool.liuren_adjudication_result.execute({action:'read',task_id:'synthetic_v2'},{agent:'liuren',sessionID:'parent'}),/TASK_ID_NOT_OWNED.*child/);await assert.rejects(()=>h.hooks['tool.execute.before']({tool:'task_result',sessionID:'parent',callID:'wrong-request-id'},{args:{task_id:'synthetic_v2'}}),/TASK_ID_NOT_OWNED.*child/);});

test('two owned results require explicit choice instead of silently picking latest',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();await h.finish(await h.submit());const f=await store(h.folder),saved=await f.result('parent','child');await f.saveResult('parent','child2',saved.data.packet,saved.data.request_ref,h.output(),{pagesVerified:true});await assert.rejects(()=>h.hooks.tool.liuren_adjudication_result.execute({action:'locate'},{agent:'liuren',sessionID:'parent'}),/TASK_ID_AMBIGUOUS.*child2/);});

test('result discovery never exposes another parent session results',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();await h.finish(await h.submit());await assert.rejects(()=>h.hooks.tool.liuren_adjudication_result.execute({action:'locate'},{agent:'liuren',sessionID:'another-parent'}),/NO_SAVED_RESULT/);});
