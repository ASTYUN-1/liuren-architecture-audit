// Inspect resolved local configuration without saving providers, credentials, or raw output.
import {spawnSync} from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
const out=import.meta.dirname,root=path.resolve(out,'../..');
const result=spawnSync('C:\\Users\\QLMa_\\scoop\\apps\\opencode\\current\\opencode.exe',['debug','config'],{cwd:root,encoding:'utf8',windowsHide:true,timeout:45000,maxBuffer:3*1024*1024});
const summary={exitCode:result.status,modelCalls:0,rawConfigurationSaved:false,websiteDeployment:false};
if(result.error){summary.errorCode=result.error.code;}
if(result.status!==0){
 summary.errorLines=((result.stderr||'')+'\n'+(result.stdout||'')).replace(/\u001b\[[0-9;]*m/g,'').split(/\r?\n/).filter(v=>/error|invalid|unknown|unrecognized|failed|ENOENT|permission|denied|not found/i.test(v)).map(v=>v.replace(/(?:sk-|Bearer\s+)\S+/gi,'[redacted]')).slice(0,8).join('\n').slice(0,2000);
}
if(result.status===0){
 const config=JSON.parse(result.stdout);
 assert.equal(config.default_agent,'liuren');
 assert.ok(config.agent.liuren.prompt.includes('8项共用方法'));
 assert.ok(!config.agent.liuren.prompt.includes('14必查'));
 assert.equal(config.agent.liuren.permission.liuren_chart,'allow');
 summary.resolvedPrimary='liuren';summary.slimPromptLoaded=true;
 summary.instructions=config.instructions?.filter(v=>v.includes('本机'));
}
fs.writeFileSync(path.join(out,'host-config-check.json'),JSON.stringify(summary,null,2)+'\n');
console.log(JSON.stringify(summary));
process.exitCode=result.status===0?0:1;
