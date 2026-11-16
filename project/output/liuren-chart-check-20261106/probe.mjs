import fs from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {performance} from 'node:perf_hooks';
import chartTool from '../../.opencode/tools/liuren_chart.ts';
import {runResolvedChart} from '../../tools/liuren-resolved-chart.mjs';
const dir=new URL('./',import.meta.url);
const requests=[
 {datetime:'2026-10-30T21:16',declared_life:[{birth_pillar:'壬午',sex:'男'}],label:'engine-check'},
 {datetime:'2026-10-30T21:16',settings:{yuejiang:'日躔换将'}},
 {mode:'manual-pillars',pillars:{year:'丙午',month_branch:'戌',day:'丁丑',hour_branch:'亥'},month_general:'辰',reference_datetime:'2026-10-30T21:16'}
];
const samples=[];
for(const [i,request] of requests.entries()){
 const start=performance.now();
 const result=i===0?JSON.parse(await chartTool.execute(request,{sessionID:'local-engine-check',abort:new AbortController().signal})):await runResolvedChart(request,{persist:false});
 await fs.writeFile(new URL(`engine-result-${i+1}.json`,dir),JSON.stringify(result,null,2));
 samples.push({route:i===0?'native liuren_chart':'runResolvedChart persist=false',request,elapsed_ms:Math.round(performance.now()-start),ok:result.ok,validation:result.validation,release:result.shensha_policy?.release??result.shensha_resolution?.release,month_general:result.facts?.month_general,pillars:result.facts?.pillars,chart_types:result.facts?.chart_types,lessons:result.facts?.lessons,transmissions:result.facts?.transmissions,counts:{palaces:result.facts?.heaven_earth.length,lessons:result.facts?.lessons.length,transmissions:result.facts?.transmissions.length},program_facts_present:!!result.program_facts,archive:result.archive});
 if(result.archive?.path){const raw=await fs.readFile(result.archive.path);if(createHash('sha256').update(raw).digest('hex')!==result.archive.sha256)throw Error('archive hash differs');}
 if(!result.ok||!result.validation.ok)throw Error('chart invalid');
}
await fs.writeFile(new URL('engine-check.json',dir),JSON.stringify({active:JSON.parse(await fs.readFile(new URL('../../.opencode/liuren-active.json',import.meta.url),'utf8')).release,externalModelCalled:false,samples},null,2));
console.log(JSON.stringify(samples.map(s=>({route:s.route,elapsed_ms:s.elapsed_ms,ok:s.ok,validation:s.validation.ok,month_general:s.month_general,transmissions:s.transmissions,counts:s.counts,program_facts_present:s.program_facts_present})),null,2));
