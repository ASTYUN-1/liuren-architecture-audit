import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {validateOutput} from './source/liuren-adjudication-contract.mjs';
const p=JSON.parse(await fs.readFile(new URL('./synthetic-input.json',import.meta.url),'utf8'));
const raw=await fs.readFile(new URL('./smoke-child-visible-output.txt',import.meta.url),'utf8');
const result=JSON.parse(raw.slice(raw.indexOf('{"schema":"liuren-adjudication-output-v1"')));
test('actual file-reader response preserves annotated entity symbols and passes contract',()=>{
  assert.equal(validateOutput(result,p).status,'completed');
  assert.equal(result.entity_checks[0].branch,'亥（天盘，临地盘丑）');
});
test('annotation allowance still rejects blank symbols and forged references',()=>{
  let r=structuredClone(result);r.entity_checks[0].branch='总体偏吉';assert.throws(()=>validateOutput(r,p),/symbol/);
  r=structuredClone(result);r.relation_checks[0].basis_ids=['E99'];assert.throws(()=>validateOutput(r,p),/reference/);
});
