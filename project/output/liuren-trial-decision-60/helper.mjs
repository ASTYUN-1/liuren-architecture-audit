// Only the small OpenCode trial uses this semantic view. It never changes E.
import {kin} from './liuren-deterministic.mjs';
import {strengthBand} from './liuren-palace-strength.mjs';
export const TRIAL_DECISION_POLICY=Object.freeze({
 id:'liuren-trial-decision-59',scope:'本机分类取用短答；局部旺衰解释，不自动裁整件事成败',
 order:['按原问分类取用并固定成功标准','确定各对象职责及这条关系对本题的实际含义','统一喜旺恶衰解释局部状态','区分数值作用与实际助阻，再综合主类及最关键条件'],
 strong_ghost:'相关官鬼、凶神较旺或强旺，默认其凶害减轻/不以侵害为主；不是更强攻击，也不自动保证整件事成功。',
 weak_ghost:'相关官鬼、凶神越衰凶态越显；极低或零仍不能解释成无害、不能作用；不设低分失用开关。',
 control:'五行克只登记关系；先辨取财、约束、制救或侵害。克的负增量不能自行证明现实侵害。',
 no_laundering:'禁止旺鬼→扣低日干→改称身弱→判凶。不能把同一次数值扣减改名后重作独立反证。日干原有衰弱仍可独立考虑。',
 rescue:'先成立本题需要解除的实际不利，才谈制救；旺鬼默认凶害轻时，不以未能压低旺鬼为失败依据。',
 support:'对已选主类的生扶与泄耗去向同样核查；制鬼不是唯一正向路径。不得只挑克制关系后声称完成综合。',
 boundaries:'本层无成败总分、固定投票、权重或成功概率；低旺衰不等于不能取财/不能兑现；具体作用通路由模型按事件及来源说明。'
});
export function localStrengthMeaning(score){
 if(score===null||score===undefined)return {level:null,tendency:'缺计算，不能当作零或无害',usable:null};
 const level=strengthBand(score);
 return {level,tendency:score>=5?'旺衰一项偏有利':score<2.5?'旺衰一项偏不利':'偏弱至中等，较强旺一侧不利；不足以单定失败',usable:null};
}
const isGhost=(day,id)=>!id.startsWith('S:')&&kin(day,id.slice(2))==='官鬼';
export function trialStrengthBasis(value,day){
 const actors=value.actors.map(a=>({id:a.id,role:a.role,day_ghost:isGhost(day,a.id),
  original:{score:a.single_palace,...localStrengthMeaning(a.single_palace)},
  scenario:{score:a.adjusted,...localStrengthMeaning(a.adjusted)},
  ...(isGhost(day,a.id)?{harm_interpretation:a.adjusted>=5?'旺鬼凶害减轻；不要求先制弱才算有救':'衰鬼不利仍须保留；不得以弱或零免除侵害'}:{})}));
 const strongGhostEdges=value.applied_relations.filter(e=>e.type==='克'&&isGhost(day,e.source)&&value.actors.find(a=>a.id===e.source).adjusted>=5);
 return {policy:TRIAL_DECISION_POLICY,actors,
  rejected_inference_chains:strongGhostEdges.map(e=>({source:e.source,target:e.target,numeric_received:e.received,
   rejected:'以旺鬼的克扣分作为实际侵害，再用受者补算后变弱判凶',
   retained:'原数值和克关系保留；受者原有状态、本题独立不利及作用条件另论'})),
  relation_meaning_required:value.applied_relations.map(e=>({source:e.source,target:e.target,type:e.type,
   event_effect:e.type==='克'?'未由五行关系决定；需按本题辨取财/约束/制救/侵害':'需核生扶去向与本题职责；泄耗不自动为凶'})),
  primary_support_candidates:(value.review?.relation_candidates??[]).filter(p=>!p.submitted&&p.facts.some(f=>f.type==='five_elements'&&['生','被生'].includes(f.value))).map(p=>({actors:p.actors,facts:p.facts,scope:'仅候选，按取用职责核相关性；不自动加入计算'})),
  final_verdict:null,model_must_decide:'主类与关键条件综合取舍；不能只按分数排序或以制鬼力度裁成败'};
}
export function withTrialStrengthBasis(value,day){return {trial_judgment_basis:trialStrengthBasis(value,day),...value};}
export function withTrialChartBasis(result){
 if(!result.ok||!result.facts)return result;
 const f=result.facts;
 const meaning=value=>typeof value==='object'&&value!==null?Object.fromEntries(Object.entries(value).map(([k,v])=>[k,localStrengthMeaning(v)])):localStrengthMeaning(value);
 const observations=(f.heaven_earth??[]).filter(r=>r.liuqin==='官鬼').map(r=>({id:r.id,di:r.di,tian:r.tian,tianjiang:r.tianjiang,
  score:r.state?.strength_index,meaning:meaning(r.state?.strength_index),
  restriction:'若本题确实兼看此鬼，按喜旺恶衰解释；弱/零不能改称无强压或无害。若不切题则不纳入，不能虚构它的有利状态。'}));
 const chartBasis={policy:TRIAL_DECISION_POLICY,day_ghost_observations:observations,
  scope:'仅列盘内日鬼状态，不自动选为本题类神，不因未进strength actors就免除其凶态，也不自动为整件事计凶票。'};
 return {trial_judgment_policy:TRIAL_DECISION_POLICY,trial_chart_basis:chartBasis,...result,facts:{...f,trial_judgment_policy:TRIAL_DECISION_POLICY,trial_chart_basis:chartBasis}};
}
