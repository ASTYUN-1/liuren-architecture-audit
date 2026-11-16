// Attach derived lookup states without changing native facts or historical exports.
import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {buildFacts} from './liuren-deterministic.mjs';
import {isEntryPoint} from './liuren-direct.mjs';
const hash=x=>createHash('sha256').update(x).digest('hex');
export async function enrichBasicStates(result,{persist=true}={}){
 if(!result?.facts||!result.ok||result.validation?.ok!==true)return {...result,basic_state_status:'chart_unusable'};
 const basic_states=buildFacts(result.facts).basic_states;
 let basic_state_archive=null;
 if(persist&&result.archive?.path){
  const raw=await fs.readFile(result.archive.path);
  if(hash(raw)!==result.archive.sha256)throw Error('基础状态保存失败：原盘归档hash变化');
  if(JSON.stringify(JSON.parse(raw)._direct?.facts)!==JSON.stringify(result.facts))throw Error('基础状态保存失败：原盘facts不一致');
  const bytes=JSON.stringify({schema:'liuren-basic-state-sidecar-v1',source_archive:result.archive,basic_states},null,2)+'\n';
  const digest=hash(bytes),target=result.archive.path.replace(/\.json$/i,'')+'.basic-states-'+digest.slice(0,16)+'.json';
  try{await fs.writeFile(target,bytes,{encoding:'utf8',flag:'wx'});}
  catch(error){if(error.code!=='EEXIST'||await fs.readFile(target,'utf8')!==bytes)throw error;}
  basic_state_archive={path:target,sha256:digest};
 }
 return {...result,basic_state_status:'resolved',basic_states,basic_state_archive,
  field_notes:{...result.field_notes,basic_states:'确定性基础状态及具名取表；无综合分、无吉凶；阴神取同名地盘上神；将与乘支状态分开；季土取表差异显式列出。'}};
}
if(isEntryPoint(process.argv[1],import.meta.url)){
 try{
  if(process.argv.length!==4||process.argv[2]!=='--chart')throw Error('使用 --chart 已存完整盘.json；不重起课');
  const raw=await fs.readFile(process.argv[3]),r=JSON.parse(raw.toString('utf8').replace(/^\uFEFF/,''));
  const facts=r._direct?.facts??r.facts??(r.schema==='liuren-chart-facts-v1'?r:null);
  if(!facts)throw Error('缺完整程序facts');
  process.stdout.write(JSON.stringify(buildFacts(facts).basic_states)+'\n');
 }catch(error){process.stderr.write('LIUREN_BASIC_STATES_ERROR: '+error.message+'\n');process.exitCode=1;}
}
