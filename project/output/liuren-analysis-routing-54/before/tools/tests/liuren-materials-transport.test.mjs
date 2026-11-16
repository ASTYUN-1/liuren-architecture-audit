import test from 'node:test';
import assert from 'node:assert/strict';
import tool from '../../.opencode/tools/liuren_materials.ts';
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';

const context = sessionID => ({ sessionID, abort: new AbortController().signal });
const firstLine = text => {
  const line=text.split('\n',1)[0], space=line.indexOf(' ');
  return [line.slice(0,space),JSON.parse(line.slice(space+1))];
};
const bodies = text => text.split('LIUREN_TEXT_BEGIN ').slice(1).map(chunk => {
  const start=chunk.indexOf('\n'),end=chunk.indexOf('\nLIUREN_TEXT_END ');
  return [JSON.parse(chunk.slice(0,start)),chunk.slice(start+1,end)];
});

test('native material execution uses the trusted session directory instead of the plugin installation directory',async t=>{
  const directory=await fs.mkdtemp(path.join(os.tmpdir(),'liuren-context-test-'));
  t.after(async()=>{assert.equal(path.dirname(path.resolve(directory)),path.resolve(os.tmpdir()));assert.ok(path.basename(directory).startsWith('liuren-context-test-'));await fs.rm(directory,{recursive:true,force:true});});
  await fs.mkdir(path.join(directory,'tools'));
  await fs.writeFile(path.join(directory,'tools/liuren-materials.py'),'import json,os,sys\nr=json.loads(sys.argv[sys.argv.index("--request")+1])\nprint(json.dumps({"directory":os.getcwd(),"session":r["_context_key"],"module":r["module"]}))\n');
  const result=JSON.parse(await tool.execute({action:'method',module:'report'},{...context('scoped-session'),directory}));
  assert.equal(await fs.realpath(result.directory),await fs.realpath(directory));assert.equal(result.session,'scoped-session');assert.equal(result.module,'report');
});

test('native tool reads a complete current method by ID without a batch plan',async()=>{
  assert.ok(tool.args.module);
  const text=await tool.execute({action:'method',module:'movement'},context('single-method-session'));
  const [label,meta]=firstLine(text);
  assert.equal(label,'LIUREN_METHOD_BEGIN');
  assert.equal(meta.module,'movement');
  assert.equal(meta.completeModule,true);
  const root=path.resolve(import.meta.dirname,'../..');
  const pointer=JSON.parse(await fs.readFile(path.join(root,'.opencode/liuren-active.json'),'utf8'));
  const manifest=JSON.parse(await fs.readFile(path.join(root,pointer.runtime,'manifest.json'),'utf8'));
  const relative=manifest.modules.movement.file;
  const expected=(await fs.readFile(path.join(root,pointer.runtime,relative),'utf8')).replaceAll('\r\n','\n');
  assert.equal(meta.fileSha256,manifest.files[relative]);
  assert.ok(text.includes('\n'+expected+'\nLIUREN_METHOD_END '));
  assert.ok(text.includes('LIUREN_METHOD_END '));
  assert.ok(!text.includes('LIUREN_READING_PLAN'));
  await assert.rejects(()=>tool.execute({action:'method',module:'../../opencode.json'},context('single-method-session')));
});

test('a stage batch returns the exact complete individual methods without host truncation',async()=>{
 const ctx=context('full-method-stage-batch');
 const response=await tool.execute({action:'method',modules:['relations','positioning']},ctx);
 assert.equal(response.metadata.truncated,false);
 const individual=await Promise.all(['relations','positioning'].map(module=>tool.execute({action:'method',module},ctx)));
 for(const text of individual)assert.ok(response.output.includes(text.trim()));
 assert.equal((response.output.match(/LIUREN_METHOD_BEGIN /g)??[]).length,2);
 await assert.rejects(()=>tool.execute({action:'method',module:'relations',modules:['positioning']},ctx),/二选一/);
});

test('native tool binds identity to trusted session, keeps old calls and full-plan escape',async()=>{
  assert.ok(tool.args.plan_id);
  assert.ok(tool.args.full_plan);
  assert.equal(tool.args._context_key,undefined);
  const args={action:'methods',domains:['illness'],batch:1};
  const first=await tool.execute(args,context('transport-session-A'));
  const [label,plan]=firstLine(first);
  assert.equal(label,'LIUREN_READING_PLAN');
  const next=await tool.execute({...args,plan_id:plan.plan_id},context('transport-session-A'));
  assert.equal(firstLine(next)[0],'LIUREN_READING_PLAN_REF');
  assert.deepEqual(bodies(next),bodies(first));
  const full=await tool.execute({...args,plan_id:plan.plan_id,full_plan:true},context('transport-session-A'));
  assert.equal(firstLine(full)[0],'LIUREN_READING_PLAN');
  const other=await tool.execute({...args,plan_id:plan.plan_id},context('transport-session-B'));
  assert.equal(firstLine(other)[0],'LIUREN_READING_PLAN');
  assert.notEqual(firstLine(other)[1].plan_id,plan.plan_id);
  assert.deepEqual(bodies(other),bodies(first));
});
