// Condition and quantity primitives for the opt-in research calculator.
import {element,fiveRelation,relations} from './liuren-deterministic.mjs';
export const clip=(x,lo=0,hi=10)=>Math.max(lo,Math.min(hi,x));
export const mean=xs=>xs.reduce((a,b)=>a+b,0)/xs.length;
export const uid=(...xs)=>xs.join('|');
export const pairKey=(a,b)=>[a,b].sort().join('|');
export const TRIPLES=['申子辰','亥卯未','寅午戌','巳酉丑'];
export const MEETINGS=['寅卯辰','巳午未','申酉戌','亥子丑'];
export const hasRelation=(a,b,type)=>relations(a,b).some(r=>r.type===type);
export function combineLosses(items,cap=1){
 const causes=new Map();
 for(const item of items){
  if(!Number.isFinite(item.loss)||item.loss<0||item.loss>1)throw Error('非法约束损失');
  causes.set(item.cause,Math.max(causes.get(item.cause)??0,item.loss));
 }
 return Math.min(cap,1-[...causes.values()].reduce((a,x)=>a*(1-x),1));
}
export function cappedLossItems(items,cap){
 const causes=new Map();for(const x of items)causes.set(x.cause,Math.max(causes.get(x.cause)??0,x.loss));
 const unique=[...causes].map(([cause,loss])=>({cause,loss})),raw=combineLosses(unique);
 if(raw<=cap)return unique;
 if(cap===0)return [];
 const exponent=Math.log(1-cap)/Math.log(Math.max(1e-15,1-raw));
 return unique.map(x=>({...x,loss:1-(1-x.loss)**exponent}));
}
export function voidRetention(season,self,ground,p){
 const v=p.inherited.void;
 return Math.min(self?v.self_retention[season]:1,ground?v.self_retention[season]**v.ground_exponent:1);
}
export function referenceBase(season,refs,p){
 const sum=refs.reduce((a,r)=>a+r.weight,0);
 if(Math.abs(sum-1)>1e-10)throw Error('十二气参照权重必须合为1');
 const old=p.inherited,change=p.proposed_changes;
 const body=refs.reduce((a,r)=>a+r.weight*(r.state==='墓'?change.tomb_body_reference:old.growth[r.state]),0);
 if(!Number.isFinite(body)||body<=0)throw Error('未登记基础状态');
 const base=p.baseline*old.season[season]*body;
 const access=refs.reduce((a,r)=>a+r.weight*(r.state==='墓'?change.tomb_body_reference:old.growth[r.state])*(r.state==='墓'?change.tomb_access_retention:1),0)/body;
 return {base,access,refs:refs.map(r=>({...r,body_ratio:r.state==='墓'?change.tomb_body_reference:old.growth[r.state],access:r.state==='墓'?change.tomb_access_retention:1}))};
}
export function openingRatio(opener,before,p){
 return clip(opener/(p.proposed_changes.tomb_release_strength_ratio*before+1e-12),0,1);
}
export function groupCandidates(symbols,modes={}){
 const set=new Set(symbols),out=[];
 for(const [kind,groups] of [['三合',TRIPLES],['三会',MEETINGS]])for(const group of groups){
  const members=[...group].filter(x=>set.has(x));
  if(members.length<2)continue;
  const type=members.length===3?kind:kind==='三合'?'半合':'未成会';
  const mode=modes[group]??'unresolved';
  if(!['cooperate','bind','unresolved','irrelevant'].includes(mode))throw Error('非法合局作用模式 '+mode);
  out.push({id:group,type,members:members.map(x=>'T:'+x),coverage:members.length===3?1:.5,mode,formed:null,transformed:false});
 }
 return out;
}
export function groupStrength(group,values,p){
 const xs=group.members.map(id=>values[id]);
 const integrity=group.type==='未成会'?0:group.coverage*Math.sqrt(Math.min(...xs)*mean(xs))/10;
 return {...group,integrity,gate_multiplier:1+(p.proposed_changes.group_gain_upper_bounds[group.type]??0)*integrity};
}
export function activation(node,phase,p){
 const a=p.proposed_changes.stage_activation,index={opening:1,development:2,outcome:3}[phase];
 return node.kind==='day'?a.day_subject:node.transmissions?.includes(index)?a.current_phase_actor:
  node.transmissions?.length?a.relevant_other_phase_actor:node.lessons?.length?a.lesson_only_actor:a.other_relevant_actor;
}
export function directedEffect(type,source,target,gate,seed,p,tau=1){
 const r=p.inherited.relations;let received=0,cost=0;
 if(type==='生'){received=r.support*gate*source*tau;cost=r.source_leak*gate*source*tau;}
 else if(type==='克'){const hit=r.control*gate*source*tau/(1+target/r.resistance_reference);received=-hit;cost=r.control_cost_ratio*hit;}
 else if(type==='比和')received=r.peer*gate*Math.min(source,seed)*tau;
 else throw Error('未支持的数值关系 '+type);
 return {received,cost};
}
export function goldFireAllocation(positive,negative,fire,metal,generalSupport,generalControl){
 const budget=positive+negative;
 if(budget<=0)return {positive,negative,budget,shift:0};
 const u=fire/(fire+metal+1e-12),v=generalSupport+generalControl>0?generalSupport/(generalSupport+generalControl):.5;
 const p0=positive/budget,shift=.25*(2*u-1)+.25*(2*v-1);
 const share=p0+(1-p0)*Math.max(shift,0)+p0*Math.min(shift,0);
 return {positive:share*budget,negative:(1-share)*budget,budget,shift,share};
}
export function specialCandidates(nodes,pairs){
 const by=new Map(nodes.map(n=>[n.id,n])),out=[];
 for(const pair of pairs){
  const a=by.get(pair.a),b=by.get(pair.b);
  if(a.kind==='general'||b.kind==='general')continue;
  for(const [s,t] of [[a,b],[b,a]])for(const r of relations(s.symbol,t.symbol).slice(1)){
   if(pair.owner&&pair.owner!==t.id)continue;
   const type=r.type.replace('六冲','冲').replace('六破','破').replace('六害','害').replace('自刑候选','自刑');
   if(type==='刑'||['冲','破','害','六合','天干五合'].includes(type))out.push({id:uid(type,s.id,t.id),type,source:s.id,target:t.id,gate:Math.max(...pair.routes.map(x=>x.gate))});
  }
 }
 for(const n of nodes)if(n.kind==='branch'&&'辰午酉亥'.includes(n.symbol))out.push({id:uid('自刑',n.id),type:'自刑',source:n.id,target:n.id,gate:1});
 return [...new Map(out.map(x=>[x.id,x])).values()];
}
export function fiveRole(subject,node){return {比和:'兄弟',生:'子孙',克:'财',被生:'父母',被克:'鬼'}[fiveRelation(subject,node.symbol)];}
export function localFormations(n,by){
 if(n.kind!=='branch')return [];
 const g=by.get('D:'+n.ground),j=by.get('J:'+n.general),forms=[];
 if(fiveRelation(g.symbol,n.symbol)==='克'&&fiveRelation(n.symbol,j.symbol)==='克')forms.push('内战');
 if(fiveRelation(j.symbol,n.symbol)==='克'&&fiveRelation(n.symbol,g.symbol)==='克')forms.push('外战');
 if(fiveRelation(g.symbol,n.symbol)==='生'&&fiveRelation(j.symbol,n.symbol)==='生')forms.push('夹生');
 if(fiveRelation(g.symbol,n.symbol)==='克'&&fiveRelation(j.symbol,n.symbol)==='克')forms.push('夹克');
 return forms;
}
export function globalQi(rows,active){
 const actors=rows.filter(n=>n.kind==='branch'&&active.includes(n.id));
 return {by_element:Object.fromEntries(['木','火','土','金','水'].map(e=>{
  const xs=actors.filter(n=>element(n.symbol)===e);return [e,{actors:xs.map(x=>x.id),mean_strength:xs.length?mean(xs.map(x=>x.strength)):null}];
 })),strongest:actors.length?[...actors].sort((a,b)=>b.strength-a.strength||a.id.localeCompare(b.id))[0].id:null,
 method:'相关天盘神分五行均值；不叠加地盘、乘将与合局成为额外票数'};
}
