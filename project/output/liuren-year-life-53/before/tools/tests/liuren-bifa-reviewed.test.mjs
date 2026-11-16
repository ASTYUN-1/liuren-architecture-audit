import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {scanBasicBifa,basicBifaCatalog} from '../liuren-bifa-basic.mjs';
import {geometryChart} from '../liuren-bifa-batch.mjs';
const variants=JSON.parse(await fs.readFile(new URL('../../output/liuren-bifa-audit-20261111/engine-day-night-1440.json',import.meta.url)));
const fixture=(day,upper,mode='昼贵',month='寅',year='午')=>{
 const v=variants.find(v=>v.day===day&&v.day_upper===upper&&v.mode===mode);assert.ok(v);
 const c=geometryChart(v);c.nobleman.rule='甲戊庚牛羊';c.pillars[0]='甲'+year;c.pillars[1]='丙'+month;return c;
};
const has=(c,id)=>scanBasicBifa(c).matches.some(r=>r.id===id);

test('all one hundred laws retain concrete definitions and correct source identities',()=>{
 const rows=basicBifaCatalog();assert.equal(new Set(rows.map(r=>r.law_number)).size,100);
 assert.equal(rows.filter(r=>r.extended).length,110);
 for(const r of rows)assert.ok(r.definition&&r.evidence_ids.length);
});

test('book examples independently exercise reviewed basic structures across chapters',()=>{
 const cases=[
 ['庚辰','丑','BF01-stem'],['己亥','子','BF01-branch'],
 ['乙卯','卯','BF07-lu'],['甲子','辰','BF08-lu'],['癸丑','申','BF10-rotten'],
 ['壬辰','寅','BF11-rescue'],['乙丑','子','BF11-ghost-parent'],['丁未','子','BF12-fox'],
 ['戊申','丑','BF14-wealth-season','昼贵','申'],['庚子','子','BF15-double','夜贵'],
 ['壬子','子','BF17-advance'],['戊申','辰','BF18-retreat'],
 ['壬寅','午','BF19-stem-fetus','昼贵','申'],['壬寅','午','BF20-fetus-dead','昼贵','寅'],
 ['庚午','卯','BF25-ding'],['丙申','丑','BF28-real-wealth'],['甲申','午','BF29-main'],['甲辰','戌','BF30-main'],
 ['乙未','申','BF33-birth-tomb'],['丙寅','丑','BF33-tomb-birth'],['戊寅','巳','BF34-two-edged'],
 ['庚寅','亥','BF35-each'],['庚寅','巳','BF35-cross'],['甲申','子','BF36-each'],
 ['甲申','亥','BF38-tail-head'],['丁卯','寅','BF40-queen-match'],['己卯','午','BF42-xun'],
 ['甲申','未','BF43-harm','夜贵'],['丁酉','酉','BF44-crowd'],['甲申','丑','BF45-cover'],
 ['丁丑','酉','BF45-stack'],['甲子','午','BF46-mismatch'],['辛丑','午','BF48-ghost'],
 ['乙丑','午','BF49-restrained'],['丁丑','酉','BF50-empty'],['丙戌','戌','BF53-snake'],
 ['甲申','卯','BF55-each'],['庚寅','卯','BF55-cross'],['丙午','寅','BF57-cost'],
 ['丙寅','申','BF58-broken','夜贵'],['壬申','辰','BF59-canopy'],
 ['乙亥','子','BF62-house'],['丁亥','子','BF63-each'],['甲子','戌','BF64-mutual-attack'],['甲子','午','BF64-separation'],
 ['乙丑','未','BF65-gate','昼贵','申'],['甲子','午','BF66-wealth-tomb'],['乙丑','酉','BF68-rescue'],
 ['丁巳','丑','BF71-illness','昼贵','寅','子'],['甲午','未','BF72-mourning','昼贵','寅','酉'],
 ['癸亥','午','BF73-return-clamp'],['乙巳','寅','BF74-lessons-void'],['甲辰','酉','BF75-self-punish'],
 ['甲申','巳','BF76-harm-each'],['甲申','亥','BF76-harm-cross'],['乙亥','子','BF76-harm-upper'],
 ['甲申','卯','BF78-each'],['甲申','申','BF79-each'],['甲申','午','BF80-each'],
 ['辛未','卯','BF81-tomb-chain'],['甲子','巳','BF82-stop'],['甲子','午','BF84-break-union'],
 ['甲申','酉','BF87-each-seat'],['壬申','辰','BF88-each'],['甲寅','寅','BF89-moving'],['己酉','丑','BF90-empty-return'],
 ['丙寅','寅','BF92-dragon-month','夜贵','辰'],['辛未','午','BF95-kin-group'],
 ['丙寅','亥','BF100-finish'],['癸未','辰','BF100-earth-conflict'],
 ];
 const failures=cases.filter(([day,upper,id,mode,month,year])=>!has(fixture(day,upper,mode,month,year),id));
 assert.deepEqual(failures,[],'source example failures: '+JSON.stringify(failures));
 // 大全庚戌卯加申例，当前起法初传戌，不因书内标签而强填卯发用。
 assert.ok(!has(fixture('庚戌','卯'),'BF10-rotten'));
 const cost=scanBasicBifa(fixture('丙午','寅')).matches.find(r=>r.id==='BF57-cost');
 assert.equal(cost.costs_all_empty,true);assert.deepEqual(cost.real_cost_branches,[]);
});

test('38 distinguishes celestial head, terrestrial head, tail and full combinations',()=>{
 let headOnly=0,groundOnly=0,tailOnly=0;
 for(const v of variants){const c=geometryChart(v),r=scanBasicBifa(c),ids=new Set(r.matches.map(m=>m.id));
  if(ids.has('BF38-head-thief')&&!ids.has('BF38-ground-head-thief'))headOnly++;
  if(ids.has('BF38-ground-head-thief')&&!ids.has('BF38-head-thief'))groundOnly++;
  if(ids.has('BF38-tail-head')&&!ids.has('BF38-head-thief'))tailOnly++;
  assert.ok(!ids.has('BF38-closed-wealth')||r.matches.find(m=>m.id==='BF38-closed-wealth').points.some(p=>p.positions.some(s=>['第1课上神','第3课上神','初传','中传','末传'].includes(s))));
 }
 assert.ok(headOnly&&groundOnly&&tailOnly);
});

test('missing calendar, noble rule or principal life identity never becomes a positive match',()=>{
 const c=fixture('壬寅','午','昼贵','申'),good=scanBasicBifa(c);assert.ok(good.matches.some(r=>r.id==='BF19-stem-fetus'));
 c.pillars[1]=null;const unknown=scanBasicBifa(c);assert.ok(!unknown.matches.some(r=>r.id==='BF19-stem-fetus'));assert.ok(unknown.conditional_candidates.some(r=>r.id==='BF19-stem-fetus'));
 const grave=fixture('甲申','未');grave.participants=[{life_branch:'未'}];grave.year_life_verified=true;
 const out=scanBasicBifa(grave);assert.ok(!out.matches.some(r=>r.id==='BF56-life'));assert.ok(out.conditional_candidates.some(r=>r.id==='BF56-life'));
 const noble=fixture('甲子','丑','夜贵');delete noble.nobleman.rule;const n=scanBasicBifa(noble);assert.ok(!n.matches.some(r=>r.id==='BF03-curtain'));assert.ok(n.coverage.unavailable_context.some(r=>r.id==='BF03-curtain'));
});

test('actual noble conventions are required; solar illumination remains explicitly unverified',()=>{
 const c=fixture('甲子','丑','夜贵');assert.ok(has(c,'BF03-curtain'));
 c.nobleman.rule='甲羊戊庚牛';assert.ok(!has(c,'BF03-curtain'));
 const sun=fixture('壬申','巳');sun.month_general='寅';const out=scanBasicBifa(sun);
 assert.ok(!out.matches.some(r=>r.id==='BF39-sun-thief'));assert.ok(out.conditional_candidates.some(r=>r.id==='BF39-sun-thief'));
});

test('54 requires the actual chart type; 96 maps both void roles; 100 does not promise immunity',()=>{
 const c=fixture('丁亥','戌','夜贵');c.chart_types=['昴星'];assert.ok(has(c,'BF54-tiger'));
 c.chart_types=['涉害'];assert.ok(!has(c,'BF54-tiger'));
 const out=scanBasicBifa(fixture('甲子','寅'));
 const v=out.method_checks.find(r=>r.law_number===96);assert.deepEqual(v.role_facts.map(r=>r.branch),['戌','亥']);assert.deepEqual(v.role_facts.map(r=>r.kin),['妻财','父母']);
 assert.ok(out.method_checks.find(r=>r.law_number===100).source_disagreement.includes('暂停'));
 assert.equal(out.coverage.all_100_laws_complete,false);assert.equal(out.coverage.all_100_laws_basic_reviewed,true);
});
