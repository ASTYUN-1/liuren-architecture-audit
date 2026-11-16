// Structured submission and diagnostics. No outcome selection or new interpretation.
import {contractScalars} from './liuren-adjudication-schema.mjs';
import {symbols,canonicalEntity} from './liuren-deterministic.mjs';
import {finalizeFoundation} from './liuren-deterministic-io.mjs';
import {validateOutput} from './liuren-adjudication-contract.mjs';
export const ENTITY_PATTERN=/^(?:[甲乙丙丁戊己庚辛壬癸]|[子丑寅卯辰巳午未申酉戌亥]{1,12}|[甲乙丙丁戊己庚辛壬癸][（(]寄宫[子丑寅卯辰巳午未申酉戌亥][）)])$/;
const programFields=['position','five_qi','twelve_states','site_yin','shenjiang','fact_refs'];
export function createOutputSchema(s,computation){
 const {text,id,texts:makeTexts}=contractScalars(s);
 const texts=makeTexts(),candidate=s.object({date:text(),day:text(),event:text()}).strict();
 const shared={question_id:id(),status:s.enum(['completed','unresolved']),target:text(),basis_ids:texts.describe('只填E01-E22或M方法来源；盘面/观察放fact_ids'),fact_ids:texts.optional(),calculation_ids:texts,alternatives:texts,limits:texts};
 const timing=s.object({...shared,kind:s.literal('timing'),record:s.object({event:text(),stage:text(),scale:text(),start:text(),count_rule:text(),trigger:text(),selected_method:text(),round_comparison:text(),candidates:s.array(candidate).max(732).optional()}).strict()}).strict();
 const quantity=s.object({...shared,kind:s.literal('quantity'),record:s.object({object:text(),position:text(),number_table:text(),operation:text(),adjustments:text(),magnitude:text(),unit:text(),precision:text(),value:s.number().optional()}).strict()}).strict();
 return s.object({
  schema:s.literal('liuren-adjudication-output-v2'),request_id:id(),status:s.enum(['completed','needs_input']),
  scope_review:s.object({question_ids:texts,mapping_status:s.enum(['confirmed','corrected','needs_input']),added_entity_ids:texts,corrections:texts,omission_check:text()}).strict(),
  entity_checks:s.array(s.object({id:id(),referent:text(),branch:text().regex(ENTITY_PATTERN).describe('仅干支/纯支组合/戊（寄宫巳），注释放mapping_review'),mapping_review:text(),limits:texts}).strict()).max(60),
  relation_checks:s.array(s.object({id:id(),from:id(),to:id(),relation:text(),validity:s.enum(['effective','limited','ineffective','unresolved']),basis_ids:texts,reason:text(),effect_scope:texts,application:s.object({object:text(),mechanism:text(),stage:text(),goal_effect:text(),alternative_resolution:text()}).strict().optional()}).strict()).max(100),
  issue_resolutions:s.array(s.object({issue_id:id(),status:s.enum(['resolved','unresolved']),relation_ids:texts,resolution:text(),limits:texts}).strict()).max(12),
  answers:s.array(s.object({question_id:id(),verdict:text(),precision:s.enum(['exact','direction','unresolved']),decisive_relation_ids:texts,counter_relation_ids:texts,counter_resolution:text(),process:text(),timing:text(),conditions:texts,limits:texts}).strict()).min(1).max(12),
  source_conflicts:s.array(s.object({basis_ids:texts,issue:text(),resolution:text()}).strict()).max(100),missing_inputs:texts,
  special_methods:s.array(s.discriminatedUnion('kind',[timing,quantity])).max(24),calculations:s.array(computation).max(30)
 }).strict();
}
export function checkSubmission(root,raw,p){
 const r=structuredClone(raw),issues=[],repairs=[];
 const issue=(path,code,value,expected)=>issues.push({path,code,value,expected});
 const methods=new Set([...p.method_materials.map(m=>m.id),...Array.from({length:22},(_,i)=>'E'+String(i+1).padStart(2,'0'))]);
 const facts=new Set([...p.facts.map(f=>f.id),...p.observations.map(o=>o.id),...(p.deterministic?.nodes??[]).map(n=>n.id),...(p.deterministic?.stems??[]).map(n=>n.id)]);
 if(!r||typeof r!=='object'||Array.isArray(r))return {ok:false,issues:[{path:'/',code:'object_required',expected:'output-v2 object'}]};
 for(const [i,e] of (Array.isArray(r.entity_checks)?r.entity_checks:[]).entries()){
  const at='/entity_checks/'+i;
  if(!e||typeof e!=='object'||Array.isArray(e)){issue(at,'object_required',e,'entity object');continue;}
  // Only strip an annotation containing NO other stem/branch. Never guess a mixed object.
  if(typeof e.branch==='string'&&!ENTITY_PATTERN.test(e.branch)){
   const match=/^([甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥]+)[（(]([^甲乙丙丁戊己庚辛壬癸子丑寅卯辰巳午未申酉戌亥]*)[）)]$/.exec(e.branch);
   if(match&&ENTITY_PATTERN.test(match[1])){repairs.push({path:at+'/branch',before:e.branch,after:match[1],kind:'unambiguous_annotation'});e.mapping_review=(e.mapping_review??'')+'；原标识注释：'+match[2];e.branch=match[1];}
  }
  try{
   symbols(e.branch);
   if(p.deterministic){const expected=canonicalEntity(e.branch,p.deterministic);for(const k of programFields)if(e[k]!==undefined&&JSON.stringify(e[k])!==JSON.stringify(expected[k]))issue(at+'/'+k,'program_field_mismatch',e[k],'omit this field; computed by program');}
  }catch{issue(at+'/branch','invalid_symbol',e.branch,'single stem/branch, pure branch combination, or 戊（寄宫巳）; explain separately');}
 }
 for(const [i,s] of (Array.isArray(r.special_methods)?r.special_methods:[]).entries()){
  const at='/special_methods/'+i;
  if(!s||typeof s!=='object'||Array.isArray(s)){issue(at,'object_required',s,'special method object');continue;}
  for(const k of ['basis_ids','fact_ids','calculation_ids','alternatives','limits'])if(s[k]!==undefined&&!Array.isArray(s[k]))issue(at+'/'+k,'array_required',s[k],'array');
  if(issues.some(e=>e.path.startsWith(at+'/')))continue;
  if(Array.isArray(s.basis_ids)){
   const split=s.basis_ids.filter(id=>facts.has(id)&&!methods.has(id));
   if(split.length){s.basis_ids=s.basis_ids.filter(id=>!split.includes(id));s.fact_ids=[...new Set([...(s.fact_ids??[]),...split])];repairs.push({path:at+'/basis_ids',kind:'partition_fact_references',fact_ids:split});}
  }
  if(s.kind==='timing'&&s.candidates!==undefined&&s.record&&typeof s.record==='object'){
   if(s.record.candidates!==undefined&&JSON.stringify(s.record.candidates)!==JSON.stringify(s.candidates))issue(at+'/record/candidates','conflicting_locations',s.candidates,'one unchanged candidate list under record');
   else {s.record.candidates=s.candidates;delete s.candidates;repairs.push({path:at+'/record/candidates',kind:'move_field_only'});}
  }
  for(const k of ['question_id','kind','status','target','basis_ids','calculation_ids','alternatives','limits','record'])if(s[k]===undefined)issue(at+'/'+k,'required',null,'required special method field');
  if(s.basis_ids?.some(id=>!methods.has(id)))issue(at+'/basis_ids','method_ids_only',s.basis_ids,'E01-E22 or supplied method IDs; facts go in fact_ids');
  if(s.fact_ids?.some(id=>!facts.has(id)))issue(at+'/fact_ids','unknown_fact_reference',s.fact_ids,'known input fact, observation or D_* ID');
  if(s.status==='completed'&&s.kind==='timing'&&!s.record?.candidates?.length)issue(at+'/record/candidates','required',null,'[{date,day,event}] checked against calendar');
  if(s.status==='completed'&&s.kind==='quantity'&&!Number.isFinite(s.record?.value))issue(at+'/record/value','required',s.record?.value,'numeric calculated value');
 }
 if(issues.length)return {ok:false,issues,repairs};
 try{return {ok:true,result:validateOutput(finalizeFoundation(root,r,p),p),issues:[],repairs};}
 catch(error){return {ok:false,issues:[{path:error.path??'/',code:'contract_error',message:String(error),expected:'correct only the reported contract; do not rejudge the case'}],repairs};}
}
