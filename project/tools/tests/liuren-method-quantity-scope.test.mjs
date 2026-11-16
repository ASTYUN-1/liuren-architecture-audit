import test from 'node:test';
import assert from 'node:assert/strict';
import {runResolvedChart} from '../liuren-resolved-chart.mjs';
import {methodQuantity,methodCatalog} from '../liuren-method-tools.mjs';
import {calculate} from '../liuren-deterministic.mjs';

const {facts:c}=await runResolvedChart({datetime:'2026-10-18T13:22'},{persist:false});
const query=target=>({id:'LF3329-class-ground',target,season_profile:'four-seasons',basis:'工程验收：按理法明确五气分支计算，不检验现实预测',unit:'测试单位'});

test('LF source branches preserve 相不倍 and distinguish 旺 unresolved scale',()=>{
 assert.equal(c.month_branch,'戌');
 // This fixed chart has 丑加辰、寅加巳、午加酉、申加亥、亥加寅.
 for(const [target,state,value,stage] of [
  ['T:丑','休',13,'method-number'],['T:寅','死',5.5,'method-number'],
  ['T:午','囚',7.5,'method-number'],['T:申','旺',28,'base-only'],['T:亥','相',28,'method-number']
 ]){
  const r=methodQuantity(c,query(target));
  assert.equal(r.seasonal,state);assert.equal(r.value,value);assert.equal(r.stage,stage);
  if(state==='旺')assert.ok(r.unresolved.some(x=>x.includes('倍进')));
 }
 const m=methodCatalog({kind:'quantity',id:'LF3329-class-ground'}).methods[0];
 assert.equal(m.source.line_mode,'universal');assert.equal(m.source.line_start,3319);
});

test('void target yields unadjusted base; separate justified quantity expression halves once',()=>{
 assert.ok(c.void_branches.includes('亥'));
 const before=JSON.stringify(c),r=methodQuantity(c,query('T:亥'));
 assert.equal(r.value,28);assert.equal(r.calculation_scope.void_quantity_adjustment_applied,false);
 assert.equal(r.calculation_scope.composite_strength_index_read,false);
 assert.equal(r.calculation_scope.included.seasonal_state,'相');
 assert.equal(calculate({op:'divide',args:[{value:r.value},{value:2}]}).value,14);
 assert.equal(calculate({op:'divide',args:[{value:40},{value:2}]}).value,20);
 assert.equal(JSON.stringify(c),before);
});

test('method refuses invented score-to-number inputs and retains scope on legacy formulas',()=>{
 assert.throws(()=>methodQuantity(c,{...query('T:亥'),strength_index:2.9}),/unknown quantity_method fields/);
 assert.throws(()=>methodQuantity(c,{...query('T:亥'),void_factor:0.5}),/unknown quantity_method fields/);
 assert.throws(()=>methodQuantity(c,{...query('T:亥'),season_profile:undefined}),/explicit season_profile/);
 for(const id of ['WY67-shenjiang-base','WY244-month','WY242-generated-base','CY501-use-ground']){
  const q={id,target:'T:'+c.transmissions[0].diZhi,basis:'工程回归，原法适用另核'};
  if(['WY242-generated-base','CY501-use-ground'].includes(id))q.season_profile='four-seasons';
  if(id==='WY244-month')q.number_table='branch';
  const r=methodQuantity(c,q);
  assert.equal(r.calculation_scope.included.source_formula,id);
  assert.equal(r.calculation_scope.void_quantity_adjustment_applied,false);
 }
});
