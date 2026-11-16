import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import {hash,ZHI,GAN,xunFacts} from './liuren-deterministic.mjs';
const ROOT=fileURLToPath(new URL('../',import.meta.url));
const fail=m=>{throw new Error('LIUREN_CALENDAR: '+m);};
const HELP='calendar须含start/end、timezone="Asia/Shanghai"、day_boundary="civil-midnight"或"zi-hour"；最小调用：{"start":"2026-11-08","end":"2026-11-09","timezone":"Asia/Shanghai","day_boundary":"civil-midnight"}';
const engines=new Map(),JIE=new Set(['小寒','立春','惊蛰','清明','立夏','芒种','小暑','立秋','白露','寒露','立冬','大雪']);
const HE={子:'丑',丑:'子',寅:'亥',亥:'寅',卯:'戌',戌:'卯',辰:'酉',酉:'辰',巳:'申',申:'巳',午:'未',未:'午'};
export function parseDate(s,field='date'){
 if(typeof s!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(s))fail(field+': YYYY-MM-DD required');
 const [y,m,d]=s.split('-').map(Number),v=new Date(Date.UTC(y,m-1,d));
 if(y<1900||y>2100||v.toISOString().slice(0,10)!==s)fail(field+': invalid date or outside 1900-2100');return v;
}
function engine(root){
 const manifest=JSON.parse(fs.readFileSync(path.join(root,'tools/liuren-direct/legacy-engine-manifest.json'),'utf8'));
 const pinned=manifest.files.find(f=>f.path==='js/lunar.js'),raw=fs.readFileSync(path.join(root,'排盘工具魔改/js/lunar.js'));
 if(hash(raw.toString('utf8'))!==pinned.sha256)fail('pinned engine calendar changed');
 const key=root+'|'+pinned.sha256;
 if(!engines.has(key)){const context=vm.createContext({});vm.runInContext(raw.toString('utf8'),context,{timeout:10000});engines.set(key,{Solar:context.Solar,digest:pinned.sha256});}
 return engines.get(key);
}
export function calendar(spec,{root=ROOT}={}){
 if(!spec||typeof spec!=='object'||Array.isArray(spec))fail('calendar: object required. '+HELP);
 const allowed=['start','end','timezone','day_boundary','branches','pillars','hour','minute','mode','boundary_types','sample_minutes','match','origin','origin_state'];
 for(const k of Object.keys(spec))if(!allowed.includes(k))fail('calendar.'+k+': unknown field. '+HELP);
 if(spec.timezone!=='Asia/Shanghai')fail('calendar.timezone: explicit "Asia/Shanghai" required. '+HELP);
 if(!['civil-midnight','zi-hour'].includes(spec.day_boundary))fail('calendar.day_boundary: expected string "civil-midnight" or "zi-hour"; do not use "midnight", "00:00" or an object. '+HELP);
 const start=parseDate(spec.start,'calendar.start'),end=parseDate(spec.end,'calendar.end'),days=Math.round((end-start)/86400000)+1,mode=spec.mode??'dates';
 if(days<1||days>732)fail('range must be 1-732 days; do not silently truncate');
 if(!['dates','boundaries'].includes(mode))fail('mode must be dates/boundaries');
 const filter=spec.branches??[],pillars=spec.pillars??[];
 if(!Array.isArray(filter)||filter.some(b=>!ZHI.includes(b))||!Array.isArray(pillars)||pillars.some(p=>typeof p!=='string'||p.length!==2||!GAN.includes(p[0])||!ZHI.includes(p[1])||GAN.indexOf(p[0])%2!==ZHI.indexOf(p[1])%2))fail('calendar.branches/pillars: invalid branch/pillar filter');
 const hour=spec.hour??12,minute=spec.minute??0;
 if(!Number.isInteger(hour)||hour<0||hour>23||!Number.isInteger(minute)||minute<0||minute>59)fail('invalid hour/minute');
 if(spec.sample_minutes!==undefined&&(!Number.isInteger(spec.sample_minutes)||spec.sample_minutes<1||spec.sample_minutes>1440))fail('sample_minutes must be integer 1-1440');
 if(spec.sample_minutes!==undefined&&(spec.hour!==undefined||spec.minute!==undefined))fail('sample_minutes cannot be mixed with hour/minute');
 if(spec.match&&(!ZHI.includes(spec.match.target)||!['值','冲','六合'].includes(spec.match.relation)||!['day','hour'].includes(spec.match.axis??'day')||Object.keys(spec.match).some(k=>!['target','relation','axis'].includes(k))))fail('match requires target branch, relation=值/冲/六合 and optional axis=day/hour');
 if(spec.origin_state!==undefined&&(!spec.origin||!['inside','outside'].includes(spec.origin_state)))fail('origin_state requires origin and inside/outside');
 const {Solar,digest}=engine(root);
 function sample(date,h,m,second=0){
  const [y,mo,d]=date.split('-').map(Number),l=Solar.fromYmdHms(y,mo,d,h,m,second).getLunar();
  const day=spec.day_boundary==='zi-hour'?l.getDayInGanZhiExact():l.getDayInGanZhiExact2();
  // getTimeInGanZhi always uses the 23h stem: bind hour stem to selected day.
  const hi=Math.floor((h+1)/2)%12,hourPillar=GAN[(GAN.indexOf(day[0])%5*2+hi)%10]+ZHI[hi];
  return {date,day,xun:xunFacts(day).xun,void_branches:xunFacts(day).void_branches,year:l.getYearInGanZhiExact(),month:l.getMonthInGanZhiExact(),hour:hourPillar,lunar:l.toString()};
 }
 let origin,originStart;
 if(spec.origin){
  if(typeof spec.origin!=='string'||!/^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}(?::\d{2})?)?$/.test(spec.origin))fail('origin must be date or local YYYY-MM-DDTHH:mm[:ss]');
  const date=spec.origin.slice(0,10),od=parseDate(date,'calendar.origin'),[h,m,second]=spec.origin.includes('T')?spec.origin.slice(11).split(':').map(Number):[12,0,0];
  if(h>23||m>59||(second??0)>59)fail('invalid origin time');
  const s=sample(date,h,m,second??0);origin={datetime:spec.origin,day:s.day,xun:s.xun,void_branches:s.void_branches};
  originStart=od.getTime()+(spec.day_boundary==='zi-hour'&&h===23?86400000:0)-GAN.indexOf(s.day[0])*86400000-(spec.day_boundary==='zi-hour'?3600000:0);
 }
 function originFields(date,h,m,s=0){if(!origin)return {};const t=parseDate(date).getTime()+(h*3600+m*60+s)*1000;return {in_origin_xun:t>=originStart&&t<originStart+864000000};}
 const rows=[],occurrences={};
 if(mode==='boundaries'){
  if(filter.length||pillars.length||spec.match||spec.sample_minutes!==undefined||spec.hour!==undefined||spec.minute!==undefined||spec.origin_state!==undefined)fail('boundaries does not accept sampling or row filters');
  const kinds=spec.boundary_types??['节气','节月','旬界'];
  if(!Array.isArray(kinds)||!kinds.length||kinds.some(k=>!['节气','节月','旬界','日界'].includes(k)))fail('invalid boundary_types');
  const seen=new Set();
  for(let y=start.getUTCFullYear();y<=end.getUTCFullYear();y++){
   const l=Solar.fromYmdHms(y,7,1,12,0,0).getLunar();
   for(const [raw,solar]of Object.entries(l.getJieQiTable())){
    const stamp=solar.toYmdHms(),date=stamp.slice(0,10),name=l._convertJieQi(raw);
    if(date<spec.start||date>spec.end||seen.has(stamp))continue;seen.add(stamp);
    const types=[...(kinds.includes('节气')?['节气']:[]),...(kinds.includes('节月')&&JIE.has(name)?['节月']:[])];
    if(!types.length)continue;
    const [h,m,s]=stamp.slice(11).split(':').map(Number);
    rows.push({datetime:stamp.replace(' ','T'),name,types,...sample(date,h,m,s),...originFields(date,h,m,s)});
   }
  }
  for(let i=0;i<days;i++){
   const date=new Date(start.getTime()+i*86400000).toISOString().slice(0,10),h=spec.day_boundary==='zi-hour'?23:0,s=sample(date,h,0);
   const types=[...(kinds.includes('日界')?['日界']:[]),...(kinds.includes('旬界')&&s.day[0]==='甲'?['旬界']:[])];
   if(types.length)rows.push({datetime:date+'T'+String(h).padStart(2,'0')+':00:00',types,...s,...originFields(date,h,0)});
  }
  rows.sort((a,b)=>a.datetime.localeCompare(b.datetime));
 }else{
  if(spec.boundary_types!==undefined)fail('boundary_types requires mode=boundaries');
  const minutes=spec.sample_minutes?Array.from({length:Math.ceil(1440/spec.sample_minutes)},(_,i)=>i*spec.sample_minutes):[hour*60+minute];
  if(days*minutes.length>10000)fail('more than 10000 time samples; narrow range or increase sample_minutes');
  for(let i=0;i<days;i++)for(const mins of minutes){
   const date=new Date(start.getTime()+i*86400000).toISOString().slice(0,10),h=Math.floor(mins/60),m=mins%60,row=sample(date,h,m),of=originFields(date,h,m);
   if((filter.length&&!filter.includes(row.day[1]))||(pillars.length&&!pillars.includes(row.day)))continue;
   if(spec.match){const b=row[spec.match.axis??'day'][1],t=spec.match.target,r=spec.match.relation;
    if(!(r==='值'?b===t:r==='冲'?ZHI[(ZHI.indexOf(t)+6)%12]===b:HE[t]===b))continue;}
   if(spec.origin_state&&(spec.origin_state==='inside')!==of.in_origin_xun)continue;
   const effectiveDate=spec.day_boundary==='zi-hour'&&h===23?new Date(start.getTime()+(i+1)*86400000).toISOString().slice(0,10):date;
   const key=row.day[1]+'|'+effectiveDate;
   if(!occurrences[key]){occurrences[row.day[1]]=(occurrences[row.day[1]]??0)+1;occurrences[key]=occurrences[row.day[1]];}
   rows.push({...row,round_for_branch:occurrences[key],offset_days:i,...of,
    ...(spec.sample_minutes!==undefined?{datetime:date+'T'+String(h).padStart(2,'0')+':'+String(m).padStart(2,'0')+':00'}:{})});
  }
 }
 return {schema:'liuren-calendar-v1',query:spec,calendar_sha256:digest,enumerated_days:days,rows,...(origin?{origin}:{}),
  convention:'Fixed Beijing civil components; explicit midnight/23h day boundary. Date samples default to noon. offset_days=0 at start.',
  limits:['Enumerates dates only; no event selection, timing confidence, or new chart is computed.','Original chart voids, generals and lessons remain unchanged.']};
}
