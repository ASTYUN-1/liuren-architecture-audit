import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,readFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {resolve,relative} from 'node:path';
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
  let prompt;const received=[];
  const hooks=await plugin({directory:root,client:{session:{
    get:async()=>({data:{parentID:'parent'}}),
    messages:async()=>({data:[{info:{role:'user'},parts:[{type:'text',text:prompt}]},{info:{role:'assistant'},parts:received}]})}}});
  const p=packet();if(long){p.observations[0].statement='完整读取测试'.repeat(800);p.unknowns=['多页边界测试'.repeat(800)];}
  // Use native schema parser as well as execute: prompt/tool schema must agree.
  const parsed=hooks.tool.liuren_adjudication_packet.args.packet.parse(p);
  const saved=JSON.parse(await hooks.tool.liuren_adjudication_packet.execute({packet:parsed},{agent:'liuren',sessionID:'parent'}));
  prompt=saved.task_prompt;
  const input={tool:'task',sessionID:'parent',callID:'call1'};
  const args={subagent_type:'liuren-adjudicator',prompt};
  const record=raw=>{received.push({type:'tool',tool:'liuren_adjudication_read',state:{status:'completed',output:typeof raw==='string'?raw:raw.output,metadata:typeof raw==='string'?{}:raw.metadata}});return raw;};
  const reader=async(page=1,extra={})=>record(await hooks.tool.liuren_adjudication_read.execute({file_path:saved.file_path,sha256:saved.sha256,page,...extra},{agent:'liuren-adjudicator',sessionID:'child'}));
  const start=()=>hooks['tool.execute.before'](input,{args});
  const finish=async(r=result())=>{
    const output={output:JSON.stringify(r),metadata:{sessionId:'child'}};
    await hooks['tool.execute.after'](input,output);return output;
  };
  return {hooks,p,saved,args,input,reader,start,finish,record,received};
}

test('native plugin packet -> short task -> all pages -> v2 checked response',async t=>{
  const h=await harness(t,{long:true});await h.start();
  assert.equal(h.args.prompt.split('\n').length,3);
  const first=JSON.parse(await h.reader());assert.ok(first.pages>1);
  for(let page=2;page<=first.pages;page++)await h.reader(page);
  const out=await h.finish();assert.equal(JSON.parse(out.output).status,'completed');
  assert.equal(out.metadata.liurenAdjudication.professionalContentChecked,false);
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
test('plugin keeps DeepSeek high thinking and its supported output budget',async t=>{
  const h=await harness(t),out={options:{},maxOutputTokens:32000};
  await h.hooks['chat.params']({agent:'liuren-adjudicator',model:{providerID:'deepseek',id:'deepseek-flash'}},out);
  assert.equal(out.options.reasoningEffort,'high');assert.equal(out.maxOutputTokens,393216);
  const unspecified={options:{}};
  await h.hooks['chat.params']({agent:'liuren-adjudicator',model:{providerID:'deepseek',id:'deepseek-flash'}},unspecified);
  assert.equal(unspecified.maxOutputTokens,393216);
  const main={options:{},maxOutputTokens:32000};
  await h.hooks['chat.params']({agent:'liuren',model:{providerID:'other',id:'other'}},main);
  assert.deepEqual(main,{options:{},maxOutputTokens:32000});
  await assert.rejects(()=>h.hooks['chat.params']({agent:'liuren-adjudicator',model:{providerID:'other',id:'other'}},{options:{}}),/MODEL_MISMATCH/);
});
test('report field omissions do not become tool failures',async t=>{
  const h=await harness(t);await h.start();await h.reader();const r=result();r.issue_resolutions=[];
  const out=await h.finish(r);assert.equal(JSON.parse(out.output).status,'completed');
  assert.equal(out.metadata.liurenAdjudication.professionalContentChecked,false);
});
test('request tampering after task dispatch fails integrity validation',async t=>{
  const h=await harness(t);await h.start();await h.reader();
  await writeFile(h.saved.file_path,(await readFile(h.saved.file_path,'utf8'))+' ');
  const out=await h.finish();assert.match(JSON.parse(out.output).error,/changed or oversized/);
});

test('execute collects duplicate fact/issue IDs and enum errors even without host schema parsing',async t=>{
  const h=await harness(t),p=structuredClone(h.p);
  p.facts=[{id:'F01',text:'合成事实',source:'合成'}];p.focus_issues[0].id='F01';
  p.observations[0].kind='not_a_kind';p.observations[0].verification='not_a_verification';
  await assert.rejects(()=>h.hooks.tool.liuren_adjudication_packet.execute({packet:p},{agent:'liuren',sessionID:'parent'}),e=>{
    const value=JSON.parse(e.message.split('LIUREN_PACKET_ARGUMENTS: ')[1]);
    assert.ok(value.issues.some(x=>x.path==='/packet/observations/0/kind'));
    assert.ok(value.issues.some(x=>x.path==='/packet/observations/0/verification'));
    assert.ok(value.issues.some(x=>x.path==='/packet/focus_issues/0/id'&&x.conflicts_with==='/packet/facts/0/id'));
    return true;
  });
  assert.equal(p.focus_issues[0].id,'F01','invalid input is not silently rewritten');
});

test('shensha observation is transported without promoting interpretation to program fact',async t=>{
  const h=await harness(t),p=structuredClone(h.p);p.observations[0].kind='shensha';
  const saved=JSON.parse(await h.hooks.tool.liuren_adjudication_packet.execute({packet:p},{agent:'liuren',sessionID:'parent'}));
  const body=JSON.parse(await readFile(saved.file_path,'utf8'));
  assert.equal(body.packet.observations[0].kind,'shensha');
  assert.equal(body.packet.observations[0].verification,'unverified');
  assert.equal(saved.next_call.arguments.prompt,saved.task_prompt);
});

test('read continuation lists actual remaining pages and applies default page at execution',async t=>{
  const h=await harness(t,{long:true});await h.start();
  const first=JSON.parse(await h.reader(undefined));
  assert.equal(first.page,1);assert.ok(first.remaining_pages.length);
  let value=first;
  while(value.next_call){const raw=h.record(await h.hooks.tool[value.next_call.tool].execute(value.next_call.arguments,{agent:'liuren-adjudicator',sessionID:'child'}));value=JSON.parse(typeof raw==='string'?raw:raw.output);}
  assert.equal(value.remaining_pages.length,0);assert.equal(value.next_call,null);
});

test('bounded batched reads transport every original byte under the configured native-host limit',async t=>{
 const h=await harness(t,{long:true});await h.start();
 let args={file_path:h.saved.file_path,sha256:h.saved.sha256,page:1,page_count:4},text='',calls=0,last;
 do{
  const response=h.record(await h.hooks.tool.liuren_adjudication_read.execute(args,{agent:'liuren-adjudicator',sessionID:'child'}));
  assert.ok(Buffer.byteLength(response.output)<350000);
  assert.equal(response.metadata.truncated,false);const page=JSON.parse(response.output);
  assert.ok(page.page_end-page.page<4);assert.equal(page.page,args.page);text+=page.content;calls++;last=page;
  args=page.next_call?.arguments;
 }while(args);
 assert.equal(text,await readFile(h.saved.file_path,'utf8'));assert.equal(calls,Math.ceil(last.pages/4));
 assert.equal(JSON.parse((await h.finish()).output).status,'completed');
});

test('an executed batch is not complete reading when the native host truncated its receipt',async t=>{
 const h=await harness(t);await h.start();await h.reader();
 h.received[0].state.metadata={truncated:true};h.received[0].state.output='... bytes truncated ...';
 assert.match(JSON.parse((await h.finish()).output).error,/NOT_FULLY_READ/);
});

test('tool help publishes the executable packet schema and confines adjudicator help',async t=>{
  const h=await harness(t),context={agent:'liuren',sessionID:'parent'};
  const help=JSON.parse(await h.hooks.tool.liuren_tool_help.execute({topic:'packet'},context));
  const packetSchema=help.parameters.properties.packet;
  assert.ok(packetSchema.properties.observations.items.properties.kind.enum.includes('shensha'));
  assert.match(help.id_convention,/全局唯一/);
  const compute=JSON.parse(await h.hooks.tool.liuren_tool_help.execute({topic:'compute'},context));
  assert.deepEqual(compute.archive_required_for_primary,['chart','lookup','life','strength','imagery','evaluation','quantity with quantity_method']);
  await assert.rejects(()=>h.hooks.tool.liuren_tool_help.execute({topic:'packet'},{agent:'liuren-adjudicator',sessionID:'child'}),/DENIED/);
});

test('all workflow tool schemas have caller-accessible help without schema references',async t=>{
 const h=await harness(t);
 for(const topic of ['packet','compute','result','read','submit','audit','chart','materials']){
  const help=JSON.parse(await h.hooks.tool.liuren_tool_help.execute({topic},{agent:'liuren',sessionID:'parent'}));
  assert.ok(help.tool);assert.equal(help.parameters.type,'object');assert.ok(!JSON.stringify(help.parameters).includes('"$ref"'),topic);
 }
 for(const topic of ['compute','read','submit','audit'])assert.ok(JSON.parse(await h.hooks.tool.liuren_tool_help.execute({topic},{agent:'liuren-adjudicator',sessionID:'child'})).parameters);
});

test('life without archive reports the conditional requirement and preservation instruction',async t=>{
  const h=await harness(t);
  await assert.rejects(()=>h.hooks.tool.liuren_compute.execute({action:'life',life:{age:25,sex:'男',age_basis:'虚岁-已核'}},{agent:'liuren',sessionID:'parent'}),e=>/\/archive/.test(e.message)&&/life/.test(e.message)&&/只补archive/.test(e.message));
});
test('program archive is copied with hash verification and focus references retained',async t=>{
  const h=await harness(t),root=resolve(h.saved.file_path,'../../..');
  const folder=resolve(root,'排盘存档/六壬');await mkdir(folder,{recursive:true});
  const archive=resolve(folder,'synthetic.json');
  const rawHash='a'.repeat(64);
  const raw=JSON.stringify({_direct:{schema:'liuren-direct-corrected-export-v1',validation:{ok:true},facts:h.p.chart.facts,raw_sha256:rawHash}});
  await writeFile(archive,raw);
  const p=packet();p.chart={source:'合成归档',archive:{path:archive,sha256:digest(raw)}};
  const saved=JSON.parse(await h.hooks.tool.liuren_adjudication_packet.execute({packet:p},{agent:'liuren',sessionID:'parent'}));
  const body=JSON.parse(await readFile(saved.file_path,'utf8'));
  p.chart.archive.path=relative(root,archive);
  const relativeSaved=JSON.parse(await h.hooks.tool.liuren_adjudication_packet.execute({packet:p},{agent:'liuren',sessionID:'parent'}));
  assert.ok(relativeSaved.file_path);
  p.chart.archive.path='../'+relative(root,archive);
  await assert.rejects(()=>h.hooks.tool.liuren_adjudication_packet.execute({packet:p},{agent:'liuren',sessionID:'parent'}),/original path/);
  p.chart.archive.path=archive;
  assert.deepEqual(body.packet.chart.facts,h.p.chart.facts);assert.equal(body.packet.focus_issues[0].id,'C1');
  p.chart.archive.raw_sha256=rawHash;
  const fullArgs={packet:p};
  h.hooks.tool.liuren_adjudication_packet.args.packet.parse(p);
  assert.ok(JSON.parse(await h.hooks.tool.liuren_adjudication_packet.execute(fullArgs,{agent:'liuren',sessionID:'parent'})).file_path);
  p.chart.archive.raw_sha256='b'.repeat(64);
  await assert.rejects(()=>h.hooks.tool.liuren_adjudication_packet.execute(fullArgs,{agent:'liuren',sessionID:'parent'}),/raw_sha256 mismatch/);
  delete p.chart.archive.raw_sha256;
  p.chart.archive.sha256='0'.repeat(64);
  await assert.rejects(()=>h.hooks.tool.liuren_adjudication_packet.execute({packet:p},{agent:'liuren',sessionID:'parent'}),/sha256 mismatch/);
});
