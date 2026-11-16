import test from 'node:test';
import assert from 'node:assert/strict';
import {solveInfluenceModel,syntheticModel,extractFeatures,translateScale,applyRetention,composeBase,sweepCoefficient} from './prototype.mjs';
import fs from 'node:fs/promises';

test('zero and five references are equivalent coordinates, including proportional losses below zero',()=>{
 assert.equal(translateScale(5),0);assert.equal(translateScale(0,'zero','five'),5);
 assert.equal(applyRetention(-3,0.8,{scale:'zero'}),-3.4);
 assert.equal(applyRetention(2,0.8),1.6);
 for(const z of [-5,-3,0,2,5]){
  const after=applyRetention(z,0.8,{scale:'zero'});
  assert.ok(after<=z);
  assert.ok(Math.abs(translateScale(after,'zero','five')-applyRetention(z+5,0.8))<1e-12);
 }
});
test('additive and proportional changes have fixed order and a reconciling base ledger',()=>{
 const b=composeBase({baseline:5,adjustments:[{cause_id:'fixture-season',points:3,parameter_id:'a',basis:'engineering only'}],
  multipliers:[{cause_id:'fixture-discount',factor:0.8,parameter_id:'b',basis:'engineering only; not a void rule'}]});
 assert.equal(b.display_five,6.4);assert.ok(Math.abs(b.display_zero-1.4)<1e-12);
 assert.ok(Math.abs(b.base-b.base_ledger.reduce((s,t)=>s+t.delta,0))<1e-12);
 assert.throws(()=>composeBase({adjustments:[{cause_id:'x',points:1,parameter_id:'a',basis:'test'}],
  multipliers:[{cause_id:'x',factor:0.8,parameter_id:'b',basis:'test'}]}),/one cause appears/);
});

test('weak controlling source has limited influence and full arithmetic reconciles',()=>{
 const result=solveInfluenceModel(syntheticModel());
 const target=result.scores.find(n=>n.id==='strong-target');
 assert.ok(target.index>0.78&&target.index<0.8);
 for(const n of result.scores)assert.ok(Math.abs(n.index-(n.base+n.ledger_delta+n.saturation_delta))<1e-9);
 assert.ok(result.convergence.error_bound<1e-8);
});
test('equivalent input ordering produces the same solved indices',()=>{
 const a=syntheticModel(),b=structuredClone(a);b.nodes.reverse();b.events.reverse();
 const x=Object.fromEntries(solveInfluenceModel(a).scores.map(n=>[n.id,n.index]));
 const y=Object.fromEntries(solveInfluenceModel(b).scores.map(n=>[n.id,n.index]));assert.deepEqual(x,y);
});
test('additional alias cannot charge the same cause and mechanism again',()=>{
 const m=syntheticModel();m.events.push({...m.events[0],id:'alias'});
 assert.throws(()=>solveInfluenceModel(m),/duplicate mechanism/);
});
test('one cause cannot silently be both a base loss and dynamic loss',()=>{
 const m=syntheticModel();m.events[0].cause_id='fixture-prior-A';
 assert.throws(()=>solveInfluenceModel(m),/same cause charged/);
});
test('mutual support converges instead of creating unlimited feedback',()=>{
 const m=syntheticModel();m.nodes.forEach(n=>{n.base=0.2;n.base_ledger[0].delta=0.2;});
 m.events=[{...m.events[0],kind:'support',coefficient:0.2,resistance:undefined},
  {...m.events[0],id:'reverse',source:'strong-target',target:'weak-source',kind:'support',coefficient:0.2,
   cause_id:'other',resistance:undefined}];
 const r=solveInfluenceModel(m);assert.ok(r.scores.every(n=>Math.abs(n.index-0.25)<1e-8));
});
test('unbounded feedback and missing numerical assumptions are rejected',()=>{
 const m=syntheticModel();m.events[0].coefficient=0.7;
 assert.throws(()=>solveInfluenceModel(m),/non-contractive/);
 const n=syntheticModel();delete n.events[0].gate;
 assert.throws(()=>solveInfluenceModel(n),/gate out of range/);
});
test('a transfer uses one event and reconciles both receiving and spending',()=>{
 const m=syntheticModel();m.events[0].kind='transfer';m.events[0].coefficient=0.1;
 const r=solveInfluenceModel(m),e=r.event_ledger[0];assert.equal(e.changes.length,2);
 assert.ok(Math.abs(e.changes.reduce((s,n)=>s+n.delta,0))<1e-12);
});
test('zero gate preserves base, and precision budget failure is explicit',()=>{
 const m=syntheticModel();m.events[0].gate=0;
 const r=solveInfluenceModel(m);assert.deepEqual(r.scores.map(n=>n.index),m.nodes.map(n=>n.base));
 assert.throws(()=>solveInfluenceModel(syntheticModel(),{maxIterations:1}),/iteration budget/);
});
test('a coefficient sweep exposes both monotone effects and unstable assumptions',()=>{
 const result=sweepCoefficient(syntheticModel(),'synthetic-c',[0,0.1,0.2,0.7]);
 assert.deepEqual(result.runs.map(r=>r.valid),[true,true,true,false]);
 const v=result.runs.filter(r=>r.valid).map(r=>r.scores.find(n=>n.id==='strong-target').display_five);
 assert.ok(v[0]>v[1]&&v[1]>v[2]);assert.ok(result.ranges.every(r=>r.min!==null));
});
test('real chart extraction keeps correct references and source-dependent structures without a verdict',async()=>{
 const archive=new URL('../../排盘存档/六壬/六壬-20261108-180639-次日应聘结果及公司职位辨识-18cea112-d303-4c6f-a54f-d5a1d2e9da84.corrected-7d8f4da2258d400a.json',import.meta.url);
 const raw=JSON.parse(await fs.readFile(archive,'utf8'));
 const c=raw._direct.facts;
 assert.throws(()=>extractFeatures(c),/explicit seasonProfile/);
 const r=extractFeatures(c,{seasonProfile:'four-seasons',lifeBranch:'未'});
 const shen=r.nodes.find(n=>n.id==='T:申'),tiger=r.nodes.find(n=>n.id==='J:白虎');
 assert.equal(shen.season,'旺');assert.equal(shen.growth_at_ground,'沐浴');assert.equal(shen.void_self,true);
 assert.equal(tiger.growth_at_carrier,'临官');assert.equal(r.day_context.life_upper,'酉');
 assert.equal(r.local_factors.find(f=>f.participants.heaven==='T:戌').conditions.内战,false);
 assert.equal(r.numerical_scores,null);assert.equal(r.nodes.length,37);
 assert.ok(r.group_candidates.every(g=>g.formation==='not adjudicated'&&g.transformation==='not inferred'));
 assert.equal(new Set(r.condition_roots.map(c=>c.id)).size,r.condition_roots.length);
});
