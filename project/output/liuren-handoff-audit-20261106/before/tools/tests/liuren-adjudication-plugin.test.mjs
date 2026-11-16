import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,readFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {resolve} from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {registerHooks} from 'node:module';
import {packet,result,moduleURL} from './fixtures/liuren-adjudication-v2.mjs';

// Resolve the installed native SDK, also when executing candidate code in output/.
const workspace=fileURLToPath(new URL('../../',import.meta.url));
registerHooks({resolve(specifier,context,nextResolve){
  if(specifier==='@opencode-ai/plugin')return nextResolve(pathToFileURL(resolve(workspace,'.opencode/node_modules/@opencode-ai/plugin/dist/index.js')).href,context);
  return nextResolve(specifier,context);
}});
const {default:plugin}=await import(moduleURL('.opencode/plugins/liuren-adjudication.ts'));
const {digest}=await import(moduleURL('tools/liuren-adjudication-files.mjs'));

async function harness(t,{long=false}={}){
  const root=await mkdtemp(resolve(tmpdir(),'liuren-v2-test-'));
  t.after(()=>rm(root,{recursive:true,force:true}));
  await mkdir(resolve(root,'.opencode'));
  await writeFile(resolve(root,'.opencode/liuren-active.json'),JSON.stringify({adjudication:{agent:'liuren-adjudicator'}}));
  let prompt;
  const hooks=await plugin({directory:root,client:{session:{
    get:async()=>({data:{parentID:'parent'}}),
    messages:async()=>({data:[{info:{role:'user'},parts:[{type:'text',text:prompt}]}]})}}});
  const p=packet();if(long){p.observations[0].statement='完整读取测试'.repeat(800);p.unknowns=['多页边界测试'.repeat(800)];}
  // Use native schema parser as well as execute: prompt/tool schema must agree.
  const parsed=hooks.tool.liuren_adjudication_packet.args.packet.parse(p);
  const saved=JSON.parse(await hooks.tool.liuren_adjudication_packet.execute({packet:parsed},{agent:'liuren',sessionID:'parent'}));
  prompt=saved.task_prompt;
  const input={tool:'task',sessionID:'parent',callID:'call1'};
  const args={subagent_type:'liuren-adjudicator',prompt};
  const reader=(page=1,extra={})=>hooks.tool.liuren_adjudication_read.execute({file_path:saved.file_path,sha256:saved.sha256,page,...extra},{agent:'liuren-adjudicator',sessionID:'child'});
  const start=()=>hooks['tool.execute.before'](input,{args});
  const finish=async(r=result())=>{
    const output={output:JSON.stringify(r),metadata:{sessionId:'child'}};
    await hooks['tool.execute.after'](input,output);return output;
  };
  return {hooks,p,saved,args,input,reader,start,finish};
}

test('native plugin packet -> short task -> all pages -> v2 checked response',async t=>{
  const h=await harness(t,{long:true});await h.start();
  assert.equal(h.args.prompt.split('\n').length,3);
  const first=JSON.parse(await h.reader());assert.ok(first.pages>1);
  for(let page=2;page<=first.pages;page++)await h.reader(page);
  const out=await h.finish();assert.equal(JSON.parse(out.output).status,'completed');
  assert.equal(out.metadata.liurenAdjudication.focusIssuesChecked,1);
  assert.equal(out.metadata.liurenAdjudication.fileReadVerified,true);
});
test('plugin blocks unread or partially read material',async t=>{
  const h=await harness(t,{long:true});await h.start();await h.reader();
  const out=await h.finish();assert.match(JSON.parse(out.output).error,/NOT_FULLY_READ/);
});
test('plugin only permits the exact bound request file',async t=>{
  const h=await harness(t);await h.start();await assert.rejects(()=>h.reader(1,{sha256:'0'.repeat(64)}),/UNAUTHORIZED_FILE/);
});
test('plugin rejects old task reuse and background dispatch',async t=>{
  const h=await harness(t);h.args.task_id='old';await assert.rejects(h.start,/FRESH_SESSION/);
  delete h.args.task_id;h.args.background=true;await assert.rejects(h.start,/FOREGROUND/);
});
test('plugin rejects a request belonging to another parent session',async t=>{
  const h=await harness(t);h.input.sessionID='other';await assert.rejects(h.start,/PARENT_MISMATCH/);
});
test('plugin keeps the requested model and high thinking configuration',async t=>{
  const h=await harness(t),out={options:{}};
  await h.hooks['chat.params']({agent:'liuren-adjudicator',model:{providerID:'deepseek',id:'deepseek-flash'}},out);
  assert.equal(out.options.reasoningEffort,'high');assert.equal(out.maxOutputTokens,65536);
  await assert.rejects(()=>h.hooks['chat.params']({agent:'liuren-adjudicator',model:{providerID:'other',id:'other'}},{options:{}}),/MODEL_MISMATCH/);
});
test('invalid v2 return is exposed as failure rather than a usable verdict',async t=>{
  const h=await harness(t);await h.start();await h.reader();const r=result();r.issue_resolutions=[];
  const out=await h.finish(r);assert.equal(JSON.parse(out.output).status,'invalid_output');
  assert.equal(out.metadata.liurenAdjudication.contractChecked,false);
});
test('request tampering after task dispatch fails integrity validation',async t=>{
  const h=await harness(t);await h.start();await h.reader();
  await writeFile(h.saved.file_path,(await readFile(h.saved.file_path,'utf8'))+' ');
  const out=await h.finish();assert.match(JSON.parse(out.output).error,/changed or oversized/);
});
test('program archive is copied with hash verification and focus references retained',async t=>{
  const h=await harness(t),root=resolve(h.saved.file_path,'../../..');
  const folder=resolve(root,'排盘存档/六壬');await mkdir(folder,{recursive:true});
  const archive=resolve(folder,'synthetic.json');
  const raw=JSON.stringify({_direct:{schema:'liuren-direct-corrected-export-v1',validation:{ok:true},facts:h.p.chart.facts}});
  await writeFile(archive,raw);
  const p=packet();p.chart={source:'合成归档',archive:{path:archive,sha256:digest(raw)}};
  const saved=JSON.parse(await h.hooks.tool.liuren_adjudication_packet.execute({packet:p},{agent:'liuren',sessionID:'parent'}));
  const body=JSON.parse(await readFile(saved.file_path,'utf8'));
  assert.deepEqual(body.packet.chart.facts,h.p.chart.facts);assert.equal(body.packet.focus_issues[0].id,'C1');
  p.chart.archive.sha256='0'.repeat(64);
  await assert.rejects(()=>h.hooks.tool.liuren_adjudication_packet.execute({packet:p},{agent:'liuren',sessionID:'parent'}),/sha256 mismatch/);
});
