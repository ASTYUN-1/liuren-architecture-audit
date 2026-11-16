import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
import {hash,ZHI,GAN,xunFacts} from './liuren-deterministic.mjs';
import {CALENDAR_HELP} from './liuren-compute-schema.mjs';
const ROOT=fileURLToPath(new URL('../',import.meta.url));
const fail=m=>{throw new Error('LIUREN_CALENDAR: '+m);};
export function parseDate(s,field='date'){
 if(typeof s!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(s))fail(field+': YYYY-MM-DD required');
 const [y,m,d]=s.split('-').map(Number),v=new Date(Date.UTC(y,m-1,d));
 if(y<1900||y>2100||v.toISOString().slice(0,10)!==s)fail(field+': invalid date or outside 1900-2100');return v;
}
export function calendar(spec,{root=ROOT}={}){
 if(!spec||typeof spec!=='object'||Array.isArray(spec))fail('calendar: object required. '+CALENDAR_HELP);
 const allowed=['start','end','timezone','day_boundary','branches','pillars','hour','minute'];
 for(const k of Object.keys(spec))if(!allowed.includes(k))fail('calendar.'+k+': unknown field. '+CALENDAR_HELP);
 if(spec.timezone!=='Asia/Shanghai')fail('calendar.timezone: explicit "Asia/Shanghai" required. '+CALENDAR_HELP);
 if(!['civil-midnight','zi-hour'].includes(spec.day_boundary))fail('calendar.day_boundary: expected string "civil-midnight" or "zi-hour"; do not use "midnight", "00:00", or an object. '+CALENDAR_HELP);
 const start=parseDate(spec.start,'calendar.start'),end=parseDate(spec.end,'calendar.end'),days=Math.round((end-start)/86400000)+1;
 if(days<1||days>732)fail('range must be 1-732 days; do not silently truncate');
 const filter=spec.branches??[],pillars=spec.pillars??[];
 if(!Array.isArray(filter)||filter.some(b=>!ZHI.includes(b))||!Array.isArray(pillars)||pillars.some(p=>typeof p!=='string'||p.length!==2||!GAN.includes(p[0])||!ZHI.includes(p[1])||GAN.indexOf(p[0])%2!==ZHI.indexOf(p[1])%2))fail('calendar.branches/pillars: invalid branch/pillar filter');
 const hour=spec.hour??12,minute=spec.minute??0;
 if(!Number.isInteger(hour)||hour<0||hour>23||!Number.isInteger(minute)||minute<0||minute>59)fail('invalid hour/minute');
 const manifest=JSON.parse(fs.readFileSync(path.join(root,'tools/liuren-direct/legacy-engine-manifest.json'),'utf8'));
 const pinned=manifest.files.find(f=>f.path==='js/lunar.js');
 const raw=fs.readFileSync(path.join(root,'排盘工具魔改/js/lunar.js'));
 if(hash(raw.toString('utf8'))!==pinned.sha256)fail('pinned engine calendar changed');
 const context=vm.createContext({});vm.runInContext(raw.toString('utf8'),context,{timeout:10000});
 const rows=[],occurrences={};
 for(let i=0;i<days;i++){
  const v=new Date(start.getTime()+86400000*i),date=v.toISOString().slice(0,10);
  const lunar=context.Solar.fromYmdHms(v.getUTCFullYear(),v.getUTCMonth()+1,v.getUTCDate(),hour,minute,0).getLunar();
  const day=spec.day_boundary==='zi-hour'?lunar.getDayInGanZhiExact():lunar.getDayInGanZhiExact2();
  if((filter.length&&!filter.includes(day[1]))||(pillars.length&&!pillars.includes(day)))continue;
  occurrences[day[1]]=(occurrences[day[1]]??0)+1;
  rows.push({date,day,round_for_branch:occurrences[day[1]],offset_days:i,xun:xunFacts(day).xun,
   void_branches:xunFacts(day).void_branches,year:lunar.getYearInGanZhiExact(),month:lunar.getMonthInGanZhiExact(),hour:lunar.getTimeInGanZhi(),lunar:lunar.toString()});
 }
 return {schema:'liuren-calendar-v1',query:spec,calendar_sha256:pinned.sha256,enumerated_days:days,rows,
  convention:'Fixed Beijing civil components; explicit midnight/23h day boundary. Date samples default to noon. offset_days=0 at start.',
  limits:['Enumerates dates only; no event selection, timing confidence, or new chart is computed.','Original chart voids, generals and lessons remain unchanged.']};
}
