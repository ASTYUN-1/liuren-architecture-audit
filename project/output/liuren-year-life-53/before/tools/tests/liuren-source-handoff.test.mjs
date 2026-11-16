import test from 'node:test';
import assert from 'node:assert/strict';
import {execFile} from 'node:child_process';
import {promisify} from 'node:util';
import {fileURLToPath} from 'node:url';
import {sourceMaterial} from '../liuren-deterministic-io.mjs';
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';

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

test('all added books and legacy encodings survive search to adjudication source handoff',async()=>{
 for(const [book,query] of [['QA','症候'],['KN','类神'],['TR','应聘'],['KE','禄为工作']]){
  const result=JSON.parse(await materials({action:'book_search',book,query,limit:1,max_chars:24000}));
  const hit=result.hits[0];assert.ok(hit?.handoff,book+' complete handoff');
  const ref=await sourceMaterial(root,hit.handoff);
  assert.equal(ref.sha256,hit.fileSha256);
  const raw=await fs.readFile(new URL('../../'+hit.path,import.meta.url));
  assert.equal(ref.sha256,createHash('sha256').update(raw).digest('hex'));
  assert.ok(ref.quote.includes(query),book+' decoded content');
  const lines=new TextDecoder(hit.sourceEncoding==='utf-8-sig'?'utf-8':hit.sourceEncoding,{fatal:true}).decode(raw).split(/\r\n|[\n\r\v\f\u001c-\u001e\u0085\u2028\u2029]/);
  assert.equal(ref.quote,lines.slice(ref.line_start-1,ref.line_end).join('\n'));
 }
});
