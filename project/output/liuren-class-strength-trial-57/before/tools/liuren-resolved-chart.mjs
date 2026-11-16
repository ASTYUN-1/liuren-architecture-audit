// User-facing chart route: original engine once, then independent fixed policy.
import fs from 'node:fs/promises';
import { runChart, isEntryPoint } from './liuren-direct.mjs';
import { runChartWithShensha } from './liuren-shensha.mjs';
import { enrichBasicStates } from './liuren-basic-states.mjs';
import { exportAIChart } from './liuren-chart-view.mjs';

export async function runResolvedChart(request, options={}) {
  const result=await runChartWithShensha(()=>runChart(request,options),
    {persist:options.persist!==false, policyRoot:options.policyRoot,sidecar:false});
  return enrichBasicStates(result,{persist:false});
}

if (isEntryPoint(process.argv[1],import.meta.url)) {
  try {
    const args=process.argv.slice(2);let request;
    if(args.length===1 && args[0]==='--now') request={mode:'now'};
    else if(args.length===2 && args[0]==='--datetime') request={datetime:args[1]};
    else if(args.length===2 && args[0]==='--input') request=JSON.parse((await fs.readFile(args[1],'utf8')).replace(/^\uFEFF/,''));
    else if(args.length===1 && args[0]==='--stdin') {
      let input='';process.stdin.setEncoding('utf8');for await(const part of process.stdin)input+=part;
      request=JSON.parse(input.replace(/^\uFEFF/,''));
    } else throw new Error('使用 --datetime 时间、--now、--input JSON 或 --stdin；原引擎只运行一次');
    const result=await exportAIChart(await runResolvedChart(request));process.stdout.write(JSON.stringify(result)+'\n');
    if(!result.ok)process.exitCode=2;
  } catch(error){process.stderr.write('LIUREN_RESOLVED_CHART_ERROR: '+error.message+'\n');process.exitCode=1;}
}
