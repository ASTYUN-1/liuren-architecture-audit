import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {registerHooks} from 'node:module';
const root=fileURLToPath(new URL('../../',import.meta.url));
registerHooks({resolve(specifier,context,next){if(specifier==='@opencode-ai/plugin')return next(pathToFileURL(path.join(root,'.opencode/node_modules/@opencode-ai/plugin/dist/index.js')).href,context);return next(specifier,context);}});
const {default:plugin}=await import('../../.opencode/plugins/liuren-adjudication.ts');
const hooks=await plugin({directory:root,client:{session:{messages:async()=>({data:[]})}}});
const ctx={agent:'liuren',sessionID:'trial61_existing_chart_interface_only'};
const a=JSON.parse(await fs.readFile(path.join(root,'output/opencode-trial60-newfive-20261115-07-deepseek/execution-audit.json'),'utf8'));
const cases=[];
for(const c of a.cases){
 const archive={path:c.archives[0].path,sha256:c.archives[0].sha256};
 const f=JSON.parse(await hooks.tool.liuren_compute.execute({action:'chart',archive},ctx));
 const i=f.trial_chart_basis.initial_transmission;
 cases.push({alias:c.alias,title:c.title,pillars:f.pillars,initial:i,season_profile:f.strength_model.season_profile,
  has_alternative_season_keys:JSON.stringify(f).includes('"四季":'),model_called:false,event_verdict:null});
}
const value={release:'20261115-trial-decision-61',scope:'既有盘的真实OpenCode工具接口核验；没有重新调用模型，不是五例预测复测',cases};
await fs.writeFile(new URL('./五例初传接口核验.json',import.meta.url),JSON.stringify(value,null,2)+'\n');
for(const c of cases)console.log(JSON.stringify({alias:c.alias,initial:c.initial.branch,qi:c.initial.branch_state.month_qi,score:c.initial.branch_state.strength_index,has_alternative_season_keys:c.has_alternative_season_keys}));
