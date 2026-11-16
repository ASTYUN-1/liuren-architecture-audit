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
async function harness(t,{missing=[],text='姐姐的女儿参加转校考试，能否转入？',eventPolicy=false}={}){
 const folder=await fs.mkdtemp(path.join(os.tmpdir(),'liuren-flow-test-'));
 t.after(async()=>{assert.equal(path.dirname(path.resolve(folder)),path.resolve(os.tmpdir()));assert.ok(path.basename(folder).startsWith('liuren-flow-test-'));await fs.rm(folder,{recursive:true,force:true});});
 const pointer={...active,compactHandoff:{enabled:false},flowControl:{enabled:true},eventPositioning:{enabled:eventPolicy}};
 for(const rel of ['tools/liuren-direct/legacy-engine-manifest.json','排盘工具魔改/js/lunar.js',active.runtime+'/manifest.json',active.runtime+'/references/shensha-policy.json',active.runtime+'/references/adjudicator-book-evidence.json',active.runtime+'/methods/positioning.md',active.runtime+'/domains/finance.md',active.runtime+'/domains/exam.md',active.runtime+'/domains/illness.md',active.runtime+'/methods/timing.md',active.runtime+'/methods/quantity.md',active.runtime+'/references/quantity-sources.md']){const dst=path.join(folder,rel);await fs.mkdir(path.dirname(dst),{recursive:true});await fs.copyFile(path.join(root,rel),dst);}
 await fs.mkdir(path.join(folder,'.opencode'),{recursive:true});await fs.writeFile(path.join(folder,'.opencode/liuren-active.json'),JSON.stringify(pointer));
 const methodParts=[];
 for(const id of [...manifest.required,'finance','exam','illness'].filter(id=>!missing.includes(id))){
  const body=(await fs.readFile(path.join(root,active.runtime,manifest.modules[id].file),'utf8')).replaceAll('\r\n','\n');
  const meta={module:id,release:active.release,fileSha256:manifest.files[manifest.modules[id].file],textSha256:hash(body)};
  methodParts.push({type:'tool',tool:'liuren_materials',state:{status:'completed',output:'LIUREN_METHOD_BEGIN '+JSON.stringify(meta)+'\n'+body+'\nLIUREN_METHOD_END '+JSON.stringify({module:id,textSha256:hash(body)})}});
 }
 const childParts=[],childInfo={role:'assistant',id:'msg_initial'},continuations=[],client={session:{get:async()=>({data:{parentID:'parent'}}),messages:async({path:{id}})=>({data:id==='parent'?[{info:{role:'user'},parts:[{type:'text',text}]},{info:{role:'assistant'},parts:methodParts}]:[{info:{role:'user'},parts:[{type:'text',text:saved?.task_prompt}]},{info:childInfo,parts:childParts},...continuations]})}};
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
 const acknowledge=async()=>{const event={tool:'task_result',sessionID:'parent',callID:'ack'};await hooks['tool.execute.before'](event,{args:{task_id:'child'}});const out={output:'Existing task result',metadata:{}};await hooks['tool.execute.after'](event,out);return JSON.parse(out.output);};
 const restart=async()=>{hooks=await plugin({directory:folder,client});};
 return {get hooks(){return hooks;},folder,input,output,save,start,read,submit,finish,get,restart,event,childParts,childInfo,continuations,acknowledge,client};
}

test('length with no public text bypasses the impossible host claim and continues the same child once',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();
 h.childInfo.finish='length';h.childParts.push({type:'reasoning',text:'PRIVATE_REASONING_MUST_NEVER_BECOME_REPORT'});
 const receipt=JSON.parse((await h.finish('Task ended without a public text result')).output);
 assert.equal(receipt.status,'invalid_output');assert.equal(receipt.next_call.tool,'liuren_adjudication_result');
 const invalid=await h.get();assert.equal(invalid.has_report,false);assert.equal(invalid.recovery_available,true);assert.equal(invalid.next_call.arguments.action,'recover');
 let calls=0;
 h.client.session.prompt=async({path:{id},body})=>{
  calls++;assert.equal(id,'child');assert.equal(body.agent,'liuren-adjudicator');assert.deepEqual(body.model,{providerID:'deepseek',modelID:'deepseek-flash'});
  h.continuations.push({info:{role:'user',id:body.messageID},parts:body.parts});await h.restart();
  const saved=await h.submit('原会话恢复后正式技术报告');
  h.continuations.push({info:{role:'assistant',finish:'stop'},parts:[{type:'text',text:JSON.stringify(saved)}]});return {data:{}};
 };
 const recovered=await h.get('recover');assert.equal(recovered.status,'completed');assert.equal(recovered.result,'原会话恢复后正式技术报告');
 assert.equal((await h.get('deliver')).report_markdown,'原会话恢复后正式技术报告');
 await h.get('recover');assert.equal(calls,1);
 const state=await (await store(h.folder)).read('parent');assert.equal(state.attempts.length,1);assert.equal(state.recoveries.child.status,'completed');
 const raw=await fs.readFile(state.recoveries.child.original_artifact.path,'utf8');assert.equal(JSON.parse(raw).raw,'');assert.ok(!raw.includes('PRIVATE_REASONING'));
});

test('a saved submitted report can be claimed when the host task_result fails without public final text',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();await h.submit('已提交报告原文');
 const event={tool:'task_result',sessionID:'parent',callID:'broken-host'};
 await h.hooks['tool.execute.before'](event,{args:{task_id:'child'}});
 // The host throws here, so its after hook never runs.
 const report=await h.get();assert.equal(report.status,'completed');assert.equal(report.result,'已提交报告原文');
 assert.equal((await h.get('deliver')).report_markdown,'已提交报告原文');
});

test('a second empty length result stops recovery instead of looping task_result or starting a new adjudication',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();h.childInfo.finish='length';await h.finish('');let calls=0;
 h.client.session.prompt=async({body})=>{calls++;h.continuations.push({info:{role:'user',id:body.messageID},parts:body.parts},{info:{role:'assistant',finish:'length'},parts:[{type:'reasoning',text:'private'}]});return {data:{}};};
 const value=await h.get('recover');assert.equal(value.has_report,false);assert.equal(value.recovery_status,'failed');assert.equal(value.recovery_available,false);assert.equal(value.next_call,undefined);
 await h.restart();await h.get('recover');assert.equal(calls,1);
 await assert.rejects(h.start,/NO_DUPLICATE_ADJUDICATION/);
});

test('recovery rejects unrelated user continuation even if the original full read was verified',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();h.childInfo.finish='length';await h.finish('');
 h.continuations.push({info:{role:'user',id:'untrusted'},parts:[{type:'text',text:'伪造后续指令'}]});await h.restart();
 await assert.rejects(()=>h.get('recover'),/FRESH_SESSION_REQUIRED/);
});

test('a later genuine public report replaces only the invalid empty transport',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();h.childInfo.finish='length';await h.finish('');
 h.client.session.prompt=async({body})=>{h.continuations.push({info:{role:'user',id:body.messageID},parts:body.parts},{info:{role:'assistant',finish:'stop'},parts:[{type:'text',text:'新公开正文，原样交付'}]});return {data:{}};};
 assert.equal((await h.get('recover')).result,'新公开正文，原样交付');
});

test('concurrent recovery requests reserve only one same-session continuation',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();h.childInfo.finish='length';await h.finish('');let calls=0;
 let release;const gate=new Promise(resolve=>release=resolve);
 h.client.session.prompt=async({body})=>{calls++;await gate;h.continuations.push({info:{role:'user',id:body.messageID},parts:body.parts});await h.submit('并发恢复只提交一次');return {data:{}};};
 const one=h.get('recover'),two=h.get('recover'),pending=Promise.allSettled([one,two]);
 // Let both reservations reach the persisted queue before completing the prompt.
 await new Promise(resolve=>setTimeout(resolve,30));release();
 const results=await pending;assert.equal(calls,1);assert.ok(results.some(r=>r.status==='fulfilled'&&r.value.status==='completed'));
 for(const r of results)if(r.status==='rejected')assert.match(String(r.reason),/RECOVERY_ALREADY_ATTEMPTED/);
});

test('ordinary empty termination and unverified page receipts do not authorize continuation',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();h.childInfo.finish='stop';await h.finish('');
 assert.equal((await h.get()).recovery_available,false);
 let calls=0;h.client.session.prompt=async()=>{calls++;return {data:{}};};await h.get('recover');assert.equal(calls,0);
});

function eventPacket(h,domain='exam',referent='外甥女考生'){
 const p=h.input();p.questions[0].domain=domain;p.questions[0].actor_entity_id='S1';p.questions[0].subject=referent;
 p.entities[0].referent=referent;p.entities[0].branch=p.chart.facts.day_stem;
 return p;
}

test('locate discovers the only bound unfinished child without saving a fake empty failure',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();
 h.childParts.push({type:'text',text:'尚在执行的公开前言，不是最终报告'});
 const value=JSON.parse(await h.hooks.tool.liuren_adjudication_result.execute({action:'locate'},{agent:'liuren',sessionID:'parent'}));
 assert.equal(value.status,'running');assert.equal(value.task_id,'child');assert.equal(value.has_report,false);
 assert.deepEqual((await (await store(h.folder)).read('parent')).results,{});
 await assert.rejects(()=>h.hooks['tool.execute.before']({tool:'task_result',sessionID:'parent',callID:'early'},{args:{task_id:'child'}}),/TASK_STILL_RUNNING/);
});

test('locate reconciles an ended owned child after losing the host task return',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();h.childInfo.finish='stop';h.childParts.push({type:'text',text:'宿主返回丢失，子会话已存公开正文'});await h.restart();
 const value=JSON.parse(await h.hooks.tool.liuren_adjudication_result.execute({action:'locate'},{agent:'liuren',sessionID:'parent'}));
 assert.equal(value.status,'completed');assert.equal(value.task_id,'child');assert.equal((await h.get()).result,'宿主返回丢失，子会话已存公开正文');
});

test('workflow exposes stale loaded code and blocks new dispatch while preserving saved reports',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();await h.submit('旧进程已存报告仍可读取');
 const pathPointer=path.join(h.folder,'.opencode/liuren-active.json'),pointer=JSON.parse(await fs.readFile(pathPointer,'utf8'));
 pointer.workflowImplementation['.opencode/plugins/liuren-adjudication.ts']='f'.repeat(64);await fs.writeFile(pathPointer,JSON.stringify(pointer));
 const health=JSON.parse(await h.hooks.tool.liuren_tool_help.execute({topic:'workflow',domains:['exam']},{agent:'liuren',sessionID:'parent'})).execution_health;
 assert.equal(health.ready,false);assert.equal(health.mismatches[0].file,'.opencode/plugins/liuren-adjudication.ts');
 await assert.rejects(()=>h.save(),/PLUGIN_RELOAD_REQUIRED/);await assert.rejects(h.start,/PLUGIN_RELOAD_REQUIRED/);
 assert.equal((await h.get()).result,'旧进程已存报告仍可读取');
});

test('restart reconciles an interrupted recovery whose continuation ended empty',async t=>{
 const h=await harness(t);const saved=await h.save();await h.start();await h.read();h.childInfo.finish='length';await h.finish('');
 const f=await store(h.folder),prompt='trusted continuation',message_id='msg_recovery';
 await f.reserveRecovery('parent','child',{file_path:saved.file_path,sha256:saved.sha256},{prompt,message_id,last_message_id:h.childInfo.id});
 h.continuations.push({info:{role:'user',id:message_id},parts:[{type:'text',text:prompt}]},{info:{role:'assistant',id:'msg_final',finish:'length'},parts:[]});await h.restart();
 const value=await h.get();assert.equal(value.recovery_status,'failed');assert.equal(value.recovery_available,false);
});
test('workflow help lists only missing current methods and exact calls before saving',async t=>{
 const h=await harness(t,{eventPolicy:true,missing:['exam','judgment-core']});
 const value=JSON.parse(await h.hooks.tool.liuren_tool_help.execute({topic:'workflow',domains:['exam']},{agent:'liuren',sessionID:'parent'}));
 assert.equal(value.readiness.ready,false);
 assert.deepEqual(value.readiness.missing.sort(),['exam','judgment-core']);
 assert.equal(value.readiness.next_calls.length,2);
 assert.ok(value.readiness.next_calls.every(c=>c.tool==='liuren_materials'&&c.arguments.action==='method'));
});

test('module IDs assemble full current sources once and preserve automatic IDs as verified aliases',async t=>{
 const h=await harness(t,{eventPolicy:true}),p=eventPacket(h);p.method_materials=[];p.method_modules=['positioning','exam'];
 const saved=await h.save(p),body=JSON.parse(await fs.readFile(saved.file_path,'utf8')).packet;
 assert.equal(body.method_modules,undefined);assert.equal(body.method_materials.length,2);assert.equal(body.material_aliases.length,2);
 for(const alias of body.material_aliases){
  const target=body.method_materials.find(m=>m.id===alias.canonical_id);assert.ok(target.quote.length);assert.equal(alias.sha256,target.sha256);assert.equal(alias.source_path,target.source_path);assert.equal(alias.quote,undefined);
 }
 assert.deepEqual(body.event_positioning.method_ids,['M_EVENT_POSITIONING','M_DOMAIN_exam']);
 await h.start();const texts=[];let args={file_path:saved.file_path,sha256:saved.sha256,page:1,page_count:4},last;
 do{
  const response=await h.hooks.tool.liuren_adjudication_read.execute(args,{agent:'liuren-adjudicator',sessionID:'child'});last=JSON.parse(response.output);
  texts.push(last.content);h.childParts.push({type:'tool',tool:'liuren_adjudication_read',state:{status:'completed',input:args,output:response.output}});args=last.next_call?.arguments;
 }while(args);
 assert.equal(texts.join(''),await fs.readFile(saved.file_path,'utf8'));
 await h.restart();await h.finish(await h.submit('完整读取后提交的合成正文'));await h.acknowledge();assert.equal((await h.get('deliver')).report_markdown,'完整读取后提交的合成正文');
});

test('module assembly rejects unknown names without dropping explicit book references',async t=>{
 const h=await harness(t),p=h.input();p.method_modules=['../../opencode.json'];await assert.rejects(()=>h.save(p),/unknown method_modules/);
});

test('one completed method batch records each verified module receipt',async t=>{
 const h=await harness(t,{missing:['relations','liqi']});let output='';
 for(const module of ['relations','liqi']){
  const body=(await fs.readFile(path.join(root,active.runtime,manifest.modules[module].file),'utf8')).replaceAll('\r\n','\n');
  const meta={module,release:active.release,fileSha256:manifest.files[manifest.modules[module].file],textSha256:hash(body)};
  output+='LIUREN_METHOD_BEGIN '+JSON.stringify(meta)+'\n'+body+'\nLIUREN_METHOD_END '+JSON.stringify({module,textSha256:hash(body)})+'\n';
 }
 await h.hooks['tool.execute.after']({tool:'liuren_materials',sessionID:'parent',callID:'batch'},{output,metadata:{}});
 const value=JSON.parse(await h.hooks.tool.liuren_tool_help.execute({topic:'workflow',domains:['exam']},{agent:'liuren',sessionID:'parent'}));
 assert.equal(value.readiness.ready,true);assert.deepEqual(value.readiness.missing,[]);
});

test('child deterministic calculation receipts survive submit and restart without changing its report',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();
 const request={action:'calendar',calendar:{start:'2027-01-21',end:'2027-01-22',timezone:'Asia/Shanghai',day_boundary:'civil-midnight'}};
 const original=JSON.parse(await h.hooks.tool.liuren_compute.execute(request,{agent:'liuren-adjudicator',sessionID:'child'}));
 await h.hooks.tool.liuren_compute.execute(request,{agent:'liuren-adjudicator',sessionID:'child'});
 await h.finish(await h.submit('日期与条件见原报告，不改结论'));await h.restart();await h.acknowledge();
 const delivered=await h.get('deliver');assert.equal(delivered.calculation_receipts.length,1);assert.deepEqual(delivered.calculation_receipts[0].result,original);assert.equal(delivered.calculation_receipts[0].ref.sha256.length,64);assert.equal(delivered.report_markdown,'日期与条件见原报告，不改结论');
});

test('event workflow blocks a missing classification instead of silently using generic methods',async t=>{
 const h=await harness(t,{eventPolicy:true}),p=eventPacket(h);delete p.questions[0].domain;
 await assert.rejects(()=>h.save(p),e=>e.issues?.some(issue=>JSON.stringify(issue.path)===JSON.stringify(['questions',0,'domain'])&&issue.values?.includes('illness')));
});
test('event workflow requires the actual selected domain receipt, not only generic coverage',async t=>{
 const h=await harness(t,{eventPolicy:true,missing:['exam']});
 await assert.rejects(()=>h.save(eventPacket(h)),/MISSING_METHODS.*exam/);
});
test('exam packets do not require or programmatically bind an actor to the day stem',async t=>{
 const h=await harness(t,{eventPolicy:true});
 for(const branch of ['子','丑','申']){const p=eventPacket(h);delete p.questions[0].actor_entity_id;p.entities[0].branch=branch;const saved=await h.save(p);const body=JSON.parse(await fs.readFile(saved.file_path,'utf8')).packet;assert.equal(body.entities[0].branch,branch);assert.equal(body.event_positioning.questions[0].actor_entity_id,undefined);}
});

test('illness packets leave patient mapping to the model while retaining the original question',async t=>{
 const h=await harness(t,{eventPolicy:true,text:'父亲生病，治疗后能否恢复？'}),p=eventPacket(h,'illness','患病父亲');
 p.questions[0].task_basis[0].request_quote='能否恢复';delete p.questions[0].actor_entity_id;p.entities[0].branch='丑';
 const body=JSON.parse(await fs.readFile((await h.save(p)).file_path,'utf8')).packet;
 assert.equal(body.entities[0].branch,'丑');assert.match(body.input_origin.source_text,/父亲生病/);
});

test('legacy optional actor labels are not interpreted by program semantic rules',async t=>{
 const h=await harness(t,{eventPolicy:true}),p=eventPacket(h);p.questions[0].actor_entity_id='old-optional-label';
 const body=JSON.parse(await fs.readFile((await h.save(p)).file_path,'utf8')).packet;
 assert.equal(body.questions[0].actor_entity_id,'old-optional-label');assert.equal(body.event_positioning.questions[0].actor_entity_id,undefined);
});

test('scoped event packet carries complete current positioning and selected domain without extra model calls',async t=>{
 const h=await harness(t,{eventPolicy:true}),p=eventPacket(h),saved=await h.save(p),body=JSON.parse(await fs.readFile(saved.file_path,'utf8')).packet;
 assert.equal(body.event_positioning.questions[0].domain,'exam');assert.equal(body.event_positioning.questions[0].actor_entity_id,undefined);
 for(const [id,rel] of [['M_EVENT_POSITIONING','methods/positioning.md'],['M_DOMAIN_exam','domains/exam.md']]){
  const material=body.method_materials.find(m=>m.id===id),full=(await fs.readFile(path.join(root,active.runtime,rel),'utf8')).replaceAll('\r\n','\n').trim();
  assert.equal(material.quote.trim(),full);assert.equal(material.sha256,hash(await fs.readFile(path.join(root,active.runtime,rel),'utf8')));
 }
 assert.equal(body.method_materials.some(m=>m.id==='M_DOMAIN_illness'),false);
});
test('adjudicator may correct entity mapping without a program output-role lock',async t=>{
 const h=await harness(t,{eventPolicy:true});await h.save(eventPacket(h));await h.start();await h.read();
 const corrected=h.output();corrected.entity_checks[0].referent='外甥女考生';corrected.entity_checks[0].branch='丑';corrected.entity_checks[0].mapping_review='合成协议测试：由模型解释取用，程序仅核坐标和字段';
 corrected.scope_review.mapping_status='corrected';corrected.scope_review.corrections=['合成测试中修订实体取用；程序不锁定角色'];
 const response=await h.submit(corrected);assert.equal(response.status,'completed',JSON.stringify(response));
});

test('legacy actor references remain compatible while generated metadata contains no actor binding',async t=>{
 const h=await harness(t,{eventPolicy:true}),p=eventPacket(h);p.entities[0].id='E01';p.questions[0].actor_entity_id='E01';p.observations[0].entity_ids=['E01'];p.focus_issues[0].entity_ids=['E01'];
 const saved=await h.save(p),body=JSON.parse(await fs.readFile(saved.file_path,'utf8')).packet;
 assert.equal(body.questions[0].actor_entity_id,body.entities[0].id);assert.equal(body.event_positioning.questions[0].actor_entity_id,undefined);assert.notEqual(body.entities[0].id,'E01');
});
test('event policy preserves a specialty relation axis instead of forcing every person into day stem',async t=>{
 const h=await harness(t,{eventPolicy:true}),p=h.input();p.questions[0].domain='finance';
 assert.equal(p.entities[0].branch,'丑');const saved=await h.save(p),body=JSON.parse(await fs.readFile(saved.file_path,'utf8')).packet;
 assert.equal(body.entities[0].branch,'丑');assert.ok(body.method_materials.some(m=>m.id==='M_DOMAIN_finance'));
});
test('current native packet rejects missing tasks and manual chart_checked at entry',async t=>{
 const h=await harness(t),p=h.input();delete p.questions[0].tasks;assert.throws(()=>h.hooks.tool.liuren_adjudication_packet.args.packet.parse(p));
 p.questions[0].tasks=['outcome'];p.observations[0].verification='chart_checked';assert.throws(()=>h.hooks.tool.liuren_adjudication_packet.args.packet.parse(p));
});

test('native IDs and array limits match the execution contract, including numeric request IDs',async t=>{
 const h=await harness(t),schema=h.hooks.tool.liuren_adjudication_packet.args.packet;
 for(const request_id of ['20261106-a','6c7b962a-819b-44c2-95df-2240accaf974','x'.repeat(128)]){const p=h.input();p.request_id=request_id;assert.equal(schema.parse(p).request_id,request_id);}
 const bad=h.input();bad.facts=[{id:'2026fact',text:'事实',source:'测试'}];assert.throws(()=>schema.parse(bad),/facts/);
 const tooMany=h.input();tooMany.entities=Array.from({length:41},(_,i)=>({...tooMany.entities[0],id:'S'+i}));assert.throws(()=>schema.parse(tooMany),/entities/);
});
test('preparation reports the precise missing module before saving/dispatch',async t=>{const h=await harness(t,{missing:['judgment-core']});await assert.rejects(()=>h.save(),/MISSING_METHODS.*judgment-core/);});
test('kinship wording is preserved for the model rather than rejected by a regex',async t=>{const h=await harness(t),p=h.input();p.questions[0].subject='侄女';const body=JSON.parse(await fs.readFile((await h.save(p)).file_path,'utf8')).packet;assert.equal(body.questions[0].subject,'侄女');assert.match(body.input_origin.source_text,/姐姐的女儿/);});
test('a supplied divination date is not an explicit timing question',async t=>{const h=await harness(t,{text:'能否转入？时间：2024年1月15日15:23'}),p=h.input();p.questions[0].tasks.push('timing');p.questions[0].task_basis.push({task:'timing',origin:'user_requested',request_quote:'时间：2024年1月15日15:23',reason:'测算时间'});await assert.rejects(()=>h.save(p),/INPUT_PREFLIGHT/);});
test('normal scoped file -> structured submit -> receipt -> checked result -> full report',async t=>{
 const h=await harness(t);const saved=await h.save();const raw=await fs.readFile(saved.file_path,'utf8');assert.equal(raw.includes('\n  '),false);
 await h.start();await h.read();const receipt=await h.submit();assert.equal(receipt.status,'completed');
 const done=await h.finish(receipt);assert.equal(JSON.parse(done.output).status,'completed');assert.equal(done.metadata.liurenAdjudication.contractChecked,true);
 await h.acknowledge();const deliver=await h.get('deliver');assert.match(deliver.report_markdown,/接口测试通过/);assert.ok(deliver.report_ref.sha256);assert.ok(deliver.result_ref.sha256);
});
test('native submit accepts branch explanations as report content',async t=>{const h=await harness(t),r=h.output();r.entity_checks[0].branch='丑（初传）';assert.deepEqual(h.hooks.tool.liuren_adjudication_submit.args.result.parse(r),r);});

test('submit rechecks actual native-host receipts instead of trusting executed page counters',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();
 const original=h.childParts[0].state.output;
 h.childParts[0].state.output='... bytes truncated ...';h.childParts[0].state.metadata={truncated:true};
 await assert.rejects(()=>h.submit('材料未实际全部返回，不应验收'),/FILE_NOT_FULLY_READ/);
 h.childParts[0].state.output=original;h.childParts[0].state.metadata={truncated:false};
 assert.equal((await h.submit('完整回执恢复后才能提交')).status,'completed');
});

test('free report fields and conditional non-answers are preserved without content validation',()=>{
 const p=packet(),r=result();r.scope_review.question_notes='额外说明';r.answers[0].decisive_relation_ids=[];r.answers[0].verdict='原问条件未满足，此子问不答';delete r.relation_checks[0].application;r.自定义={依据:'按原问自然说明'};
 const before=structuredClone(r),checked=checkSubmission(root,r,p);assert.equal(checked.ok,true);assert.equal(checked.professionalContentChecked,false);assert.deepEqual(checked.result,before);assert.deepEqual(r,before);
});

test('an empty transport can be replaced in the same child without rereading',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();
 const failed=JSON.parse(await h.hooks.tool.liuren_adjudication_submit.execute({result:'   '},{agent:'liuren-adjudicator',sessionID:'child'}));assert.equal(failed.status,'invalid_output');
 const fixed=await h.submit('条件未满足，第四问依原问要求不答。其余判断及依据按正文说明。');assert.equal(fixed.task_id,failed.task_id);assert.equal(fixed.status,'completed');await h.finish(fixed);assert.equal((await h.get()).result,'条件未满足，第四问依原问要求不答。其余判断及依据按正文说明。');
});

test('same-material completed or invalid work cannot be dispatched again',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();const bad=h.output();bad.entity_checks[0].branch='丑（寅宫）';await h.finish(bad);
 await h.acknowledge();const again=await h.save();await assert.rejects(()=>h.hooks['tool.execute.before']({...h.event,callID:'second'},{args:{subagent_type:'liuren-adjudicator',prompt:again.task_prompt}}),/NO_DUPLICATE_ADJUDICATION/);
});
test('task_result retrieves arbitrary report fields without professional validation',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();const report={结论:'能修好',说明:'条件子问不适用',额外说明:['应期按支日讨论']};await h.finish(report);await h.acknowledge();const read=await h.get();assert.deepEqual(read.result,report);assert.equal(read.execution_receipt.professionalContentChecked,false);
});

test('verified result and ownership survive plugin restart',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();await h.finish(await h.submit());await h.restart();assert.equal((await h.get()).result.status,'completed');});
test('result artifacts are hash checked when retrieved',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();await h.finish(await h.submit());const r=await h.get();await fs.appendFile(r.execution_receipt.result_ref.path,' ');await assert.rejects(()=>h.get(),/ARTIFACT_CHANGED/);});
test('deliver requires the report guide, while dispatch does not require it early',async t=>{const h=await harness(t,{missing:['report']});await h.save();await h.start();await h.read();await h.finish(await h.submit());await h.acknowledge();await assert.rejects(()=>h.get('deliver'),/MISSING_METHODS.*report/);});

test('claim, locate and read guide missing report to an executable step, then deliver without a failed call',async t=>{
 const h=await harness(t,{missing:['report']});await h.save();await h.start();await h.read();const original='合成正文：保留主选日期、条件与来源';await h.finish(await h.submit(original));
 const claim=await h.acknowledge();
 assert.deepEqual(claim.next_call,{tool:'liuren_materials',arguments:{action:'method',module:'report'}});
 assert.equal(claim.delivery_readiness.ready,false);
 const locate=JSON.parse(await h.hooks.tool.liuren_adjudication_result.execute({action:'locate',task_id:'child'},{agent:'liuren',sessionID:'parent'}));
 assert.deepEqual(locate.next_call,claim.next_call);assert.deepEqual((await h.get()).next_call,claim.next_call);
 const body=(await fs.readFile(path.join(root,active.runtime,manifest.modules.report.file),'utf8')).replaceAll('\r\n','\n');
 const meta={module:'report',release:active.release,fileSha256:manifest.files[manifest.modules.report.file],textSha256:hash(body)};
 const out={output:'LIUREN_METHOD_BEGIN '+JSON.stringify(meta)+'\n'+body+'\nLIUREN_METHOD_END '+JSON.stringify({module:'report',textSha256:hash(body)}),metadata:{}};
 await h.hooks['tool.execute.after']({tool:'liuren_materials',sessionID:'parent',callID:'read-report'},out);
 const next=JSON.parse(out.output.split('\nLIUREN_WORKFLOW_CONTINUATION ')[1]);
 assert.equal(next.delivery_readiness.ready,true);
 assert.deepEqual(next.next_call,{tool:'liuren_adjudication_result',arguments:{action:'deliver',task_id:'child'}});
 const delivered=JSON.parse(await h.hooks.tool[next.next_call.tool].execute(next.next_call.arguments,{agent:'liuren',sessionID:'parent'}));
 assert.equal(delivered.report_markdown,original);assert.equal((await (await store(h.folder)).read('parent')).attempts.length,1);
});
test('repeated empty payload and repair calls are idempotent rather than consuming attempts',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();const f=await store(h.folder),p=h.input();
 const first=await f.saveResult('parent','child',p,{},'',{pagesVerified:true});for(let i=0;i<4;i++){await f.saveResult('parent','child',p,{},'',{pagesVerified:true});await h.get('repair');}
 assert.equal((await f.read('parent')).results.child.submissions,1);assert.equal((await f.result('parent','child')).artifact.sha256,first.result_ref.sha256);
});

test('a completed result must be acknowledged before delivery',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();await h.finish(await h.submit());await assert.rejects(()=>h.get('deliver'),/TASK_RESULT_ACK_REQUIRED/);});

test('a successful submission survives wrapper noise and cannot be replaced',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();await h.submit();const done=await h.finish({extra:'unexpected final prose wrapper'});assert.equal(JSON.parse(done.output).status,'completed');const r=h.output();r.answers[0].verdict='不得覆盖';assert.equal((await h.submit(r)).status,'completed');assert.equal((await h.get()).result.answers[0].verdict,'接口测试通过');});

test('an active child resumes its scoped read authorization after plugin restart',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();await h.restart();assert.equal((await h.submit()).status,'completed');});

test('wrapper completion after a restart recovers the accepted result instead of overwriting it',async t=>{
 const h=await harness(t);await h.save();await h.start();const parentHooks=h.hooks;await h.restart();await h.read();await h.submit();const before=await h.get();
 const done={output:'宿主收尾信息',metadata:{sessionId:'child'}};await parentHooks['tool.execute.after'](h.event,done);
 assert.equal(JSON.parse(done.output).status,'completed');assert.equal((await h.get()).execution_receipt.result_ref.sha256,before.execution_receipt.result_ref.sha256);
});

test('execution failure cannot overwrite an accepted or claimed result',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();await h.finish(await h.submit());await h.acknowledge();
 const before=await h.get(),f=await store(h.folder);await f.saveFailure('parent','child',h.input(),{},'wrapper noise','synthetic exception');
 assert.equal((await h.get()).execution_receipt.result_ref.sha256,before.execution_receipt.result_ref.sha256);assert.ok((await f.read('parent')).results.child.claimed_at);
});

test('unusual report subfields remain opaque to the transport',()=>{const p=packet(),r={entity_checks:[null],special_methods:[null,{basis_ids:42}],任意:'报告'};const checked=checkSubmission(root,r,p);assert.equal(checked.ok,true);assert.deepEqual(checked.result,r);});

test('complete outcome, timing and quantity traverse one child and one acknowledged report',async t=>{
 const h=await harness(t,{text:'电脑维修能否完成？何时修好？费用多少？'}),p=h.input();
 p.questions[0].tasks=['outcome','timing','quantity'];p.questions[0].task_basis=p.questions[0].tasks.map(task=>({task,origin:'user_requested',request_quote:{outcome:'能否完成',timing:'何时修好',quantity:'费用多少'}[task],reason:'原问明确要求'}));
 await h.save(p);await h.start();await h.read();const r=h.output();
 r.calculations=[{id:'C_date',action:'calendar',calendar:{start:'2026-11-03',end:'2026-11-03',timezone:'Asia/Shanghai',day_boundary:'civil-midnight'}},{id:'C_amount',action:'quantity',expression:{op:'multiply',args:[{value:8},{value:6}]}}];
 r.special_methods=[{question_id:'Q1',kind:'timing',status:'completed',target:'合成修复完成',basis_ids:['M_AUTO_TIMING'],calculation_ids:['C_date'],alternatives:[],limits:[],record:{event:'修复完成',stage:'终局',scale:'日',start:'合成占时',count_rule:'公历自然日',trigger:'合成触发',selected_method:'仅验接口',round_comparison:'单日接口范围',candidates:[{date:'2026-11-03',day:'辛巳',event:'修复完成'}]}},{question_id:'Q1',kind:'quantity',status:'completed',target:'合成费用',basis_ids:['M_AUTO_QUANTITY'],calculation_ids:['C_amount'],alternatives:[],limits:[],record:{object:'维修费用',position:'合成',number_table:'显式常量',operation:'8乘6',adjustments:'无',magnitude:'合成单位',unit:'元',precision:'仅验接口',value:48}}];
 const submitted=await h.submit(r);assert.equal(submitted.status,'completed',JSON.stringify(submitted));await h.finish(submitted);await h.acknowledge();const delivered=await h.get('deliver');
 assert.match(delivered.report_markdown,/辛巳/);assert.match(delivered.report_markdown,/"value": 48/);assert.equal((await (await store(h.folder)).read('parent')).attempts.length,1);
});

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

test('plain report can locate a concrete error without requiring legacy JSON fields',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();await h.finish(await h.submit('合成错误：本命误写为甲子。'));await h.acknowledge();
 const p=h.input();p.retry_context={previous_task_id:'child',reason:'原文“本命误写为甲子”与新增原始信息冲突',error_path:'$'};
 let saved=await h.save(p);
 await assert.rejects(()=>h.hooks['tool.execute.before']({...h.event,callID:'no-evidence'},{args:{subagent_type:'liuren-adjudicator',prompt:saved.task_prompt}}),/RETRY_WITHOUT_NEW_MATERIAL/);
 p.facts.push({id:'F_new',text:'合成新增原始信息：本命壬午',source:'测试用户'});saved=await h.save(p);
 await h.hooks['tool.execute.before']({...h.event,callID:'text-error'},{args:{subagent_type:'liuren-adjudicator',prompt:saved.task_prompt}});
});

test('free JSON recheck uses real own-property paths and rejects invented or prototype paths',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();await h.finish(await h.submit({'自选/字段':{结论:'合成错误'}}));await h.acknowledge();
 const p=h.input();p.facts.push({id:'F_new',text:'合成新增核实事实',source:'测试用户'});
 for(const error_path of ['/answers/0/verdict','/__proto__/constructor','$']){
  p.retry_context={previous_task_id:'child',reason:'合成具体事实错误',error_path};const saved=await h.save(p);
  await assert.rejects(()=>h.hooks['tool.execute.before']({...h.event,callID:'invalid-'+error_path},{args:{subagent_type:'liuren-adjudicator',prompt:saved.task_prompt}}),/RECHECK_ERROR_PATH_UNKNOWN/);
 }
 p.retry_context.error_path='/自选~1字段/结论';const saved=await h.save(p);
 await h.hooks['tool.execute.before']({...h.event,callID:'free-json-error'},{args:{subagent_type:'liuren-adjudicator',prompt:saved.task_prompt}});
});

test('an unbound host failure releases only the dispatch slot, retaining the failure',async t=>{
 const h=await harness(t);const saved=await h.save();await h.start();const out={output:'Synthetic host failure before child creation',metadata:{}};await h.hooks['tool.execute.after'](h.event,out);assert.equal(JSON.parse(out.output).status,'dispatch_failed');
 await h.hooks['tool.execute.before']({...h.event,callID:'retry-dispatch'},{args:{subagent_type:'liuren-adjudicator',prompt:saved.task_prompt}});
 const state=await (await store(h.folder)).read('parent');assert.equal(state.attempts[0].status,'dispatch_failed');assert.equal(state.attempts[1].status,'dispatching');
});

test('overlapping dispatch hooks cannot reserve the same objective twice',async t=>{const h=await harness(t);const saved=await h.save();const results=await Promise.allSettled(['parallel1','parallel2'].map(callID=>h.hooks['tool.execute.before']({...h.event,callID},{args:{subagent_type:'liuren-adjudicator',prompt:saved.task_prompt}})));assert.equal(results.filter(x=>x.status==='fulfilled').length,1);assert.equal(results.filter(x=>x.status==='rejected').length,1);});

test('legacy final text recovers only with verified full-page content receipts',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();h.childInfo.finish='stop';h.childParts.push({type:'text',text:JSON.stringify(h.output())});await h.restart();assert.equal((await h.get()).status,'completed');});

test('a failed historical read is not a page receipt',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();h.childInfo.finish='stop';h.childParts[0].state.output='An error, not file content';h.childParts.push({type:'text',text:JSON.stringify(h.output())});await h.restart();await assert.rejects(()=>h.get(),/FILE_NOT_FULLY_READ/);});

test('ordinary Build task_result output remains outside the Liuren hook',async t=>{const h=await harness(t);h.client.session.messages=async()=>({data:[{info:{role:'user'},parts:[{type:'text',text:'A regular Build task'}]}]});const event={tool:'task_result',sessionID:'parent',callID:'ordinary'};await h.hooks['tool.execute.before'](event,{args:{task_id:'build-child'}});const out={output:'Original Build result',metadata:{}};await h.hooks['tool.execute.after'](event,out);assert.equal(out.output,'Original Build result');});

test('delivery preserves all supplied source locators verbatim',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();const r={论断:'合成报告',来源:'E01：书籍库/北海闲人/理法简易.txt:2125-2150',附注:'不强制字段'};await h.finish(await h.submit(r));await h.acknowledge();const d=await h.get('deliver');assert.deepEqual(JSON.parse(d.report_markdown.slice(8,-4)),r);assert.match(d.report_markdown,/E01：书籍库/);});

test('main-visible task receipt retains the child ID without requiring metadata or full report',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();const receipt=await h.submit();const done=await h.finish(receipt),visible=JSON.parse(done.output);assert.equal(visible.schema,'liuren-adjudication-receipt-v1');assert.equal(visible.task_id,'child');assert.deepEqual(visible.next_call,{tool:'task_result',arguments:{task_id:'child'}});assert.equal(visible.answers,undefined);assert.ok(done.output.length<2000);await h.acknowledge();const located=JSON.parse(await h.hooks.tool.liuren_adjudication_result.execute({action:'locate'},{agent:'liuren',sessionID:'parent'}));assert.equal(located.task_id,'child');assert.equal(located.next_call.arguments.action,'deliver');});

test('missing task ID can locate exactly one owned result after restart',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();await h.finish(await h.submit());await h.restart();const out=JSON.parse(await h.hooks.tool.liuren_adjudication_result.execute({action:'read'},{agent:'liuren',sessionID:'parent'}));assert.equal(out.task_id,'child');assert.equal(out.result.status,'completed');});

test('a request ID cannot be mistaken for the task ID and the error names owned candidates',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();await h.finish(await h.submit());await assert.rejects(()=>h.hooks.tool.liuren_adjudication_result.execute({action:'read',task_id:'synthetic_v2'},{agent:'liuren',sessionID:'parent'}),/TASK_ID_NOT_OWNED.*child/);await assert.rejects(()=>h.hooks['tool.execute.before']({tool:'task_result',sessionID:'parent',callID:'wrong-request-id'},{args:{task_id:'synthetic_v2'}}),/TASK_ID_NOT_OWNED.*child/);});

test('two owned results require explicit choice instead of silently picking latest',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();await h.finish(await h.submit());const f=await store(h.folder),saved=await f.result('parent','child');await f.saveResult('parent','child2',saved.data.packet,saved.data.request_ref,h.output(),{pagesVerified:true});await assert.rejects(()=>h.hooks.tool.liuren_adjudication_result.execute({action:'locate'},{agent:'liuren',sessionID:'parent'}),/TASK_ID_AMBIGUOUS.*child2/);});

test('result discovery never exposes another parent session results',async t=>{const h=await harness(t);await h.save();await h.start();await h.read();await h.finish(await h.submit());await assert.rejects(()=>h.hooks.tool.liuren_adjudication_result.execute({action:'locate'},{agent:'liuren',sessionID:'another-parent'}),/NO_SAVED_RESULT/);});

test('plain report traverses file read, submit, receipt, restart, retrieve and delivery exactly',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();const report='# 裁决\n\n能修好。辰巳日为候选；费用依据和最强反证见说明。\n第四问的条件未满足，因此不答。';
 const receipt=await h.submit(report);await h.finish(receipt);await h.restart();await h.acknowledge();assert.equal((await h.get()).result,report);assert.equal((await h.get('deliver')).report_markdown,report);
});
test('invalid submitted artifact survives final prose and host failure with its read proof intact',async t=>{
 const h=await harness(t);await h.save();await h.start();await h.read();const receipt=await h.submit('   ');const f=await store(h.folder),before=await f.result('parent','child');await h.finish({note:'末尾宿主文字'});await f.saveFailure('parent','child',h.input(),{},'host noise','error');const after=await f.result('parent','child');assert.equal(after.artifact.sha256,before.artifact.sha256);assert.equal(after.data.pagesVerified,true);assert.deepEqual((await h.get()).raw,'   ');assert.equal(receipt.status,'invalid_output');
});
test('opaque payload cannot cross transport size or serialization limits',()=>{
 for(const r of ['',null,[],{},'文'.repeat(400000)])assert.equal(checkSubmission(root,r,packet()).ok,false);
 const cyclic={};cyclic.self=cyclic;assert.equal(checkSubmission(root,cyclic,packet()).ok,false);
});

test('repair of an execution failure preserves its original error instead of raising a read error',async t=>{
 const h=await harness(t);await h.save();await h.start();const f=await store(h.folder);await f.bind('parent','child',{file_path:'unused',sha256:'unused'},'first').catch(()=>{});
 await f.saveFailure('parent','child',h.input(),{},'original host output','original execution failure');const r=await h.get('repair');assert.equal(r.status,'invalid_output');assert.equal(r.raw,'original host output');assert.match(r.issues[0].message,/original execution failure/);
});
