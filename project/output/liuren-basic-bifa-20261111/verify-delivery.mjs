// Real engine + real local packet/read route, no model is dispatched.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {runResolvedChart} from '../../tools/liuren-resolved-chart.mjs';
import {exportAIChart} from '../../tools/liuren-chart-view.mjs';
import {execute,status,ROOT} from '../../tools/liuren-codex.mjs';
import {loadPacket} from '../../tools/liuren-adjudication-files.mjs';
import {scanBasicBifa,basicBifaCatalog} from '../../tools/liuren-bifa-basic.mjs';
import {geometryChart} from '../../tools/liuren-bifa-batch.mjs';
const OUT=path.dirname(fileURLToPath(import.meta.url)),hash=b=>createHash('sha256').update(b).digest('hex');
const write=(name,x)=>fs.writeFile(path.join(OUT,name),JSON.stringify(x,null,2)+'\n',{flag:'wx'});
const health=await status();if(!health.ready)throw Error(JSON.stringify(health));
const source=await runResolvedChart({datetime:'2026-11-11T14:42',label:'基本毕法42版交接工程验证'});
const shown=await exportAIChart(source);if(!shown.ok)throw Error('chart failed');
await write('正式盘导出.json',shown);
const question='合成工程验收：核对基本毕法是否从正式盘进入裁决AI核心；不作现实预测。';
const saved=await execute({action:'packet',purpose:'transport-test',original_question:question,
 packet:{schema:'liuren-adjudication-input-v2',request_id:'bifa42-proof-'+Date.now(),
 chart:{source:'可信程序盘，工程测试',archive:source.archive},
 questions:[{id:'Q_transport',domain:'finance',text:question,subject:'基本毕法交接',stage:'工程验收',deadline:'本轮',
  success_criteria:'完整核心能读取与正式盘相同的已核结构及其连续书证',alternatives:['传输通过','传输失败'],tasks:['outcome'],
  task_basis:[{task:'outcome',origin:'user_requested',request_quote:question,reason:'工程传输测试'}]}],
 entities:[{id:'S_test',question_ids:['Q_transport'],referent:'测试坐标',branch:'己',mapping_basis:'仅为程序坐标验证'}],
 facts:[{id:'F_test',text:'仅为工程验收，无现实预测。',source:'测试构造'}],observations:[],focus_issues:[],method_materials:[],method_modules:[],unknowns:[],
 input_review:{questions:[{question_id:'Q_transport',request_quote:question,success_basis:'工程测试',stage_origin:'user_explicit',stage_basis:question}],facts:[{fact_id:'F_test',origin:'inferred',basis:'测试构造'}],neutrality_review:'无占断结果'}}});
const loaded=await loadPacket(ROOT,saved.packet_ref),core=JSON.parse(loaded.raw);
if(JSON.stringify(core.chart.bifa_conditions)!==JSON.stringify(shown.facts.bifa_conditions))throw Error('chart/core Bifa mismatch');
const pages=[];let request={action:'read',run:saved.run,page:1,page_count:1};
while(request){const page=await execute(request);pages.push(page);request=page.next_request;}
await write('裁决AI实际核心.json',core);await write('裁决reader逐页回执.json',pages);
const references=[];for(const e of core.chart.bifa_conditions.evidence){
 const read=await execute({action:'read',run:saved.run,material_id:e.id,page:1,page_count:4});
 if(!read.content.trim())throw Error('empty reference');references.push(read);
}
await write('裁决reader书证回执.json',references);
const fixture='output/liuren-bifa-audit-20261111/engine-day-night-1440.json';
const bytes=await fs.readFile(path.join(ROOT,fixture)),pins=JSON.parse(await fs.readFile(path.join(ROOT,'output/liuren-bifa-audit-20261111/source-hashes.json'),'utf8'));
if(pins.find(p=>p.path===fixture)?.sha256!==hash(bytes))throw Error('1440 cached engine geometries drifted');
const variants=JSON.parse(bytes),counts=Object.fromEntries(basicBifaCatalog().map(r=>[r.id,0])),rows=[];
for(const v of variants){const r=scanBasicBifa(geometryChart(v));for(const m of r.matches)counts[m.id]++;rows.push({day:v.day,upper:v.day_upper,mode:v.mode,...r});}
await write('1440盘逐项匹配.json',rows);
const baseline=JSON.parse(await fs.readFile(path.join(OUT,'before.json'),'utf8'));
for(const [file,expected]of Object.entries(baseline.frozen))if(hash(await fs.readFile(path.join(ROOT,file)))!==expected)throw Error('frozen41 changed');
await write('验收结果.json',{release:health.release,ready:health.ready,method_version:health.method_version,
 chart_archive:source.archive,ai_chart_file:shown.chart_file,packet_ref:saved.packet_ref,run:saved.run,
 bifa_core_field:'chart.bifa_conditions',chart_equals_core:true,reader_pages:pages.length,
 matched:core.chart.bifa_conditions.matches.map(m=>({id:m.id,name:m.name,checks:m.checks})),
 source_excerpt_ids:references.map(r=>r.id),geometries:variants.length,condition_evaluations:variants.length*32,
 counts,geometry_file_sha256:hash(bytes),frozen41_unchanged:true,
 registered_structures:32,represented_laws:25,all100LawsComplete:false,model_calls:0,predictive_validation_count:0,
 scope:'实际引擎、正式AI盘、packet及裁决reader链路；未运行真实模型，不证明模型理解或现实预测效果'});
console.log(JSON.stringify({ready:health.ready,release:health.release,matches:core.chart.bifa_conditions.matches.length,reader_pages:pages.length,source_refs:references.length,geometries:variants.length,model_calls:0}));
