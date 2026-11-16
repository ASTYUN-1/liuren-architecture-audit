import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {store} from '../../tools/liuren-flow-control.mjs';
const root=process.cwd(),out=path.join(root,'output/liuren-receipt-fix-20261106'),parent='ses_e50b30172ffezjWWKjx2zDLh4n',child='ses_e50ab57a1ffeScZIPXHyM1WiJ7';
const hash=s=>createHash('sha256').update(s).digest('hex'),statePath=path.join(root,'output/liuren-flow-state',parent+'.json');
const stateRaw=await fs.readFile(statePath,'utf8'),state=JSON.parse(stateRaw),originalRef=state.results[child].artifact;
const originalRaw=await fs.readFile(originalRef.path,'utf8');assert.equal(hash(originalRaw),originalRef.sha256);
const original=JSON.parse(originalRaw);assert.equal(original.checked.ok,true);assert.equal(original.checked.result.status,'completed');
const active=JSON.parse(await fs.readFile(path.join(root,'.opencode/liuren-active.json'),'utf8'));
const temp=await fs.mkdtemp(path.join(os.tmpdir(),'liuren-real-recovery-'));
try{
 for(const rel of ['.opencode/liuren-active.json',active.runtime+'/manifest.json',active.runtime+'/references/adjudicator-book-evidence.json']){const dst=path.join(temp,rel);await fs.mkdir(path.dirname(dst),{recursive:true});await fs.copyFile(path.join(root,rel),dst);}
 const f=await store(temp),receipt=await f.saveResult(parent,child,original.packet,original.request_ref,original.raw,{pagesVerified:true});assert.equal(receipt.contractChecked,true);
 const replay=await f.getResult(parent,child,'read',{});assert.deepEqual(replay.result,original.checked.result);
 const manifest=JSON.parse(await fs.readFile(path.join(root,active.runtime,'manifest.json'),'utf8')),reportFile=manifest.modules.report.file,body=(await fs.readFile(path.join(root,active.runtime,reportFile),'utf8')).replaceAll('\r\n','\n');
 const meta={module:'report',release:active.release,fileSha256:manifest.files[reportFile],textSha256:hash(body)};
 await f.noteMethod(parent,'LIUREN_METHOD_BEGIN '+JSON.stringify(meta)+'\n'+body+'\nLIUREN_METHOD_END '+JSON.stringify({module:'report',textSha256:hash(body)}));
 // Offline recovery only; do not mutate or pretend to acknowledge the live slim job.
 await f.acknowledge(parent,child);
 const delivery=await f.getResult(parent,child,'deliver',{});
 const report='> 此文件为已通过裁决的离线恢复输出；没有调用新模型或重新裁决。原主会话的slim领取状态未改动。\n\n'+delivery.report_markdown;
 await fs.writeFile(path.join(out,'本次已存裁决恢复报告.md'),report);
 assert.equal(await fs.readFile(statePath,'utf8'),stateRaw);assert.equal(await fs.readFile(originalRef.path,'utf8'),originalRaw);
 await fs.writeFile(path.join(out,'real-recovery.json'),JSON.stringify({parent,child,original_result_ref:originalRef,original_result_unchanged:true,original_state_unchanged:true,replayed_result_equal:true,report_sha256:hash(report),live_slim_acknowledged:false,new_model_calls:0},null,2));
 console.log(JSON.stringify({recovered:true,originalUnchanged:true,newModelCalls:0,reportChars:report.length}));
}finally{assert.equal(path.dirname(path.resolve(temp)),path.resolve(os.tmpdir()));assert.ok(path.basename(temp).startsWith('liuren-real-recovery-'));await fs.rm(temp,{recursive:true,force:true});}
