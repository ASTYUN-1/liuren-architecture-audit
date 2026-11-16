// Deterministic state presentation. No scores, efficacy, outcome or energy model.
export const BASIC_STATE_VERSION='liuren-basic-states-v1';
const table=(columns,rows)=>({columns,rows});
function month(profiles){
 const values=Object.values(profiles),agreed=values.every(v=>v===values[0]);
 return {profiles,adopted:agreed?values[0]:null,
  status:agreed?'profiles_agree':'seasonal_convention_required',
  de_ling:agreed?values[0]==='旺':null};
}
function coexistence(state,forward,reverse){
 const flags=[];
 if(state==='长生'&&forward==='生')flags.push('长生兼泄');
 if(state==='长生'&&reverse==='克')flags.push('长生兼受克');
 if(state==='绝'&&reverse==='生')flags.push('临绝并见受生');
 if(state==='墓'&&reverse==='生')flags.push('临墓并见受生，不等于已开墓');
 return flags;
}
export function basicStateView(d){
 const branchRows=[],generalRows=[],localRows=[],jointRows=[];
 const qi=n=>month(n.seasonal.profiles);
 for(const n of d.nodes){
  const r=n.local_relations,v=d.xun.void_branches;
  branchRows.push([n.id,n.symbol,n.element,n.ground,n.direct_yin,n.general,qi(n),
   n.growth.ground,n.growth.yin,n.void_self,n.void_ground,v.includes(n.direct_yin),
   n.lesson_slots,n.transmission_slots]);
  generalRows.push([n.id,n.general,n.general_element,n.symbol,n.ground,month(n.general_seasonal.profiles),
   n.general_growth.branch,n.general_growth.ground,
   {carrier_void:n.void_self,ground_void:n.void_ground,self_xun_void:null,
    rule:'天将不是旬空地支，乘支空/坐处空分别登记，不自动继承为将自身空'}]);
  const b2d=r.branch_to_ground[0].value,d2b=r.ground_to_branch[0].value;
  const j2b=r.general_to_branch[0].value,b2j=r.branch_to_general[0].value;
  localRows.push([n.id,r.ground_to_branch,r.branch_to_ground,r.general_to_branch,r.branch_to_general,
   r.ground_to_general,r.general_to_ground,r.yin_to_branch,r.branch_to_yin,
   {内战:d2b==='克'&&b2j==='克',外战:j2b==='克'&&b2d==='克',
    夹克:d2b==='克'&&j2b==='克',夹生:d2b==='生'&&j2b==='生'}]);
  for(const [object,ref,state,fwd,rev] of [
   [n.symbol,'地盘'+n.ground,n.growth.ground,b2d,d2b],
   [n.symbol,'阴神'+n.direct_yin,n.growth.yin,r.branch_to_yin[0].value,r.yin_to_branch[0].value],
   [n.general,'乘神'+n.symbol,n.general_growth.branch,j2b,b2j],
   [n.general,'地盘'+n.ground,n.general_growth.ground,r.general_to_ground[0].value,r.ground_to_general[0].value],
  ]){const flags=coexistence(state,fwd,rev);if(flags.length)jointRows.push([n.id,object,ref,state,fwd,rev,flags]);}
 }
 return {schema:BASIC_STATE_VERSION,chart_sha256:d.chart_sha256,
  scope:'全12宫天盘神、天将和日干；固定坐标、采用表内状态及原始关系；未求综合旺衰',
  policies:{growth:d.policies.growth,seasonal:'旺相休囚死按具名表查得。季土取法不同则adopted/de_ling=null；不可把某表自动当作统一采用值。',
   seasonal_profiles:{'four-seasons':'春木夏火秋金冬水，含各季末月','quarter-earth':'辰未戌丑全月土旺表；不是季末十八日自动算法'},
   general_void:'天将无独立旬空支身份；空的是乘支/地盘分别列，不自动转成天将失用',
   relations:'方向字段是原始关系，内外战等只标构成；不决定主作用、成局、救成或吉凶',
   coexistence:'长生兼泄、临绝受生等只提示同处条件并见，不能当作额外吉凶证据或能量修复认证'},
  branches:table(['node_ref','branch','element','ground','direct_yin','general','month_qi','growth_ground','growth_yin','self_void','sitting_void','yin_void','lesson_slots','transmission_slots'],branchRows),
  generals:table(['node_ref','general','element','carrier','ground','month_qi','growth_carrier','growth_ground','void_context'],generalRows),
  local:table(['node_ref','ground_to_branch','branch_to_ground','general_to_branch','branch_to_general','ground_to_general','general_to_ground','yin_to_branch','branch_to_yin','formation_flags'],localRows),
  coexistence:table(['node_ref','subject','reference','growth','subject_to_reference','reference_to_subject','flags'],jointRows),
  day:{...d.day,upper_void:d.xun.void_branches.includes(d.day.upper),
   home_void:d.xun.void_branches.includes(d.day.home),yin_void:d.xun.void_branches.includes(d.day.direct_yin),
   month_qi:qi(d.day),note:'日干采用天干十二长生，寄宫不是日干五行替身'},
  limits:['无分数、加权、空亡衰减或成功概率；不调用研究能量模型。','基础状态不是综合旺衰或有效作用；不得据得令、临绝、旬空或构成标记独断成败。','12宫全列不是12宫全同等参与；取用、通路、救制及时间变化仍由原工作流判断。']};
}
