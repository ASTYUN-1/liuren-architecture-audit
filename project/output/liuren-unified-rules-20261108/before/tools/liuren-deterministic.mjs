// Coordinate/lookup/arithmetic facts only. No outcome scoring or interpretation.
import {createHash} from 'node:crypto';
export const VERSION='liuren-deterministic-v1';
export const ZHI=[...'子丑寅卯辰巳午未申酉戌亥'];
export const GAN=[...'甲乙丙丁戊己庚辛壬癸'];
export const GENERALS=['贵人','腾蛇','朱雀','六合','勾陈','青龙','天空','白虎','太常','玄武','太阴','天后'];
const ELEMENTS=['木','火','土','金','水'];
const BRANCH_ELEMENT=['水','土','木','木','土','火','火','土','金','金','土','水'];
const STEM_ELEMENT=['木','木','火','火','土','土','金','金','水','水'];
const GENERAL_ELEMENT=['土','火','火','木','土','木','土','金','土','水','金','水'];
export const HOMES=Object.fromEntries(GAN.map((g,i)=>[g,[...'寅辰巳未巳未申戌亥丑'][i]]));
const STATES=['长生','沐浴','冠带','临官','帝旺','衰','病','死','墓','绝','胎','养'];
const START={木:'亥',火:'寅',土:'申',金:'巳',水:'申'};
const mod=(n,m=12)=>(n%m+m)%m;
export const hash=v=>createHash('sha256').update(typeof v==='string'?v:JSON.stringify(v)).digest('hex');
const fail=m=>{throw new Error('LIUREN_DETERMINISTIC: '+m);};
export function element(s){const i=ZHI.indexOf(s),j=GAN.indexOf(s),k=GENERALS.indexOf(s==='螣蛇'?'腾蛇':s);return i>=0?BRANCH_ELEMENT[i]:j>=0?STEM_ELEMENT[j]:k>=0?GENERAL_ELEMENT[k]:ELEMENTS.includes(s)?s:fail('unknown symbol '+s);}
export function fiveRelation(a,b){a=element(a);b=element(b);return a===b?'比和':ELEMENTS[(ELEMENTS.indexOf(a)+1)%5]===b?'生':ELEMENTS[(ELEMENTS.indexOf(a)+2)%5]===b?'克':ELEMENTS[(ELEMENTS.indexOf(b)+1)%5]===a?'被生':'被克';}
export function kin(reference,target){return {比和:'兄弟',生:'子孙',克:'妻财',被生:'父母',被克:'官鬼'}[fiveRelation(reference,target)];}
export function growth(subject,place){if(!ZHI.includes(place))fail('growth place must be branch');return STATES[mod(ZHI.indexOf(place)-ZHI.indexOf(START[element(subject)]))];}
export function seasonal(subject,month,profile='four-seasons'){
 if(!ZHI.includes(month))fail('month branch');
 let dominant=['木','火','金','水'][Math.floor(mod(ZHI.indexOf(month)-2)/3)];
 if(profile==='quarter-earth'&&[...'辰未戌丑'].includes(month))dominant='土';
 else if(!['four-seasons','quarter-earth'].includes(profile))fail('unregistered seasonal profile');
 const i=ELEMENTS.indexOf(dominant),r=ELEMENTS.indexOf(element(subject));
 return ['旺','相','死','囚','休'][mod(r-i,5)];
}
export function xunFacts(day){
 if(typeof day!=='string'||day.length!==2||!GAN.includes(day[0])||!ZHI.includes(day[1])||GAN.indexOf(day[0])%2!==ZHI.indexOf(day[1])%2)fail('invalid sexagenary day');
 const start=mod(ZHI.indexOf(day[1])-GAN.indexOf(day[0]));
 return {xun:'甲'+ZHI[start],void_branches:[ZHI[mod(start+10)],ZHI[mod(start+11)]],
  xungan:Object.fromEntries(ZHI.map((b,i)=>[b,mod(i-start)<10?GAN[mod(i-start)]:'空']))};
}
const paired=(a,b,pairs)=>pairs.some(p=>p.includes(a)&&p.includes(b)&&a!==b);
export function relations(a,b){
 const out=[{type:'five_elements',from:a,to:b,value:fiveRelation(a,b)}];
 if(ZHI.includes(a)&&ZHI.includes(b)){
  for(const [type,pairs] of [['六合',['子丑','寅亥','卯戌','辰酉','巳申','午未']],['六冲',['子午','丑未','寅申','卯酉','辰戌','巳亥']],['六害',['子未','丑午','寅巳','卯辰','申亥','酉戌']],['六破',['子酉','卯午','辰丑','未戌','寅亥','巳申']]])if(paired(a,b,pairs))out.push({type,from:a,to:b});
  if(['子卯','卯子','寅巳','巳申','申寅','丑戌','戌未','未丑'].includes(a+b))out.push({type:'刑',from:a,to:b,profile:'directed-pair; efficacy not decided'});
  if(a===b&&[...'辰午酉亥'].includes(a))out.push({type:'自刑候选',from:a,to:b,requires_distinct_occurrences:true});
 }
 if(GAN.includes(a)&&GAN.includes(b)&&paired(a,b,['甲己','乙庚','丙辛','丁壬','戊癸']))out.push({type:'天干五合',from:a,to:b});
 return out;
}
export function validateChart(c){
 if(c?.schema!=='liuren-chart-facts-v1')fail('chart schema');
 const rows=c.heaven_earth;
 if(!Array.isArray(rows)||rows.length!==12||new Set(rows.map(r=>r.di)).size!==12||new Set(rows.map(r=>r.tian)).size!==12||rows.some(r=>!ZHI.includes(r.di)||!ZHI.includes(r.tian)||!GENERALS.includes(r.tianjiang)))fail('complete coordinate/general map required');
 const at=b=>rows.find(r=>r.di===b),on=b=>rows.find(r=>r.tian===b);
 if(new Set(rows.map(r=>mod(ZHI.indexOf(r.tian)-ZHI.indexOf(r.di)))).size!==1)fail('plate rotation mismatch');
 if(new Set(rows.map(r=>r.tianjiang)).size!==12)fail('general permutation');
 const steps=ZHI.map((b,i)=>mod(GENERALS.indexOf(at(ZHI[mod(i+1)]).tianjiang)-GENERALS.indexOf(at(b).tianjiang)));
 if(!steps.every(n=>n===1)&&!steps.every(n=>n===11))fail('general sequence');
 if(c.day_stem!==c.pillars?.[2]?.[0]||c.day_branch!==c.pillars?.[2]?.[1]||c.month_branch!==c.pillars?.[1]?.slice(-1)||c.hour_branch!==c.pillars?.[3]?.[1])fail('duplicate pillar fields conflict');
 if(at(c.hour_branch)?.tian!==c.month_general)fail('month general on hour');
 const x=xunFacts(c.pillars[2]);
 if(JSON.stringify([...c.void_branches].sort())!==JSON.stringify([...x.void_branches].sort())||(c.xun&&c.xun!==x.xun))fail('xun or void inconsistent with day');
 const expected=[[at(HOMES[c.day_stem]).tian,c.day_stem],[null,null],[at(c.day_branch).tian,c.day_branch],[null,null]];
 expected[1]=[at(expected[0][0]).tian,expected[0][0]];expected[3]=[at(expected[2][0]).tian,expected[2][0]];
 if(c.lessons?.length!==4||c.lessons.some((r,i)=>r.index!==i+1||r.tianpan!==expected[i][0]||r.dizhi!==expected[i][1]||r.tianjiang!==on(r.tianpan)?.tianjiang))fail('four lessons coordinates/order mismatch');
 if(c.transmissions?.length!==3||c.transmissions.some((r,i)=>r.index!==i+1||!on(r.diZhi)||r.tianjiang!==on(r.diZhi).tianjiang||(r.earth_position&&r.earth_position!==on(r.diZhi).di)))fail('transmission coordinates/order mismatch');
 return {at,on,x};
}
export function buildFacts(c){
 const {at,on,x}=validateChart(c);
 const warnings=[];
 const nodes=ZHI.map((b,i)=>{
  const r=on(b),yin=at(b).tian;
  const rawKin=c.transmissions.filter(t=>t.diZhi===b).map(t=>t.liuqin);
  if(rawKin.some(k=>k!==kin(c.day_stem,b)))warnings.push({code:'ENGINE_KIN_DIFFERENCE',branch:b,engine:rawKin,computed:kin(c.day_stem,b)});
  if(r.xungan!==undefined&&r.xungan!==x.xungan[b])warnings.push({code:'ENGINE_XUNGAN_DIFFERENCE',branch:b,engine:r.xungan,computed:x.xungan[b]});
  const engineGrowth=c.growth?.branches?.[b];
  if(engineGrowth&&engineGrowth[growth(b,r.di)]!==r.di)warnings.push({code:'ENGINE_GROWTH_DIFFERENCE',branch:b,engine:engineGrowth,profile:'element-forward-water-earth'});
  return {id:'D_B'+i,symbol:b,element:element(b),ground:r.di,general:r.tianjiang,general_element:element(r.tianjiang),earth_upper:at(b).tian,earth_upper_general:at(b).tianjiang,direct_yin:yin,
   void_self:x.void_branches.includes(b),void_ground:x.void_branches.includes(r.di),xungan:x.xungan[b],engine_xungan:r.xungan??null,engine_nayin:r.nayin??null,
   kin:{reference:c.day_stem,value:kin(c.day_stem,b)},
   seasonal:{month:c.month_branch,profiles:{'four-seasons':seasonal(b,c.month_branch),'quarter-earth':seasonal(b,c.month_branch,'quarter-earth')},adoption:'select and state the applicable source convention; profiles are not votes'},
   growth:{profile:'element-forward-water-earth',reference:b,ground:growth(b,r.di),yin:growth(b,yin)},
   general_growth:{reference:r.tianjiang,ground:growth(r.tianjiang,r.di),profile:'element-forward-water-earth'},
   local_relations:{branch_to_ground:relations(b,r.di),general_to_branch:relations(r.tianjiang,b),yin_to_branch:relations(yin,b)},
   lesson_slots:c.lessons.filter(l=>l.tianpan===b).map(l=>l.index),transmission_slots:c.transmissions.filter(t=>t.diZhi===b).map(t=>t.index),
   engine_shensha:r.shensha??[],shensha_note:'engine labels retained; adoption only from shensha_resolution, not all labels are adopted'};
 });
 const stems=GAN.map((stem,index)=>{const home=HOMES[stem],upper=at(home).tian;return {id:'D_S'+index,symbol:stem,element:element(stem),home,upper,direct_yin:at(upper).tian,
  seasonal:{month:c.month_branch,profiles:{'four-seasons':seasonal(stem,c.month_branch),'quarter-earth':seasonal(stem,c.month_branch,'quarter-earth')},adoption:'select applicable source convention'},
  growth:{profile:'element-forward-water-earth',reference:stem,home:growth(stem,home),day_branch:growth(stem,c.day_branch)},
  engine_growth:stem===c.day_stem?c.growth?.day_stem??null:null,engine_growth_note:'engine day-stem table retained separately; may use yin-stem reverse convention'};});
 const stem=c.day_stem,stemNode=stems.find(s=>s.symbol===stem),upper=stemNode.upper;
 const tr=c.transmissions.map(r=>r.diZhi);
 return {schema:VERSION,chart_sha256:hash(c),policies:{coordinate:'tian branch -> inverse plate ground; direct_yin = heaven over same-name earth branch',
  seasonal:'four-seasons and quarter-earth remain parallel conditional profiles; no implicit choice',growth:'element-forward; 木亥火寅金巳水土申; not yin-stem reverse',
  relations:'raw relationships, not efficacy/success/transformations',source_basis:['E01','E02','E05','methods/relations.md','methods/liqi.md']},
  xun:x,day:stemNode,stems,anchors:{day_upper:upper,day_yin:at(upper).tian,branch_upper:at(c.day_branch).tian,branch_yin:at(at(c.day_branch).tian).tian},nodes,
  structure:{engine_types:c.chart_types??[],transmissions:tr,transmission_kin:tr.map(b=>kin(stem,b)),
   same_element:new Set(tr.map(element)).size===1,plate_is_identity:c.heaven_earth.every(r=>r.di===r.tian),plate_is_opposition:c.heaven_earth.every(r=>mod(ZHI.indexOf(r.tian)-ZHI.indexOf(r.di))===6),
   triple_member_candidates:['申子辰','亥卯未','寅午戌','巳酉丑'].filter(group=>[...group].every(b=>tr.includes(b))),note:'membership/coordinate facts only; not a final course classification or formed transformation'},
  engine_inventory:{preserved_fields:Object.keys(c),references:Object.fromEntries(['growth','seasonal_strength','nobleman','participants','declared_life','chart_types'].map(k=>[k,'chart.facts.'+k])),year_life_verified:c.year_life_verified??false},
  warnings,limits:['No outcome, probability or weighted score is computed.','Legacy age/year-life is not independently verified; declared life does not establish age.','Raw shensha, course names and native interpretation are not automatically adopted.']};
}
export function symbols(value){
 if(ZHI.includes(value)||GAN.includes(value))return [value];
 const annotated=/^([甲乙丙丁戊己庚辛壬癸])[（(]寄宫([子丑寅卯辰巳午未申酉戌亥])[）)]$/.exec(value);
 if(annotated){if(HOMES[annotated[1]]!==annotated[2])fail('stem home mismatch');return [annotated[1]];}
 if(typeof value==='string'&&value.length>=2&&value.length<=12&&[...value].every(b=>ZHI.includes(b)))return [...new Set(value)];
 fail('entity branch must be one symbol, explicit branch combination, or stem（寄宫X）');
}
export function canonicalEntity(value,d){
 const ss=symbols(value),rows=ss.map(s=>ZHI.includes(s)?d.nodes.find(n=>n.symbol===s):d.stems.find(n=>n.symbol===s));
 if(rows.some(r=>!r))fail('unresolved symbol');
 return {fact_refs:rows.map(r=>r.id),position:rows.map(r=>r.symbol+':'+(r.ground?'天盘临'+r.ground+'乘'+r.general+';地盘本宫上'+r.earth_upper+'乘'+r.earth_upper_general:'寄宫'+r.home+';寄宫上神'+r.upper)).join(' / '),
  site_yin:rows.map(r=>r.symbol+':'+(r.ground?'临'+r.ground+';':'寄'+r.home+';上神'+r.upper+';')+'直接阴神'+r.direct_yin).join(' / '),
  five_qi:rows.map(r=>r.symbol+':'+JSON.stringify(r.seasonal)).join(' / '),
  twelve_states:rows.map(r=>r.symbol+':'+JSON.stringify(r.growth)).join(' / '),
  shenjiang:rows.map(r=>r.symbol+':'+(r.general??'见寄宫上神事实')).join(' / ')};
}
export function focusFacts(d,selected=[]){
 if(!Array.isArray(selected)||selected.some(b=>!ZHI.includes(b)&&!GAN.includes(b)))fail('focus symbols');
 const chosen=selected.length?[...new Set(selected)]:[...new Set([d.day.symbol,...Object.values(d.anchors),...d.structure.transmissions])];
 return {schema:VERSION,chart_sha256:d.chart_sha256,policies:d.policies,xun:d.xun,day:d.day,anchors:d.anchors,
  nodes:d.nodes.filter(n=>chosen.includes(n.symbol)),stems:d.stems.filter(n=>chosen.includes(n.symbol)),relations:chosen.flatMap((a,i)=>chosen.slice(i+1).map(b=>({id:'D_R'+GAN.concat(ZHI).indexOf(a)+'_'+GAN.concat(ZHI).indexOf(b),a,b,forward:relations(a,b),reverse:relations(b,a)}))),
  structure:d.structure,engine_inventory:d.engine_inventory,warnings:d.warnings,limits:d.limits};
}
const TABLES={branch:Object.fromEntries(ZHI.map((b,i)=>[b,[9,8,7,6,5,4,9,8,7,6,5,4][i]])),
 stem:Object.fromEntries(GAN.map((g,i)=>[g,[9,8,7,6,5,9,8,7,6,5][i]])),sheng:{水:1,火:2,木:3,金:4,土:5},cheng:{水:6,火:7,木:8,金:9,土:10}};
export function calculate(spec){
 let count=0;const steps=[];
 const gcd=(a,b)=>{a=a<0n?-a:a;b=b<0n?-b:b;while(b){const t=b;b=a%b;a=t;}return a||1n;};
 const norm=(n,d=1n)=>{if(!d)fail('division by zero');if(d<0n){n=-n;d=-d;}const g=gcd(n,d);n/=g;d/=g;if(n.toString().length>200||d.toString().length>200)fail('arithmetic fraction bound');return {n,d};};
 const numeric=q=>Number(q.n)/Number(q.d);
 function rational(v){const [m,e='0']=String(v).toLowerCase().split('e'),[a,b='']=m.split('.');let n=BigInt(a+b),power=Number(e)-b.length;return power>=0?norm(n*10n**BigInt(power)):norm(n,10n**BigInt(-power));}
 function go(x,depth=0){
  if(++count>100||depth>12||!x||typeof x!=='object'||Array.isArray(x))fail('bounded arithmetic expression required');
  if('value'in x){if(Object.keys(x).length!==1||!Number.isFinite(x.value)||Math.abs(x.value)>1e12||Math.abs(x.value)>0&&Math.abs(x.value)<1e-100)fail('invalid numeric literal');return rational(x.value);}
  if('table'in x){if(Object.keys(x).some(k=>!['table','symbol'].includes(k))||!Object.hasOwn(TABLES,x.table)||!Object.hasOwn(TABLES[x.table],x.symbol))fail('unregistered number table/symbol; general tables must not be guessed');const v=TABLES[x.table][x.symbol];steps.push({lookup:x,value:v});return rational(v);}
  if(Object.keys(x).some(k=>!['op','args'].includes(k))||!['add','subtract','multiply','divide'].includes(x.op)||!Array.isArray(x.args)||x.args.length<2||x.args.length>20)fail('invalid arithmetic operation');
  const vs=x.args.map(v=>go(v,depth+1));
  const v=vs.slice(1).reduce((a,b)=>({add:()=>norm(a.n*b.d+b.n*a.d,a.d*b.d),subtract:()=>norm(a.n*b.d-b.n*a.d,a.d*b.d),multiply:()=>norm(a.n*b.n,a.d*b.d),divide:()=>norm(a.n*b.d,a.d*b.n)}[x.op]()),vs[0]);
  if(!Number.isFinite(numeric(v))||Math.abs(numeric(v))>1e12)fail('arithmetic range');steps.push({op:x.op,args:vs.map(numeric),value:numeric(v)});return v;
 }
 const result=go(spec);
 return {schema:'liuren-arithmetic-v1',expression:spec,value:numeric(result),exact_fraction:{numerator:result.n.toString(),denominator:result.d.toString()},steps,table_profile:'branch/stem/S01-sheng-cheng',limits:['Computes submitted expression only; does not select numerology, magnitude, unit or valid conditions.']};
}
