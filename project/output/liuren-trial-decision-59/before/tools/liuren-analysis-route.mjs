// Model-authored event routing and bound evidence transport. This module checks
// identities/coverage, never selects a class-god or decides professional efficacy.
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
export const loadedRouteSha256=createHash('sha256').update(await readFile(new URL(import.meta.url))).digest('hex');
export const ROUTE_POLICY='liuren-analysis-route-v1';
export const DOMAIN_ROUTES={
 relationship:'婚配成否、关系现状、对方态度、复合及财礼分事件；先双方关系，专类按各自职责。',
 exam:'日常成绩、某科过关、升学录取、职称评定拿证、通知分流；某一专业科过线首重幕贵，不由考试名称直接转拿证。',
 recruitment:'一般求职、特定单位录用、报到、待遇分别定位；求职首禄，指定录用另核单位接纳。',
 'promotion-salary':'任职、晋升、调动、加薪、实际到账分流；职位专类与德禄贵人分工，动象须落实到所求变化。',
 finance:'财源、经营持续、盈利、约定款实得、净额分流；实得以财爻及与取双方为主线。',
 'lost-person-object':'先分人、物、宠物及遗忘/被盗等已知身份；本物专类、当事年命、盗者与寻回分职责。',
 litigation:'已涉司法程序或问会否涉诉；诉讼本体勾陈首取，朱雀按原法递补；胜诉、处罚与执行兑现分流。',
 interpersonal:'普通争执、信任、态度与合作关系；已有诉讼或明确问诉讼结果转litigation。',
 illness:'患者、疾病、病程、治疗与恢复分流；核病与人、救治与制救，不把病弱等同病人衰败。',
 pregnancy:'有孕、胎儿、母体、分娩各定对象与节点，不能以其中一个结果替代全部。',
 home:'宅况、人宅损益、构件、迁居、交易、产权与付款分流；跨事项按子问接finance/travel等。',
 travel:'能动、成行、途中、到达、办成、归来与音信分流；人到和消息到不是同一事件。',
 weather:'地点时段及具体天气现象；人物不是必需主位，受灾与损失另接home/agriculture。',
 agriculture:'农作、畜养、渔猎、生长与收获分流；养旺与捕获的目标作用不同，获物与收益另核。',
 'period-outlook':'限定时段的处境与各生活主题，整体气势定侧重；具体事件另按相应专项。',
 'long-period':'长期占事按实际所求与阶段分析，不转出生推命；时间跨度不改变具体事件的职责。',
 'classical-conflict':'兵事攻守、盗捕逃亡的专法；普通口角不套兵占，普通失物先lost-person-object。'
};
export const ROUTE_GUIDE='按可验收的事件选择专项分支，不按题目关键词。每问input_review.questions[].route登记event(所求事件/量)、focus(class/relationship/overall/unresolved)、primary_entity_ids、selection_basis(适用条件、首取或递补依据)、time_scope(结果形成/评定/通知/兑现的职责)。关系主线标双方，整体主线可无单一主类；不是每题强造一个类神。路线为有依据候选，不是预断，独立裁决可纠正并在正文说明原问/条件/职责为何改变。后续所有有效作用、制救、反证、应期与取数回到此事件核验。';
const nonempty=x=>typeof x==='string'&&!!x.trim();
export function routeSchema(s){const t=s.string().min(1).max(4000);return s.object({
 event:t,focus:s.enum(['class','relationship','overall','unresolved']),primary_entity_ids:s.array(t).max(12),selection_basis:t,time_scope:t
}).strict().describe(ROUTE_GUIDE);}
export function checkRoutes(p,{required=false}={}){
 const issues=[],add=(path,message)=>issues.push({code:'analysis_route',path,message});
 for(const [i,q] of (p.questions??[]).entries()){
  const row=p.input_review?.questions?.find(r=>r.question_id===q.id),r=row?.route,at='/input_review/questions/'+i+'/route';
  if(!r){if(required)add(at,'每问先确定所求事件、分析侧重、主候选职责及时间口径');continue;}
  if(!['class','relationship','overall','unresolved'].includes(r.focus)||!['event','selection_basis','time_scope'].every(k=>nonempty(r[k]))||!Array.isArray(r.primary_entity_ids)){
   add(at,'路线须完整；程序不决定取用或成败');continue;}
  const ids=r.primary_entity_ids;
  if(ids.length>12||new Set(ids).size!==ids.length||ids.some(id=>!p.entities?.some(e=>e.id===id&&e.question_ids?.includes(q.id))))add(at+'/primary_entity_ids','主候选必须存在并关联该子问，不得借用另一问的角色');
  if(r.focus==='class'&&!ids.length||r.focus==='relationship'&&ids.length<2)add(at+'/primary_entity_ids','类神主线至少一项，关系主线须明确双方；无法定位时如实用unresolved');
 }
 return issues;
}
// Exact quotations establish provenance, not the truth of an application.
export function quantityEvidenceSchema(s){const t=s.string().min(1).max(4000);return s.array(s.object({
 use:s.enum(['base','magnitude','void']),ref:t,quote:t,application:t
}).strict()).max(12).describe('54版：source用expression须给base书证；非零量级给magnitude证据，免空减例外给void证据。ref为本任务材料ID或用户明确F_事实；quote原句及application解释适用条件。证据绑定不等于专业适用已经核实。');}
export function checkQuantityEvidence(p,q,base){
 if(!p?.consistency_policy?.analysis_route_required)return;
 const evidence=q.evidence??[],uses=new Set();
 if(!Array.isArray(evidence)||evidence.length>12)throw Error('LIUREN_QUANTITY_EVIDENCE: evidence须为有界数组');
 for(const e of evidence){
  const canonical=p.material_aliases?.find(a=>a.id===e.ref)?.canonical_id??e.ref;
  const m=p.method_materials?.find(m=>m.id===canonical),fact=p.input_review?.facts?.find(f=>f.fact_id===e.ref&&f.origin==='user_explicit');
  const source=m?.quote??fact?.source_quote;
  if(!['base','magnitude','void'].includes(e.use)||!nonempty(e.application)||!nonempty(e.quote)||!source?.includes(e.quote))
   throw Error('LIUREN_QUANTITY_EVIDENCE: 须引用本任务绑定书段或用户明确事实的连续原句，并说明适用条件');
  uses.add(e.use);
 }
 const required=[...(q.route==='source'&&!base.request.quantity_method?['base']:[]),
  ...(q.magnitude.exponent!==0?['magnitude']:[]),...(q.void.status==='exception'?['void']:[])];
 for(const use of required)if(!uses.has(use))throw Error('LIUREN_QUANTITY_EVIDENCE: 缺少'+use+'的绑定原句与应用依据；不能仅改状态或进位说明通过');
}
