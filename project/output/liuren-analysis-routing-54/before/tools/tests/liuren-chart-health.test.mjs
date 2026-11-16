// Test the complete active chart path and failures that file hashes alone miss.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import crypto from 'node:crypto';
import { loadShenshaPolicy, runChartWithShensha } from '../liuren-shensha.mjs';
import { runResolvedChart } from '../liuren-resolved-chart.mjs';
import { ROOT } from '../liuren-direct.mjs';
import tool from '../../.opencode/tools/liuren_chart.ts';

const hash=b=>crypto.createHash('sha256').update(b).digest('hex');
const ascii=v=>JSON.stringify(v).replace(/[\u007f-\uffff]/g,c=>'\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'));
const identity=files=>hash('{'+Object.keys(files).sort().map(k=>ascii(k)+': '+ascii(files[k])).join(', ')+'}');
const active=JSON.parse(await fs.readFile(path.join(ROOT,'.opencode/liuren-active.json'),'utf8'));
const runtime=path.join(ROOT,active.runtime);
const sourceManifest=JSON.parse(await fs.readFile(path.join(runtime,'manifest.json'),'utf8'));
const sourcePolicy=JSON.parse(await fs.readFile(path.join(runtime,sourceManifest.shenshaPolicyFile),'utf8'));

async function fixture(t,modify=()=>{},tamper=false) {
  const root=await fs.mkdtemp(path.join(os.tmpdir(),'liuren-policy-health-'));
  // Keep synthetic state only; no real config or archives are changed.
  t.after(async()=>{
    assert.equal(path.dirname(path.resolve(root)),path.resolve(os.tmpdir()));
    assert.ok(path.basename(root).startsWith('liuren-policy-health-'));
    await fs.rm(root,{recursive:true,force:true});
  });
  const policy=structuredClone(sourcePolicy);
  const pointer={...active,runtime:'runtime/test'};
  const manifest={...sourceManifest,files:{},shenshaPolicyFile:'references/policy.json'};
  modify({policy,pointer,manifest});
  const body=JSON.stringify(policy);
  manifest.files[manifest.shenshaPolicyFile||'references/policy.json']=hash(body);
  manifest.version=identity(manifest.files);pointer.methodVersion=manifest.version;
  await fs.mkdir(path.join(root,'runtime/test/references'),{recursive:true});
  await fs.mkdir(path.join(root,'.opencode'));
  await fs.writeFile(path.join(root,'runtime/test/references/policy.json'),body+(tamper?'\n':''));
  await fs.writeFile(path.join(root,'runtime/test/manifest.json'),JSON.stringify(manifest));
  await fs.writeFile(path.join(root,'.opencode/liuren-active.json'),JSON.stringify(pointer));
  return root;
}

test('active release, manifest and shensha table identity agree, not just file hashes',async()=>{
  const loaded=await loadShenshaPolicy();
  assert.equal(active.release,sourceManifest.release);
  assert.equal(loaded.policy.release,active.release);
  assert.equal(loaded.sha256,sourceManifest.files[sourceManifest.shenshaPolicyFile]);
});

test('hash-valid stale policy release reproduces the reported failure before any engine/archive operation',async t=>{
  const root=await fixture(t,({policy})=>{policy.release='old-workflow';});
  let engineCalls=0;
  await assert.rejects(runChartWithShensha(async()=>{engineCalls++;throw Error('must not run');},
    {policyRoot:root}),/神煞表版本不一致.*重复起课无效/);
  assert.equal(engineCalls,0);
  await assert.rejects(fs.access(path.join(root,'排盘存档')));
});

test('tampered content, unsupported schema, foreign manifest and escaped path stay rejected',async t=>{
  const cases=[
    [()=>{},true,/哈希不一致/],
    [({policy})=>{policy.schema='unknown';},false,/格式不支持/],
    [({manifest})=>{manifest.release='foreign';},false,/活动指针不一致/],
    [({manifest})=>{manifest.shenshaPolicyFile='../outside.json';},false,/路径越界/],
    [({manifest})=>{delete manifest.shenshaPolicyFile;},false,/没有确定的神煞采用表/],
  ];
  for(const [modify,tamper,expected] of cases) {
    const root=await fixture(t,modify,tamper);
    await assert.rejects(loadShenshaPolicy(root),expected);
  }
});

test('resolved time, manual pillars and invalid inputs pass through the complete public layer',async()=>{
  const dated=await runResolvedChart({datetime:'2026-08-04T14:32'}, {persist:false});
  assert.equal(dated.ok,true);
  assert.deepEqual(dated.facts.pillars,['丙午','乙未','庚戌','癸未']);
  assert.equal(dated.shensha_resolution.release,active.release);
  const manual=await runResolvedChart({mode:'manual-pillars',pillars:{year:'甲子',month_branch:'子',day:'乙丑',hour_branch:'子'},month_general:'午'}, {persist:false});
  assert.equal(manual.ok,true);
  assert.equal(manual.shensha_resolution.release,active.release);
  await assert.rejects(runResolvedChart({datetime:'2026-02-30T12:00'}, {persist:false}),
    error=>error.code==='INVALID_DATETIME');
  const invalid=JSON.parse(await tool.execute({datetime:'2026-02-30T12:00'},
    {abort:new AbortController().signal}));
  assert.equal(invalid.ok,false);
  assert.equal(invalid.error.code,'INVALID_DATETIME');
});

test('reported native now + Beijing time + 2001 female succeeds on three separate invocations with valid saved exports',async()=>{
  const archives=[];
  for(let n=0;n<3;n++) {
    const result=JSON.parse(await tool.execute({mode:'now',timezone:'Asia/Shanghai',
      participants:[{sex:'女',birth_year:2001}],label:'工具健壮性回归'},
      {abort:new AbortController().signal}));
    assert.equal(result.ok,true);
    assert.equal(result.validation,undefined);
    assert.equal(result.facts.heaven_earth.length,12);
    assert.equal(result.facts.lessons.length,4);
    assert.equal(result.facts.transmissions.length,3);
    assert.equal(result.shensha_resolution,undefined);
    assert.equal(result.facts.schema,'liuren-ai-chart-v1');
    assert.ok(result.chart_file.path);
    const bytes=await fs.readFile(result.archive.path);
    assert.equal(hash(bytes),result.archive.sha256);
    const record=JSON.parse(bytes);
    assert.equal(record._direct.shensha_resolution.release,active.release);
    const ai=JSON.parse(await fs.readFile(result.chart_file.path,'utf8'));
    assert.deepEqual(ai,result.facts);
    for(const item of record._direct.shensha_resolution.items.filter(x=>x.status==='resolved')){
      assert.deepEqual(ai.heaven_earth.filter(r=>r.shensha.some(s=>s[0]===item.id)).map(r=>r.tian).sort(),item.places.map(r=>r.tian).sort());
    }
    archives.push(result.archive.path);
  }
  assert.equal(new Set(archives).size,3);
});
