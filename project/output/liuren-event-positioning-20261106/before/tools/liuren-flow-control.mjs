// Durable local execution state. No professional scoring, model calls or network.
import fs from 'node:fs/promises';
import path from 'node:path';
import {randomUUID,createHash} from 'node:crypto';
import {checkSubmission} from './liuren-adjudication-output.mjs';
const hash=v=>createHash('sha256').update(typeof v==='string'?v:JSON.stringify(v)).digest('hex');
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
  const match=/LIUREN_METHOD_BEGIN (\{[^\r\n]+\})\r?\n([\s\S]*?)\r?\nLIUREN_METHOD_END (\{[^\r\n]+\})/.exec(text??'');if(!match)return;
  const meta=JSON.parse(match[1]),end=JSON.parse(match[3]),pointer=await load(path.join(root,'.opencode/liuren-active.json')),manifest=await load(path.join(root,pointer.runtime,'manifest.json'));
  const record=manifest.modules[meta.module];if(!record||meta.release!==pointer.release||manifest.files[record.file]!==meta.fileSha256||end.module!==meta.module||meta.textSha256!==end.textSha256||hash(match[2])!==meta.textSha256)return;
  const state=await read(parent);if(state.methods[meta.module]?.release===pointer.release&&state.methods[meta.module]?.sha256===meta.fileSha256)return;
  state.methods[meta.module]={release:pointer.release,sha256:meta.fileSha256};await write(state);
 }
 async function hydrateMethods(parent,client){
  const response=await client.session.messages({path:{id:parent},query:{directory:root}});if(response.error)fail('SESSION_LOOKUP_FAILED',{});
  for(const m of response.data??[])for(const part of m.parts??[])if(part.type==='tool'&&part.tool==='liuren_materials'&&part.state?.status==='completed')await exclusive(file(parent),()=>noteMethod(parent,part.state.output));
  return response.data??[];
 }
 async function coverage(parent,client,{report=false}={}){
  const pointer=await load(path.join(root,'.opencode/liuren-active.json')),manifest=await load(path.join(root,pointer.runtime,'manifest.json'));let state=await read(parent);
  const required=report?['report']:manifest.required.filter(m=>m!=='report');
  if(required.some(m=>state.methods[m]?.release!==pointer.release||state.methods[m]?.sha256!==manifest.files[manifest.modules[m].file])){await hydrateMethods(parent,client);state=await read(parent);}
  const missing=required.filter(m=>state.methods[m]?.release!==pointer.release||state.methods[m]?.sha256!==manifest.files[manifest.modules[m].file]);
  if(missing.length)fail('MISSING_METHODS',{missing,action:'用liuren_materials action=method补读这些当前版模块；不要重读已核模块'});
 }
 async function origin(parent,client,p){
  const messages=await hydrateMethods(parent,client);
  const users=messages.filter(m=>m.info?.role==='user').map(m=>({id:m.info.id,text:(m.parts??[]).filter(p=>p.type==='text').map(p=>p.text).join('\n').trim()}));
  const quotes=p.questions.flatMap(q=>(q.task_basis??[]).map(b=>b.request_quote).filter(q=>typeof q==='string'&&q.trim()));
  const selected=users.filter((m,i)=>i===users.length-1||quotes.some(q=>m.text.includes(q)));
  const text=selected.map(m=>m.text).join('\n\n');
  if(!text)fail('ORIGINAL_QUESTION_UNAVAILABLE',{action:'保留原始用户题干后再交接，不猜造原问'});
  const errors=[];
  const roles=[[/[姐姊妹]姐?的女儿|妹妹的女儿/,'外甥女','侄女'],[/哥哥的女儿|弟弟的女儿/,'侄女','外甥女'],[/姐姐的儿子|妹妹的儿子/,'外甥','侄子'],[/哥哥的儿子|弟弟的儿子/,'侄子','外甥']];
  // Only unambiguous literal relations are checked; no inference of six-kin selection.
  for(const [pattern,label,wrong] of roles)if(pattern.test(text)&&!text.includes(wrong)){
   for(const [i,q] of p.questions.entries())if((q.subject??'').includes(wrong))errors.push({path:'/questions/'+i+'/subject',expected:label,actual:wrong});
   for(const [i,e] of p.entities.entries())if((e.referent??'').includes(wrong))errors.push({path:'/entities/'+i+'/referent',expected:label,actual:wrong});
  }
  for(const [i,q] of p.questions.entries()){
   const basis=q.task_basis;
   if(!Array.isArray(basis)||basis.length!==q.tasks?.length||new Set(basis.map(b=>b.task)).size!==q.tasks.length){errors.push({path:'/questions/'+i+'/task_basis',expected:'one origin/reason per declared task'});continue;}
   for(const b of basis){
    if(!q.tasks.includes(b.task)||!['user_requested','necessary'].includes(b.origin)||typeof b.reason!=='string'||!b.reason.trim())errors.push({path:'/questions/'+i+'/task_basis',expected:'task + user_requested/necessary + concrete reason'});
    if(b.origin==='user_requested'&&(typeof b.request_quote!=='string'||!b.request_quote.trim()||!text.includes(b.request_quote)))errors.push({path:'/questions/'+i+'/task_basis',expected:'exact quote from original user request'});
    if(b.origin==='user_requested'&&b.task!=='outcome'){
     const cue=b.task==='timing'?/何时|什么时候|哪[天日月年]|多久|多长|几[天日月年]|应期|何日|何年|何.*时间|时间.*[?？]/:/多少|几[元块个次米]|金额|价格|费用|花费|取数|数量/;
     const quote=(b.request_quote??'').replace(/\d{4}年\d{1,2}月\d{1,2}日.*$/,'');
     if(!cue.test(quote))errors.push({path:'/questions/'+i+'/task_basis',expected:'explicit timing/quantity question; a supplied divination timestamp is not a timing request'});
    }
   }
  }
  if(errors.length)fail('INPUT_PREFLIGHT',{issues:errors,action:'只更正题干对应关系/任务来源，不为过校验更换日干或专业对象'});
  return {...p,input_origin:{source_text:text,source_sha256:hash(text),objective_sha256:hash(selected[0].text)}};
 }
 async function reserve(parent,p,ref,call){
  if(!p.input_origin?.source_sha256)fail('LEGACY_PACKET_REBUILD_REQUIRED',{action:'旧材料可领取核验；新派发须由packet工具保留当前原问与任务依据'});
  const state=await read(parent),key=hash([p.input_origin?.objective_sha256??p.input_origin.source_sha256,p.deterministic?.chart_sha256??p.chart.facts]);
  const same=state.attempts.filter(a=>a.objective===key&&a.status!=='dispatch_failed');
  if(state.attempts.filter(a=>a.objective===key&&a.status==='dispatch_failed').length>=3)fail('DISPATCH_FAILURE_LIMIT',{action:'宿主连续三次未创建裁决任务；保留错误，先修宿主，不继续调用'});
  if(same.length){
   const previous=same.at(-1),record=state.results[previous.child];
   if(record&&!record.claimed_at)fail('TASK_RESULT_ACK_REQUIRED',{task_id:previous.child,action:'先task_result领取并确认已有结果'});
   const factual=record?.status==='completed'&&/^\/(entity_checks|relation_checks|source_conflicts)\//.test(p.retry_context?.error_path??'');
   if(!p.retry_context||p.retry_context.previous_task_id!==previous.child||(!factual&&record?.status!=='needs_input')||same.length>=2)fail('NO_DUPLICATE_ADJUDICATION',{previous_task_id:previous.child,status:record?.status??previous.status,action:'已产出先task_result或liuren_adjudication_result领取/修格式；needs_input或具体事实/引用错误，且有新材料，才可一次补核'});
   const old=await readArtifact(record.artifact);
   if(factual){let at=old.checked.result;for(const k of p.retry_context.error_path.slice(1).split('/'))at=at?.[k];if(at===undefined)fail('RECHECK_ERROR_PATH_UNKNOWN',{});}
   if(hash([old.packet.facts,old.packet.observations,old.packet.method_materials,old.packet.unknowns])===hash([p.facts,p.observations,p.method_materials,p.unknowns]))fail('RETRY_WITHOUT_NEW_MATERIAL',{});
   if(typeof p.retry_context.reason!=='string'||!p.retry_context.reason.trim())fail('RETRY_REASON_REQUIRED',{});
  }
  state.attempts.push({call,objective:key,request_id:p.request_id,ref,status:'dispatching'});await write(state);
 }
 async function bind(parent,child,ref,call){const state=await read(parent),a=state.attempts.find(a=>a.call===call);if(!a||a.ref.file_path!==ref.file_path||a.ref.sha256!==ref.sha256||(a.child&&a.child!==child)||a.status==='dispatch_failed')fail('DISPATCH_BINDING_MISMATCH',{});a.child=child;a.status='running';await write(state);}
 async function dispatchFailure(parent,call,message){const state=await read(parent),a=state.attempts.find(a=>a.call===call);if(!a)return;if(a.child)fail('CHILD_RESULT_RECOVERY_REQUIRED',{task_id:a.child});a.status='dispatch_failed';a.error=message;await write(state);}
 async function saveResult(parent,child,p,ref,raw,{pagesVerified=false}={}){
  if(!pagesVerified)fail('FILE_NOT_FULLY_READ',{});
  const state=await read(parent),previous=state.results[child];
  if(previous?.status==='completed'||previous?.status==='needs_input')fail('RESULT_ALREADY_ACCEPTED',{task_id:child,action:'已通过结果已固定，直接返回既有回执，不再提交或改判'});
  if((previous?.submissions??0)>=3)fail('FORMAT_REPAIR_LIMIT',{action:'停止修复，保留原产物与具体缺口，不派整轮裁决'});
  const checked=checkSubmission(root,raw,p),status=checked.ok?checked.result.status:'invalid_output';
  const refResult=await artifact(parent,child,{schema:'liuren-saved-result-v1',parent,child,packet:p,request_ref:ref,raw,checked,pagesVerified});
  state.results[child]={status,request_id:p.request_id,artifact:refResult,submissions:(previous?.submissions??0)+1};
  const a=state.attempts.find(a=>a.child===child);if(a)a.status=status;
  await write(state);
  return checked.ok?{schema:'liuren-adjudication-receipt-v1',task_id:child,request_id:p.request_id,status,result_ref:refResult,contractChecked:true}:{schema:'liuren-adjudication-error-v1',task_id:child,request_id:p.request_id,status,contractChecked:false,result_ref:refResult,issues:checked.issues,action:'只修这些字段并再次liuren_adjudication_submit；保持结论/效力/应期选择，不新建裁决。已结束则用liuren_adjudication_result读取原产物；含混处明确未完成。'};
 }
 async function result(parent,child){const state=await read(parent),r=state.results[child];if(!r)fail('NO_SAVED_RESULT',{task_id:child,action:'先用task_result领取已有子会话输出，不能再派同任务'});return {...r,data:await readArtifact(r.artifact)};}
 async function locate(parent,child){
  const state=await read(parent),available=Object.entries(state.results).map(([task_id,r])=>({task_id,request_id:r.request_id,status:r.status,claimed:!!r.claimed_at}));
  if(child&&state.results[child])return child;
  if(!child&&available.length===1)return available[0].task_id;
  fail(child?'TASK_ID_NOT_OWNED':available.length?'TASK_ID_AMBIGUOUS':'NO_SAVED_RESULT',{task_id:child,available_results:available,action:'task_id只能使用上述子会话ID；不能使用request_id、文件UUID或hash。多项时明确选择，不自动取最新。'});
 }
 async function receipt(parent,child){
  const saved=await result(parent,child),r=saved.data.checked;
  return {schema:'liuren-adjudication-receipt-v1',task_id:child,request_id:saved.request_id,status:saved.status,contractChecked:r.ok,result_ref:saved.artifact,...(!r.ok?{issues:r.issues}:{}),next_call:saved.claimed_at?{tool:'liuren_adjudication_result',arguments:{action:saved.status==='completed'?'deliver':'read',task_id:child}}:{tool:'task_result',arguments:{task_id:child}},action:'此task_id是唯一可传给task_result及结果工具的子会话ID。不要改用request_id或文件编号，不重新派裁决。'};
 }
 async function acknowledge(parent,child){await result(parent,child);const state=await read(parent);state.results[child].claimed_at=new Date().toISOString();await write(state);}
 async function saveFailure(parent,child,p,ref,raw,message){
  const state=await read(parent),checked={ok:false,issues:[{path:'/',code:'execution_error',message}]};
  const artifactRef=await artifact(parent,child,{schema:'liuren-saved-result-v1',parent,child,packet:p,request_ref:ref,raw,checked,pagesVerified:false});
  state.results[child]={status:'invalid_output',request_id:p.request_id,artifact:artifactRef,submissions:1};await write(state);
  return {schema:'liuren-adjudication-error-v1',status:'invalid_output',task_id:child,request_id:p.request_id,result_ref:artifactRef,issues:checked.issues,action:'保留原产物与此具体缺口；不得重派整轮裁决，不由主智能体补判。'};
 }
 async function getResult(parent,child,action,client){
  let saved=await result(parent,child);
  if(action==='repair'&&saved.status==='invalid_output'){
   const {packet,request_ref,raw,pagesVerified}=saved.data;await exclusive(file(parent),()=>saveResult(parent,child,packet,request_ref,raw,{pagesVerified}));saved=await result(parent,child);
  }
  if(!saved.data.checked.ok)return {schema:'liuren-adjudication-error-v1',task_id:child,status:'invalid_output',result_ref:saved.artifact,issues:saved.data.checked.issues,action:'保留具体缺口；不得重派或由主智能体改判'};
  const r=saved.data.checked.result;
  if(action==='deliver'){
   if(r.status!=='completed')fail('RESULT_NOT_COMPLETED',{status:r.status});if(!saved.claimed_at)fail('TASK_RESULT_ACK_REQUIRED',{task_id:child});await coverage(parent,client,{report:true});
   const pointer=await load(path.join(root,'.opencode/liuren-active.json')),manifest=await load(path.join(root,pointer.runtime,'manifest.json'));
   const evidencePath='references/adjudicator-book-evidence.json',evidenceRaw=await fs.readFile(path.join(root,pointer.runtime,evidencePath),'utf8');
   if(hash(evidenceRaw)!==manifest.files[evidencePath])fail('BOOK_EVIDENCE_CHANGED',{});
   const used=new Set([...r.relation_checks.flatMap(x=>x.basis_ids),...r.source_conflicts.flatMap(x=>x.basis_ids),...(r.special_methods??[]).flatMap(x=>x.basis_ids)]);
   const evidence=JSON.parse(evidenceRaw).evidence.filter(e=>used.has(e.id));
   const report=renderReport(r,saved.data.packet,evidence,pointer.release);const receipt=await artifact(parent,child,{schema:'liuren-report-v1',result_sha256:saved.artifact.sha256,request_id:r.request_id,report_markdown:report});
   await exclusive(file(parent),async()=>{const state=await read(parent);state.results[child].delivery=receipt;await write(state);});
   return {schema:'liuren-delivery-v1',task_id:child,request_id:r.request_id,result_ref:saved.artifact,report_ref:receipt,report_markdown:report,policy:'直接交付此技术正文；可调整排版，不增加决定性理由、不改结论/精度/条件'};
  }
  return {schema:'liuren-result-v1',task_id:child,request_id:r.request_id,status:r.status,result:r,execution_receipt:{task_id:child,result_ref:saved.artifact,contractChecked:true}};
 }
 const locked=fn=>(parent,...args)=>exclusive(file(parent),()=>fn(parent,...args));
 return {read,noteMethod:locked(noteMethod),coverage,origin,reserve:locked(reserve),bind:locked(bind),dispatchFailure:locked(dispatchFailure),saveResult:locked(saveResult),saveFailure:locked(saveFailure),result,getResult,locate,receipt,acknowledge:locked(acknowledge)};
}
function renderReport(r,p,evidence=[],release=''){
 const c=p.chart.facts,lines=['# 大六壬研判报告','',`版本：${release}；裁决：${r.request_id}；DeepSeek Flash / high；程序事实校验通过不等于预测效果验证。`,'','## 原问与课盘','',p.input_origin?.source_text??p.questions.map(q=>q.text).join('\n'),'',`四柱：${c.pillars.join(' ')}；月将${c.month_general}；旬空${c.void_branches.join('、')}。`,'','| 四课 | 上神 | 下位 | 天将 |','|---|---|---|---|',...c.lessons.map(l=>`| ${l.index} | ${l.tianpan} | ${l.dizhi} | ${l.tianjiang} |`),'','三传：'+c.transmissions.map(t=>`${t.diZhi}（${t.tianjiang}、${t.liuqin}）`).join(' → '),'','## 取用与复核','',r.scope_review.omission_check,...r.scope_review.corrections.map(t=>'- '+t)];
 for(const e of r.entity_checks){lines.push('',`**${e.id} ${e.referent}：${e.branch}**`,e.position,e.site_yin,'神将：'+e.shenjiang,'原定位依据：'+(p.entities.find(x=>x.id===e.id)?.mapping_basis??'裁决新增实体，见下述复核'),e.mapping_review,...e.limits.map(t=>'限制：'+t));for(const id of e.fact_refs??[]){const n=[...(p.deterministic?.nodes??[]),...(p.deterministic?.stems??[])].find(n=>n.id===id);if(n)lines.push(`程序查表 ${n.symbol}：四时${n.seasonal.profiles['four-seasons']}，季土口径${n.seasonal.profiles['quarter-earth']}；十二气${JSON.stringify(n.growth)}。异口径不计为两票，实际采用见裁决理由。`);}}
 lines.push('','天地盘：'+c.heaven_earth.map(x=>`${x.di}上${x.tian}乘${x.tianjiang}`).join('；'),'');
 if(c.participants)lines.push('年命/行年原始信息：'+JSON.stringify(c.participants)+'；采用范围见取用复核。');
 if(p.observations.length)lines.push('','## 准备阶段核查记录','以下为主智能体交接的观察；是否形成有效作用，以后文裁决为准，不把未核项说成通过。','',...p.observations.map(o=>`${o.id}（${o.verification}）：${o.statement}；参照${o.reference}；来源${o.source}`));
 lines.push('','## 关键作用与最强反证');
 for(const rel of r.relation_checks){lines.push('',`**${rel.id}：${rel.from} → ${rel.to}，${rel.relation}（${rel.validity}）**`,rel.reason,`作用范围：${rel.effect_scope.join('、')}；依据：${rel.basis_ids.join('、')}。`);if(rel.application)lines.push(...Object.entries(rel.application).map(([k,v])=>`${({object:'对象',mechanism:'机制',stage:'阶段',goal_effect:'对目标的作用',alternative_resolution:'另一解释的取舍'})[k]??k}：${v}`));}
 for(const a of r.answers){const q=p.questions.find(q=>q.id===a.question_id);lines.push('',`## ${a.question_id} ${q.text}`,'',`**结论：${a.verdict}**`,`精度：${a.precision}；成功标准：${q.success_criteria}`,`决定性作用：${a.decisive_relation_ids.join('、')}；反证：${a.counter_relation_ids.join('、')||'未列独立反证'}。`,a.counter_resolution,`过程：${a.process}`,`时间：${a.timing}`,...a.conditions.map(t=>'条件：'+t),...a.limits.map(t=>'限制：'+t));}
 if(r.issue_resolutions.length)lines.push('','## 争点处理','',...r.issue_resolutions.map(i=>`${i.issue_id}（${i.status}）：${i.resolution}${i.limits.length?'；限制：'+i.limits.join('；'):''}`));
 const labels={event:'事件',stage:'阶段',scale:'尺度',start:'起算点',count_rule:'计时口径',trigger:'触发条件',selected_method:'选法',round_comparison:'竞争轮次',candidates:'候选日期',object:'对象',position:'位置',number_table:'数表',operation:'算式',adjustments:'调整',magnitude:'量级',unit:'单位',precision:'精度',value:'计算值'};
 for(const s of r.special_methods??[])lines.push('',`## ${s.question_id} ${s.kind==='timing'?'应期':'取数'}（${s.status}）`,'',s.target,...Object.entries(s.record).map(([k,v])=>`${labels[k]??k}：${typeof v==='string'?v:JSON.stringify(v)}`),`方法依据：${s.basis_ids.join('、')}；盘面/观察：${(s.fact_ids??[]).join('、')||'见关键作用'}；计算：${s.calculation_ids.join('、')||'未完成'}。`,...s.alternatives.map(t=>'备选：'+t),...s.limits.map(t=>'限制：'+t));
 const cited=new Set([...r.relation_checks.flatMap(x=>x.basis_ids),...r.source_conflicts.flatMap(x=>x.basis_ids),...(r.special_methods??[]).flatMap(x=>x.fact_ids??[])]);
 const calcs=new Set((r.special_methods??[]).flatMap(x=>x.calculation_ids));
 for(const calc of [...(p.deterministic?.calculations??[]),...(r.calculations??[])].filter(x=>calcs.has(x.id))){const shown=calc.action==='calendar'?{...calc.result,rows:calc.result.rows.filter(row=>(r.special_methods??[]).some(s=>s.kind==='timing'&&s.record.candidates?.some(c=>c.date===row.date)))}:calc.result;lines.push('',`程序计算 ${calc.id}：${JSON.stringify({...calc,result:shown})}`);}
 lines.push('','## 来源与缺口','',...p.method_materials.map(m=>`- ${m.id} ${m.title}：${m.source_path}:${m.line_start}-${m.line_end}`),...p.facts.filter(x=>cited.has(x.id)).map(x=>`- ${x.id}：${x.text}（${x.source}）`),...p.observations.filter(x=>cited.has(x.id)).map(x=>`- ${x.id}：${x.statement}；${x.reference}；${x.source}（${x.verification}，是否有效见裁决）`),...evidence.map(e=>`- ${e.id}：${e.path}:${e.line_start}-${e.line_end}`),'固定书据E01–E22见同版 references/adjudicator-book-evidence.json；本次未检索案例库、经验库。',...r.source_conflicts.map(x=>`来源分歧：${x.issue}；${x.resolution}`),...p.unknowns.map(t=>'原始未知：'+t));
 return lines.join('\n')+'\n';
}
