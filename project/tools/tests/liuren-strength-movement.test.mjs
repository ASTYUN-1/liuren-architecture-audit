import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {HOMES,ZHI} from '../liuren-deterministic.mjs';
import {computeStrength} from '../liuren-strength-engine.mjs';
import {loadShenshaPolicy,resolveShensha} from '../liuren-shensha.mjs';

// Synthetic export only: fix 戌月 and 辰加申 so the movement loss is observable.
const {facts:source}=JSON.parse(await fs.readFile(new URL('../../../examples/normalized-chart-result.json',import.meta.url),'utf8'));
const chart=structuredClone(source);
chart.month_branch='戌';chart.month_pillar='戊戌';chart.pillars[1]='戊戌';
for(const row of chart.heaven_earth)row.tian=ZHI[(ZHI.indexOf(row.di)+8)%12];
const at=di=>chart.heaven_earth.find(row=>row.di===di),on=tian=>chart.heaven_earth.find(row=>row.tian===tian);
chart.month_general=at(chart.hour_branch).tian;
const upper=at(HOMES[chart.day_stem]).tian,branchUpper=at(chart.day_branch).tian;
chart.lessons=[[upper,chart.day_stem],[at(upper).tian,upper],[branchUpper,chart.day_branch],[at(branchUpper).tian,branchUpper]]
 .map(([tianpan,dizhi],i)=>({index:i+1,tianpan,dizhi,tianjiang:on(tianpan).tianjiang}));
chart.transmissions=chart.transmissions.map(item=>({...item,tianjiang:on(item.diZhi).tianjiang,earth_position:on(item.diZhi).di}));
const {policy,sha256}=await loadShenshaPolicy();
const adopted=resolveShensha(chart,policy,sha256);
const context={seasonProfile:'quarter-earth',seasonBasis:'固定合成盘工程测试条件',phase:'outcome',
 goal:{id:'movement-regression',target:'T:辰',mode:'movement'}};
const branch=result=>result.rows.find(row=>row.id==='T:辰');
const calculate=(item,overrides={})=>computeStrength(chart,{...context,...overrides},{shensha:{items:[item]}});

for(const id of ['S15','S01','S12'])for(const goalMode of ['movement','external']){
 const registered=adopted.items.find(item=>item.id===id);
 test(`${registered.name} cannot explicitly select movement with a ${goalMode} goal`,t=>{
  assert.equal(registered.status,'resolved');
  // Fix the location to test adapter identity independently of placement rules.
  const item={...registered,places:[{tian:'辰'}]};
  assert.throws(()=>{
   const accepted=calculate(item,{goal:{...context.goal,mode:goalMode},
    shenshaRules:[{id:item.id,mode:'movement',basis:'负向工程测试'}]});
   t.diagnostic(JSON.stringify({unexpectedly_accepted:item.name,target:'T:辰',
    growth:branch(accepted).refs[0].state,movement:branch(accepted).mechanisms.movement}));
  },/仅驿马、天马、丁马可使用movement适配/);
 });
}

test('the adopted S15 reproduction is on a long-life branch without an implicit horse loss',()=>{
 const item=adopted.items.find(item=>item.id==='S15');
 assert.equal(item.name,'月破');assert.equal(item.places[0].tian,'辰');
 const result=calculate(item);
 assert.equal(branch(result).refs[0].state,'长生');
 assert.deepEqual(branch(result).mechanisms.movement,[]);
 assert.ok(!result.audit.mechanisms.some(item=>item.rule==='马的长生/墓/合/空分层'));
});

for(const name of ['日驿马','驿马','天马','丁马']){
 test(`${name} preserves the same explicit and automatic movement loss`,()=>{
  // Adopted test rows exercise the existing name contract, not new policy entries.
  const item={id:'fixture-horse',name,status:'resolved',places:[{tian:'辰'}]};
  const automatic=calculate(item);
  const explicit=calculate(item,{shenshaRules:[{id:item.id,mode:'movement',basis:'合法马星适配工程对照'}]});
  assert.equal(branch(explicit).refs[0].state,'长生');
  assert.equal(branch(explicit).mechanisms.movement.length,1);
  assert.ok(branch(explicit).mechanisms.movement[0].loss>0);
  assert.deepEqual(explicit.rows,automatic.rows);
  assert.deepEqual(explicit.audit.mechanisms,automatic.audit.mechanisms);
  const external=calculate(item,{goal:{...context.goal,mode:'external'},
   shenshaRules:[{id:item.id,mode:'movement',basis:'合法马星但不是动象占题'}]});
  assert.deepEqual(branch(external).mechanisms.movement,[]);
 });
}

test('a horse name cannot bypass membership in the adopted table',()=>{
 assert.throws(()=>computeStrength(chart,{...context,
  shenshaRules:[{id:'not-adopted',mode:'movement',basis:'未采用项工程测试'}]},
  {shensha:{items:[]}}),/神煞裁用不在本盘采用表/);
});
