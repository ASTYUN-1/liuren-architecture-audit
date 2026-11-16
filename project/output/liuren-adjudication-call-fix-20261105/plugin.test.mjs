import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import plugin from './candidate/.opencode/plugins/liuren-adjudication.ts';
import {savePacket} from './candidate/tools/liuren-adjudication-files.mjs';
const directory=fileURLToPath(new URL('./candidate',import.meta.url));
const packet=JSON.parse(await fs.readFile(new URL('./synthetic-input.json',import.meta.url),'utf8'));
async function setup(){
  const saved=await savePacket(directory,packet,'parent-test');
  const client={session:{get:async()=>({data:{parentID:'parent-test'}}),messages:async()=>({data:[{info:{role:'user'},parts:[{type:'text',text:saved.task_prompt}]}]})}};
  const hooks=await plugin({directory,client});
  const input={tool:'task',sessionID:'parent-test',callID:Math.random().toString()};
  const output={args:{subagent_type:'liuren-adjudicator',description:'倾向标题',prompt:saved.task_prompt}};
  return {saved,hooks,input,output};
}
test('file task rejects resume, escaped JSON and wrong parent before child creation',async()=>{
  const {hooks,input,output}=await setup();
  await assert.rejects(hooks['tool.execute.before'](input,{args:{...output.args,task_id:'old'}}),/FRESH_SESSION/);
  await assert.rejects(hooks['tool.execute.before'](input,{args:{...output.args,prompt:'{\\"schema\\":1}'}}),/liuren_adjudication_packet/);
  await assert.rejects(hooks['tool.execute.before']({...input,sessionID:'other'},output),/PARENT_MISMATCH/);
});
test('scoped reader enforces child identity path and all pages before validated return',async()=>{
  const {saved,hooks,input,output}=await setup();
  await hooks['tool.execute.before'](input,output);assert.equal(output.args.description,'大六壬独立裁决');
  const context={agent:'liuren-adjudicator',sessionID:'child-test'};
  await assert.rejects(hooks.tool.liuren_adjudication_read.execute({...saved,page:1},{...context,agent:'liuren'}),/READER_ONLY/);
  await assert.rejects(hooks.tool.liuren_adjudication_read.execute({...saved,file_path:'wrong',page:1},context),/UNAUTHORIZED/);
  const page=JSON.parse(await hooks.tool.liuren_adjudication_read.execute({...saved,page:1},context));
  for(let i=2;i<=page.pages;i++)await hooks.tool.liuren_adjudication_read.execute({...saved,page:i},context);
  const answer={schema:'liuren-adjudication-output-v1',request_id:packet.request_id,status:'needs_input',entity_checks:[],relation_checks:[],answers:[{question_id:'Q1',verdict:'需补资料',precision:'unresolved',decisive_relation_ids:[],counter_relation_ids:[],counter_resolution:'待补',process:'未定',timing:'不适用',conditions:[],limits:[]}],source_conflicts:[],missing_inputs:['补具体条件']};
  const after={output:JSON.stringify(answer),metadata:{sessionId:'child-test'}};
  await hooks['tool.execute.after'](input,after);
  assert.equal(after.metadata.liurenAdjudication.fileReadVerified,true);
  assert.equal(after.metadata.liurenAdjudication.contractChecked,true);
});
test('unread packet cannot be accepted and designated model remains high',async()=>{
  const {hooks,input,output}=await setup();await hooks['tool.execute.before'](input,output);
  const after={output:'{}',metadata:{sessionId:'unread-child'}};await hooks['tool.execute.after'](input,after);
  assert.match(after.output,/FILE_NOT_FULLY_READ/);
  const params={options:{}};
  await hooks['chat.params']({agent:'liuren-adjudicator',model:{providerID:'deepseek',id:'deepseek-flash'}},params);
  assert.equal(params.maxOutputTokens,65536);assert.equal(params.options.reasoningEffort,'high');
});
test('replay actual returned response through full file-read and output hooks',async()=>{
  const raw=await fs.readFile(new URL('./smoke-child-visible-output.txt',import.meta.url),'utf8');
  const returned=raw.slice(raw.indexOf('{"schema":"liuren-adjudication-output-v1"'));
  const {saved,hooks,input,output}=await setup();await hooks['tool.execute.before'](input,output);
  const context={agent:'liuren-adjudicator',sessionID:'child-test'};
  const page=JSON.parse(await hooks.tool.liuren_adjudication_read.execute({...saved,page:1},context));
  for(let i=2;i<=page.pages;i++)await hooks.tool.liuren_adjudication_read.execute({...saved,page:i},context);
  const after={output:returned,metadata:{sessionId:'child-test'}};await hooks['tool.execute.after'](input,after);
  assert.equal(after.metadata.liurenAdjudication.contractChecked,true);
  assert.equal(after.metadata.liurenAdjudication.fileReadVerified,true);
  assert.equal(JSON.parse(after.output).status,'completed');
  await fs.writeFile(new URL('./actual-response-replay.json',import.meta.url),JSON.stringify({replayed:true,modelCalled:false,metadata:after.metadata.liurenAdjudication},null,2));
});
