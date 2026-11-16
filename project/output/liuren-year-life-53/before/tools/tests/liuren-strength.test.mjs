import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {HOMES,ZHI,xunFacts,buildFacts} from '../liuren-deterministic.mjs';
import {computeStrength,compactStrength,STRENGTH_PROFILE} from '../liuren-strength-engine.mjs';
import {combineLosses,cappedLossItems,voidRetention,referenceBase,directedEffect,groupCandidates,groupStrength,openingRatio,goldFireAllocation} from '../liuren-strength-rules.mjs';
import {chartView} from '../liuren-chart-view.mjs';
const read=async p=>JSON.parse(await fs.readFile(new URL(p,import.meta.url),'utf8'));
const source=await read('../../output/liuren-energy-yin-20261106-1443/chart-result.json'),c=source.facts,p=STRENGTH_PROFILE;
const ctx={seasonProfile:'quarter-earth',seasonBasis:'戌月末季土用事研究口径',phase:'outcome',groupModes:{'寅午戌':'cooperate'}};
const result=computeStrength(c,ctx);
const close=(a,b,eps=1e-7)=>assert.ok(Math.abs(a-b)<eps,`${a} != ${b}`);
function synthetic(day='甲申',rotation=8,transmissions=['戌','午','寅']){
 const v=structuredClone(c),at=b=>v.heaven_earth.find(r=>r.di===b),on=b=>v.heaven_earth.find(r=>r.tian===b);
 v.pillars[2]=day;v.day_stem=day[0];v.day_branch=day[1];
 const x=xunFacts(day);v.xun=x.xun;v.void_branches=x.void_branches;
 for(const r of v.heaven_earth)r.tian=ZHI[(ZHI.indexOf(r.di)+rotation)%12];
 v.month_general=at(v.hour_branch).tian;
 const u=at(HOMES[v.day_stem]).tian,b=at(v.day_branch).tian;
 v.lessons=[[u,v.day_stem],[at(u).tian,u],[b,v.day_branch],[at(b).tian,b]].map(([tianpan,dizhi],i)=>({index:i+1,tianpan,dizhi,tianjiang:on(tianpan).tianjiang}));
 v.transmissions=transmissions.map((diZhi,i)=>({index:i+1,diZhi,tianjiang:on(diZhi).tianjiang}));
 return v;
}
test('retains the agreed research void settings and combines self/sitting once',()=>{
 close(voidRetention('旺',true,true,p),.85);close(voidRetention('休',false,true,p),Math.sqrt(.7));
 close(voidRetention('死',false,false,p),1);
});
test('tomb decomposition reproduces the original no-flow score without a second penalty',()=>{
 const r=referenceBase('旺',[{state:'墓',weight:.7},{state:'长生',weight:.3}],p);
 close(r.base*r.access,5*1.3*(.7*.6+.3*1.1));
 assert.ok(openingRatio(3,3.6,p)>openingRatio(1,3.6,p));
});
test('weak control and source support/cost obey the same actual directional limit',()=>{
 const weak=directedEffect('克',1,8,1,1,p),strong=directedEffect('克',8,1,1,8,p);
 assert.ok(-weak.received < -strong.received);
 const full=directedEffect('生',6,4,.75,6,p),half=directedEffect('生',6,4,.75,6,p,.5);
 close(full.received,2*half.received);close(full.cost,2*half.cost);
 const peer=directedEffect('比和',10,4,1,3,p);close(peer.received,.06*3);
});
test('same causes use max, independent causes combine once under a cap',()=>{
 close(combineLosses([{cause:'a',loss:.2},{cause:'a',loss:.1}]),.2);
 close(combineLosses([{cause:'a',loss:.2},{cause:'b',loss:.3}]),.44);
 close(combineLosses([{cause:'a',loss:.8}],.35),.35);
 assert.throws(()=>combineLosses([{cause:'a',loss:NaN}]),/非法/);
});
test('group coverage excludes the twelve-palace inventory and avoids full plus half duplication',()=>{
 const groups=groupCandidates(['寅','午','戌'],{'寅午戌':'cooperate'});
 assert.equal(groups.length,1);assert.equal(groups[0].type,'三合');
 const a=groupStrength(groups[0],{'T:寅':6,'T:午':5,'T:戌':4},p);
 const b=groupStrength(groups[0],{'T:寅':4,'T:午':.1,'T:戌':4},p);
 assert.ok(a.gate_multiplier>b.gate_multiplier);assert.ok(b.gate_multiplier>=1);assert.equal(a.transformed,false);
});
test('gold fire reallocation preserves the common absolute budget and has directional response',()=>{
 const a=goldFireAllocation(.6,.3,3,3,0,0),b=goldFireAllocation(.6,.3,8,3,2,0);
 close(a.positive,.6);close(a.negative,.3);close(b.positive+b.negative,.9);
 assert.ok(b.positive>a.positive);assert.ok(b.negative<a.negative);
});
test('all nodes and multi-start agreement are calculated, with one active yin layer',()=>{
 assert.equal(result.rows.length,37);assert.ok(result.audit.convergence.spread<1e-6);
 assert.equal(result.audit.convergence.initials.length,3);
 assert.ok(result.audit.lower_depth.ledger.every(e=>e.route!=='yin'));
 for(const e of result.audit.ledger.filter(e=>e.route==='yin')){
  if(e.owner!==e.source)close(e.source_strength,result.audit.lower_depth.values[e.source]);
  if(e.owner!==e.target)close(e.target_strength,result.audit.lower_depth.values[e.target]);
 }
});
test('the numeric ledger reconstructs E with exactly one void factor and actual costs',()=>{
 for(const row of result.rows){
  if(row.kind==='ground'){close(row.strength,row.seed);continue;}
  const input=result.audit.ledger.filter(e=>e.target===row.id).reduce((s,e)=>s+e.received+e.reference_reallocation,0);
  const costs=result.audit.ledger.filter(e=>e.source===row.id).reduce((s,e)=>s+e.source_cost,0);
  close(row.delta,input-costs);
  close(row.strength,row.retention*Math.max(0,Math.min(10,row.access*(row.base+input-costs))));
 }
 const key=e=>(e.owner??'mutual')+'|'+e.source;
 for(const id of new Set(result.audit.ledger.map(key)))assert.ok(result.audit.ledger.filter(e=>key(e)===id).reduce((a,e)=>a+e.gate,0)<=2+1e-9);
});
test('坐空 remains different from 自身旬空 and does not become a second full penalty',()=>{
 const n=result.rows.find(x=>x.id==='T:寅');assert.equal(n.void_self,false);assert.equal(n.void_ground,true);
 close(n.retention,Math.sqrt(.6));
});
test('birth plus drain and death plus support are both numerically present',()=>{
 assert.ok(result.audit.ledger.find(e=>e.source==='T:辰'&&e.target==='D:申').source_cost>0);
 assert.ok(result.audit.ledger.find(e=>e.source==='D:巳'&&e.target==='T:丑').received>0);
});
test('unresolved action semantics remain missing instead of false zero/full completeness',()=>{
 assert.ok(result.coverage.pending.length>0);assert.equal(result.coverage.complete_for_declared_actions,false);
 assert.equal(result.rows.find(r=>r.id==='T:寅').action_index,null);
 assert.ok(result.rows.find(r=>r.id==='T:寅').partial_action_index>0);
 assert.equal(result.coverage.event_verdict_supported,false);
});
test('display filtering cannot change a computed graph or revive the other nine stems',()=>{
 const ss={items:[]}; // Test-only explicit adopted empty set, not production resolution.
 const a=chartView(c,{shensha:ss,researchStrength:result});
 const b=a.heaven_earth.filter(n=>n.tian==='寅');
 assert.equal(b[0].state.strength_index,Math.round(result.rows.find(x=>x.id==='T:寅').strength*10)/10);
 assert.equal(a.stems,undefined);assert.equal(a.day.symbol,c.day_stem);
 assert.equal(typeof a.heaven_earth[0].state.strength_index,'number');
 const altered=structuredClone(c);altered.event_datetime='changed';
 assert.throws(()=>chartView(altered,{shensha:ss,researchStrength:result}),/不属于/);
});
test('season and semantic rule inputs fail explicitly rather than silently choosing another rule',()=>{
 assert.throws(()=>computeStrength(c,{seasonBasis:'未选表'}),/seasonProfile/);
 assert.throws(()=>computeStrength(c,{...ctx,effectRules:[{id:'fake',mode:'disrupt',basis:'x'}]}),/不存在/);
 assert.throws(()=>computeStrength(c,{...ctx,shenshaRules:[{id:'fake',mode:'role',basis:'x'}]}),/采用表/);
 assert.throws(()=>computeStrength(c,{...ctx,tombReleases:[{target:'T:寅',source:'T:戌',place:'午',basis:'x'}]}),/开墓/);
});
test('evaluation updates time conditions without recharting or changing the original chart',()=>{
 const before=JSON.stringify(c),r=computeStrength(c,{...ctx,evaluation:{day_pillar:'甲戌',month_branch:'亥',basis:'构造出旬冬月对照'}});
 assert.equal(JSON.stringify(c),before);assert.deepEqual(r.original_void,['午','未']);assert.deepEqual(r.evaluation_void,['申','酉']);
 assert.notEqual(r.rows.find(n=>n.id==='T:午').retention,result.rows.find(n=>n.id==='T:午').retention);
});
test('initial cannot suppress last ghost; last suppressing initial applies at the outcome phase',()=>{
 const a=computeStrength(synthetic('甲申',9,['巳','午','申']),ctx);
 assert.ok(a.audit.blocked_edges.some(e=>e.source==='T:巳'&&e.target==='T:申'&&e.blocked==='初不能制末鬼'));
 const c2=synthetic('甲申',9,['申','午','巳']);
 const b=computeStrength(c2,{...ctx,phase:'opening'}),end=computeStrength(c2,ctx);
 assert.ok(b.audit.blocked_edges.some(e=>e.source==='T:巳'&&e.target==='T:申'));
 assert.ok(end.audit.ledger.some(e=>e.source==='T:巳'&&e.target==='T:申'));
});
test('the metal-stem special branch is an actual ledger replacement and never a free extra grant',()=>{
 const v=synthetic('庚申',9,['巳','午','申']),r=computeStrength(v,ctx);
 const e=r.audit.ledger.find(e=>e.target==='S:庚'&&e.special);
 assert.ok(e);close(e.special.positive+e.special.negative,e.special.budget);
 close(e.received,-e.special.negative);
});
test('nonconvergence stops without scores; reruns are deterministic',()=>{
 const short=structuredClone(p);short.iteration.max_iterations=0;
 assert.throws(()=>computeStrength(c,ctx,{profile:short}),/未收敛/);
 assert.deepEqual(computeStrength(c,ctx),result);
 assert.equal(compactStrength(result).actors.length,25);
});
test('cross-category direct nourishment/binding share a cause instead of double charging',()=>{
 const bind=cappedLossItems([{cause:'place',loss:.2}],.3),greedy=cappedLossItems([{cause:'place',loss:.3}],.5);
 close(combineLosses([...bind,...greedy]),.3);
 const many=cappedLossItems([{cause:'x',loss:.4},{cause:'y',loss:.4}],.3);
 close(combineLosses(many),.3);
});
test('a same-name day branch does not automatically complete a transmission half-combination',()=>{
 const v=synthetic('甲辰',8,['申','子','戌']);
 // Force a rotation where 辰 is not among any lesson heaven symbols.
 for(let rot=0;rot<12;rot++){
  const candidate=synthetic('甲辰',rot,['申','子','戌']);
  if(candidate.lessons.every(l=>l.tianpan!=='辰')){
   const r=computeStrength(candidate,ctx),g=r.groups.find(g=>g.id==='申子辰');
   assert.equal(g.type,'半合');assert.deepEqual(g.members,['T:申','T:子']);return;
  }
 }
 assert.fail('test fixture should have a suitable rotation');
});
test('real tomb opening removes only that closure and does not award new body energy',()=>{
 const v=synthetic('甲申',6,['戌','午','寅']);
 const base=computeStrength(v,ctx),t=base.rows.find(x=>x.kind==='branch'&&x.refs.some(r=>r.state==='墓'));
 assert.ok(t);const ref=t.refs.find(r=>r.state==='墓'),opener=ZHI[(ZHI.indexOf(ref.place)+6)%12];
 const opened=computeStrength(v,{...ctx,tombReleases:[{target:t.id,source:'T:'+opener,place:ref.place,basis:'条件成立的开墓机制对照'}]});
 const after=opened.rows.find(x=>x.id===t.id);
 assert.ok(after.access>=t.access);close(after.base,t.base);close(after.retention,t.retention);
 assert.ok(opened.audit.tomb_before);
});
test('qualified directly related virtue applies without adding base energy or cross-palace force',()=>{
 const chart=synthetic('戊申',8),ss={items:[{id:'test-de',name:'日德',status:'resolved',places:[{tian:'丑'}]}]};
 const first=computeStrength(chart,ctx,{shensha:ss});
 const effectRules=first.audit.relations.map(r=>({id:r.id,mode:'irrelevant',basis:'仅测试德解方向，其他专项固定排除'}));
 const baseContext={...ctx,effectRules,adverseTargets:['S:戊'],shenshaRules:[{id:'test-de',mode:'role',basis:'德解关闭对照'}]};
 const off=computeStrength(chart,baseContext,{shensha:ss});
 const on=computeStrength(chart,{...baseContext,shenshaRules:[{id:'test-de',mode:'virtue',eligible:true,target:'S:戊',basis:'合格德解与真实相关通路的机制试验'}]},{shensha:ss});
 const a=off.rows.find(r=>r.id==='S:戊'),b=on.rows.find(r=>r.id==='S:戊');
 close(a.strength,b.strength);assert.ok(b.virtue_reduction>0);assert.ok(b.virtue_reduction<=.25);
 assert.ok(b.interpretation.qualified_adverse_index<=a.interpretation.qualified_adverse_index);
 assert.equal(on.rows.find(r=>r.id==='J:天后').virtue_reduction,0);
});
test('亥 and 子 use their own ground, yin and carrier only; no arbitrary earth attacks',()=>{
 const contributors=id=>new Set(result.audit.ledger.filter(e=>e.target===id&&e.received!==0).map(e=>e.source));
 assert.deepEqual([...contributors('T:子')].sort(),['D:辰','T:申'].sort());
 assert.deepEqual([...contributors('T:亥')].sort(),['T:未']);
 assert.ok(result.audit.ledger.some(e=>e.source==='T:亥'&&e.target==='D:卯'&&e.type==='生'&&e.source_cost>0));
 assert.ok(!result.audit.ledger.some(e=>e.target==='T:亥'&&e.received<0&&['D:丑','T:丑','T:辰','T:戌'].includes(e.source)));
 assert.ok(!result.audit.ledger.some(e=>e.target==='T:子'&&e.received<0&&['D:丑','T:丑','T:辰','T:戌'].includes(e.source)));
});
test('only direct routes occur; carrier and ground effects remain bidirectional',()=>{
 const d=buildFacts(c);
 for(const e of result.audit.ledger){
  assert.ok(['ground','carrier','yin','day_upper'].includes(e.route));
  if(e.received!==0&&e.target.startsWith('T:')){
   const n=d.nodes.find(n=>'T:'+n.symbol===e.target);
   assert.ok(['D:'+n.ground,'T:'+n.direct_yin,'J:'+n.general].includes(e.source),e.id);
  }
 }
 assert.ok(result.audit.ledger.some(e=>e.source==='D:巳'&&e.target==='T:丑'&&e.received>0));
 assert.ok(result.audit.ledger.some(e=>e.source==='T:辰'&&e.target==='D:申'&&e.source_cost>0));
 assert.ok(result.audit.ledger.some(e=>e.source.startsWith('J:')&&e.target.startsWith('T:')&&e.received!==0));
 assert.ok(result.audit.ledger.some(e=>e.source.startsWith('T:')&&e.target.startsWith('J:')&&e.received!==0));
});
test('adding unrelated focus subjects cannot create extra attacks or change strengths',()=>{
 const other=computeStrength(c,{...ctx,selectedSubjects:['丑','亥','未','酉']});
 for(const row of result.rows)close(other.rows.find(n=>n.id===row.id).strength,row.strength);
 assert.throws(()=>computeStrength(c,{...ctx,fourBuildingLinks:[{role:'月',target:'T:子',basis:'不能靠身份造边'}]}),/无直接加临/);
});
test('user-deferred group calculations neither modify scores nor block action completion',()=>{
 const enabledRequest=computeStrength(c,{...ctx,includeGroupEffects:true,groupModes:{'寅午戌':'bind'}});
 close(enabledRequest.rows.find(x=>x.id==='T:寅').strength,result.rows.find(x=>x.id==='T:寅').strength);
 assert.ok(enabledRequest.groups.every(g=>g.numeric_enabled===false&&g.integrity===null&&g.gate_multiplier===1));
 assert.ok(enabledRequest.coverage.pending.every(x=>!x.rule.startsWith('group:')));
});
