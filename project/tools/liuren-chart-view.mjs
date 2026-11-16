// One presentation for humans, chart tools and adjudicator cores.
// Internal validated records remain the calculation/transport source.
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {buildFacts,HOMES,relations,ZHI,GAN} from './liuren-deterministic.mjs';
import {palaceStrength,palaceProfiles,PALACE_MODEL,BANDS,strengthBand} from './liuren-palace-strength.mjs';
import {STRENGTH_INTERPRETATION} from './liuren-strength-interpretation.mjs';
import {bifaView} from './liuren-bifa-view.mjs';
const rawProfile=await fs.readFile(new URL('./liuren-base-index-profile.json',import.meta.url),'utf8');
export const BASE_INDEX_PROFILE=JSON.parse(rawProfile);
export const LOCAL_STRENGTH_PROFILE=JSON.parse(await fs.readFile(new URL('./liuren-local-strength-profile.json',import.meta.url),'utf8'));
const hash=s=>createHash('sha256').update(s).digest('hex');
const p=BASE_INDEX_PROFILE;
const qi=profiles=>profiles['four-seasons']===profiles['quarter-earth']?profiles['four-seasons']:
 {四季:profiles['four-seasons'],季土:profiles['quarter-earth']};
export const voidStatus=(self,ground)=>[self?'旬空':'',ground?'坐空':''].filter(Boolean).join('、');
const round=x=>Math.round(x*1000)/1000;
// Identical to the v0.2 baseScore layer: no inter-node flow or action score.
export function baseIndex(kind,profiles,states,{self=false,ground=false}={}){
 const w=p.growth_reference_weights;
 const g=kind==='branch'?w.heaven_ground*p.growth[states[0]]+w.heaven_yin*p.growth[states[1]]:
  kind==='general'?w.general_carrier*p.growth[states[0]]+w.general_ground*p.growth[states[1]]:p.growth[states[0]];
 if(!Number.isFinite(g))throw Error('未登记十二气状态');
 const score=season=>{
  if(!Number.isFinite(p.season[season]))throw Error('未登记五气状态');
  const retention=kind==='branch'?Math.min(self?p.void_self_retention[season]:1,ground?p.void_self_retention[season]**p.void_ground_exponent:1):1;
  return round(Math.max(p.range[0],Math.min(p.range[1],p.baseline*p.season[season]*g))*retention);
 };
 return profiles['four-seasons']===profiles['quarter-earth']?score(profiles['four-seasons']):
  {四季:score(profiles['four-seasons']),季土:score(profiles['quarter-earth'])};
}
function pairState(a,b,an,bn){
 const forward=relations(a,b),reverse=relations(b,a),r=forward[0].value;
 const out=[{生:an+'生'+bn,克:an+'克'+bn,被生:bn+'生'+an,被克:bn+'克'+an,比和:an+'与'+bn+'比和'}[r]];
 for(const v of forward.slice(1))out.push(v.type==='刑'?an+'刑'+bn:an+'与'+bn+v.type.replace('自刑候选','自刑'));
 for(const v of reverse.slice(1))if(v.type==='刑')out.push(bn+'刑'+an);
 return [...new Set(out)];
}
export function chartView(c,{deterministic,shensha,conventions,stemSymbols=[],researchStrength,seasonProfile}={}){
 if(seasonProfile!==undefined&&seasonProfile!=='quarter-earth')throw Error('单表盘只支持五行月令quarter-earth');
 if(seasonProfile&&researchStrength&&researchStrength.context.seasonProfile!==seasonProfile)throw Error('研究盘与指定五行月令不一致');
 const d=deterministic??buildFacts(c),ss=shensha??d.adopted_shensha;
 if(!ss?.items)throw Error('正式盘需要当前采用神煞结果');
 if(researchStrength&&researchStrength.chart_sha256!==hash(JSON.stringify(c)))throw Error('研究计算结果不属于此原盘');
 const researchRows=researchStrength?new Map(researchStrength.rows.map(n=>[n.id,n])):null;
 const strength=researchStrength?null:seasonProfile?{[seasonProfile]:palaceStrength(c,seasonProfile,{shensha:ss})}:palaceProfiles(c,{shensha:ss});
 const displayQi=(profiles,id)=>researchRows?researchRows.get(id)?.season:seasonProfile?profiles[seasonProfile]:qi(profiles);
 const actionValue=id=>{
  const row=researchRows?.get(id);
  return !row?undefined:row.action_index===null?null:Math.round(row.action_index*10)/10;
 };
 const strengthValue=id=>{
  if(researchRows)return researchRows.has(id)?Math.round(researchRows.get(id).strength*10)/10:undefined;
  if(seasonProfile){const v=strength[seasonProfile].rows.find(n=>n.id===id)?.strength;return v===undefined?undefined:round(v);}
  const a=strength['four-seasons'].rows.find(n=>n.id===id)?.strength,b=strength['quarter-earth'].rows.find(n=>n.id===id)?.strength;
  if(a===undefined||b===undefined)return undefined;
  return round(a)===round(b)?round(a):{四季:round(a),季土:round(b)};
 };
 const levelValue=id=>{
  if(researchRows)return strengthBand(researchRows.get(id)?.strength);
  if(seasonProfile)return strengthBand(strength[seasonProfile].rows.find(n=>n.id===id)?.strength);
  const a=strengthBand(strength['four-seasons'].rows.find(n=>n.id===id)?.strength),b=strengthBand(strength['quarter-earth'].rows.find(n=>n.id===id)?.strength);
  return a===b?a:{四季:a,季土:b};
 };
 const node=b=>d.nodes.find(n=>n.symbol===b);
 const formations=new Map(d.basic_states?.local.rows.map(r=>[r[0],Object.entries(r.at(-1)).filter(([,v])=>v).map(([k])=>k)])??[]);
 const samePlace=new Map();
 for(const row of d.basic_states?.coexistence.rows??[]){
  const key=row[0]+':'+row[1];
  samePlace.set(key,[...(samePlace.get(key)??[]),...row.at(-1).map(f=>row[2]+':'+f.replace('，不等于已开墓',''))]);
 }
 const heaven_earth=d.nodes.map(n=>({
  id:n.id,di:n.ground,tian:n.symbol,tianjiang:n.general,element:n.element,
  direct_yin:n.direct_yin,liuqin:n.kin.value,xungan:n.xungan,nayin:n.engine_nayin,
  status:voidStatus(n.void_self,n.void_ground),
  yin_status:voidStatus(node(n.direct_yin).void_self,node(n.direct_yin).void_ground),
  lesson_slots:n.lesson_slots,transmission_slots:n.transmission_slots,
  state:{month_qi:displayQi(n.seasonal.profiles,'T:'+n.symbol),growth_ground:n.growth.ground,growth_yin:n.growth.yin,
   strength_index:strengthValue('T:'+n.symbol),strength_level:levelValue('T:'+n.symbol),
   ...(researchRows?{action_index:actionValue('T:'+n.symbol)}:{}),
   local:[...pairState(n.symbol,n.ground,'神','地'),...pairState(n.general,n.symbol,'将','神'),
    ...pairState(n.direct_yin,n.symbol,'阴神','神'),...pairState(n.general,n.ground,'将','地')],
   ...(formations.get(n.id)?.length?{formations:formations.get(n.id)}:{}),
   ...(samePlace.get(n.id+':'+n.symbol)?.length?{coexistence:samePlace.get(n.id+':'+n.symbol)}:{})},
  general_state:{element:n.general_element,month_qi:displayQi(n.general_seasonal.profiles,'J:'+n.general),
   growth_carrier:n.general_growth.branch,growth_ground:n.general_growth.ground,
   strength_index:strengthValue('J:'+n.general),strength_level:levelValue('J:'+n.general),
   ...(researchRows?{action_index:actionValue('J:'+n.general)}:{}),
   ...(samePlace.get(n.id+':'+n.general)?.length?{coexistence:samePlace.get(n.id+':'+n.general)}:{})},
  shensha:ss.items.filter(s=>s.status==='resolved'&&s.places.some(r=>r.tian===n.symbol)).map(s=>[s.id,s.name])
 }));
 const stemView=s=>({id:s.id,symbol:s.symbol,element:s.element,home:s.home,upper:s.upper,direct_yin:s.direct_yin,
  month_qi:displayQi(s.seasonal.profiles,'S:'+s.symbol),growth:{home:s.growth.home,upper:s.growth.upper,yin:s.growth.yin,day_branch:s.growth.day_branch},
  local:[...pairState(s.upper,s.symbol,'上神','本干'),...pairState(s.direct_yin,s.symbol,'干阴神','本干')],
  void_positions:[d.xun.void_branches.includes(s.home)?'寄宫旬空':'',
   d.xun.void_branches.includes(s.upper)?'上神旬空':'',d.xun.void_branches.includes(s.direct_yin)?'干阴神旬空':''].filter(Boolean),
  strength_index:strengthValue('S:'+s.symbol),strength_level:levelValue('S:'+s.symbol),...(researchRows?{action_index:actionValue('S:'+s.symbol)}:{})});
 // Preserve the old focused chart's pair facts, plus the actual day branch.
 // All are fixed relations, without efficacy, formation or outcome decisions.
 const active=[...new Set([d.day.symbol,c.day_branch,...Object.values(d.anchors),...d.structure.transmissions])];
 const activeRelations=active.flatMap((a,i)=>active.slice(i+1).map(b=>({a,b,state:pairState(a,b,a,b)})));
 const missing=ss.items.filter(s=>!['resolved','disabled'].includes(s.status)).map(s=>({name:s.name,reason:s.reason}));
 const view={schema:'liuren-ai-chart-v1',datetime:c.event_datetime,lunar:c.lunar,pillars:c.pillars,
  month_general:c.month_general,xun:d.xun.xun,void_branches:d.xun.void_branches,chart_types:c.chart_types,
  nobleman:{rule:c.nobleman?.rule,zhouye:c.nobleman?.actual_zhouye,heaven_branch:c.nobleman?.heaven_branch,direction:c.nobleman?.direction},
  ...(conventions?.settings?{settings:conventions.settings}:{}),
  growth_basis:{stems:'天干十二长生，阳顺阴逆',branches_and_generals:'五行十二气顺行，木亥火寅金巳水土申'},
  strength_interpretation:STRENGTH_INTERPRETATION,
  strength_model:researchStrength?{id:researchStrength.model,kind:'研究综合旺衰及定向作用',range:p.range,
   season_profile:researchStrength.context.seasonProfile,phase:researchStrength.context.phase,goal:researchStrength.context.goal,
   strength_scope_complete:researchStrength.coverage.strength_scope_complete,
   action_complete:researchStrength.coverage.complete_for_declared_actions,
   deferred:researchStrength.coverage.deferred_by_user,
   ...(researchStrength.context.evaluation?{evaluation:researchStrength.context.evaluation,evaluation_void:researchStrength.evaluation_void}:{}),
   pending:[...new Set(researchStrength.coverage.pending.map(x=>x.scope))]}:
  {id:PALACE_MODEL,base_model:strength[seasonProfile??'four-seasons'].model,profile_sha256:strength[seasonProfile??'four-seasons'].profile_sha256,kind:'研究单宫旺衰',range:p.range,reference:5,
   scope:'已计天地、自己的直接阴神、同宫神将及日干自身直接生扶泄耗克制；未计刑冲合化、神煞及取用后跨宫作用',
   bands:BANDS,selected_relations:'取用并明确双方作用依据后，调用liuren_compute(action=strength)补算；不得自行加减或再扣空亡',
   ...(seasonProfile?{season_profile:seasonProfile,seasonal_basis:'五行月令旺相休囚死：寅卯木、巳午火、申酉金、亥子水、辰未戌丑土当令；单一采用表，不是季末十八日自动算法'}:{seasonal_keys:{四季:'春木夏火秋金冬水',季土:'辰未戌丑土旺条件表'}}),general_void:'乘支空通过实际生克通路影响将，未另扣将分'},
  lessons:c.lessons.map((l,i)=>({...l,...(i===0?{day_stem_home:HOMES[c.day_stem]}:{}),status:voidStatus(node(l.tianpan).void_self,node(l.tianpan).void_ground)})),
  transmissions:c.transmissions.map(t=>({...t,liuqin:node(t.diZhi).kin.value,tianGan:node(t.diZhi).xungan,
   earth_position:node(t.diZhi).ground,status:voidStatus(node(t.diZhi).void_self,node(t.diZhi).void_ground)})),
  heaven_earth,day:stemView(d.day),
  anchors:d.anchors,active_relations:activeRelations,
  structure:{transmission_same_element:d.structure.same_element,plate_is_identity:d.structure.plate_is_identity,
   plate_is_opposition:d.structure.plate_is_opposition,triple_members:d.structure.triple_member_candidates}};
 if(researchStrength)view.qi_summary={by_element:Object.fromEntries(Object.entries(researchStrength.global_qi.by_element).map(([key,value])=>[key,value.mean_strength===null?null:Math.round(value.mean_strength*10)/10])),strongest:researchStrength.global_qi.strongest};
 if(!c.year_life&&c.participants?.length)view.participants=c.participants;
 const requestedStems=d.stems.filter(s=>s.symbol!==c.day_stem&&stemSymbols.includes(s.symbol));
 if(requestedStems.length)view.stems=requestedStems.map(stemView);
 if(!c.year_life&&c.declared_life?.length)view.declared_life=c.declared_life;
 if(c.year_life?.participants?.length)view.year_life=c.year_life;
 else if(c.participants?.length)view.year_life_verified=c.year_life_verified===true;
 if(missing.length)view.missing_shensha=missing;
 view.bifa_conditions=bifaView(view);
 return view;
}
// Keep each palace/lesson on one row for inspection, without redundant JSON indentation.
export function formatChart(view){
 const entries=Object.entries(view).filter(([,v])=>v!==undefined);
 return '{\n'+entries.map(([key,value])=>{
  const body=Array.isArray(value)&&value.length&&value.every(v=>v&&typeof v==='object')?
   '[\n'+value.map(v=>'    '+JSON.stringify(v)).join(',\n')+'\n  ]':JSON.stringify(value);
  return '  '+JSON.stringify(key)+': '+body;
 }).join(',\n')+'\n}\n';
}
export async function exportAIChart(result,{persist=true,seasonProfile}={}){
 if(!result.ok||!result.facts||result.validation?.ok!==true)return {ok:false,error:result.error??{code:'CHART_UNUSABLE',message:'排盘未完成'}};
 const facts=chartView(result.facts,{shensha:result.shensha_resolution,conventions:result.conventions,seasonProfile});
 let chart_file=null;
 if(persist&&result.archive?.path){
  const source=await fs.readFile(result.archive.path);
  if(hash(source)!==result.archive.sha256)throw Error('正式盘保存前源盘发生变化');
  const bytes=formatChart(facts),digest=hash(bytes);
  const target=result.archive.path.replace(/\.json$/i,'')+'.ai-'+digest.slice(0,16)+'.json';
  try{await fs.writeFile(target,bytes,{encoding:'utf8',flag:'wx'});}
  catch(e){if(e.code!=='EEXIST'||await fs.readFile(target,'utf8')!==bytes)throw e;}
  chart_file={path:target,sha256:digest};
 }
 return {ok:true,facts,archive:result.archive,chart_file};
}
export function chartQuery(c,shensha,symbols=[],{seasonProfile}={}){
 if(!Array.isArray(symbols)||symbols.some(s=>!ZHI.includes(s)&&!GAN.includes(s)))throw Error('focus symbols');
 const v=chartView(c,{shensha,stemSymbols:symbols.filter(s=>GAN.includes(s)),seasonProfile});
 if(!symbols.length)return v;
 return {...v,schema:'liuren-ai-chart-query-v1',focus_symbols:symbols,
  heaven_earth:v.heaven_earth.filter(n=>symbols.includes(n.tian))};
}
