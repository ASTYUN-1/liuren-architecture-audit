// Coupled local five-element model. No event verdict or unseen global pair links.
import {fiveRelation,element,seasonal} from './liuren-deterministic.mjs';
const cap=(v,p)=>Math.max(p.range[0],Math.min(p.range[1],v));
const key=(a,b)=>[a,b].sort().join('|');
export function relationEffect(type,source,target,gate,p){
 if(!['生','克','比和'].includes(type))throw Error('Unregistered directed relation');
 let received=0,cost=0;
 if(type==='生'){received=p.support*gate*source;cost=p.leak*gate*source;}
 if(type==='克'){const hit=p.control*gate*source/(1+target/p.resistance_reference);received=-hit;cost=p.control_cost_ratio*hit;}
 if(type==='比和')received=p.peer*gate*source;
 return {received,cost};
}
function branchBase(n,profile,p){
 const season=n.seasonal.profiles[profile],w=p.growth_reference_weights;
 const prevoid=cap(p.baseline*p.season[season]*(w.heaven_ground*p.growth[n.growth.ground]+w.heaven_yin*p.growth[n.growth.yin]),p);
 const retention=Math.min(n.void_self?p.void_self_retention[season]:1,n.void_ground?p.void_self_retention[season]**p.void_ground_exponent:1);
 return {prevoid,retention,base:prevoid*retention};
}
export function buildLocalGraph(d,month,profile,p,r){
 if(!['four-seasons','quarter-earth'].includes(profile))throw Error('Seasonal profile required');
 const nodes=[];
 for(const n of d.nodes){
  nodes.push({id:'T:'+n.symbol,symbol:n.symbol,kind:'branch',...branchBase(n,profile,p)});
  const season=n.general_seasonal.profiles[profile],w=p.growth_reference_weights;
  const base=cap(p.baseline*p.season[season]*(w.general_carrier*p.growth[n.general_growth.branch]+w.general_ground*p.growth[n.general_growth.ground]),p);
  nodes.push({id:'J:'+n.general,symbol:n.general,kind:'general',base,prevoid:base,retention:1});
  // Ground is a fixed environment, not a second heaven actor or self-sitting god.
  const groundBase=p.baseline*p.season[seasonal(n.ground,month,profile)];
  nodes.push({id:'D:'+n.ground,symbol:n.ground,kind:'ground',base:groundBase,prevoid:groundBase,retention:1});
 }
 const s=d.day,stemBase=cap(p.baseline*p.season[s.seasonal.profiles[profile]]*p.growth[s.growth.upper],p);
 nodes.push({id:'S:'+s.symbol,symbol:s.symbol,kind:'day',base:stemBase,prevoid:stemBase,retention:1});
 const by=new Map(nodes.map(n=>[n.id,n])),pairs=new Map();
 const connect=(a,b,gate,route)=>{
  if(a===b)return;
  if(!by.has(a)||!by.has(b))throw Error('Missing local reference '+a+' / '+b);
  const k=key(a,b),prior=pairs.get(k);
  if(!prior||gate>prior.gate)pairs.set(k,{a,b,gate,routes:[route]});
  else if(gate===prior.gate&&!prior.routes.includes(route))prior.routes.push(route);
 };
 for(const n of d.nodes){
  connect('T:'+n.symbol,'D:'+n.ground,r.routes.ground,'天盘—地盘');
  connect('T:'+n.symbol,'T:'+n.direct_yin,r.routes.yin,'天盘—直接阴神');
  connect('J:'+n.general,'T:'+n.symbol,r.routes.carrier,'天将—乘支');
  connect('J:'+n.general,'D:'+n.ground,r.routes.general_ground,'天将—地盘');
 }
 connect('S:'+s.symbol,'T:'+s.upper,r.routes.day_upper,'日干—干上神');
 connect('S:'+s.symbol,'T:'+s.direct_yin,r.routes.day_yin,'日干—干阴神');
 const edges=[];
 for(const pair of pairs.values())for(const [source,target]of[[pair.a,pair.b],[pair.b,pair.a]]){
  const type=fiveRelation(by.get(source).symbol,by.get(target).symbol);
  if(['生','克','比和'].includes(type))edges.push({id:source+'>'+target,source,target,type,raw_gate:pair.gate,routes:pair.routes});
 }
 for(const e of edges){
  const total=edges.filter(v=>v.source===e.source).reduce((a,v)=>a+v.raw_gate,0);
  e.gate=e.raw_gate/Math.max(1,total/r.relation.outgoing_gate_budget);
 }
 return {profile,nodes,edges,pairs:[...pairs.values()]};
}
export function evaluateLocal(graph,values,p,r){
 const by=new Map(graph.nodes.map(n=>[n.id,n])),delta=Object.fromEntries(graph.nodes.map(n=>[n.id,0])),ledger=[];
 for(const e of graph.edges){
  const {received,cost}=relationEffect(e.type,values[e.source],values[e.target],e.gate,r.relation);
  const sourceFixed=by.get(e.source).kind==='ground',targetFixed=by.get(e.target).kind==='ground';
  if(!targetFixed)delta[e.target]+=received;
  if(!sourceFixed)delta[e.source]-=cost;
  ledger.push({...e,source_strength:values[e.source],target_strength:values[e.target],
   received:targetFixed?0:received,source_cost:sourceFixed?0:cost,environment_effect:targetFixed?received:0});
 }
 const mapped=Object.fromEntries(graph.nodes.map(n=>[n.id,n.kind==='ground'?n.base:cap(n.prevoid+delta[n.id],p)*n.retention]));
 return {delta,ledger,mapped};
}
export function solveLocal(graph,p,r){
 let values=Object.fromEntries(graph.nodes.map(n=>[n.id,n.base])),residual=Infinity,k=0;
 for(;k<r.iteration.max_iterations;k++){
  const next=evaluateLocal(graph,values,p,r);residual=Math.max(...graph.nodes.map(n=>Math.abs(next.mapped[n.id]-values[n.id])));
  if(residual<=r.iteration.tolerance)break;
  values=Object.fromEntries(graph.nodes.map(n=>[n.id,values[n.id]+r.iteration.damping*(next.mapped[n.id]-values[n.id])]));
 }
 if(k===r.iteration.max_iterations)throw Error('局部生克算法未收敛，不输出作用后指数');
 const result=evaluateLocal(graph,values,p,r);
 return {profile:graph.profile,values,iterations:k,residual,ledger:result.ledger,delta:result.delta,
  rows:graph.nodes.map(n=>({...n,element:element(n.symbol),value:values[n.id],change:values[n.id]-n.base,
   cap_adjustment:cap(n.prevoid+result.delta[n.id],p)-(n.prevoid+result.delta[n.id])}))};
}
export function localStrength(d,month,p,r){
 const outputs={};
 for(const profile of ['four-seasons','quarter-earth']){
  const graph=buildLocalGraph(d,month,profile,p,r);outputs[profile]={graph,solution:solveLocal(graph,p,r)};
 }
 return {model:r.id,outputs};
}
