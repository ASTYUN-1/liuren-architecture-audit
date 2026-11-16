// Synthetic in-memory probes only; no agent calls or active file changes.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {validateInput,validateOutput,parseTaskOutput} from '../../tools/liuren-adjudication-contract.mjs';
const here=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(here,'../..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8').replace(/^\uFEFF/,''));
const summary=read('output/liuren-screen-repair-investigation-20261106/summary.json');
const packet=read(summary.packetFiles[1].path).packet;
const calls=read('output/liuren-screen-repair-investigation-20261106/adjudications.json');
const result=typeof calls[1].result==='string'?parseTaskOutput(calls[1].result):calls[1].result;
const checks=[];
function probe(name,fn){try{fn();checks.push({name,accepted:true});}catch(e){checks.push({name,accepted:false,error:e.message});}}
probe('unmodified input',()=>validateInput(packet));
probe('unmodified second adjudication',()=>validateOutput(result,packet));
const quote=structuredClone(packet);
quote.method_materials[0].quote='[SYNTHETIC CONTRACT PROBE] This sentence is not a quote from the indicated source.';
probe('source path exists but quote is synthetic',()=>validateInput(quote));
const observation=structuredClone(packet);
observation.observations[0].statement='[SYNTHETIC CONTRACT PROBE] 初传丑的直接阴神为寅。';
observation.observations[0].verification='chart_checked';
probe('incorrect coordinate observation labeled chart_checked',()=>validateInput(observation));
const wrong=structuredClone(result);
wrong.entity_checks[0].site_yin='[SYNTHETIC CONTRACT PROBE] 阴神为错误坐标；仅测试字符串是否接受。';
probe('output site_yin is arbitrary nonempty text',()=>validateOutput(wrong,packet));
const output={schema:'liuren-contract-semantic-gap-probe-v1',checks,
  limits:['Accepting a synthetic bad field proves only a contract validation gap, not that a live model would adopt it.',
          'All mutations stayed in memory. No packet, source, runtime or config was changed.']};
fs.writeFileSync(path.join(here,'contract-probe.json'),JSON.stringify(output,null,2)+'\n');
console.log(JSON.stringify(output,null,2));
