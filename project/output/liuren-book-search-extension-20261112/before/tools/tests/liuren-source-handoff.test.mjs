import test from 'node:test';
import assert from 'node:assert/strict';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {fileURLToPath} from 'node:url';
import {sourceMaterial} from '../liuren-deterministic-io.mjs';

const root=fileURLToPath(new URL('../../',import.meta.url)),run=promisify(execFile);
async function materials(request){
 const result=await run(process.platform==='win32'?'python':'python3',['-X','utf8','tools/liuren-materials.py','--request',JSON.stringify(request)],{cwd:root,encoding:'utf8',windowsHide:true});
 return result.stdout;
}
test('actual method reader references can be consumed without model path or hash conversion',async()=>{
 const raw=await materials({action:'method',module:'class-mapping'});
 const meta=JSON.parse(raw.split('\n')[0].slice('LIUREN_METHOD_BEGIN '.length));
 const ref=await sourceMaterial(root,meta.handoff);
 assert.equal(ref.sha256,meta.fileSha256);
 const absolute=await sourceMaterial(root,{...meta.handoff,source_path:meta.file});
 assert.equal(absolute.source_path,ref.source_path);assert.equal(absolute.quote,ref.quote);
});
test('actual complete book search references preserve the source hash and line convention',async()=>{
 const result=JSON.parse(await materials({action:'book_search',book:'TY',query:'死火 旺金',limit:1,max_chars:24000}));
 assert.ok(result.hits.length);
 const hit=result.hits[0];assert.equal(hit.passage_complete,true);assert.ok(hit.handoff);
 const ref=await sourceMaterial(root,hit.handoff);
 assert.equal(ref.sha256,hit.fileSha256);assert.equal(ref.line_mode,'universal');
 assert.ok(ref.line_start<=hit.start&&ref.line_end>=hit.end);assert.ok(ref.quote.includes('旺金'));
});
