import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {strengthBand,calculateSelectedStrength,palaceStrength} from '../liuren-palace-strength.mjs';
import {chartView} from '../liuren-chart-view.mjs';
import {compute} from '../liuren-deterministic-io.mjs';
const source=JSON.parse(await fs.readFile(new URL('../../output/liuren-energy-yin-20261106-1443/chart-result.json',import.meta.url),'utf8')),c=source.facts;
const request={mode:'selected_relations',season_profile:'quarter-earth',season_basis:'本示例固定戌月季土表，非依结果选表',
 actors:[{id:'T:酉',role:'假设取用的施助金神',basis:'接口算例假设，非本课实际裁决'},{id:'T:子',role:'假设所问类神',basis:'接口算例指定'}],
 links:[{source:'T:酉',target:'T:子',basis:'假设完成取用后，确认施助方生扶子水；仅检验计算方向'}]};
test('bands use exact agreed boundaries; weak never becomes an absolute unusable boolean',()=>{
 for(const [x,text]of [[0,'本计算'],[.99999,'极弱'],[1,'弱，仍'],[2.49999,'弱，仍'],[2.5,'偏弱'],[4.99999,'偏弱'],[5,'较强'],[7.49999,'较强'],[7.5,'强'],[10,'强']])assert.ok(strengthBand(x).startsWith(text));
 assert.equal(strengthBand(null),null);assert.equal(strengthBand(undefined),null);
 for(const x of [NaN,Infinity,-1,11,'1'])assert.throws(()=>strengthBand(x));
});
test('selected support raises target, costs source; tool dispatcher is deterministic and does not mutate chart',()=>{
 const before=JSON.stringify(c),a=compute({action:'strength',strength:request},c),b=calculateSelectedStrength(c,request);
 assert.deepEqual(a,b);assert.equal(JSON.stringify(c),before);
 assert.ok(a.actors.find(x=>x.id==='T:子').delta>0);assert.ok(a.actors.find(x=>x.id==='T:酉').delta<0);
 assert.equal(a.applied_relations.length,1);assert.equal(a.applied_relations[0].type,'生');
 assert.ok(a.convergence.spread<1e-6);
});
test('existing yin support is not counted twice; no links preserves single-palace scores',()=>{
 const q=structuredClone(request);q.actors[0].id='T:申';q.links[0].source='T:申';
 const r=calculateSelectedStrength(c,q);assert.equal(r.applied_relations.length,0);assert.equal(r.already_local_or_blocked.length,1);
 for(const a of r.actors)assert.equal(a.delta,0);
 q.mode='single_palace';q.links=[];
 for(const a of calculateSelectedStrength(c,q).actors)assert.equal(a.delta,0);
});
test('rejects arbitrary coefficients, unselected actors, reversed generation and duplicate relationships',()=>{
 const call=q=>calculateSelectedStrength(c,q);
 assert.throws(()=>call({...request,multiplier:2}),/系数/);
 const q=structuredClone(request);q.links.push(q.links[0]);assert.throws(()=>call(q),/重复/);
 const reverse=structuredClone(request);[reverse.links[0].source,reverse.links[0].target]=[reverse.links[0].target,reverse.links[0].source];assert.throws(()=>call(reverse),/施生/);
 const missing=structuredClone(request);missing.actors.pop();assert.throws(()=>call(missing),/先取用/);
 assert.throws(()=>call({...request,season_basis:''}),/season/);
 assert.throws(()=>call({...request,mode:'single_palace'}),/跨宫/);
 const otherStem=structuredClone(request);otherStem.actors[0].id='S:乙';assert.throws(()=>call(otherStem),/本日日干/);
});
test('explicit control reduces target; void and closure are each applied once',()=>{
 const q=structuredClone(request);q.actors[0].id='T:丑';q.links[0].source='T:丑';
 const r=calculateSelectedStrength(c,q);assert.ok(r.actors.find(a=>a.id==='T:子').delta<0);
 const base=palaceStrength(c,'quarter-earth'),target=base.rows.find(x=>x.id==='T:子'),flow=r.applied_relations[0];
 const expected=target.retention*Math.max(0,Math.min(10,target.access*(target.base+target.delta+flow.received)));
 assert.ok(Math.abs(expected-r.actors.find(a=>a.id==='T:子').adjusted)<1e-6);
});
test('default merged view uses the same single-palace model, scope and weakness bands',()=>{
 const shensha={items:[]},v=chartView(c,{shensha}),base=palaceStrength(c,'quarter-earth'),r=v.heaven_earth.find(x=>x.tian==='子');
 assert.equal(v.strength_model.id,'liuren-palace-strength-v1');assert.ok(v.strength_model.scope.includes('自己的直接阴神'));
 assert.equal(r.state.strength_index.季土,Math.round(base.rows.find(x=>x.id==='T:子').strength*1000)/1000);
 assert.equal(r.state.strength_level.季土??r.state.strength_level,strengthBand(base.rows.find(x=>x.id==='T:子').strength));
 assert.equal(r.state.action_index,undefined);assert.equal(v.qi_summary,undefined);
});
