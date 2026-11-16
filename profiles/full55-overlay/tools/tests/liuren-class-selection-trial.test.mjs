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
test('numeric and timing computation refuse trial even when called directly',async()=>{
 for(const action of ['quantity','strength','calendar','evaluation','methods','imagery'])await assert.rejects(()=>hooks.tool.liuren_compute.execute({action},context),/LIUREN_CLASS_SELECTION_TRIAL/);
});
test('full professional core, domains and Codex integration retain baseline bytes',async()=>{
 const before=await load('output/liuren-class-selection-trial-56/before.json');
 const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
 for(const [f,h] of Object.entries(before.frozen))assert.equal(hash(await fs.readFile(path.join(root,f))),h,f);
 const old=await load('runtime/liuren/20261114-tool-reliability-55/manifest.json');
 for(const f of Object.keys(old.files).filter(f=>f.startsWith('domains/')||f==='references/judgment-core.md'))assert.equal(hash(await fs.readFile(path.join(root,pointer.runtime,f))),old.files[f],f);
 for(const f of ['tools/liuren-adjudication-files.mjs','tools/liuren-core-handoff.mjs','integrations/codex/daliuren-codex/SKILL.md'])assert.equal(hash(await fs.readFile(path.join(root,f))),before.files[f],f);
});
