// Research extension: include a named subject outside lessons/transmissions.
// It retains its actual positions; selection does not invent a lesson or stage.
import {fiveRelation} from '../../tools/liuren-deterministic.mjs';
import {baseScore,buildCore} from '../liuren-energy-prototype-20261108/fixed-v02/model.mjs';

export function buildSelectedCore(features,p,subjects=[]){
 if(!subjects.length)return buildCore(features,p);
 const selected=new Set(subjects);
 const heaven=features.nodes.filter(n=>n.kind==='天盘神'&&(n.lesson_slots.length||n.transmission_slots.length||selected.has(n.symbol)));
 for(const symbol of selected)if(!heaven.some(n=>n.symbol===symbol))throw Error('Unknown selected subject: '+symbol);
 const ids=new Set([features.nodes.find(n=>n.kind==='日干').id]);
 for(const n of heaven){ids.add(n.id);ids.add('J:'+n.general);ids.add('D:'+n.ground);}
 const nodes=features.nodes.filter(n=>ids.has(n.id)).map(n=>baseScore(n,p));
 const by=new Map(nodes.map(n=>[n.id,n])),pairs=new Map();
 function connect(a,b,gate,route){
  if(a===b||!by.has(a)||!by.has(b))return;
  const k=[a,b].sort().join('|'),old=pairs.get(k);
  if(!old||gate>old.gate)pairs.set(k,{a,b,gate,route});
 }
 const gn=nodes.find(n=>n.kind==='日干'),ts=heaven.map(n=>n.id);
 const stages=Object.fromEntries(features.activated_positions.map(x=>[x.node,x.stage]));
 for(let i=0;i<ts.length;i++)for(let j=i+1;j<ts.length;j++){
  const a=by.get(ts[i]),b=by.get(ts[j]);let gate=p.routes.same_core,route='同课传或选定类神';
  if(stages[a.id]&&stages[b.id]){gate=Math.abs(stages[a.id]-stages[b.id])===1?p.routes.transmission_adjacent:p.routes.transmission_remote;route='三传关系';}
  if(a.direct_yin===b.symbol||b.direct_yin===a.symbol){gate=Math.max(gate,p.routes.yin);route='直接阴神';}
  connect(a.id,b.id,gate,route);
 }
 for(const n of heaven){
  connect(gn.id,n.id,n.symbol===gn.upper?p.routes.local:p.routes.same_core,n.symbol===gn.upper?'干上':'干与课传或选定类神');
  connect('D:'+n.ground,n.id,p.routes.local,'天地直接');
  for(const j of nodes.filter(x=>x.kind==='天将'))connect(j.id,n.id,j.carried_by===n.symbol?p.routes.local:p.routes.cross_general,j.carried_by===n.symbol?'神将直接':'异宫神将');
 }
 const edges=[];
 for(const pair of pairs.values())for(const [source,target]of[[pair.a,pair.b],[pair.b,pair.a]]){
  const s=by.get(source),t=by.get(target);
  if(s.kind==='地盘环境'&&t.kind==='地盘环境')continue;
  const type=fiveRelation(s.symbol,t.symbol);if(!['生','克','比和'].includes(type))continue;
  edges.push({id:source+'>'+target,source,target,type,raw_gate:pair.gate,route:pair.route,environment_target:t.kind==='地盘环境',fixed_source:s.kind==='地盘环境'});
 }
 for(const e of edges){const sum=edges.filter(x=>x.source===e.source).reduce((a,x)=>a+x.raw_gate,0);e.gate=e.raw_gate/Math.max(1,sum/p.relation.outgoing_gate_budget);}
 return {nodes,edges,pairs:[...pairs.values()],stages,features,selected_subjects:[...selected],scope:'original core plus explicitly selected subjects and their local general/ground; numerical research only'};
}
