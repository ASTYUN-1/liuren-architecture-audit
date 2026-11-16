// Local replay of observed inputs against preserved 16-version materials and current implementation.
// No model calls, no semantic changes to the case, and no files in the live request/session directories.
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import {createHash} from 'node:crypto';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {registerHooks} from 'node:module';
import {savePacket,loadPacket,resolveChartArchive} from '../../tools/liuren-adjudication-files.mjs';
const out=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(out,'../..');
const hash=v=>createHash('sha256').update(typeof v==='string'?v:JSON.stringify(v)).digest('hex');
const before=JSON.parse(await fs.readFile(path.join(out,'before/.opencode/liuren-active.json'),'utf8'));
const calls=JSON.parse(await fs.readFile(path.join(out,'packet-calls.json'),'utf8')).calls;
const tmp=await fs.mkdtemp(path.join(os.tmpdir(),'liuren-observed-replay-'));
const records=[];
registerHooks({resolve(specifier,context,next){if(specifier==='@opencode-ai/plugin')return next(pathToFileURL(path.join(root,'.opencode/node_modules/@opencode-ai/plugin/dist/index.js')).href,context);return next(specifier,context);}});
const {default:plugin}=await import('../../.opencode/plugins/liuren-adjudication.ts');
const messages=JSON.parse(await fs.readFile(path.join(out,'replay-session.json'),'utf8'));
try{
 await fs.mkdir(path.join(tmp,'.opencode'),{recursive:true});
 await fs.writeFile(path.join(tmp,'.opencode/liuren-active.json'),JSON.stringify(before));
 for(const rel of [before.runtime,'tools/liuren-direct/legacy-engine-manifest.json','排盘工具魔改/js/lunar.js']){
  const dest=path.join(tmp,rel);await fs.mkdir(path.dirname(dest),{recursive:true});await fs.cp(path.join(root,rel),dest,{recursive:true});
 }
 const indices=[0,1,2,3,9,14,15,16];
 const books=new Set(indices.flatMap(i=>calls[i].state.input.packet.method_materials.map(m=>m.source_path)).filter(p=>p.startsWith('书籍库/')||p.startsWith('books/')));
 for(const rel of books){const dest=path.join(tmp,rel);await fs.mkdir(path.dirname(dest),{recursive:true});await fs.copyFile(path.join(root,rel),dest);}
 const hooks=await plugin({directory:tmp,client:{session:{messages:async()=>({data:messages})}}});
 for(const index of indices){
  const entry=calls[index],original=entry.state.input.packet;
  try{
   const resolved=await resolveChartArchive(root,original);
   const replayInput=structuredClone(original);
   if(original.chart.archive){
    const dest=path.join(tmp,'排盘存档/六壬',path.basename(original.chart.archive.path));
    await fs.mkdir(path.dirname(dest),{recursive:true});await fs.copyFile(original.chart.archive.path,dest);
    replayInput.chart.archive.path=dest; // Exact same archive bytes/hash, isolated destination only.
   }
   const parsed=hooks.tool.liuren_adjudication_packet.args.packet.parse(replayInput);
   const saved=JSON.parse(await hooks.tool.liuren_adjudication_packet.execute({packet:parsed},{agent:'liuren',sessionID:'observed-replay-parent'})),loaded=await loadPacket(tmp,saved),p=loaded.envelope.packet;
   for(const key of ['request_id','facts','observations','focus_issues','unknowns','questions'])if(JSON.stringify(original[key])!==JSON.stringify(p[key]))throw Error('original field altered: '+key);
   if(hash(resolved.chart.facts)!==hash(p.chart.facts))throw Error('chart facts altered');
   for(const material of original.method_materials)if(!p.method_materials.some(m=>m.id===material.id&&m.source_path===material.source_path))throw Error('missing material '+material.id);
   records.push({index,part_id:entry.part_id,request_id:p.request_id,ok:true,characters:JSON.stringify(p).length,bytes:Buffer.byteLength(loaded.raw),pages:loaded.pages,
    originalInputSha256:hash(original),originalFactsPreserved:true,chartFactsPreserved:true,originalObservationsPreserved:true,originalFocusIssuesPreserved:true,originalMethodsRetained:original.method_materials.length,
    totalMethods:p.method_materials.length,calculations:p.deterministic.calculations.length,nativeSchemaAndToolExecuted:true,methodCoveragePassed:true,originalQuestionBound:!!p.input_origin?.source_text});
  }catch(error){records.push({index,ok:false,error:String(error)});}
 }
}finally{
 if(path.dirname(path.resolve(tmp))!==path.resolve(os.tmpdir())||!path.basename(tmp).startsWith('liuren-observed-replay-'))throw Error('unexpected temporary path');
 await fs.rm(tmp,{recursive:true,force:true});
}
const result={schema:'liuren-observed-packet-replay-v1',sourceRelease:before.release,modelCalled:false,filesWrittenToLiveRequests:false,
 implementationSha256:Object.fromEntries(await Promise.all(['tools/liuren-adjudication-contract.mjs','tools/liuren-adjudication-files.mjs','tools/liuren-deterministic-io.mjs','.opencode/plugins/liuren-adjudication.ts'].map(async rel=>[rel,hash(await fs.readFile(path.join(root,rel),'utf8'))]))),records};
await fs.writeFile(path.join(out,'observed-replay.json'),JSON.stringify(result,null,2)+'\n');
process.stdout.write(JSON.stringify({cases:records.length,passed:records.filter(r=>r.ok).length,errors:records.filter(r=>!r.ok),modelCalled:false}));
if(records.some(r=>!r.ok))process.exitCode=1;
