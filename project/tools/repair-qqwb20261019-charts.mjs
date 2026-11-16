import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
const project=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const out=path.join(project,'output/qqwb20261019-repair-20261019');
const source=path.join(project,'资料来源/qq-homework-20261018/batch_20261019');
const {createChart}=await import(pathToFileURL(path.join(project,'materials/vendor/liuren-chart-legacy-20261102/adapters/chart.mjs')).href);
const reviews=JSON.parse(fs.readFileSync(path.join(out,'reviewed_images.json'),'utf8'));
const write=(file,value)=>{fs.mkdirSync(path.dirname(file),{recursive:true});fs.writeFileSync(file,JSON.stringify(value,null,2)+'\n');};
const comparisons=(facts,r)=>{
 const pairs=[['month_general',facts.month_general,r.month_general],['year_pillar',facts.year_pillar,r.printed_pillars[0]],['month_pillar',facts.month_pillar,r.printed_pillars[1]],['day_pillar',facts.day_pillar,r.printed_pillars[2]],['casting_hour_branch',facts.hour_branch,r.effective_casting_hour_branch]];
 for(const [i,l] of r.lessons.entries()) for(const key of ['tianpan','dizhi','tianjiang']) pairs.push([`lessons.${i}.${key}`,facts.lessons?.[i]?.[key],l[key]]);
 for(const [i,t] of r.transmissions.entries()) for(const key of ['diZhi','tianjiang']) pairs.push([`transmissions.${i}.${key}`,facts.transmissions?.[i]?.[key],t[key]]);
 return pairs.filter(([,actual,expected])=>actual!==expected).map(([field,actual,expected])=>({field,actual,expected}));
};
const rows=[];
for(const r of reviews){
 const destination=path.join(out,'charts',path.basename(r.file).replace(/\.[^.]+$/,'.json'));
 if(fs.existsSync(destination)){const existing=JSON.parse(fs.readFileSync(destination,'utf8'));if(JSON.stringify(existing.source_review)===JSON.stringify(r)){rows.push({case_id:r.case_id,file:r.file,matched:existing.source_chart_validation.ok,path:destination,method:existing.reconstruction_method});continue;}}
 const priorFile=path.join(source,'stage1_ready_v1/charts/v7',r.case_id+'.json');
 const prior=JSON.parse(fs.readFileSync(priorFile,'utf8'));
 const primary=Number(/_(\d+)\./.exec(r.file)[1])===1;
 let chosen=null,method=null,attempts=[];
 if(primary&&prior.validation?.ok&&prior.facts&&comparisons(prior.facts,r).length===0){chosen=prior;method='retained_datetime_engine_chart_visually_matched';}
 const date=r.original_transcription.time_norm;
 if(!chosen){
  const candidates=[];
  // Source images determine comparison targets. Assignments never enter this generator.
  for(const zhouye of ['自动选择','昼贵','夜贵']) for(const guiren of ['甲戊庚牛羊','甲羊戊庚牛']) for(const shehai of ['孟仲季','深度']) candidates.push({zhouye,guiren,shehai});
  for(const settings of candidates){
   const input={mode:'manual-pillars',pillars:{year:r.printed_pillars[0],month_branch:r.printed_pillars[1][1],day:r.printed_pillars[2],hour_branch:r.effective_casting_hour_branch},month_general:r.month_general,settings};
   if(date) input.reference_datetime=date.replace(' ','T');
   try{
    const result=await createChart(input); const diffs=comparisons(result.facts,r);
    attempts.push({settings,differences:diffs,engine_validation_ok:result.validation.ok});
    if(result.validation.ok&&diffs.length===0){chosen=result;method='manual_source_pillars_and_casting_hour_reconstruction';break;}
   }catch(error){attempts.push({settings,error:error.message});}
  }
 }
 if(chosen){
  const {summary,key_shensha,...facts}=chosen.facts;
  const result={...chosen,facts,schema:'reviewed-case-chart-v1',status:'source_core_chart_visually_matched',usable_for_batch_analysis:true,
   source_review:r,source_chart_validation:{ok:true,checked:['printed year/month/day pillars','effective casting hour','month general','four ordered lessons with generals','three ordered transmissions with generals'],unchecked:r.not_verified},
   reconstruction_method:method,
   recorded_event_time:r.original_transcription.time_norm||null,
   time_precision:r.original_transcription.time_norm?'source-minute-or-second':'date-and-minute-not-established',
   reconstruction_notice:method.startsWith('manual')?'按原图四柱、月将与有效占时复现；参考日期只供原引擎显示，不用于更改原盘四柱。与民用历法默认的差异仍按来源保留。':'程序盘已与原图核心字段核对一致；双时间行和起课方式另见source_review。',
   settings_evidence:method.startsWith('manual')?'配置经原图四课三传天将核对匹配；不代表原软件已明确声明全部配置。':'沿用旧引擎输入约定，已检查原图核心盘面。',attempts};
  write(destination,result);
  rows.push({case_id:r.case_id,file:r.file,matched:true,path:destination,method,settings:chosen.input?.settings});
  console.log(r.case_id,r.file,'OK',method);
 }else{
  write(destination,{schema:'reviewed-case-chart-v1',status:'source_core_mismatch_unresolved',usable_for_batch_analysis:false,source_review:r,source_chart_validation:{ok:false},attempts});
  const best=attempts.filter(x=>x.differences).sort((a,b)=>a.differences.length-b.differences.length)[0];
  rows.push({case_id:r.case_id,file:r.file,matched:false,path:destination,best});console.log(r.case_id,r.file,'HELD',JSON.stringify(best));
 }
 write(path.join(out,'chart_repair_manifest.json'),rows);
}
console.log(JSON.stringify({charts:rows.length,matched:rows.filter(r=>r.matched).length,held:rows.filter(r=>!r.matched).length}));
