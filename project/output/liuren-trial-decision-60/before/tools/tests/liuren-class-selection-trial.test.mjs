import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {registerHooks} from 'node:module';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
const root=fileURLToPath(new URL('../../',import.meta.url));
registerHooks({resolve(specifier,context,next){if(specifier==='@opencode-ai/plugin')return next(pathToFileURL(path.join(root,'.opencode/node_modules/@opencode-ai/plugin/dist/index.js')).href,context);return next(specifier,context);}});
const {default:plugin}=await import('../../.opencode/plugins/liuren-adjudication.ts');
const load=async f=>JSON.parse(await fs.readFile(path.join(root,f),'utf8'));
const pointer=await load('.opencode/liuren-active.json');
const config=await load('opencode.json');
const hooks=await plugin({directory:root,client:{session:{messages:async()=>({data:[]})}}});
const context={agent:'liuren',sessionID:'trial_synthetic_no_model'};
test('default short mode denies delegation and all report pipeline tools',()=>{
 assert.equal(pointer.defaultMode,'class-selection-trial');
 const p=config.agent.liuren.permission;
 for(const name of ['liuren_adjudication_packet','liuren_adjudication_result','liuren_adjudication_read','liuren_adjudication_submit','liuren_adjudication_audit','task_result'])assert.equal(p[name],'deny');
 assert.equal(p.task['*'],'deny');assert.equal(p.task['liuren-adjudicator'],'deny');
});
test('workflow help returns direct short route without full-flow readiness or dispatch',async()=>{
 const out=JSON.parse(await hooks.tool.liuren_tool_help.execute({topic:'workflow',domains:['exam']},context));
 assert.equal(out.execution_health.ready,true);assert.equal(out.adjudication_enabled,false);
 assert.equal(out.mode,'class-selection-trial');assert.equal(out.readiness,undefined);
 assert.deepEqual(out.required_modules,['class-selection-trial']);
 assert.ok(out.steps.every(s=>!s.includes('packet')&&!s.includes('task')));
});
test('packet refuses trial before validation or any task creation',async()=>{
 await assert.rejects(()=>hooks.tool.liuren_adjudication_packet.execute({packet:{}},context),/LIUREN_CLASS_SELECTION_TRIAL/);
});
test('actual materials tool reads the short module and exam without the full workflow',()=>{
 const out=execFileSync('python',['-X','utf8','tools/liuren-materials.py','--request',JSON.stringify({action:'method',modules:['class-selection-trial','exam']})],{cwd:root,encoding:'utf8',maxBuffer:200000});
 assert.ok(out.includes('分类取用短答试验'));assert.ok(out.includes('学业考核'));
 assert.equal((out.match(/LIUREN_METHOD_BEGIN/g)??[]).length,2);
 assert.ok(!out.includes('# 本机占事共用判断规范'));
});

test('native primary materials adapter selects the trial domain while other callers keep full source',async()=>{
 const {default:materialsTool}=await import('../../.opencode/tools/liuren_materials.ts');
 const args={action:'method',modules:['class-selection-trial','exam']};
 const primary=await materialsTool.execute(args,{...context,directory:root,abort:new AbortController().signal});
 assert.ok(primary.output.includes('"module": "trial-domain-exam"'));
 assert.ok(!primary.output.includes('## 判断流程'));
 const normal=await materialsTool.execute(args,{...context,agent:'build',directory:root,abort:new AbortController().signal});
 assert.ok(normal.output.includes('"module": "exam"'));
 assert.ok(normal.output.includes('## 判断流程'));
});
test('numeric and timing computation refuse trial even when called directly',async()=>{
 for(const action of ['quantity','calendar','evaluation','methods','imagery'])await assert.rejects(()=>hooks.tool.liuren_compute.execute({action},context),/LIUREN_CLASS_SELECTION_TRIAL/);
});

test('trial can compute selected strength from a real chart archive without creating an adjudication',async()=>{
 const {default:chartTool}=await import('../../.opencode/tools/liuren_chart.ts');
 const chart=JSON.parse(await chartTool.execute({mode:'datetime',datetime:'2026-11-14T12:00:00+08:00',label:'strength57-interface'}, {...context,abort:new AbortController().signal}));
 assert.ok(chart.ok);assert.ok(chart.archive.sha256);
 assert.equal(chart.trial_judgment_policy.id,'liuren-trial-decision-59');
 assert.equal(chart.facts.strength_interpretation.score_is_usability,false);
 assert.equal(chart.facts.strength_interpretation.high_ghost_score_means_more_harm,false);
 const out=JSON.parse(await hooks.tool.liuren_compute.execute({action:'strength',archive:chart.archive,strength:{
  mode:'selected_relations',season_profile:'four-seasons',season_basis:'固定工程表，只核接口，不作案例预测',
  actors:[{id:'T:酉',role:'工程假设作用方',basis:'接口验证预先指定金生水'}, {id:'T:子',role:'工程假设主类',basis:'接口验证指定，不验证专业取类'}],
  links:[{source:'T:酉',target:'T:子',basis:'工程检验选定金生水关系传输'}],review:true
 }},context));
 assert.deepEqual(out.actors.map(a=>a.id),['T:酉','T:子']);
 assert.equal(out.quantity_basis.scope,'selected_relations');assert.ok(out.review);
 assert.equal(out.coverage.semantic_role_validated,false);assert.equal(out.coverage.event_verdict_supported,false);
 assert.equal(out.calculation_receipt,undefined);
 assert.equal(out.strength_interpretation.low_score_means_harmless,false);
 assert.equal(out.strength_interpretation.bands[0].label,'本模型计算下限');
 assert.equal(out.trial_judgment_basis.policy.id,'liuren-trial-decision-59');
 assert.equal(out.trial_judgment_basis.final_verdict,null);
 await assert.rejects(()=>hooks.tool.liuren_compute.execute({action:'strength',strength:{mode:'single_palace',season_profile:'four-seasons',season_basis:'工程',actors:[{id:'T:子',role:'工程',basis:'接口'}]}},context),/LIUREN_COMPUTE_ARCHIVE_REQUIRED/);
});
test('frozen baseline, domains and Codex protocol retained; core changes confined to approved strength meaning',async()=>{
 const before=await load('output/liuren-class-selection-trial-56/before.json');
 const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
 for(const [f,h] of Object.entries(before.frozen))assert.equal(hash(await fs.readFile(path.join(root,f))),h,f);
 const old=await load('runtime/liuren/20261114-tool-reliability-55/manifest.json');
 for(const f of Object.keys(old.files).filter(f=>f.startsWith('domains/')))assert.equal(hash(await fs.readFile(path.join(root,pointer.runtime,f))),old.files[f],f);
 const prior=await fs.readFile(path.join(root,'runtime/liuren/20261114-class-strength-trial-57/references/judgment-core.md'),'utf8');
 const current=await fs.readFile(path.join(root,pointer.runtime,'references/judgment-core.md'),'utf8');
 const omitU02=s=>s.replace(/- \*\*U02 喜旺恶衰。\*\*[\s\S]*?(?=\n- \*\*U03)/,'');
 assert.equal(omitU02(current),omitU02(prior).replace('2.5不是失用开关；','2.5不是失用开关；标签是旺衰层级，非可用程度；'));
 for(const f of ['tools/liuren-adjudication-files.mjs','tools/liuren-core-handoff.mjs','integrations/codex/daliuren-codex/SKILL.md'])assert.equal(hash(await fs.readFile(path.join(root,f))),before.files[f],f);
});
