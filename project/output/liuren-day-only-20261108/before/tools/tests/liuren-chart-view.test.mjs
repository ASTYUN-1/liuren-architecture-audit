import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {chartView,exportAIChart,baseIndex,BASE_INDEX_PROFILE as p,voidStatus} from '../liuren-chart-view.mjs';
import {buildFacts,focusFacts,relations} from '../liuren-deterministic.mjs';
import {shenshaForChart} from '../liuren-shensha.mjs';
import {baseScore} from '../../output/liuren-energy-prototype-20261108/fixed-v02/model.mjs';
const saved=JSON.parse(await fs.readFile(new URL('../../output/liuren-energy-yin-20261106-1443/chart-result.json',import.meta.url),'utf8'));
const c=saved.facts,d=buildFacts(c),shensha=await shenshaForChart(c),v=chartView(c,{deterministic:d,shensha});
test('one complete merged chart preserves positions, lessons, transmissions and all adopted shensha',()=>{
 assert.equal(v.lessons[0].dizhi,'甲');assert.equal(v.lessons[0].day_stem_home,'寅');
 assert.equal(v.heaven_earth.length,12);assert.equal(v.lessons.length,4);assert.equal(v.transmissions.length,3);
 for(const n of d.nodes){
  const row=v.heaven_earth.find(r=>r.tian===n.symbol);
  assert.equal(row.di,n.ground);assert.equal(row.tianjiang,n.general);assert.equal(row.direct_yin,n.direct_yin);
  assert.equal(row.state.growth_yin,n.growth.yin);assert.equal(row.general_state.growth_ground,n.general_growth.ground);
  assert.equal(row.status,voidStatus(n.void_self,n.void_ground));
 }
 for(const item of shensha.items.filter(s=>s.status==='resolved')){
  assert.deepEqual(v.heaven_earth.filter(r=>r.shensha.some(s=>s[0]===item.id)).map(r=>r.tian).sort(),item.places.map(r=>r.tian).sort());
 }
 assert.equal(v.day.symbol,c.day_stem);assert.equal(v.stems.length,9);
});
test('void status is semantic, not engine symbols or resolution status',()=>{
 assert.deepEqual(v.transmissions.map(t=>t.status),['','旬空','坐空']);
 assert.equal(voidStatus(true,true),'旬空、坐空');
 assert.ok(!JSON.stringify(v).includes('resolved'));
});
test('no native verdicts, diagnostic inventories, duplicate basic tables or process explanations',()=>{
 const text=JSON.stringify(v);
 for(const key of ['summary','keJing','bifa','zhiZhi','jiYingQian','_direct','engine_check','disabled_names','unregistered_names','validation','limits','policies','local_relations','basic_states','program_facts'])assert.ok(!text.includes('"'+key+'"'),key);
 assert.equal(v.missing_shensha,undefined);
 assert.ok(v.strength_model.kind.includes('研究'));assert.ok(v.strength_model.scope.includes('生克制救未计'));
});
test('base indices exactly reproduce frozen baseScore for all qi, growth states and void combinations',()=>{
 const states=Object.keys(p.growth);
 for(const season of Object.keys(p.season))for(const a of states)for(const b of states)for(const self of [false,true])for(const ground of [false,true]){
  const profiles={'four-seasons':season,'quarter-earth':season};
  for(const [kind,label] of [['branch','天盘神'],['general','天将'],['stem','日干']]){
   const raw=baseScore({kind:label,season,growth_at_ground:kind==='general'?b:a,growth_at_yin:b,growth_at_carrier:a,growth_at_upper:a,void_self:self,void_ground:ground},p).base;
   assert.equal(baseIndex(kind,profiles,[a,b],{self,ground}),Math.round(raw*1000)/1000);
  }
 }
});
test('ambiguous seasonal convention retains paired results rather than inventing one score',()=>{
 const r=v.heaven_earth.find(r=>r.tian==='丑');
 assert.deepEqual(r.state.month_qi,{四季:'休',季土:'旺'});
 assert.equal(typeof r.state.base_index.四季,'number');assert.equal(typeof r.state.base_index.季土,'number');
});
test('compact local states retain all directional five-element and special relationships',()=>{
 const phrase=(a,b,r)=>({生:a+'生'+b,克:a+'克'+b,被生:b+'生'+a,被克:b+'克'+a,比和:a+'与'+b+'比和'}[r]);
 for(const n of d.nodes){
  const row=v.heaven_earth.find(r=>r.tian===n.symbol);
  for(const [a,b,an,bn] of [[n.symbol,n.ground,'神','地'],[n.general,n.symbol,'将','神'],[n.direct_yin,n.symbol,'阴神','神'],[n.general,n.ground,'将','地']]){
   const forward=relations(a,b),reverse=relations(b,a);
   assert.ok(row.state.local.includes(phrase(an,bn,forward[0].value)));
   for(const r of forward.slice(1))assert.ok(row.state.local.includes(r.type==='刑'?an+'刑'+bn:an+'与'+bn+r.type.replace('自刑候选','自刑')));
   for(const r of reverse.slice(1))if(r.type==='刑')assert.ok(row.state.local.includes(bn+'刑'+an));
  }
 }
});
test('public output contains one view and no diagnostics; source facts stay untouched',async()=>{
 const before=JSON.stringify(c),r=await exportAIChart({...saved,ok:true,validation:{ok:true},shensha_resolution:shensha},{persist:false});
 assert.equal(r.facts.schema,'liuren-ai-chart-v1');assert.equal(r.chart_file,null);
 assert.deepEqual(Object.keys(r),['ok','facts','archive','chart_file']);
 assert.equal(JSON.stringify(c),before);
 assert.deepEqual(await exportAIChart({ok:false,error:{code:'INVALID_DATETIME'}}),{ok:false,error:{code:'INVALID_DATETIME'}});
});
test('explicit roles, anchors and void references survive presentation without model reconstruction',()=>{
 assert.deepEqual(v.anchors,d.anchors);
 for(const n of d.nodes){
  const row=v.heaven_earth.find(r=>r.tian===n.symbol),yin=d.nodes.find(r=>r.symbol===n.direct_yin);
  assert.deepEqual(row.lesson_slots,n.lesson_slots);assert.deepEqual(row.transmission_slots,n.transmission_slots);
  assert.equal(row.yin_status,voidStatus(yin.void_self,yin.void_ground));
 }
 assert.deepEqual(v.day.void_positions,['干阴神旬空']);
 assert.ok(v.growth_basis.stems.includes('天干'));assert.ok(v.growth_basis.branches_and_generals.includes('五行'));
});
test('every old focus relationship is represented, including direction and special relations',()=>{
 for(const pair of focusFacts(d).relations){
  const row=v.active_relations.find(r=>r.a===pair.a&&r.b===pair.b||r.a===pair.b&&r.b===pair.a);
  assert.ok(row,pair.a+pair.b);
  const phrase=(a,b,r)=>({生:a+'生'+b,克:a+'克'+b,被生:b+'生'+a,被克:b+'克'+a,比和:a+'与'+b+'比和'}[r]);
  const fwd=relations(row.a,row.b),rev=relations(row.b,row.a);
  assert.ok(row.state.includes(phrase(row.a,row.b,fwd[0].value)));
  for(const r of fwd.slice(1))assert.ok(row.state.includes(r.type==='刑'?row.a+'刑'+row.b:row.a+'与'+row.b+r.type.replace('自刑候选','自刑')));
  for(const r of rev.slice(1))if(r.type==='刑')assert.ok(row.state.includes(row.b+'刑'+row.a));
 }
});
test('stem-specific local effects are retained for all ten stems rather than substituted with home elements',()=>{
 for(const s of d.stems){
  const row=[v.day,...v.stems].find(r=>r.symbol===s.symbol);
  const phrase=(a,b,r)=>({生:a+'生'+b,克:a+'克'+b,被生:b+'生'+a,被克:b+'克'+a,比和:a+'与'+b+'比和'}[r]);
  assert.ok(row.local.includes(phrase('上神','本干',s.local_relations.upper_to_stem[0].value)));
  assert.ok(row.local.includes(phrase('干阴神','本干',s.local_relations.yin_to_stem[0].value)));
 }
 const yi=v.stems.find(s=>s.symbol==='乙');
 assert.ok(yi.local.includes('上神生本干')); // 子生乙木, not 子被辰土克.
});
