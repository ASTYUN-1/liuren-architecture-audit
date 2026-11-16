import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {loadSources,parseLabel,modeRequirement,reviewCandidates,reviewResolvedFile,scanRegistered,buildAIHandoff} from '../liuren-bifa-audit.mjs';

const base=new URL('../../output/liuren-bifa-audit-20261111/',import.meta.url);
const resolved=JSON.parse(await fs.readFile(new URL('current-example-1442/resolved-chart.json',base),'utf8'));
const chart=resolved.facts,raw=await fs.readFile(new URL('current-example-1442/raw-bifa.txt',base),'utf8');
const inspect=(c=chart,text=raw)=>reviewCandidates(c,text,{sourcesValid:true});

test('current real chart binds original archive, both source books and all 14 candidates',async()=>{
 const r=await reviewResolvedFile(new URL('current-example-1442/resolved-chart.json',base));
 assert.equal(r.summary.raw_label_count,14);assert.equal(r.summary.distinct_law_count,11);
 assert.equal(r.source_validated,true);assert.ok(r.source_validation.every(s=>s.valid));
 assert.deepEqual(r.summary.counts,{definition_not_met:1,structure_matched:6,relation_only:1,excluded_other_mode:4,engine_basis_unproven:1,branch_matched:1});
 const ids=new Set(r.evidence.map(e=>e.id));
 for(const row of r.rows)for(const id of row.evidence_ids)assert.ok(ids.has(id),id);
});

test('source bytes and all 19 continuous excerpts still match the two approved books',async()=>{
 const sources=await loadSources();assert.equal(sources.sources.length,2);assert.equal(sources.valid,true);
 assert.equal(sources.sources.reduce((n,s)=>n+s.excerpts.length,0),19);
 assert.ok(sources.sources.every(s=>s.excerpts.every(e=>e.quote.trim().length>0)));
});

test('mode follows selected actual noble mode and excludes four night-only rows',()=>{
 const r=inspect();assert.deepEqual(r.rows.filter(x=>x.status==='excluded_other_mode').map(x=>x.index),[7,10,12,14]);
 assert.throws(()=>inspect({...chart,nobleman:{zhouye:'自动选择'}}),/缺实际昼夜/);
});

test('hypothetical night setting uses the matching generals, irrespective of the original clock time',async()=>{
 const all=JSON.parse(await fs.readFile(new URL('engine-day-night-1440.json',base),'utf8'));
 const v=all.find(r=>r.day==='己丑'&&r.day_upper==='卯'&&r.mode==='夜贵');
 const night=structuredClone(chart);
 night.nobleman.zhouye='夜贵';
 const names=['zi','chou','yin','mao','chen','si','wu','wei','shen','you','xu','hai'];
 const zhi=[...'子丑寅卯辰巳午未申酉戌亥'];
 for(const p of night.heaven_earth)p.tianjiang=v.shenpan[names[zhi.indexOf(p.di)]];
 for(const [i,l]of night.lessons.entries())l.tianjiang=v.sike[i][0];
 for(const [i,t]of night.transmissions.entries())t.tianjiang=v.sanchuan[i][4];
 const r=inspect(night);
 assert.deepEqual(r.rows.filter(x=>x.status==='excluded_other_mode').map(x=>x.index),[5,9]);
 for(const index of [7,10,12,14])assert.equal(r.rows[index-1].status,'structure_matched');
});

test('day/night in law titles and in a referenced noble is not blindly treated as a mode restriction',()=>{
 assert.equal(modeRequirement(parseLabel('45.昼夜贵加求两贵')).kind,'unspecified');
 assert.equal(modeRequirement(parseLabel('43.害贵讼直作屈断.Ⅰ.害夜贵')).kind,'referenced_noble');
 assert.equal(inspect(chart,'43.害贵讼直作屈断.Ⅰ.害夜贵').rows[0].status,'not_reviewed');
 assert.deepEqual(modeRequirement(parseLabel('31.三传递生人举荐.C.两面刀格.②昼将（夜将无)')),{kind:'explicit',required:'昼贵'});
});

test('unreviewed and failed-source candidates never acquire adoptable conclusions',()=>{
 const unknown=inspect(chart,'99.常问不应逢吉象').rows[0];
 assert.equal(unknown.status,'not_reviewed');assert.deepEqual(unknown.adoptable_information,[]);
 const blocked=reviewCandidates(chart,raw,{sourcesValid:false});
 assert.ok(blocked.rows.filter(r=>r.status!=='excluded_other_mode').every(r=>r.status==='source_validation_required'&&r.adoptable_information.length===0));
});

test('broad Japan-Taichang relation cannot acquire the narrower on-day/on-branch conclusions',()=>{
 const r=inspect().rows[4];assert.equal(r.status,'relation_only');
 assert.deepEqual(r.extensions,[{condition:'临干',met:false},{condition:'临支',met:false}]);
 assert.equal(inspect(chart,'26.水日逢丁财动之.A.财乘丁马格.③财乘日本临干上.昼常').rows[0].status,'definition_not_met');
 assert.equal(inspect(chart,'26.水日逢丁财动之.A.财乘丁马格.③财乘日本临支上.昼常').rows[0].status,'definition_not_met');
});

test('prison branch is a valid ordinary rule, not a partially fulfilled favorable exception',()=>{
 const r=inspect().rows[10];assert.equal(r.status,'branch_matched');
 assert.deepEqual(r.adoptable_information,['贵人入狱']);assert.ok(r.exceptions.every(e=>!e.met));
});

test('false ring and unsupported engine noble orientation do not masquerade as competing book doctrines',()=>{
 const r=inspect();assert.equal(r.rows[0].status,'definition_not_met');assert.deepEqual(r.rows[0].missing_members,['丑']);
 assert.deepEqual(r.rows[8].adoptable_information,[]);
 assert.deepEqual(r.rows[8].source_supported_information,['按北海明示核法，本盘贵在干后']);
 assert.equal(r.rows[8].status,'engine_basis_unproven');
});

test('duplicate Ding/horse and tiger-ghost observations have stable shared evidence keys',()=>{
 const r=inspect();assert.deepEqual(r.rows[2].deduplicate_key,r.rows[3].deduplicate_key);
});

test('law 22 B uses Daqan vertical pairs, not Beihai same-name horizontal pairs',()=>{
 const c=structuredClone(chart);c.pillars[2]='甲申';
 c.lessons[0].tianpan='亥';c.lessons[2].tianpan='巳';
 const label='22.上下皆合两心齐.B.上下俱合格';
 const r=inspect(c,label).rows[0];assert.equal(r.status,'structure_matched');assert.deepEqual(r.evidence_ids,['D22']);
 // 壬寅伏吟 is Beihai's horizontal example; it is not the adopted vertical branch.
 c.pillars[2]='壬寅';c.lessons[0].tianpan='亥';c.lessons[2].tianpan='寅';
 assert.equal(inspect(c,label).rows[0].status,'definition_not_met');
});

test('AI material omits failed labels, binds sources and preserves limits instead of title verdicts',async()=>{
 const r=await reviewResolvedFile(new URL('current-example-1442/resolved-chart.json',base));
 const ai=buildAIHandoff(r,r.independent_scan);
 assert.equal(ai.items.length,8);assert.equal(ai.actual_mode,'昼贵');assert.equal(ai.coverage.all_100_laws_reviewed,false);
 assert.ok(ai.chart_binding.archive_sha256);assert.equal(ai.auto_attached_to_adjudicator,false);
 assert.ok(ai.items.every(i=>!i.raw_label&&!i.title&&i.limits));
 assert.ok(ai.items.every(i=>![2,46,61,91].includes(i.law_number)));
 const keys=ai.items.filter(i=>i.law_number===26&&i.deduplicate_key.length).map(i=>i.deduplicate_key);
 assert.equal(keys.length,2);assert.deepEqual(keys[0],keys[1]);
 assert.throws(()=>buildAIHandoff({...r,source_validated:false},r.independent_scan),/未核书证/);
 assert.throws(()=>buildAIHandoff({...r,evidence:[]},r.independent_scan),/缺完整有效/);
});

test('independent scan can find a valid omitted structure without trusting native export coverage',()=>{
 const r=inspect(chart,'06.六阴相继尽昏迷.A.六阴格');
 const scan=scanRegistered(chart,{sourcesValid:true});
 assert.equal(r.rows.some(i=>i.law_number===31),false);
 assert.equal(scan.rows.find(i=>i.raw_label==='31.三传递生人举荐').status,'structure_matched');
});

test('the complete exported label vocabulary has no unrecognized day/night suffix silently accepted',async()=>{
 const all=JSON.parse(await fs.readFile(new URL('engine-bifa-lookup-720.json',base),'utf8'));
 const labels=[...new Set(all.flatMap(r=>(r.text??'').split('\n')))];
 assert.equal(labels.length,250);
 const unresolved=labels.map(parseLabel).filter(l=>modeRequirement(l).kind==='unresolved_wording');
 assert.deepEqual(unresolved,[]);
 assert.equal(parseLabel('课义：传及支干，总下').kind,'non_bifa_text');
 assert.ok(parseLabel('4.贵人差迭事参差.昼贵在干后').label_error);
});
