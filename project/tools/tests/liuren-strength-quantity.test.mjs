import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {calculate,hash} from '../liuren-deterministic.mjs';
import {computeStrength} from '../liuren-strength-engine.mjs';
import {calculateSelectedStrength} from '../liuren-palace-strength.mjs';
import {adjustQuantity,quantityFactor} from '../liuren-quantity-adjustment.mjs';
import {compute} from '../liuren-deterministic-io.mjs';
import {methodQuantity} from '../liuren-method-tools.mjs';
import {checkQuantityReviews,quantityReviewSchema} from '../liuren-quantity-review.mjs';
import {createComputeSchemas} from '../liuren-compute-schema.mjs';
import {tool} from '../../.opencode/node_modules/@opencode-ai/plugin/dist/index.js';
const c=JSON.parse(await fs.readFile(new URL('../../output/liuren-energy-yin-20261106-1443/chart-result.json',import.meta.url),'utf8')).facts;
const target='T:'+c.void_branches[0];
const request={mode:'selected_relations',season_profile:'quarter-earth',season_basis:'固定工程表；不作占断',
 actors:[target,'T:卯'].map(id=>({id,role:'工程对象',basis:'核接口不裁专业取类'})),
 links:[{source:'T:卯',target,basis:'工程指定木生火；不证实实际事件适用'}]};
const realStrength=calculateSelectedStrength(c,request);
function fixture({score=5,route='experimental',value=56,voidSelf=true}={}){
 const sr=structuredClone(realStrength),a=sr.quantity_basis.rows.find(r=>r.id===target);
 // Synthetic score overrides test coefficient arithmetic only. Production
 // callers can supply only receipt hashes, never scores or void booleans.
 a.without_void=score;a.void_self=voidSelf;
 const receipts=[{receipt_sha256:'a'.repeat(64),request:{action:'quantity',expression:{value}},result:calculate({value})},
  {receipt_sha256:'b'.repeat(64),request:{action:'strength',strength:request},result:sr}];
 const q={route,target,base_receipt_sha256:'a'.repeat(64),strength_receipt_sha256:'b'.repeat(64),kind:'score',
  base_factors:{qi:'raw',void:false,basis:'合成本数未纳气态及空减'},
  magnitude:{exponent:0,unit:'分',basis:'合成已定单位',upper_bound:100},
  void:{status:voidSelf?'apply_half':'not_applicable',basis:'合成空半，只测算术与查重',origin:'user_research'},basis:'合成参数验证，非预测'};
 return {q,receipts};
}
const run=f=>adjustQuantity(c,f.q,{receipts:f.receipts});
test('void-free strength rebuilds the same selected graph and preserves the chart and ordinary scores',()=>{
 const before=JSON.stringify(c),r=calculateSelectedStrength(c,request),local=computeStrength(c,{seasonProfile:'quarter-earth',seasonBasis:'固定工程表',phase:'outcome'});
 assert.equal(JSON.stringify(c),before);
 const without=calculateSelectedStrength(c,request,{voidMode:'excluded',quantityView:false});
 for(const a of r.actors){const row=r.quantity_basis.rows.find(x=>x.id===a.id);
  assert.equal(row.with_void,a.adjusted);assert.equal(row.without_void,without.actors.find(x=>x.id===a.id).adjusted);
  assert.equal(a.single_palace,Math.round(local.rows.find(x=>x.id===a.id).strength*1e6)/1e6);
 }
 assert.ok(r.quantity_basis.rows.some(x=>x.with_void!==x.without_void));
 assert.equal(r.quantity_basis.scope,'selected_relations');assert.equal(r.coverage.unselected_palaces_updated,false);
});
test('research curve is continuous at boundaries, monotone, bounded, and never automatic zero or tenfold',()=>{
 for(const [e,v] of [[0,.5],[2.5,.5],[4,1],[6,1],[7.5,1.2],[10,1.2]]){
  assert.equal(quantityFactor(e),v);
  if(e>0)assert.ok(Math.abs(quantityFactor(e)-quantityFactor(e-1e-8))<1e-7);
 }
 let prev=.5;for(let e=0;e<=10;e+=.01){const f=quantityFactor(e);assert.ok(f>=prev&&f<=1.2);prev=f;}
 for(const e of [-1,11,NaN,null])assert.throws(()=>quantityFactor(e));
});
test('experimental weak factor and independent self-void half each occur once',()=>{
 const f=fixture({score:1}),r=run(f);assert.equal(r.value,14);
 assert.deepEqual(r.review.steps.map(s=>[s.kind,s.operand]),[['qi',.5],['void',.5]]);
 assert.equal(r.strength_used.without_void,1);assert.equal(r.experimental_profile.calibrated,false);
 const neutral=run(fixture());assert.equal(neutral.value,28);
 assert.deepEqual(neutral.review.steps.map(s=>s.kind),['void']);
});
test('source route keeps an already season-adjusted sum; no second strength factor even at score zero',()=>{
 const f=fixture({route:'source',score:0,value:17});f.q.base_factors.qi='source_adjusted';
 f.q.void={status:'exception',basis:'源法未明示与囚休叠扣；本例明确不额外扣'};
 const r=run(f);assert.equal(r.value,17);assert.deepEqual(r.review.steps,[]);
 assert.equal(r.review.status,'base_retained');
});
test('named seasonal formulas cannot be relabelled raw and fed into the experimental curve',()=>{
 const f=fixture(),base=methodQuantity(c,{id:'LF3329-class-ground',target,season_profile:'quarter-earth',basis:'工程源法',unit:'分'});
 f.receipts[0]={...f.receipts[0],request:{action:'quantity',quantity_method:{id:'LF3329-class-ground',target}},result:base};
 assert.throws(()=>run(f),/月令/);f.q.base_factors.qi='source_adjusted';assert.throws(()=>run(f),/重复修正/);
 f.q.route='source';assert.ok(Number.isFinite(run(f).value));
});
test('void already included in base forbids a second half; sitting void is not self-void',()=>{
 const f=fixture({route:'source'});f.q.base_factors.void=true;assert.throws(()=>run(f),/已含空减/);
 f.q.void.status='already_in_base';assert.equal(run(f).value,56);
 const g=fixture({voidSelf:false});g.q.void.status='apply_half';assert.throws(()=>run(g),/本身旬空/);
 const h=fixture();h.q.void.status='not_applicable';assert.throws(()=>run(h),/阶段/);
});
test('rank/date/code cannot be multiplied by strength or halved, while explicit source estimates remain possible',()=>{
 for(const kind of ['ordinal','date','identifier']){
  const f=fixture();f.q.kind=kind;assert.throws(()=>run(f),/序数/);
  f.q.route='source';assert.throws(()=>run(f),/序数/);
  f.q.void={status:'exception',basis:'序数含义不支持折半'};assert.equal(run(f).value,56);
 }
});
test('magnitude is independent; bounds reject rather than clip; rounding is an actual recorded operation',()=>{
 const f=fixture({route:'source',value:8,voidSelf:false});delete f.q.magnitude.upper_bound;f.q.kind='amount';
 f.q.magnitude.exponent=3;f.q.magnitude.unit='元';f.q.magnitude.basis='合成已知交易金额级别';assert.equal(run(f).value,8000);
 f.q.magnitude.upper_bound=100;assert.throws(()=>run(f),/超出/);
 const g=fixture({score:3.1,voidSelf:false});g.q.rounding={decimals:0,basis:'分数按整数给估计'};
 const r=run(g);assert.equal(r.value,39);assert.equal(r.review.steps.at(-1).kind,'rounding');
});
test('real receipts must contain the target, matching chart, and unadjusted base',()=>{
 for(const mutate of [f=>f.q.base_receipt_sha256='c'.repeat(64),f=>f.receipts[1].result.chart_sha256=hash({}),
  f=>f.q.target='T:酉',f=>f.q.base_factors.void=true,f=>f.receipts[0].result.contract='liuren-strength-quantity-51',
  f=>f.receipts[1].result.quantity_basis.baseline_reference=6]){const f=fixture();mutate(f);assert.throws(()=>run(f));}
 const f=fixture();f.q.coefficient=.4;assert.throws(()=>run(f),/未知/);
});
test('direct schema and compute share one request shape; legacy or unbound calls cannot inject receipts',()=>{
 const f=fixture(),req={action:'quantity',quantity_adjustment:f.q},schemas=createComputeSchemas(tool.schema);
 assert.deepEqual(schemas.parse(req),req);
 assert.throws(()=>schemas.parse({...req,expression:{value:56}}));
 assert.throws(()=>compute(req,c,{receipts:f.receipts}),/51版/);
 assert.equal(compute(req,c,{receipts:f.receipts,quantityCoupling:true}).value,28);
});
test('new audit accepts generated review but rejects manual final expressions and rewritten steps',()=>{
 const f=fixture(),r=run(f),body='合成估计28分，不作现实预测。',finalHash='c'.repeat(64);
 f.receipts.push({receipt_sha256:finalHash,request:{action:'quantity',quantity_adjustment:f.q},result:r});
 const row={...r.review,question_id:'Q1',final_receipt_sha256:finalHash,report_quote:body};
 quantityReviewSchema(tool.schema).parse([row]);
 const p={consistency_policy:{quantity_review_required:true,quantity_coupling_required:true},questions:[{id:'Q1',tasks:['quantity']}]};
 assert.deepEqual(checkQuantityReviews(p,body,{quantity_reviews:[row]},f.receipts),[]);
 const changed=structuredClone(row);changed.steps[0].basis='重写为另一个理由';
 assert.ok(checkQuantityReviews(p,body,{quantity_reviews:[changed]},f.receipts).some(e=>e.code==='quantity_coupling_mismatch'));
 f.receipts[2].request={action:'quantity',expression:{value:28}};
 assert.ok(checkQuantityReviews(p,body,{quantity_reviews:[row]},f.receipts).some(e=>e.code==='quantity_coupling_required'));
});
