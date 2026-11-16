// Closed, source-backed structural scanner. It neither uses native Bifa labels
// nor decides whether a relation is effective or a real-world event succeeds.
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {ZHI,GENERALS,HOMES,xunFacts,element,fiveRelation,kin} from './liuren-deterministic.mjs';
const sha=v=>createHash('sha256').update(v).digest('hex');
const raw=await fs.readFile(new URL('./liuren-bifa-basic-rules.json',import.meta.url),'utf8');
const registry=JSON.parse(raw);
export const BASIC_BIFA_RULES_SHA256=sha(raw);
export const loadedBasicBifaSha256=sha(await fs.readFile(new URL(import.meta.url)));
const knownEvidence=new Set(registry.sources.flatMap(s=>s.excerpts.map(e=>e.id)));
if(registry.sources.some(s=>s.excerpts.some(e=>!e.quote?.trim()))||registry.rules.some(r=>!r.evidence_ids.every(id=>knownEvidence.has(id))))throw Error('BIFA: empty or missing source evidence');
export const basicBifaCatalog=()=>structuredClone(registry.rules);
const sheng=(a,b)=>a!=='空'&&b!=='空'&&fiveRelation(a,b)==='生';
const ke=(a,b)=>a!=='空'&&b!=='空'&&fiveRelation(a,b)==='克';
const he=(a,b)=>['子丑','寅亥','卯戌','辰酉','巳申','午未'].some(s=>s.includes(a)&&s.includes(b)&&a!==b);
const mod=n=>(n%12+12)%12;
const canonical=s=>s==='螣蛇'?'腾蛇':s;
const horse=b=>['申子辰','寅午戌','巳酉丑','亥卯未'].map((s,i)=>s.includes(b)?['寅','申','亥','巳'][i]:null).find(Boolean);
const tomb={木:'未',火:'戌',土:'辰',金:'丑',水:'辰'};
const lu={甲:'寅',乙:'卯',丙:'巳',丁:'午',戊:'巳',己:'午',庚:'申',辛:'酉',壬:'亥',癸:'子'};
const fail=m=>{throw Error('BIFA: '+m);};

export function scanBasicBifa(c){
 const mode=c.nobleman?.zhouye;
 if(!['昼贵','夜贵'].includes(mode))fail('actual noble mode required');
 const day=c.pillars?.[2],x=xunFacts(day),g=day[0],b=day[1],home=HOMES[g];
 if(c.void_branches&&JSON.stringify([...c.void_branches].sort())!==JSON.stringify([...x.void_branches].sort()))fail('void/day mismatch');
 const rows=c.heaven_earth?.map(r=>({di:r.di,tian:r.tian,tianjiang:canonical(r.tianjiang),xungan:x.xungan[r.tian]}));
 if(rows?.length!==12||new Set(rows.map(r=>r.tian)).size!==12||new Set(rows.map(r=>r.di)).size!==12||new Set(rows.map(r=>r.tianjiang)).size!==12||rows.some(r=>!ZHI.includes(r.tian)||!ZHI.includes(r.di)||!GENERALS.includes(r.tianjiang)))fail('complete chart coordinates required');
 if(new Set(rows.map(r=>mod(ZHI.indexOf(r.tian)-ZHI.indexOf(r.di)))).size!==1)fail('plate rotation mismatch');
 const at=s=>rows.find(r=>r.tian===s),above=s=>rows.find(r=>r.di===s)?.tian,on=j=>rows.find(r=>r.tianjiang===j);
 const lessons=c.lessons??[],trans=c.transmissions??[],u=lessons.map(r=>r.tianpan),t=trans.map(r=>r.diZhi);
 if(u.length!==4||t.length!==3||[...u,...t].some(s=>!ZHI.includes(s)))fail('complete lessons/transmissions required');
 if(u[0]!==above(home)||u[1]!==above(u[0])||u[2]!==above(b)||u[3]!==above(u[2]))fail('lesson coordinates mismatch');
 if([...lessons.map(r=>[r.tianpan,r.tianjiang]),...trans.map(r=>[r.diZhi,r.tianjiang])].some(([s,j])=>at(s).tianjiang!==canonical(j)))fail('lesson/transmission generals mismatch');
 const used=new Set([...u,...t]),noble=on('贵人'),tiger=on('白虎'),empty=on('天空');
 const group=[{members:'亥卯未',element:'木',middle:'卯'},{members:'寅午戌',element:'火',middle:'午'},
  {members:'巳酉丑',element:'金',middle:'酉'},{members:'申子辰',element:'水',middle:'子'}].find(a=>new Set(t).size===3&&t.every(s=>a.members.includes(s)));
 const fSheng=sheng(t[0],t[1])&&sheng(t[1],t[2]),rSheng=sheng(t[2],t[1])&&sheng(t[1],t[0]);
 const fKe=ke(t[0],t[1])&&ke(t[1],t[2]),rKe=ke(t[2],t[1])&&ke(t[1],t[0]);
 const positions=s=>[...u.flatMap((v,i)=>v===s?['第'+(i+1)+'课上神']:[]),...t.flatMap((v,i)=>v===s?[['初传','中传','末传'][i]]:[])];
 const point=s=>({...at(s),positions:positions(s),void_self:x.void_branches.includes(s),void_ground:x.void_branches.includes(at(s).di)});
 const results=[];
 for(const rule of registry.rules){
  const checks=[],branches=new Set();let detail={};
  const check=(condition,met,actual)=>checks.push({condition,met:Boolean(met),actual});
  const use=(...symbols)=>symbols.forEach(s=>branches.add(s));
  switch(rule.id){
   case 'BF02-boundary':{
    const head=x.xun[1],tail=ZHI[mod(ZHI.indexOf(head)+9)];
    check('干支上分见本旬旬首与旬尾',(u[0]===head&&u[2]===tail)||(u[0]===tail&&u[2]===head),{干上:u[0],支上:u[2],旬首:head,旬尾:tail});use(u[0],u[2]);break;
   }
   case 'BF02-return':t.forEach((s,i)=>check(['初','中','末'][i]+'传见四课上神',u.includes(s),s));use(...t);break;
   case 'BF05-yang':case 'BF06-yin':{
    const parity=rule.id==='BF05-yang'?0:1;check('四课上神与三传均为'+(parity?'阴':'阳')+'支',[...u,...t].every(s=>ZHI.indexOf(s)%2===parity),{四课:u,三传:t});use(...u,...t);break;
   }
   case 'BF16-empty':check('天空乘旬空',x.void_branches.includes(empty.tian),empty.tian);check('见四课或三传',used.has(empty.tian),positions(empty.tian));use(empty.tian);break;
   case 'BF21-cross':check('干支分宫',home!==b,{寄宫:home,支:b});check('干上与支六合',he(u[0],b),[u[0],b]);check('支上与干寄宫六合',he(u[2],home),[u[2],home]);use(u[0],u[2]);break;
   case 'BF22-main':check('干支上神六合',he(u[0],u[2]),[u[0],u[2]]);check('干寄宫与日支六合',he(home,b),[home,b]);use(u[0],u[2]);break;
   case 'BF22-vertical':check('干寄宫与干上六合',he(home,u[0]),[home,u[0]]);check('日支与支上六合',he(b,u[2]),[b,u[2]]);use(u[0],u[2]);break;
   case 'BF22-upper':check('仅干支上神六合',he(u[0],u[2]),[u[0],u[2]]);use(u[0],u[2]);detail={restriction:'只成立上神相合这一层，不能补足上下皆合主格'};break;
   case 'BF23-to-stem':case 'BF24-to-branch':{
    const toStem=rule.id==='BF23-to-stem';check('两上不同，可区分方向',u[0]!==u[2],{干上:u[0],支上:u[2]});
    check('初传在'+(toStem?'支':'干')+'上',t[0]===u[toStem?2:0],t[0]);check('末传在'+(toStem?'干':'支')+'上',t[2]===u[toStem?0:2],t[2]);use(t[0],t[2]);detail={restriction:'流向依占类确定双方，不自动等于求我或我求人'};break;
   }
   case 'BF26-ding':case 'BF26-horse':{
    const ding=rule.id==='BF26-ding';const hits=rows.filter(r=>ke(g,r.tian)&&(ding?r.xungan==='丁':r.tian===horse(b))&&used.has(r.tian));
    check(ding?'日财旬遁丁且见课传':'日财兼日驿马且见课传',hits.length>0,hits.map(r=>r.tian));use(...hits.map(r=>r.tian));detail={restriction:'只报告财与丁/日驿马同支；不直接断得财、远行或水日财动正格全部成立'};break;
   }
   case 'BF27-drain':check('三传三合成局',Boolean(group),group?.members??t);check('日干生合局',Boolean(group)&&sheng(g,group.element),group?.element??null);use(...t);detail={restriction:'只是传脱分支，不是传财化鬼正格；三合成象不代表已数值合化'};break;
   case 'BF31-chain':case 'BF32-chain':{
    const birth=rule.id==='BF31-chain',f=birth?fSheng:fKe,r=birth?rSheng:rKe,end=f?t[2]:r?t[0]:null;
    check(birth?'初生中生末或末生中生初':'初克中克末或末克中克初',f||r,t);use(...t);
    detail={direction:f?'初→中→末':r?'末→中→初':null,endpoint:end,endpoint_to_day:end?fiveRelation(end,g):null,endpoint_kin:end?kin(g,end):null,
     daquan_complete_chain:Boolean(end)&&(birth?sheng(end,g):ke(end,g)),restriction:'北海递生/递克结构与《大全》终点到干条件分层；不由标题断举荐、欺凌或成败'};break;
   }
   case 'BF37-assist':check('末传生初传',sheng(t[2],t[0]),[t[2],t[0]]);use(t[2],t[0]);detail={initial_kin:kin(g,t[0]),restriction:'按初传财/鬼/父等及空实、所求所忧判断，不一律当助力'};break;
   case 'BF41-luma':check('干上为支驿马',u[0]===horse(b),{干上:u[0],支马:horse(b)});check('支上为干禄',u[2]===lu[g],{支上:u[2],干禄:lu[g]});use(u[0],u[2]);break;
   case 'BF47-prison':{
    const prison=['辰','戌'].includes(noble.di),body=prison&&['乙','辛'].includes(g)&&noble.di===home,house=prison&&noble.di===b;
    check('实际贵人临地盘辰戌',prison,noble);use(noble.tian);detail={branch:body?'贵人临身':house?'贵人入宅':'贵人入狱',exception_body:body,exception_house:house,restriction:'临身/入宅与普通入狱分开；不由标题补出宜投贵结论'};break;
   }
   case 'BF51-gate':check('戌加亥',at('戌').di==='亥',at('戌').di);check('戌发用',t[0]==='戌',t[0]);use('戌');break;
   case 'BF52-gate':check('辰加寅',at('辰').di==='寅',at('辰').di);use('辰');detail={restriction:'原段不论入传与否；不是任意谋事必成的开关'};break;
   case 'BF61-tomb':check('白虎乘日五行墓',tiger.tian===tomb[element(g)],{白虎:tiger.tian,五行墓:tomb[element(g)]});check('墓虎临干寄宫',tiger.di===home,{地盘:tiger.di,寄宫:home});use(tiger.tian);detail={restriction:'本段五行墓取类不改U04阴干十二长生；不由单格作生死判断'};break;
   case 'BF69-hidden':check('白虎乘支旬遁干克日',ke(tiger.xungan,g),{乘支:tiger.tian,旬干:tiger.xungan,日干:g});check('见课传',used.has(tiger.tian),positions(tiger.tian));use(tiger.tian);break;
   case 'BF69-plain-hidden':case 'BF69-hidden-plain':{
    const direct=rule.id==='BF69-plain-hidden',light=u[direct?0:2],dark=u[direct?2:0];
    check('明鬼支克日干',ke(light,g),{支:light,日干:g});check('暗鬼旬遁干克日干',ke(at(dark).xungan,g),{支:dark,旬干:at(dark).xungan,日干:g});use(light,dark);detail={restriction:'明暗二鬼分支不等于白虎乘遁鬼正格成立'};break;
   }
   case 'BF70-two':check('第三课上神为日鬼',ke(u[2],g),u[2]);check('第四课上神为日鬼',ke(u[3],g),u[3]);use(u[2],u[3]);break;
   case 'BF77-cross':check('干上生日支',sheng(u[0],b),[u[0],b]);check('支上生日干',sheng(u[2],g),[u[2],g]);use(u[0],u[2]);break;
   case 'BF77-each':check('干上生日干',sheng(u[0],g),[u[0],g]);check('支上生日支',sheng(u[2],b),[u[2],b]);use(u[0],u[2]);break;
   case 'BF83-call':{
    const responders=group?[u[0],u[2]].filter(s=>he(s,group.middle)):[];
    check('三传三合局',Boolean(group),group?.members??t);check('合局中神与干上或支上六合',responders.length>0,{中神:group?.middle??null,呼应上神:responders});use(...t,...responders);break;
   }
   case 'BF85-clamp':check('地盘克初传',ke(at(t[0]).di,t[0]),[at(t[0]).di,t[0]]);check('所乘天将克初传',ke(at(t[0]).tianjiang,t[0]),[at(t[0]).tianjiang,t[0]]);use(t[0]);detail={initial_kin:kin(g,t[0]),restriction:'先看被夹克者对本问的作用；财受夹克与鬼受夹克不可一律断凶'};break;
   case 'BF86-internal':{
    const hits=rows.filter(r=>used.has(r.tian)&&ke(r.di,r.tian)&&ke(r.tian,r.tianjiang));
    check('课传支上地克神且神克将',hits.length>0,hits.map(r=>[r.di,r.tian,r.tianjiang]));use(...hits.map(r=>r.tian));detail={restriction:'内部矛盾候选，不由格名断所谋必危'};break;
   }
   case 'BF91-tiger':check('白虎乘神克日干',ke(tiger.tian,g),{乘支:tiger.tian,日干:g});check('见课传',used.has(tiger.tian),positions(tiger.tian));use(tiger.tian);detail={also_law61_tiger_on_stem:tiger.di===home,restriction:'与第61虎鬼加干同一作用不重复计证；病、官、行动等须依事取义'};break;
   default:fail('unimplemented registered rule '+rule.id);
  }
  if(checks.length&&checks.every(r=>r.met))results.push({...rule,checks,points:[...branches].map(point),...detail});
 }
 const evidenceIds=new Set(results.flatMap(r=>r.evidence_ids));
 return {schema:'liuren-basic-bifa-v1',release:registry.release,actual_mode:mode,
  binding:{geometry_sha256:sha(JSON.stringify({day,mode,rows,u,t})),rules_sha256:BASIC_BIFA_RULES_SHA256,implementation_sha256:loadedBasicBifaSha256},
  coverage:{registered_structures:registry.rules.length,represented_laws:new Set(registry.rules.map(r=>r.law_number)).size,all_registered_checked:true,all_100_laws_complete:false,year_life_branches_checked:false},
  instruction:'仅为已核基本结构，按本问类神、位置、旺衰空实、制救和阶段选用。成立关系不等于有效成格或标题断语兑现；相关条目不得重复计证。未列出不代表其他毕法不存在，偏僻/未核旁格暂不自动采用。',
  matches:results,
  evidence:registry.sources.flatMap(s=>s.excerpts.filter(e=>evidenceIds.has(e.id)).map(e=>({id:e.id,path:s.path,source_sha256:s.sha256,line_mode:s.line_mode,line_start:e.line_start,line_end:e.line_end}))),
  reference_module:'bifa-basic-evidence'};
}
