import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {fileURLToPath, pathToFileURL} from 'node:url';
const here=fileURLToPath(new URL('./',import.meta.url));
const root=path.resolve(here,'../..');
const pointer=JSON.parse(await fs.readFile(path.join(root,'.opencode/liuren-active.json'),'utf8'));
const runtime=path.join(root,pointer.runtime);
const manifest=JSON.parse(await fs.readFile(path.join(runtime,'manifest.json'),'utf8'));
const material=(await import(pathToFileURL(path.join(root,'.opencode/tools/liuren_materials.ts')).href)).default;
const context={sessionID:'adjudication-local-verification',abort:new AbortController().signal};
const sha=raw=>crypto.createHash('sha256').update(raw).digest('hex');
const results=[];
let overlay;
for(const key of ['positioning','liqi','structure','adjudication','evidence','report','exam']){
  const text=await material.execute({action:'method',module:key},context);
  const [header,...remaining]=text.split('\n');
  assert.ok(header.startsWith('LIUREN_METHOD_BEGIN '));
  const meta=JSON.parse(header.slice('LIUREN_METHOD_BEGIN '.length));
  const rest=remaining.join('\n');
  const marker=rest.lastIndexOf('\nLIUREN_METHOD_END ');
  assert.ok(marker>=0);
  const body=rest.slice(0,marker);
  const expected=await fs.readFile(path.join(runtime,manifest.modules[key].file));
  assert.equal(body,expected.toString('utf8').replaceAll('\r\n','\n'));
  assert.equal(meta.fileSha256,sha(expected));
  assert.equal(meta.textSha256,sha(Buffer.from(body)));
  assert.equal(meta.release,pointer.release);
  assert.equal(meta.version,pointer.methodVersion);
  assert.equal(meta.completeModule,true);
  if(overlay)assert.equal(meta.overlayFingerprint,overlay);
  overlay=meta.overlayFingerprint;
  results.push({check:'native-complete-method',module:key});
}
for(const rel of ['references/expert-adjudication.md','references/expert-adjudication-cases.md',
                  'references/expert-adjudication-excerpts.md','references/expert-adjudication-sources.json',
                  'procedures/liuren-cases.md','procedures/liuren-extract.md']){
  let start=1,lines=[],identity;
  do{
    const result=JSON.parse(await material.execute({action:'read',path:pointer.runtime.replaceAll('/','\\')+'\\'+rel.replaceAll('/','\\'),start,count:300},context));
    assert.equal(result.start,start);
    if(identity)assert.equal(result.fileSha256,identity);
    identity=result.fileSha256;
    // read() reports a string with one-based line numbers.
    const chunk=result.text.split('\n');
    for(let i=0;i<chunk.length;i++){
      assert.ok(chunk[i].startsWith(`${start+i}: `));
      lines.push(chunk[i].slice(`${start+i}: `.length));
    }
    start=result.next_line;
  }while(start!==null);
  const expected=await fs.readFile(path.join(runtime,rel));
  assert.equal(identity,sha(expected));
  const expectedLines=expected.toString('utf8').split(/\r\n|[\n\r\v\f\x1c-\x1e\x85\u2028\u2029]/u);
  if(expectedLines.at(-1)==='')expectedLines.pop();
  assert.equal(lines.length,expectedLines.length);
  assert.deepEqual(lines,expectedLines);
  results.push({check:'native-paged-reference',file:rel,lines:lines.length});
}
await assert.rejects(()=>material.execute({action:'read',path:'opencode.json',start:1,count:20},context));
await assert.rejects(()=>material.execute({action:'read',path:'runtime/liuren/20261105-restructure-01/methods/liqi.md',start:1,count:20},context));
results.push({check:'config-and-unregistered-old-runtime-denied'});
const result={ok:true,release:pointer.release,methodVersion:pointer.methodVersion,overlayFingerprint:overlay,checks:results,modelCalls:0,predictiveValidationCount:0};
await fs.writeFile(path.join(here,'transports.json'),JSON.stringify(result,null,2)+'\n');
process.stdout.write(JSON.stringify({ok:true,release:pointer.release,checks:results.length,modelCalls:0})+'\n');
