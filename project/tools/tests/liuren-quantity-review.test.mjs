import test from 'node:test';
import assert from 'node:assert/strict';
import {checkQuantityReviews,quantityReviewSchema} from '../liuren-quantity-review.mjs';
import {calculate} from '../liuren-deterministic.mjs';
import {checkAudit,createAuditSchemas,POLICY} from '../liuren-consistency-audit.mjs';
import {tool} from '../../.opencode/node_modules/@opencode-ai/plugin/dist/index.js';
const s=tool.schema;

function fixture(){
 const expression={op:'multiply',args:[{value:56},{value:0.5}]};
 const p={consistency_policy:{quantity_review_required:true},questions:[{id:'Q1',tasks:['quantity']}],deterministic:{nodes:[{symbol:'未',void_self:true}]}};
 const body='示例仅核传输：基数56，数量旬空减半，56×0.5=28分；不是历史案例预测。';
 const row={question_id:'Q1',status:'adjusted',target:'T:未',base_receipt_sha256:'base',strength_receipt_sha256:'strength',final_receipt_sha256:'final',
  steps:[{kind:'void',op:'multiply',operand:0.5,origin:'user_research',basis:'合成情景指定数量主类旬空减半'}],
  qi_review:'此合成例不另加气态比例，免得同一空减再扣',void_review:{status:'applied',basis:'数量层尚未扣，本次实际扣一次'},report_quote:body};
 const receipts=[{receipt_sha256:'base',request:{action:'quantity',expression:{value:56}},result:calculate({value:56})},
  {receipt_sha256:'strength',request:{action:'strength'},result:{actors:[{id:'T:未',adjusted:2.5}]}},
  {receipt_sha256:'final',request:{action:'quantity',expression},result:calculate(expression)}];
 return {p,body,row,receipts};
}
const errors=f=>checkQuantityReviews(f.p,f.body,{quantity_reviews:[f.row]},f.receipts);
test('real expression result and one quantity-layer void half form a traceable derivation',()=>{assert.deepEqual(errors(fixture()),[]);});
test('declaring not executed no longer satisfies new quantity review',()=>{const f=fixture();assert.equal(checkQuantityReviews(f.p,f.body,{},f.receipts)[0].code,'quantity_review_required');delete f.row.void_review;assert.ok(errors(f).some(x=>x.code==='quantity_void_review'));});
test('final receipt and claimed correction must agree; 56 half is 28, never retrofitted 22',()=>{const f=fixture();f.receipts[2].result=calculate({value:22});assert.ok(errors(f).some(x=>x.code==='quantity_arithmetic'));});
test('missing strength, unrelated target, fabricated quantity receipt and wrong quote are caught',()=>{
 for(const mutate of [f=>f.row.strength_receipt_sha256='fake',f=>f.row.target='T:子',f=>f.row.final_receipt_sha256='fake',f=>f.row.report_quote='不存在的公开句子']){
  const f=fixture();mutate(f);assert.ok(errors(f).length);
 }
});
test('state-layer void is not enough to claim a quantity half',()=>{const f=fixture();f.row.steps=[];assert.ok(errors(f).some(x=>x.code==='quantity_void_half'));});
test('one estimated quantity factor may include void without a second half',()=>{const f=fixture();f.row.steps[0].kind='qi';f.row.steps[0].origin='model_estimate';f.row.void_review={status:'included_in_qi',basis:'本次数量比例0.5已含旬空，不以状态计空代替数量运算'};assert.deepEqual(errors(f),[]);});
test('already included void cannot silently be deducted again',()=>{const f=fixture();f.row.void_review.status='already_in_base';assert.ok(errors(f).some(x=>x.code==='quantity_void_duplicate'));});
test('retaining a base is allowed when state and specialized non-application are explained',()=>{const f=fixture();f.row.status='base_retained';f.row.steps=[];f.row.final_receipt_sha256='base';f.row.void_review={status:'exception',basis:'合成序数例：不能将第56名折半为第28名，另循专法；不自动将此例用于分数'};assert.deepEqual(errors(f),[]);f.row.void_review.status='not_applicable';assert.ok(errors(f).some(x=>x.code==='quantity_void_exception'));});
test('unknown correction remains an explicit unresolved issue, not an invented final estimate',()=>{const f=fixture();f.row={question_id:'Q1',status:'unresolved',qi_review:'查法后尚缺所求量级映射',report_quote:f.body};assert.ok(errors(f).some(x=>x.code==='quantity_unresolved'));});
test('legacy bound tasks and non-quantity questions are unaffected',()=>{const f=fixture();delete f.p.consistency_policy.quantity_review_required;assert.deepEqual(checkQuantityReviews(f.p,f.body,{},[]),[]);f.p.consistency_policy.quantity_review_required=true;f.p.questions[0].tasks=['outcome'];assert.deepEqual(checkQuantityReviews(f.p,f.body,{},[]),[]);});
test('audit schema accepts the compact review and rejects unknown operations',()=>{const f=fixture();assert.equal(quantityReviewSchema(s).parse([f.row]).length,1);f.row.steps[0].op='divide';assert.throws(()=>quantityReviewSchema(s).parse([f.row]));assert.ok(createAuditSchemas(s).audit.shape.quantity_reviews);});
test('shared audit actually invokes the new review for flagged numerical questions',()=>{
 const f=fixture();Object.assign(f.p,{input_origin:{source_text:'多少分'},method_materials:[],observations:[],facts:[]});f.p.consistency_policy={...POLICY,quantity_review_required:true};
 const audit={schema:POLICY.schema,questions:[{question_id:'Q1',request_quote:'多少分',stage_origin:'unknown',stage_basis:'未说明',success_review:'示例',answer_quote:f.body,candidates:[],counterevidence:{present:false,relation_ids:[],report_quote:'',resolution:'本例只核算术',basis_refs:[]}}],relations:[],calculations:[],omission_review:'合成示例'};
 assert.ok(checkAudit(f.p,f.body,audit,f.receipts).issues.some(x=>x.code==='quantity_review_required'));
 audit.quantity_reviews=[f.row];assert.equal(checkAudit(f.p,f.body,audit,f.receipts).ok,true);
});
test('new active task binds the requirement and audits real Codex computation receipts without a model call',async()=>{
 const {ROOT,execute}=await import('../liuren-codex.mjs');
 const {runResolvedChart}=await import('../liuren-resolved-chart.mjs');
 const {loadPacket}=await import('../liuren-adjudication-files.mjs');
 const {packet}=await import('./fixtures/liuren-adjudication-v2.mjs');
 const chart=await runResolvedChart({datetime:'2026-10-18T13:22'},{persist:true});
 const p=packet(),question='合成数值传输测试，核对56减半为28，不作现实预测。';
 p.method_modules=['quantity-correction'];p.request_id='quantity-review-transport-'+Date.now();p.chart={source:'可信程序盘，仅工程验证',archive:chart.archive};
 p.questions[0].text=question;p.questions[0].tasks=['quantity'];p.questions[0].task_basis=[{task:'quantity',origin:'user_requested',request_quote:question,reason:'明确算术验证'}];
 delete p.entities[0].position;
 p.input_review={questions:[{question_id:'Q1',request_quote:question,success_basis:'合成传输',stage_origin:'unknown',stage_basis:'无现实阶段',route:{event:'合成数量验收',focus:'class',primary_entity_ids:['S1'],selection_basis:'工程传递',time_scope:'本轮合成运算'}}],facts:[],neutrality_review:'不作专业预测'};
 const saved=await execute({action:'packet',purpose:'transport-test',original_question:question,packet:p});
 const loaded=await loadPacket(ROOT,saved.packet_ref);
 assert.equal(loaded.envelope.packet.consistency_policy.quantity_review_required,true);
 assert.equal(JSON.parse(loaded.raw).consistency_policy.quantity_review_required,true);
 const base=await execute({action:'compute',run:saved.run,request:{action:'quantity',expression:{value:56}}});
 const actualTarget='T:'+loaded.envelope.packet.chart.facts.void_branches[0];
 const strength=await execute({action:'compute',run:saved.run,request:{action:'strength',strength:{mode:'single_palace',season_profile:'quarter-earth',season_basis:'合成固定表，仅工程测试',actors:[{id:actualTarget,role:'合成数量主类',basis:'指定本盘实际旬空支验证回执绑定，不作专业取类'}]}}});
 const coupled=loaded.envelope.packet.consistency_policy.quantity_coupling_required===true;
 const request=coupled?{action:'quantity',quantity_adjustment:{route:'source',target:actualTarget,kind:'score',
  base_receipt_sha256:base.calculation_receipt.sha256,strength_receipt_sha256:strength.calculation_receipt.sha256,
  base_factors:{qi:'raw',void:false,basis:'合成常量56，仅核工程'},magnitude:{exponent:0,unit:'分',basis:'合成已定量级',upper_bound:100},
  evidence:[{use:'base',ref:'M_quantity-correction',quote:'base-only是已算基础步',application:'合成指定56，仅测传递和半数；引用不宣称真实预测原法'}],void:{status:'apply_half',basis:'合成指定数量主类本身旬空，采用项目半数',origin:'user_research'},basis:'仅传输测试，不作占断'}}:
  {action:'quantity',expression:{op:'multiply',args:[{value:56},{value:0.5}]}};
 const final=await execute({action:'compute',run:saved.run,request});
 const f=fixture(),row={...(coupled?final.review:{...f.row,target:actualTarget}),question_id:'Q1',report_quote:f.body,base_receipt_sha256:base.calculation_receipt.sha256,strength_receipt_sha256:strength.calculation_receipt.sha256,final_receipt_sha256:final.calculation_receipt.sha256};
 const audit={schema:POLICY.schema,questions:[{question_id:'Q1',request_quote:question,stage_origin:'unknown',stage_basis:'合成无阶段',success_review:'只核回执',answer_quote:f.body,candidates:[],counterevidence:{present:false,relation_ids:[],report_quote:'',resolution:'仅合成算术',basis_refs:[]}}],relations:[],calculations:[],omission_review:'合成传输，非术理判断'};
 const missing=await execute({action:'audit',mode:'check',run:saved.run,result:f.body,audit});
 assert.ok(missing.issues.some(x=>x.code==='quantity_review_required'));
 audit.quantity_reviews=[row];const valid=await execute({action:'audit',mode:'check',run:saved.run,result:f.body,audit});
 assert.equal(valid.ok,true,JSON.stringify(valid.issues));
 if(coupled){
  const experimental=await execute({action:'compute',run:saved.run,request:{action:'quantity',quantity_adjustment:{...request.quantity_adjustment,route:'experimental',rounding:{decimals:0,basis:'工程测试整数输出'}}}});
  const e=strength.quantity_basis.rows.find(r=>r.id===actualTarget).without_void;
  const {quantityFactor}=await import('../liuren-quantity-adjustment.mjs');
  assert.equal(experimental.strength_used.without_void,e);
  assert.equal(experimental.value,Math.round(56*Number(quantityFactor(e).toFixed(12))*.5));
  assert.equal(experimental.review.steps.filter(s=>s.kind==='void').length,1);
  await assert.rejects(()=>execute({action:'compute',run:saved.run,request:{action:'quantity',quantity_adjustment:{...request.quantity_adjustment,base_receipt_sha256:experimental.calculation_receipt.sha256}}}),/再次修正/);
 }
});
