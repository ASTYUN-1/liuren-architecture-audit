// Read-only original session -> isolated diagnostic parent; never dispatch.
import {spawnSync} from 'node:child_process';
import {readFile,writeFile} from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {registerHooks} from 'node:module';
const root=process.cwd();
registerHooks({resolve(specifier,context,next){if(specifier==='@opencode-ai/plugin')return next(pathToFileURL(path.join(root,'.opencode/node_modules/@opencode-ai/plugin/dist/index.js')).href,context);return next(specifier,context);}});
const query=`import sqlite3,pathlib,json
c=sqlite3.connect((pathlib.Path.home()/'.local/share/opencode/opencode.db').as_uri()+'?mode=ro',uri=True)
sid='ses_e4f99151dfferLH336YCY2pe08'
p=json.loads(c.execute('select data from part where id=?',('prt_1b06d5e06001AGoQdYmS7xjCY0',)).fetchone()[0])['state']['input']['packet']
messages=[]
for mid,data in c.execute('select id,data from message where session_id=? order by time_created',(sid,)):
 messages.append({'info':json.loads(data),'parts':[json.loads(x[0]) for x in c.execute('select data from part where message_id=? order by time_created',(mid,))]})
print(json.dumps({'packet':p,'messages':messages},ensure_ascii=False))`;
const proc=spawnSync('python',['-X','utf8','-c',query],{encoding:'utf8',maxBuffer:20*1024*1024,windowsHide:true});
if(proc.status!==0)throw Error(proc.stderr);
const original=JSON.parse(proc.stdout),{default:plugin}=await import(pathToFileURL(path.join(root,'.opencode/plugins/liuren-adjudication.ts')).href);
const hooks=await plugin({directory:root,client:{session:{messages:async()=>({data:original.messages})}}});
const context={agent:'liuren',sessionID:'audit_tool_usage_latest_20261106'},results=[];
try{await hooks.tool.liuren_adjudication_packet.execute({packet:original.packet},context);throw Error('duplicate unexpectedly accepted');}catch(e){
 if(!e.message.startsWith('LIUREN_PACKET_ARGUMENTS:'))throw e;
 const details=JSON.parse(e.message.split('LIUREN_PACKET_ARGUMENTS: ')[1]);
 results.push({case:'original duplicate IDs',rejected:true,issues:details.issues});
}
const corrected=structuredClone(original.packet);
for(const issue of corrected.focus_issues)issue.id='I_'+issue.id;
const saved=JSON.parse(await hooks.tool.liuren_adjudication_packet.execute({packet:corrected},context));
const actual=JSON.parse(await readFile(saved.file_path,'utf8')).packet;
if(JSON.stringify(actual.observations)!==JSON.stringify(original.packet.observations))throw Error('observations changed');
results.push({case:'only namespace correction',accepted:true,observationCount:actual.observations.length,shenshaObservations:actual.observations.filter(o=>o.kind==='shensha').length,observationsByteEquivalent:true,questionsByteEquivalent:JSON.stringify(actual.questions)===JSON.stringify(corrected.questions),requestSha256:saved.sha256,nextCall:saved.next_call.tool,dispatched:false});
await writeFile(path.join(root,'output/liuren-workflow-review-20261106/latest-replay.json'),JSON.stringify({baseline:'20261106-handoff-chain-20',originalSessionUnchanged:true,results},null,2));
console.log(JSON.stringify(results.map(({case:name,rejected,accepted,shenshaObservations,observationsByteEquivalent})=>({case:name,rejected,accepted,shenshaObservations,observationsByteEquivalent}))));
