// Exhaustive execution of reviewed definitions, not an automatic book review.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {loadSources,reviewCandidates,scanRegistered,REGISTERED_SCAN_LABELS} from './liuren-bifa-audit.mjs';
import {isEntryPoint} from './liuren-direct.mjs';

const ROOT=fileURLToPath(new URL('../',import.meta.url));
const ZHI=[...'子丑寅卯辰巳午未申酉戌亥'],GAN=[...'甲乙丙丁戊己庚辛壬癸'];
const LATIN=['zi','chou','yin','mao','chen','si','wu','wei','shen','you','xu','hai'];
const HOMES={甲:'寅',乙:'辰',丙:'巳',丁:'未',戊:'巳',己:'未',庚:'申',辛:'戌',壬:'亥',癸:'丑'};
const sha=s=>createHash('sha256').update(s).digest('hex');
const json=async p=>JSON.parse((await fs.readFile(p,'utf8')).replace(/^\uFEFF/,''));
const mod=n=>(n%12+12)%12;
const canonical=g=>g==='螣蛇'?'腾蛇':g;
const accepted=r=>['structure_matched','branch_matched','relation_only'].includes(r.status);

export function geometryChart(v) {
 const i=Array.from({length:60},(_,i)=>GAN[i%10]+ZHI[i%12]).indexOf(v.day);
 if(i<0||!ZHI.includes(v.day_upper)||v.mode!==v.engine_mode)throw Error('遍历盘日柱、上神或实际昼夜不符');
 const home=HOMES[v.day[0]],shift=mod(ZHI.indexOf(v.day_upper)-ZHI.indexOf(home));
 const start=i-i%10,xunZhi=ZHI[start%12],xungan=b=>{
  const delta=mod(ZHI.indexOf(b)-ZHI.indexOf(xunZhi));return delta<10?GAN[delta]:'空';
 };
 const rows=ZHI.map((di,k)=>{const tian=ZHI[mod(k+shift)];return {di,tian,tianjiang:canonical(v.shenpan[LATIN[k]]),xungan:xungan(tian)};});
 const lessons=v.sike.map((r,i)=>({index:i+1,tianjiang:canonical(r[0]),tianpan:r[1],dizhi:r[2]}));
 const transmissions=v.sanchuan.map((r,i)=>({index:i+1,diZhi:r[3],tianjiang:canonical(r[4])}));
 for(const l of lessons)if(rows.find(r=>r.tian===l.tianpan)?.tianjiang!==l.tianjiang)throw Error('四课天将与本模式天地盘不符');
 for(const t of transmissions)if(rows.find(r=>r.tian===t.diZhi)?.tianjiang!==t.tianjiang)throw Error('三传天将与本模式天地盘不符');
 if(lessons[0].tianpan!==v.day_upper)throw Error('第一课上神不符');
 return {schema:'liuren-bifa-geometry-test-v1',datetime:null,pillars:[null,null,v.day,null],
  day:{symbol:v.day[0],home},nobleman:{zhouye:v.mode},lessons,transmissions,heaven_earth:rows,
  synthetic_scope:'只核日柱、天地盘、四课三传及昼夜天将，未给年月时年命和具体占事，不冒充真实时间盘'};
}

export async function runBatch({out}={}) {
 const start=performance.now(),input=path.join(ROOT,'output/liuren-bifa-audit-20261111');
 const pinned=await json(path.join(input,'source-hashes.json'));
 const required=['排盘工具魔改/index.html','排盘工具魔改/index.js','排盘工具魔改/js/data.js','排盘工具魔改/js/paipan.js','排盘工具魔改/js/hexin.js','排盘工具魔改/js/guize.js','output/liuren-bifa-audit-20261111/engine-bifa-lookup-720.json','output/liuren-bifa-audit-20261111/engine-day-night-1440.json'];
 const checked=await Promise.all(required.map(async name=>{
  const recorded=pinned.find(x=>x.path===name),actual=sha(await fs.readFile(path.join(ROOT,name)));
  if(!recorded||actual!==recorded.sha256)throw Error('原引擎或枚举证据已变，须先重新生成全表：'+name);
  return {path:name,sha256:actual};
 }));
 const sources=await loadSources();if(!sources.valid)throw Error('双蓝本来源变化，须先复核条件');
 const variants=await json(path.join(input,'engine-day-night-1440.json'));
 const lookup=await json(path.join(input,'engine-bifa-lookup-720.json'));
 if(variants.length!==1440||lookup.length!==720)throw Error('穷举数据数量不完整');
 const cells=new Map(lookup.map(r=>[r.day+'|'+r.day_upper,r.text]));
 if(cells.size!==720)throw Error('720盘索引重复');
 const seen=new Set(),rows=[],scans=[],labels=new Map(),labelSource=new Set();
 let rawRows=0;for(const r of lookup)for(const l of r.text.split('\n').filter(Boolean)){rawRows++;labelSource.add(l);}
 for(const v of variants) {
  const key=v.day+'|'+v.day_upper+'|'+v.mode;
  if(seen.has(key)||cells.get(v.day+'|'+v.day_upper)!==v.bifa)throw Error('昼夜版本与720表不一致或重复');
  seen.add(key);
  const c=geometryChart(v),r=reviewCandidates(c,v.bifa,{sourcesValid:true}),scan=scanRegistered(c,{sourcesValid:true});
  const rawSet=new Set(r.rows.map(x=>x.raw_label));
  for(const item of r.rows) {
   rows.push({day:v.day,day_upper:v.day_upper,mode:v.mode,...item});
   if(!labels.has(item.raw_label))labels.set(item.raw_label,{label:item.raw_label,mode_rows:0,statuses:{},samples:[]});
   const summary=labels.get(item.raw_label);summary.mode_rows++;
   summary.statuses[item.status]=(summary.statuses[item.status]??0)+1;
   if(summary.samples.length<3)summary.samples.push({day:v.day,day_upper:v.day_upper,mode:v.mode,status:item.status});
  }
  for(const item of scan.rows.filter(accepted))scans.push({day:v.day,day_upper:v.day_upper,mode:v.mode,raw_label:item.raw_label,status:item.status,checks:item.checks,adoptable_information:item.adoptable_information,missing_from_native_list:!rawSet.has(item.raw_label)});
 }
 const counts={};for(const r of rows)counts[r.status]=(counts[r.status]??0)+1;
 const pending=[...labels.values()].filter(r=>Object.keys(r.statuses).some(s=>['not_reviewed','needs_context','mode_wording_unresolved'].includes(s))).sort((a,b)=>(b.statuses.not_reviewed??0)-(a.statuses.not_reviewed??0));
 const issues=rows.filter(r=>['definition_not_met','engine_basis_unproven','label_error','non_bifa_text'].includes(r.status));
 const summary={schema:'liuren-bifa-batch-summary-v1',native_geometries:720,mode_geometries:1440,native_rows:rawRows,mode_candidate_rows:rows.length,unique_native_labels:labelSource.size,
  registered_scan_labels:REGISTERED_SCAN_LABELS.length,counts,pending_label_definitions:pending.length,
  independent_scan_matches:scans.length,registered_matches_missing_from_native:scans.filter(r=>r.missing_from_native_list).length,
  complete_100_law_semantic_review:false,predictive_validation_count:0,
  elapsed_ms:Math.round(performance.now()-start),
  limitations:['720×昼夜只穷举固定几何，不能穷尽月令旺衰、四建、年命、应期、具体事类','definition_not_met仅指本模式当前明示条件不符；有另一模式成立者须补限定，不一概当引擎两模式都错','只有已登记条件可计算；未核标签按定义去重排队，不重复手读9075行','独立扫描只检查已登记分支；未列出不能反推不存在其他百法条件']};
 if(out){
  const dir=path.resolve(out),rel=path.relative(ROOT,dir);
  if(rel.startsWith('..')||path.isAbsolute(rel)||!rel.startsWith('output'+path.sep))throw Error('批量输出须在本项目output新目录');
  await fs.mkdir(dir); // Deliberately fails on an existing evidence directory.
  const write=(name,data)=>fs.writeFile(path.join(dir,name),JSON.stringify(data,null,2)+'\n',{flag:'wx'});
  await Promise.all([write('summary.json',summary),write('all-mode-rows.json',rows),write('label-review-queue.json',pending),write('issues-by-mode.json',issues),write('independent-scan.json',scans),write('inputs.json',{source_validation:sources.sources.map(s=>({path:s.path,sha256:s.sha256,valid:s.valid})),checked_inputs:checked,condition_implementation_sha256:sha(await fs.readFile(new URL('./liuren-bifa-audit.mjs',import.meta.url))),registry_sha256:sha(await fs.readFile(new URL('./liuren-bifa-source-rules.json',import.meta.url)))} )]);
  const report=`# 720局×昼夜批量核查\n\n原表${rawRows}行、${labelSource.size}种标签；1440个昼夜盘全部执行，共${rows.length}次候选检查。独立扫描已登记${REGISTERED_SCAN_LABELS.length}个标签分支。\n\n| 本模式核查状态 | 次数 |\n| --- | ---: |\n${Object.entries(counts).map(([k,v])=>'| '+k+' | '+v+' |').join('\n')}\n\n待核按原始标签去重，当前${pending.length}种标签仍有未核或上下文缺口；共用核法还可继续归并，标签数不是独立定义数。耗时${summary.elapsed_ms}ms仅指复用哈希核验过的枚举数据后运行已登记规则，不包含读书和全表生成；不是百法语义已全面验收。\n\n昼夜不符只作筛除，不能算错误；未成立需看当前模式、类格、位置、普通分支与例外。独立扫描额外发现${summary.registered_matches_missing_from_native}项已登记关系未被原表列出，只是有限范围的漏项探查。\n\n用户已指定第22法依《大全》；详见规则登记及D22。\n`;
  await fs.writeFile(path.join(dir,'批量说明.md'),report,{flag:'wx'});
 }
 return summary;
}

if(isEntryPoint(process.argv[1],import.meta.url)) {
 try {const args=process.argv.slice(2);if(args.length!==2||args[0]!=='--out')throw Error('用法：node tools/liuren-bifa-batch.mjs --out output/新目录');process.stdout.write(JSON.stringify(await runBatch({out:args[1]}),null,2)+'\n');}
 catch(e){process.stderr.write('LIUREN_BIFA_BATCH_ERROR: '+e.message+'\n');process.exitCode=1;}
}
