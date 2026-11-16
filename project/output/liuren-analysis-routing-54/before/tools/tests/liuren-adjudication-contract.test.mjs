import test from 'node:test';
import assert from 'node:assert/strict';
import {packet,result,moduleURL} from './fixtures/liuren-adjudication-v2.mjs';
const {validateInput,validateOutput,parseTaskOutput}=await import(moduleURL('tools/liuren-adjudication-contract.mjs'));
const {normalizePacket}=await import(moduleURL('tools/liuren-adjudication-files.mjs'));

test('v2 accepts a focused packet and result',()=>assert.equal(validateOutput(result(),validateInput(packet())).status,'completed'));
test('no conflict is legitimate and does not require fabricated opposition',()=>{
  const p=packet(),r=result();p.focus_issues=[];r.issue_resolutions=[];
  assert.equal(validateOutput(r,p),r);
});
for(const field of ['initial_verdict','preferred','ranking','weights','known_result','previous_judgment']){
  test('packet rejects tendency/answer field '+field,()=>{const p=packet();p[field]='forbidden';assert.throws(()=>validateInput(p),/unexpected/);});
}
test('missing focus_issues cannot silently use the v1 interface',()=>{const p=packet();delete p.focus_issues;assert.throws(()=>validateInput(p),/focus_issues/);});
test('old schemas identify the exact schema field instead of a generic identity error',()=>{const p=packet();p.schema='liuren-adjudication-input-v1';assert.throws(()=>validateInput(p),/packet.schema: expected liuren-adjudication-input-v2/);});

test('date-prefixed and UUID request IDs survive input, output and normalization unchanged',()=>{
 for(const id of ['20261106-liuren-01','6c7b962a-819b-44c2-95df-2240accaf974','q'.repeat(128)]){
  const p=packet(),r=result();p.request_id=id;r.request_id=id;
  assert.equal(normalizePacket(p).packet.request_id,id);assert.equal(validateOutput(r,p).request_id,id);
 }
});

test('unsafe request IDs name the single field to repair without dropping analysis material',()=>{
 for(const id of ['../escape','a/b','a\\b','','a'.repeat(129),null]){const p=packet();p.request_id=id;assert.throws(()=>validateInput(p),/packet.request_id:.*preserve all materials/);}
});

test('expanded materials above the old 100k limit are retained and oversize errors include exact counts',()=>{
 const p=packet();p.unknowns=Array.from({length:24},()=> '材'.repeat(5500));
 assert.ok(JSON.stringify(p).length>100000);assert.equal(validateInput(p).unknowns.length,24);
 p.unknowns=Array.from({length:40},()=> '材'.repeat(5500));
 assert.throws(()=>validateInput(p),/actual \d+ characters; maximum 200000/);
});
for(const field of ['question_ids','entity_ids','observation_ids']){
  test('focus issue rejects unknown '+field,()=>{const p=packet();p.focus_issues[0][field]=['Missing'];assert.throws(()=>validateInput(p),/unknown reference/);});
}
test('focus issue needs a question and globally unique ID',()=>{
  const p=packet();p.focus_issues[0].question_ids=[];assert.throws(()=>validateInput(p),/invalid array/);
  p.focus_issues[0].question_ids=['Q1'];p.focus_issues[0].id='O1';assert.throws(()=>validateInput(p),/globally unique/);
});
test('reserved book E identifiers are renamed in every structured focus reference',()=>{
  const p=packet();p.questions[0].id='E01';p.entities[0].question_ids=['E01'];p.observations[0].id='E02';
  p.focus_issues[0].question_ids=['E01'];p.focus_issues[0].observation_ids=['E02'];
  const normalized=normalizePacket(p);
  assert.deepEqual(normalized.packet.focus_issues[0].question_ids,['I_E01']);
  assert.deepEqual(normalized.packet.focus_issues[0].observation_ids,['I_E02']);
  assert.equal(normalized.renamed_ids.length,2);assert.equal(p.observations[0].id,'E02');
});
test('adjudicator may add a chart entity outside the main focus issues',()=>{
  const p=packet(),r=result();r.entity_checks.push({...r.entity_checks[0],id:'J1',branch:'丑'});
  r.scope_review.mapping_status='corrected';r.scope_review.added_entity_ids=['J1'];
  r.relation_checks.push({...r.relation_checks[0],id:'R2',from:'J1'});
  r.answers[0].decisive_relation_ids=['R2'];assert.equal(validateOutput(r,p),r);
});
test('new entities must be declared and use J IDs',()=>{
  const p=packet(),r=result();r.entity_checks.push({...r.entity_checks[0],id:'S2'});
  assert.throws(()=>validateOutput(r,p),/J IDs/);
  r.entity_checks[1].id='J1';assert.throws(()=>validateOutput(r,p),/every new entity/);
});
for(const field of ['branch','referent','position']){
  test('mapping change '+field+' must be declared',()=>{
    const p=packet(),r=result();r.entity_checks[0][field]=field==='branch'?'丑':'明确修正';
    assert.throws(()=>validateOutput(r,p),/mapping changes/);
    r.scope_review.mapping_status='corrected';r.scope_review.corrections=['S1 '+field+'修正'];assert.equal(validateOutput(r,p),r);
  });
}
test('completed result cannot omit an original entity',()=>{const r=result();r.entity_checks=[];assert.throws(()=>validateOutput(r,packet()),/omitted input entity/);});
test('scope review must cover all questions exactly once',()=>{
  const r=result();r.scope_review.question_ids=['Q1','Q1'];assert.throws(()=>validateOutput(r,packet()),/every question once/);
});
test('every focus issue must have exactly one response',()=>{
  const r=result();r.issue_resolutions=[];assert.throws(()=>validateOutput(r,packet()),/missing focus/);
  r.issue_resolutions=[result().issue_resolutions[0],result().issue_resolutions[0]];
  assert.throws(()=>validateOutput(r,packet()),/unknown or duplicate/);
  r.issue_resolutions[0].issue_id='C9';assert.throws(()=>validateOutput(r,packet()),/unknown or duplicate/);
});
test('resolved issue needs an existing checked relation',()=>{
  const r=result();r.issue_resolutions[0].relation_ids=[];assert.throws(()=>validateOutput(r,packet()),/requires checked/);
  r.issue_resolutions[0].relation_ids=['R9'];assert.throws(()=>validateOutput(r,packet()),/unknown reference/);
});
test('unresolved issue needs a concrete limit but does not force a lower verdict',()=>{
  const r=result();r.issue_resolutions[0].status='unresolved';assert.throws(()=>validateOutput(r,packet()),/concrete limit/);
  r.issue_resolutions[0].limits=['该合成细节不确定，不影响已核趋势'];r.answers[0].precision='direction';
  assert.equal(validateOutput(r,packet()).answers[0].verdict,'接口测试通过');
});
test('needs_input must specify missing material and cannot be completed with missing inputs',()=>{
  const r=result();r.status='needs_input';r.scope_review.mapping_status='needs_input';r.answers[0].precision='unresolved';
  assert.throws(()=>validateOutput(r,packet()),/concrete missing/);
  r.missing_inputs=['缺少某已知背景的核对'];assert.equal(validateOutput(r,packet()),r);
  r.status='completed';assert.throws(()=>validateOutput(r,packet()),/unresolved mapping/);
  r.scope_review.mapping_status='confirmed';assert.throws(()=>validateOutput(r,packet()),/missing inputs/);
});
test('decisive and source references are checked',()=>{
  const r=result();r.answers[0].decisive_relation_ids=['R9'];assert.throws(()=>validateOutput(r,packet()),/unknown reference/);
  r.answers[0].decisive_relation_ids=['R1'];r.relation_checks[0].basis_ids=['E99'];assert.throws(()=>validateOutput(r,packet()),/unknown reference/);
});
test('native task wrapper is accepted without changing the verdict',()=>{
  assert.deepEqual(parseTaskOutput('<task_result>\n```json\n'+JSON.stringify(result())+'\n```\n</task_result>'),result());
});
