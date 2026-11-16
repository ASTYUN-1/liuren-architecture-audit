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
 const results=[],candidates=[],methods=[],missingContext=[];
 for(const rule of registry.rules){
  if(rule.extended){
   const evaluated=evaluateReviewedRule(rule,{c,g,b,home,rows,u,t,at,above,on,point,group,x,used,mode});
   if(evaluated.status==='matched')results.push(evaluated.value);
   else if(evaluated.status==='conditional')candidates.push(evaluated.value);
   else if(evaluated.status==='method')methods.push(evaluated.value);
   else if(evaluated.status==='missing')missingContext.push({id:rule.id,law_number:rule.law_number,missing:evaluated.value.checks.filter(x=>x.met===null)});
   continue;
  }
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
 const evidenceIds=new Set([...results,...candidates,...methods].flatMap(r=>r.evidence_ids));
 return {schema:'liuren-basic-bifa-v2',release:registry.release,actual_mode:mode,
  binding:{geometry_sha256:sha(JSON.stringify({day,mode,rows,u,t})),context_sha256:sha(JSON.stringify({pillars:c.pillars,month_general:c.month_general,rule:c.nobleman?.rule,participants:c.participants,declared_life:c.declared_life,year_life_verified:c.year_life_verified,...(c.year_life?{year_life:c.year_life}:{})})),rules_sha256:BASIC_BIFA_RULES_SHA256,implementation_sha256:loadedBasicBifaSha256},
  coverage:{registered_structures:registry.rules.filter(r=>r.operation!=='method').length,registered_method_checks:methods.length,represented_laws:registry.law_review.length,all_registered_checked:true,all_100_laws_basic_reviewed:true,all_100_laws_complete:false,year_life_branches_checked:false,unavailable_context:missingContext},
  instruction:'已逐法核查百法的基本定义，非穷尽全部正变旁格。matches仅确认明列条件全真；conditional_candidates尚缺条件，不能称完整成格；method_checks为按问履行的分析核查，不是几何格。依本问类神、位置、旺衰空实、制救和阶段选用。标题不裁成败，包含及同位置条目不重复计证。第22依大全；空亡效力沿用U08，不按古文极端判辞推医学或隐私事实。',
  matches:results,
  conditional_candidates:candidates,method_checks:methods,
  evidence:registry.sources.flatMap(s=>s.excerpts.filter(e=>evidenceIds.has(e.id)).map(e=>({id:e.id,path:s.path,source_sha256:s.sha256,line_mode:s.line_mode,line_start:e.line_start,line_end:e.line_end}))),
  reference_module:'bifa-basic-evidence'};
}

// Tri-state evaluation: unknown input is never converted to a successful check.
// Efficacy, choice of relevant class spirit, and real-world outcomes stay with AI.
function evaluateReviewedRule(rule,z){
 const {c,g,b,home,rows,u,t,at,above,on,point,group,x,mode}=z;
 const checks=[],branches=new Set(),detail={};
 const check=(condition,met,actual)=>checks.push({condition,met:met===null?null:Boolean(met),actual:actual??null});
 const use=(...ss)=>ss.filter(s=>ZHI.includes(s)).forEach(s=>branches.add(s));
 const ix=s=>ZHI.indexOf(s),step=(s,n)=>ZHI[mod(ix(s)+n)];
 const relevant=[...new Set([u[0],u[2],...t])];
 const empty=s=>x.void_branches.includes(s)||x.void_branches.includes(at(s).di);
 const birth={木:'亥',火:'寅',土:'申',金:'巳',水:'申'};
 const bath={木:'子',火:'卯',土:'酉',金:'午',水:'酉'};
 const peak={木:'卯',火:'午',土:'子',金:'酉',水:'子'};
 const end={木:'申',火:'亥',土:'巳',金:'寅',水:'巳'};
 const death={木:'午',火:'酉',土:'卯',金:'子',水:'卯'};
 const fetal={木:['酉'],火:['子'],土:['子','午'],金:['卯'],水:['午']};
 const harm=(a,b)=>['子未','丑午','寅巳','卯辰','申亥','酉戌'].some(s=>a!==b&&s.includes(a)&&s.includes(b));
 const clash=(a,b)=>mod(ix(a)-ix(b))===6;
 // Directed three-punishment edges. Self-punishment remains a named branch.
 const punish=(a,b)=>({子:'卯',卯:'子',寅:'巳',巳:'申',申:'寅',丑:'戌',戌:'未',未:'丑',辰:'辰',午:'午',酉:'酉',亥:'亥'})[a]===b;
 const isSet=(ss,desired)=>new Set(ss).size===desired.length&&desired.every(s=>ss.includes(s));
 const head=x.xun[1],tail=step(head,9),tiger=on('白虎'),thief=on('玄武'),dragon=on('青龙');
 const month=ZHI.includes(c.pillars?.[1]?.[1])?c.pillars[1][1]:null;
 const year=ZHI.includes(c.pillars?.[0]?.[1])?c.pillars[0][1]:null;
 const season=month?['寅卯辰','巳午未','申酉戌','亥子丑'].findIndex(s=>s.includes(month)):null;
 const seasonElement=season===null?null:['木','火','金','水'][season];
 const live=month?step(month,-2):null,dead=month?step(month,4):null;
 const nobleTable=registry.nobleman_tables?.[c.nobleman?.rule];
 const gi=[...'甲乙丙丁戊己庚辛壬癸'].indexOf(g);
 const nobles=nobleTable?{day:nobleTable['昼贵'][gi],night:nobleTable['夜贵'][gi]}:null;
 const nobleValid=nobles&&on('贵人').tian===(mode==='昼贵'?nobles.day:nobles.night);
 const needNoble=()=>check('贵人取法已登记且与实际天乙坐标一致',nobles?!!nobleValid:null,{rule:c.nobleman?.rule,actual:on('贵人').tian,nobles});
 const hits=(label,ss)=>{check(label,ss.length>0,ss);use(...ss);};
 const pairRule=(a,ar,b,br)=>{check(a,ar[0],ar[1]);check(b,br[0],br[1]);use(u[0],u[2]);};
 switch(rule.operation){
  case 'bracket':{
   const s=u[rule.target==='stem'?0:2];check('初末分见所引神前后相邻支',isSet([t[0],t[2]],[step(s,-1),step(s,1)]),{center:s,initial:t[0],final:t[2]});use(s,t[0],t[2]);
   detail.order=t[0]===step(s,1)?'初前末后':'初后末前';break;
  }
  case 'curtain':needNoble();if(nobleValid){const s=mode==='昼贵'?nobles.night:nobles.day;check('另一贵人支临干',u[0]===s,{upper:u[0],curtain:s});use(s);}break;
  case 'usher':check('日鬼乘实际白虎',ke(tiger.tian,g),tiger);check('白虎临干',tiger.di===home,{di:tiger.di,home});use(tiger.tian);detail.same_action_as=['BF91-tiger','BF61-tomb'];break;
  case 'warrant':check('干上日鬼',ke(u[0],g),u[0]);check('三传合财局生鬼',!!group&&ke(g,group.element)&&sheng(group.element,u[0]),group);use(u[0],...t);detail.role_required='赴任/官职语境，不能按鬼名自动断祸';break;
  case 'lu-strong':check('本法特准阴干旺禄/己土禄临干',!!({乙:'卯',丁:'午',己:'午',辛:'酉',癸:'子'}[g])&&u[0]===lu[g],{stem:g,upper:u[0],lu:lu[g]});use(u[0]);detail.closed_mouth=u[0]===tail;break;
  case 'lu-branch':check('支上为日禄',u[2]===lu[g],{upper:u[2],lu:lu[g]});use(u[2]);break;
  case 'wheel':case 'rotten':check('卯加申且发用',at('卯').di==='申'&&t[0]==='卯',{di:at('卯').di,initial:t[0]});if(rule.operation==='rotten')check('卯自空',x.void_branches.includes('卯'),x.void_branches);use('卯');detail.ground_void=x.void_branches.includes('申');break;
  case 'rescue':{
   const ghosts=relevant.filter(s=>ke(s,g)),children=relevant.filter(s=>sheng(g,s));
   check('相关位置见日鬼',ghosts.length>0,ghosts);check('相关位置子孙能克已见鬼',children.some(s=>ghosts.some(h=>ke(s,h))),children);use(...ghosts,...children);
   detail.relations=children.flatMap(s=>ghosts.filter(h=>ke(s,h)).map(h=>({rescuer:s,target:h,rescuer_void:empty(s),target_void:empty(h),rescuer_ground:at(s).di,restrained:ke(at(s).di,s)})));
   detail.restriction='有制关系不等于有效救解；依位置、空实与U06/U08判断。';break;
  }
  case 'group-parent':check('三传合鬼局',!!group&&ke(group.element,g),group);hits('干支上父母承接鬼局之生',[u[0],u[2]].filter(s=>group&&sheng(group.element,s)&&sheng(s,g)));use(...t);break;
  case 'fox':check('干上为日鬼或脱气',ke(u[0],g)||sheng(g,u[0]),{upper:u[0],kin:kin(g,u[0])});check('干寄宫克制干上神',ke(home,u[0]),{home,upper:u[0]});use(u[0]);break;
  case 'ghost-season':check('三传合鬼局',!!group&&ke(group.element,g),group);check('鬼局当四时旺',season===null?null:group?.element===seasonElement,{month,season_element:seasonElement});use(...t);break;
  case 'wealth-season':check('三传合财局',!!group&&ke(g,group.element),group);check('财局当四时旺或相',season===null?null:!!group&&(group.element===seasonElement||sheng(seasonElement,group.element)),{month,season_element:seasonElement});use(...t);detail.restriction='未核日主承受与财之真实作用，不能把旺相财局直接判财亏。';break;
  case 'double-drain':check('干生干上',sheng(g,u[0]),[g,u[0]]);check('干上生乘将',sheng(u[0],at(u[0]).tianjiang),[u[0],at(u[0]).tianjiang]);use(u[0]);break;
  case 'drain-thief':check('干上脱气乘玄武',sheng(g,u[0])&&at(u[0]).tianjiang==='玄武',point(u[0]));use(u[0]);break;
  case 'advance-void':case 'retreat-void':{
   const delta=rule.operation==='advance-void'?1:-1;check('三传逐支'+(delta===1?'进':'退'),t[1]===step(t[0],delta)&&t[2]===step(t[1],delta),t);check('至少一传空陷',t.some(empty),t.filter(empty));use(...t);detail.all_transmissions_void=t.every(empty);detail.restriction='方向与空陷已核；进退建议须另比较可走路径。';break;
  }
  case 'fetus':{
   const f=fetal[element(rule.side==='stem'?g:b)],ss=relevant.filter(s=>f.includes(s)&&(rule.side==='branch'||ke(g,s)));
   hits('相关位置见指定胎神'+(rule.side==='stem'?'且作日财':''),ss);
   const target=rule.dead?dead:live;check(rule.dead?'胎兼月死气':'胎兼月生气',month===null?null:ss.includes(target),{month,target,fetus:f});detail.restriction='仅胎爻组合，不能凭此确认现实怀孕或医学结局；孕产阶段须核。';break;
  }
  case 'metal-ding':check('庚辛日',element(g)==='金',g);hits('旬丁见干支上或三传',relevant.filter(s=>at(s).xungan==='丁'));break;
  case 'ghost-wealth':{
   const real=t.filter(s=>!empty(s));check('三传合鬼局',!!group&&ke(group.element,g),group);check('两空陷一实财',t.filter(empty).length===2&&real.length===1&&ke(g,real[0]),{empty:t.filter(empty),real});use(...t);break;
  }
  case 'group-house-drain':case 'group-stem-drain':{
   const reverse=rule.operation==='group-stem-drain';check('三传合局',!!group,group);check('局生一方并泄另一方',!!group&&sheng(group.element,reverse?b:g)&&sheng(reverse?g:b,group.element),{group,stem:g,branch:b});use(...t);break;
  }
  case 'birth-tomb':check('初末分别为日五行'+(rule.reverse?'墓、生':'生、墓'),t[0]===(rule.reverse?tomb:birth)[element(g)]&&t[2]===(rule.reverse?birth:tomb)[element(g)],{initial:t[0],final:t[2],birth:birth[element(g)],tomb:tomb[element(g)]});use(t[0],t[2]);break;
  case 'ghost-child':check('初传日鬼',ke(t[0],g),kin(g,t[0]));check('末传子孙克初鬼',sheng(g,t[2])&&ke(t[2],t[0]),kin(g,t[2]));use(t[0],t[2]);break;
  case 'two-edged':check('戊日伏吟且巳申寅',g==='戊'&&rows.every(r=>r.di===r.tian)&&t.join('')==='巳申寅',{day:c.pillars[2],t});use(...t);break;
  case 'upper-pair':{
   const refs=rule.cross?[b,g]:[g,b],symbols=[u[0],u[2]],rel=rule.relation;
   symbols.forEach((s,i)=>check((i===0?'干上':'支上')+'对'+(i===0?(rule.cross?'日支':'日干'):(rule.cross?'日干':'日支'))+'为'+rule.name,
    rel==='drain'?sheng(refs[i],s):rel==='attack'?ke(s,refs[i]):s===({bath,peak,end,death,tomb}[rel])[element(refs[i])],{upper:s,reference:refs[i],basis:'本法五行十二气'}));use(...symbols);break;
  }
  case 'tail-head':check('旬尾加旬首',at(tail).di===head,{head,tail,tail_ground:at(tail).di});use(tail);detail.is_initial=t[0]===tail;detail.with_thief=at(tail).tianjiang==='玄武';break;
  case 'head-thief':check('天盘旬首乘玄武',at(head).tianjiang==='玄武',point(head));use(head);detail.definition_source='北海第38法第2支';break;
  case 'ground-head-thief':check('地盘旬首上神乘玄武',thief.di===head,{head,thief});use(thief.tian);detail.definition_source='大全第38法地盘旬首取法';break;
  case 'closed-lu':check('日禄为旬尾',lu[g]===tail,{lu:lu[g],tail});use(lu[g]);detail.restriction='大全明确此旁格可就天盘查，不因每盘有旬尾泛称闭口成格。';break;
  case 'closed-wealth':check('旬尾为日财并见干支上或三传',ke(g,tail)&&relevant.includes(tail),{tail,kin:kin(g,tail),relevant});use(tail);break;
  case 'sun-thief':{
   const sun=ZHI.includes(c.month_general)?c.month_general:null,relations={carrier:thief.tian,ground:thief.di,yin:above(thief.tian)};
   check('月将已知',sun?true:null,sun);check('玄武乘、临、阴神中见月将',sun?Object.values(relations).includes(sun):null,relations);
   check('实际太阳日照条件核实',null,'需当时当地真实日出日入；贵人昼夜设置不能替代此条件');use(thief.tian,sun);detail.daquan_direct_ground=sun?thief.di===sun:null;break;
  }
  case 'queen-match':check('两上分乘后合',isSet([at(u[0]).tianjiang,at(u[2]).tianjiang],['天后','六合']),[at(u[0]).tianjiang,at(u[2]).tianjiang]);use(u[0],u[2]);break;
  case 'queen-trans':check('三传同见天后六合',t.some(s=>at(s).tianjiang==='天后')&&t.some(s=>at(s).tianjiang==='六合'),t.map(s=>at(s).tianjiang));use(...t);detail.order=t.map(s=>at(s).tianjiang);break;
  case 'three-wonders':{
   const start=[0,2,4,6,8][gi%5],letters=[...'甲乙丙丁戊己庚辛壬癸'];
   const stems=t.map(s=>rule.mode==='xun'?at(s).xungan:letters[(start+ix(s))%10]);
   check('单一遁法集齐三奇',isSet(stems,[...'甲戊庚'])||isSet(stems,[...'乙丙丁']),{mode:rule.mode,stems});use(...t);break;
  }
  case 'harm-noble':check('实际贵临干',on('贵人').di===home,on('贵人'));check('初传害干上贵',harm(t[0],on('贵人').tian),[t[0],on('贵人').tian]);use(t[0],u[0]);break;
  case 'crowd-noble':case 'cover-noble':{
   needNoble();if(nobleValid){check('干支上分两贵',isSet([u[0],u[2]],[nobles.day,nobles.night]),{uppers:[u[0],u[2]],nobles});
    if(rule.operation==='crowd-noble')check('初中又分两贵',isSet(t.slice(0,2),[nobles.day,nobles.night]),t.slice(0,2));use(u[0],u[2],...t.slice(0,2));}break;
  }
  case 'stack-noble':needNoble();if(nobleValid){const top=[nobles.day,nobles.night].filter(s=>at(s).di===(s===nobles.day?nobles.night:nobles.day)&&relevant.includes(s));hits('两贵天地相加且上贵见相关位置',top);}break;
  case 'mismatch-noble':needNoble();if(nobleValid){check('昼贵临夜方','酉戌亥子丑寅'.includes(at(nobles.day).di),at(nobles.day).di);check('夜贵临昼方','卯辰巳午未申'.includes(at(nobles.night).di),at(nobles.night).di);use(nobles.day,nobles.night);}break;
  case 'noble-ghost':check('实际贵所乘为日鬼且见相关位置',ke(on('贵人').tian,g)&&relevant.includes(on('贵人').tian),on('贵人'));use(on('贵人').tian);break;
  case 'noble-restrained':case 'noble-void':needNoble();if(nobleValid)for(const [k,s] of Object.entries(nobles)){check(k+'贵'+(rule.operation==='noble-void'?'自空或坐空':'受地盘克'),rule.operation==='noble-void'?empty(s):ke(at(s).di,s),point(s));use(s);}break;
  case 'snake-tomb':check('日五行墓加巳乘蛇',at(tomb[element(g)]).di==='巳'&&at(tomb[element(g)]).tianjiang==='腾蛇',point(tomb[element(g)]));use(tomb[element(g)]);detail.on_stem=at(tomb[element(g)]).di===home;break;
  case 'tiger-star':check('柔日',gi%2===1,g);check('本盘昴星（北海虎视）',Array.isArray(c.chart_types)?c.chart_types.some(s=>s.includes('昴星')||s==='虎视'):null,c.chart_types);check('实际白虎见课传',relevant.includes(tiger.tian),tiger);use(tiger.tian,...t);break;
  case 'net':{const targets=rule.cross?[step(b,1),step(home,1)]:[step(home,1),step(b,1)];check('干上对应罗网',u[0]===targets[0],{upper:u[0],target:targets[0]});check('支上对应罗网',u[2]===targets[1],{upper:u[2],target:targets[1]});use(u[0],u[2]);detail.chong_relief_candidates=targets.map(s=>({net:s,opposite:step(s,6),related_present:relevant.includes(step(s,6))}));break;}
  case 'life-net':{
   check('日五行墓临干',u[0]===tomb[element(g)],{upper:u[0],tomb:tomb[element(g)]});
   // Existing transport does not assert a principal-person identity or verified
   // declaration. Never bind any arbitrary participant to "self".
   check('本人已核本命与墓同支',null,'需占人本人已核本命及身份绑定；当前盘字段不证明这一对应');use(u[0]);break;
  }
  case 'cost':{const gains=[u[0],u[2]].filter(s=>sheng(s,g)&&empty(s)),costs=[...new Set([...u,...t])].filter(s=>ke(s,g)||sheng(g,s));hits('干支上生我者空陷',gains);hits('四课三传见鬼或脱',costs);detail.real_cost_branches=costs.filter(s=>!empty(s));detail.costs_all_empty=costs.every(empty);detail.restriction='原例丙午之二四课鬼坐空，不能因古文总括称实；位置与空实随点交接，效力仍需核。';break;}
  case 'broken-use':{
   const initial=t[0],useful=ke(g,initial)||sheng(initial,g)||initial===lu[g],clamped=ke(at(initial).di,initial)&&ke(at(initial).tianjiang,initial);
   check('初财禄生气空陷或夹克',useful&&(empty(initial)||clamped),point(initial));check('中末各为鬼脱或空陷',t.slice(1).every(s=>empty(s)||ke(s,g)||sheng(g,s)),t.slice(1).map(s=>({s,kin:kin(g,s),empty:empty(s)})));use(...t);break;
  }
  case 'canopy':{
   const canopy=['申子辰','寅午戌','巳酉丑','亥卯未'].map((s,i)=>s.includes(b)?['辰','戌','丑','未'][i]:null).find(Boolean);
   check('华盖兼日五行墓',canopy===tomb[element(g)],{canopy,tomb:tomb[element(g)]});check('华盖临干且发用',u[0]===canopy&&t[0]===canopy,{upper:u[0],initial:t[0]});use(canopy);break;
  }
  case 'sun-house':check('月将临支',ZHI.includes(c.month_general)?u[2]===c.month_general:null,{sun:c.month_general,upper:u[2]});use(u[2]);detail.light_condition='仍须按事件及太阳方位取义';break;
  case 'house-tomb-tiger':check('白虎临支',tiger.di===b,tiger);check('虎乘干墓或支墓',tiger.tian===tomb[element(g)]||tiger.tian===tomb[element(b)],{carrier:tiger.tian,stem_tomb:tomb[element(g)],branch_tomb:tomb[element(b)]});use(tiger.tian);detail.also_ke_house=ke(tiger.tian,b);detail.is_month_general=tiger.tian===c.month_general;detail.restriction='月将例外及空实仍核；不能由本名断言伏尸或现实死亡。';break;
  case 'mutual-attack':pairRule('干上克支',[ke(u[0],b),[u[0],b]],'支上克干',[ke(u[2],g),[u[2],g]]);break;
  case 'separation':pairRule('干克支上',[ke(g,u[2]),[g,u[2]]],'支克干上',[ke(b,u[0]),[b,u[0]]]);break;
  case 'season-gate':check('日墓发用',t[0]===tomb[element(g)],{initial:t[0],tomb:tomb[element(g)]});check('发用兼本季关神',season===null?null:t[0]===['丑','辰','未','戌'][season],{month,gate:season===null?null:['丑','辰','未','戌'][season]});use(t[0]);detail.initial_lessons=u.flatMap((s,i)=>s===t[0]?[i+1]:[]);detail.restriction='仓库类及旺为库按原文取义；与S33同一位置不重复计证。';break;
  case 'house-wealth-tomb':check('初传为支墓且日财',t[0]===tomb[element(b)]&&ke(g,t[0]),{initial:t[0],branch_tomb:tomb[element(b)],kin:kin(g,t[0])});use(t[0]);break;
  case 'tiger-carrier':check('实际白虎见相关位置',relevant.includes(tiger.tian),tiger);use(tiger.tian);detail.carrier_element=element(tiger.tian);detail.element_restrained_by_carrier={木:'土',火:'金',土:'水',金:'木',水:'火'}[element(tiger.tian)];detail.restriction='使用虎所乘支五行，不拿白虎将金替代；只给取类关系，不输出病名或治疗方案。';break;
  case 'illness':check('岁支已知',year?true:null,year);check('岁病符临支且克支',year?u[2]===step(year,-1)&&ke(u[2],b):null,{year,illness:year?step(year,-1):null,upper:u[2]});use(u[2]);break;
  case 'mourning':check('岁支已知',year?true:null,year);check('丧吊全见干支上或三传',year?relevant.includes(step(year,2))&&relevant.includes(step(year,-2)):null,{year,mourning:year?[step(year,2),step(year,-2)]:null});if(year)use(step(year,2),step(year,-2));break;
  case 'return-clamp':{const lower=t[0]===u[0]?g:at(t[0]).di;check('初传受所临下位克（临干用日干）',ke(lower,t[0]),{lower,initial:t[0],ground:at(t[0]).di});check('初回本宫又受上神克',ke(above(t[0]),t[0]),{home:t[0],upper:above(t[0])});use(t[0],above(t[0]));break;}
  case 'all-void':check('三传各空陷',t.every(empty),t.map(s=>point(s)));use(...t);break;
  case 'sky-void':check('三传两空陷余一乘天空',t.filter(empty).length===2&&t.filter(s=>!empty(s)).every(s=>at(s).tianjiang==='天空'),t.map(s=>point(s)));use(...t);break;
  case 'lessons-void':check('四课各空陷',u.every(empty),u.map(s=>point(s)));use(...u);break;
  case 'two-punish':check('两上分见子卯',isSet([u[0],u[2]],[...'子卯']),[u[0],u[2]]);use(u[0],u[2]);break;
  case 'three-punish':check('三传集齐三刑',isSet(t,[...'寅巳申'])||isSet(t,[...'丑戌未']),t);use(...t);break;
  case 'self-punish':check('四课上皆逢自刑支',u.every(s=>'辰午酉亥'.includes(s)),u);use(...u);detail.restriction='这是大全一字刑分支；不等于每个同支重复都已发生同一现实事件。';break;
  case 'harm':{
   let pairs=[];
   if(rule.mode==='each')pairs=[[home,u[0]],[b,u[2]]];
   if(rule.mode==='upper')pairs=[[u[0],u[2]]];
   if(rule.mode==='base-upper')pairs=[[home,b],[u[0],u[2]]];
   if(rule.mode==='trans')pairs=[[t[0],t[1]],[t[1],t[2]]];
   if(rule.mode==='cross')pairs=[[u[0],b],[u[2],home]];
   pairs.forEach(([a,b],i)=>check('第'+(i+1)+'对六害',harm(a,b),[a,b]));use(...pairs.flat());break;
  }
  case 'tomb-chain':check('中为初墓',t[1]===tomb[element(t[0])],{initial:t[0],middle:t[1],initial_tomb:tomb[element(t[0])]});check('末坐中墓地',at(t[2]).di===t[1],{final:t[2],ground:at(t[2]).di,middle:t[1]});use(...t);detail.initial_kin=kin(g,t[0]);break;
  case 'stop':check('初传自支坐地皆实',!empty(t[0]),point(t[0]));check('中末皆空陷',t.slice(1).every(empty),t.slice(1).map(s=>point(s)));use(...t);break;
  case 'break-union':{
   check('三传三合局',!!group,group);const rs=group?[u[0],u[2]].flatMap(s=>['刑','冲','害'].filter(k=>k==='刑'?(punish(s,group.middle)||punish(group.middle,s)):k==='冲'?clash(s,group.middle):harm(s,group.middle)).map(k=>({upper:s,middle:group.middle,relation:k}))):[];
   check('局中神与干支上刑冲害',rs.length>0,rs);use(...t,...rs.map(r=>r.upper));break;
  }
  case 'seat-tomb':{
   const refs=rule.cross?[b,g]:[g,b];[home,b].forEach((s,i)=>check((i===0?'天盘干寄宫':'天盘日支')+'坐指定墓',at(s).di===tomb[element(refs[i])],{tian:s,ground:at(s).di,reference:refs[i],tomb:tomb[element(refs[i])]}));use(home,b);break;
  }
  case 'moving':check('天地盘伏吟',rows.every(r=>r.tian===r.di),rows[0]);hits('相关位置见旬丁或日马',relevant.filter(s=>at(s).xungan==='丁'||s===horse(b)||c.heaven_earth.find(r=>r.tian===s)?.shensha?.some(v=>v[0]==='S04')));break;
  case 'empty-return':check('天地盘返吟',rows.every(r=>clash(r.tian,r.di)),rows[0]);check('三传全空陷',t.every(empty),t.map(s=>point(s)));use(...t);break;
  case 'dragon':check('青龙乘神生干且见相关位置',sheng(dragon.tian,g)&&relevant.includes(dragon.tian),dragon);if(rule.strict)check('兼月生气',month===null?null:dragon.tian===live,{month,live});use(dragon.tian);detail.also_month_life=month===null?null:dragon.tian===live;detail.daquan_complete=month?dragon.tian===live:null;break;
  case 'kin-group':check('三传三合局',!!group,group);if(group){detail.group_kin=kin(g,group.element);detail.upper_relations=[u[0],u[2]].map(s=>({upper:s,kin:kin(g,s),group_to_upper:fiveRelation(group.element,s),upper_to_day:fiveRelation(s,g),void:empty(s)}));}use(...t,u[0],u[2]);detail.restriction='被克类神必须与本问相关且真实出现，仍核旺衰制救；不能按局名断某亲属遭灾。';break;
  case 'finish':check('干上五行绝且鬼或财',u[0]===end[element(g)]&&(ke(u[0],g)||ke(g,u[0])),{upper:u[0],end:end[element(g)],kin:kin(g,u[0])});use(u[0]);break;
  case 'earth-conflict':check('壬癸日',element(g)==='水',g);check('初末土鬼互冲',element(t[0])==='土'&&element(t[2])==='土'&&clash(t[0],t[2]),[t[0],t[2]]);use(t[0],t[2]);detail.restriction='灾讼与升迁之喜惧相反，冲鬼不保证一概吉利。';break;
  case 'method':{
   use(...relevant);detail.required_analysis=rule.definition;
   if(rule.law_number===9)detail.routes=[{role:'干上',branch:u[0]},{role:'支上',branch:u[2]},{role:'天盘干寄宫',branch:home},...t.map((s,i)=>({role:['初传','中传','末传'][i],branch:s}))].map(r=>({...r,kin:kin(g,r.branch),point:point(r.branch)}));
   if([94,96].includes(rule.law_number)){
    branches.clear();const ss=rule.law_number===96?x.void_branches:relevant;use(...ss);
    detail.role_facts=ss.map(s=>({branch:s,kin:kin(g,s),void_self:x.void_branches.includes(s),void_ground:x.void_branches.includes(at(s).di),ground_to_spirit:fiveRelation(at(s).di,s),yin_to_spirit:fiveRelation(above(s),s),is_lu:s===lu[g]}));
   }
   if(rule.law_number===97)detail.requires=['依问取类神','查干支上/三传/已核年命的主类神位置','分成败问与具体情状问','不入时按占类决定天地盘补查及权重'];
   if(rule.law_number===100)detail.source_disagreement='大全以已灾后的凶课概括可消灾；北海明确否认该保证。暂停此概括自动判辞，仅保留阶段核查与明确定义的基本结构。';
   return {status:'method',value:{...rule,check_kind:'reasoning_required',checks:[{condition:'本法属于按问推理核查，程序不宣布完成',met:null,actual:rule.definition}],points:[...branches].map(point),...detail}};
  }
  default:throw Error('BIFA: unimplemented reviewed operation '+rule.operation);
 }
 const value={...rule,checks,points:[...branches].map(point),...detail};
 if(checks.some(r=>r.met===false))return {status:'not_matched',value};
 if(checks.some(r=>r.met===null))return {status:checks.some(r=>r.met===true)?'conditional':'missing',value};
 if(!checks.length)throw Error('BIFA: missing checks '+rule.id);
 return {status:'matched',value};
}
