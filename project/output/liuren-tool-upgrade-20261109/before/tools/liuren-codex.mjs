import {chartQuery} from './liuren-chart-view.mjs';
// Codex host adapter. Reuses current chart, source and packet implementations.
// No model API or OpenCode session/database mutation. Strength uses shared tools.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {randomUUID,createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {savePacket,loadPacket,PAGE_SIZE} from './liuren-adjudication-files.mjs';
import {readBoundReference} from './liuren-core-handoff.mjs';
import {compute} from './liuren-deterministic-io.mjs';
import {resolveChartArchive} from './liuren-adjudication-files.mjs';
import {checkSubmission,reportMarkdown} from './liuren-adjudication-output.mjs';

export const ROOT=path.resolve(fileURLToPath(new URL('../',import.meta.url)));
const RUNS=path.join(ROOT,'output/codex-liuren');
const sha=x=>createHash('sha256').update(x).digest('hex');
const readJSON=async p=>JSON.parse((await fs.readFile(p,'utf8')).replace(/^\uFEFF/,''));
const emit=x=>process.stdout.write(JSON.stringify(x,null,2)+'\n');
const fail=m=>{throw new Error('LIUREN_CODEX: '+m);};
const writeJSON=(p,x)=>fs.writeFile(p,JSON.stringify(x,null,2)+'\n',{flag:'wx'});
const MODEL={model:'gpt-6.1-sol',reasoning_effort:'high',fork_turns:'none'};

async function active(){
 const pointer=await readJSON(path.join(ROOT,'.opencode/liuren-active.json'));
 if(!/^runtime\/liuren\/[A-Za-z0-9_-]+$/.test(pointer.runtime))fail('invalid active runtime');
 const manifest=await readJSON(path.join(ROOT,pointer.runtime,'manifest.json'));
 return {pointer,manifest};
}
export async function status(){
 const {pointer,manifest}=await active(),mismatches=[];
 for(const [file,expected] of Object.entries(manifest.files)){
  const target=path.resolve(ROOT,pointer.runtime,file);
  if(!target.startsWith(path.resolve(ROOT,pointer.runtime)+path.sep))fail('manifest path escapes runtime');
  try{if(sha(await fs.readFile(target))!==expected)mismatches.push(file);}catch{mismatches.push(file);}
 }
 for(const [file,expected] of Object.entries(pointer.workflowImplementation??{})){
  try{if(sha(await fs.readFile(path.join(ROOT,file)))!==expected)mismatches.push(file);}catch{mismatches.push(file);}
 }
 return {schema:'liuren-codex-status-v1',ready:mismatches.length===0,
  root:ROOT,release:pointer.release,runtime:pointer.runtime,method_version:pointer.methodVersion,
  adjudicator:MODEL,native_subagent_required:true,mismatches,
  domains:Object.keys(manifest.modules).filter(k=>manifest.modules[k].file.startsWith('domains/')),
  modules:Object.keys(manifest.modules),professional_content_changed:Boolean(pointer.confirmedJudgmentPolicy),judgment_policy:pointer.confirmedJudgmentPolicy??null,
  note:'ready checks local files only; host spawn settings must be supplied explicitly. No accuracy claim.'};
}
async function runContext(run){
 if(typeof run!=='string')fail('run is required');
 const base=await fs.realpath(RUNS),dir=path.resolve(run);
 if(path.dirname(dir)!==base||!/^codex-[a-f0-9-]{36}$/.test(path.basename(dir))||await fs.realpath(dir)!==dir)fail('invalid run directory');
 const record=await readJSON(path.join(dir,'run.json'));
 if(record.schema!=='liuren-codex-run-v1')fail('invalid run manifest');
 const loaded=await loadPacket(ROOT,record.packet_ref);
 if(loaded.envelope.parent_session_id!==record.owner)fail('packet owner differs');
 if(sha(record.adjudicator_prompt)!==record.adjudicator_prompt_sha256)fail('role prompt changed');
 return {dir,record,loaded};
}
function spawnMessage(dir){
 return `你是本次大六壬独立裁决子智能体。仅执行本任务，不再派子智能体。工作目录：${ROOT}。本任务run：${dir}。\n`+
 `使用JSON请求文件调用 node tools/liuren-codex.mjs --request 请求文件。先调用 {"action":"role","run":${JSON.stringify(dir)}} 读取本任务绑定的专业指令与宿主映射；再以 {"action":"read","run":${JSON.stringify(dir)},"page":1,"page_count":1} 读取全部核心，按next_request接续。每次shell读取设置足够输出额度；若出现显示截断，重读补齐，不能把回执当成已读全文。\n`+
 '只使用本任务核心、绑定参考及compute；不读取主会话、其他任务、案例库、经验库或已知答案。主智能体候选可纠正，从完整盘查漏。原书按需查。完整报告写到本run/report-draft.md，再调用submit，成功后只回小回执。不得把内部推理当报告。若role标明transport-test，只验证传输，不作专业占断。';
}
export async function execute(req){
 if(!req||typeof req!=='object'||Array.isArray(req))fail('request object required');
 if(req.action==='status')return status();
 if(req.action==='compute'&&!req.run){
  if(req.request?.action!=='strength'||!req.request.archive)fail('未绑定run仅支持带可信archive的strength计算');
  const chart=(await resolveChartArchive(ROOT,{chart:{source:'Codex main strength query',archive:req.request.archive}})).chart;
  return compute(req.request,chart.facts,{root:ROOT});
 }
 if(req.action==='materials'){
  const r=req.request;
  if(!r||!['method','book_search','book_outline','shensha'].includes(r.action))fail('materials supports method/book_search/book_outline/shensha only; no case/experience retrieval');
  return {schema:'liuren-codex-materials-v1',content:execFileSync(process.env.LIUREN_PYTHON??'python',
   ['-X','utf8',path.join(ROOT,'tools/liuren-materials.py'),'--request',JSON.stringify(r)],
   {cwd:ROOT,encoding:'utf8',timeout:60000,maxBuffer:8*1024*1024,windowsHide:true})};
 }
 if(req.action==='packet'){
  const health=await status();if(!health.ready)fail('active implementation mismatch: '+health.mismatches.join(', '));
  if(typeof req.original_question!=='string'||!req.original_question.trim())fail('original_question must preserve the user original text');
  const owner='codex-'+randomUUID(),dir=path.join(RUNS,owner);
  await fs.mkdir(dir,{recursive:true});
  const packet=structuredClone(req.packet);
  if(!packet)fail('packet required');
  packet.input_origin={source_text:req.original_question,source_identity:'current user question; supplied by Codex main agent'};
  const saved=await savePacket(ROOT,packet,owner);
  const cfg=await readJSON(path.join(ROOT,'.opencode/oh-my-opencode-slim.jsonc'));
  const professional=cfg.agents?.['liuren-adjudicator']?.prompt;
  if(typeof professional!=='string'||!professional.trim())fail('missing current adjudicator instructions');
  const record={schema:'liuren-codex-run-v1',owner,created_at:new Date().toISOString(),release:health.release,
   method_version:health.method_version,purpose:req.purpose==='transport-test'?'transport-test':'judgment',
   requested_adjudicator:MODEL,packet_ref:{file_path:saved.file_path,sha256:saved.sha256},
   adjudicator_prompt:professional,adjudicator_prompt_sha256:sha(professional),
   validation_scope:'transport-only; native model settings are recorded requests, not API attestation'};
  await writeJSON(path.join(dir,'run.json'),record);
  const spawn={task_name:'liuren_adjudicator_'+owner.slice(6,14),...MODEL,message:spawnMessage(dir)};
  await writeJSON(path.join(dir,'dispatch-request.json'),spawn);
  return {schema:'liuren-codex-packet-v1',run:dir,reading:saved.reading,packet_ref:record.packet_ref,
   spawn,bind_after_spawn:{action:'bind',run:dir,agent_id:'REPLACE_WITH_NATIVE_AGENT_ID'},
   note:'Use native collaboration.spawn_agent, map reasoning_effort directly; do not call OpenCode task.'};
 }
 const {dir,record,loaded}=await runContext(req.run);
 if(req.action==='role')return {purpose:record.purpose,professional_instructions:record.adjudicator_prompt,
  host_mapping:{liuren_adjudication_read:'action=read, same run; module/material_id optional. Codex uses page_count=1 to avoid shell output truncation; the original page_count=4 is an OpenCode transport convention, not a professional rule.',
   liuren_compute:'action=compute, request=original computation arguments',
   liuren_adjudication_submit:'write full report-draft.md inside this run, action=submit, report_file=absolute draft path',
   task:'not available; child does not spawn',
   tool_help:'action=status returns current module/domain IDs; use the existing compute guide for exact request schemas'},
  test_instruction:record.purpose==='transport-test'?'Only verify complete core and one bound module, then submit an explicitly labelled transport test receipt. Do not predict outcomes.':null};
 if(req.action==='bind'){
  if(typeof req.agent_id!=='string'||!/^\/?[A-Za-z0-9_/-]{1,150}$/.test(req.agent_id))fail('native agent_id or canonical task name required');
  const file=path.join(dir,'native-agent.json');
  try{const old=await readJSON(file);if(old.agent_id!==req.agent_id)fail('run already bound to another agent');return old;}
  catch(e){if(e.code!=='ENOENT')throw e;}
  const result={agent_id:req.agent_id,requested_model:MODEL.model,requested_reasoning_effort:MODEL.reasoning_effort,source:'main agent recorded native spawn result'};
  await writeJSON(file,result);return result;
 }
 if(req.action==='read'){
  let raw=loaded.raw,details={view:loaded.readView,view_sha256:loaded.viewSha256};
  if(req.module||req.material_id){const source=await readBoundReference(ROOT,loaded,req);raw=source.content;const {content,...meta}=source;details={view:'reference',...meta,view_sha256:sha(raw)};}
  const pages=Math.ceil(raw.length/PAGE_SIZE),page=req.page??1,count=req.page_count??1;
  if(!Number.isInteger(page)||page<1||page>pages||!Number.isInteger(count)||count<1||count>4)fail('invalid page/page_count');
  const end=Math.min(pages,page+count-1),content=raw.slice((page-1)*PAGE_SIZE,end*PAGE_SIZE);
  await fs.mkdir(path.join(dir,'reads'),{recursive:true});
  await writeJSON(path.join(dir,'reads',randomUUID()+'.json'),{...details,page,page_end:end,pages,content_sha256:sha(content),packet_sha256:record.packet_ref.sha256});
  return {...details,page,page_end:end,pages,remaining_pages:Array.from({length:Math.max(0,pages-end)},(_,i)=>end+i+1),content,
   next_request:end<pages?{...req,page:end+1,page_count:count}:null,
   note:'Receipt records emitted text; it cannot establish semantic understanding or authenticate reader identity.'};
 }
 if(req.action==='compute'){
  if(req.request?.action==='strength'){
   if(JSON.parse(loaded.raw).chart?.strength_model?.id!=='liuren-palace-strength-v1')fail('旧任务未绑定当前单宫算法；沿原资料领取结果，另开新任务才使用新算法');
   const value=compute(req.request,loaded.envelope.packet.chart.facts,{root:ROOT});
   const folder=path.join(dir,'calculations');await fs.mkdir(folder,{recursive:true});
   await writeJSON(path.join(folder,randomUUID()+'.json'),{request:req.request,result:value});
   return value;
  }
  if(req.request?.action==='chart')return chartQuery(loaded.envelope.packet.chart.facts,loaded.envelope.packet.deterministic.adopted_shensha,req.request.symbols);
  return compute(req.request,loaded.envelope.packet.chart.facts,{root:ROOT});
 }
 if(req.action==='submit'){
  const reportFile=path.resolve(req.report_file??'');
  if(path.dirname(reportFile)!==dir||await fs.realpath(reportFile)!==reportFile)fail('report_file must be an ordinary file directly in this run');
  const report=await fs.readFile(reportFile,'utf8');
  const checked=checkSubmission(ROOT,report,loaded.envelope.packet);if(!checked.ok)fail(JSON.stringify(checked.issues));
  const seen=new Set();
  let files=[];try{files=await fs.readdir(path.join(dir,'reads'));}catch(e){if(e.code!=='ENOENT')throw e;}
  for(const name of files){
   const row=await readJSON(path.join(dir,'reads',name));
   if(row.view!==loaded.readView||row.view_sha256!==loaded.viewSha256||row.packet_sha256!==record.packet_ref.sha256)continue;
   if(!Number.isInteger(row.page)||!Number.isInteger(row.page_end)||row.page<1||row.page_end>loaded.pages||row.page_end<row.page||row.page_end-row.page>=4)continue;
   if(row.content_sha256!==sha(loaded.raw.slice((row.page-1)*PAGE_SIZE,row.page_end*PAGE_SIZE)))continue;
   for(let n=row.page;n<=row.page_end;n++)seen.add(n);
  }
  if(seen.size!==loaded.pages)fail('core pages not fully emitted; read remaining core before submitting');
  const body=reportMarkdown(checked.result),file=path.join(dir,'report.md'),digest=sha(body);
  let existing;try{existing=await readJSON(path.join(dir,'receipt.json'));}catch(e){if(e.code!=='ENOENT')throw e;}
  if(existing){if(existing.report_sha256!==digest)fail('a different report is already submitted; do not overwrite');return existing;}
  try{await fs.writeFile(file,body,{flag:'wx'});}catch(e){if(e.code!=='EEXIST'||sha(await fs.readFile(file))!==digest)throw e;}
  const receipt={schema:'liuren-codex-receipt-v1',run:dir,status:checked.status,report_file:file,report_sha256:digest,
   packet_ref:record.packet_ref,core_pages_emitted:seen.size,validationScope:'transport-only',professionalContentChecked:false};
  await writeJSON(path.join(dir,'receipt.json'),receipt);return receipt;
 }
 if(req.action==='result'){
  const receipt=await readJSON(path.join(dir,'receipt.json')),body=await fs.readFile(receipt.report_file,'utf8');
  if(path.resolve(receipt.report_file)!==path.join(dir,'report.md')||sha(body)!==receipt.report_sha256)fail('saved report changed');
  return {...receipt,body};
 }
 fail('unsupported action');
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
 try{
  const args=process.argv.slice(2);
  const req=args.length===1&&args[0]==='status'?{action:'status'}:
   args.length===2&&args[0]==='--request'?await readJSON(args[1]):null;
  if(!req)fail('usage: node tools/liuren-codex.mjs status | --request UTF8_JSON_FILE');
  emit(await execute(req));
 }catch(e){process.stderr.write(e.message+'\n');process.exitCode=1;}
}
