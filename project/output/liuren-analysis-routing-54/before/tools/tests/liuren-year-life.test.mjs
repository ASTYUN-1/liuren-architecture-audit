import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {registerHooks} from 'node:module';
import {resolveLife,computeLife,lifeInputSchema} from '../liuren-year-life.mjs';
import {runChart,prepareRequest} from '../liuren-direct.mjs';
import {runResolvedChart} from '../liuren-resolved-chart.mjs';
import {exportAIChart} from '../liuren-chart-view.mjs';
import {resolveChartArchive} from '../liuren-adjudication-files.mjs';
import {validateInput} from '../liuren-adjudication-contract.mjs';
import {prepareFoundation} from '../liuren-deterministic-io.mjs';
import {makeReadingCore} from '../liuren-core-handoff.mjs';
import {createComputeSchemas} from '../liuren-compute-schema.mjs';
import {packet} from './fixtures/liuren-adjudication-v2.mjs';
const ROOT=fileURLToPath(new URL('../../',import.meta.url));
registerHooks({resolve(s,c,next){if(s==='@opencode-ai/plugin')return next(pathToFileURL(path.join(ROOT,'.opencode/node_modules/@opencode-ai/plugin/dist/index.js')).href,c);return next(s,c);}});
const {tool}=await import('@opencode-ai/plugin');
const {default:chartTool}=await import('../../.opencode/tools/liuren_chart.ts');
const {default:plugin}=await import('../../.opencode/plugins/liuren-adjudication.ts');
const native=await plugin({directory:ROOT,client:{}}),schemas=createComputeSchemas(tool.schema);
const B=[...'子丑寅卯辰巳午未申酉戌亥'],G=[...'甲乙丙丁戊己庚辛壬癸'];
const C=Array.from({length:60},(_,i)=>G[i%10]+B[i%12]);
const chart={pillars:['丙午','乙未','庚戌','癸未'],event_datetime:'2026-08-04T14:32:00+08:00',heaven_earth:B.map((b,i)=>({di:b,tian:B[(i+3)%12],tianjiang:'将'+i}))};

test('2005, 05 and 99 adopt birth-year life without birthday or age',()=>{
 for(const birth_year of [2005,'2005','05',5,'05年出生']){
  const r=resolveLife({birth_year,sex:'男'},chart);assert.equal(r.birth_year,2005);assert.equal(r.birth.pillar,'乙酉');assert.equal(r.xingnian.pillar,'丁亥');assert.equal(r.adopted,true);assert.deepEqual(r.missing,[]);
 }
 const r=resolveLife({birth_year:'99',sex:'女'},chart);assert.equal(r.birth_year,1999);assert.equal(r.birth.pillar,'己卯');assert.equal(r.xingnian.pillar,'乙巳');
});

test('甲子 and 申命 require no unique Gregorian birth year; a single branch never invents stems',()=>{
 const a=resolveLife({birth_pillar:'甲子',sex:'男'},chart);assert.equal(a.birth.branch,'子');assert.equal(a.xingnian.pillar,'戊申');assert.equal(a.birth_year,undefined);assert.equal(a.age,undefined);
 const b=resolveLife({birth_pillar:'申命',sex:'男'},chart);assert.equal(b.birth.branch,'申');assert.equal(b.xingnian.branch,'子');assert.equal(b.xingnian.pillar,undefined);assert.equal(b.birth_year,undefined);
 assert.deepEqual(b.birth.position,{earth_branch:'申',upper_branch:'亥',upper_general:'将8',direct_yin_branch:'寅',direct_yin_general:'将11'});
 assert.equal(resolveLife({birth_branch:'申',sex:'女'},chart).xingnian.branch,'戌');
});

test('missing sex retains adopted life and both directional candidates; stated xingnian is still adopted',()=>{
 const r=resolveLife({birth_year:2005},chart);assert.equal(r.birth.branch,'酉');assert.equal(r.adopted,true);assert.deepEqual(r.missing,['sex']);assert.deepEqual(r.xingnian_candidates.map(x=>[x.sex,x.pillar]),[['男','丁亥'],['女','辛亥']]);
 const x=resolveLife({xingnian:'戌'},chart);assert.equal(x.xingnian.branch,'戌');assert.equal(x.adopted,true);assert.equal(x.birth_candidates.length,2);
});

test('explicit life and explicit xingnian win locally over calculations without dropping valid inputs',()=>{
 const r=resolveLife({birth_year:2005,birth_pillar:'申',sex:'男',xingnian:'甲戌'},chart);
 assert.equal(r.birth.branch,'申');assert.equal(r.xingnian.pillar,'甲戌');assert.equal(r.adopted,true);assert.deepEqual(r.conflicts.map(x=>x.field),['birth_year','xingnian']);
 const reverse=resolveLife({xingnian:'丁亥',sex:'男'},chart);assert.equal(reverse.birth.pillar,'乙酉');assert.equal(reverse.birth_year,undefined);
 assert.equal(resolveLife({xingnian_branch:'子',sex:'男'},chart).birth.branch,'申');
});

test('cyclic adapter agrees with independent age-by-age stepping for all 60 years and 150 ages',()=>{
 for(let y=0;y<60;y++)for(const sex of ['男','女']){
  let expected=sex==='男'?2:8;
  for(let age=1;age<=150;age++){
   const birth=C[((y-age+1)%60+60)%60],c={...chart,pillars:[C[y],...chart.pillars.slice(1)]};
   const full=resolveLife({birth_pillar:birth,sex},c),branch=resolveLife({birth_branch:birth[1],sex},c);
   assert.equal(full.xingnian.pillar,C[expected]);assert.equal(branch.xingnian.branch,C[expected][1]);
   expected=(expected+(sex==='男'?1:59))%60;
  }
 }
});

test('占课年柱 controls xingnian and manual reference dates never control life',async()=>{
 const input={mode:'manual-pillars',pillars:{year:'甲子',month_branch:'子',day:'乙丑',hour_branch:'子'},month_general:'午',participants:[{birth_year:'05',sex:'男'}]};
 const a=await runChart({...input,reference_datetime:'2000-01-01T12:00'},{persist:false}),b=await runChart({...input,reference_datetime:'2099-01-01T12:00'},{persist:false});
 assert.deepEqual(a.facts.year_life,b.facts.year_life);assert.equal(a.facts.year_life.participants[0].year_pillar,'甲子');assert.equal(a.facts.year_life.participants[0].birth_year,2005);
 assert.equal(a.facts.year_life.participants[0].xingnian.pillar,'乙巳');
});

test('year boundary follows chart year while birthday-free default life remains usable',()=>{
 const january={...chart,pillars:['乙巳',...chart.pillars.slice(1)],event_datetime:'2026-01-02T12:00:00+08:00'};
 const r=resolveLife({birth_year:2005,sex:'男'},january);assert.equal(r.birth.branch,'酉');assert.equal(r.xingnian.pillar,'丙戌');assert.equal(r.adopted,true);
 assert.throws(()=>resolveLife({birth_year:2027,sex:'男'},chart),/晚于/);
 for(const life of [{birth_pillar:'甲丑'},{birth_branch:'甲子'},{birth_year:'0005'},{birth_year:'no'},{sex:'男'},{}])assert.throws(()=>resolveLife(life,chart),/LIUREN_YEAR_LIFE/);
 assert.throws(()=>prepareRequest({datetime:'2026-08-04T14:32',participants:[{birth_year:2005,name:'private'}]}),/不支持name/);
});

test('legacy nominal-age interface retains prior results while raw unqualified age stays legacy',()=>{
 for(const [sex,age,expected] of [['男',96,'辛丑'],['男',97,'壬寅'],['女',21,'壬子']])assert.equal(computeLife({sex,age,age_basis:'虚岁-已核'},chart).xingnian,expected);
 assert.equal(computeLife({sex:'女',age:21,age_basis:'虚岁'},chart).xingnian,'壬子');
 const r=resolveLife({sex:'男',age:21},chart);assert.equal(r.adopted,false);assert.equal(r.birth,null);assert.equal(r.xingnian,null);
});

test('native chart, compute and packet schemas accept every life form and serialize without refs',()=>{
 const cases=[{birth_year:'05',sex:'男'},{birth_year:2005},{birth_pillar:'申'},{birth_pillar:'甲子',sex:'女'},{xingnian:'甲戌'},{xingnian_branch:'戌'}];
 for(const life of cases){
  assert.deepEqual(tool.schema.object(chartTool.args).parse({datetime:'2026-08-04T14:32',participants:[life]}).participants,[life]);
  assert.deepEqual(schemas.parse({action:'life',life}).life,life);
  assert.deepEqual(schemas.computation.parse({id:'C_life',action:'life',life}).life,life);
 }
 assert.throws(()=>lifeInputSchema(tool.schema).parse({birth_year:2005,name:'private'}),/Unrecognized/);
 for(const def of [chartTool,native.tool.liuren_compute,native.tool.liuren_adjudication_packet]){
  const full=tool.schema.toJSONSchema(tool.schema.object(def.args));assert.ok(!JSON.stringify(full).includes('"$ref"'));
 }
});

test('new life survives corrected archive, AI view, native packet, deterministic facts and reading core',async()=>{
 const args=tool.schema.object(chartTool.args).parse({datetime:'2026-08-04T14:32',participants:[{birth_year:'05',sex:'男'},{birth_pillar:'申',sex:'女'}],label:'年命适配合成测试'});
 const exported=JSON.parse(await chartTool.execute(args,{abort:new AbortController().signal})),life=exported.facts.year_life;
 assert.equal(life.participants[0].birth.branch,'酉');assert.equal(life.participants[0].xingnian.branch,'亥');assert.equal(life.participants[1].xingnian.branch,'戌');
 assert.equal(exported.facts.year_life_verified,undefined);assert.equal(exported.facts.participants,undefined);
 const p=packet();p.chart={source:'合成工程测试，非占断',archive:exported.archive};delete p.entities[0].position;
 const resolved=await resolveChartArchive(ROOT,p);assert.deepEqual(resolved.chart.facts.year_life,life);
 const prepared=validateInput(await prepareFoundation(ROOT,resolved));
 native.tool.liuren_adjudication_packet.args.packet.parse({...p,chart:{source:'合成工程测试',facts:resolved.chart.facts}});
 const computed=JSON.parse(await native.tool.liuren_compute.execute({action:'life',archive:exported.archive,life:{birth_pillar:'申',sex:'男'}},{agent:'liuren',sessionID:'synthetic_life_53'}));
 assert.equal(computed.life_branch,'申');assert.equal(computed.xingnian,'子');
 const core=JSON.parse((await makeReadingCore(ROOT,prepared)).core.content);assert.deepEqual(core.chart.year_life,life);
 assert.match(prepared.deterministic.engine_inventory.references.year_life,/year_life/);
});

test('a later life input reaches the core as a real computation receipt without recasting',async()=>{
 const r=await runResolvedChart({datetime:'2026-08-04T14:32'},{persist:false}),p=packet();p.chart={source:'同盘合成测试',facts:r.facts};delete p.entities[0].position;
 p.computation_requests=[{id:'C_life',action:'life',life:{birth_year:2005,sex:'男'}}];
 const prepared=validateInput(await prepareFoundation(ROOT,p)),core=JSON.parse((await makeReadingCore(ROOT,prepared)).core.content);
 const receipt=core.program.calculations.find(x=>x.id==='C_life');assert.equal(receipt.result.life_branch,'酉');assert.equal(receipt.result.xingnian,'丁亥');assert.equal(receipt.result.adopted,true);
 assert.deepEqual(prepared.chart.facts.pillars,r.facts.pillars);
});
