import test from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';
import {isEntryPoint} from './candidate/tools/liuren-direct.mjs';
const direct=new URL('./candidate/tools/liuren-direct.mjs',import.meta.url);
test('real script entry is still recognized while another file is not',()=>{
  assert.equal(isEntryPoint(fileURLToPath(direct),direct.href),true);
  assert.equal(isEntryPoint(fileURLToPath(import.meta.url),direct.href),false);
});
test('missing compiled-host virtual entry is not a CLI and does not throw',()=>{
  assert.equal(isEntryPoint('B:/~BUN/root/src/index.js',direct.href),false);
  assert.equal(isEntryPoint(undefined,direct.href),false);
});
test('shensha and direct modules import safely under a compiled Bun argv',()=>{
  const shensha=new URL('./candidate/tools/liuren-shensha.mjs',import.meta.url);
  const script='process.argv[1]="B:/~BUN/root/src/index.js"; const m=await import('+JSON.stringify(shensha.href)+'); if(typeof m.runChartWithShensha!=="function")throw Error("bad import"); console.log("IMPORTED_ONLY");';
  const result=execFileSync(process.execPath,['--input-type=module','-e',script],{encoding:'utf8'});
  assert.equal(result.trim(),'IMPORTED_ONLY');
});
