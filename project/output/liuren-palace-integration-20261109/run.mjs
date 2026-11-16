import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {loadStrengthSource} from '../../tools/liuren-strength.mjs';
import {chartView,formatChart} from '../../tools/liuren-chart-view.mjs';
import {compute} from '../../tools/liuren-deterministic-io.mjs';
import {status} from '../../tools/liuren-codex.mjs';
const ROOT=fileURLToPath(new URL('../../',import.meta.url)),OUT=path.dirname(fileURLToPath(import.meta.url));
const read=async p=>JSON.parse((await fs.readFile(p,'utf8')).replace(/^\uFEFF/,''));
const sha=b=>createHash('sha256').update(b).digest('hex');
const write=async(p,b)=>{await fs.mkdir(path.dirname(p),{recursive:true});await fs.writeFile(p,typeof b==='string'?b:JSON.stringify(b,null,2)+'\n');};
const earlier=await read(path.join(ROOT,'output/liuren-energy-prototype-20261108/fixed-v02/本课固定参数计算.json'));
const cases=[['应聘盘',earlier.chart_archive],['寅午戌盘',path.join(ROOT,'output/liuren-energy-yin-20261106-1443/chart-result.json')]];
const reports=[];
for(const [name,file]of cases){
 const before=sha(await fs.readFile(file)),s=await loadStrengthSource(file),v=chartView(s.facts,{shensha:s.shensha,conventions:s.conventions});
 await write(path.join(OUT,name,'AI盘.json'),formatChart(v));
 if(name==='寅午戌盘'){
  const request={action:'strength',strength:{mode:'selected_relations',season_profile:'quarter-earth',season_basis:'固定沿季土条件表示范补算，不依结果择表',
   actors:[{id:'T:酉',role:'演示假设施助金神',basis:'用户所举金生子水的接口假设，不代表本课真实取用'},{id:'T:子',role:'演示目标类神',basis:'用户假设子水为类神'}],
   links:[{source:'T:酉',target:'T:子',basis:'仅演示：假设取用后已确认酉对子的生扶通路，不据全盘五行自动添加'}]}};
  const result=compute(request,s.facts);
  await write(path.join(OUT,name,'取用后补算请求.json'),request);await write(path.join(OUT,name,'取用后补算结果.json'),result);
  reports.push({name,example:result.actors});
 }
 if(before!==sha(await fs.readFile(file)))throw Error('original archive changed');
 reports.push({name,source:file,source_sha256:before,chart_file:path.join(OUT,name,'AI盘.json'),bytes:Buffer.byteLength(formatChart(v)),
  scores:v.heaven_earth.filter(n=>['申','子','亥','丑','寅','午','戌'].includes(n.tian)).map(n=>({tian:n.tian,status:n.status,score:n.state.strength_index,level:n.state.strength_level}))});
}
await write(path.join(OUT,'复算与完整性.json'),{health:await status(),reports,paidModelCalls:0,predictionValidation:false});
process.stdout.write(JSON.stringify(reports,null,2)+'\n');
