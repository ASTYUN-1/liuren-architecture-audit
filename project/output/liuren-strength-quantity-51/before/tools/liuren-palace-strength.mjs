// Single-palace observations and explicit, post-selection scenario calculations.
// No imports from chart presentation: shared by both tool transports and export.
import {computeStrength,STRENGTH_PROFILE} from './liuren-strength-engine.mjs';
import {fiveRelation,relations,hash} from './liuren-deterministic.mjs';
import {directedEffect,clip} from './liuren-strength-rules.mjs';

export const PALACE_MODEL='liuren-palace-strength-v1';
export const SELECTED_POLICY=Object.freeze({id:'liuren-selected-relations-v1',route_gate:.75,local_balance:'frozen',
 source_loss:'baseline-direct-greedy-and-binding',groups:false});
export const BANDS=[
 {range:'0',label:'本计算无有效力量'},
 {range:'0<E<1',label:'极弱，通常难以独立显著作用'},
 {range:'1≤E<2.5',label:'弱，仍有作用'},
 {range:'2.5≤E<5',label:'偏弱至中等，可发挥作用'},
 {range:'5≤E<7.5',label:'较强'},
 {range:'7.5≤E≤10',label:'强'}
];
export function strengthBand(e){
 if(e===null||e===undefined)return null;
 if(!Number.isFinite(e)||e<0||e>10)throw Error('旺衰分数须为0至10有限数；缺失不等于0');
 return BANDS[e===0?0:e<1?1:e<2.5?2:e<5?3:e<7.5?4:5].label;
}
const fail=m=>{throw Error('LIUREN_STRENGTH_ARGUMENTS: '+m);};
const text=(v)=>typeof v==='string'&&v.trim().length>0&&v.length<=1500;
export function palaceStrength(c,seasonProfile,{shensha}={}){
 return computeStrength(c,{seasonProfile,seasonBasis:'同盘固定月令条件表；不依预测结果选表',phase:'outcome'},{shensha});
}
export function palaceProfiles(c,{shensha}={}){
 const a=palaceStrength(c,'four-seasons',{shensha});
 return {'four-seasons':a,'quarter-earth':'辰未戌丑'.includes(c.month_branch)?palaceStrength(c,'quarter-earth',{shensha}):a};
}
// Strict even when the Codex adapter calls JS directly without the host's Zod.
export function calculateSelectedStrength(c,request,{evaluation}={}){
 const q=request??{},keys=['mode','season_profile','season_basis','actors','links','review'];
 if(Object.keys(q).some(k=>!keys.includes(k)))fail('未支持字段；不接受自定分数或系数');
 if(q.review!==undefined&&typeof q.review!=='boolean')fail('review须为布尔值');
 if(!['single_palace','selected_relations'].includes(q.mode))fail('mode须为single_palace/selected_relations');
 if(!['four-seasons','quarter-earth'].includes(q.season_profile)||!text(q.season_basis))fail('须明确season_profile及season_basis');
 if(!Array.isArray(q.actors)||!q.actors.length||q.actors.length>25)fail('须明确1至25个实际取用对象');
 const baseline=evaluation?computeStrength(c,{seasonProfile:q.season_profile,seasonBasis:q.season_basis,phase:'outcome',evaluation}):palaceStrength(c,q.season_profile),by=new Map(baseline.rows.filter(r=>r.kind!=='ground').map(r=>[r.id,r]));
 const actors=new Map();
 for(const a of q.actors){
  if(!a||Object.keys(a).some(k=>!['id','role','basis'].includes(k))||!by.has(a.id)||!text(a.role)||!text(a.basis))fail('actors须给本盘T:支/J:将/S:本日日干、role及取用basis');
  if(actors.has(a.id))fail('重复actor '+a.id);actors.set(a.id,a);
 }
 const links=q.links??[];
 if(!Array.isArray(links)||links.length>30)fail('links须为至多30项');
 if(q.mode==='single_palace'&&links.length)fail('single_palace不接收跨宫作用');
 if(q.mode==='selected_relations'&&!links.length)fail('selected_relations须提供已确认作用关系');
 const seen=new Set(),edges=[],skipped=[];
 for(const l of links){
  if(!l||Object.keys(l).some(k=>!['source','target','basis'].includes(k))||!text(l.basis)||!actors.has(l.source)||!actors.has(l.target)||l.source===l.target)fail('links双方须先取用并明确作用依据；不能自指');
  const key=[l.source,l.target].sort().join('|');
  if(seen.has(key))fail('同一对关系不得重复或反向重复计分');seen.add(key);
  const a=by.get(l.source),b=by.get(l.target),type=fiveRelation(a.symbol,b.symbol);
  if(!['生','克','比和'].includes(type))fail('source必须是施生/施克/比和方；实际关系为'+type);
  // A direct placement was already booked in at least one local view. Never
  // turn the same placement into a second reward/penalty after role selection.
  const existing=[...baseline.audit.ledger,...baseline.audit.blocked_edges].find(e=>e.source===l.source&&e.target===l.target&&e.type===type);
  if(existing){skipped.push({...l,type,reason:'直接位置关系已计入单宫或受原时序限制，不再叠加'});continue;}
  let blocked=null;
  if(type==='克'&&a.transmissions.includes(1)&&b.transmissions.includes(3)&&fiveRelation(b.symbol,c.day_stem)==='克')blocked='初不能制末鬼';
  if(blocked){skipped.push({...l,type,reason:blocked});continue;}
  edges.push({...l,type});
 }
 const p=STRENGTH_PROFILE,gates=new Map();
 // One fixed scenario gate; an actor cannot multiply its total source budget
 // by submitting numerous selected targets. Coefficients are not AI inputs.
 for(const e of edges)gates.set(e.source,(gates.get(e.source)??0)+SELECTED_POLICY.route_gate);
 for(const e of edges)e.gate=SELECTED_POLICY.route_gate/Math.max(1,gates.get(e.source)/p.inherited.relations.source_gate_budget);
 const ids=[...actors.keys()];
 function evaluate(values){
  const delta=Object.fromEntries(ids.map(id=>[id,0])),ledger=[];
  for(const e of edges){
   const a=by.get(e.source),tau=['生','克'].includes(e.type)?1-(a.goal_loss??0):1;
   const f=directedEffect(e.type,values[e.source],values[e.target],e.gate,a.seed,p,tau);
   delta[e.target]+=f.received;delta[e.source]-=f.cost;
   ledger.push({...e,tau,received:f.received,source_cost:f.cost});
  }
  const mapped=Object.fromEntries(ids.map(id=>{
   const b=by.get(id);
   // Re-use the baseline's raw local balance, not its already-attenuated E.
   // This applies void/access once and freezes unselected palaces.
   return [id,b.retention*clip(b.access*(b.base+b.delta+delta[id]))];
  }));
  return {mapped,delta,ledger};
 }
 const solutions=p.iteration.initial_values.map(start=>{
  let values=Object.fromEntries(ids.map(id=>[id,start])),residual,k=0;
  for(;k<p.iteration.max_iterations;k++){
   const v=evaluate(values);residual=Math.max(...ids.map(id=>Math.abs(v.mapped[id]-values[id])));
   if(residual<p.iteration.tolerance)break;
   values=Object.fromEntries(ids.map(id=>[id,values[id]+p.iteration.damping*(v.mapped[id]-values[id])]));
  }
  if(k===p.iteration.max_iterations)fail('补算未收敛');
  return {values,residual,iterations:k};
 });
 const spread=Math.max(...ids.map(id=>Math.max(...solutions.map(s=>s.values[id]))-Math.min(...solutions.map(s=>s.values[id]))));
 if(spread>p.iteration.agreement_tolerance)fail('补算多初值不一致');
 const detail=evaluate(solutions[1].values),values=detail.mapped,round=e=>Math.round(e*1e6)/1e6||0;
 const result={schema:'liuren-selected-strength-v1',model:PALACE_MODEL,base_model:baseline.model,profile_sha256:baseline.profile_sha256,
  selected_policy:SELECTED_POLICY,chart_sha256:hash(c),scope:q.mode,season_profile:q.season_profile,season_basis:q.season_basis,
  actors:ids.map(id=>{const b=by.get(id);return {...actors.get(id),single_palace:round(b.strength),single_palace_level:strengthBand(b.strength),
   adjusted:round(values[id]),delta:round(values[id]-b.strength),level:strengthBand(values[id])};}),
  applied_relations:detail.ledger.map(e=>({...e,received:round(e.received),source_cost:round(e.source_cost)})),already_local_or_blocked:skipped,
  interpretation:'分数描述力量；弱仍可作用，0不等于整件事绝对不成。取用与关系适用性由AI依原法判断；未选关系及合局数值未补入。',
  receipt_sha256:hash({chart:hash(c),profile:baseline.profile_sha256,selected:SELECTED_POLICY,request:q,...(evaluation?{evaluation}:{})}),
   convergence:{residual:solutions[1].residual,spread},
   coverage:{actors:ids,submitted_relations:links.length,computed_relations:edges.length,
    skipped_relations:skipped.length,unselected_palaces_updated:false,
    semantic_role_validated:false,relation_applicability_validated:false,event_verdict_supported:false,
    qualitative_conditions:'刑冲合害、神煞专项、制救通达与兑现仍依原法；合局数值暂缓'}};
 if(q.review){
  // Inspection is deliberately limited to declared actors. Facts are not
  // automatically promoted to effective links or added to the calculation.
  const candidates=[];
  for(let i=0;i<ids.length;i++)for(let j=i+1;j<ids.length;j++){
   const a=by.get(ids[i]),b=by.get(ids[j]),pair=[a.id,b.id].sort().join('|');
   const facts=relations(a.symbol,b.symbol),reverse=relations(b.symbol,a.symbol);
   const conditions=[...facts,...reverse.filter(x=>x.type==='刑')].filter((x,k,all)=>
    all.findIndex(v=>v.type===x.type&&v.from===x.from&&v.to===x.to)===k);
   const direct=baseline.audit.ledger.filter(e=>
    [e.source,e.target].sort().join('|')===pair&&(!e.owner||e.owner===a.id||e.owner===b.id));
   candidates.push({actors:[a.id,b.id],facts:conditions,
    submitted:seen.has(pair),already_local:direct.length>0,
    numeric_use:'仅事实核查；是否切题、可作用及是否提交补算由原法裁定'});
  }
  const other=q.season_profile==='four-seasons'?'quarter-earth':'four-seasons';
  const comparison=calculateSelectedStrength(c,{...q,review:false,season_profile:other,
   season_basis:'双表敏感性核查；不据分数选择采用表'}, {evaluation});
  result.review={schema:'liuren-strength-review-v1',
   state_basis:ids.map(id=>{const b=by.get(id);return {id,kind:b.kind,ground:b.ground,carrier:b.carrier??null,month:baseline.context.month,month_qi:b.season,
    references:b.refs,original_void:baseline.original_void,evaluation_void:baseline.evaluation_void,
    void_self:b.kind==='branch'?baseline.evaluation_void.includes(b.symbol):null,
    void_ground:baseline.evaluation_void.includes(b.ground),
    void_carrier:b.carrier?baseline.evaluation_void.includes(b.carrier):null,
    void_upper:b.upper?baseline.evaluation_void.includes(b.upper):null,
    void_retention:b.retention,tomb_access:b.access,base:b.base,local_net:b.delta,
    outward_restriction:b.goal_loss??0,
    direct_relations:baseline.audit.ledger.filter(e=>e.target===id||e.source===id),
    pending_action_conditions:b.pending??[]};}),
   relation_candidates:candidates,
   season_comparison:{selected_profile:q.season_profile,comparison_profile:other,
    rows:result.actors.map(a=>{const b=comparison.actors.find(v=>v.id===a.id);return {id:a.id,
     selected:a.adjusted,comparison:b.adjusted,delta:round(b.adjusted-a.adjusted)};}),
    interpretation:'同一对象与关系快照分别核算；差异不决定采用表，不平均、不计两票'},
   limitation:'仅核已声明对象；未声明对象与专项条件未穷尽。pending是计算适配提示，不是成败裁决或新待办清单'};
 }
 return result;
}
