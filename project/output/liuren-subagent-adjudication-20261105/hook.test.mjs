import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import plugin from './candidate/.opencode/plugins/liuren-adjudication.ts';
const directory=fileURLToPath(new URL('./candidate',import.meta.url));
const packet=JSON.parse(await fs.readFile(new URL('./synthetic-input.json',import.meta.url),'utf8'));
const call=(n=1)=>({tool:'task',sessionID:'synthetic-parent',callID:'test-'+n});
const args=()=>({subagent_type:'liuren-adjudicator',description:'此字段会被中性标题替换',prompt:JSON.stringify(packet)});
test('task hook rejects session reuse and asynchronous unvalidated return',async()=>{
  const hooks=await plugin({directory});
  await assert.rejects(hooks['tool.execute.before'](call(),{args:{...args(),task_id:'previous-child'}}),/FRESH_SESSION/);
  await assert.rejects(hooks['tool.execute.before'](call(),{args:{...args(),background:true}}),/FOREGROUND/);
});
test('task hook normalizes description and rejects extra verdict payload',async()=>{
  const hooks=await plugin({directory});let out={args:args()};
  await hooks['tool.execute.before'](call(),out);assert.equal(out.args.description,'大六壬独立裁决');assert.deepEqual(JSON.parse(out.args.prompt),packet);
  out={args:{...args(),prompt:JSON.stringify({...packet,known_result:'已知答案'})}};
  await assert.rejects(hooks['tool.execute.before'](call(2),out),/unexpected/);
});
test('invalid returned prose becomes explicit incomplete adjudication, not a verdict',async()=>{
  const hooks=await plugin({directory});const before={args:args()};await hooks['tool.execute.before'](call(),before);
  const after={output:'我觉得折中选一个',metadata:{sessionId:'synthetic-child'}};
  await hooks['tool.execute.after']({...call(),args:before.args},after);
  assert.equal(JSON.parse(after.output).status,'invalid_output');assert.equal(after.metadata.liurenAdjudication.contractChecked,false);assert.equal(after.metadata.sessionId,'synthetic-child');
});
test('adjudicator uses high effort and refuses another model',async()=>{
  const hooks=await plugin({directory});const out={options:{}};
  await hooks['chat.params']({agent:'liuren-adjudicator',model:{providerID:'deepseek',id:'deepseek-flash'}},out);assert.equal(out.options.reasoningEffort,'high');
  assert.equal(out.maxOutputTokens,65536);
  await assert.rejects(hooks['chat.params']({agent:'liuren-adjudicator',model:{providerID:'conpera',id:'gpt-6.1-sol'}},out),/MODEL_MISMATCH/);
});
