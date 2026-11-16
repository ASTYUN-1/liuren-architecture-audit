// Durable local execution state. No professional scoring, model calls or network.
import fs from 'node:fs/promises';
import path from 'node:path';
import {randomUUID,createHash} from 'node:crypto';
import {checkSubmission,reportMarkdown} from './liuren-adjudication-output.mjs';
import {audited,checkAudit,checkDeliveryReview,inspectRecheckFindings,checkInputReview,evidenceCatalog,reviewScaffold,auditHash,REVIEW_CHECKS} from './liuren-consistency-audit.mjs';
const hash=v=>createHash('sha256').update(typeof v==='string'?v:JSON.stringify(v)).digest('hex');
export const loadedImplementationSha256=createHash('sha256').update(await fs.readFile(new URL(import.meta.url))).digest('hex');
const safe=v=>typeof v==='string'&&/^[A-Za-z0-9_-]{1,160}$/.test(v);
const fail=(code,details)=>{throw new Error('LIUREN_FLOW: '+code+' '+JSON.stringify(details));};
const load=p=>fs.readFile(p,'utf8').then(JSON.parse);
// OpenCode hooks can overlap; serialize read/modify/write across plugin instances.
const stateQueues=new Map();
async function exclusive(key,fn){const previous=stateQueues.get(key)??Promise.resolve();let release;const gate=new Promise(resolve=>release=resolve);stateQueues.set(key,gate);await previous;try{return await fn();}finally{release();if(stateQueues.get(key)===gate)stateQueues.delete(key);}}
export async function enabled(root){try{return (await load(path.join(root,'.opencode/liuren-active.json'))).flowControl?.enabled===true;}catch(error){if(error.code==='ENOENT')return false;throw error;}}
export async function store(root){
 const folder=path.join(await fs.realpath(root),'output/liuren-flow-state');await fs.mkdir(folder,{recursive:true});
 if(await fs.realpath(folder)!==folder)fail('LINKED_STATE_DIRECTORY',{});
 const file=id=>{if(!safe(id))fail('BAD_SESSION_ID',{});return path.join(folder,id+'.json');};
 async function read(parent){try{return await load(file(parent));}catch(e){if(e.code!=='ENOENT')throw e;return {schema:'liuren-flow-state-v1',parent,methods:{},attempts:[],results:{}};}}
 async function write(state){const dest=file(state.parent),tmp=dest+'.'+randomUUID()+'.tmp';await fs.writeFile(tmp,JSON.stringify(state),{flag:'wx',mode:0o600});await fs.rename(tmp,dest);}
 async function artifact(parent,child,value){
  if(!safe(parent)||!safe(child))fail('BAD_ARTIFACT_OWNER',{});
  const raw=JSON.stringify(value),dest=path.join(folder,parent+'--'+child+'--'+randomUUID()+'.json');await fs.writeFile(dest,raw,{flag:'wx',mode:0o600});return {path:dest,sha256:hash(raw)};
 }
 async function readArtifact(ref){const p=path.resolve(ref.path);if(path.dirname(p)!==folder||await fs.realpath(p)!==p)fail('ARTIFACT_OUTSIDE_STATE',{});const raw=await fs.readFile(p,'utf8');if(hash(raw)!==ref.sha256)fail('ARTIFACT_CHANGED',{});return JSON.parse(raw);}
 async function noteMethod(parent,text){
  const matches=[...(text??'').matchAll(/LIUREN_METHOD_BEGIN (\{[^\r\n]+\})\r?\n([\s\S]*?)\r?\nLIUREN_METHOD_END (\{[^\r\n]+\})/g)];
  for(const match of matches){
  const meta=JSON.parse(match[1]),end=JSON.parse(match[3]),pointer=await load(path.join(root,'.opencode/liuren-active.json')),manifest=await load(path.join(root,pointer.runtime,'manifest.json'));
  const record=manifest.modules[meta.module];if(!record||meta.release!==pointer.release||manifest.files[record.file]!==meta.fileSha256||end.module!==meta.module||meta.textSha256!==end.textSha256||hash(match[2])!==meta.textSha256)continue;
  const state=await read(parent);if(state.methods[meta.module]?.release===pointer.release&&state.methods[meta.module]?.sha256===meta.fileSha256)continue;
  state.methods[meta.module]={release:pointer.release,sha256:meta.fileSha256};await write(state);
  }
 }
 async function hydrateMethods(parent,client){
  const response=await client.session.messages({path:{id:parent},query:{directory:root}});if(response.error)fail('SESSION_LOOKUP_FAILED',{});
  for(const m of response.data??[])for(const part of m.parts??[])if(part.type==='tool'&&part.tool==='liuren_materials'&&part.state?.status==='completed')await exclusive(file(parent),()=>noteMethod(parent,part.state.output));
  return response.data??[];
 }
 async function readiness(parent,client,{report=false,domains=[]}={}){
  const pointer=await load(path.join(root,'.opencode/liuren-active.json')),manifest=await load(path.join(root,pointer.runtime,'manifest.json'));let state=await read(parent);
  for(const domain of domains)if(!manifest.domains.includes(domain))fail('UNKNOWN_DOMAIN',{domain});
  const required=report?['report']:[...new Set([...manifest.required.filter(m=>m!=='report'),...domains])];
  if(client&&required.some(m=>state.methods[m]?.release!==pointer.release||state.methods[m]?.sha256!==manifest.files[manifest.modules[m].file])){await hydrateMethods(parent,client);state=await read(parent);}
  const missing=required.filter(m=>state.methods[m]?.release!==pointer.release||state.methods[m]?.sha256!==manifest.files[manifest.modules[m].file]);
  return {release:pointer.release,ready:missing.length===0,required,missing,next_calls:missing.map(module=>({tool:'liuren_materials',arguments:{action:'method',module}})),scope:'完整方法传输回执；不证明模型已理解或专业判断正确'};
 }
 async function coverage(parent,client,options={}){
  const status=await readiness(parent,client,options);
  if(!status.ready)fail('MISSING_METHODS',{missing:status.missing,next_calls:status.next_calls,action:'只补这些模块；保存前可liuren_tool_help topic=workflow查就绪状态，不重读已核模块'});
 }
 async function origin(parent,client,p){
  const messages=await hydrateMethods(parent,client);
  const users=messages.filter(m=>m.info?.role==='user').map(m=>({id:m.info.id,text:(m.parts??[]).filter(p=>p.type==='text').map(p=>p.text).join('\n').trim()}));
  const quotes=p.questions.flatMap(q=>(q.task_basis??[]).map(b=>b.request_quote).filter(q=>typeof q==='string'&&q.trim()));
  const selected=users.filter((m,i)=>i===users.length-1||quotes.some(q=>m.text.includes(q)));
  const text=selected.map(m=>m.text).join('\n\n');
  if(!text)fail('ORIGINAL_QUESTION_UNAVAILABLE',{action:'保留原始用户题干后再交接，不猜造原问'});
  const errors=[];
  for(const [i,q] of p.questions.entries()){
   const basis=q.task_basis;
   if(!Array.isArray(basis)||basis.length!==q.tasks?.length||new Set(basis.map(b=>b.task)).size!==q.tasks.length){errors.push({path:'/questions/'+i+'/task_basis',expected:'one origin/reason per declared task'});continue;}
   for(const [j,b] of basis.entries()){
    if(!q.tasks.includes(b.task)||!['user_requested','necessary'].includes(b.origin)||typeof b.reason!=='string'||!b.reason.trim())errors.push({path:'/questions/'+i+'/task_basis',expected:'task + user_requested/necessary + concrete reason'});
    if(b.origin==='user_requested'&&(typeof b.request_quote!=='string'||!b.request_quote.trim()||!text.includes(b.request_quote)))errors.push({path:'/questions/'+i+'/task_basis/'+j+'/request_quote',expected:'原始用户消息连续逐字片段，不能改写或省略',source_excerpt:text.slice(0,1600)});
    if(b.origin==='user_requested'&&b.task!=='outcome'){
     const cue=b.task==='timing'?/何时|什么时候|哪[天日月年]|多久|多长|几[天日月年]|应期|何日|何年|何.*时间|时间.*[?？]/:/多少|几[元块个次米分斤两岁成倍名位档级等]|金额|价格|费用|花费|取数|数量|给(?:我|出)?(?:一)?个(?:具体)?(?:数字|数)|估(?:一|个)?数|具体数字|报(?:一)?个数/;
     const quote=(b.request_quote??'').replace(/\d{4}年\d{1,2}月\d{1,2}日(?:\s*\d{1,2}(?:[:：时点]\d{1,2}分?|时|点))?/g,'');
     if(!cue.test(quote))errors.push({path:'/questions/'+i+'/task_basis',expected:b.task==='timing'?'explicit timing question; a supplied divination timestamp is not a timing request':'explicit numerical/ordinal question in the user quote; this wording check does not decide whether a numerical method applies'});
    }
   }
  }
  if(p.input_review)errors.push(...checkInputReview({...p,input_origin:{source_text:text}}).issues);
  if(errors.length)fail('INPUT_PREFLIGHT',{issues:errors,action:'一次更正所列字段；stage_basis在user_explicit时整个字段只能是原问连续原句，解释放success_basis/route。不为过校验更换专业对象，不读工具源码猜字段。',help:{tool:'liuren_tool_help',arguments:{topic:'packet'}}});
  return {...p,input_origin:{source_text:text,source_sha256:hash(text),objective_sha256:hash(selected[0].text),source_messages:selected.map(m=>({id:m.id??null,sha256:hash(m.text)})),identity:'native user messages; semantic confirmation is not implied'}};
 }
 async function reserve(parent,p,ref,call){
  if(!p.input_origin?.source_sha256)fail('LEGACY_PACKET_REBUILD_REQUIRED',{action:'旧材料可领取核验；新派发须由packet工具保留当前原问与任务依据'});
  const state=await read(parent),key=hash([p.input_origin?.objective_sha256??p.input_origin.source_sha256,p.deterministic?.chart_sha256??p.chart.facts]);
  const same=state.attempts.filter(a=>a.objective===key&&a.status!=='dispatch_failed');
  if(state.attempts.filter(a=>a.objective===key&&a.status==='dispatch_failed').length>=3)fail('DISPATCH_FAILURE_LIMIT',{action:'宿主连续三次未创建裁决任务；保留错误，先修宿主，不继续调用'});
  if(same.length){
   if(audited(p))fail('SAME_CHILD_RECHECK_ONLY',{task_id:same.at(-1).child,action:'39版有具体证据缺口用result recheck，在原子会话补核一次；不得另派同题'});
   const previous=same.at(-1),record=state.results[previous.child];
   if(record&&!record.claimed_at)fail('TASK_RESULT_ACK_REQUIRED',{task_id:previous.child,next_call:{tool:'liuren_adjudication_result',arguments:{action:'read',task_id:previous.child}},action:'用结果工具read领取已有报告或明确失败；无正文时不要重复task/task_result'});
   const errorPath=p.retry_context?.error_path;
   const factual=record?.status==='completed'&&typeof errorPath==='string'&&(errorPath==='$'||errorPath.startsWith('/'));
   if(!p.retry_context||p.retry_context.previous_task_id!==previous.child||(!factual&&record?.status!=='needs_input')||same.length>=2)fail('NO_DUPLICATE_ADJUDICATION',{previous_task_id:previous.child,status:record?.status??previous.status,action:'已产出先task_result或liuren_adjudication_result领取/修格式；needs_input或具体事实/引用/已确认U口径错误，且有新材料，才可一次补核'});
   const old=await readArtifact(record.artifact);
   if(factual){
    let at=old.checked.result;
    if(errorPath==='$'){
     if(typeof at!=='string')fail('RECHECK_ERROR_PATH_UNKNOWN',{action:'$仅定位自由正文；JSON对象请引用真实字段的JSON Pointer'});
    }else{
     for(const token of errorPath.slice(1).split('/')){
      if(/~(?![01])/.test(token))fail('RECHECK_ERROR_PATH_UNKNOWN',{});
      const k=token.replaceAll('~1','/').replaceAll('~0','~');
      if(at===null||typeof at!=='object'||!Object.hasOwn(at,k))fail('RECHECK_ERROR_PATH_UNKNOWN',{});
      at=at[k];
     }
    }
    if(at===undefined)fail('RECHECK_ERROR_PATH_UNKNOWN',{});
   }
   if(hash([old.packet.facts,old.packet.observations,old.packet.method_materials,old.packet.unknowns])===hash([p.facts,p.observations,p.method_materials,p.unknowns]))fail('RETRY_WITHOUT_NEW_MATERIAL',{});
   if(typeof p.retry_context.reason!=='string'||!p.retry_context.reason.trim())fail('RETRY_REASON_REQUIRED',{});
  }
  state.attempts.push({call,objective:key,request_id:p.request_id,ref,status:'dispatching'});await write(state);
 }
 async function bind(parent,child,ref,call){const state=await read(parent),a=state.attempts.find(a=>a.call===call);if(!a||a.ref.file_path!==ref.file_path||a.ref.sha256!==ref.sha256||(a.child&&a.child!==child)||a.status==='dispatch_failed')fail('DISPATCH_BINDING_MISMATCH',{});a.child=child;a.status='running';await write(state);}
 async function dispatchFailure(parent,call,message){const state=await read(parent),a=state.attempts.find(a=>a.call===call);if(!a)return;if(a.child)fail('CHILD_RESULT_RECOVERY_REQUIRED',{task_id:a.child});a.status='dispatch_failed';a.error=message;await write(state);}
 async function noteCalculation(parent,child,request,value){
  const state=await read(parent),a=state.attempts.find(a=>a.child===child);if(!a)fail('CALCULATION_OWNER_REQUIRED',{});
  a.calculations??=[];
  for(const ref of a.calculations){const old=await readArtifact(ref);if(hash(old.request)===hash(request)&&hash(old.result)===hash(value))return ref;}
  const payload={schema:'liuren-calculation-receipt-v1',request,result:value};
  if(a.calculations.length>=30||JSON.stringify(payload).length>200000)fail('CALCULATION_RECEIPT_LIMIT',{});
  const ref=await artifact(parent,child,payload);a.calculations.push(ref);await write(state);return ref;
 }
 async function calculations(parent,child){const state=await read(parent),out=[];for(const ref of state.attempts.find(a=>a.child===child)?.calculations??[])out.push({ref,...await readArtifact(ref)});return out;}
 async function saveResult(parent,child,p,ref,raw,{pagesVerified=false,audit=null}={}){
  if(!pagesVerified)fail('FILE_NOT_FULLY_READ',{});
  const state=await read(parent),previous=state.results[child];
  const recheck=state.consistency_rechecks?.[child],replacing=audited(p)&&recheck?.status==='running'&&recheck.original_artifact.sha256===previous?.artifact.sha256;
  if((previous?.status==='completed'||previous?.status==='needs_input')&&!replacing)return receipt(parent,child);
  if(previous){const saved=await readArtifact(previous.artifact);if(saved.pagesVerified&&(saved.checked.validationScope==='transport-only'||saved.checked.issues?.every(x=>x.code==='report_transport'))&&hash(saved.raw)===hash(raw))return receipt(parent,child);}
  const checked=checkSubmission(root,raw,p),status=checked.ok?checked.status:'invalid_output';
  const calculation_receipts=await calculations(parent,child),consistency_check=checked.ok?checkAudit(p,checked.result,audit,calculation_receipts):null;
  const refResult=await artifact(parent,child,{schema:'liuren-saved-result-v1',parent,child,packet:p,request_ref:ref,raw,checked,pagesVerified,calculation_receipts,...(audited(p)?{audit,consistency_check}:{})});
  state.results[child]={status,request_id:p.request_id,artifact:refResult,submissions:(previous?.submissions??0)+1,...(replacing?{history:[...(previous.history??[]),previous.artifact]}:{})};
  if(replacing){recheck.status='completed';recheck.finished_at=new Date().toISOString();recheck.revised_artifact=refResult;}
  const a=state.attempts.find(a=>a.child===child);if(a)a.status=status;
  await write(state);
  return checked.ok?{schema:'liuren-adjudication-receipt-v1',task_id:child,request_id:p.request_id,status,result_ref:refResult,contractChecked:true,validationScope:'transport-only',professionalContentChecked:false,...(consistency_check?{consistency_check,action:'正文与一致性附件已保存；主智能体read核对，具体缺口在原子会话recheck一次，不另派任务。'}:{})}:{schema:'liuren-adjudication-error-v1',task_id:child,request_id:p.request_id,status,contractChecked:false,result_ref:refResult,issues:checked.issues,error_kind:'transport',action:'仅检查报告是否非空、可保存及是否超传输上限；不修专业字段、不重派裁决。read可领取已有原文。'};
 }
 async function result(parent,child){const state=await read(parent),r=state.results[child];if(!r)fail('NO_SAVED_RESULT',{task_id:child,action:'先用task_result领取已有子会话输出，不能再派同任务'});return {...r,data:await readArtifact(r.artifact)};}
 async function locate(parent,child){
  const state=await read(parent),available=Object.entries(state.results).map(([task_id,r])=>({task_id,request_id:r.request_id,status:r.status,claimed:!!r.claimed_at}));
  if(child&&state.results[child])return child;
  if(!child&&available.length===1)return available[0].task_id;
  fail(child?'TASK_ID_NOT_OWNED':available.length?'TASK_ID_AMBIGUOUS':'NO_SAVED_RESULT',{task_id:child,available_results:available,action:'task_id只能使用上述子会话ID；不能使用request_id、文件UUID或hash。多项时明确选择，不自动取最新。'});
 }
 async function receipt(parent,child,client){
  const saved=await result(parent,child),r=saved.data.checked;
  const delivery=saved.claimed_at&&saved.status==='completed'?await readiness(parent,client,{report:true}):null;
  const requiresReview=r.ok&&saved.status==='completed'&&audited(saved.data.packet)&&!saved.delivery_review;
  const next=delivery&&!delivery.ready?delivery.next_calls:saved.status==='invalid_output'||saved.claimed_at?[saved.status==='completed'&&requiresReview?{tool:'liuren_tool_help',arguments:{topic:'result',task_id:child}}:{tool:'liuren_adjudication_result',arguments:{action:saved.status==='completed'?'deliver':'read',task_id:child}}]:[{tool:'task_result',arguments:{task_id:child}}];
  return {schema:'liuren-adjudication-receipt-v1',task_id:child,request_id:saved.request_id,status:saved.status,contractChecked:r.ok,validationScope:'transport-only',professionalContentChecked:false,result_ref:saved.artifact,...(audited(saved.data.packet)?{consistency_check:saved.data.consistency_check,...(r.ok?{report_sha256:auditHash(r.result)}:{}),review_required:requiresReview,recheck_available:r.ok&&!(await read(parent)).consistency_rechecks?.[child],review_checks:REVIEW_CHECKS}:{}),...(!r.ok?{issues:r.issues}:{}),...(delivery?{delivery_readiness:delivery}:{}),next_call:next[0],next_calls:next,action:'按next_call接续；39版先read正文及附件，读report方法并提交review五项核对；具体缺口用原子会话recheck一次；旧版按原协议deliver。不重新派裁决。'};
 }
 async function reviewDelivery(parent,child,review){
  const saved=await result(parent,child);if(!audited(saved.data.packet))fail('LEGACY_NO_AUDIT',{});
  if(!saved.data.checked.ok||saved.status!=='completed')fail('REVIEW_REQUIRES_COMPLETED_REPORT',{next_call:{tool:'liuren_adjudication_result',arguments:{action:'read',task_id:child}},action:'尚无完整可复核报告，保留原任务缺口并按read回执接续。'});
  if((await read(parent)).consistency_rechecks?.[child]?.status==='running')fail('RECHECK_RUNNING',{});
  const check=checkDeliveryReview(review,saved.data.checked.result,{packet:saved.data.packet,receipts:saved.data.calculation_receipts});if(!check.ok)fail('DELIVERY_REVIEW_INVALID',{issues:check.issues,evidence_catalog:evidenceCatalog(saved.data.packet,saved.data.calculation_receipts),help:{tool:'liuren_tool_help',arguments:{topic:'result',task_id:child}},action:'按具体索引修正未知引用或非连续引句；不替换报告、不自动通过实质复核。'});
  const state=await read(parent);state.results[child].delivery_review={review,check,artifact_sha256:saved.artifact.sha256,recorded_at:new Date().toISOString()};await write(state);return {review_saved:true,unresolved:check.unresolved,consistency_check:saved.data.consistency_check,next_call:{tool:'liuren_adjudication_result',arguments:{action:'deliver',task_id:child}}};
 }
 async function reserveRecheck(parent,child,{findings,message_id,prompt}){
  const saved=await result(parent,child),state=await read(parent);
  if(!audited(saved.data.packet)||!saved.data.checked.ok)fail('RECHECK_REQUIRES_AUDITED_REPORT',{});
  if(state.consistency_rechecks?.[child])fail('RECHECK_ALREADY_ATTEMPTED',{action:'同一子会话只补核一次；保留剩余缺口，不另派或循环'});
  const body=typeof saved.data.checked.result==='string'?saved.data.checked.result:JSON.stringify(saved.data.checked.result);
   const findingCheck=inspectRecheckFindings(saved.data.packet,body,findings,saved.data.calculation_receipts);
   if(!findingCheck.ok)fail('RECHECK_EVIDENCE_REQUIRED',{issues:findingCheck.issues,evidence_catalog:evidenceCatalog(saved.data.packet,saved.data.calculation_receipts),action:'每项附当前报告连续逐字引句、合法evidence_refs、证据与具体补核事项；不同意结论不是补核理由。此失败未消耗一次补核额度。'});
  state.consistency_rechecks??={};state.consistency_rechecks[child]={status:'running',message_id,prompt_sha256:hash(prompt),findings,original_artifact:saved.artifact,started_at:new Date().toISOString()};delete state.results[child].delivery_review;await write(state);return state.consistency_rechecks[child];
 }
 async function finishRecheck(parent,child,error){const state=await read(parent),row=state.consistency_rechecks?.[child];if(!row)fail('RECHECK_NOT_RESERVED',{});if(row.status==='running'){row.status='failed';row.finished_at=new Date().toISOString();row.error=error??'原子会话未保存修订报告';await write(state);}return row;}
 async function acknowledge(parent,child){await result(parent,child);const state=await read(parent);state.results[child].claimed_at=new Date().toISOString();await write(state);}
 async function reserveRecovery(parent,child,ref,{message_id,prompt,last_message_id}){
  const saved=await result(parent,child),state=await read(parent),attempt=state.attempts.find(a=>a.child===child);
  if(!attempt||attempt.ref.file_path!==ref.file_path||attempt.ref.sha256!==ref.sha256)fail('RECOVERY_OWNER_MISMATCH',{});
  if(saved.status!=='invalid_output'||saved.data.pagesVerified!==true||typeof saved.data.raw!=='string'||saved.data.raw.trim())fail('RECOVERY_REQUIRES_EMPTY_REPORT',{});
  if(state.recoveries?.[child])fail('RECOVERY_ALREADY_ATTEMPTED',{task_id:child,action:'同一子会话只续写一次；读取现有状态，不再派发或重复调用恢复'});
  state.recoveries??={};state.recoveries[child]={status:'running',message_id,prompt_sha256:hash(prompt),last_message_id,started_at:new Date().toISOString(),original_artifact:saved.artifact};
  await write(state);return state.recoveries[child];
 }
 async function finishRecovery(parent,child,error){const state=await read(parent),record=state.recoveries?.[child];if(!record)fail('RECOVERY_NOT_RESERVED',{});record.status=state.results[child]?.status==='completed'||state.results[child]?.status==='needs_input'?'completed':'failed';record.finished_at=new Date().toISOString();if(error)record.error=String(error);await write(state);}
 async function saveFailure(parent,child,p,ref,raw,message){
  const state=await read(parent);
  if(state.results[child])return receipt(parent,child);
  const previous=state.results[child];
  const checked={ok:false,issues:[{path:'/',code:'execution_error',message}]};
  const artifactRef=await artifact(parent,child,{schema:'liuren-saved-result-v1',parent,child,packet:p,request_ref:ref,raw,checked,pagesVerified:false});
  state.results[child]={status:'invalid_output',request_id:p.request_id,artifact:artifactRef,submissions:Math.max(1,previous?.submissions??0)};
  const attempt=state.attempts.find(a=>a.child===child);if(attempt)attempt.status='invalid_output';await write(state);
  return {schema:'liuren-adjudication-error-v1',status:'invalid_output',task_id:child,request_id:p.request_id,result_ref:artifactRef,issues:checked.issues,action:'保留原产物与此具体缺口；不得重派整轮裁决，不由主智能体补判。'};
 }
 async function getResult(parent,child,action,client){
  let saved=await result(parent,child);
  if(action==='repair'&&saved.status==='invalid_output'){
   const {packet,request_ref,raw,pagesVerified}=saved.data;if(pagesVerified)await exclusive(file(parent),()=>saveResult(parent,child,packet,request_ref,raw,{pagesVerified}));saved=await result(parent,child);
  }
  if(!saved.data.checked.ok)return {schema:'liuren-adjudication-error-v1',task_id:child,status:'invalid_output',result_ref:saved.artifact,issues:saved.data.checked.issues,raw:saved.data.raw,action:'保留原文和具体传输错误；不得重派或由主智能体改判'};
  const r=saved.data.checked.result;
  if(action==='deliver'){
   if(saved.status!=='completed')fail('RESULT_NOT_COMPLETED',{status:saved.status});if(!saved.claimed_at)fail('TASK_RESULT_ACK_REQUIRED',{task_id:child});await coverage(parent,client,{report:true});
   let gapNotice='',process_status;
   if(audited(saved.data.packet)){
    const state=await read(parent);if(state.consistency_rechecks?.[child]?.status==='running')fail('RECHECK_RUNNING',{});
    if(!saved.delivery_review||saved.delivery_review.artifact_sha256!==saved.artifact.sha256)fail('DELIVERY_REVIEW_REQUIRED',{report_sha256:auditHash(typeof r==='string'?r:JSON.stringify(r)),checks:REVIEW_CHECKS});
    const gaps=[...(saved.data.consistency_check?.issues??[]).map(x=>x.message),...saved.delivery_review.check.unresolved.map(x=>x.basis)];
    if(state.consistency_rechecks?.[child]?.status==='failed')gaps.push('一次原子会话补核未完成，保留原报告与具体缺口');
    process_status=gaps.length?'completed_with_gaps':'checks_recorded';
    if(gaps.length)gapNotice='> 一致性核对仍有未解决项，本报告不能视为已完成核验：\n'+[...new Set(gaps)].map(s=>'> - '+s.replaceAll('\n',' ')).join('\n')+'\n\n';
   }
   const report=gapNotice+reportMarkdown(r);const receipt=await artifact(parent,child,{schema:'liuren-report-v1',result_sha256:saved.artifact.sha256,request_id:saved.request_id,report_markdown:report});
   await exclusive(file(parent),async()=>{const state=await read(parent);state.results[child].delivery=receipt;await write(state);});
   return {schema:'liuren-delivery-v1',task_id:child,request_id:saved.request_id,result_ref:saved.artifact,report_ref:receipt,report_markdown:report,calculation_receipts:saved.data.calculation_receipts??[],...(process_status?{process_status,consistency_check:saved.data.consistency_check,delivery_review:saved.delivery_review}:{}),policy:'直接交付此技术正文并保留缺口提示；可调整排版，不增加决定性理由、不改结论/精度/条件；程序核对不证明预测准确'};
  }
  const continuation=await receipt(parent,child,client);
  return {schema:'liuren-result-v1',task_id:child,request_id:saved.request_id,status:saved.status,result:r,calculation_receipts:saved.data.calculation_receipts??[],...(audited(saved.data.packet)?{audit:saved.data.audit,consistency_check:saved.data.consistency_check,report_sha256:continuation.report_sha256,review_required:continuation.review_required,recheck_available:continuation.recheck_available,review_checks:REVIEW_CHECKS,evidence_catalog:evidenceCatalog(saved.data.packet,saved.data.calculation_receipts),review_scaffold:reviewScaffold(saved.data.packet,r,saved.data.calculation_receipts,child)}:{}),next_call:continuation.next_call,next_calls:continuation.next_calls,...(continuation.delivery_readiness?{delivery_readiness:continuation.delivery_readiness}:{}),execution_receipt:{task_id:child,result_ref:saved.artifact,contractChecked:true,validationScope:'transport-only',professionalContentChecked:false}};
 }
 const locked=fn=>(parent,...args)=>exclusive(file(parent),()=>fn(parent,...args));
 return {read,noteMethod:locked(noteMethod),readiness,coverage,origin,reserve:locked(reserve),bind:locked(bind),dispatchFailure:locked(dispatchFailure),noteCalculation:locked(noteCalculation),calculations,saveResult:locked(saveResult),saveFailure:locked(saveFailure),result,getResult,locate,receipt,acknowledge:locked(acknowledge),reserveRecovery:locked(reserveRecovery),finishRecovery:locked(finishRecovery),reviewDelivery:locked(reviewDelivery),reserveRecheck:locked(reserveRecheck),finishRecheck:locked(finishRecheck)};
}
