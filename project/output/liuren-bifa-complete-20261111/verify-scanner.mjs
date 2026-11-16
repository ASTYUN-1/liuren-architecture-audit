import fs from 'node:fs/promises';
import assert from 'node:assert/strict';
import {scanBasicBifa,basicBifaCatalog} from '../../tools/liuren-bifa-basic.mjs';
import {geometryChart} from '../../tools/liuren-bifa-batch.mjs';
const vs=JSON.parse(await fs.readFile(new URL('../liuren-bifa-audit-20261111/engine-day-night-1440.json',import.meta.url)));
const catalog=basicBifaCatalog(),stats=Object.fromEntries(catalog.map(r=>[r.id,{matches:0,candidates:0,methods:0,example:null}]));
const zhi=[...'子丑寅卯辰巳午未申酉戌亥'];let scans=0;
for(const v of vs){
 const c=geometryChart(v);c.nobleman.rule='甲戊庚牛羊';
 for(let m=0;m<12;m++){
  // Independent synthetic calendar dimensions, not a claim of real civil dates.
  c.pillars[0]='甲'+zhi[m];c.pillars[1]='丙'+zhi[m];c.month_general=zhi[m];
  const out=scanBasicBifa(c);scans++;
  for(const [key,items] of [['matches',out.matches],['candidates',out.conditional_candidates],['methods',out.method_checks]])for(const r of items){
   stats[r.id][key]++;
   if(key==='matches')assert.ok(r.checks.length&&r.checks.every(x=>x.met===true));
   if(key==='candidates')assert.ok(r.checks.some(x=>x.met===null)&&!r.checks.some(x=>x.met===false));
   if(!stats[r.id].example)stats[r.id].example={day:v.day,upper:v.day_upper,mode:v.mode,month:zhi[m],checks:r.checks,points:r.points};
  }
 }
}
const missed=catalog.filter(r=>!stats[r.id].example);
await fs.writeFile(new URL('./批量核查.json',import.meta.url),JSON.stringify({scans,geometries:1440,calendar_scenarios_per_geometry:12,scope:'synthetic independent calendar probes; not all real dates or all year/month combinations',stats,unreached:missed.map(r=>({id:r.id,definition:r.definition}))},null,2)+'\n');
console.log(JSON.stringify({scans,registered:catalog.length,unreached:missed.map(r=>r.id)}));
