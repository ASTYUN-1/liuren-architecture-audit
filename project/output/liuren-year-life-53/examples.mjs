// Synthetic input examples on one program chart; no prediction or known outcome.
import fs from 'node:fs/promises';
import {runResolvedChart} from '../../tools/liuren-resolved-chart.mjs';
import {resolveLife} from '../../tools/liuren-year-life.mjs';
const {facts}=await runResolvedChart({datetime:'2026-08-04T14:32'},{persist:false});
const inputs=[{birth_year:'05',sex:'男'},{birth_year:'99',sex:'女'},{birth_pillar:'甲子',sex:'男'},{birth_pillar:'申',sex:'男'},{birth_pillar:'申',sex:'女'},{birth_year:2005},{birth_pillar:'申',xingnian:'戌',sex:'男'}];
const result={scope:'合成输入演示，仅核输入采用、循环计算与盘面坐标，非预测验收',pillars:facts.pillars,examples:inputs.map(input=>resolveLife(input,facts))};
await fs.writeFile(new URL('./年命输入回执示例.json',import.meta.url),JSON.stringify(result,null,2)+'\n');
console.log(JSON.stringify({examples:inputs.length,year_pillar:facts.pillars[0]}));
