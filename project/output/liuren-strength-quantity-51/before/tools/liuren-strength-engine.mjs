import fs from 'node:fs/promises';
import {buildFacts,element,fiveRelation,seasonal,relations,xunFacts,ZHI,GAN,hash} from './liuren-deterministic.mjs';
import {clip,mean,uid,pairKey,hasRelation,combineLosses,voidRetention,referenceBase,openingRatio,
 groupCandidates,groupStrength,activation,directedEffect,goldFireAllocation,specialCandidates,fiveRole,localFormations,globalQi,cappedLossItems} from './liuren-strength-rules.mjs';

export const STRENGTH_PROFILE=JSON.parse(await fs.readFile(new URL('./liuren-strength-profile.json',import.meta.url),'utf8'));
const phaseNames=['opening','development','outcome'];
const round=x=>Math.round(x*10)/10;
const error=message=>{throw Error('LIUREN_STRENGTH: '+message);};
function normalizeContext(c,ctx){
 const o=structuredClone(ctx),month=o.evaluation?.month_branch??c.month_branch;
 if(!ZHI.includes(month))error('评价月支无效');
 if(o.evaluation&&!o.evaluation.basis)error('时间条件更新必须给出依据，不重新排原盘');
 const season=o.seasonProfile??(!'辰未戌丑'.includes(month)?'four-seasons':null);
 if(!['four-seasons','quarter-earth'].includes(season))error('季月须显式选择seasonProfile及采用依据');
 if(!o.seasonBasis)error('须给出seasonBasis，不能按结果自动择表');
 const phase=o.phase??'outcome';if(!phaseNames.includes(phase))error('phase须为opening/development/outcome');
 if(o.selectedSubjects?.some(s=>!ZHI.includes(s)))error('selectedSubjects只接受支，其他九干不默认接入');
 if(o.evaluation?.day_pillar)xunFacts(o.evaluation.day_pillar);
 const goal=o.goal??{id:'day',target:'S:'+c.day_stem,mode:'external'};
 if(!['external','cooperate','movement'].includes(goal.mode))error('goal.mode无效');
 return {...o,month,seasonProfile:season,phase,goal,effectRules:o.effectRules??[],shenshaRules:o.shenshaRules??[],groupModes:o.groupModes??{},includeGroupEffects:false};
}
function graphFrom(c,d,o,p){
 const old=p.inherited,nodes=[];
 const voidBranches=o.evaluation?.day_pillar?xunFacts(o.evaluation.day_pillar).void_branches:d.xun.void_branches;
 function addNode(v,refs){
  const season=seasonal(v.symbol,o.month,o.seasonProfile),basis=referenceBase(season,refs,p);
  const retention=v.kind==='branch'?voidRetention(season,voidBranches.includes(v.symbol),voidBranches.includes(v.ground),p):1;
  nodes.push({...v,season,...basis,retention,seed:retention*clip(basis.base*basis.access)});
 }
 for(const n of d.nodes){
  addNode({id:'T:'+n.symbol,symbol:n.symbol,kind:'branch',ground:n.ground,general:n.general,direct_yin:n.direct_yin,
   lessons:n.lesson_slots,transmissions:n.transmission_slots,void_self:d.xun.void_branches.includes(n.symbol),void_ground:d.xun.void_branches.includes(n.ground)},
   [{place:n.ground,state:n.growth.ground,weight:old.growth_weights.branch.ground},{place:n.direct_yin,state:n.growth.yin,weight:old.growth_weights.branch.direct_yin}]);
  addNode({id:'J:'+n.general,symbol:n.general,kind:'general',carrier:n.symbol,ground:n.ground,lessons:n.lesson_slots,transmissions:n.transmission_slots},
   [{place:n.symbol,state:n.general_growth.branch,weight:old.growth_weights.general.carrier},{place:n.ground,state:n.general_growth.ground,weight:old.growth_weights.general.ground}]);
  const season=seasonal(n.ground,o.month,o.seasonProfile),base=p.baseline*old.season[season];
  nodes.push({id:'D:'+n.ground,symbol:n.ground,kind:'ground',season,base,access:1,retention:1,seed:base,refs:[]});
 }
 addNode({id:'S:'+d.day.symbol,symbol:d.day.symbol,kind:'day',ground:d.day.home,upper:d.day.upper,direct_yin:d.day.direct_yin,lessons:[],transmissions:[]},
  [{place:d.day.upper,state:d.day.growth.upper,weight:1}]);
 const by=new Map(nodes.map(n=>[n.id,n]));
 if(!by.has(o.goal.target))error('goal.target不是本盘节点');
 const active=[...new Set([c.day_branch,...Object.values(d.anchors),...d.structure.transmissions,...o.selectedSubjects??[],
  ...(c.year_life_verified?(c.participants??[]).flatMap(x=>ZHI.includes(x.life_branch)?[x.life_branch]:[]):[])])].map(s=>'T:'+s);
 const pairs=new Map();
 function connect(a,b,kind,gate,owner=null){
  if(a===b)return;if(!by.has(a)||!by.has(b))error('缺少通路对象 '+a+'/'+b);
  const key=pairKey(a,b)+'|'+(owner??'mutual'),v=pairs.get(key)??{a,b,owner,routes:[]};
  if(!v.routes.some(r=>r.kind===kind))v.routes.push({kind,gate});pairs.set(key,v);
 }
 for(const n of d.nodes){
  connect('T:'+n.symbol,'D:'+n.ground,'ground',old.routes.direct_ground);
  connect('T:'+n.symbol,'T:'+n.direct_yin,'yin',old.routes.direct_yin,'T:'+n.symbol);
  connect('J:'+n.general,'T:'+n.symbol,'carrier',old.routes.direct_general);
 }
 connect('S:'+d.day.symbol,'T:'+d.day.upper,'day_upper',old.routes.day_upper,'S:'+d.day.symbol);
 connect('S:'+d.day.symbol,'T:'+d.day.direct_yin,'yin',old.routes.direct_yin,'S:'+d.day.symbol);
 // Four-building roles use actual participating coordinates; seasonal qi never requires this gate.
 const four=c.pillars.map((pillar,i)=>({role:['岁','月','日','时'][i],branch:pillar.at(-1),upper:d.nodes.find(n=>n.ground===pillar.at(-1))?.symbol}));
 for(const s of o.fourBuildingLinks??[]){
  const f=four.find(x=>x.role===s.role);if(!f||!s.basis||!by.has(s.target))error('四建关系须给实际角色、目标及依据');
  const a='T:'+f.upper;
  if(![...pairs.values()].some(v=>(v.a===a&&v.b===s.target||v.b===a&&v.a===s.target)&&(!v.owner||v.owner===s.target)))error('四建身份不能创建无直接加临的生克边');
 }
 const groupSymbols=d.nodes.filter(n=>n.lesson_slots.length||n.transmission_slots.length).map(n=>n.symbol);
 for(const member of o.additionalGroupMembers??[]){
  if(!member.basis||!ZHI.includes(member.symbol)||member.layer!=='heaven')error('补局成员须明确天盘支身份及专项依据，不能混入同名地盘');
  if(!active.includes('T:'+member.symbol))error('补局成员须先属于所论切题对象');
  groupSymbols.push(member.symbol);
 }
 const groups=groupCandidates(groupSymbols,{}).map(g=>({...g,mode:'deferred',numeric_enabled:false}));
 const edges=[];
 for(const pair of pairs.values())for(const [source,target]of[[pair.a,pair.b],[pair.b,pair.a]]){
  const a=by.get(source),b=by.get(target),type=fiveRelation(a.symbol,b.symbol);
  if(['生','克','比和'].includes(type)){
   let blocked=null;
   if(type==='克'&&a.transmissions?.includes(1)&&b.transmissions?.includes(3)&&fiveRole(c.day_stem,b)==='鬼')blocked='初不能制末鬼';
   if(type==='克'&&a.transmissions?.includes(3)&&b.transmissions?.includes(1)&&fiveRole(c.day_stem,b)==='鬼'&&o.phase!=='outcome')blocked='末制初只在终局评价救达';
   edges.push({id:source+'>'+target+(pair.owner?'|view:'+pair.owner:''),source,target,type,routes:pair.routes,owner:pair.owner,blocked});
  }
 }
 const graph={nodes,by,edges,pairs:[...pairs.values()],active,groups,four,phase:o.phase,goal:o.goal,void_branches: voidBranches};
 graph.candidates=specialCandidates(nodes,graph.pairs);
 // Pin explicit semantic selections to real relationships, not caller-assigned labels.
 const modes=new Map();
 for(const r of o.effectRules){
  if(!r.basis)error('关系裁用须给依据');
  const candidate=graph.candidates.find(x=>x.id===r.id);
  if(!candidate)error('关系裁用ID不存在 '+r.id);
  if(!['disrupt','irrelevant','move','bind','release_binding'].includes(r.mode))error('非法关系作用 '+r.mode);
  if(r.mode==='release_binding'&&candidate.type!=='冲')error('只有实际冲关系可使用本破绊接口');
  if(r.mode==='release_binding'&&!r.bindingCause)error('破绊须指定解除哪项bindingCause，不能撤销全部合绊');
  if(r.mode==='bind'&&!['六合','天干五合'].includes(candidate.type))error('牵绊接口须为实际合关系');
  if(modes.has(r.id))error('同一关系不能重复裁用');modes.set(r.id,r);
 }
 graph.modes=modes;
 const releases=[];
 for(const release of o.tombReleases??[]){
  const n=by.get(release.target),source=by.get(release.source);
   if(!n||!source||!release.basis||!n.refs.some(r=>r.state==='墓'&&r.place===release.place)||!hasRelation(source.symbol,release.place,'六冲'))error('开墓须匹配真实墓位、冲者与适用依据');
   if(release.gate!==undefined&&(!Number.isFinite(release.gate)||release.gate<0||release.gate>1))error('开墓通路gate须在0至1');
  releases.push(release);
 }
 graph.releases=releases;
 return graph;
}

function edgesAt(graph,depth,values,p){
 const adjusted=graph.groups.map(g=>g.numeric_enabled===false?{...g,integrity:null,gate_multiplier:1}:groupStrength(g,values,p)),out=[];
 for(const e of graph.edges){
  if(e.blocked)continue;
  const routes=e.routes.filter(r=>depth>0||r.kind!=='yin');if(!routes.length)continue;
  const best=[...routes].sort((a,b)=>b.gate-a.gate||a.kind.localeCompare(b.kind))[0];
  let boost=1;
  for(const g of adjusted)if(g.mode==='cooperate'&&g.members.includes(e.source)&&g.members.includes(e.target))boost=Math.max(boost,g.gate_multiplier);
  out.push({...e,route:best.kind,raw_gate:best.gate*boost});
 }
 // A yin reference is the owner's local view, not a new outgoing attack on
 // every node which happens to use this source as its yin. Budget per view.
 const budgetKey=e=>e.owner?uid('view',e.owner,e.source):e.source;
 const sums=new Map();for(const e of out)sums.set(budgetKey(e),(sums.get(budgetKey(e))??0)+e.raw_gate);
 for(const e of out)e.gate=e.raw_gate/Math.max(1,sums.get(budgetKey(e))/p.inherited.relations.source_gate_budget);
 return {edges:out,groups:adjusted};
}
function greedyFactors(n,graph,values,p){
 if(n.kind!=='branch'||n.id===graph.goal.target)return [];
 const factors=[];
 for(const id of ['D:'+n.ground,'T:'+n.direct_yin]){
  const s=graph.by.get(id);if(!s||id===n.id||id===graph.goal.target||fiveRelation(s.symbol,n.symbol)!=='生')continue;
  const gate=id.startsWith('D:')?1:p.inherited.routes.direct_yin;
  factors.push({cause:'direct-nourish:'+id,loss:p.inherited.constraints.direct_greedy*gate*values[id]/(values[id]+values[n.id]+1e-12)});
 }
 return factors;
}
function greedyLoss(n,graph,values,p){return combineLosses(greedyFactors(n,graph,values,p),p.inherited.constraints.cap_greedy);}
function accessFor(n,graph,values,before,p){
 if(!graph.releases.some(r=>r.target===n.id))return n.access;
 const sum=n.refs.reduce((a,r)=>a+r.weight*r.body_ratio,0);
 return n.refs.reduce((a,r)=>{
  let h=r.access;
  for(const release of graph.releases.filter(x=>x.target===n.id&&x.place===r.place))h=Math.max(h,r.access+(1-r.access)*openingRatio(values[release.source]*(release.gate??1),before[n.id],p));
  return a+r.weight*r.body_ratio*h;
 },0)/sum;
}
function evaluate(graph,values,p,{depth,lower,before}){
 const gates=edgesAt(graph,depth,values,p),delta=Object.fromEntries(graph.nodes.map(n=>[n.id,0])),ledger=[];
 const subject=graph.by.get(graph.goal.target),old=p.inherited;
 for(const e of gates.edges){
  const a=graph.by.get(e.source),b=graph.by.get(e.target);
  const sourceValue=e.route==='yin'&&e.owner!==e.source?lower[e.source]:values[e.source];
  const targetValue=e.route==='yin'&&e.owner!==e.target?lower[e.target]:values[e.target];
  let tau=1;
  if(e.target===subject.id&&a.kind==='branch'&&['生','克'].includes(e.type))tau=1-greedyLoss(a,graph,e.route==='yin'?lower:values,p);
  const flow=directedEffect(e.type,sourceValue,targetValue,e.gate,a.seed,p,tau);
  let positiveReplacement=0,special=null;
  // Only the explicit stem 庚/辛 fire/long-life example is adapted; not all metal branches.
  if(e.type==='克'&&a.symbol==='巳'&&b.kind==='day'&&['庚','辛'].includes(b.symbol)&&b.refs.some(r=>r.place==='巳'&&r.state==='长生')){
   const positive=b.refs.filter(r=>r.place==='巳').reduce((sum,r)=>sum+p.baseline*old.season[b.season]*r.weight*Math.max(0,r.body_ratio-1),0);
   const j=graph.nodes.find(n=>n.kind==='general'&&n.carrier==='巳');
   const jr=j?fiveRelation(j.symbol,b.symbol):null;
   const support=jr==='生'?old.relations.support*values[j.id]:0,control=jr==='克'?old.relations.control*values[j.id]:0;
   special=goldFireAllocation(positive,-flow.received,sourceValue,values[b.id],support,control);
   positiveReplacement=special.positive-positive;flow.received=-special.negative;flow.cost=old.relations.control_cost_ratio*special.negative;
  }
  const targetBooked=b.kind!=='ground'&&(!e.owner||e.owner===b.id),sourceBooked=a.kind!=='ground'&&(!e.owner||e.owner===a.id);
  if(targetBooked)delta[b.id]+=flow.received+positiveReplacement;
  if(sourceBooked)delta[a.id]-=flow.cost;
  ledger.push({...e,source_strength:sourceValue,target_strength:targetValue,tau,received:targetBooked?flow.received:0,
   source_cost:sourceBooked?flow.cost:0,reference_reallocation:targetBooked?positiveReplacement:0,special,
   local_observation:e.owner??null,observed_received:flow.received,observed_source_cost:flow.cost});
 }
 const mapped={},access={};
 for(const n of graph.nodes){
  access[n.id]=accessFor(n,graph,values,before??values,p);
  mapped[n.id]=n.kind==='ground'?n.seed:n.retention*clip(access[n.id]*(n.base+delta[n.id]));
 }
 return {mapped,delta,ledger,access,groups:gates.groups};
}
function solveDepth(graph,p,{depth,lower,before}){
 const results=[];
 for(const init of p.iteration.initial_values){
  let values=Object.fromEntries(graph.nodes.map(n=>[n.id,n.kind==='ground'?n.seed:init]));let residual=Infinity,k=0;
  for(;k<p.iteration.max_iterations;k++){
   const v=evaluate(graph,values,p,{depth,lower:lower??values,before});
   residual=Math.max(...graph.nodes.map(n=>Math.abs(v.mapped[n.id]-values[n.id])));
   if(residual<p.iteration.tolerance)break;
   values=Object.fromEntries(graph.nodes.map(n=>[n.id,values[n.id]+p.iteration.damping*(v.mapped[n.id]-values[n.id])]));
  }
  if(k===p.iteration.max_iterations)error('方程未收敛，不交付综合分数');
  results.push({values,iterations:k,residual});
 }
 const spread=Math.max(...graph.nodes.map(n=>Math.max(...results.map(r=>r.values[n.id]))-Math.min(...results.map(r=>r.values[n.id]))));
 if(spread>p.iteration.agreement_tolerance)error('多个初值所得结果不一致，不择解交付');
 const main=results[1]??results[0];
 return {...main,initials:results.map(r=>({iterations:r.iterations,residual:r.residual})),spread,...evaluate(graph,main.values,p,{depth,lower:lower??main.values,before})};
}
function solveGraph(graph,p){
 const bare={...graph,releases:[]};
 let lower=solveDepth(bare,p,{depth:0});
 let upper=solveDepth(bare,p,{depth:1,lower:lower.values});
 if(graph.releases.length){
  const before=upper.values;
  lower=solveDepth(graph,p,{depth:0,before});
  upper=solveDepth(graph,p,{depth:1,lower:lower.values,before});
  return {...upper,lower,before};
 }
 return {...upper,lower};
}

function actions(graph,solution,c,o,p,shensha){
 const E=solution.values,old=p.inherited,rows=[],pending=[],mechanisms=[],virtueRoutes=[];
 const addPending=(id,rule,scope)=>pending.push({id,rule,scope});
 if(!shensha?.items)for(const id of graph.active)addPending(id,'adopted_shensha','未提供当前采用神煞，不能宣称完整作用');
 const groups=solution.groups;
 for(const group of groups)if(group.mode==='unresolved'&&group.type!=='未成会')for(const id of group.members)addPending(id,'group:'+group.id,'合的协作/牵绊用途未指定');
 for(const n of graph.nodes.filter(n=>n.kind!=='ground')){
  const greedy=greedyFactors(n,graph,E,p),disrupt=[],bind=[],releaseBindings=[];
  for(const candidate of graph.candidates.filter(x=>x.target===n.id)){
   const mode=graph.modes.get(candidate.id),source=graph.by.get(candidate.source);
   const direct=candidate.type==='六合'&&n.kind==='branch'&&[ 'D:'+n.ground,'T:'+n.direct_yin ].includes(source.id);
   const loss=(old.constraints[candidate.type]??0)*candidate.gate*E[source.id]/(E[source.id]+E[n.id]+1e-12);
   const cause=direct?'direct-nourish:'+source.id:candidate.type==='六合'?pairKey(source.id,n.id)+':合':candidate.id;
   if(mode?.mode==='disrupt')disrupt.push({cause,loss});
   else if(mode?.mode==='bind'||(direct&&!mode&&o.goal.mode!=='cooperate'))bind.push({cause,loss});
   else if(mode?.mode==='release_binding')releaseBindings.push({source:source.id,cause:mode.bindingCause,ratio:openingRatio(E[source.id]*candidate.gate,E[n.id],p)});
   else if(!mode&&['刑','冲','破','害','自刑','天干五合','六合'].includes(candidate.type)&&graph.active.includes(n.id)){
    if(candidate.type==='刑'&&source.symbol==='寅'&&n.symbol==='巳'&&c.lessons[0].tianpan==='寅'&&c.lessons[2].tianpan==='巳')disrupt.push({cause,loss});
    else addPending(n.id,candidate.id,'专项作用方向未适配');
   }
  }
  for(const g of groups.filter(x=>x.mode==='bind'&&x.members.includes(n.id))){
   const partners=g.members.filter(x=>x!==n.id),s=partners.reduce((sum,id)=>sum+E[id],0);
   bind.push({cause:'group-bind:'+g.id,loss:(old.constraints[g.type]??0)*g.integrity*s/(s+E[n.id]+1e-12)});
  }
  for(const release of releaseBindings)if(!bind.some(x=>x.cause===release.cause))error('破绊未匹配本节点的具体合绊 '+release.cause);
  const effectiveBind=bind.map(x=>({...x,loss:x.loss*(1-Math.max(0,...releaseBindings.filter(r=>r.cause===x.cause).map(r=>r.ratio)))}));
  const bindItems=cappedLossItems(effectiveBind,old.constraints.cap_binding);
  const binding=combineLosses(bindItems);
  const disruption=combineLosses(disrupt,old.constraints.cap_disruption);
  const move=[];
  const sha=n.kind==='branch'?(shensha?.items??[]).filter(x=>x.status==='resolved'&&x.places.some(place=>place.tian===n.symbol)):[];
  const virtues=[];
  for(const item of sha){
   const rule=o.shenshaRules.find(x=>x.id===item.id);
   if(rule&&!rule.basis)error('神煞适配须给依据');
   if(rule&&!['role','movement','virtue','irrelevant'].includes(rule.mode))error('未支持的神煞适配类型');
   if(rule?.mode==='virtue'){
    if(!['日德','支德','天德','月德'].includes(item.name))error('不能将任意神煞指定成德');
    if(fiveRole(c.day_stem,n)==='鬼')addPending(n.id,item.id,'德化鬼条件不满足普通德解资格');
    else if(rule.eligible!==true)addPending(n.id,item.id,'德解资格未明确');
    else {
     const target=rule.target??n.id;
     if(!graph.by.has(target)||graph.by.get(target).kind==='ground')error('德解目标须是本盘实际作用对象');
     virtues.push({target,item:item.id});
    }
   }else if(rule?.mode==='movement'||(!rule&&/(驿马|天马|丁马)$/.test(item.name))){
    if(o.goal.mode==='movement'&&n.kind==='branch'){
     if(n.refs[0].state==='长生')move.push({cause:'direct-nourish:D:'+n.ground,loss:old.constraints.direct_greedy*E['D:'+n.ground]/(E['D:'+n.ground]+E[n.id]+1e-12)});
     mechanisms.push({id:n.id,rule:'马的长生/墓/合/空分层',facts:{growth:n.refs[0].state,void:n.void_self,sitting_void:n.void_ground},hard_zero:false});
    }
   }else if(!rule&&['日禄','太岁','月建','旬仪'].includes(item.name)){
    // Role identity only, not a second source of five-element power.
   }else if(!rule&&graph.active.includes(n.id))addPending(n.id,item.id,'神煞专项事件适配未完成:'+item.name);
  }
  const greedyItems=cappedLossItems([...greedy,...move],old.constraints.cap_greedy);
  const greedAndMovement=combineLosses(greedyItems);
  const goalLoss=combineLosses([...bindItems,...greedyItems]);
  const act=activation(n,o.phase,p),potential=clip(E[n.id]*act*(1-disruption)*(1-goalLoss));
  for(const v of virtues)virtueRoutes.push({...v,source:n.id,capacity:potential});
  const problems=pending.filter(x=>x.id===n.id).map(x=>x.rule);
  const harmfulCoefficient=old.harm_tendency[n.season];
  const incomingHarm=solution.ledger.filter(x=>x.target===n.id&&x.type==='克').reduce((sum,x)=>sum-x.received*old.harm_tendency[graph.by.get(x.source).season],0);
  rows.push({id:n.id,strength:E[n.id],action_index:problems.length?null:potential,partial_action_index:potential,
   activation:act,disruption,binding,greedy:greedAndMovement,goal_loss:goalLoss,virtue_reduction:0,
   interpretation:{harm_tendency:harmfulCoefficient,favorable_tendency:old.favorable_tendency[n.season],
    qualified_adverse_index:o.adverseTargets?.includes(n.id)?incomingHarm:null},
   pending:problems,mechanisms:{disruption:disrupt,binding:bind,movement:move,releases:releaseBindings}});
 }
 for(const v of virtueRoutes){
  const target=rows.find(x=>x.id===v.target),source=rows.find(x=>x.id===v.source);
  const edges=solution.ledger.filter(x=>x.source===v.source&&x.target===v.target&&(!x.owner||x.owner===v.target));
  const gate=v.source===v.target?1:Math.max(0,...edges.map(x=>x.gate));
  if(!gate||source.pending.length){
   addPending(target.id,v.item,!gate?'德解未见有效定向通路':'德源自身作用尚有未适配条件');
   target.pending.push(v.item);target.action_index=null;continue;
  }
  target.virtue_reduction=Math.max(target.virtue_reduction,old.virtue_max_reduction*v.capacity*gate/10);
  mechanisms.push({id:target.id,rule:'定向德解',source:v.source,gate,cause:v.item});
 }
 for(const row of rows)if(row.interpretation.qualified_adverse_index!==null)row.interpretation.qualified_adverse_index*=1-row.virtue_reduction;
 return {rows,pending:[...new Map(pending.map(x=>[uid(x.id,x.rule),x])).values()],mechanisms};
}

export function computeStrength(c,context={}, {profile=STRENGTH_PROFILE,shensha}={}){
 const p=structuredClone(profile),o=normalizeContext(c,context),d=buildFacts(c),graph=graphFrom(c,d,o,p),solution=solveGraph(graph,p);
 for(const rule of o.shenshaRules)if(!(shensha?.items??[]).some(x=>x.status==='resolved'&&x.id===rule.id))error('神煞裁用不在本盘采用表 '+rule.id);
 const action=actions(graph,solution,c,o,p,shensha);
 const rows=graph.nodes.map(n=>({...n,element:element(n.symbol),strength:solution.values[n.id],access:solution.access[n.id],
  delta:solution.delta[n.id],formations:localFormations(n,graph.by),...(action.rows.find(r=>r.id===n.id)??{})}));
 const coverage={numeric_scope:'已登记基础与关系机制；事件专项按pending限制；合局数值依用户指示暂缓',strength_scope_complete:true,complete_for_declared_actions:action.pending.length===0,
  event_verdict_supported:false,pending:action.pending,
  adapters:['五气/十二气','旬空/坐空一次','墓闭藏/定向冲开','直接加临生扶泄耗克制','比和源限幅','本节点一层阴神观察','直接贪生合','六合牵绊','有条件刑冲破害','直接关系内的初末制鬼时序','庚辛临巳共同预算','德解资格接口','马的动静限制','四建身份不新增跨宫生克','评价时段更新'],
  deferred_by_user:['三合/半合/三会数值作用'],
  not_claimed:['全年季土自动判定','所有神煞及课体专项','合局数值及自动合化','遁干纳音全专项','录用/行业/成败裁决']};
 return {schema:'liuren-strength-research-v05',model:p.id,profile_sha256:hash(p),chart_sha256:hash(c),context:o,independent_strength_line:p.inherited.independent_strength_line,
  original_void:d.xun.void_branches,evaluation_void:graph.void_branches,rows,groups:solution.groups,
  four_buildings:graph.four,coverage,global_qi:globalQi(rows,graph.active),
  audit:{ledger:solution.ledger,lower_depth:solution.lower,convergence:{iterations:solution.iterations,residual:solution.residual,spread:solution.spread,initials:solution.initials},
   blocked_edges:graph.edges.filter(x=>x.blocked),relations:graph.candidates,mechanisms:action.mechanisms,active:graph.active,
   tomb_before:solution.before??null}};
}

export function compactStrength(result){
 return {model:result.model,season_profile:result.context.seasonProfile,phase:result.context.phase,
  actors:result.rows.filter(x=>x.kind!=='ground').map(x=>({id:x.id,strength:round(x.strength),
   action_index:x.action_index===null?null:round(x.action_index),
   ...(x.pending?.length?{pending:x.pending}:{}),...(x.formations.length?{formations:x.formations}:{}),
   below_reference:x.strength<result.independent_strength_line})),
  groups:result.groups.map(g=>({members:g.members,type:g.type,mode:g.mode,numeric_enabled:false,transformed:false})),
  coverage:{complete_for_declared_actions:result.coverage.complete_for_declared_actions,event_verdict_supported:false,
   pending:[...new Set(result.coverage.pending.map(x=>x.scope))]},global_qi:result.global_qi};
}
