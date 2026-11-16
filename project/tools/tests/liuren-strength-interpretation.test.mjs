import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {STRENGTH_INTERPRETATION as policy} from '../liuren-strength-interpretation.mjs';
import {strengthBand,calculateSelectedStrength} from '../liuren-palace-strength.mjs';
import {chartView} from '../liuren-chart-view.mjs';
const root=fileURLToPath(new URL('../../',import.meta.url));
const load=async f=>JSON.parse(await fs.readFile(path.isAbsolute(f)?f:path.join(root,f),'utf8'));
const pointer=await load('.opencode/liuren-active.json');
test('zero and low strength never encode harmlessness; high ghost strength never encodes greater harm',()=>{
 assert.equal(policy.score_is_usability,false);
 assert.equal(policy.low_score_means_harmless,false);assert.equal(policy.zero_means_harmless,false);
 assert.equal(policy.high_ghost_score_means_more_harm,false);assert.equal(policy.control_delta_is_event_harm,false);
 assert.equal(strengthBand(0),'本模型计算下限');assert.equal(strengthBand(0.99),'极衰');assert.equal(strengthBand(1),'衰弱');
 assert.equal(strengthBand(2.5),'偏弱至中等');assert.equal(strengthBand(5),'较旺');assert.equal(strengthBand(7.5),'强旺');
 assert.equal(strengthBand(null),null);
});
test('changing interpretation preserves every frozen57 selected numeric result',async()=>{
 const prior=await load('output/liuren-xianfeng-five-20261114/clinical-combined-rescue.json');
 const cases=await load('output/liuren-xianfeng-five-20261114/facts.json');
 const archive=await load(cases.cases[1].archive.path);
 const result=calculateSelectedStrength(archive._direct.facts,prior.request);
 for(const a of result.actors){
  const old=prior.result.actors.find(x=>x.id===a.id);
  for(const key of ['single_palace','adjusted','delta'])assert.equal(a[key],old[key],a.id+':'+key);
 }
 assert.deepEqual(result.applied_relations,prior.result.applied_relations);
 assert.equal(result.strength_interpretation.id,'liuren-strength-meaning-58');
 const view=chartView(archive._direct.facts,{shensha:archive._direct.shensha_resolution});
 assert.deepEqual(view.strength_interpretation,result.strength_interpretation);
 assert.deepEqual(view.strength_model.bands,policy.bands);
});
test('primary prompt and short material both explicitly deliver all boundaries and unified rule',async()=>{
 const cfg=await load('opencode.json');
 const short=await fs.readFile(path.join(root,pointer.runtime,'references/class-selection-trial.md'),'utf8');
 for(const text of [cfg.agent.liuren.prompt,short]){
  for(const required of ['官鬼','喜旺恶衰','零','无害','通路','2.5','7.5','4至6'])assert.ok(text.includes(required),required);
 }
 const backup=await load('output/liuren-strength-meaning-58/before/opencode.json');
 assert.equal(cfg.agent.liuren.model,backup.agent.liuren.model);
});
