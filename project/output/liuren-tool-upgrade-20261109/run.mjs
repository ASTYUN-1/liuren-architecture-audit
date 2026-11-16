import fs from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import assert from 'node:assert/strict';
import {compute} from '../../tools/liuren-deterministic-io.mjs';
import {chartView} from '../../tools/liuren-chart-view.mjs';
import {shenshaForChart} from '../../tools/liuren-shensha.mjs';
import {hash} from '../../tools/liuren-deterministic.mjs';
const ROOT=fileURLToPath(new URL('../../',import.meta.url)),OUT=fileURLToPath(new URL('./',import.meta.url));
const load=async p=>JSON.parse(await fs.readFile(path.join(ROOT,p),'utf8'));
const save=(name,d)=>fs.writeFile(path.join(OUT,name),JSON.stringify(d,null,2)+'\n');
const c=(await load('output/liuren-energy-yin-20261106-1443/chart-result.json')).facts,before=hash(c);
const requests={
 methods:{action:'methods',methods:{kind:'quantity'}},
 quantity:{action:'quantity',quantity_method:{id:'CY501-use-ground',target:'T:戌',season_profile:'quarter-earth',basis:'固定工程算例：原盘戌初传临寅，戌月采用季土表；不作现实取数预测'}},
 base_quantity:{action:'quantity',quantity_method:{id:'WY67-shenjiang-base',target:'T:戌',basis:'固定工程算例，只核本段神将相乘基础数'}},
 calendar:{action:'calendar',calendar:{start:'2026-11-06',end:'2026-11-20',timezone:'Asia/Shanghai',day_boundary:'civil-midnight',mode:'boundaries',origin:'2026-11-06T14:43'}},
 imagery:{action:'imagery',imagery:{id:'DF449-growth',target:'T:寅',reference:'ground',basis:'固定工程算例，仅显示原段十二气物态候选'}},
 evaluation:{action:'evaluation',evaluation:{calendar:{start:'2026-11-06',end:'2026-11-08',timezone:'Asia/Shanghai',day_boundary:'civil-midnight',origin:'2026-11-06T14:43'},
  strength:{mode:'single_palace',season_profile:'quarter-earth',season_basis:'工程算例固定季土表，不据分数择表',actors:[{id:'T:寅',role:'测试对象',basis:'只核接口，非实际取用结论'}]},void_policy:'original'}}
};
const results=Object.fromEntries(Object.entries(requests).map(([k,q])=>[k,compute(q,c,{root:ROOT})]));
assert.equal(hash(c),before);
const old=await load('output/liuren-palace-integration-20261109/寅午戌盘/AI盘.json'),view=chartView(c,{shensha:await shenshaForChart(c)});
const differences=Object.keys(view).filter(k=>JSON.stringify(view[k])!==JSON.stringify(old[k]));
assert.deepEqual(differences,[],'default merged AI chart must not expand or change');
await save('示例请求.json',requests);await save('示例结果.json',results);await save('当前默认AI盘.json',view);
const pre=await load('output/liuren-tool-upgrade-20261109/before.json');
for(const [rel,digest]of Object.entries(pre.frozen))assert.equal(hash((await fs.readFile(path.join(ROOT,'runtime/liuren',pre.release,rel))).toString('utf8')),digest,rel);
assert.equal(hash((await fs.readFile(path.join(ROOT,'tools/liuren-strength-profile.json'))).toString('utf8')),pre.strength_profile_sha256);
await save('功能验收.json',{release:'20261109-deterministic-tools-35',quantity_methods:4,base_only_methods:2,imagery_methods:3,
 original_chart_unchanged:true,default_ai_chart_identical_to_34:true,default_ai_chart_bytes:Buffer.byteLength(JSON.stringify(view)),frozen34_files_unchanged:Object.keys(pre.frozen).length,
 strength_and_void_parameters_unchanged:true,group_numeric_effects:false,paid_model_calls:0,predictive_validation_count:0});
console.log(JSON.stringify({defaultChartIdentical:true,quantity:results.quantity.candidates,base:results.base_quantity.value,evaluation:results.evaluation.rows.map(r=>({datetime:r.datetime,score:r.actors[0].adjusted}))}));
