import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import {validateInput,validateOutput,parseTaskOutput} from './source/liuren-adjudication-contract.mjs';
const input=JSON.parse(await fs.readFile(new URL('./synthetic-input.json',import.meta.url),'utf8'));
const copy=()=>structuredClone(input);
function output(){return {schema:'liuren-adjudication-output-v1',request_id:input.request_id,status:'needs_input',entity_checks:[],relation_checks:[],answers:[{question_id:'Q1',verdict:'尚未裁明，需补充资料',precision:'unresolved',decisive_relation_ids:[],counter_relation_ids:[],counter_resolution:'材料不足，不虚构反证',process:'未定',timing:'不适用',conditions:[],limits:['缺关键取用']}],source_conflicts:[],missing_inputs:['缺关键取用依据，影响Q1']};}
test('complete program chart and neutral packet are accepted',()=>assert.equal(validateInput(copy()).request_id,input.request_id));
test('primary verdict, candidate rankings and unknown nested fields cannot pass through',()=>{
  for(const field of ['initial_verdict','ranking','known_result','previous_judgment']){const p=copy();p[field]='测试倾向';assert.throws(()=>validateInput(p),/unexpected/);}
  const p=copy();p.questions[0].preferred='可取得';assert.throws(()=>validateInput(p),/unexpected/);
});
test('incomplete lessons, duplicate plate, extra chart summary and missing reference fail',()=>{
  let p=copy();p.chart.facts.lessons.pop();assert.throws(()=>validateInput(p),/lessons/);
  p=copy();p.chart.facts.heaven_earth[1].di=p.chart.facts.heaven_earth[0].di;assert.throws(()=>validateInput(p),/plate/);
  p=copy();p.chart.facts.summary='原初判';assert.throws(()=>validateInput(p),/unexpected/);
  p=copy();p.entities[0].question_ids=['Q404'];assert.throws(()=>validateInput(p),/unknown reference/);
});
test('case/experience material cannot masquerade as method source',()=>{
  for(const source of ['案例项目库/a.md','经验日志/b.md','output/experience-index/a.json','books/../案例项目库/a.md']){const p=copy();p.method_materials[0].source_path=source;assert.throws(()=>validateInput(p),/source/);}
});
test('needs_input is explicit and mismatched request cannot be accepted',()=>{
  assert.equal(validateOutput(output(),input).status,'needs_input');
  let r=output();r.request_id='another';assert.throws(()=>validateOutput(r,input),/identity/);
  r=output();r.missing_inputs=[];assert.throws(()=>validateOutput(r,input),/missing inputs/);
});
test('cannot claim completed with omitted entities or invented basis',()=>{
  let r=output();r.status='completed';r.missing_inputs=[];assert.throws(()=>validateOutput(r,input),/omitted/);
  r=output();r.entity_checks=[{id:'S1',referent:'人',branch:'亥',position:'干上',mapping_review:'待核',five_qi:'待核',twelve_states:'待核',site_yin:'待核',shenjiang:'待核',limits:[]}];r.relation_checks=[{id:'R1',from:'S1',to:'S1',relation:'待核关系',validity:'unresolved',basis_ids:['E99'],reason:'未知来源',effect_scope:['结果']}];assert.throws(()=>validateOutput(r,input),/unknown reference/);
});
test('native task wrapper is parsed; prose and scratch output are rejected',()=>{
  const result=output();assert.deepEqual(parseTaskOutput('<task_result>\n'+JSON.stringify(result)+'\n</task_result>'),result);
  assert.throws(()=>parseTaskOutput('我先想一想，然后给答案'),/did not return/);
});
