// Explicit research entry. Default chart / adjudication routes remain unchanged.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
import {computeStrength,compactStrength} from './liuren-strength-engine.mjs';
import {chartView,formatChart} from './liuren-chart-view.mjs';
import {shenshaForChart} from './liuren-shensha.mjs';
export {computeStrength,compactStrength};
export function analyzeStrengthChart(c,context,{shensha,conventions,profile}={}){
 const calculation=computeStrength(c,context,{shensha,profile});
 if(!shensha?.items)throw Error('需要原盘当前采用神煞，不能以空表冒充已采用全表');
 const chart=chartView(c,{shensha,conventions,researchStrength:calculation});
 return {chart,calculation,summary:compactStrength(calculation)};
}
async function readJson(file){return JSON.parse((await fs.readFile(file,'utf8')).replace(/^\uFEFF/,''));}
export async function loadStrengthSource(file){
 const record=await readJson(file),facts=record._direct?.facts??record.facts??(record.schema==='liuren-chart-facts-v1'?record:null);
 if(!facts)throw Error('须提供原始可信排盘归档，精简AI盘不能逆向还原计算输入');
 let shensha=record._direct?.shensha_resolution??record.shensha_resolution;
 if(!shensha?.items)shensha=await shenshaForChart(record);
 return {facts,shensha,conventions:record._direct?.conventions??record.conventions};
}
async function saveNew(file,body){
 await fs.mkdir(path.dirname(path.resolve(file)),{recursive:true});
 try{await fs.writeFile(file,body,{encoding:'utf8',flag:'wx'});}
 catch(e){if(e.code!=='EEXIST'||await fs.readFile(file,'utf8')!==body)throw Error('拒绝覆盖不同内容：'+file);}
}
async function main(){
 const args=process.argv.slice(2),opts={};
 for(let i=0;i<args.length;i+=2){
  const key=args[i];if(!['--input','--context','--out','--audit','--summary'].includes(key)||!args[i+1])throw Error('参数：--input 原盘.json --context 计算条件.json --out AI盘.json [--audit 审计.json] [--summary 摘要.json]');
  if(opts[key])throw Error('重复参数 '+key);opts[key]=args[i+1];
 }
 if(!opts['--input']||!opts['--context']||!opts['--out'])throw Error('必须提供--input、--context、--out');
 const paths=Object.values(opts).map(x=>path.resolve(x).toLowerCase());
 if(new Set(paths).size!==paths.length)throw Error('输入、条件及各输出路径必须不同');
 const source=await loadStrengthSource(opts['--input']),context=await readJson(opts['--context']);
 const result=analyzeStrengthChart(source.facts,context,source);
 await saveNew(opts['--out'],formatChart(result.chart));
 if(opts['--audit'])await saveNew(opts['--audit'],JSON.stringify(result.calculation,null,2)+'\n');
 if(opts['--summary'])await saveNew(opts['--summary'],JSON.stringify(result.summary,null,2)+'\n');
 process.stdout.write(JSON.stringify({ok:true,model:result.calculation.model,chart_file:path.resolve(opts['--out']),
  strength_scope_complete:result.calculation.coverage.strength_scope_complete,
  action_complete:result.calculation.coverage.complete_for_declared_actions,
  pending:result.calculation.coverage.pending.length})+'\n');
}
if(process.argv[1]&&pathToFileURL(path.resolve(process.argv[1])).href===import.meta.url)main().catch(e=>{process.stderr.write(e.message+'\n');process.exitCode=1;});
