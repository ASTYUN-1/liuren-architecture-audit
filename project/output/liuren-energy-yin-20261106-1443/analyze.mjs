import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {extractFeatures} from '../liuren-energy-prototype-20261108/prototype.mjs';
import {buildCore,solveCore,actionLayer} from '../liuren-energy-prototype-20261108/fixed-v02/model.mjs';
const folder=new URL('.',import.meta.url),read=async name=>JSON.parse(await fs.readFile(new URL(name,folder),'utf8'));
const r=await read('chart-result.json');
const pb=await fs.readFile(new URL('../liuren-energy-prototype-20261108/fixed-v02/profile.json',folder)),p=JSON.parse(pb);
const f=extractFeatures(r.facts,{seasonProfile:p.season_profile});
const m=buildCore(f,p),s=solveCore(m,p),a=actionLayer(m,s,p,r.shensha_resolution);
const yin=m.nodes.find(n=>n.id==='T:寅'),V=yin.base_ledger.adopted_retention;
const scenarios=[];
function runScenario(name,modifier){const q=structuredClone(m);modifier(q);const z=solveCore(q,p);scenarios.push({name,E_yin:z.values['T:寅'],difference:z.values['T:寅']-s.values['T:寅'],iterations:z.iterations,residual:z.residual});}
runScenario('取消天后直接生寅，保留其他距离及作用',q=>{q.edges=q.edges.filter(e=>!(e.source==='J:天后'&&e.target==='T:寅'&&e.type==='生'));});
runScenario('取消子水生寅，保留其他距离及作用',q=>{q.edges=q.edges.filter(e=>!(e.source==='T:子'&&e.target==='T:寅'&&e.type==='生'));});
runScenario('取消所有直接输入寅的生扶边，仍保留比和',q=>{q.edges=q.edges.filter(e=>!(e.target==='T:寅'&&e.type==='生'));});
runScenario('只撤寅坐空折损，不撤午自身旬空',q=>{const n=q.nodes.find(n=>n.id==='T:寅');n.base_ledger.adopted_retention=1;n.base=n.base_ledger.prevoid;});
runScenario('只撤午自身旬空折损，不撤寅坐空折损',q=>{const n=q.nodes.find(n=>n.id==='T:午');n.base_ledger.adopted_retention=1;n.base=n.base_ledger.prevoid;});
runScenario('同时撤午自身空与寅坐午空的折损',q=>{for(const id of ['T:午','T:寅']){const n=q.nodes.find(n=>n.id===id);n.base_ledger.adopted_retention=1;n.base=n.base_ledger.prevoid;}});
const ledger=s.ledger.filter(e=>e.target==='T:寅'||e.source==='T:寅').map(e=>({...e,delta_before_void:(e.target==='T:寅'?e.received:0)-(e.source==='T:寅'?e.source_cost:0)})).filter(e=>Math.abs(e.delta_before_void)>1e-12).map(e=>({...e,delta_after_void:e.delta_before_void*V}));
const alt=extractFeatures(r.facts,{seasonProfile:'quarter-earth'}),altModel=buildCore(alt,p),altSolution=solveCore(altModel,p);
const knownLimitations=[
 '寅午戌字齐，但午旬空且入火墓；通用三合协作1.1不能当作已证明的出行动力增益',
 '日支申冲寅未列入初版通用关系图；不能将其遗漏后的A认作完整驿马行动力',
 '子午冲、辰戌冲已有位置事实，但冲空、冲墓、救神受制的专项交互没有完整数值适配器',
 '天后生木可补气，不等于已填实地盘午或已解除驿马陷空；出行阶段未给，不判绝对无法出发',
 '当前坐空平方根折损及1分线未经案例校准；不能从超过1分反推陷空无需处理'
];
const hash=x=>createHash('sha256').update(x).digest('hex');
const result={research_only:true,chart:r.archive,profile_id:p.id,profile_sha256:hash(pb),features:f,
 nodes:m.nodes.map(n=>({...n,E:s.values[n.id]})),yin_ledger:ledger,solution:s,
 diagnostic_generic_action:a.rows.find(n=>n.id==='T:寅'),
 generic_action_status:'诊断旧通用公式输出，不是完整驿马出行效能，不据其超过1分裁可用',
 local_mechanisms:f.local_factors.filter(x=>['寅','戌','申','辰','午'].includes(x.participants.earth.slice(2))),
 scenarios,season_profile_sensitivity:{adopted:p.season_profile,adopted_yin_season:yin.season,adopted_yin_E:s.values['T:寅'],alternate:'quarter-earth',alternate_yin_season:altModel.nodes.find(n=>n.id==='T:寅').season,alternate_yin_E:altSolution.values['T:寅'],note:'仅记录季土表差异影响，不按结果更换当前固定研究口径'},
 limitations:knownLimitations,complete_travel_action_model:false,predicted_departure:null,predictive_validation:false,
 profile_unchanged:hash(pb)===hash(await fs.readFile(new URL('../liuren-energy-prototype-20261108/fixed-v02/profile.json',folder)))};
await fs.writeFile(new URL('寅木力量与救制计算.json',folder),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({chart:r.archive,pillars:r.facts.pillars,base:yin.base_ledger,E:s.values['T:寅'],ledger:ledger.map(e=>({source:e.source,target:e.target,type:e.type,before:e.delta_before_void,after:e.delta_after_void})),scenarios,season_profile_sensitivity:result.season_profile_sensitivity,flags:result.limitations},null,2));
