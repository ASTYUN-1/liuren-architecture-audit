// Read-only implementation audit. Only writes new demonstration outputs.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
import {registerHooks} from 'node:module';
import {execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {runResolvedChart} from '../../tools/liuren-resolved-chart.mjs';
import {exportAIChart} from '../../tools/liuren-chart-view.mjs';
import {computeStrength} from '../../tools/liuren-strength-engine.mjs';
import {strengthBand} from '../../tools/liuren-palace-strength.mjs';
import {buildFacts} from '../../tools/liuren-deterministic.mjs';

const folder=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(folder,'../..');
const save=(name,value)=>fs.writeFile(path.join(folder,name),JSON.stringify(value,null,2)+'\n',{flag:'wx'});
const exact=(name,value)=>fs.writeFile(path.join(folder,name),value,{flag:'wx'});
const own=(object,key)=>Object.hasOwn(object,key);
const digest=bytes=>createHash('sha256').update(bytes).digest('hex');
const input={mode:'datetime',datetime:'2026-11-06T14:43:00+08:00',timezone:'Asia/Shanghai',label:'strength_AI接口演示'};
await save('00-chart-input.json',input);
const chart=await runResolvedChart(input);
if(!chart.ok||!chart.archive)throw Error('Trusted demonstration chart failed');
const publicChart=await exportAIChart(chart);
await save('01-chart-public-codex.json',publicChart);
const facts=chart.facts,det=buildFacts(facts);
const reason='纯工程输出核查：预先指定对象，不验证专业取类，不作现实事件预测';
const actors=publicChart.facts.heaven_earth.flatMap(row=>[
 {id:'T:'+row.tian,role:'全盘观察对象：天盘'+row.tian,basis:reason},
 {id:'J:'+row.tianjiang,role:'全盘观察对象：天将'+row.tianjiang,basis:reason}
]);
actors.push({id:'S:'+facts.day_stem,role:'本日日干观察对象',basis:reason});
const common={season_profile:'quarter-earth',season_basis:'预先固定采用辰未戌丑整月土旺条件表，只作工程演示',review:true};
const single={action:'compute',request:{action:'strength',archive:chart.archive,strength:{...common,mode:'single_palace',actors}}};
const selected={action:'compute',request:{action:'strength',archive:chart.archive,strength:{...common,mode:'selected_relations',
 actors:[
  {id:'T:酉',role:'假设施助方',basis:reason+'；指定酉金生子水'},
  {id:'T:子',role:'假设目标类神',basis:reason+'；指定子水为受助对象'},
  {id:'T:卯',role:'并列观察对象，未采用其与其他对象的跨宫作用',basis:reason+'；用于展示冲刑事实和未采用关系'}
 ],links:[{source:'T:酉',target:'T:子',basis:reason+'；本次只检验已声明金生水的计算通路'}]}}};
await save('02-single-palace.request.json',single);
await save('04-selected-relations.request.json',selected);
const cli=name=>execFileSync(process.execPath,['tools/liuren-codex.mjs','--request',path.join(folder,name)],{cwd:root,encoding:'utf8',windowsHide:true,maxBuffer:16*1024*1024});
const singleText=cli('02-single-palace.request.json');
await exact('03-single-palace.response.json',singleText);
const selectedText=cli('04-selected-relations.request.json');
await exact('05-selected-relations.response.json',selectedText);
const a=JSON.parse(singleText),b=JSON.parse(selectedText);

// Invoke the real native tool executor with a synthetic, local-only context.
// No model request is made and no real OpenCode conversation is touched.
registerHooks({resolve(specifier,context,next){
 if(specifier==='@opencode-ai/plugin')return next(pathToFileURL(path.join(root,'.opencode/node_modules/@opencode-ai/plugin/dist/index.js')).href,context);
 return next(specifier,context);
}});
const {default:plugin}=await import('../../.opencode/plugins/liuren-adjudication.ts');
const hooks=await plugin({directory:root,client:{session:{messages:async()=>({data:[]})}}});
const context={agent:'liuren',sessionID:'strength_ai_output_audit_no_model_20261116'};
const openSingleText=await hooks.tool.liuren_compute.execute(single.request,context);
await exact('06-opencode-single-palace.response.json',openSingleText);
const openSelectedText=await hooks.tool.liuren_compute.execute(selected.request,context);
await exact('07-opencode-selected-relations.response.json',openSelectedText);
const openChartText=await hooks.tool.liuren_compute.execute({action:'chart',archive:chart.archive},context);
await exact('08-opencode-chart.response.json',openChartText);
const oa=JSON.parse(openSingleText),ob=JSON.parse(openSelectedText),oc=JSON.parse(openChartText);

const ctx={seasonProfile:'quarter-earth',seasonBasis:common.season_basis,phase:'outcome'};
const internal=computeStrength(facts,ctx,{shensha:chart.shensha_resolution});
await save('09-engine-internal-with-shensha.json',internal);
await save('10-engine-global-qi.json',internal.global_qi);
const unprovided=computeStrength(facts,ctx);

const coordinate=id=>{
 const native=det.nodes.find(row=>'T:'+row.symbol===id);
 return native?{id,天盘:native.symbol,地盘:native.ground,乘将:native.general,直接阴神:native.direct_yin,
  六亲:native.kin.value,四课位置:native.lesson_slots,三传位置:native.transmission_slots,
  身份说明:'上述为程序盘事实；占题职责未由global_qi提供'}:null;
};
const values=a.actors.filter(row=>row.id.startsWith('T:')).map(row=>{
 const state=a.review.state_basis.find(x=>x.id===row.id),q=a.quantity_basis.rows.find(x=>x.id===row.id);
 return {id:row.id,base:state.base,tomb_access:state.tomb_access,void_retention:state.void_retention,
  environmental_seed:unprovided.rows.find(x=>x.id===row.id).seed,
  with_void:q.with_void,without_void:q.without_void,
  single_palace:row.single_palace,adjusted:row.adjusted,level:row.level,
  void_self:state.void_self,void_ground:state.void_ground,
  public_pending:state.pending_action_conditions,
  internal_pending_with_shensha:internal.coverage.pending.filter(x=>x.id===row.id)};
});
const audit={
 schema:'liuren-strength-output-observation-v1',generated_at:new Date().toISOString(),
 purpose:'捕获当前实际公开接口输出；不改算法、提示词、活动指针或冻结runtime；不调用模型',
 chart_input:input,archive:chart.archive,
 output_presence:{
  codex_single:{keys:Object.keys(a),global_qi:own(a,'global_qi'),review:own(a,'review')},
  codex_selected:{keys:Object.keys(b),global_qi:own(b,'global_qi'),review:own(b,'review')},
  opencode_single:{keys:Object.keys(oa),global_qi:own(oa,'global_qi')},
  opencode_selected:{keys:Object.keys(ob),global_qi:own(ob,'global_qi')},
  codex_chart:{global_qi:own(publicChart.facts,'global_qi'),qi_summary:own(publicChart.facts,'qi_summary')},
  opencode_chart:{global_qi:own(oc,'global_qi'),qi_summary:own(oc,'qi_summary')}
 },
 actor_values:values,
 selected_actors:b.actors,selected_applied_relations:b.applied_relations,
 role_and_position_in_actual_output:{
  actor_keys:Object.keys(b.actors[0]),state_basis_keys:Object.keys(b.review.state_basis[0]),
  roles_returned_verbatim:true,roles_validated:b.coverage.semantic_role_validated,
  native_positions_in_state_basis:true,lesson_and_transmission_slots_in_state_basis:false,
  global_qi_members:Object.entries(internal.global_qi.by_element).map(([element,group])=>({element,...group,
   joined_position_facts:group.actors.map(coordinate),
   joined_position_facts_origin:'本审查脚本跨表拼接，并非实际global_qi返回字段'}))
 },
 pending_observations:{
  public_conditions:a.review.state_basis.map(x=>({id:x.id,pending_action_conditions:x.pending_action_conditions})).filter(x=>x.pending_action_conditions.length),
  internal_without_shensha:unprovided.coverage.pending,
  internal_with_shensha:internal.coverage.pending,
  public_actor_has_action_index:own(a.actors[0],'action_index'),
  public_coverage_keys:Object.keys(a.coverage),
  public_limitation:a.review.limitation
 },
 parity:{codex_and_opencode_single_actors:JSON.stringify(a.actors)===JSON.stringify(oa.actors),
  codex_and_opencode_selected_actors:JSON.stringify(b.actors)===JSON.stringify(ob.actors)},
 implementation_files:Object.fromEntries(await Promise.all([
  '.opencode/liuren-active.json','tools/liuren-palace-strength.mjs','tools/liuren-strength-engine.mjs',
  'tools/liuren-strength-rules.mjs','tools/liuren-chart-view.mjs','tools/liuren-compute-schema.mjs',
  '.opencode/plugins/liuren-adjudication.ts'
 ].map(async name=>[name,digest(await fs.readFile(path.join(root,name)))])))
};
await save('11-field-audit.json',audit);
await save('12-opencode-requests.json',{context,requests:[single.request,selected.request,{action:'chart',archive:chart.archive}],
 scope:'调用原生execute函数返回值；未连接运行中的OpenCode会话或模型，没有捕获模型HTTP请求'});
const names=(await fs.readdir(folder)).filter(name=>name.endsWith('.json'));
await save('13-output-manifest.json',{files:await Promise.all(names.map(async name=>{const bytes=await fs.readFile(path.join(folder,name));return {name,bytes:bytes.length,sha256:digest(bytes)};}))});
console.log(JSON.stringify({folder,chart:{pillars:facts.pillars,void_branches:facts.void_branches},actor_values:values,
 selected:b.actors,relations:b.applied_relations,global_qi:internal.global_qi,output_presence:audit.output_presence,
 pending_count:{public:audit.pending_observations.public_conditions.length,internal_with_shensha:internal.coverage.pending.length},
 parity:audit.parity},null,2));
