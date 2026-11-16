import fs from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import path from 'node:path';
import {runResolvedChart} from '../../tools/liuren-resolved-chart.mjs';
import {validateInput} from './source/liuren-adjudication-contract.mjs';
const here=path.dirname(fileURLToPath(import.meta.url));
const chart=await runResolvedChart({datetime:'2026-11-05T10:00'},{persist:false});
if(!chart.ok||!chart.validation.ok)throw Error('synthetic chart unavailable');
const packet={schema:'liuren-adjudication-input-v1',request_id:'smoke-20261105',
  questions:[{id:'Q1',text:'合成技术题：按此课判断一般求财能否取得。',subject:'合成求测者，无真实客户',stage:'尚未取财',deadline:'未限定',success_criteria:'实际取得钱款；不问金额或日期',alternatives:['可取得','不可取得','条件尚不足以区分']}],
  chart:{source:'liuren-resolved-chart：2026-11-05T10:00，北京时间，persist=false，仅技术合成课',facts:chart.facts},
  facts:[{id:'F1',text:'仅为软件接线验收的合成问题；没有现实反馈或已知正确答案。',source:'测试构造'}],
  entities:[
    {id:'S1',question_ids:['Q1'],referent:'求测者干上神候选',branch:'亥',position:'第一课干上',mapping_basis:'癸寄丑，程序盘干上亥；待专业复核'},
    {id:'T1',question_ids:['Q1'],referent:'钱款财类候选',branch:'巳',position:'初传、支上',mapping_basis:'程序盘巳为癸日财，尚须核本问取用'},
    {id:'T2',question_ids:['Q1'],referent:'影响取财的末传类神候选',branch:'丑',position:'末传',mapping_basis:'程序盘末传官鬼，吉凶作用待独立审查'}],
  observations:[],
  method_materials:[{id:'M1',title:'当前finance专项完整正文，条件待核',source_path:'runtime/liuren/20261105-subagent-adjudication-03/domains/finance.md',quote:await fs.readFile(path.join(here,'candidate/runtime/liuren/20261105-subagent-adjudication-03/domains/finance.md'),'utf8')}],
  unknowns:['没有现实当事人、交易对手和业务过程，不能把技术题当成真实预测验证。']};
validateInput(packet);
await fs.writeFile(path.join(here,'synthetic-input.json'),JSON.stringify(packet,null,2)+'\n');
console.log(JSON.stringify({validSyntheticInput:true,privateCaseData:false,chartPersisted:false,packetChars:JSON.stringify(packet).length}));
