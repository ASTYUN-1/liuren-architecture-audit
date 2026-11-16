// Input adoption, cyclic arithmetic and chart coordinates only; no adjudication.
const ZHI=[...'子丑寅卯辰巳午未申酉戌亥'],GAN=[...'甲乙丙丁戊己庚辛壬癸'];
const JIAZI=Array.from({length:60},(_,i)=>GAN[i%10]+ZHI[i%12]);
const mod=(n,m)=>((n%m)+m)%m;
const fail=message=>{throw Object.assign(new Error('LIUREN_YEAR_LIFE: '+message),{code:'INVALID_YEAR_LIFE'});};
export const YEAR_LIFE_METHOD='liuren-year-life-v1';
export const LIFE_INPUT_FIELDS=['sex','birth_year','birth_pillar','birth_branch','xingnian','xingnian_branch','age','age_basis'];
export function lifeInputSchema(s){
 return s.object({sex:s.enum(['男','女']).optional(),
  birth_year:s.union([s.number().int(),s.string()]).optional().describe('出生年份2005、05、99均可，无需出生月日；05按2005，99按1999（日期盘以占年展开最近过去世纪）。'),
  birth_pillar:s.string().optional().describe('用户明确本命：甲子或申，单支足够，不猜出生年份或天干。'),
  birth_branch:s.string().optional(),xingnian:s.string().optional().describe('用户明确行年，地支或完整干支，直接采用。'),xingnian_branch:s.string().optional(),
  age:s.number().int().min(0).max(150).optional().describe('若为虚岁另给age_basis；不带口径时只保留旧引擎age，出生年份优先用birth_year。'),
  age_basis:s.enum(['虚岁','虚岁-已核']).optional()}).strict();
}
function symbol(value,key){
 if(typeof value!=='string')fail(key+'须为本命/行年地支或有效六十甲子');
 const s=value.trim().replace(/[年命]$/u,'');
 if(!ZHI.includes(s)&&!JIAZI.includes(s))fail(key+'须为单地支或有效六十甲子，例如申、甲子');
 return s;
}
export function normalizeLifeInput(value,{allowPartial=false}={}){
 if(!value||typeof value!=='object'||Array.isArray(value))fail('年命参数须为对象');
 const r={...value};
 if(r.sex!==undefined&&!['男','女'].includes(r.sex))fail('sex须为男或女');
 for(const k of ['birth_pillar','birth_branch','xingnian','xingnian_branch'])if(r[k]!==undefined){
  r[k]=symbol(r[k],k);if(k.endsWith('_branch')&&!ZHI.includes(r[k]))fail(k+'须为单地支');
 }
 if(r.birth_year!==undefined){
  const s=String(r.birth_year).trim().replace(/年(?:出生|生)?$/u,'');
  if(!/^\d{1,2}$|^(?:19|20)\d{2}$|^2100$/.test(s))fail('birth_year须为1900—2100年份或00—99简写，例如2005、05、99');
  r.birth_year=s.length<=2?s.padStart(2,'0'):Number(s);
 }
 if(r.age!==undefined&&(!Number.isInteger(r.age)||r.age<0||r.age>150))fail('age须为0—150整数');
 if(r.age_basis!==undefined&&!['虚岁','虚岁-已核'].includes(r.age_basis))fail('age_basis须为虚岁或虚岁-已核');
 if(r.age_basis&&(!r.age||r.age<1))fail('虚岁须为1—150整数');
 if(!['birth_year','birth_pillar','birth_branch','xingnian','xingnian_branch','age'].some(k=>r[k]!==undefined)&&!(allowPartial&&r.sex))fail('至少提供出生年、本命、行年或年龄一项');
 return r;
}
function birthYear(value,chart){
 if(value===undefined)return null;
 const s=String(value),absolute=/^(\d{4})-/.exec(chart.event_datetime??'');
 if(s.length>2){const year=Number(s);if(absolute&&year>Number(absolute[1]))fail('出生年晚于占课公历年');return {year,rule:'用户四位出生年'};}
 const yy=Number(s);
 // No wall-clock dependency: a dated chart uses its own Gregorian year.
 const anchor=absolute?Number(absolute[1]):null;
 const year=anchor===null?(yy<50?2000:1900)+yy:Math.floor(anchor/100)*100+yy-(yy>anchor%100?100:0);
 return {year,rule:anchor===null?'四柱无公历占年：00—49按2000—2049，50—99按1950—1999':'以占课公历年展开为最近不晚于占年的同尾数年份'};
}
function position(chart,b){
 const row=chart.heaven_earth?.find(r=>r.di===b),yin=chart.heaven_earth?.find(r=>r.di===row?.tian);
 if(!row||!yin)fail('可信盘缺少年命宫或其直接阴神坐标');
 return {earth_branch:b,upper_branch:row.tian,upper_general:row.tianjiang,direct_yin_branch:yin.tian,direct_yin_general:yin.tianjiang};
}
function lifeSymbol(s,source,chart){return {branch:s.at(-1),...(s.length===2?{pillar:s}:{}),source,eligible_as_input:true,position:position(chart,s.at(-1))};}
function calculatedXingnian(birth,sex,year,chart){
 const full=!!birth.pillar,m=full?60:12;
 const offset=mod((full?JIAZI.indexOf(year):ZHI.indexOf(year[1]))-(full?JIAZI.indexOf(birth.pillar):ZHI.indexOf(birth.branch)),m);
 const n=mod(sex==='男'?2+offset:8-offset,m),s=full?JIAZI[n]:ZHI[n];
 return {...lifeSymbol(s,'工具按本命及占课年柱计算',chart),sex,calculation:{cycle:m,offset,rule:sex==='男'?'一岁丙寅顺行':'一岁壬申逆行'}};
}
export function resolveLife(value,chart){
 const input=normalizeLifeInput(value),year=chart.pillars?.[0]??chart.year_pillar;
 if(!JIAZI.includes(year))fail('可信盘缺少有效占课年柱；不使用主机时间或显示参考日期替代');
 const conflicts=[],notes=[],by=birthYear(input.birth_year,chart);
 const declaredBirth=input.birth_pillar??input.birth_branch;
 const fromYear=by?JIAZI[mod(by.year-4,60)]:null;
 let birth=declaredBirth?lifeSymbol(declaredBirth,'用户明确提供',chart):fromYear?lifeSymbol(fromYear,'工具按出生年换算（整年默认）',chart):null;
 if(input.birth_pillar&&input.birth_branch&&input.birth_pillar.at(-1)!==input.birth_branch)conflicts.push({field:'birth_branch',adopted:input.birth_pillar,other:input.birth_branch});
 if(declaredBirth&&fromYear&&declaredBirth!==(declaredBirth.length===2?fromYear:fromYear[1]))conflicts.push({field:'birth_year',adopted:declaredBirth,other:fromYear,note:'采用明确本命；不因缺生日弃用。年界差异只在本冲突局部保留。'});
 if(by)notes.push(by.rule+'；出生年按该公历编号常用干支整年映射，无需出生月日；明确本命优先。');
 const statedX=input.xingnian??input.xingnian_branch;
 let xingnian=statedX?lifeSymbol(statedX,'用户明确提供',chart):null;
 if(input.xingnian&&input.xingnian_branch&&input.xingnian.at(-1)!==input.xingnian_branch)conflicts.push({field:'xingnian_branch',adopted:input.xingnian,other:input.xingnian_branch});
 const nominal=input.age!==undefined&&input.age_basis!==undefined;
 const fromAge=sex=>lifeSymbol(JIAZI[mod(sex==='男'?2+input.age-1:8-input.age+1,60)],'工具按用户虚岁计算',chart);
 // A directly stated xingnian is reversible without knowing an absolute birth year.
 const reverse=sex=>{
  const full=!!xingnian.pillar,m=full?60:12;
  const x=full?JIAZI.indexOf(xingnian.pillar):ZHI.indexOf(xingnian.branch);
  const offset=mod(sex==='男'?x-2:8-x,m);
  const y=full?JIAZI.indexOf(year):ZHI.indexOf(year[1]);
  return {...lifeSymbol(full?JIAZI[mod(y-offset,m)]:ZHI[mod(y-offset,m)],'工具按明确行年、性别及占课年柱反推',chart),sex};
 };
 let birth_candidates,xingnian_candidates;
 if(!birth&&xingnian){if(input.sex)birth=reverse(input.sex);else birth_candidates=['男','女'].map(reverse);}
 if(!birth&&nominal){
  birth=lifeSymbol(JIAZI[mod(JIAZI.indexOf(year)-(input.age-1),60)],'工具按用户虚岁及占课年柱计算',chart);
 }
 const expected=sex=>birth?calculatedXingnian(birth,sex,year,chart):nominal?{...fromAge(sex),sex}:null;
 if(input.sex){
  const e=expected(input.sex);
  if(!xingnian)xingnian=e;
  else if(e&&(xingnian.branch!==e.branch||xingnian.pillar&&e.pillar&&xingnian.pillar!==e.pillar))conflicts.push({field:'xingnian',adopted:xingnian.pillar??xingnian.branch,calculated:e.pillar??e.branch,note:'明确行年直接采用；保留差异供针对性核对，不覆盖或停用年命。'});
  if(nominal&&e&&fromAge(input.sex).branch!==e.branch)conflicts.push({field:'age',adopted:birth?.pillar??birth?.branch,other:input.age,note:'本命优先，年龄差异只标记本字段。'});
 }else if(!xingnian&&(birth||nominal))xingnian_candidates=['男','女'].map(expected);
 const missing=[];if(!input.sex&&(xingnian_candidates||birth_candidates))missing.push('sex');
 if(input.age!==undefined&&!nominal&&!birth&&!xingnian)missing.push('age_basis（如为虚岁，请明确传虚岁；旧原工具age不直接冒充虚岁）');
 return {schema:YEAR_LIFE_METHOD,input,year_pillar:year,year_source:'chart.pillars[0]',
  ...(by?{birth_year:by.year,birth_year_rule:by.rule}:{}),...(input.sex?{sex:input.sex}:{}),
  ...(nominal?{age:input.age,age_basis:input.age_basis}:{}),
  birth,xingnian,...(birth_candidates?{birth_candidates}:{}),...(xingnian_candidates?{xingnian_candidates}:{}),
  adopted:!!(birth||xingnian),missing,conflicts,notes,
  method:'本命取生年支；男一岁丙寅顺、女一岁壬申逆。只知本命支按12支循环；知本命干支按60甲子循环，不倒造唯一出生年或年龄。'};
}
export function resolveChartLife(input,chart){
 const people=input?.participants??[],declared=input?.declared_life??[];
 const participants=Array.from({length:Math.max(people.length,declared.length)},(_,i)=>{
  const a=people[i]??{},b=declared[i]??{},merged={};
  for(const k of LIFE_INPUT_FIELDS)if(b[k]!==undefined||a[k]!==undefined)merged[k]=b[k]??a[k];
  const r=resolveLife(merged,chart);
  if(a.sex&&b.sex&&a.sex!==b.sex)r.conflicts.push({field:'sex',adopted:b.sex,other:a.sex});
  return {id:'P'+(i+1),name:'参与者'+(i+1),...r};
 });
 return {schema:YEAR_LIFE_METHOD,participants};
}
// Flat compatibility fields for existing compute callers, with the full new receipt.
export function computeLife(input,chart){
 const r=resolveLife(input,chart),at=b=>chart.heaven_earth.find(p=>p.di===b);
 return {...r,...(r.xingnian?{xingnian_detail:r.xingnian,xingnian:r.xingnian.pillar??r.xingnian.branch,upper:at(r.xingnian.branch),direct_yin:r.xingnian.position.direct_yin_branch}:{}),
  ...(r.birth?{life_branch:r.birth.branch,life_upper:at(r.birth.branch),...(input.birth_pillar?.length===2?{declared_birth_pillar:input.birth_pillar}:{})}:{}),
  limits:['用户信息直接采用；计算及坐标可核，不等于预测结论。']};
}
