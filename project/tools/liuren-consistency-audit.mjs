// Evidence/receipt consistency only. No model calls, scoring or outcome selection.
import {createHash} from 'node:crypto';
import fs from 'node:fs/promises';
import {quantityReviewSchema,checkQuantityReviews,QUANTITY_REVIEW_GUIDE} from './liuren-quantity-review.mjs';
import {routeSchema} from './liuren-analysis-route.mjs';
export const AUDIT_SCHEMA='liuren-consistency-audit-v1';
export const POLICY={schema:AUDIT_SCHEMA,enabled:true,maxRechecks:1};
export const auditHash=value=>createHash('sha256').update(typeof value==='string'?value:JSON.stringify(value)).digest('hex');
export const loadedAuditSha256=auditHash(await fs.readFile(new URL(import.meta.url),'utf8'));
export const audited=p=>p?.consistency_policy?.schema===AUDIT_SCHEMA&&p.consistency_policy.enabled===true;
export const REVIEW_CHECKS=['input_fidelity','role_stage_consistency','calculation_scope','counterevidence','answer_constraints'];
export const REVIEW_GUIDE='五项实质复核：input_fidelity核原问实际事件及事实身份；role_stage_consistency逐问对route核专项分支、主次与时段，首取在实判中须实际生效；calculation_scope核基数/数法/量级及已含因素，回执一致不证明理由成立；counterevidence核施受双方、通路、救谁制谁、解除范围和时序；answer_constraints核逐问直接回答、精度和限制。新路线任务每项evidence_refs附input/core/domain:本问/材料ID/route:问ID/真实回执hash；职责项覆盖各route:问ID。题意、首取、有效制救及量级不符是可补核的一致性问题；一次recheck聚焦这些实质缺口，不预先锁定原结论或数字。无法核实标unresolved。';
export const AUDIT_GUIDE=`39版一致性附件：正文仍自由Markdown，不提交私下推理。submit另给audit，schema=${AUDIT_SCHEMA}。questions每问一项：question_id、request_quote(原问逐字片段)、stage_origin(user_explicit/inferred/unknown)、stage_basis(明确阶段附原问引句，推断/未知如实标记)、success_review、answer_quote(正文逐字片段)、candidates(有数量限制时列边界清楚的职能候选；否则[])、counterevidence:{present,relation_ids,report_quote,resolution,basis_refs}。relations仅登记决定性作用与最强反证：id、source/target(程序对象如T:寅、S:丙)、question_ids、role(support/obstruction/rescue/context)、basis_refs、basis、effect_scope、disposition(used/limited/excluded/unresolved)、reason、report_quote、numeric(supported/qualitative_only)。完整盘查漏，候选可纠正；未采用的反证须解释，救应须核到达和解除范围，不因不克日干排除所求受阻。basis_refs可用program/core/domain:本问domain/已绑定材料ID。calculations每个被正文引用的strength回执一项：receipt_sha256(计算返回calculation_receipt.sha256)、scope(local/combined)、relation_ids、report_quote、score_claims:[{actor,path,value,report_quote}]；path是该回执result中的JSON Pointer，可用liuren_adjudication_audit(action=receipts)查真实回执。local只代表局部情景；combined须覆盖已登记、同问且涉及本次对象的有效数值作用，不能把分开的局部扶助冒充综合结果；定性刑冲不强行量化。不引用分数则calculations=[]。最后omission_review简述查漏结果，不穷举全盘。程序核结构、原句、引用和回执，不判专业效力。`+"\n"+QUANTITY_REVIEW_GUIDE;

export function createAuditSchemas(s){
 const t=s.string().min(1).max(4000),quote=s.string().min(1).max(16000),refs=s.array(t).max(40);
 const origin=s.enum(['user_explicit','inferred','unknown']);
 const stageBasis=t.describe('stage_origin=user_explicit时，本字段只能填原始用户消息中的连续逐字片段，例如“9月5号已考完试，10月底出成绩”；不要加“用户明确”、引号或解释。阶段解释放success_basis/route；推断用inferred，未知用unknown。');
 const input=s.object({questions:s.array(s.object({question_id:t,request_quote:quote.describe('原始用户消息连续逐字片段，不能用重写后的questions.text'),success_basis:t,stage_origin:origin,stage_basis:stageBasis,route:routeSchema(s).optional(),max_candidates:s.number().int().min(1).max(12).optional(),limit_quote:quote.optional()}).strict()).min(1).max(12),facts:s.array(s.object({fact_id:t,origin,source_quote:quote.optional(),basis:t}).strict()).max(100),neutrality_review:t}).strict();
 const audit=s.object({schema:s.literal(AUDIT_SCHEMA),questions:s.array(s.object({question_id:t,request_quote:quote,stage_origin:origin,stage_basis:t,success_review:t,answer_quote:quote,candidates:s.array(t).max(20),counterevidence:s.object({present:s.boolean(),relation_ids:refs,report_quote:s.string().max(16000),resolution:t,basis_refs:refs}).strict()}).strict()).min(1).max(12),relations:s.array(s.object({id:t,source:t,target:t,question_ids:refs,role:s.enum(['support','obstruction','rescue','context']),basis_refs:refs,basis:t,effect_scope:t,disposition:s.enum(['used','limited','excluded','unresolved']),reason:t,report_quote:quote,numeric:s.enum(['supported','qualitative_only'])}).strict()).max(40),calculations:s.array(s.object({receipt_sha256:t,scope:s.enum(['local','combined']),relation_ids:refs,report_quote:quote,score_claims:s.array(s.object({actor:t,path:t,value:s.number().finite(),report_quote:quote}).strict()).max(40)}).strict()).max(30),omission_review:t,quantity_reviews:quantityReviewSchema(s)}).strict();
 const evidenceRefs=refs.describe('从result read/help返回的evidence_catalog.allowed_refs原样选ID，不填路径:行号、算法说明或猜测hash。职责项须含每个route:问ID。');
 const finding=s.object({check:s.enum(REVIEW_CHECKS),report_quote:quote.describe('当前公开报告连续逐字片段，不把多处原文拼接'),evidence_refs:evidenceRefs.min(1),evidence:t,request:t}).strict();
 const review=s.object({report_sha256:s.string().regex(/^[a-f0-9]{64}$/),checks:s.array(s.object({check:s.enum(REVIEW_CHECKS),status:s.enum(['checked','unresolved']),report_quote:quote.describe('当前报告连续逐字片段，不能用省略号拼接'),basis:t,evidence_refs:evidenceRefs.optional()}).strict()).length(5)}).strict().describe('外层调用必须为{action:"review",task_id,review:{report_sha256,checks:[...]}}。'+REVIEW_GUIDE);
 return {input,audit,finding,review};
}
const nonempty=v=>typeof v==='string'&&!!v.trim();
const array=v=>Array.isArray(v)?v:[];
const object=v=>v&&typeof v==='object'&&!Array.isArray(v);
function issuesCollector(){const issues=[];return {issues,add:(code,path,message)=>issues.push({code,path,message})};}
function exact(source,quote){return nonempty(quote)&&source.includes(quote);}
function quotedNumbers(text){const nums={'一':1,'二':2,'两':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,'十':10};return [...text.matchAll(/(?:限|至多|最多|不超过)\s*([一二两三四五六七八九十]|\d{1,2})/g)].map(m=>nums[m[1]]??Number(m[1]));}

export function checkInputReview(p){
 const c=issuesCollector(),review=p.input_review,source=p.input_origin?.source_text??'';
 if(!object(review)||!nonempty(review.neutrality_review)||!Array.isArray(review.questions)||!Array.isArray(review.facts)){c.add('input_review_required','/input_review','保留原问依据、阶段来源、事实身份与中性交接复核');return {ok:false,issues:c.issues};}
 const ids=new Set();
 for(const [i,row] of review.questions.entries()){
  const at='/input_review/questions/'+i,q=p.questions.find(q=>q.id===row?.question_id);
  if(!q||ids.has(row.question_id)){c.add('question_identity',at,'每个原问题ID恰好一次');continue;}ids.add(row.question_id);
  if(!exact(source,row.request_quote))c.add('original_quote',at+'/request_quote','必须是原始用户消息逐字片段');
  if(!nonempty(row.success_basis)||!nonempty(row.stage_basis)||!['user_explicit','inferred','unknown'].includes(row.stage_origin))c.add('input_provenance',at,'成功标准依据、阶段来源和依据须完整');
  if(row.stage_origin==='user_explicit'&&!exact(source,row.stage_basis))c.issues.push({code:'stage_quote',path:at+'/stage_basis',message:'stage_basis整个字段必须是原问连续逐字片段，不要加解释或引号；推断和未知另行标记',received:row.stage_basis,source_excerpt:source.slice(0,1600)});
  if(row.max_candidates!==undefined&&(!Number.isInteger(row.max_candidates)||row.max_candidates<1||row.max_candidates>12||!exact(source,row.limit_quote)||!quotedNumbers(row.limit_quote??'').includes(row.max_candidates)))c.add('candidate_limit_basis',at,'候选上限须绑定含明确数量限制的原问引句');
  if(quotedNumbers(row.request_quote??'').length&&row.max_candidates===undefined)c.add('candidate_limit_missing',at,'原问片段有明确候选数量限制，须登记max_candidates及limit_quote');
 }
 if(ids.size!==p.questions.length)c.add('question_coverage','/input_review/questions','必须覆盖全部子问');
 const facts=new Set();
 for(const [i,row] of review.facts.entries()){
  const at='/input_review/facts/'+i;
  if(!p.facts.some(f=>f.id===row?.fact_id)||facts.has(row.fact_id))c.add('fact_identity',at,'每条补充现实事实须对应唯一fact_id');facts.add(row?.fact_id);
  if(!['user_explicit','inferred','unknown'].includes(row?.origin)||!nonempty(row?.basis))c.add('fact_provenance',at,'事实须区分用户明确、推断、未知并附依据；程序核算不确认输入');
  if(row?.origin==='user_explicit'&&!exact(source,row.source_quote))c.add('fact_quote',at,'用户确认事实须附原问逐字引句');
 }
 if(facts.size!==p.facts.length)c.add('fact_coverage','/input_review/facts','全部补充现实事实须登记来源身份');
 return {ok:!c.issues.length,issues:c.issues};
}

export function receiptRows(receipts){return array(receipts).map(row=>({receipt_sha256:row.ref?.sha256??row.receipt_sha256,request:row.request,result:row.result}));}
function atPointer(value,pointer){
 if(typeof pointer!=='string'||!pointer.startsWith('/'))return undefined;
 for(const token of pointer.slice(1).split('/')){if(/~(?![01])/.test(token))return undefined;const key=token.replaceAll('~1','/').replaceAll('~0','~');if(!object(value)&&!Array.isArray(value)||!Object.hasOwn(value,key))return undefined;value=value[key];}return value;
}
function basisKnown(p,id){return p.consistency_policy?.bound_method_source_ids?.includes(id)||p.input_review?.questions?.some(q=>q.route&&id==='route:'+q.question_id)||id==='program'||id==='core'||id==='input'||p.questions.some(q=>id===q.id||id==='input:'+q.id||id==='domain:'+q.domain)||[...(p.entities??[]),...(p.method_materials??[]),...(p.material_aliases??[]),...(p.observations??[]),...(p.facts??[])].some(m=>m.id===id)||/^E(?:0[1-9]|1[0-9]|2[0-2])$/.test(id);}

// An allowlist of real, bound identities; this does not establish professional efficacy.
export function evidenceCatalog(p,receipts=[]){
 const route_refs=(p.input_review?.questions??[]).filter(q=>q.route).map(q=>'route:'+q.question_id);
 const allowed_refs=[...new Set(['input','program','core',...p.questions.flatMap(q=>[q.id,'input:'+q.id,'domain:'+q.domain]),...route_refs,
  ...['entities','method_materials','material_aliases','observations','facts'].flatMap(k=>(p[k]??[]).map(m=>m.id)),...(p.consistency_policy?.bound_method_source_ids??[]),
  ...Array.from({length:22},(_,i)=>'E'+String(i+1).padStart(2,'0')),...receiptRows(receipts).map(r=>r.receipt_sha256).filter(Boolean)])];
 return {allowed_refs,required_role_refs:route_refs,scope:'仅本任务已绑定身份/来源及真实回执；ID有效不证明应用正确。路径:行号和方法名称不能冒充ID。'};
}

export function reviewScaffold(p,report,receipts=[],task_id){
 return {tool:'liuren_adjudication_result',arguments:{action:'review',...(task_id?{task_id}:{}),review:{report_sha256:auditHash(typeof report==='string'?report:JSON.stringify(report)),checks:REVIEW_CHECKS.map(check=>({check,status:'unresolved',report_quote:'',basis:'',evidence_refs:[]}))}},
  fill_required:true,instruction:'这是待人工/模型实质填写的骨架，不可原样执行。逐项阅读核对后填当前报告连续原句、依据和合法引用；不得为过检自动标checked。',evidence_catalog:evidenceCatalog(p,receipts)};
}
export function checkAudit(p,report,audit,receipts=[]){
 const c=issuesCollector(),warnings=[],body=typeof report==='string'?report:JSON.stringify(report),report_sha256=auditHash(body);
 const done=()=>({schema:AUDIT_SCHEMA,ok:!c.issues.length,issues:c.issues,warnings,report_sha256,validationScope:'declared-evidence-and-receipt-consistency',professionalContentChecked:false});
 if(!audited(p))return null;
 if(audit?.schema!==AUDIT_SCHEMA||!Array.isArray(audit.questions)||!Array.isArray(audit.relations)||!Array.isArray(audit.calculations)||!nonempty(audit.omission_review)){c.add('audit_required','/audit','缺少完整一致性附件：需逐问核对、关键关系、引用计算与查漏记录。按核心consistency_guide补齐；原报告保留。');return done();}
 if(audit.questions.length>12||audit.relations.length>40||audit.calculations.length>30){c.add('audit_limit','/audit','附件超过精简数量上限');return done();}
 const source=p.input_origin?.source_text??'',qids=new Set(),rids=new Set();
 const known=new Set([...(p.deterministic?.nodes??[]).flatMap(n=>['T:'+n.symbol,'J:'+n.general]),...(p.deterministic?.stems??[]).map(n=>'S:'+n.symbol)]);
 const quote=(v,at)=>{if(!exact(body,v))c.add('report_quote',at,'必须逐字定位当前报告公开正文');};
 const basis=(values,at)=>{if(!Array.isArray(values)||!values.length||values.some(id=>!basisKnown(p,id)))c.add('basis_reference',at,'须引用本任务program/core/domain:占类/绑定材料/观察/事实ID');};
 for(const [i,r] of audit.relations.entries()){
  const at='/audit/relations/'+i;if(!object(r)){c.add('relation_shape',at,'关系须为对象');continue;}
  if(!nonempty(r.id)||rids.has(r.id))c.add('relation_identity',at,'关系ID须唯一');rids.add(r.id);
  if(!known.has(r.source)||!known.has(r.target))c.add('relation_actor',at,'source/target须为本盘程序对象ID');
  if(!array(r.question_ids).length||r.question_ids.some(id=>!p.questions.some(q=>q.id===id)))c.add('relation_question',at,'关系须指向本任务子问');
  if(!['support','obstruction','rescue','context'].includes(r.role)||!['used','limited','excluded','unresolved'].includes(r.disposition)||!['supported','qualitative_only'].includes(r.numeric)||!['basis','effect_scope','reason'].every(k=>nonempty(r[k])))c.add('relation_review',at,'登记作用方向、适用依据、结果环节、限制与制救处理');
  basis(r.basis_refs,at+'/basis_refs');quote(r.report_quote,at+'/report_quote');
  if(r.disposition==='unresolved')c.add('unresolved_relation',at,'决定性关系仍未解决；补核后仍未解决须显式保留缺口');
 }
 for(const [i,q] of audit.questions.entries()){
  const at='/audit/questions/'+i;if(!object(q)){c.add('question_shape',at,'逐问核对须为对象');continue;}
  if(!p.questions.some(x=>x.id===q.question_id)||qids.has(q.question_id))c.add('question_identity',at,'每问恰好一次');qids.add(q.question_id);
  if(!exact(source,q.request_quote))c.add('original_quote',at+'/request_quote','须绑定原问逐字片段');
  if(!['user_explicit','inferred','unknown'].includes(q.stage_origin)||!nonempty(q.stage_basis)||!nonempty(q.success_review))c.add('stage_review',at,'阶段来源和成功标准复核须完整');
  if(q.stage_origin==='user_explicit'&&!exact(source,q.stage_basis))c.add('stage_quote',at+'/stage_basis','用户明确阶段须附原问引句；不得把流程推断改成已知事实');
  quote(q.answer_quote,at+'/answer_quote');
  const limit=p.input_review?.questions.find(x=>x.question_id===q.question_id)?.max_candidates;
  if(!Array.isArray(q.candidates)||limit&&(q.candidates.length<1||q.candidates.length>limit||new Set(q.candidates).size!==q.candidates.length))c.add('candidate_count',at+'/candidates','候选必须遵守原问数量上限且不能重复；候选职能边界另由主智能体复核');
  const counter=q.counterevidence;
  if(!object(counter)||typeof counter.present!=='boolean'||!nonempty(counter.resolution)||!Array.isArray(counter.relation_ids)){c.add('counter_review',at,'登记最强反证及其处理；无真实反证须说明理由');continue;}
  if(counter.relation_ids.some(id=>!rids.has(id)))c.add('counter_relation',at,'反证只能引用本附件关系ID');
  if(counter.present){quote(counter.report_quote,at+'/counterevidence/report_quote');basis(counter.basis_refs,at+'/counterevidence/basis_refs');}
  const obstacles=audit.relations.filter(r=>r?.question_ids?.includes(q.question_id)&&r.role==='obstruction');
  if(obstacles.length&&!counter.present||obstacles.some(r=>!counter.relation_ids.includes(r.id)))c.add('counter_coverage',at,'已登记的不利关系须纳入反证处理，不能只留下正向依据');
 }
 if(qids.size!==p.questions.length)c.add('question_coverage','/audit/questions','全部原问必须逐项核对');
 const rows=receiptRows(receipts);
 for(const [i,calc] of audit.calculations.entries()){
  const at='/audit/calculations/'+i;if(!object(calc)){c.add('calculation_shape',at,'计算核对须为对象');continue;}
  const receipt=rows.find(r=>r.receipt_sha256===calc.receipt_sha256);
  quote(calc.report_quote,at+'/report_quote');
  if(!receipt||receipt.request?.action!=='strength'){c.add('receipt_identity',at,'须引用本任务实际strength回执sha256');continue;}
  const links=receipt.request.strength?.links??[],actors=new Set((receipt.request.strength?.actors??[]).map(a=>a.id));
  if(!['local','combined'].includes(calc.scope)||!Array.isArray(calc.relation_ids)||!Array.isArray(calc.score_claims)){c.add('calculation_scope',at,'声明local/combined、关系ID及分数引用');continue;}
  for(const id of calc.relation_ids){const rel=audit.relations.find(r=>r.id===id);if(!rel||!links.some(l=>l.source===rel.source&&l.target===rel.target))c.add('receipt_relation',at,'所称已计算关系没有进入该回执：'+id);}
  const questions=new Set(audit.relations.filter(r=>calc.relation_ids.includes(r.id)).flatMap(r=>r.question_ids));
  const relevant=audit.relations.filter(r=>['used','limited'].includes(r.disposition)&&r.numeric==='supported'&&(!questions.size||r.question_ids.some(id=>questions.has(id)))&&(actors.has(r.source)||actors.has(r.target)));
  const omitted=relevant.filter(r=>!links.some(l=>l.source===r.source&&l.target===r.target));
  if(omitted.length){const item={code:'scenario_coverage',path:at,message:'该数值情景未含已登记关键关系：'+omitted.map(r=>r.id).join(',')};if(calc.scope==='combined')c.issues.push(item);else warnings.push({...item,message:item.message+'；局部分数不代表整体作用链，主智能体须核适用范围'});}
  for(const [j,claim] of calc.score_claims.entries()){
   quote(claim?.report_quote,at+'/score_claims/'+j);
   const actorMatch=/^\/actors\/(\d+)\//.exec(claim?.path??'');
   if(!actors.has(claim?.actor)||!actorMatch||receipt.result?.actors?.[Number(actorMatch[1])]?.id!==claim.actor||typeof claim?.value!=='number'||atPointer(receipt.result,claim?.path)!==claim.value)c.add('receipt_value',at+'/score_claims/'+j,'对象、JSON Pointer与数值须匹配真实回执');
  }
 }
 c.issues.push(...checkQuantityReviews(p,body,audit,rows));
 return done();
}

export function checkDeliveryReview(review,report,{packet,receipts=[]}={}){
 const c=issuesCollector(),body=typeof report==='string'?report:JSON.stringify(report);
 if(!object(review)||review.report_sha256!==auditHash(body)||!Array.isArray(review.checks)){c.add('delivery_review_required','/review','主智能体须对当前报告hash完成五项核对');return {ok:false,issues:c.issues};}
 const seen=new Set();for(const [i,row] of review.checks.entries()){
  const at='/review/checks/'+i;
  if(!REVIEW_CHECKS.includes(row?.check)||seen.has(row.check)||!['checked','unresolved'].includes(row.status)||!nonempty(row.basis))c.add('delivery_review',at,'check须唯一、status为checked/unresolved且basis非空；未解决如实标记');
  if(!exact(body,row?.report_quote))c.add('report_quote',at+'/report_quote','必须复制当前报告连续原句，不拼接、不改标点；用result read取原文');
  seen.add(row?.check);
 }
 if(seen.size!==5)c.add('delivery_review_coverage','/review/checks','须覆盖五项核对');
 if(packet?.consistency_policy?.analysis_route_required){
  const hashes=new Set(receiptRows(receipts).map(r=>r.receipt_sha256));
  const known=id=>id==='input'||basisKnown(packet,id)||hashes.has(id)||packet.questions.some(q=>id==='route:'+q.id);
  for(const [i,row] of review.checks.entries()){
   const at='/review/checks/'+i+'/evidence_refs',unknown_refs=array(row.evidence_refs).filter(id=>!known(id));
   if(!array(row.evidence_refs).length||unknown_refs.length)c.issues.push({code:'review_evidence',path:at,check:row.check,message:'实质核对须附本任务合法引用；只替换下列未知ID，保留真实核对理由',unknown_refs});
   const missing=packet.questions.filter(q=>!array(row.evidence_refs).includes('route:'+q.id)).map(q=>'route:'+q.id);
   if(row.check==='role_stage_consistency'&&missing.length)c.issues.push({code:'review_route_coverage',path:at,message:'职责项须覆盖每问route',missing_refs:missing});
  }
 }
 return {ok:!c.issues.length,issues:c.issues,unresolved:array(review.checks).filter(r=>r.status==='unresolved')};
}
export function inspectRecheckFindings(p,report,findings,receipts=[]){
 const body=typeof report==='string'?report:JSON.stringify(report),hashes=new Set(receiptRows(receipts).map(r=>r.receipt_sha256));
 const issues=[];
 if(!Array.isArray(findings)||!findings.length||findings.length>5)return {ok:false,issues:[{code:'findings_shape',path:'/findings',message:'须1..5项具体补核事项'}]};
 for(const [i,f] of findings.entries()){
  const at='/findings/'+i;
  if(!object(f)){issues.push({code:'finding_shape',path:at,message:'补核项须为对象'});continue;}
  if(!REVIEW_CHECKS.includes(f.check))issues.push({code:'finding_check',path:at+'/check',allowed:REVIEW_CHECKS});
  if(!exact(body,f.report_quote))issues.push({code:'report_quote',path:at+'/report_quote',message:'必须是当前报告连续逐字片段；不得拼接或改标点'});
  for(const key of ['evidence','request'])if(!nonempty(f[key]))issues.push({code:'finding_required',path:at+'/'+key,message:'须填写具体证据/补核事项'});
  const unknown_refs=array(f.evidence_refs).filter(id=>!basisKnown(p,id)&&!hashes.has(id));
  if(!array(f.evidence_refs).length||unknown_refs.length)issues.push({code:'finding_evidence',path:at+'/evidence_refs',unknown_refs,message:'从evidence_catalog.allowed_refs选真实已绑定ID'});
 }
 return {ok:!issues.length,issues};
}
export const checkRecheckFindings=(...args)=>inspectRecheckFindings(...args).ok;
