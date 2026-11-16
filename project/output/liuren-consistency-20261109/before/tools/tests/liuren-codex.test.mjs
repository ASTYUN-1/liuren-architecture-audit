import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {ROOT,execute,status} from '../liuren-codex.mjs';
import {runResolvedChart} from '../liuren-resolved-chart.mjs';
import {loadPacket} from '../liuren-adjudication-files.mjs';

const artifact=path.join(ROOT,'output/liuren-codex-tests',String(Date.now())+'-'+process.pid);
await fs.mkdir(artifact,{recursive:true});
const question='合成工程验收材料：只核对完整盘、绑定方法和报告传输，不预测天气或任何现实结果。';
const chart=await runResolvedChart({datetime:'2026-10-18T13:22',label:'Codex工程验收'});
assert.ok(chart.ok);
function input(){return {
 action:'packet',purpose:'transport-test',original_question:question,
 packet:{schema:'liuren-adjudication-input-v2',request_id:'codex-transport-'+Date.now(),
 chart:{source:'可信程序盘，合成工程验收，无预测验收',archive:chart.archive},
 questions:[{id:'Q_transport',domain:'weather',text:question,subject:'合成工程验收',stage:'传输验收',deadline:'本轮',
 success_criteria:'完整核心和引用可读取、完整报告可保存领取，不验证现实预测',alternatives:['传输通过','传输失败'],tasks:['outcome'],
 task_basis:[{task:'outcome',origin:'user_requested',request_quote:question,reason:'本轮为宿主适配的合成工程验收'}]}],
 facts:[{id:'F_test',text:'这是工程测试，不是真实天气预测。',source:'测试构造'}],
 entities:[{id:'S_test',question_ids:['Q_transport'],referent:'测试对象',branch:chart.facts.day_stem,mapping_basis:'仅用于验证程序坐标完整传递'}],
 observations:[],focus_issues:[],method_materials:[],method_modules:['void'],unknowns:['无真实预测任务']}
};}
let saved;
test('health checks unchanged shared runtime and implementation hashes',async()=>{
 const s=await status();assert.equal(s.ready,true);assert.equal(s.adjudicator.model,'gpt-6.1-sol');assert.equal(s.adjudicator.reasoning_effort,'high');
});
test('skill YAML and discovery metadata parse with available YAML parser',async()=>{
 const require=createRequire(path.join(ROOT,'.opencode/package.json')),yaml=require('yaml');
 const skill=path.join(ROOT,'integrations/codex/daliuren-codex');
 const md=await fs.readFile(path.join(skill,'SKILL.md'),'utf8'),match=md.match(/^---\r?\n([\s\S]+?)\r?\n---/);
 assert.ok(match);const meta=yaml.parse(match[1]);assert.equal(meta.name,'daliuren-codex');assert.ok(meta.description.length>30);
 assert.equal(yaml.parse(await fs.readFile(path.join(skill,'agents/openai.yaml'),'utf8')).policy.allow_implicit_invocation,true);
 assert.ok((await fs.stat(path.join(skill,'references/host.md'))).isFile());
});
test('packet preserves original question and whole program chart, native model settings and isolation',async()=>{
 saved=await execute(input());
 const loaded=await loadPacket(ROOT,saved.packet_ref),core=JSON.parse(loaded.raw);
 assert.equal(core.original_question,question);assert.equal(core.chart.schema,'liuren-ai-chart-v1');assert.deepEqual(core.chart.pillars,chart.facts.pillars);assert.equal(core.chart.heaven_earth.length,12);assert.deepEqual(loaded.envelope.packet.chart.facts,chart.facts);
 assert.equal(saved.spawn.model,'gpt-6.1-sol');assert.equal(saved.spawn.reasoning_effort,'high');assert.equal(saved.spawn.fork_turns,'none');
 assert.ok(!saved.spawn.message.includes('偏不成功'));assert.equal((await execute({action:'role',run:saved.run})).purpose,'transport-test');
 const role=await execute({action:'role',run:saved.run});
 assert.ok(role.professional_instructions.includes('严格采用核心U01—U11'));
 for(let i=1;i<=11;i++)assert.ok(core.shared_method.includes('**U'+String(i).padStart(2,'0')+' '));
 assert.ok(role.professional_instructions.includes('不是待确认清单'));
 assert.ok(core.shared_method.includes('财难为我得'));
 assert.ok(core.shared_method.includes('父母/生气'));
 assert.ok(core.shared_method.includes('干支胎同等重要'));
 assert.ok(core.shared_method.includes('通类定大方向'));
 assert.ok(core.shared_method.includes('吉事已动、凶事已萌'));
 assert.ok(!core.shared_method.includes('贪生停用能否扩大到财类'));
 assert.equal(core.chart.strength_model.id,'liuren-palace-strength-v1');
 assert.ok(core.shared_method.includes('单宫旺衰与取用后补算'));
 assert.ok(core.shared_method.includes('不能自行估算、手加分'));
 assert.ok(role.professional_instructions.includes('弱但仍有作用'));
});

test('main and bound Codex child share strength calculation and keep a receipt',async()=>{
 const request={action:'strength',strength:{mode:'single_palace',season_profile:'quarter-earth',season_basis:'合成宿主测试',
  actors:[{id:'T:子',role:'测试类神',basis:'传输验证指定'}]}};
 const main=await execute({action:'compute',request:{...request,archive:chart.archive}});
 const child=await execute({action:'compute',run:saved.run,request});
 assert.deepEqual(main,child);assert.equal(child.actors[0].delta,0);
 assert.ok((await fs.readdir(path.join(saved.run,'calculations'))).length>0);
 const target='T:'+chart.facts.transmissions[0].diZhi;
 for(const r of [
  {action:'quantity',quantity_method:{id:'WY67-shenjiang-base',target,basis:'合成传输验收'}},
  {action:'imagery',imagery:{id:'DF449-growth',target,reference:'ground',basis:'合成传输验收'}},
  {action:'evaluation',evaluation:{calendar:{start:'2026-10-18',end:'2026-10-18',timezone:'Asia/Shanghai',day_boundary:'civil-midnight'},strength:request.strength}}
 ]){
  assert.deepEqual(await execute({action:'compute',request:{...r,archive:chart.archive}}),await execute({action:'compute',run:saved.run,request:r}));
 }
 assert.equal((await execute({action:'compute',request:{action:'methods',methods:{kind:'quantity'}}})).methods.length,4);
});
test('material wrapper supplies current methods and rejects case/experience retrieval',async()=>{
 const result=await execute({action:'materials',request:{action:'method',modules:['judgment-core']}});
 assert.ok(result.content.includes('LIUREN_METHOD_BEGIN'));
 await assert.rejects(execute({action:'materials',request:{action:'retrieve',query:'test'}}),/no case\/experience/);
});
test('submit refuses missing core; module-only reads do not satisfy core receipt',async()=>{
 const file=path.join(saved.run,'report-draft.md');await fs.writeFile(file,'工程传输测试，不是占断报告。');
 await execute({action:'read',run:saved.run,module:'void',page:1,page_count:4});
 await assert.rejects(execute({action:'submit',run:saved.run,report_file:file}),/core pages not fully emitted/);
});
test('core paging, fixed evidence, bound source, compute and binding work',async()=>{
 let req={action:'read',run:saved.run,page:1,page_count:1},count=0;
 while(req){const page=await execute(req);assert.ok(page.content);count++;req=page.next_request;}
 assert.ok(count>=2);
 const evidence=await execute({action:'read',run:saved.run,material_id:'E04',page:1,page_count:4});assert.equal(evidence.id,'E04');
 const module=await execute({action:'read',run:saved.run,module:'void',page:1,page_count:4});assert.equal(module.id,'void');
 const pending=await execute({action:'read',run:saved.run,module:'pending-conflicts',page:1,page_count:4});assert.ok(pending.content.includes('C11'));assert.ok(pending.content.includes('已明确，关闭'));assert.ok(pending.content.includes('非理论裁决'));
 const supplemental=await execute({action:'read',run:saved.run,module:'confirmed-policy-supplements',page:1,page_count:4});assert.ok(supplemental.content.includes('SP06'));
 const lookup=await execute({action:'compute',run:saved.run,request:{action:'lookup',lookup:{subject:'申',place:'午',reference:'庚'}}});assert.equal(lookup.kin,'兄弟');
 await execute({action:'bind',run:saved.run,agent_id:'fixture-native-agent'});
 await assert.rejects(execute({action:'bind',run:saved.run,agent_id:'another-agent'}),/already bound/);
 await assert.rejects(execute({action:'read',run:saved.run,page:0}),/invalid page/);
});
test('full Unicode free report is preserved, idempotent and cannot be overwritten',async()=>{
 const file=path.join(saved.run,'report-draft.md'),body='# 工程传输验收\n\n只验证宿主、完整核心、绑定参考与报告保存。\n不作天气或录用预测。\n';
 await fs.writeFile(file,body);
 const receipt=await execute({action:'submit',run:saved.run,report_file:file});
 assert.equal(receipt.validationScope,'transport-only');assert.equal(receipt.professionalContentChecked,false);
 assert.equal((await execute({action:'result',run:saved.run})).body,body);
 assert.deepEqual(await execute({action:'submit',run:saved.run,report_file:file}),receipt);
 await fs.writeFile(file,body+'不同正文');
 await assert.rejects(execute({action:'submit',run:saved.run,report_file:file}),/different report/);
 await fs.writeFile(file,body);
 await fs.writeFile(path.join(artifact,'synthetic-result.json'),JSON.stringify({scope:'synthetic transport only; no prediction',receipt},null,2));
});
test('create an unread clean run for real native subagent forward test',async()=>{
 const native=await execute(input());
 await fs.writeFile(path.join(artifact,'native-dispatch-'+path.basename(native.run)+'.json'),JSON.stringify(native,null,2));
 try{await fs.writeFile(path.join(artifact,'native-dispatch.json'),JSON.stringify(native,null,2),{flag:'wx'});}
 catch(e){if(e.code!=='EEXIST')throw e;}
});
