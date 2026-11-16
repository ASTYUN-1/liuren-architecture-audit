import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {trialStrengthBasis,withTrialStrengthBasis,localStrengthMeaning,withTrialChartBasis} from '../liuren-trial-decision.mjs';
const root=fileURLToPath(new URL('../../',import.meta.url));
const load=async p=>JSON.parse(await fs.readFile(path.isAbsolute(p)?p:path.join(root,p),'utf8'));
const actor=(id,single_palace,adjusted)=>({id,role:'test',basis:'synthetic',single_palace,adjusted});
test('strong ghost numerical attack cannot become an independent body-weak adverse reason',()=>{
 const raw={actors:[actor('T:申',8.3,7.7),actor('S:甲',2.432,1.519)],applied_relations:[{source:'T:申',target:'S:甲',type:'克',received:-.886}]};
 const out=withTrialStrengthBasis(raw,'甲');
 assert.deepEqual(out.actors,raw.actors);assert.deepEqual(out.applied_relations,raw.applied_relations);
 const b=out.trial_judgment_basis;assert.equal(b.final_verdict,null);assert.equal(b.rejected_inference_chains.length,1);
 assert.match(b.actors[0].harm_interpretation,/旺鬼凶害减轻/);
 assert.equal(b.actors[1].original.score,2.432);assert.equal(b.actors[1].scenario.score,1.519);
});
test('weak and zero ghosts retain adverse tendency rather than becoming harmless',()=>{
 for(const e of [0,.5,2.49]){
  const b=trialStrengthBasis({actors:[actor('T:申',e,e)],applied_relations:[]},'甲');
  assert.equal(b.actors[0].day_ghost,true);assert.match(b.actors[0].harm_interpretation,/衰鬼不利/);
  assert.equal(b.actors[0].scenario.usable,null);assert.match(b.actors[0].scenario.tendency,/偏不利/);
 }
 assert.equal(localStrengthMeaning(null).level,null);assert.match(localStrengthMeaning(null).tendency,/缺计算/);
});
test('control is not automatically damage; support candidates do not silently become applied edges',()=>{
 const raw={actors:[actor('S:乙',2,1.9),actor('T:未',4,3.9)],applied_relations:[{source:'S:乙',target:'T:未',type:'克',received:-.1}],review:{relation_candidates:[{submitted:false,actors:['T:午','T:未'],facts:[{type:'five_elements',value:'生'}]}]}};
 const b=trialStrengthBasis(raw,'乙');assert.equal(b.rejected_inference_chains.length,0);
 assert.match(b.relation_meaning_required[0].event_effect,/取财/);assert.equal(b.primary_support_candidates.length,1);
 assert.equal(raw.applied_relations.length,1);assert.equal(b.final_verdict,null);
});
test('trial adapter preserves every frozen clinical numerical value',async()=>{
 const a=await load('output/opencode-strength-meaning-20261115-five-04-deepseek/execution-audit.json');
 const raw=a.cases[1].compute_calls[0].output;const copy=structuredClone(raw);
 const out=withTrialStrengthBasis(raw,'甲');assert.deepEqual(raw,copy);
 for(const key of Object.keys(raw))assert.deepEqual(out[key],raw[key],key);
 assert.equal(out.trial_judgment_basis.rejected_inference_chains[0].source,'T:申');
});
test('short material reads registered trial domain; normal reader keeps exact original module',async()=>{
 const run=flag=>execFileSync('python',['-X','utf8','tools/liuren-materials.py','--request',JSON.stringify({action:'method',modules:['class-selection-trial','exam'],_class_selection_trial:flag})],{cwd:root,encoding:'utf8',maxBuffer:200000});
 const trial=run(true),normal=run(false);
 assert.ok(trial.includes('"module": "trial-domain-exam"'));assert.ok(trial.includes('"requestedModule": "exam"'));
 assert.ok(!trial.includes('## 判断流程'));assert.ok(trial.includes('河魁'));assert.ok(trial.includes('幕贵'));
 assert.ok(normal.includes('"module": "exam"'));assert.ok(normal.includes('## 判断流程'));
 const p=await load('.opencode/liuren-active.json'),m=await load(p.runtime+'/manifest.json');
 assert.equal(Object.keys(m.classSelectionTrial.domainModules).length,m.domains.length);
});
test('full professional core and domain sources remain byte-identical to 58',async()=>{
 const p=await load('.opencode/liuren-active.json');const old='runtime/liuren/20261115-strength-meaning-58';const m=await load(old+'/manifest.json');
 const sha=x=>createHash('sha256').update(x).digest('hex');
 for(const k of [...m.domains,'judgment-core']){
  const rel=m.modules[k].file;
  assert.equal(sha(await fs.readFile(path.join(root,p.runtime,rel))),sha(await fs.readFile(path.join(root,old,rel))),k);
 }
 const source=await fs.readFile(path.join(root,'.opencode/tools/liuren_materials.ts'),'utf8');
 assert.match(source,/context.agent==='liuren'/);assert.match(source,/_class_selection_trial:trial/);
 const cfg=await load('opencode.json'),prior=await load('output/liuren-trial-decision-59/before/opencode.json');
 assert.equal(cfg.agent.liuren.model,prior.agent.liuren.model);
});
test('chart adapter adds scoped policy without mutating chart or assuming unselected class roles',()=>{
 const raw={ok:true,facts:{day:{symbol:'甲'},heaven_earth:[]},archive:{path:'x',sha256:'abc'}};
 const copy=structuredClone(raw),out=withTrialChartBasis(raw);assert.deepEqual(raw,copy);
 assert.deepEqual(out.archive,raw.archive);assert.equal(out.trial_judgment_policy.id,'liuren-trial-decision-61');
 assert.equal(out.facts.trial_judgment_policy.id,'liuren-trial-decision-61');
 assert.deepEqual(withTrialChartBasis({ok:false}),{ok:false});
});

test('unselected weak and zero day ghosts still expose their adverse state in chart view',()=>{
 const raw={ok:true,facts:{heaven_earth:[{id:'T:申',di:'巳',tian:'申',tianjiang:'勾陈',liuqin:'官鬼',state:{strength_index:{四季:0,季土:.6}}},{id:'T:未',liuqin:'妻财',state:{strength_index:6}}]}};
 const out=withTrialChartBasis(raw);const rows=out.trial_chart_basis.day_ghost_observations;
 assert.equal(rows.length,1);assert.equal(rows[0].id,'T:申');assert.match(rows[0].meaning.四季.tendency,/偏不利/);
 assert.match(rows[0].meaning.季土.tendency,/偏不利/);assert.match(rows[0].restriction,/不能改称无强压/);
 assert.equal(raw.trial_chart_basis,undefined);
});
