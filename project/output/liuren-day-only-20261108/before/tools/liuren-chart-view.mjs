// One presentation for humans, chart tools and adjudicator cores.
// Internal validated records remain the calculation/transport source.
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {buildFacts,HOMES,relations,ZHI,GAN} from './liuren-deterministic.mjs';
const rawProfile=await fs.readFile(new URL('./liuren-base-index-profile.json',import.meta.url),'utf8');
export const BASE_INDEX_PROFILE=JSON.parse(rawProfile);
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
export function chartView(c,{deterministic,shensha,conventions}={}){
 const d=deterministic??buildFacts(c),ss=shensha??d.adopted_shensha;
 if(!ss?.items)throw Error('正式盘需要当前采用神煞结果');
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
  state:{month_qi:qi(n.seasonal.profiles),growth_ground:n.growth.ground,growth_yin:n.growth.yin,
   base_index:baseIndex('branch',n.seasonal.profiles,[n.growth.ground,n.growth.yin],{self:n.void_self,ground:n.void_ground}),
   local:[...pairState(n.symbol,n.ground,'神','地'),...pairState(n.general,n.symbol,'将','神'),
    ...pairState(n.direct_yin,n.symbol,'阴神','神'),...pairState(n.general,n.ground,'将','地')],
   ...(formations.get(n.id)?.length?{formations:formations.get(n.id)}:{}),
   ...(samePlace.get(n.id+':'+n.symbol)?.length?{coexistence:samePlace.get(n.id+':'+n.symbol)}:{})},
  general_state:{element:n.general_element,month_qi:qi(n.general_seasonal.profiles),
   growth_carrier:n.general_growth.branch,growth_ground:n.general_growth.ground,
   base_index:baseIndex('general',n.general_seasonal.profiles,[n.general_growth.branch,n.general_growth.ground]),
   ...(samePlace.get(n.id+':'+n.general)?.length?{coexistence:samePlace.get(n.id+':'+n.general)}:{})},
  shensha:ss.items.filter(s=>s.status==='resolved'&&s.places.some(r=>r.tian===n.symbol)).map(s=>[s.id,s.name])
 }));
 const stemView=s=>({id:s.id,symbol:s.symbol,element:s.element,home:s.home,upper:s.upper,direct_yin:s.direct_yin,
  month_qi:qi(s.seasonal.profiles),growth:{home:s.growth.home,upper:s.growth.upper,yin:s.growth.yin,day_branch:s.growth.day_branch},
  local:[...pairState(s.upper,s.symbol,'上神','本干'),...pairState(s.direct_yin,s.symbol,'干阴神','本干')],
  void_positions:[d.xun.void_branches.includes(s.home)?'寄宫旬空':'',
   d.xun.void_branches.includes(s.upper)?'上神旬空':'',d.xun.void_branches.includes(s.direct_yin)?'干阴神旬空':''].filter(Boolean),
  base_index:baseIndex('stem',s.seasonal.profiles,[s.growth.upper])});
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
  strength_model:{id:p.id,kind:p.kind,range:p.range,scope:'月令、十二气及支神空亡的基础指数；生克制救未计',
   seasonal_keys:{四季:'春木夏火秋金冬水',季土:'辰未戌丑土旺条件表'},general_void:'将的乘支空、坐空见同宫status，未另扣将分'},
  lessons:c.lessons.map((l,i)=>({...l,...(i===0?{day_stem_home:HOMES[c.day_stem]}:{}),status:voidStatus(node(l.tianpan).void_self,node(l.tianpan).void_ground)})),
  transmissions:c.transmissions.map(t=>({...t,liuqin:node(t.diZhi).kin.value,tianGan:node(t.diZhi).xungan,
   earth_position:node(t.diZhi).ground,status:voidStatus(node(t.diZhi).void_self,node(t.diZhi).void_ground)})),
  heaven_earth,day:stemView(d.day),stems:d.stems.filter(s=>s.symbol!==c.day_stem).map(stemView),
  anchors:d.anchors,active_relations:activeRelations,
  structure:{transmission_same_element:d.structure.same_element,plate_is_identity:d.structure.plate_is_identity,
   plate_is_opposition:d.structure.plate_is_opposition,triple_members:d.structure.triple_member_candidates}};
 if(c.participants?.length)view.participants=c.participants;
 if(c.declared_life?.length)view.declared_life=c.declared_life;
 if(c.participants?.length)view.year_life_verified=c.year_life_verified===true;
 if(missing.length)view.missing_shensha=missing;
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
export async function exportAIChart(result,{persist=true}={}){
 if(!result.ok||!result.facts||result.validation?.ok!==true)return {ok:false,error:result.error??{code:'CHART_UNUSABLE',message:'排盘未完成'}};
 const facts=chartView(result.facts,{shensha:result.shensha_resolution,conventions:result.conventions});
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
export function chartQuery(c,shensha,symbols=[]){
 if(!Array.isArray(symbols)||symbols.some(s=>!ZHI.includes(s)&&!GAN.includes(s)))throw Error('focus symbols');
 const v=chartView(c,{shensha});
 if(!symbols.length)return v;
 return {...v,schema:'liuren-ai-chart-query-v1',focus_symbols:symbols,
  heaven_earth:v.heaven_earth.filter(n=>symbols.includes(n.tian)),stems:v.stems.filter(s=>symbols.includes(s.symbol))};
}
