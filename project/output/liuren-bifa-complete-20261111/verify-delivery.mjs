// Actual engine/chart/packet/reader transport. No prediction model is called.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {runResolvedChart} from '../../tools/liuren-resolved-chart.mjs';
import {exportAIChart} from '../../tools/liuren-chart-view.mjs';
import {execute,status,ROOT} from '../../tools/liuren-codex.mjs';
import {loadPacket} from '../../tools/liuren-adjudication-files.mjs';
const OUT=path.dirname(fileURLToPath(import.meta.url)),hash=b=>createHash('sha256').update(b).digest('hex');
const write=(name,x)=>fs.writeFile(path.join(OUT,name),JSON.stringify(x,null,2)+'\n',{flag:'wx'});
const health=await status();if(!health.ready)throw Error(JSON.stringify(health));
const source=await runResolvedChart({datetime:'2026-11-11T14:42',label:'毕法43版书证与核心交接工程验证'});
const shown=await exportAIChart(source);if(!shown.ok)throw Error('chart failed');
await write('正式盘导出.json',shown);
const question='合成工程验收：核对百法基本条件、候选与方法核查是否从正式盘进入裁决核心；不作现实预测。';
const saved=await execute({action:'packet',purpose:'transport-test',original_question:question,
 packet:{schema:'liuren-adjudication-input-v2',request_id:'bifa43-proof-'+Date.now(),chart:{source:'可信程序盘，工程测试',archive:source.archive},
 questions:[{id:'Q_transport',domain:'finance',text:question,subject:'毕法基本条件交接',stage:'工程验收',deadline:'本轮',success_criteria:'核心与正式盘相同，书证可完整按页取出',alternatives:['传输通过','传输失败'],tasks:['outcome'],task_basis:[{task:'outcome',origin:'user_requested',request_quote:question,reason:'工程传输测试'}]}],
 entities:[{id:'S_test',question_ids:['Q_transport'],referent:'测试坐标',branch:'己',mapping_basis:'程序坐标验证'}],facts:[{id:'F_test',text:'仅为工程验收，无现实预测。',source:'测试构造'}],observations:[],focus_issues:[],method_materials:[],method_modules:[],unknowns:[],
 input_review:{questions:[{question_id:'Q_transport',request_quote:question,success_basis:'工程测试',stage_origin:'user_explicit',stage_basis:question}],facts:[{fact_id:'F_test',origin:'inferred',basis:'测试构造'}],neutrality_review:'无占断结果'}}});
const loaded=await loadPacket(ROOT,saved.packet_ref),core=JSON.parse(loaded.raw);
if(JSON.stringify(core.chart.bifa_conditions)!==JSON.stringify(shown.facts.bifa_conditions))throw Error('chart/core Bifa mismatch');
const pages=[];let request={action:'read',run:saved.run,page:1,page_count:1};
while(request){const page=await execute(request);pages.push(page);request=page.next_request;}
await write('裁决AI实际核心.json',core);await write('裁决reader逐页回执.json',pages);
const references=[];
for(const id of new Set([...core.chart.bifa_conditions.evidence.map(e=>e.id),'BF-B38','BF-D38','BF-B100','BF-D100'])){
 const readPages=[];let req={action:'read',run:saved.run,material_id:id,page:1,page_count:1};
 while(req){const r=await execute(req);if(!r.content?.trim())throw Error('empty reference '+id);readPages.push(r);req=r.next_request;}
 references.push({id,pages:readPages});
}
await write('裁决reader书证回执.json',references);
const baseline=JSON.parse(await fs.readFile(path.join(OUT,'before.json'),'utf8'));
for(const [file,expected] of Object.entries(baseline.frozen))if(hash(await fs.readFile(path.join(ROOT,file)))!==expected)throw Error('frozen42 changed');
await write('验收结果.json',{release:health.release,ready:health.ready,method_version:health.method_version,chart_archive:source.archive,ai_chart_file:shown.chart_file,packet_ref:saved.packet_ref,run:saved.run,
 bifa_core_field:'chart.bifa_conditions',chart_equals_core:true,reader_pages:pages.length,matched:core.chart.bifa_conditions.matches.map(m=>({id:m.id,name:m.name,checks:m.checks})),
 candidates:core.chart.bifa_conditions.conditional_candidates.map(m=>({id:m.id,name:m.name,checks:m.checks})),methods:core.chart.bifa_conditions.method_checks.map(m=>m.id),source_excerpt_ids:references.map(r=>r.id),
 registered_conditions:134,method_checks:8,represented_laws:100,all_100_laws_basic_reviewed:true,all_variants_complete:false,frozen42_unchanged:true,model_calls:0,predictive_validation_count:0,
 scope:'实际引擎、正式AI盘、packet及裁决reader链路；未运行真实模型，不证明模型理解或现实预测效果'});
console.log(JSON.stringify({ready:health.ready,release:health.release,matches:core.chart.bifa_conditions.matches.length,candidates:core.chart.bifa_conditions.conditional_candidates.length,methods:core.chart.bifa_conditions.method_checks.length,reader_pages:pages.length,source_refs:references.length,model_calls:0}));
