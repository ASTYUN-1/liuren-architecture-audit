// One final quantity from task-owned receipts. Experimental coefficients are
// project parameters, not ancient text, probabilities, or fitted predictions.
import {calculate,hash} from './liuren-deterministic.mjs';
export const QUANTITY_COUPLING='liuren-strength-quantity-51';
export const QUANTITY_BANDS=Object.freeze({id:'quantity-band-experiment-51',reference:5,
 weak_end:2.5,neutral_start:4,neutral_end:6,strong_end:7.5,weak_factor:0.5,strong_factor:1.2,
 calibrated:false,predictive_validation_count:0});
const fail=m=>{throw Error('LIUREN_QUANTITY_ADJUSTMENT: '+m);};
const text=v=>typeof v==='string'&&!!v.trim()&&v.length<=4000;
const object=v=>v&&typeof v==='object'&&!Array.isArray(v);
function keys(v,allowed){if(!object(v)||Object.keys(v).some(k=>!allowed.includes(k)))fail('未知字段或缺少对象');}
const finite=v=>Number.isFinite(v)&&Math.abs(v)<=1e12;
const digest=v=>typeof v==='string'&&/^[a-f0-9]{64}$/.test(v);
export function quantityFactor(e){
 if(!Number.isFinite(e)||e<0||e>10)fail('须用真实不含空亡指数，范围0至10');
 return e<=2.5?0.5:e<4?0.5+(e-2.5)/3:e<=6?1:e<7.5?1+(e-6)*0.2/1.5:1.2;
}
export function quantityAdjustmentSchema(s){
 const t=s.string().min(1).max(4000),h=s.string().regex(/^[a-f0-9]{64}$/);
 return s.object({route:s.enum(['source','experimental']),target:t,
  base_receipt_sha256:h,strength_receipt_sha256:h,
  kind:s.enum(['amount','score','count','distance','weight','ordinal','date','identifier']),
  base_factors:s.object({qi:s.enum(['raw','source_adjusted']),void:s.boolean(),basis:t}).strict(),
  magnitude:s.object({exponent:s.number().int().min(-6).max(9),unit:s.string().min(1).max(40),basis:t,
   lower_bound:s.number().finite().min(0).optional(),upper_bound:s.number().finite().positive().optional()}).strict(),
  void:s.object({status:s.enum(['apply_half','already_in_base','not_applicable','exception']),basis:t,origin:s.enum(['source','user_research','model_estimate']).optional()}).strict(),
  rounding:s.object({decimals:s.number().int().min(0).max(6),basis:t}).strict().optional(),
  basis:t}).strict().describe('51版同任务数量兑现。quantity三选一：expression/quantity_method/quantity_adjustment。引用本任务回执；source不再叠强弱倍率，experimental用真实without_void指数固定分段。量级需独立依据，超界报错不截满分。序数日期编号不套分段或空半。须绑定51版新任务。');
}
export function adjustQuantity(c,q,{receipts=[]}={}){
 keys(q,['route','target','base_receipt_sha256','strength_receipt_sha256','kind','base_factors','magnitude','void','rounding','basis']);
 if(!['source','experimental'].includes(q.route)||!/^T:[子丑寅卯辰巳午未申酉戌亥]$/.test(q.target??'')||!text(q.basis)||!digest(q.base_receipt_sha256)||!digest(q.strength_receipt_sha256))fail('须明确路径、数量主类T:支、依据及真实回执hash；天将类须定位所乘支');
 const kinds=['amount','score','count','distance','weight','ordinal','date','identifier'];
 if(!kinds.includes(q.kind))fail('数量含义无效');
 keys(q.base_factors,['qi','void','basis']);
 if(!['raw','source_adjusted'].includes(q.base_factors.qi)||typeof q.base_factors.void!=='boolean'||!text(q.base_factors.basis))fail('须登记基数已含的气态及空减');
 keys(q.magnitude,['exponent','unit','basis','lower_bound','upper_bound']);
 const m=q.magnitude;
 if(!Number.isInteger(m.exponent)||m.exponent< -6||m.exponent>9||!text(m.unit)||m.unit.length>40||!text(m.basis))fail('须明确独立量级指数、单位及依据');
 if(m.lower_bound!==undefined&&(!finite(m.lower_bound)||m.lower_bound<0)||m.upper_bound!==undefined&&(!finite(m.upper_bound)||m.upper_bound<=0)||m.lower_bound!==undefined&&m.upper_bound!==undefined&&m.lower_bound>m.upper_bound)fail('现实上下限无效');
 keys(q.void,['status','basis','origin']);
 if(!['apply_half','already_in_base','not_applicable','exception'].includes(q.void.status)||!text(q.void.basis))fail('须明确空亡数量处理');
 if(q.void.origin!==undefined&&!['source','user_research','model_estimate'].includes(q.void.origin)||q.void.status==='apply_half'&&!q.void.origin)fail('实际折半须标明原法/项目研究/估计的来源身份');
 if(q.rounding!==undefined){keys(q.rounding,['decimals','basis']);if(!Number.isInteger(q.rounding.decimals)||q.rounding.decimals<0||q.rounding.decimals>6||!text(q.rounding.basis))fail('须说明舍入精度及依据');}
 const find=h=>receipts.find(r=>(r.ref?.sha256??r.receipt_sha256)===h);
 const base=find(q.base_receipt_sha256),strength=find(q.strength_receipt_sha256);
 if(!base||base.request?.action!=='quantity'||!finite(base.result?.value)||base.result.value<0)fail('基数须引用本任务真实quantity单一非负value');
 if(base.result.contract===QUANTITY_COUPLING)fail('不得以已兑现结果为新基数再次修正');
 if(base.result.chart_sha256&&base.result.chart_sha256!==hash(c))fail('具名基数不属于本盘');
 if(!strength||strength.request?.action!=='strength'||strength.result?.chart_sha256!==hash(c))fail('旺衰回执不属于本盘');
 const qb=strength.result.quantity_basis,row=qb?.rows?.find(a=>a.id===q.target);
 if(qb?.schema!=='liuren-quantity-strength-basis-v1'||qb.void_excluded_by_recomputation!==true||qb.baseline_reference!==5||!row)fail('须用含真实无空重算视图及数量主类的strength回执');
 if(base.request.quantity_method?.target&&base.request.quantity_method.target!==q.target)fail('基数主类与数量主类不一致');
 const included=base.result.calculation_scope?.included;
 const seasonalUsed=included?.seasonal_state!=null||included?.month_build_break_factor!=null;
 if(seasonalUsed&&q.base_factors.qi!=='source_adjusted')fail('具名数法已使用月令，不能声明为raw');
 if(q.route==='experimental'&&(q.base_factors.qi!=='raw'||q.base_factors.void))fail('实验分段只接受尚未使用气态及空减的本数；不得重复修正');
 if(q.route==='experimental'&&base.request.quantity_method)fail('实验路径须另取原始本数expression，不能改装具名源法结果');
 const ordinal=['ordinal','date','identifier'].includes(q.kind);
 if(ordinal&&(q.route==='experimental'||q.void.status==='apply_half'))fail('序数/日期/编号不作分段倍率或空亡折半');
 if(q.base_factors.void&&q.void.status!=='already_in_base')fail('基数已含空减，必须声明already_in_base且不得再扣');
 if(!q.base_factors.void&&q.void.status==='already_in_base')fail('already_in_base须与基数因素登记一致');
 if(q.void.status==='apply_half'&&!row.void_self)fail('仅数量主类本身旬空可采用本项折半；坐空/载体空不自动套用');
 if(row.void_self&&q.void.status==='not_applicable')fail('主类旬空须明确按阶段/专项例外处理，不能略过');
 let expression={value:base.result.value},value=base.result.value;const steps=[];
 function step(kind,op,operand,origin,basis){
  expression={op:op==='add'?'add':'multiply',args:[expression,{value:operand}]};
  value=calculate(expression).value;steps.push({kind,op,operand,origin,basis});
 }
 if(m.exponent!==0)step('other','multiply',10**m.exponent,'model_estimate',m.basis);
 const factor=q.route==='experimental'?Number(quantityFactor(row.without_void).toFixed(12)):1;
 if(factor!==1)step('qi','multiply',factor,'user_research','quantity-band-experiment-51；不含空亡指数='+row.without_void+'；未经预测校准');
 if(q.void.status==='apply_half')step('void','multiply',0.5,q.void.origin,q.void.basis);
 // Bounds are diagnostics, never a recipe for turning an implausible result
 // into a full mark by clamping. Check before AND after rounding.
 function bounds(v){if(m.lower_bound!==undefined&&v<m.lower_bound||m.upper_bound!==undefined&&v>m.upper_bound)fail('结果超出现实上下限，须复核取法/量级，不自动截断');}
 bounds(value);
 if(q.rounding){const rounded=Math.round(value*10**q.rounding.decimals)/10**q.rounding.decimals;
  if(rounded!==value){
   const difference={op:'subtract',args:[{value:rounded},expression]},operand=calculate(difference).value;
   // Keep the subtraction as exact rational arithmetic, rather than adding
   // a floating-point delta that would turn 39 into 38.99999999999999.
   expression={op:'add',args:[expression,difference]};value=calculate(expression).value;
   steps.push({kind:'rounding',op:'add',operand,origin:'model_estimate',basis:q.rounding.basis});
  }}
 bounds(value);
 const computed=calculate(expression),voidStatus={apply_half:'applied',already_in_base:'already_in_base',not_applicable:'not_applicable',exception:'exception'}[q.void.status];
 return {...computed,schema:'liuren-quantity-adjustment-v1',contract:QUANTITY_COUPLING,route:q.route,
  target:q.target,kind:q.kind,unit:m.unit,magnitude:m,base_factors:q.base_factors,
  strength_used:{scope:qb.scope,with_void:row.with_void,without_void:row.without_void,seasonal:row.seasonal,
   selected_actor_ids:strength.result.coverage?.actors??[],selected_relations:strength.result.applied_relations??[],
   baseline_reference:5,calibrated:false},
  ...(q.route==='experimental'?{experimental_profile:QUANTITY_BANDS}:{}),
  review:{route:q.route,status:steps.length?'adjusted':'base_retained',target:q.target,
   base_receipt_sha256:q.base_receipt_sha256,strength_receipt_sha256:q.strength_receipt_sha256,steps,
   qi_review:q.route==='source'?'按所选源法及基数因素执行；不再叠实验强弱倍率。'+q.base_factors.basis:
    '真实不含空亡指数='+row.without_void+'；实验强弱系数='+factor+'；量级另行说明，强不等于个人所得必多。',
   void_review:{status:voidStatus,basis:q.void.basis}},
  limits:['算术与回执可核；类神、关系有效性、数量口径与量级依据仍需专业核对。',
   '实验分段未经预测校准；0不自动表示事情失败，强旺不自动进十百；未计算合局数值。']};
}
