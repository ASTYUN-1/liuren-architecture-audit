import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {buildFacts,ZHI} from '../liuren-deterministic.mjs';
import {buildLocalGraph,solveLocal,evaluateLocal,relationEffect,localStrength} from '../liuren-local-strength.mjs';
const read=async file=>JSON.parse(await fs.readFile(new URL(file,import.meta.url),'utf8'));
const p=await read('../liuren-base-index-profile.json'),r=await read('../liuren-local-strength-profile.json');
const c=(await read('../../output/liuren-energy-yin-20261106-1443/chart-result.json')).facts,d=buildFacts(c);
const out=localStrength(d,c.month_branch,p,r);
const close=(a,b)=>assert.ok(Math.abs(a-b)<1e-8,`${a} != ${b}`);
test('all direct ground/yin/carrier/general-ground and day references are actually computed',()=>{
 for(const {graph,solution} of Object.values(out.outputs)){
  assert.equal(graph.nodes.length,37);assert.ok(solution.residual<r.iteration.tolerance);
  const pairs=new Set(graph.pairs.map(e=>[e.a,e.b].sort().join('|')));
  const has=(a,b)=>assert.ok(pairs.has([a,b].sort().join('|')),a+'/'+b);
  for(const n of d.nodes){
   has('T:'+n.symbol,'D:'+n.ground);has('T:'+n.symbol,'T:'+n.direct_yin);
   has('J:'+n.general,'T:'+n.symbol);has('J:'+n.general,'D:'+n.ground);
  }
  has('S:'+d.day.symbol,'T:'+d.day.upper);has('S:'+d.day.symbol,'T:'+d.day.direct_yin);
 }
});
test('weak controller causes less damage; strong target resists more; weak support gives less',()=>{
 const control=(s,t)=>-relationEffect('克',s,t,1,r.relation).received;
 assert.ok(control(1,8)<control(8,1));assert.ok(control(1,8)<control(1,2));
 assert.ok(relationEffect('生',1,5,1,r.relation).received<relationEffect('生',8,5,1,r.relation).received);
 assert.ok(relationEffect('生',8,5,1,r.relation).cost>0);
 assert.ok(relationEffect('克',8,5,1,r.relation).cost>0);
});
test('each causal edge occurs once and each source has one outgoing budget',()=>{
 for(const {graph} of Object.values(out.outputs)){
  assert.equal(new Set(graph.edges.map(e=>e.id)).size,graph.edges.length);
  for(const n of graph.nodes){
   const sum=graph.edges.filter(e=>e.source===n.id).reduce((s,e)=>s+e.gate,0);
   assert.ok(sum<=r.relation.outgoing_gate_budget+1e-10);
  }
 }
});
test('support, drain, harm and control cost reconcile with the displayed result; void occurs once',()=>{
 for(const {graph,solution} of Object.values(out.outputs))for(const n of solution.rows){
  if(n.kind==='ground'){close(n.value,n.base);continue;}
  const incoming=solution.ledger.filter(e=>e.target===n.id).reduce((a,e)=>a+e.received,0);
  const costs=solution.ledger.filter(e=>e.source===n.id).reduce((a,e)=>a+e.source_cost,0);
  close(solution.delta[n.id],incoming-costs);
  const expected=Math.max(0,Math.min(10,n.prevoid+incoming-costs))*n.retention;
  close(n.value,expected);
 }
});
test('provided examples now include the ground and yin effects with real numeric contributions',()=>{
 const {solution}=out.outputs['quarter-earth'];
 assert.ok(solution.ledger.find(e=>e.source==='T:申'&&e.target==='D:子').source_cost>0);
 assert.ok(solution.ledger.find(e=>e.source==='T:辰'&&e.target==='T:申').received>0);
 assert.ok(solution.ledger.find(e=>e.source==='D:丑'&&e.target==='T:酉').received>0);
 assert.ok(solution.ledger.find(e=>e.source==='J:勾陈'&&e.target==='T:酉').received>0);
 assert.ok(solution.ledger.find(e=>e.source==='T:巳'&&e.target==='T:酉').received<0);
 assert.notEqual(solution.values['T:申'],solution.rows.find(n=>n.id==='T:申').base);
});
test('birth plus drain and death plus support coexist without a second free bonus',()=>{
 const {solution}=out.outputs['quarter-earth'];
 const chen=solution.rows.find(n=>n.id==='T:辰'),chou=solution.rows.find(n=>n.id==='T:丑');
 assert.equal(d.nodes.find(n=>n.symbol==='辰').growth.ground,'长生');
 assert.ok(solution.ledger.find(e=>e.source==='T:辰'&&e.target==='D:申').source_cost>0);
 assert.equal(d.nodes.find(n=>n.symbol==='丑').growth.ground,'绝');
 assert.ok(solution.ledger.find(e=>e.source==='D:巳'&&e.target==='T:丑').received>0);
 assert.ok(chou.value>chou.base);assert.ok(Number.isFinite(chen.value));
});
test('rerunning is deterministic; unbounded iteration failure never returns a score',()=>{
 const graph=out.outputs['quarter-earth'].graph,a=solveLocal(graph,p,r),b=solveLocal(graph,p,r);
 assert.deepEqual(a.values,b.values);
 assert.throws(()=>solveLocal(graph,p,{...r,iteration:{...r.iteration,max_iterations:0}}),/未收敛/);
});
test('rotation and identity/opposition layouts do not create self-edges or duplicate routes',()=>{
 for(const rotation of [0,1,6]){
  const clone=structuredClone(d);
  for(const n of clone.nodes){
   const i=ZHI.indexOf(n.symbol);n.ground=ZHI[(i-rotation+12)%12];n.direct_yin=ZHI[(i+rotation)%12];
  }
  clone.day.upper=clone.nodes[0].symbol;clone.day.direct_yin=clone.nodes[0].direct_yin;
  const graph=buildLocalGraph(clone,c.month_branch,'quarter-earth',p,r);
  assert.ok(graph.edges.every(e=>e.source!==e.target));
  assert.equal(new Set(graph.edges.map(e=>e.id)).size,graph.edges.length);
  assert.ok(solveLocal(graph,p,r).residual<r.iteration.tolerance);
 }
});
