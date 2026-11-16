import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {bifaView,bifaStatementCatalog} from '../liuren-bifa-view.mjs';
import {scanBasicBifa,basicBifaCatalog} from '../liuren-bifa-basic.mjs';
import {geometryChart} from '../liuren-bifa-batch.mjs';
const variants=JSON.parse(await fs.readFile(new URL('../../output/liuren-bifa-audit-20261111/engine-day-night-1440.json',import.meta.url)));
const fixture=(day,upper,mode='昼贵',month='寅')=>{
 const v=variants.find(v=>v.day===day&&v.day_upper===upper&&v.mode===mode);assert.ok(v);
 const c=geometryChart(v);c.nobleman.rule='甲戊庚牛羊';c.pillars[0]='丙午';c.pillars[1]='己'+month;c.month_general='卯';return c;
};
const find=(c,n)=>bifaView(c).find(r=>r.条目.startsWith('毕法赋'+String(n).padStart(2,'0')+'：'));

test('every law and registered branch has fixed imagery, condition template and original source identity',()=>{
 const catalog=bifaStatementCatalog();assert.deepEqual(catalog.laws.map(r=>r.number),Array.from({length:100},(_,i)=>i+1));
 assert.equal(catalog.rules.length,142);
 for(const rule of basicBifaCatalog()){
  const fixed=catalog.rules.find(r=>r.id===rule.id);assert.ok(fixed);
  assert.deepEqual(fixed.evidence_ids,rule.evidence_ids);assert.equal(fixed.number,rule.law_number);
  assert.ok(fixed.imagery.length>5&&fixed.condition_template.length>5);
 }
 // Opposite meanings and partial structures must not inherit a misleading law title.
 assert.match(catalog.rules.find(r=>r.id==='BF27-drain').imagery,/传脱分支/);
 assert.match(catalog.rules.find(r=>r.id==='BF33-birth-tomb').imagery,/先振后滞/);
 assert.match(catalog.rules.find(r=>r.id==='BF33-tomb-birth').imagery,/困中转机/);
});

test('current 17:07 chart renders exact lesson coordinates and separately names void and void ground',async()=>{
 const source=JSON.parse(await fs.readFile(new URL('../../output/liuren-bifa-current-handoff-20261111/正式盘导出.json',import.meta.url)));
 const c=source.facts,before=JSON.stringify(c),rows=bifaView(c);
 assert.equal(rows.length,5);assert.equal(JSON.stringify(c),before);
 assert.equal(find(c,74).成格,'第一、第四课天盘丑临地盘未，坐空；第二、第三课天盘未临地盘丑，旬空。');
 assert.equal(find(c,82).成格,'初传亥临地盘巳，支与坐地皆不空；中传天盘未临地盘丑，旬空；末传天盘丑临地盘未，坐空。');
 const wealth=find(c,26);assert.match(wealth.条目,/财乘丁马/);assert.match(wealth.成格,/己丑日，初传亥/);
 assert.match(wealth.成格,/旬遁丁，又为日驿马/);
 for(const row of rows)assert.deepEqual(Object.keys(row),['条目','成格','意象']);
 assert.ok(!JSON.stringify(rows).includes('source_sha256'));
});

test('chain endpoints and assistance targets determine precise imagery instead of title-based conclusions',()=>{
 const chain=find(fixture('辛丑','子'),31);assert.match(chain.成格,/终点/);assert.match(chain.意象,/终点/);
 const assist=find(fixture('庚午','午'),37);assert.match(assist.成格,/初传.*为官鬼/);assert.match(assist.意象,/助初鬼/);
 const sun=fixture('壬申','巳');sun.month_general='寅';assert.ok(!find(sun,39));
 const missing=fixture('甲申','未');missing.participants=[{life_branch:'未'}];missing.year_life_verified=true;assert.ok(!find(missing,56));
 const noMethod=bifaView(fixture('甲子','寅'));assert.ok(!noMethod.some(r=>[9,93,94,96,97,98,99].some(n=>r.条目.startsWith('毕法赋'+String(n).padStart(2,'0')+'：'))));
});

test('1440 day/night geometries across twelve contexts preserve every matched law and every subbranch',()=>{
 const seen=new Set();let scans=0;
 for(const v of variants)for(const [i,month] of [...'寅卯辰巳午未申酉戌亥子丑'].entries()){
  const c=geometryChart(v);c.nobleman.rule='甲戊庚牛羊';c.pillars[0]='甲'+month;c.pillars[1]='丙'+month;c.month_general=[...'子丑寅卯辰巳午未申酉戌亥'][i];
  const scan=scanBasicBifa(c),rows=bifaView(c);
  assert.deepEqual(rows.map(r=>Number(r.条目.match(/^毕法赋(\d+)：/)[1])),[...new Set(scan.matches.map(r=>r.law_number))].sort((a,b)=>a-b));
  for(const r of scan.matches){
   seen.add(r.id);const entry=rows.find(x=>x.条目.startsWith('毕法赋'+String(r.law_number).padStart(2,'0')+'：'));
   if(r.law_number===26&&entry.条目.includes('财乘丁马'))assert.match(entry.成格,/财、丁、马同支/);
   else assert.ok(entry.条目.includes(r.name),r.id);
  }
  for(const row of rows){assert.ok(!/[{}]|undefined|NaN|未提供|[a-zA-Z_]/.test(row.成格),row.成格);assert.ok(!/[{}]|undefined|NaN/.test(row.意象));}
  scans++;
 }
 assert.equal(scans,17280);assert.ok(seen.size>=130);
});
