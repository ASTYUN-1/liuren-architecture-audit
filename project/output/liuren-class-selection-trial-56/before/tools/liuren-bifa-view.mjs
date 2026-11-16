// Deterministic presentation of verified matches. Source checks stay in the scanner.
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {scanBasicBifa,basicBifaCatalog} from './liuren-bifa-basic.mjs';
import {xunFacts} from './liuren-deterministic.mjs';

const hash=s=>createHash('sha256').update(s).digest('hex');
const raw=await fs.readFile(new URL('./liuren-bifa-statements.json',import.meta.url),'utf8');
const catalog=JSON.parse(raw);
export const BIFA_STATEMENTS_SHA256=hash(raw);
export const loadedBifaViewSha256=hash(await fs.readFile(new URL(import.meta.url)));
export const bifaStatementCatalog=()=>structuredClone(catalog);
const laws=new Map(catalog.laws.map(r=>[r.number,r]));
const rules=new Map(catalog.rules.map(r=>[r.id,r]));
const registered=basicBifaCatalog();
if(laws.size!==100||rules.size!==registered.length||registered.some(r=>
 !rules.has(r.id)||!laws.get(r.law_number)?.rules.includes(r.id)||
 rules.get(r.id).number!==r.law_number||!rules.get(r.id).imagery?.trim()||
 !rules.get(r.id).condition_template?.trim()))throw Error('BIFA_VIEW: incomplete fixed statement catalog');

const labels={
 center:'被引神',initial:'初传',final:'末传',stem:'日干',branch:'日支',upper:'上神',
 home:'寄宫',lu:'日禄',head:'旬首',tail:'旬尾',tail_ground:'旬尾所临地盘',
 di:'地盘',tian:'天盘',tianjiang:'天将',xungan:'旬干',day:'昼贵',night:'夜贵',
 nobles:'两贵',noble:'贵人',rule:'贵人取法',actual:'实际',uppers:'两上',
 month:'月建',season_element:'季旺五行',members:'合局三支',element:'五行',middle:'中神',
 group:'三合局',month_general:'月将',birth:'长生',tomb:'墓',fetus:'胎',target:'所查支',
 mode:'遁法',stems:'遁干',carrier:'乘支',ground:'地盘',yin:'阴神',
 kin:'六亲',empty:'空陷',real:'实处',canopy:'华盖',stem_tomb:'干墓',branch_tomb:'支墓',
 gate:'季关神',lower:'下位',reference:'所对干支',basis:'取法',s:'支',t:'三传',
 illness:'岁病符',year:'岁支',mourning:'丧吊',opposite:'冲支',
 thief:'玄武',curtain:'帘幕贵人',sun:'太阳月将',relation:'关系',end:'绝地',
 initial_tomb:'初传墓',relevant:'干支上及三传',
 live:'月生气',dead:'月死气',
};
const status=p=>[p.void_self?'旬空':'',p.void_ground?'坐空':''].filter(Boolean).join('、');
const position=p=>p.positions?.length?p.positions.join('、'):'天盘';
const pointText=(p,withPosition=true)=>`${withPosition?position(p):'天盘'}${p.tian}临地盘${p.di}乘${p.tianjiang}${status(p)?'（'+status(p)+'）':''}`;
function actualText(v){
 if(v===null||v===undefined)return '未提供';
 if(v===true)return '是';if(v===false)return '否';
 if(typeof v!=='object')return ({day:'昼贵',night:'夜贵','five-zi':'五子元遁',xun:'旬遁'})[v]??String(v);
 if(Array.isArray(v))return v.map(x=>actualText(x)).join('、');
 if(v.tian&&v.di&&v.tianjiang)return pointText(v,Boolean(v.positions));
 return Object.entries(v).map(([k,x])=>`${labels[k]??k}${actualText(x)}`).join('，');
}
const names=['第一课','第二课','第三课','第四课'];
function groupedLessons(c){
 const groups=new Map();
 for(const [i,l] of c.lessons.entries()){
  const key=l.tianpan;if(!groups.has(key))groups.set(key,[]);groups.get(key).push(i);
 }
 return [...groups].map(([s,indices])=>{
  const row=c.heaven_earth.find(r=>r.tian===s);
  const empty=[c.void_branches.includes(s)?'旬空':'',c.void_branches.includes(row.di)?'坐空':''].filter(Boolean).join('、');
  return `${indices.map(i=>names[i].replace('课','')).join('、')}课天盘${s}临地盘${row.di}，${empty}`;
 }).join('；');
}
const relationNames={生:'生干',被生:'受干生（脱干）',克:'克干',被克:'受干克（日财）',比和:'比和'};
function context(c,r){
 const points=r.points??[],rows=c.heaven_earth;
 const at=s=>rows.find(p=>p.tian===s);
 const tr=c.transmissions.map(t=>t.diZhi),up=c.lessons.map(l=>l.tianpan);
 const pt=s=>({...at(s),positions:[...up.flatMap((v,i)=>v===s?[names[i]]:[]),...tr.flatMap((v,i)=>v===s?[['初传','中传','末传'][i]]:[])],void_self:c.void_branches.includes(s),void_ground:c.void_branches.includes(at(s).di)});
 const tv=(s,i)=>`${['初传','中传','末传'][i]}天盘${s}临地盘${at(s).di}，${status(pt(s))||'支与坐地皆不空'}`;
 const facts=r.checks.filter(k=>k.met===true&&!k.condition.startsWith('贵人取法已登记')).map(k=>
  `${k.condition.replace(/^day贵/,'昼贵支').replace(/^night贵/,'夜贵支')}（${actualText(k.actual)}）`).join('；');
 return {
  核实条件:facts,落点:points.map(p=>pointText(p)).join('；'),
  四课:up.join('、'),三传:tr.join('→'),日柱:c.pillars[2],日干:c.pillars[2][0],
  干上:up[0],支上:up[2],干将:at(up[0]).tianjiang,支将:at(up[2]).tianjiang,
  初传:tr[0],中传:tr[1],末传:tr[2],初传地:at(tr[0]).di,
  初传六亲:r.initial_kin??at(tr[0]).liuqin,
  财丁位置:points.map(p=>`${position(p)}${p.tian}`).join('、'),
  财马位置:points.map(p=>`${position(p)}${p.tian}`).join('、'),
  后合位置:tr.flatMap((s,i)=>['天后','六合'].includes(at(s).tianjiang)?[`${['初传','中传','末传'][i]}${s}乘${at(s).tianjiang}`]:[]).join('，'),
  四课空陷:groupedLessons(c),三传空陷:tr.map(tv).join('；'),中末空陷:tr.map(tv).slice(1).join('；'),
  递向:r.direction,终点:r.endpoint,终点对干:relationNames[r.endpoint_to_day]??r.endpoint_to_day,
  内战位置:points.map(p=>`地盘${p.di}克天盘${p.tian}，${p.tian}克所乘${p.tianjiang}（${position(p)}）`).join('；'),
  虎乘五行:r.carrier_element,虎所克五行:r.element_restrained_by_carrier,
 };
}
function interpolate(template,ctx){
 return template.replace(/\{([^{}]+)\}/g,(_,key)=>{
  if(ctx[key]===null||ctx[key]===undefined||ctx[key]==='')throw Error('BIFA_VIEW: missing template value '+key);
  return ctx[key];
 });
}
function renderBranch(c,r){
 if(!r.checks?.length||r.checks.some(k=>k.met!==true))throw Error('BIFA_VIEW: non-matched rule '+r.id);
 const fixed=rules.get(r.id);if(!fixed)throw Error('BIFA_VIEW: unregistered rule '+r.id);
 const ctx=context(c,r);
 let conditions=interpolate(fixed.condition_template,ctx).replace(/；。/g,'。');
 // Void is a chart fact, not boilerplate. Retain it when a short custom template
 // did not spell out the coordinates affected by it.
 const voids=(r.points??[]).filter(p=>status(p)).map(p=>`${p.tian}临${p.di}${status(p)}`);
 if(voids.length&&!['BF74-lessons-void','BF74-all-void','BF82-stop'].includes(r.id)){
  const note=voids.join('、');if(!conditions.includes(note))conditions=conditions.replace(/。$/,'')+'；'+note+'。';
 }
 const selector=r.id==='BF47-prison'?r.branch:r.initial_kin;
 const imagery=catalog.variants[r.id]?.[selector]??fixed.imagery;
 return {name:fixed.name,conditions,imagery:interpolate(imagery,ctx)};
}

// No limit or ranking: all verified branches survive, grouped only by law.
export function bifaView(c){
 c={...c,void_branches:c.void_branches??xunFacts(c.pillars[2]).void_branches};
 const scan=scanBasicBifa(c),grouped=new Map();
 for(const r of scan.matches){
  if(!grouped.has(r.law_number))grouped.set(r.law_number,[]);
  grouped.get(r.law_number).push({rule:r,...renderBranch(c,r)});
 }
 return [...grouped].sort(([a],[b])=>a-b).map(([number,branches])=>{
  const law=laws.get(number);
  if(number===26&&branches.length===2){
   const ding=branches.find(b=>b.rule.id==='BF26-ding'),horse=branches.find(b=>b.rule.id==='BF26-horse');
   if(ding&&horse&&ding.rule.points.length===horse.rule.points.length&&ding.rule.points.every(p=>horse.rule.points.some(q=>q.tian===p.tian))){
    const fixed=catalog.combinations['BF26-ding-horse'],ctx=context(c,ding.rule);
    let conditions=interpolate(fixed.condition_template,ctx);
    const voids=ding.rule.points.filter(p=>status(p)).map(p=>`${p.tian}临${p.di}${status(p)}`);
    if(voids.length)conditions=conditions.replace(/。$/,'')+'；'+voids.join('、')+'。';
    return {条目:`毕法赋26：${law.title}（${fixed.name}）`,成格:conditions,意象:fixed.imagery};
   }
  }
  const conditionParts=branches.map(b=>branches.length===1?b.conditions:`${b.name}：${b.conditions}`);
  const imagery=[...new Set(branches.map(b=>b.imagery))].join('；');
  return {条目:`毕法赋${String(number).padStart(2,'0')}：${law.title}（${branches.map(b=>b.name).join('、')}）`,
   成格:conditionParts.join('；').replace(/。；/g,'；'),意象:imagery.replace(/。；/g,'；')};
 });
}
