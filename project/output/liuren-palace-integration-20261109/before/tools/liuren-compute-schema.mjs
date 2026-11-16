// One native schema for direct computation and packet calculation requests.
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
 const date=s.string().regex(/^\d{4}-\d{2}-\d{2}$/).describe('YYYY-MM-DD公历日期，1900至2100年；程序检查实际日期有效性');
 const calendar=s.object({
  start:date.describe('枚举起点，含当天。字段名start'),end:date.describe('枚举终点，含当天。单次最多732天'),
  timezone:s.literal('Asia/Shanghai').describe('必须显式填写Asia/Shanghai；不使用系统本地时区'),
  day_boundary:s.enum(['civil-midnight','zi-hour']).describe('必填字符串：civil-midnight=00:00换日；zi-hour=23:00换日。禁止midnight、00:00或对象'),
  branches:s.array(s.enum([...'子丑寅卯辰巳午未申酉戌亥'])).optional().describe('可选，按日支筛选；不指定则列全部日期'),
  pillars:s.array(s.string().regex(/^[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]$/)).optional().describe('可选，按完整日柱筛选，例如辛巳；程序再核六十甲子有效性'),
  hour:s.number().int().min(0).max(23).optional().describe('每日取样小时，默认12；23点结果须按显式换日口径解释'),
  minute:s.number().int().min(0).max(59).optional().describe('取样分钟，默认0')
 }).strict().describe(CALENDAR_HELP);
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
  s.object({id:s.string().regex(/^C_[A-Za-z0-9_-]+$/),action:s.literal('quantity'),expression}).strict()
 ]);
 const args={
  action:s.enum(['chart','lookup','calendar','quantity','life','source']).describe('calendar必须给calendar对象；quantity必须给expression；source给source；lookup给lookup；life给life'),
  archive:archiveReferenceSchema(s).optional().describe('主智能体action=chart/lookup/life条件必填：可原样复用liuren_chart.archive（含可选raw_sha256），也可只给path/sha256。文件及可选原始hash均核对。life需要课盘给行年上神/阴神；裁决者自动用绑定盘，不传archive。calendar/quantity/source不传此字段'),
  symbols:s.array(s.string()).optional(),
  lookup:s.object({subject:s.string(),place:s.string().optional(),reference:s.string().optional(),profile:s.enum(['four-seasons','quarter-earth']).optional()}).strict().optional(),
  calendar:calendar.optional(),expression:expression.optional(),
  life:s.object({age:s.number().int(),sex:s.enum(['男','女']),age_basis:s.literal('虚岁-已核'),birth_pillar:s.string().optional()}).strict().optional(),
  source:s.object({id:s.string(),title:s.string(),source_path:s.string().describe(SOURCE_HELP),line_start:s.number().int().min(1).optional(),line_end:s.number().int().min(1).optional(),line_mode:s.enum(['lf','universal']).optional(),sha256:s.string().optional()}).strict().optional().describe(SOURCE_HELP)
 };
 const schema=s.object({...args,expression:runtimeExpression.optional()}).strict().superRefine((v,ctx)=>{
  const key={calendar:'calendar',quantity:'expression',lookup:'lookup',life:'life',source:'source'}[v.action];
  if(key&&v[key]===undefined)ctx.addIssue({code:'custom',path:[key],message:'action='+v.action+' requires '+key});
  for(const candidate of ['calendar','expression','lookup','life','source','symbols']){
   if(v[candidate]!==undefined&&candidate!==(v.action==='chart'?'symbols':key))ctx.addIssue({code:'custom',path:[candidate],message:'field is not used by action='+v.action+'; remove it rather than silently ignoring it'});
  }
  if(v.archive!==undefined&&!['chart','lookup','life'].includes(v.action))ctx.addIssue({code:'custom',path:['archive'],message:'archive is only used by chart/lookup/life'});
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
