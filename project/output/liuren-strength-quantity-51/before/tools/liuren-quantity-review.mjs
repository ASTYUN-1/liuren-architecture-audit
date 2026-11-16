// Checks declared quantity derivations against this task's real receipts.
// No score-to-quantity formula or automatic prediction is defined here.
export const QUANTITY_REVIEW_GUIDE='仅consistency_policy.quantity_review_required=true的新任务执行以下50版要求，旧绑定任务不补造新字段。数值问另给audit.quantity_reviews，每个tasks含quantity的问一项：question_id、status(adjusted/base_retained/unresolved)、target、base_receipt_sha256、strength_receipt_sha256、final_receipt_sha256、steps、qi_review、void_review:{status(applied/already_in_base/included_in_qi/not_applicable/exception),basis}、report_quote。三个receipt字段均为本任务calculation_receipt.sha256。steps每步含kind(qi/void/other/rounding)、op(multiply/add)、operand、origin(source/user_research/model_estimate)、basis；依序从基础数运算到最终数，全部用quantity expression实际计算，不手改尾数。base_retained也须说明为何原数可用，steps=[]且final回执可复用base。unresolved仅须question_id/status/qi_review/report_quote，说明具体缺步，不能以基数冒充最终数。旬空减半若已纳入同层基数或qi比例须声明；strength状态计空本身不算数量已扣。程序核回执、算术和声明完整性，不验证专业系数、取用或预测准确率。';

export function quantityReviewSchema(s){
 const t=s.string().min(1).max(4000);
 return s.array(s.object({question_id:t,status:s.enum(['adjusted','base_retained','unresolved']),
  target:t.optional(),base_receipt_sha256:t.optional(),strength_receipt_sha256:t.optional(),final_receipt_sha256:t.optional(),
  steps:s.array(s.object({kind:s.enum(['qi','void','other','rounding']),op:s.enum(['multiply','add']),
   operand:s.number().finite(),origin:s.enum(['source','user_research','model_estimate']),basis:t}).strict()).max(8).optional(),
  qi_review:t,void_review:s.object({status:s.enum(['applied','already_in_base','included_in_qi','not_applicable','exception']),basis:t}).strict().optional(),
  report_quote:t}).strict()).max(12).optional();
}
const text=v=>typeof v==='string'&&!!v.trim();
const near=(a,b)=>Number.isFinite(a)&&Number.isFinite(b)&&Math.abs(a-b)<=1e-9*Math.max(1,Math.abs(a),Math.abs(b));
export function checkQuantityReviews(p,body,audit,receipts){
 if(!p.consistency_policy?.quantity_review_required)return [];
 const issues=[],add=(code,path,message)=>issues.push({code,path,message});
 const questions=p.questions.filter(q=>q.tasks?.includes('quantity')),seen=new Set();
 if(!questions.length)return issues;
 if(!Array.isArray(audit.quantity_reviews)){add('quantity_review_required','/audit/quantity_reviews','数值问须核基数、真实旺衰及数量修正，不能仅注明未执行');return issues;}
 for(const [i,r] of audit.quantity_reviews.entries()){
  const at='/audit/quantity_reviews/'+i;
  if(!r||!questions.some(q=>q.id===r.question_id)||seen.has(r.question_id)){add('quantity_question',at,'每个数值问恰好一项');continue;}
  seen.add(r.question_id);
  if(!text(r.report_quote)||!body.includes(r.report_quote)||!text(r.qi_review))add('quantity_basis',at,'须定位公开正文并说明气态与数量关系');
  if(r.status==='unresolved'){
   // The report remains explicitly incomplete; never invent a number to pass.
   add('quantity_unresolved',at,'取数尚有具体缺步，保留缺口，不能视为数值已完成');continue;
  }
  if(!['adjusted','base_retained'].includes(r.status)){add('quantity_status',at,'未知修正状态');continue;}
  const find=h=>receipts.find(v=>v.receipt_sha256===h),base=find(r.base_receipt_sha256),final=find(r.final_receipt_sha256),strength=find(r.strength_receipt_sha256);
  if(!base||base.request?.action!=='quantity'||!Number.isFinite(base.result?.value)||!final||final.request?.action!=='quantity'||!Number.isFinite(final.result?.value)){
   add('quantity_receipt',at,'基数与最终数须引用本任务真实且有单一value的quantity回执');continue;
  }
  if(!strength||strength.request?.action!=='strength'||!strength.result?.actors?.some(a=>a.id===r.target))add('quantity_strength_receipt',at,'须引用包含本次数量主类的真实strength回执');
  const methodTarget=base.request.quantity_method?.target;
  if(methodTarget&&methodTarget!==r.target)add('quantity_target',at,'具名基数与数量主类不一致，不能无说明互换');
  if(!text(r.target)||!Array.isArray(r.steps)||r.steps.length>8){add('quantity_steps',at,'须声明主类与有序修正步骤，保留基数时用空steps');continue;}
  let value=base.result.value;
  for(const step of r.steps){
   if(!step||!['qi','void','other','rounding'].includes(step.kind)||!['multiply','add'].includes(step.op)||!Number.isFinite(step.operand)||!['source','user_research','model_estimate'].includes(step.origin)||!text(step.basis)){
    add('quantity_step_basis',at,'每步须明确增减方式、数值、来源身份及条件');value=NaN;break;
   }
   value=step.op==='multiply'?value*step.operand:value+step.operand;
  }
  if(!near(value,final.result.value))add('quantity_arithmetic',at,'声明的基数和修正步骤与最终回执不符');
  if(r.status==='base_retained'&&(r.steps.length||!near(base.result.value,final.result.value)))add('quantity_retained',at,'保留基数不得暗中增减');
  if(r.status==='adjusted'&&!r.steps.length)add('quantity_adjustment_missing',at,'声称已修正但没有修正步骤');
  const v=r.void_review;
  if(!v||!['applied','already_in_base','included_in_qi','not_applicable','exception'].includes(v.status)||!text(v.basis)){
   add('quantity_void_review',at,'须核旬空是否减数、已包含或有何例外');continue;
  }
  const voidSteps=r.steps.filter(s=>s?.kind==='void');
  if(v.status==='applied'&&(voidSteps.length!==1||voidSteps[0].op!=='multiply'||voidSteps[0].operand!==0.5))add('quantity_void_half',at,'采用本次数量旬空减半须有且仅有一次乘0.5步骤');
  if(['already_in_base','included_in_qi','not_applicable'].includes(v.status)&&voidSteps.length)add('quantity_void_duplicate',at,'已包含或不适用旬空减数，不得再添一次同义void步骤');
  if(v.status==='included_in_qi'&&!r.steps.some(s=>s.kind==='qi'&&s.op==='multiply'&&s.operand<1&&s.operand>0))add('quantity_void_inclusion',at,'声称数量比例已含空亡时须有相应减数步骤；状态计空不算');
  const node=r.target?.startsWith('T:')?p.deterministic?.nodes?.find(n=>n.symbol===r.target.slice(2)):null;
  if(node?.void_self===true&&v.status==='not_applicable')add('quantity_void_exception',at,'数量主类本身旬空；若本题不减须明确exception及阶段/专项依据，不能略过');
 }
 if(seen.size!==questions.length)add('quantity_coverage','/audit/quantity_reviews','须覆盖全部数值问');
 return issues;
}
