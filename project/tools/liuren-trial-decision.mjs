// Only the small OpenCode trial uses this semantic view. It never changes E.
import {kin} from './liuren-deterministic.mjs';
import {strengthBand} from './liuren-palace-strength.mjs';
export const TRIAL_DECISION_POLICY=Object.freeze({
 id:'liuren-trial-decision-61',scope:'本机分类取用短答；局部旺衰解释，不自动裁整件事成败',
 selection_policy:{id:'class-selection-source-62',
  question:'保留原问对象、阶段及验收目标；经营概况不能自行改成收款，关系发展不能缩成一方旺衰。',
  roles:'对象题首取主类；关系题以必要双方及其关系为主线，不为一个主类的格式删掉另一方。',
  evidence:'说明采用的书中或专项取法、其条件与题面对应；现代映射标明推定。材质、身份及年命未知不补造，不因旺衰或答案换类。',
  coordinates:'天盘类神写天盘X临地盘Y乘将Z；年命写地盘本命或行年X上见Y乘Z，不混成同名天盘支。',
  review:'两路核对属于初答锁定后的测试复盘：分别看原案答者如何取及书中怎样教；待测会话不读取原案答案。'},
 order:['按原问分类取用并固定成功标准','核初传身份、五行旺衰、坐处、乘将和切题专项条件','确定各对象职责及这条关系对本题的实际含义','统一喜旺恶衰解释局部状态','综合主类与初传：区分事情是否发生、对本人利弊及质量待遇'],
 seasonal:'仅五行月令旺相休囚死，内部参数quarter-earth：寅卯木、巳午火、申酉金、亥子水、辰未戌丑土当令；不使用four-seasons及双表比较。不是季末十八日自动算法。',
 initial:'初传必须核查但不自动替换主类：先解释其在本问是发动、压力、门槛、款项还是结果线索，再看状态与作用。衰弱不等于无力发动；旬空不自动等于事件不发生；发用旺也不保证成功。',
 special_conditions:'闭口、空墓、月破及神将专项象义不全部包含在旺衰分数；须按本问职责另核，不能因分数较高便降为消息迟。宫位、乘将及其各自十二气不得混写。',
 event_dimensions:'事件发生、本人吉凶、岗位待遇或物品质量分开。喜旺恶衰保留；不能把待遇差直接判不录用，也不能把不利的调动判成不调动。',
 strong_ghost:'相关官鬼、凶神较旺或强旺，默认其凶害减轻/不以侵害为主；不是更强攻击，也不自动保证整件事成功。',
 weak_ghost:'相关官鬼、凶神越衰凶态越显；极低或零仍不能解释成无害、不能作用；不设低分失用开关。',
 control:'五行克只登记关系；先辨取财、约束、制救或侵害。克的负增量不能自行证明现实侵害。',
 no_laundering:'禁止旺鬼→扣低日干→改称身弱→判凶。不能把同一次数值扣减改名后重作独立反证。日干原有衰弱仍可独立考虑。',
 rescue:'先成立本题需要解除的实际不利，才谈制救；旺鬼默认凶害轻时，不以未能压低旺鬼为失败依据。',
 support:'对已选主类的生扶与泄耗去向同样核查；制鬼不是唯一正向路径。不得只挑克制关系后声称完成综合。',
 boundaries:'本层无成败总分、固定投票、权重或成功概率；低旺衰不等于不能取财/不能兑现；具体作用通路由模型按事件及来源说明。'
});
export function trialComputeRequest(request){
 const q=structuredClone(request);
 if(q.action==='strength'&&q.strength&&q.strength.season_profile!=='quarter-earth')
  throw Error('LIUREN_TRIAL_SEASON: 当前只用五行月令旺衰；保留actors/links，改season_profile为quarter-earth，不使用four-seasons。');
 if(q.action==='lookup'&&q.lookup){
  if(q.lookup.profile!==undefined&&q.lookup.profile!=='quarter-earth')throw Error('LIUREN_TRIAL_SEASON: lookup.profile只允许quarter-earth（五行月令旺衰）。');
  q.lookup.profile='quarter-earth';
 }
 return q;
}
export function trialComputeHelp(parameters){
 const q=structuredClone(parameters);
 function walk(v){
  if(!v||typeof v!=='object')return;
  if(Array.isArray(v.enum)&&v.enum.includes('four-seasons')&&v.enum.includes('quarter-earth'))v.enum=['quarter-earth'];
  if(typeof v.description==='string')v.description=v.description.replaceAll('季土双表差异','五行月令状态依据').replaceAll('季月不按结果换表','仅用五行月令quarter-earth');
  for(const x of Object.values(v))walk(x);
 }
 walk(q);return q;
}
export function trialLookupBasis(value){
 // canonicalEntity's legacy display string embeds both profiles; replace it.
 const out=structuredClone(value);
 if(out.five_qi!==undefined)out.five_qi=out.subject+':'+JSON.stringify(out.seasonal);
 return out;
}
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
 const t=f.transmissions?.[0],row=t&&(f.heaven_earth??[]).find(r=>r.tian===t.diZhi);
 const initial=t?{branch:t.diZhi,liuqin:t.liuqin,ground:row?.di??t.earth_position,general:t.tianjiang,
  status:t.status??null,branch_state:row?.state??null,general_state:row?.general_state??null,
  shensha:row?.shensha??[],role_in_question:null,event_effect:null,
  interpretation_required:TRIAL_DECISION_POLICY.initial,
  special_conditions:TRIAL_DECISION_POLICY.special_conditions}:null;
 const chartBasis={policy:TRIAL_DECISION_POLICY,initial_transmission:initial,day_ghost_observations:observations,
  scope:'仅列盘内日鬼状态，不自动选为本题类神，不因未进strength actors就免除其凶态，也不自动为整件事计凶票。'};
 return {trial_judgment_policy:TRIAL_DECISION_POLICY,trial_chart_basis:chartBasis,...result,facts:{...f,trial_judgment_policy:TRIAL_DECISION_POLICY,trial_chart_basis:chartBasis}};
}
