// Synthetic deterministic examples only. No model, network or native agent calls.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const packageRoot=path.resolve(fileURLToPath(new URL('../',import.meta.url)));
const root=path.resolve(process.argv[2]||path.join(packageRoot,'project'));
const out=path.join(packageRoot,'examples');await fs.mkdir(out,{recursive:true});
const {runResolvedChart}=await import(pathToFileURL(path.join(root,'tools/liuren-resolved-chart.mjs')));
const {exportAIChart}=await import(pathToFileURL(path.join(root,'tools/liuren-chart-view.mjs')));
const {execute}=await import(pathToFileURL(path.join(root,'tools/liuren-codex.mjs')));
const write=(name,value)=>fs.writeFile(path.join(out,name),JSON.stringify(value,null,2)+'\n','utf8');
const input={datetime:'2026-11-16T12:00',timezone:'Asia/Shanghai',label:'synthetic-architecture-audit',declared_life:[]};
await write('synthetic-chart-input.json',input);
const chart=await runResolvedChart(input);
await write('normalized-chart-result.json',chart);
await fs.copyFile(chart.archive.path,path.join(out,'original-engine-archive.json'));
const ai=await exportAIChart(chart);await write('ai-chart-view.json',ai);
const lookup=await execute({action:'compute',request:{action:'lookup',archive:chart.archive,lookup:{subject:'申',place:'午',reference:'庚'}}});
await write('lookup-receipt.json',lookup);
const strength=await execute({action:'compute',request:{action:'strength',archive:chart.archive,strength:{mode:'single_palace',season_profile:'quarter-earth',season_basis:'合成接口验收，不作专业采用',review:true,actors:[{id:'T:子',role:'合成指定对象',basis:'只验证工具输入输出'}]}}});
await write('strength-receipt.json',strength);
const fields=[];
function visit(value,prefix){
 const type=value===null?'null':Array.isArray(value)?'array':typeof value;
 fields.push({path:prefix,type,...(Array.isArray(value)?{length:value.length}:{})});
 if(Array.isArray(value)){if(value.length)visit(value[0],prefix+'[]');}
 else if(value&&typeof value==='object')for(const [key,v] of Object.entries(value))visit(v,prefix?prefix+'.'+key:key);
}
visit(JSON.parse(await fs.readFile(chart.archive.path,'utf8')),'raw');visit(chart,'normalized');visit(ai,'ai');
await write('field-dictionary.json',fields);
// Capture an existing local synthetic transport fixture from the successful test.
// Its report explicitly makes no prediction and bind uses a fixture ID.
const runs=path.join(root,'output/codex-liuren');let chosen;
for(const d of await fs.readdir(runs)){const p=path.join(runs,d);try{const text=await fs.readFile(path.join(p,'report.md'),'utf8');if(text.includes('工程传输验收'))chosen=p;}catch{}}
if(chosen){await fs.cp(chosen,path.join(out,'synthetic-handoff'),{recursive:true});}
await write('example-provenance.json',{scope:'synthetic deterministic and fixture report transport only',input,model_calls:0,native_agent_calls:0,real_prediction:false,chart_valid:chart.ok,source_release:JSON.parse(await fs.readFile(path.join(root,'.opencode/liuren-active.json'),'utf8')).release,field_paths:fields.length,captured_fixture_report:Boolean(chosen)});
console.log(JSON.stringify({ok:chart.ok,field_paths:fields.length,captured_fixture_report:Boolean(chosen)}));
