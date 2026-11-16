// Real engine and normal exporter. No post-export edit and no model call.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import assert from 'node:assert/strict';
import {runResolvedChart} from '../../tools/liuren-resolved-chart.mjs';
import {exportAIChart} from '../../tools/liuren-chart-view.mjs';
import {scanBasicBifa} from '../../tools/liuren-bifa-basic.mjs';
import {execute,status,ROOT} from '../../tools/liuren-codex.mjs';
import {loadPacket} from '../../tools/liuren-adjudication-files.mjs';
const OUT=path.dirname(fileURLToPath(import.meta.url));
const hash=v=>createHash('sha256').update(v).digest('hex');
const write=(name,value)=>fs.writeFile(path.join(OUT,name),JSON.stringify(value,null,2)+'\n',{flag:'wx'});
const health=await status();assert.ok(health.ready);
const source=await runResolvedChart({mode:'now',label:'毕法固定语句44版程序直接导出'});
const shown=await exportAIChart(source);assert.ok(shown.ok);
const bytes=await fs.readFile(shown.chart_file.path);assert.equal(hash(bytes),shown.chart_file.sha256);
const exported=JSON.parse(bytes);assert.deepEqual(exported,shown.facts);
const scan=scanBasicBifa(exported);
await write('程序排盘回执.json',shown);
await write('内部毕法核查.json',scan);
const question='合成工程传输测试：核对正式程序盘及裁决核心中的毕法精简字段完全相同。weather分类只是接口测试占位，无用户天气占问、无现实预测。';
const saved=await execute({action:'packet',purpose:'transport-test',original_question:question,
 packet:{schema:'liuren-adjudication-input-v2',request_id:'bifa44-engine-'+Date.now(),chart:{source:'可信程序盘，仅合成传输测试',archive:source.archive},
 questions:[{id:'Q_transport',domain:'weather',text:question,subject:'毕法程序导出链路',stage:'工程验收',deadline:'本轮',success_criteria:'导出与核心相同、原文仍可按需读取',alternatives:['一致','不一致'],tasks:['outcome'],task_basis:[{task:'outcome',origin:'user_requested',request_quote:question,reason:'工程测试'}]}],
 entities:[{id:'S_test',question_ids:['Q_transport'],referent:'测试坐标',branch:source.facts.day_stem,mapping_basis:'程序日干坐标'}],
 facts:[{id:'F_test',text:'工程测试不代表用户有天气占问，不运行预测模型。',source:'合成测试构造'}],observations:[],focus_issues:[],method_materials:[],method_modules:[],unknowns:['用户未指定具体占事'],
 input_review:{questions:[{question_id:'Q_transport',request_quote:question,success_basis:'工程链路相同',stage_origin:'user_explicit',stage_basis:question}],facts:[{fact_id:'F_test',origin:'inferred',basis:'合成测试构造'}],neutrality_review:'未设现实结果'}}});
const loaded=await loadPacket(ROOT,saved.packet_ref),core=JSON.parse(loaded.raw);
assert.deepEqual(core.chart,exported);
const pages=[];let req={action:'read',run:saved.run,page:1,page_count:1};
while(req){const r=await execute(req);pages.push(r);req=r.next_request;}
const book=[];req={action:'read',run:saved.run,material_id:'BF-B74',page:1,page_count:1};
while(req){const r=await execute(req);assert.ok(r.content.trim());book.push(r);req=r.next_request;}
await write('AI实际核心.json',core);await write('核心逐页读取回执.json',pages);await write('按需书证回执.json',book);
const before=JSON.parse(await fs.readFile(path.join(OUT,'before.json'),'utf8'));
for(const [file,expected] of Object.entries(before.frozen))assert.equal(hash(await fs.readFile(path.join(ROOT,file))),expected,file);
const receipt={release:health.release,datetime:exported.datetime,chart_file:shown.chart_file,archive:source.archive,chart_equals_core:true,
 branch_matches:scan.matches.length,output_laws:exported.bifa_conditions.length,conditional_candidates:scan.conditional_candidates.length,
 method_checks:scan.method_checks.length,core_reader_pages:pages.length,model_calls:0,predictive_validation_count:0,frozen43_unchanged:true,
 original_example_unchanged:hash(await fs.readFile('排盘存档/六壬/六壬-20261111-170741-当前时间毕法AI交付查看-1f48fe6f-8e62-4322-b5c6-8bee60b2e03d.corrected-3ad2322acd47a575.ai-98e1a0ecc2eea5e3.json'))==='98e1a0ecc2eea5e317efd416609cb7f431ba56b35ef18a70b5139c8da52ea16c',
 packet_ref:saved.packet_ref,run:saved.run};
await write('验收结果.json',receipt);console.log(JSON.stringify(receipt,null,2));
