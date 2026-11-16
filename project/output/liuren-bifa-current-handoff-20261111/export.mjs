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
const source=await runResolvedChart({mode:'now',label:'当前时间毕法AI交付查看'});
const shown=await exportAIChart(source);if(!shown.ok)throw Error('chart failed');
await write('正式盘导出.json',shown);
const question='用当前时间起一课，查看实际交付给AI的通用盘面及毕法内容。本次无具体占事，仅作交接内容查看。';
const saved=await execute({action:'packet',purpose:'transport-test',original_question:question,
 packet:{schema:'liuren-adjudication-input-v2',request_id:'bifa43-proof-'+Date.now(),chart:{source:'可信程序盘，工程测试',archive:source.archive},
 questions:[{id:'Q_transport',domain:'bifa-basic',text:question,subject:'毕法基本条件交接',stage:'工程验收',deadline:'本轮',success_criteria:'核心与正式盘相同，书证可完整按页取出',alternatives:['传输通过','传输失败'],tasks:['outcome'],task_basis:[{task:'outcome',origin:'user_requested',request_quote:question,reason:'工程传输测试'}]}],
 entities:[{id:'S_test',question_ids:['Q_transport'],referent:'日干坐标',branch:source.facts.day_stem,mapping_basis:'程序坐标验证'}],facts:[{id:'F_test',text:'仅为工程验收，无现实预测。',source:'测试构造'}],observations:[],focus_issues:[],method_materials:[],method_modules:[],unknowns:[],
 input_review:{questions:[{question_id:'Q_transport',request_quote:question,success_basis:'工程测试',stage_origin:'user_explicit',stage_basis:question}],facts:[{fact_id:'F_test',origin:'inferred',basis:'测试构造'}],neutrality_review:'无占断结果'}}});
const loaded=await loadPacket(ROOT,saved.packet_ref),core=JSON.parse(loaded.raw);
if(JSON.stringify(core.chart.bifa_conditions)!==JSON.stringify(shown.facts.bifa_conditions))throw Error('chart/core Bifa mismatch');
const pages=[];let request={action:'read',run:saved.run,page:1,page_count:1};
while(request){const page=await execute(request);pages.push(page);request=page.next_request;}
await write('裁决AI实际核心.json',core);await write('裁决reader逐页回执.json',pages);

await write('毕法交接原文.json',core.chart.bifa_conditions);
await write('交接记录.json',{release:health.release,run:saved.run,packet_ref:saved.packet_ref,archive:source.archive,chart_file:shown.chart_file,chart_equals_core:true,reader_pages:pages.length,model_calls:0,preview_module:'bifa-basic',note:'未指定人事占类，以已注册bifa-basic模块展示共用内容；实际占断按用户占事加载相应专项。'});
const refs=core.chart.bifa_conditions.evidence.slice(0,2),referencePages=[];
for(const e of refs){let req={action:'read',run:saved.run,material_id:e.id,page:1,page_count:1};const results=[];while(req){const r=await execute(req);results.push(r);req=r.next_request;}referencePages.push({id:e.id,pages:results});}
await write('按需书证示例.json',referencePages);
console.log(JSON.stringify({dir:OUT,chart_keys:Object.keys(core.chart),time:core.chart.event_datetime,pillars:core.chart.pillars,nobleman:core.chart.nobleman,bifa:core.chart.bifa_conditions,chart_file:shown.chart_file,reader_pages:pages.length},null,2));
