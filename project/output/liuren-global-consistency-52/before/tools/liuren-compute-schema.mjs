// One native schema for direct computation and packet calculation requests.
import {quantityAdjustmentSchema} from './liuren-quantity-adjustment.mjs';
// Receives the host SDK's Zod instance; does not load a second SDK/runtime.
export const CALENDAR_EXAMPLE={action:'calendar',calendar:{start:'2024-01-15',end:'2024-02-05',timezone:'Asia/Shanghai',day_boundary:'civil-midnight'}};
export const SOURCE_HELP='优先原样复制liuren_materials返回的handoff对象；也可复制liuren_compute(action="source")返回的引用字段。source_path接受工作区相对路径或同一工作区内的绝对路径，程序统一为相对路径；仅允许当前runtime、书籍库/、books/和已登记应期资料，不接受旧runtime、案例/经验库或任意output。当前runtime方法给id/title/source_path和已知sha256，省略quote及行界可装完整原文；书籍必须给准确line_start/line_end/line_mode及已知sha256。缺引用时从已返回元数据取值，不猜路径/hash/行号。';
export const CALENDAR_HELP='calendar须含start、end（YYYY-MM-DD）、timezone="Asia/Shanghai"、day_boundary="civil-midnight"（00:00换日）或"zi-hour"（23:00换日）。day_boundary是枚举字符串，不是"midnight"、"00:00"或对象。最小调用：'+JSON.stringify(CALENDAR_EXAMPLE)+'。示例日期只示范结构，实际范围按本问确定。按字段错误更正，不猜参数、不手算公历代替程序。';

// Both callers can copy the chart tool's complete archive reference unchanged.
// sha256 authenticates the file; raw_sha256 is optional provenance checked against it.
export function archiveReferenceSchema(s){
 const digest=s.string().regex(/^[a-f0-9]{64}$/);
 return s.object({path:s.string(),sha256:digest,raw_sha256:digest.optional()}).strict();
}

export function createComputeSchemas(s){
 const quantityAdjustment=quantityAdjustmentSchema(s);
 const actor=s.object({id:s.string().describe('本盘T:支、J:天将或S:本日日干'),role:s.string().min(1).max(1500),basis:s.string().min(1).max(1500)}).strict();
 const strength=s.object({mode:s.enum(['single_palace','selected_relations']),season_profile:s.enum(['four-seasons','quarter-earth']),season_basis:s.string().min(1).max(1500),
   actors:s.array(actor).min(1).max(25),links:s.array(s.object({source:s.string(),target:s.string(),basis:s.string().min(1).max(1500)}).strict()).max(30).optional(),
   review:s.boolean().optional().describe('按需核已取用对象的状态依据、彼此关系事实和季土双表差异；不自动新增作用，不验证专业取用，不改系数')}).strict()
  .describe('单宫旺衰或取用后补算。actors明确类神身份与取用依据；links只提交经原法确定适用的跨宫作用。返回quantity_basis含同范围真实不含空亡重算，不能用含空分数倒除。原直接关系不重复计分，不接受手填分数/倍率。季月不按结果换表。');
 const date=s.string().regex(/^\d{4}-\d{2}-\d{2}$/).describe('YYYY-MM-DD公历日期，1900至2100年；程序检查实际日期有效性');
 const calendar=s.object({
  start:date.describe('枚举起点，含当天。字段名start'),end:date.describe('枚举终点，含当天。单次最多732天'),
  timezone:s.literal('Asia/Shanghai').describe('必须显式填写Asia/Shanghai；不使用系统本地时区'),
  day_boundary:s.enum(['civil-midnight','zi-hour']).describe('必填字符串：civil-midnight=00:00换日；zi-hour=23:00换日。禁止midnight、00:00或对象'),
  branches:s.array(s.enum([...'子丑寅卯辰巳午未申酉戌亥'])).optional().describe('可选，按日支筛选；不指定则列全部日期'),
  pillars:s.array(s.string().regex(/^[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]$/)).optional().describe('可选，按完整日柱筛选，例如辛巳；程序再核六十甲子有效性'),
  hour:s.number().int().min(0).max(23).optional().describe('每日取样小时，默认12；23点结果须按显式换日口径解释'),
  minute:s.number().int().min(0).max(59).optional().describe('取样分钟，默认0'),
  mode:s.enum(['dates','boundaries']).optional().describe('默认dates；boundaries查询节气/节月/旬界/日界准确时刻'),
  boundary_types:s.array(s.enum(['节气','节月','旬界','日界'])).min(1).optional(),
  sample_minutes:s.number().int().min(1).max(1440).optional().describe('按此分钟步长取全天样本；不与hour/minute混用；最多10000样本'),
  match:s.object({target:s.enum([...'子丑寅卯辰巳午未申酉戌亥']),relation:s.enum(['值','冲','六合']),axis:s.enum(['day','hour']).optional()}).strict().optional(),
  origin:s.string().regex(/^\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}(?::\d{2})?)?$/).optional().describe('原占日期或北京时间本地时刻YYYY-MM-DDTHH:mm[:ss]；只给日期时取午时；与day_boundary共用口径'),
  origin_state:s.enum(['inside','outside']).optional().describe('需origin；筛选是否处于原来那一次十日旬，非仅比较旬名')
 }).strict().describe(CALENDAR_HELP);
 const quantityMethod=s.object({id:s.string(),target:s.string(),basis:s.string().min(1).max(1500),
  season_profile:s.enum(['four-seasons','quarter-earth']).optional(),number_table:s.enum(['branch','sheng','cheng']).optional(),unit:s.string().min(1).max(40).optional()}).strict()
  .describe('先action=methods,methods={kind:"quantity"}查方法。id绑定原段，不自由拼系数；target=T:支。CY501-use-ground、WY244-month为初传分支；WY67/WY242仅基础步；LF3329-class-ground为选定类神与地盘分支。旺衰读取月令五气，非综合指数。calculation_scope说明未执行的空亡数量修正；有据修正另次expression，不以指数计空冒充数量已修正。');
 const imagery=s.object({id:s.string(),target:s.string(),basis:s.string().min(1).max(1500),season_profile:s.enum(['four-seasons','quarter-earth']).optional(),reference:s.enum(['ground','yin']).optional()}).strict();
 const methods=s.object({kind:s.enum(['quantity','imagery']),id:s.string().optional()}).strict();
 const evaluation=s.object({calendar,strength,void_policy:s.enum(['original','evaluation-xun-research']).optional()}).strict()
  .describe('批量时间情景，最多128个匹配时刻。默认保留原空亡；新旬替换仅研究情景，不等同冲实/填实。原盘位置及日干固定。');
 const atom=s.object({value:s.number().finite().min(-1e12).max(1e12)}).strict();
 const table=s.object({table:s.enum(['branch','stem','sheng','cheng']),symbol:s.string().min(1).max(4)}).strict();
 // OpenCode 1.18.29 rebuilds the root object from its properties, losing $defs.
 // Keep recursion exclusively in execution validation; publish a reference-free
 // node contract whose children are objects of the same documented shape.
 const ops=()=>s.enum(['add','subtract','multiply','divide']);
 const expression=s.union([atom,table,s.object({op:ops(),args:s.array(s.record(s.string(),s.unknown())).min(2).max(20)}).strict()])
  .describe('算式节点三选一：{value:6}；{table:"branch",symbol:"丑"}；{op:"multiply",args:[{table:"branch",symbol:"丑"},{value:6}]}。args每项仍按这三种节点格式，可继续嵌套；程序逐层严格校验，限制深度12/节点100。无统一天将数表，不猜腾蛇数。');
 const runtimeExpression=s.lazy(()=>s.union([atom,table,s.object({op:ops(),args:s.array(runtimeExpression).min(2).max(20)}).strict()]));
 const computation=s.discriminatedUnion('action',[
  s.object({id:s.string().regex(/^C_[A-Za-z0-9_-]+$/),action:s.literal('calendar'),calendar}).strict(),
  s.object({id:s.string().regex(/^C_[A-Za-z0-9_-]+$/),action:s.literal('quantity'),expression:expression.optional(),quantity_method:quantityMethod.optional()}).strict()
 ]);
 const args={
  action:s.enum(['chart','lookup','calendar','quantity','life','source','strength','methods','imagery','evaluation']).describe('quantity给expression/quantity_method/quantity_adjustment三选一；后者仅51版绑定任务，引用本任务真实基数与旺衰回执。其余同名对象'),
  archive:archiveReferenceSchema(s).optional().describe('主智能体chart/lookup/life/strength/imagery/evaluation及quantity_method须带liuren_chart.archive；裁决者自动绑定盘。calendar、methods、纯expression无须归档。完整archive含可选raw_sha256可原样复用。'),
  symbols:s.array(s.string()).optional(),strength:strength.optional(),quantity_method:quantityMethod.optional(),quantity_adjustment:quantityAdjustment.optional(),imagery:imagery.optional(),methods:methods.optional(),evaluation:evaluation.optional(),
  lookup:s.object({subject:s.string(),place:s.string().optional(),reference:s.string().optional(),profile:s.enum(['four-seasons','quarter-earth']).optional()}).strict().optional(),
  calendar:calendar.optional(),expression:expression.optional(),
  life:s.object({age:s.number().int(),sex:s.enum(['男','女']),age_basis:s.literal('虚岁-已核'),birth_pillar:s.string().optional()}).strict().optional(),
  source:s.object({id:s.string(),title:s.string(),source_path:s.string().describe(SOURCE_HELP),line_start:s.number().int().min(1).optional(),line_end:s.number().int().min(1).optional(),line_mode:s.enum(['lf','universal']).optional(),sha256:s.string().optional()}).strict().optional().describe(SOURCE_HELP)
 };
 const schema=s.object({...args,expression:runtimeExpression.optional()}).strict().superRefine((v,ctx)=>{
  const key={calendar:'calendar',quantity:v.quantity_adjustment?'quantity_adjustment':v.quantity_method?'quantity_method':'expression',lookup:'lookup',life:'life',source:'source',strength:'strength',methods:'methods',imagery:'imagery',evaluation:'evaluation'}[v.action];
  if(key&&v[key]===undefined)ctx.addIssue({code:'custom',path:[key],message:'action='+v.action+' requires '+key});
  for(const candidate of ['calendar','expression','lookup','life','source','symbols','strength','quantity_method','quantity_adjustment','imagery','methods','evaluation']){
   if(v[candidate]!==undefined&&candidate!==(v.action==='chart'?'symbols':key))ctx.addIssue({code:'custom',path:[candidate],message:'field is not used by action='+v.action+'; remove it rather than silently ignoring it'});
  }
  if(v.archive!==undefined&&!(['chart','lookup','life','strength','imagery','evaluation'].includes(v.action)||v.action==='quantity'&&v.quantity_method))ctx.addIssue({code:'custom',path:['archive'],message:'archive is only used by chart-bound actions including quantity_method'});
 });
 const parse=request=>{
  const result=schema.safeParse(request);
  if(!result.success){
   const issues=result.error.issues.slice(0,6).map(e=>(e.path.join('.')||'request')+': '+e.message).join('; ');
   throw new Error('LIUREN_COMPUTE_ARGUMENTS: '+issues+(request?.action==='calendar'?'\n'+CALENDAR_HELP:''));
  }
  return result.data;
 };
 return {calendar,expression,computation,args,parse};
}
