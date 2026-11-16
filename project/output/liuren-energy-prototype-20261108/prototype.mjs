// Research prototype: feature extraction and a bounded, auditable influence solver.
// No connection to active workflows. No default traditional or predictive weights.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {buildFacts,element,fiveRelation,growth,seasonal,relations,HOMES,ZHI} from '../../tools/liuren-deterministic.mjs';

export const VERSION='liuren-energy-research-v0.1';
const clamp=x=>Math.max(0,Math.min(1,x));
const fail=message=>{throw new Error('ENERGY_RESEARCH: '+message);};
const finite=(x,label,min=-Infinity,max=Infinity)=>{
 if(typeof x!=='number'||!Number.isFinite(x)||x<min||x>max)fail(label+' out of range');
 return x;
};
const bundle=(a,b)=>({source:a,target:b,relationships:relations(a,b),reverse_relationships:relations(b,a),
 interpretation:'relationships coexist; no efficacy or additive bonus inferred'});
const triples={三合:['申子辰','亥卯未','寅午戌','巳酉丑'],三会:['寅卯辰','巳午未','申酉戌','亥子丑']};
export function translateScale(value,from='five',to='zero'){
 if(!['five','zero'].includes(from)||!['five','zero'].includes(to))fail('scale must be five or zero');
 finite(value,'display value',from==='five'?0:-5,from==='five'?10:5);
 return from===to?value:from==='five'?value-5:value+5;
}
export function applyRetention(value,ratio,{scale='five'}={}){
 finite(ratio,'retention',0,1);
 const positive=translateScale(value,scale,'five');
 return translateScale(positive*ratio,'five',scale);
}
// All numbers are explicit caller assumptions. Additive changes first; multiply
// nonnegative resources next; cap once per documented stage, never per label.
export function composeBase({baseline=5,adjustments=[],multipliers=[]}={}){
 finite(baseline,'baseline',0,10);
 if(!Array.isArray(adjustments)||!Array.isArray(multipliers))fail('factor arrays required');
 const causes=new Set(),ledger=[{cause_id:'coordinate-baseline',delta:baseline/10,
  parameter_id:'baseline',basis:'coordinate reference only; not calibrated traditional strength'}];
 for(const factor of [...adjustments,...multipliers]){
  for(const k of ['cause_id','parameter_id','basis'])if(typeof factor[k]!=='string'||!factor[k])fail('factor provenance required '+k);
  if(causes.has(factor.cause_id)||factor.cause_id==='coordinate-baseline')fail('one cause appears in multiple base factors; use a joint factor');
  causes.add(factor.cause_id);
 }
 let raw=baseline;
 for(const a of [...adjustments].sort((a,b)=>a.cause_id.localeCompare(b.cause_id))){
  raw+=finite(a.points,'additive points',-10,10);
  ledger.push({cause_id:a.cause_id,delta:a.points/10,parameter_id:a.parameter_id,basis:a.basis});
 }
 let value=10*clamp(raw/10);
 if(value!==raw)ledger.push({cause_id:'derived-additive-saturation',delta:(value-raw)/10,
  parameter_id:'range-rule',basis:'0..10 resource bound; derived arithmetic, not independent evidence'});
 for(const m of [...multipliers].sort((a,b)=>a.cause_id.localeCompare(b.cause_id))){
  const before=value;value*=finite(m.factor,'multiplier',0,10);
  ledger.push({cause_id:m.cause_id,delta:(value-before)/10,parameter_id:m.parameter_id,basis:m.basis,
   factor:m.factor,before_0to10:before,after_0to10:value});
 }
 const final=10*clamp(value/10);
 if(final!==value)ledger.push({cause_id:'derived-multiplier-saturation',delta:(final-value)/10,
  parameter_id:'range-rule',basis:'final 0..10 bound; derived arithmetic, not an outcome veto'});
 return {base:final/10,base_ledger:ledger,display_five:final,display_zero:final-5,
  order:'baseline + unique joint additive factors -> 0..10 bound -> multiplier product -> 0..10 bound',
  coefficients:'explicit caller assumptions; no defaults for month, growth, void or combinations'};
}
export function extractFeatures(chart,{lifeBranch=null,seasonProfile}={}){
 if(!['four-seasons','quarter-earth'].includes(seasonProfile))fail('explicit seasonProfile required');
 if(lifeBranch!==null&&!ZHI.includes(lifeBranch))fail('invalid life branch');
 const d=buildFacts(chart),at=b=>chart.heaven_earth.find(r=>r.di===b);
 const on=b=>chart.heaven_earth.find(r=>r.tian===b);
 const nodes=[],localFactors=[],roots={};
 for(const b of ZHI){
  const row=on(b),symbol=row.tianjiang,phase=seasonal(b,chart.month_branch,seasonProfile);
  const ids={earth:'D:'+row.di,heaven:'T:'+b,general:'J:'+symbol};
  const voidSelf=d.xun.void_branches.includes(b),voidGround=d.xun.void_branches.includes(row.di);
  const selfRoot='xun:'+d.xun.xun+':'+b,groundRoot='xun:'+d.xun.xun+':'+row.di;
  for(const [branch,yes,root] of [[b,voidSelf,selfRoot],[row.di,voidGround,groundRoot]]){
   if(yes)roots[root]={id:root,type:'旬空',branch,xun:d.xun.xun,identity:true,
    implication:'root condition only; no fixed strength loss, delay or failure implied'};
  }
  nodes.push({id:ids.heaven,kind:'天盘神',symbol:b,element:element(b),ground:row.di,general:symbol,
   season:phase,growth_at_ground:growth(b,row.di),direct_yin:at(b).tian,
   growth_at_yin:growth(b,at(b).tian),void_self:voidSelf,void_ground:voidGround,
   cause_roots:[...(voidSelf?[selfRoot]:[]),...(voidGround?[groundRoot]:[])],
   lesson_slots:d.nodes.find(n=>n.symbol===b).lesson_slots,
   transmission_slots:d.nodes.find(n=>n.symbol===b).transmission_slots});
  nodes.push({id:ids.general,kind:'天将',symbol,element:element(symbol),season:seasonal(symbol,chart.month_branch,seasonProfile),
   carried_by:b,ground:row.di,growth_at_carrier:growth(symbol,b),growth_at_ground:growth(symbol,row.di),
   void_inheritance:'not automatically copied from carrier; requires explicit source-conditioned factor'});
  nodes.push({id:ids.earth,kind:'地盘环境',symbol:row.di,element:element(row.di),season:seasonal(row.di,chart.month_branch,seasonProfile),
   role:'environment at a location, not a duplicate movable heaven branch',void_location:voidGround});
  const dt=fiveRelation(row.di,b),tj=fiveRelation(b,symbol),jt=fiveRelation(symbol,b),td=fiveRelation(b,row.di);
  const flags={内战:dt==='克'&&tj==='克',外战:jt==='克'&&td==='克',夹克:dt==='克'&&jt==='克',
   夹生:dt==='生'&&jt==='生',将生神:jt==='生',神生将:tj==='生',神将比和:tj==='比和'};
  localFactors.push({id:'local:'+row.di,participants:ids,
   signature:{season_heaven:phase,season_general:seasonal(symbol,chart.month_branch,seasonProfile),
    season_ground:seasonal(row.di,chart.month_branch,seasonProfile),growth_heaven_at_ground:growth(b,row.di),
    growth_general_at_carrier:growth(symbol,b),growth_general_at_ground:growth(symbol,row.di),
    ground_to_heaven:dt,heaven_to_general:tj,void_self:voidSelf,void_ground:voidGround},
   conditions:flags,ground_heaven:bundle(row.di,b),general_heaven:bundle(symbol,b),general_ground:bundle(symbol,row.di),
   active_mechanisms:[],numeric_status:'joint local factor awaits an explicit parameter profile',
   counting:'ground relation, ground growth and inner/outer-war label share this factor; no automatic independent deductions'});
 }
 const home=HOMES[chart.day_stem],upper=at(home).tian;
 nodes.push({id:'G:'+chart.day_stem,kind:'日干',symbol:chart.day_stem,element:element(chart.day_stem),
  season:seasonal(chart.day_stem,chart.month_branch,seasonProfile),home,upper,
  growth_at_home:growth(chart.day_stem,home),growth_at_upper:growth(chart.day_stem,upper),
  growth_profile:'stem yang-forward/yin-reverse; home is not a substitute heaven node'});
 const scopes={四课上神:[...new Set(chart.lessons.map(l=>l.tianpan))],
  三传:[...new Set(chart.transmissions.map(t=>t.diZhi))],
  课传上神:[...new Set([...chart.lessons.map(l=>l.tianpan),...chart.transmissions.map(t=>t.diZhi)])]};
 const groups=[];
 for(const [scope,available] of Object.entries(scopes)){
  for(const [type,sets] of Object.entries(triples))for(const set of sets){
   const present=[...set].filter(b=>available.includes(b));
   if(present.length>=2)groups.push({id:'group:'+scope+':'+type+':'+set,type,scope,members:[...set],present,
    missing:[...set].filter(b=>!present.includes(b)),membership:present.length===3?'complete':'partial',
    formation:'not adjudicated',transformation:'not inferred',
    counting:'complete and partial views of the same participants are not independent bonuses; scope aliases need one adopted mechanism'});
  }
 }
 const focus=[...new Set([chart.day_branch,...scopes.课传上神,...(lifeBranch?[lifeBranch,at(lifeBranch).tian]:[])])];
 const pairs=focus.flatMap((a,i)=>focus.slice(i+1).map(b=>({id:'pair:'+a+':'+b,
  ...bundle(a,b),participants:['T:'+a,'T:'+b],
  scope:'key-branch candidates; occurrence alone does not establish action route',active:false})));
 return {schema:VERSION,mode:'symbolic-feature-model',calibration:null,numerical_scores:null,
  chart_sha256:d.chart_sha256,original_time:chart.datetime??chart.pillars,
  proposed_display:{five:{range:[0,10],reference:5},zero:{range:[-5,5],reference:0},conversion:'zero = five - 5; proportional adjustment applies to five-scale nonnegative resource'},
  assessment_time:'original chart only; future snapshots require explicit temporal convention',
  season_profile:seasonProfile,season_alternatives:'retained in original deterministic facts; never silently average or select by outcome',
  month_context:{branch:chart.month_branch,source:'one common seasonal context; not independent votes for each node'},
  nodes,local_factors:localFactors,condition_roots:Object.values(roots),group_candidates:groups,pair_candidates:pairs,
  day_context:{stem:chart.day_stem,branch:chart.day_branch,upper,life_branch:lifeBranch,
   life_upper:lifeBranch?at(lifeBranch).tian:null},
  activated_positions:chart.transmissions.map(t=>({node:'T:'+t.diZhi,stage:t.index,
   role:t.index===1?'发用':'传位',effect:'activation/prominence feature; no source-free fixed strength multiplier'})),
  meaning_layer:{favorable_or_harmful:'not equal to resource strength; apply adopted 喜旺恶衰, 旺鬼贪荣, 贪生合 and domain roles',
   direct_greedy_life_union:'joint context may restrict intended action toward subject; not identical to remote support',
   twelve_states:'state and contextual meaning remain visible; no universal twelve-rank monotonic scale'},
  missing_for_numeric_use:['reusable seasonal prior values','joint local-factor response functions',
   'source-scoped void response','activated relation routes and competing mechanism groups',
   'coupling and resistance coefficients','activation and intended-action coefficients','time-update convention'],
  limits:['Uncalibrated research index, not physical energy or outcome probability.',
   'No success/failure or industry option selected. Known-outcome case is development evidence only.',
   'Membership, relation identity and effective action are separate fields.']};
}

// Generic numeric workbench. Every base and coefficient is caller supplied.
// x_i = clip(b_i + sum_c d_ci(x), 0, 1).
// support/transfer: d_target = w*g*x_source; transfer additionally spends that same amount at source.
// control: d_target = -w*g*x_source/(1+r*x_target).
// Contractivity is checked before iteration; no self-inflating cycles or hidden final void veto.
export function solveInfluenceModel(model,{tolerance=1e-10,maxIterations=2000,damping=1}={}){
 if(model?.schema!=='liuren-energy-numeric-research-v1')fail('numeric model schema');
 if(typeof model.profile_id!=='string'||!model.profile_id)fail('explicit parameter profile id required');
 if(!Array.isArray(model.nodes)||!model.nodes.length||!Array.isArray(model.events))fail('nodes/events required');
 finite(tolerance,'tolerance',1e-14,1e-3);finite(damping,'damping',0.001,1);
 if(!Number.isInteger(maxIterations)||maxIterations<1||maxIterations>100000)fail('iteration bound');
 const ids=model.nodes.map(n=>n.id),index=new Map(ids.map((id,i)=>[id,i]));
 if(ids.some(id=>typeof id!=='string'||!id)||new Set(ids).size!==ids.length)fail('duplicate/invalid node');
 const base=model.nodes.map(n=>{
  finite(n.base,n.id+' base',0,1);
  if(!Array.isArray(n.base_ledger)||!n.base_ledger.length)fail('base ledger required '+n.id);
  const groups=n.base_ledger.map(t=>t.cause_id);
  if(groups.some(g=>typeof g!=='string'||!g)||new Set(groups).size!==groups.length)fail('duplicate base cause '+n.id);
  const total=n.base_ledger.reduce((s,t)=>s+finite(t.delta,'base delta',-1,1),0);
  if(Math.abs(total-n.base)>1e-12)fail('base ledger does not reconcile '+n.id);
  return n.base;
 });
 const events=[],mechanisms=new Set(),eventIds=new Set(),rowBounds=base.map(()=>0);
 for(const e of model.events){
  const s=index.get(e.source),t=index.get(e.target);
  if(!e.id||eventIds.has(e.id)||s===undefined||t===undefined||s===t||!['support','control','transfer'].includes(e.kind))fail('invalid/duplicate event');
  if(model.nodes[t].fixed||(e.kind==='transfer'&&model.nodes[s].fixed))fail('event modifies fixed environment');
  for(const k of ['cause_id','mechanism_id','parameter_id','basis'])if(typeof e[k]!=='string'||!e[k])fail('explicit event provenance required '+k);
  const key=[e.cause_id,e.mechanism_id,e.source,e.target].join('|');
  if(mechanisms.has(key))fail('duplicate mechanism via aliases');
  if(model.nodes[t].base_ledger.some(term=>term.cause_id===e.cause_id))fail('same cause charged as both base and dynamic event; replace by one joint factor');
  finite(e.coefficient,'coefficient',0,1);finite(e.gate,'gate',0,1);
  const resistance=e.kind==='control'?finite(e.resistance,'resistance',0,10):0;
  const w=e.coefficient*e.gate;
  rowBounds[t]+=w*((model.nodes[s].fixed?0:1)+(e.kind==='control'?resistance:0));
  if(e.kind==='transfer')rowBounds[s]+=w;
  events.push({...e,s,t,w,resistance});eventIds.add(e.id);mechanisms.add(key);
 }
 const L=Math.max(...rowBounds);
 if(L>=1)fail('non-contractive feedback profile; Lipschitz bound '+L+' must be < 1');
 function step(x){
  const raw=[...base],ledger=[];
  for(const e of events){
   const amount=e.w*x[e.s]/(e.kind==='control'?1+e.resistance*x[e.t]:1);
   const changes=[{node:e.target,delta:e.kind==='control'?-amount:amount}];
   raw[e.t]+=changes[0].delta;
   if(e.kind==='transfer'){raw[e.s]-=amount;changes.push({node:e.source,delta:-amount});}
   ledger.push({event_id:e.id,cause_id:e.cause_id,mechanism_id:e.mechanism_id,
    parameter_id:e.parameter_id,basis:e.basis,source:e.source,target:e.target,kind:e.kind,
    coefficient:e.coefficient,gate:e.gate,resistance:e.resistance,source_strength:x[e.s],
    target_strength:x[e.t],amount,changes});
  }
  const values=raw.map((v,i)=>model.nodes[i].fixed?base[i]:clamp(v));
  return {raw,values,ledger};
 }
 let x=[...base],iterations=0,residual=Infinity;
 for(;iterations<maxIterations;iterations++){
  const f=step(x);residual=Math.max(...x.map((v,i)=>Math.abs(f.values[i]-v)));
  if(residual<=tolerance)break;
  x=x.map((v,i)=>model.nodes[i].fixed?v:(1-damping)*v+damping*f.values[i]);
 }
 if(iterations===maxIterations)fail('iteration budget exhausted; no approximate score silently accepted');
 const final=step(x);
 return {schema:VERSION,mode:'explicit-parameter-research-index',profile_id:model.profile_id,
  predictive_validation:false,parameter_profile_status:model.calibration?.status??'undeclared',
  numeric_values_are:'normalized comparative index, not physical energy, probability or a verdict',
  convergence:{iterations,residual,lipschitz_bound:L,error_bound:residual/(1-L),unique_fixed_point:true},
  scores:model.nodes.map((n,i)=>({id:n.id,index:x[i],display_five:10*x[i],display_zero:10*x[i]-5,base:n.base,
   base_ledger:n.base_ledger,raw_before_saturation:final.raw[i],saturation_delta:final.values[i]-final.raw[i],
   ledger_delta:final.ledger.flatMap(e=>e.changes).filter(t=>t.node===n.id).reduce((s,t)=>s+t.delta,0)})),
  event_ledger:final.ledger,model,
  limits:['All coefficients are explicitly supplied research assumptions unless separately established.',
   'No post-score empty/void veto, success threshold or option ranking is implemented.',
   'Calibration declaration is a label supplied by the caller, not validation by this solver.']};
}

export function syntheticModel(){return {
 schema:'liuren-energy-numeric-research-v1',profile_id:'synthetic-engineering-only-not-a-liuren-weight-table',
 calibration:{status:'uncalibrated'},
 nodes:[{id:'strong-target',base:0.8,base_ledger:[{cause_id:'fixture-prior-A',delta:0.8}]},
  {id:'weak-source',base:0.1,base_ledger:[{cause_id:'fixture-prior-B',delta:0.1}]}],
 events:[{id:'fixture-control',source:'weak-source',target:'strong-target',kind:'control',coefficient:0.2,
  gate:1,resistance:1,cause_id:'fixture-relation',mechanism_id:'actual-control',parameter_id:'synthetic-c',
  basis:'Synthetic numerical example to verify weak control cannot arbitrarily erase a strong target; no ancient coefficients asserted.'}]
};}

export function sweepCoefficient(model,parameterId,values){
 if(typeof parameterId!=='string'||!Array.isArray(values)||values.length<2||values.length>101)fail('bounded coefficient sweep required');
 if(!model.events.some(e=>e.parameter_id===parameterId))fail('coefficient parameter not found');
 const runs=values.map(value=>{
  finite(value,'sweep coefficient',0,1);
  const candidate=structuredClone(model);
  for(const e of candidate.events)if(e.parameter_id===parameterId)e.coefficient=value;
  try{
   const result=solveInfluenceModel(candidate);
   return {value,valid:true,scores:result.scores.map(n=>({id:n.id,display_five:n.display_five})),
    numerical_error:result.convergence.error_bound*10};
  }catch(error){return {value,valid:false,error:error.message};}
 });
 const good=runs.filter(r=>r.valid);
 const ranges=model.nodes.map(n=>{
  const scores=good.map(r=>r.scores.find(s=>s.id===n.id).display_five);
  return {id:n.id,min:scores.length?Math.min(...scores):null,max:scores.length?Math.max(...scores):null};
 });
 return {schema:VERSION,mode:'research-coefficient-sensitivity',parameter_id:parameterId,runs,ranges,
  limits:['Only sampled explicit coefficient values, not a rigorous all-parameter interval bound.',
   'Unstable parameter sets remain visible; favorable output is not automatically selected.']};
}

async function main(){
 const [action,input,output,seasonProfile,lifeBranch]=process.argv.slice(2);
 let result;
 if(action==='extract'){
  const raw=JSON.parse((await fs.readFile(input,'utf8')).replace(/^\uFEFF/,''));
  const c=raw.schema==='liuren-chart-facts-v1'?raw:raw._direct?.facts??raw.facts;
  if(!c)fail('trusted chart facts absent');
  result=extractFeatures(c,{seasonProfile,lifeBranch:lifeBranch??null});
 }else if(action==='solve')result=solveInfluenceModel(JSON.parse((await fs.readFile(input,'utf8')).replace(/^\uFEFF/,'')));
 else if(action==='demo')result=solveInfluenceModel(syntheticModel());
 else fail('usage: extract <archive> <out.json> <four-seasons|quarter-earth> [lifeBranch]; solve <model.json> <out.json>; demo [unused] <out.json>');
 const text=JSON.stringify(result,null,2)+'\n';
 if(output)await fs.writeFile(output,text);else process.stdout.write(text);
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url))await main();
