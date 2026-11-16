import {spawnSync} from 'node:child_process';
import fs from 'node:fs';import path from 'node:path';
const out=import.meta.dirname,root=path.resolve(out,'../..');
const run=spawnSync('C:/Users/QLMa_/scoop/apps/opencode/current/opencode.exe',['debug','config'],{cwd:root,encoding:'utf8',windowsHide:true,timeout:45000,maxBuffer:3e6});
if(run.status!==0)throw new Error('Resolved configuration check failed: '+run.status);
const config=JSON.parse(run.stdout);
const summary={plugin:config.plugin,default_agent:config.default_agent,skillPaths:config.skills?.paths,primaryPromptSlim:config.agent.liuren.prompt.includes('8项共用方法')};
fs.writeFileSync(path.join(out,'resolved-registration.json'),JSON.stringify(summary,null,2)+'\n');
console.log(JSON.stringify(summary));
