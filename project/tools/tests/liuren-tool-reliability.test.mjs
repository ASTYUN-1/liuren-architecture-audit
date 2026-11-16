import test from 'node:test';
import assert from 'node:assert/strict';
import {tool} from '../../.opencode/node_modules/@opencode-ai/plugin/dist/index.js';
import {packet} from './fixtures/liuren-adjudication-v2.mjs';
import {createAuditSchemas,evidenceCatalog,reviewScaffold,checkDeliveryReview,inspectRecheckFindings,REVIEW_CHECKS,auditHash} from '../liuren-consistency-audit.mjs';
import {parseResultArguments} from '../liuren-adjudication-schema.mjs';

function fixture(){
 const p=packet();p.questions[0].domain='exam';
 p.input_review={questions:[{question_id:'Q1',route:{event:'合成评分',focus:'class',primary_entity_ids:['S1'],selection_basis:'仅测试接口',time_scope:'评定结果'}}]};
 p.consistency_policy={analysis_route_required:true};
 const report='合成工程报告：15与7.5均为本数，量级仍有缺口。';
 const receipts=[{ref:{sha256:'a'.repeat(64)},request:{action:'quantity'},result:{value:15}}];
 const review={report_sha256:auditHash(report),checks:REVIEW_CHECKS.map(check=>({check,status:'checked',report_quote:report,basis:'合成工程核对',evidence_refs:['Q1','input:Q1','S1','route:Q1','a'.repeat(64)]}))};
 return {p,report,receipts,review};
}
test('observed question and actor refs are real bound identities; invented refs remain rejected',()=>{
 const {p,report,receipts,review}=fixture();
 assert.equal(checkDeliveryReview(review,report,{packet:p,receipts}).ok,true);
 review.checks[2].evidence_refs.push('LF3329 scope','书籍库/不存在.txt:1-2','b'.repeat(64));
 const r=checkDeliveryReview(review,report,{packet:p,receipts});
 assert.deepEqual(r.issues[0].unknown_refs,['LF3329 scope','书籍库/不存在.txt:1-2','b'.repeat(64)]);
 assert.equal(r.issues[0].path,'/review/checks/2/evidence_refs');
});
test('catalog and scaffold expose actual identities without claiming semantic review',()=>{
 const {p,report,receipts}=fixture(),catalog=evidenceCatalog(p,receipts);
 assert.ok(catalog.allowed_refs.includes('input:Q1'));assert.ok(!catalog.allowed_refs.includes('input:Q2'));
 const draft=reviewScaffold(p,report,receipts,'child');
 assert.equal(draft.fill_required,true);assert.equal(draft.arguments.review.report_sha256,auditHash(report));
 assert.ok(draft.arguments.review.checks.every(r=>r.status==='unresolved'&&r.report_quote===''&&r.basis===''));
 assert.equal(checkDeliveryReview(draft.arguments.review,report,{packet:p,receipts}).ok,false);
});
test('recheck reports the exact invalid quotation and unknown source IDs before consuming a turn',()=>{
 const {p,report,receipts}=fixture();
 const findings=[{check:'calculation_scope',report_quote:'拼接的句子',evidence_refs:['input:Q1','not-a-bound-ref'],evidence:'合成缺口',request:'核实合成条件'}];
 const r=inspectRecheckFindings(p,report,findings,receipts);
 assert.deepEqual(r.issues.map(i=>i.path),['/findings/0/report_quote','/findings/0/evidence_refs']);
 findings[0].report_quote='量级仍有缺口';findings[0].evidence_refs=['input:Q1','a'.repeat(64)];
 assert.equal(inspectRecheckFindings(p,report,findings,receipts).ok,true);
});
test('flat review compatibility moves only the envelope and rejects conflicts or ignored fields',()=>{
 const {review}=fixture(),s=tool.schema,a=createAuditSchemas(s);
 const schema=s.object({task_id:s.string().optional(),action:s.enum(['review','recheck','read','deliver']),review:a.review.optional(),findings:s.array(a.finding).optional(),report_sha256:s.string().optional(),checks:a.review.shape.checks.optional()}).strict();
 const flat={action:'review',task_id:'child',...review};schema.parse(flat);
 const normalized=parseResultArguments(schema,flat);assert.deepEqual(normalized.review,review);assert.equal(normalized.checks,undefined);
 assert.throws(()=>parseResultArguments(schema,{...flat,review}),/不能同时/);
 assert.throws(()=>parseResultArguments(schema,{action:'review'}),/须填写/);
 assert.throws(()=>parseResultArguments(schema,{action:'read',review}),/不使用/);
 assert.throws(()=>parseResultArguments(schema,{action:'review',...review,unexpected:true}),/unexpected|Unrecognized/);
});
test('bound method source IDs do not become available retroactively to old packets',()=>{
 const {p,report,review}=fixture();review.checks[0].evidence_refs=['QM:LF3329-class-ground'];
 assert.equal(checkDeliveryReview(review,report,{packet:p}).ok,false);
 p.consistency_policy.bound_method_source_ids=['QM:LF3329-class-ground'];
 assert.ok(evidenceCatalog(p).allowed_refs.includes('QM:LF3329-class-ground'));
 assert.equal(checkDeliveryReview(review,report,{packet:p,receipts:fixture().receipts}).ok,true);
});
