import fs from 'node:fs/promises';
import path from 'node:path';
import {exportAIChart,formatChart} from '../../tools/liuren-chart-view.mjs';
import {makeReadingCore} from '../../tools/liuren-core-handoff.mjs';
import {createHash} from 'node:crypto';
const root=process.cwd(),out=path.join(root,'output/liuren-day-only-20261108');
const source=path.join(root,'排盘存档/六壬/六壬-20261108-214237-基础状态接入验收-41b34a16-3c4e-400f-a551-35c73cd652da.corrected-7d8f4da2258d400a.json');
const raw=await fs.readFile(source),record=JSON.parse(raw),meta=record._direct;
const hash=v=>createHash('sha256').update(v).digest('hex');
const result=await exportAIChart({ok:true,...meta,archive:{path:source,sha256:hash(raw),raw_sha256:meta.raw_sha256}});
await fs.writeFile(path.join(out,'本课正式盘.json'),formatChart(result.facts));
await fs.writeFile(path.join(out,'工具返回.json'),JSON.stringify(result,null,2)+'\n');
const packetFile=path.join(root,'output/liuren-adjudication-requests/codex-transport-1794145416335-2925f8dc-d03a-4ac4-9fc5-f1d13392d014.json');
const old=JSON.parse(await fs.readFile(packetFile,'utf8'));
const full=JSON.parse(await fs.readFile(path.join(path.dirname(packetFile),old.packet_archive.file),'utf8'));
const core=await makeReadingCore(root,full.packet);
await fs.writeFile(path.join(out,'同材料子智能体核心.json'),JSON.stringify(JSON.parse(core.core.content),null,2)+'\n');
const size=x=>{const s=typeof x==='string'?x:JSON.stringify(x);return {characters:s.length,utf8_bytes:Buffer.byteLength(s)}};
const prior=JSON.parse(await fs.readFile('output/liuren-json-size-audit-20261108/同盘新增量对照.json','utf8'));
const metrics={measurement:'characters and UTF8 bytes; not measured model tokens',source_unchanged:hash(await fs.readFile(source))===hash(raw),
 tool:{before:prior.same_chart_tool.current,after:size(result)},core:{before:size(old.reading_core.content),after:size(core.core.content)},
 formal_chart:size(result.facts),chart_file:result.chart_file,numeric_profile:result.facts.strength_model};
metrics.tool.reduction=1-metrics.tool.after.characters/metrics.tool.before.characters;
metrics.core.reduction=1-metrics.core.after.characters/metrics.core.before.characters;
await fs.writeFile(path.join(out,'验收数据.json'),JSON.stringify(metrics,null,2)+'\n');
console.log(JSON.stringify(metrics,null,2));
