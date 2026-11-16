import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {runResolvedChart} from '../liuren-resolved-chart.mjs';
import {enrichBasicStates} from '../liuren-basic-states.mjs';
import {buildFacts,focusFacts,hash} from '../liuren-deterministic.mjs';
import {validateFoundation} from '../liuren-deterministic-io.mjs';
const root=fileURLToPath(new URL('../../',import.meta.url));
const saved=JSON.parse(await fs.readFile(path.join(root,'output/liuren-energy-yin-20261106-1443/chart-result.json'),'utf8'));
const facts=saved.facts,d=buildFacts(facts),basic=d.basic_states;
const restore=t=>t.rows.map(row=>Object.fromEntries(t.columns.map((k,i)=>[k,row[i]])));

test('all 12 heavenly branches and 12 generals are exported, no scoring',()=>{
 assert.equal(basic.branches.rows.length,12);assert.equal(basic.generals.rows.length,12);
 assert.equal(basic.chart_sha256,hash(facts));assert.equal(basic.score,undefined);
 assert.ok(!JSON.stringify(basic).includes('energy-fixed'));
});
test('focus carries the selected branch and its general with the same chart binding',()=>{
 const r=focusFacts(d,['丑']);assert.equal(r.basic_states.branches.rows.length,1);
 assert.equal(r.basic_states.generals.rows.length,1);assert.equal(r.basic_states.branches.rows[0][1],'丑');
 assert.equal(r.basic_states.chart_sha256,basic.chart_sha256);
});
test('separate stem and element growth; explicit ground, yin and carrier',()=>{
 const m=restore(basic.branches).find(x=>x.branch==='午'),j=restore(basic.generals).find(x=>x.general==='白虎');
 assert.equal(m.ground,'戌');assert.equal(m.direct_yin,'寅');assert.equal(m.growth_ground,'墓');assert.equal(m.growth_yin,'长生');
 assert.equal(j.carrier,'午');assert.equal(j.ground,'戌');assert.equal(j.growth_carrier,'沐浴');assert.equal(j.growth_ground,'衰');
 assert.equal(j.month_qi.profiles['quarter-earth'],'相');assert.equal(m.month_qi.profiles['quarter-earth'],'休');
 assert.equal(d.stems.find(x=>x.symbol==='丁').growth.upper,'病'); // explicitly stem-specific, not generic fire
});
test('季月分歧不静默取表，不把旺相写成同一得令',()=>{
 const m=restore(basic.branches).find(x=>x.branch==='辰');
 assert.equal(m.month_qi.adopted,null);assert.equal(m.month_qi.de_ling,null);
 assert.equal(m.month_qi.profiles['four-seasons'],'休');assert.equal(m.month_qi.profiles['quarter-earth'],'旺');
});
test('寅自身不空而坐空，午自身空；白虎不自动继承自身空',()=>{
 const rows=restore(basic.branches),yin=rows.find(x=>x.branch==='寅'),wu=rows.find(x=>x.branch==='午');
 assert.equal(yin.self_void,false);assert.equal(yin.sitting_void,true);assert.equal(wu.self_void,true);
 const j=restore(basic.generals).find(x=>x.general==='白虎');assert.equal(j.void_context.carrier_void,true);assert.equal(j.void_context.self_xun_void,null);
});
test('绝兼受生与长生兼泄保留同处方向，不裁救成',()=>{
 const rows=restore(basic.coexistence),chou=rows.find(x=>x.subject==='丑'&&x.reference==='地盘巳'),chen=rows.find(x=>x.subject==='辰'&&x.reference==='地盘申');
 assert.ok(chou.flags.includes('临绝并见受生'));assert.equal(chou.reference_to_subject,'生');
 assert.ok(chen.flags.includes('长生兼泄'));assert.equal(chen.subject_to_reference,'生');
 assert.equal(chou.rescued,undefined);
});
test('完整内战、夹克链保留，神将关系和将地关系均导出',()=>{
 const rows=restore(basic.local),zi=rows.find(x=>x.node_ref==='D_B0'),xu=rows.find(x=>x.node_ref==='D_B10');
 assert.equal(zi.formation_flags.内战,true);assert.equal(xu.formation_flags.夹克,true);
 assert.equal(rows.find(x=>x.node_ref==='D_B6').ground_to_general[0].value,'生');
});
test('旧事实不变，旧格式可重建且新字段篡改会被校验发现',()=>{
 const previous=JSON.stringify(facts);buildFacts(facts);assert.equal(JSON.stringify(facts),previous);
 const stub=deterministic=>({chart:{facts},deterministic:{...deterministic,special_requirements:[]},entities:[],observations:[],questions:[]});
 validateFoundation(stub(buildFacts(facts,{basicStates:false})));validateFoundation(stub(d));
 const bad=structuredClone(d);bad.basic_states.generals.rows[0][1]='白虎';assert.throws(()=>validateFoundation(stub(bad)),/deterministic facts changed/);
});
test('unusable chart cannot get an apparently resolved basic table',async()=>{
 const r=await enrichBasicStates({ok:false,validation:{ok:false},facts});assert.equal(r.basic_state_status,'chart_unusable');assert.equal(r.basic_states,undefined);
});
test('resolved route returns same full table with no second engine invocation',async()=>{
 const r=await runResolvedChart({datetime:'2026-11-06T14:43'},{persist:false});
 assert.equal(r.basic_state_status,'resolved');assert.deepEqual(r.basic_states,buildFacts(r.facts).basic_states);
 // Hashes bind the exact facts snapshot, including serialization identity.
 // Compare states with the historical fixture separately from that identity.
 const {chart_sha256:currentHash,...current}=r.basic_states;
 const {chart_sha256:historicalHash,...historical}=basic;
 assert.equal(currentHash,hash(r.facts));assert.deepEqual(current,historical);assert.equal(r.basic_state_archive,null);
});
test('manual pillars have no fabricated date and nonseasonal-month states agree',async()=>{
 const r=await runResolvedChart({mode:'manual-pillars',pillars:{year:'甲子',month_branch:'子',day:'乙丑',hour_branch:'子'},month_general:'午'},{persist:false});
 assert.equal(r.facts.event_datetime,null);assert.ok(restore(r.basic_states.branches).every(x=>x.month_qi.status==='profiles_agree'));
});
test('sidecar is hash-bound and immutable; historical archive stays byte-identical',async t=>{
 const folder=await fs.mkdtemp(path.join(os.tmpdir(),'liuren-basic-state-'));
 t.after(async()=>{assert.equal(path.dirname(path.resolve(folder)),path.resolve(os.tmpdir()));assert.ok(path.basename(folder).startsWith('liuren-basic-state-'));await fs.rm(folder,{recursive:true,force:true});});
 const archive=path.join(folder,'chart.json'),raw=JSON.stringify({_direct:{facts}});await fs.writeFile(archive,raw);
 const input={ok:true,validation:{ok:true},facts,archive:{path:archive,sha256:hash(raw)}};
 const a=await enrichBasicStates(input),b=await enrichBasicStates(input);assert.deepEqual(a.basic_state_archive,b.basic_state_archive);
 assert.equal(await fs.readFile(archive,'utf8'),raw);assert.equal(hash(await fs.readFile(a.basic_state_archive.path,'utf8')),a.basic_state_archive.sha256);
 await fs.appendFile(a.basic_state_archive.path,'x');await assert.rejects(()=>enrichBasicStates(input));
});
test('enhancement imports no research numeric module',async()=>{
 for(const file of ['tools/liuren-basic-state-view.mjs','tools/liuren-basic-states.mjs']){
  const source=await fs.readFile(path.join(root,file),'utf8');assert.ok(!/from\s+['"].*(?:output|joint-v03|fixed-v02)/.test(source));
 }
});
