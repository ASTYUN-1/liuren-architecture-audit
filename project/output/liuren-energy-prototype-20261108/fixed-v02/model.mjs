// Fixed research assumptions. This module does not import answers or predict hiring.
import {fiveRelation,relations,ZHI} from '../../../tools/liuren-deterministic.mjs';
export const cap=(x,lo=0,hi=10)=>Math.max(lo,Math.min(hi,x));
const pairKey=(a,b)=>[a,b].sort().join('|');
export function baseScore(n,p){
 const m=p.season[n.season];if(!Number.isFinite(m))throw Error('unregistered season');
 let r=1;
 const w=p.growth_reference_weights;
 if(n.kind==='天盘神')r=w.heaven_ground*p.growth[n.growth_at_ground]+w.heaven_yin*p.growth[n.growth_at_yin];
 if(n.kind==='天将')r=w.general_carrier*p.growth[n.growth_at_carrier]+w.general_ground*p.growth[n.growth_at_ground];
 if(n.kind==='日干')r=p.growth[n.growth_at_upper];
 if(!Number.isFinite(r))throw Error('unregistered growth');
 const vself=n.kind==='天盘神'&&n.void_self?p.void_self_retention[n.season]:1;
 const vground=n.kind==='天盘神'&&n.void_ground?p.void_self_retention[n.season]**p.void_ground_exponent:1;
 // One maximal location/self loss per node, rather than repeated labels.
 const v=Math.min(vself,vground),unvoid=cap(p.baseline*m*r);
 return {...n,base:unvoid*v,base_ledger:{baseline:p.baseline,month_multiplier:m,growth_multiplier:r,prevoid:unvoid,self_retention:vself,ground_retention:vground,adopted_retention:v,base:unvoid*v}};
}
export function buildCore(features,p){
 const heaven=features.nodes.filter(n=>n.kind==='天盘神'&&(n.lesson_slots.length||n.transmission_slots.length));
 const ids=new Set([features.nodes.find(n=>n.kind==='日干').id]);
 for(const n of heaven){ids.add(n.id);ids.add('J:'+n.general);ids.add('D:'+n.ground);}
 const nodes=features.nodes.filter(n=>ids.has(n.id)).map(n=>baseScore(n,p));
 const by=new Map(nodes.map(n=>[n.id,n])),pairs=new Map();
 function connect(a,b,gate,route){if(a===b||!by.has(a)||!by.has(b))return;const k=pairKey(a,b),old=pairs.get(k);if(!old||gate>old.gate)pairs.set(k,{a,b,gate,route});}
 const gn=nodes.find(n=>n.kind==='日干'),ts=heaven.map(n=>n.id);
 const stages=Object.fromEntries(features.activated_positions.map(x=>[x.node,x.stage]));
 for(let i=0;i<ts.length;i++)for(let j=i+1;j<ts.length;j++){
  const a=by.get(ts[i]),b=by.get(ts[j]);let gate=p.routes.same_core,route='同课传';
  if(stages[a.id]&&stages[b.id]){gate=Math.abs(stages[a.id]-stages[b.id])===1?p.routes.transmission_adjacent:p.routes.transmission_remote;route='三传关系';}
  if(a.direct_yin===b.symbol||b.direct_yin===a.symbol){gate=Math.max(gate,p.routes.yin);route='直接阴神';}
  connect(a.id,b.id,gate,route);
 }
 for(const n of heaven){
  connect(gn.id,n.id,n.symbol===gn.upper?p.routes.local:p.routes.same_core,n.symbol===gn.upper?'干上':'干与课传');
  connect('D:'+n.ground,n.id,p.routes.local,'天地直接');
  for(const j of nodes.filter(x=>x.kind==='天将'))connect(j.id,n.id,j.carried_by===n.symbol?p.routes.local:p.routes.cross_general,j.carried_by===n.symbol?'神将直接':'课传异宫神将');
 }
 // Single causal pair uses strongest route; never add lesson and transmission aliases.
 const edges=[];
 for(const pair of pairs.values())for(const [source,target]of[[pair.a,pair.b],[pair.b,pair.a]]){
  const s=by.get(source),t=by.get(target);if(s.kind==='地盘环境'&&t.kind==='地盘环境')continue;
  const type=fiveRelation(s.symbol,t.symbol);if(!['生','克','比和'].includes(type))continue;
  edges.push({id:source+'>'+target,source,target,type,raw_gate:pair.gate,route:pair.route,environment_target:t.kind==='地盘环境',fixed_source:s.kind==='地盘环境'});
 }
 for(const e of edges){const sum=edges.filter(x=>x.source===e.source).reduce((a,x)=>a+x.raw_gate,0);e.gate=e.raw_gate/Math.max(1,sum/p.relation.outgoing_gate_budget);}
 return {nodes,edges,pairs:[...pairs.values()],stages,features};
}
export function evaluateRelations(model,values,p){
 const delta=Object.fromEntries(model.nodes.map(n=>[n.id,0]));const ledger=[];
 for(const e of model.edges){
  const es=values[e.source],et=values[e.target];let gain=0,loss=0,cost=0;
  if(e.type==='生'){gain=p.relation.support*e.gate*es;cost=p.relation.leak*e.gate*es;}
  if(e.type==='克'){loss=p.relation.control*e.gate*es/(1+et/p.relation.resistance_reference);cost=p.relation.control_cost_ratio*loss;}
  if(e.type==='比和')gain=p.relation.peer*e.gate*es;
  // The earth is a boundary environment, not a second movable actor.
  if(!e.environment_target)delta[e.target]+=gain-loss;
  if(!e.fixed_source)delta[e.source]-=cost;
  ledger.push({...e,source_strength:es,target_strength:et,received:e.environment_target?0:gain-loss,source_cost:e.fixed_source?0:cost,environment_effect:e.environment_target?gain-loss:0});
 }
 return {delta,ledger};
}
export function solveCore(model,p){
 let values=Object.fromEntries(model.nodes.map(n=>[n.id,n.base])),residual=Infinity,k=0;
 const run=x=>{const r=evaluateRelations(model,x,p);return {mapped:Object.fromEntries(model.nodes.map(n=>[n.id,n.kind==='地盘环境'?n.base:cap(n.base_ledger.prevoid+r.delta[n.id])*n.base_ledger.adopted_retention])),...r};};
 for(;k<p.iteration.max_iterations;k++){
  const {mapped}=run(values);residual=Math.max(...model.nodes.map(n=>Math.abs(mapped[n.id]-values[n.id])));
  if(residual<=p.iteration.tolerance)break;
  values=Object.fromEntries(model.nodes.map(n=>[n.id,values[n.id]+p.iteration.damping*(mapped[n.id]-values[n.id])]));
 }
 if(k===p.iteration.max_iterations)throw Error('fixed profile did not converge; no strength result');
 const {ledger,delta}=run(values);
 return {values,ledger,delta,iterations:k,residual,validation:'Observed convergence for supplied graph only; no universal uniqueness proof or predictive validation.'};
}
export function actionLayer(model,solution,p,shensha){
 const by=new Map(model.nodes.map(n=>[n.id,n])),E=solution.values,rows=[];
 const heavens=model.nodes.filter(n=>n.kind==='天盘神');
 const groupSets=['申子辰','亥卯未','寅午戌','巳酉丑'];
 const meetingSets=['寅卯辰','巳午未','申酉戌','亥子丑'];
 const activeSymbols=new Set(heavens.map(n=>n.symbol));
 const groups=[...groupSets.map(s=>({type:'三合',set:s})),...meetingSets.map(s=>({type:'三会',set:s}))].map(g=>({...g,members:[...g.set].filter(s=>activeSymbols.has(s))})).filter(g=>g.members.length>=2).map(g=>({...g,adopted:g.members.length===3?g.type:g.type==='三合'?'半合':'未成会',no_transformation:true}));
 for(const n of heavens){
  const factors=[];let disruptive=0,binding=0,greedy=0;
  // Both direct physical relations and actual appearing heaven actors; no full-plate pairing.
  const peers=model.pairs.filter(x=>x.a===n.id||x.b===n.id).map(x=>({pair:x,other:by.get(x.a===n.id?x.b:x.a)})).filter(x=>x.other.kind!=='天将');
  for(const {pair,other:s}of peers){
   if(!ZHI.includes(s.symbol))continue;
   for(const r of relations(s.symbol,n.symbol)){
    if(['刑','六冲','六破','六害'].includes(r.type)){
     const value=p.availability[r.type]*pair.gate*E[s.id]/(E[s.id]+E[n.id]||1);disruptive+=value;factors.push({kind:r.type,source:s.id,gate:pair.gate,value});
    }
    if(r.type==='六合'){const value=p.availability.六合*pair.gate*E[s.id]/(E[s.id]+E[n.id]||1);binding+=value;factors.push({kind:'六合牵系',source:s.id,value});}
   }
   if((s.id==='D:'+n.ground||s.id==='T:'+n.direct_yin)&&fiveRelation(s.symbol,n.symbol)==='生'){
    const value=p.availability.direct_greedy*pair.gate*E[s.id]/(E[s.id]+E[n.id]||1);greedy+=value;factors.push({kind:'直接临生贪恋',source:s.id,value,scope:'对日主或其他外部目标的作用；对生合对象本身不沿用此折损'});
   }
  }
  if([...'辰午酉亥'].includes(n.symbol)){disruptive+=p.availability.自刑;factors.push({kind:'自刑',source:n.id,value:p.availability.自刑});}
  let coop=1;
  for(const g of groups.filter(g=>g.members.includes(n.symbol)&&g.adopted!=='未成会')){
   const partners=g.members.filter(s=>s!==n.symbol).map(s=>E['T:'+s]),ratio=partners.reduce((a,v)=>a+v,0)/(partners.reduce((a,v)=>a+v,0)+E[n.id]||1);
   const b=p.availability[g.adopted]*p.group.gate*ratio;binding+=b;
   coop=Math.max(coop,g.adopted==='半合'?p.group.half_external_cooperation:g.adopted==='三合'?p.group.triple_external_cooperation:p.group.meeting_external_cooperation);
   factors.push({kind:g.adopted,set:g.set,members:g.members,value:b,cooperation:coop,scope:'课传出现支；不自动合化，不吸收日支跨层补全'});
  }
  const sha=shensha.items.filter(x=>x.status==='resolved'&&x.places.some(q=>q.tian===n.symbol));
  const virtue=sha.filter(x=>['日德','支德'].includes(x.name));
  const virtueReduction=virtue.length?p.rescue.virtue_max*E[n.id]/p.rescue.virtue_power_reference:0;
  // This is a default local de-risking mechanism, not a universal promise of rescue.
  const q=cap(disruptive,0,p.availability.cap_disruption)*(1-virtueReduction);
  const b=cap(binding,0,p.availability.cap_binding),h=cap(greedy,0,p.availability.cap_greedy);
  const stage=model.stages[n.id],activation=stage===1?p.activation.initial:stage===2?p.activation.middle:stage===3?p.activation.last:p.activation.lesson_only;
  const general=by.get('J:'+n.general),harmful=['腾蛇','朱雀','勾陈','天空','白虎','玄武'].includes(n.general);
  const lowerControl=solution.ledger.find(e=>e.source==='D:'+n.ground&&e.target===n.id&&e.type==='克');
  const riskBeforeRescue=harmful&&lowerControl?-lowerControl.received*p.harmful_general_tendency[general.season]:0;
  const riskAfterRescue=riskBeforeRescue*(1-virtueReduction);
  rows.push({id:n.id,strength:E[n.id],activation,disruption_retention:1-q,binding_retention:1-b,greedy_retention:1-h,cooperation:coop,virtue_reduction:virtueReduction,action_index:E[n.id]*activation*(1-q)*(1-b)*(1-h)*coop,
   lower_control_harmful_general:{triggered:!!(harmful&&lowerControl),risk_before_rescue:riskBeforeRescue,risk_after_rescue:riskAfterRescue,scope:'下克乘凶将条件的研究风险指数；非灾害概率，不再扣本体分，也不独立裁败'},
   action_scope:'日主或本问外部目标；非节点自身生存状态、非录用概率',factors,shensha:sha.map(x=>({id:x.id,name:x.name,energy_adjustment:0,reason:['日德','支德'].includes(x.name)?'德的护解作用进入局部不利通路，不加本体力量':x.name==='日禄'?'取用身份，不另制造五行能量':'保留身份，尚未编成本问专项作用；不等于无影响'}))});
 }
 return {rows,groups,unresolved:['课体名称对应的专项事件机制尚未全部编译，不据名称给固定加减分','本轮未完成全部神煞到本问事件的专项映射；表列零能量调整不代表零事件影响','六合兼刑害、冲墓开闭和墓库取用需按已确认来源另给适配器；不能据通用分数宣称这些机制已经解决','年命、日支对类神的跨宫作用及四建跨层组合尚未全部进入本轮作用指数，不据此判整盘成败','动作层参数是通用研究默认值；原文明示的特殊生刑、生克合条件优先，未编译时阻止给完整结论']};
}
