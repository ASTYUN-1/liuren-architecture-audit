// Review native Bifa candidates separately from chart facts and adjudication.
// The two source books define conditions; native titles do not decide outcomes.
import fs from 'node:fs/promises';
import path from 'node:path';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {isEntryPoint} from './liuren-direct.mjs';

const ROOT=fileURLToPath(new URL('../',import.meta.url));
const ZHI=[...'子丑寅卯辰巳午未申酉戌亥'];
const GENERALS=['贵人','腾蛇','朱雀','六合','勾陈','青龙','天空','白虎','太常','玄武','太阴','天后'];
const ELEMENT=Object.fromEntries([...['甲乙寅卯','丙丁巳午','戊己辰戌丑未','庚辛申酉','壬癸亥子'].entries()].flatMap(([i,s])=>[...s].map(v=>[v,['木','火','土','金','水'][i]])));
const BIRTH={木:'亥',火:'寅',土:'申',金:'巳',水:'申'};
const TOMB={木:'未',火:'戌',土:'辰',金:'丑',水:'辰'};
const he=(a,b)=>['子丑','寅亥','卯戌','辰酉','巳申','午未'].some(s=>s.includes(a)&&s.includes(b)&&a!==b);
const HOMES={甲:'寅',乙:'辰',丙:'巳',丁:'未',戊:'巳',己:'未',庚:'申',辛:'戌',壬:'亥',癸:'丑'};
const sheng=(a,b)=>ELEMENT[a]!==undefined&&['木火','火土','土金','金水','水木'].includes(ELEMENT[a]+ELEMENT[b]);
const ke=(a,b)=>ELEMENT[a]!==undefined&&['木土','土水','水火','火金','金木'].includes(ELEMENT[a]+ELEMENT[b]);
const hash=s=>createHash('sha256').update(s).digest('hex');
const horse=b=>['申子辰','寅午戌','巳酉丑','亥卯未'].map((s,i)=>s.includes(b)?['寅','申','亥','巳'][i]:null).find(Boolean);
const opposite=(a,b)=>ZHI.includes(a)&&ZHI.includes(b)&&(ZHI.indexOf(a)-ZHI.indexOf(b)+12)%12===6;
// The TXT contains CR-CR-LF. Match the registered universal-newline line numbers.
const norm=s=>s.replace(/^\uFEFF/,'').replaceAll('\r\n','\n').replaceAll('\r','\n');

export function parseLabel(raw) {
 const m=/^(\d+)\.([^\.]+)(?:\.(.*))?$/.exec(raw);
 if(!m)return {raw_label:raw,kind:'non_bifa_text',segments:[]};
 const segments=m[3]?.split('.')??[];
 return {raw_label:raw,kind:'candidate',law_number:Number(m[1]),title:m[2],segments,
  ...(m[1]==='4'&&m[2]==='贵人差迭事参差'?{label_error:'编号应属46，保留原标签，不按第4法使用'}:{}),
  ...(m[1]==='84'&&m[2]==='不传行者考初时'?{label_error:'编号与题名不符，不能按第84法使用'}:{})};
}

export function modeRequirement(label) {
 if(label.kind!=='candidate')return {kind:'not_applicable'};
 const detail=label.segments.join('.');
 // “害昼贵” names a noble branch. It is not automatically a daytime restriction.
 // The same applies to 昼夜 in the seven-character title of laws 44/45/49/50.
 if(label.law_number===43&&/^Ⅰ\.害[昼夜]贵$/.test(detail))return {kind:'referenced_noble',note:'昼/夜修饰被害的贵人支，不据此自动剔除另一昼夜盘；须核本法条件'};
 if(detail==='C.两面刀格.②昼将（夜将无)')return {kind:'explicit',required:'昼贵'};
 const hits=label.segments.filter(s=>/^[昼夜](?:(?:贵(?:在干[前后]|在六处|兼传鬼)?)|(?:虎(?:不临干)?)|常|玄|后|蛇|空)?$/.test(s));
 if(hits.length&&new Set(hits.map(s=>s[0])).size===1)return {kind:'explicit',required:hits[0][0]==='昼'?'昼贵':'夜贵'};
 if(/[昼夜]/.test(detail))return {kind:'unresolved_wording',note:'后缀含昼夜字样，但未登记其语义，不能靠关键词猜筛选条件'};
 return {kind:'unspecified',note:'没有显式昼夜限定；只保留候选，不等于已证昼夜均适用'};
}

export async function loadSources() {
 const registry=JSON.parse(await fs.readFile(new URL('./liuren-bifa-source-rules.json',import.meta.url),'utf8'));
 const results=await Promise.all(registry.sources.map(async s=>{
  try {
   const bytes=await fs.readFile(path.join(ROOT,s.path));
   const lines=norm(bytes.toString('utf8')).split('\n');
   return {...s,valid:hash(bytes)===s.sha256&&s.excerpts.every(e=>e.quote.trim().length>0&&lines.slice(e.line_start-1,e.line_end).join('\n')===e.quote)};
  } catch(error) {return {...s,valid:false,error:error.code??error.message};}
 }));
 return {valid:results.every(s=>s.valid),sources:results};
}

function semanticCheck(label,c) {
 const u=c.lessons.map(r=>r.tianpan),t=c.transmissions.map(r=>r.diZhi);
 const stem=c.pillars[2][0],branch=c.pillars[2][1],home=HOMES[stem];
 const rows=c.heaven_earth,at=b=>rows.find(r=>r.tian===b),on=g=>rows.find(r=>r.tianjiang===g);
 const used=new Set([...u,...t]);
 const checks=[];
 const add=(name,met,actual)=>{checks.push({condition:name,met:Boolean(met),actual});return Boolean(met);};
 const answer=(status,info,refs,extra={})=>({status,checks,adoptable_information:info,evidence_ids:refs,...extra});
 const all=()=>checks.every(r=>r.met);
 const raw=label.raw_label;
 if(raw==='02.首尾相见始终宜.B.回环格') {
  for(const [i,b]of t.entries())add(['初','中','末'][i]+'传在四课上神中',u.includes(b),b);
  return answer(all()?'structure_matched':'definition_not_met',all()?['三传不出四课上神的回环结构']:[],['D02','B02'],{unsupported_extensions:['未成回环时，不采用回环的拖拉、转圈及吉凶判辞'],missing_members:t.filter(b=>!u.includes(b))});
 }
 if(raw==='06.六阴相继尽昏迷.A.六阴格') {
  add('四课上神及三传均阴支',[...u,...t].every(b=>'丑卯巳未酉亥'.includes(b)),{lessons:u,transmissions:t});
  return answer(all()?'structure_matched':'definition_not_met',all()?['课传全阴结构']:[],['B06']);
 }
 if(raw==='22.上下皆合两心齐.B.上下俱合格') {
  add('日干寄宫与干上神六合（《大全》本类格）',he(home,u[0]),{home,upper:u[0]});
  add('日支与支上神六合（《大全》本类格）',he(branch,u[2]),{branch,upper:u[2]});
  return answer(all()?'structure_matched':'definition_not_met',all()?['干与自身上神合、支与自身上神合（《大全》上下俱合格）']:[],['D22'],{adopted_definition:'用户指定第22法以《大全》为准；此处仅实现B上下俱合格，其余分支不凭同名补全',unsupported_extensions:['不混入北海同名横向关系定义；六合关系不自动保证合作或婚姻成功']});
 }
 if(/^26\..*\.A\.财乘丁马格\.[①②]/.test(raw)) {
  const ding=raw.includes('①');
  const hits=rows.filter(r=>ke(stem,r.tian)&&(ding?r.xungan==='丁':r.tian===horse(branch)));
  add(ding?'日财旬遁丁':'日财兼日驿马',hits.length>0,hits.map(r=>r.tian));
  const visible=hits.filter(r=>used.has(r.tian));
  add('该支见四课上神或三传',visible.length>0,visible.map(r=>r.tian));
  const status=all()?'structure_matched':hits.length?'needs_context':'definition_not_met';
  return answer(status,all()?[ding?'财与旬丁同支':'财与日驿马同支']:[],['D26','B26'],{deduplicate_key:visible.map(r=>'财丁马:'+r.tian),unsupported_extensions:['非水日不套水日正格的全部财动结论；求财、妻财等含义依占类使用','未入课传时，不因缺年命资料而断永不成立']});
 }
 if(/^26\..*\.A\.财乘丁马格\.[③④]财乘日本/.test(raw)) {
  const birth=BIRTH[ELEMENT[stem]],carrier=on('太常');
  add('按《大全》本段五行长生取日本，太常乘之',carrier?.tian===birth,{japan:birth,carrier:carrier?.tian});
  const combo=all(),onDay=carrier?.di===home,onBranch=carrier?.di===branch;
  const requested=raw.includes('临干上')?'干':raw.includes('临支上')?'支':null;
  if(requested)add('日本太常临'+requested,requested==='干'?onDay:onBranch,carrier?.di);
  return answer(!all()?'definition_not_met':requested?'structure_matched':'relation_only',combo&&all()?['太常乘日本（《大全》本段五行长生口径）',...(onDay?['日本太常临干']:[]),...(onBranch?['日本太常临支']:[])]:[],['D26','B26'],{
   normalized_name:'太常乘日本',source_basis:'本段六己申为日本；不改现行己天干十二长生取酉',
   extensions:[{condition:'临干',met:onDay},{condition:'临支',met:onBranch}],
   unsupported_extensions:['宽泛④项不自动带有临干/临支断语','本盘无具体占事，不据该组合反推来意、婚喜、赏赐或实际得财','原标签的“财乘日本”不是本盘已出现财爻的证明']});
 }
 if(raw==='27.传财化鬼财休觅.Ⅱ.传脱') {
  const group=[['亥卯未','木'],['寅午戌','火'],['巳酉丑','金'],['申子辰','水']].find(([s])=>t.length===3&&new Set(t).size===3&&t.every(b=>s.includes(b)));
  add('三传成三合局',Boolean(group),group?.[0]??t);
  const example={木:'寅',火:'巳',金:'申',水:'亥'}[group?.[1]];
  add('日干生三传合局',example&&sheng(stem,example),group?.[1]);
  return answer(all()?'structure_matched':'definition_not_met',all()?['三传合局脱日干之气']:[],['D27','B27'],{unsupported_extensions:['传脱不等于传财化鬼；不套原文壬戌旁例的病症或结局']});
 }
 if(raw==='31.三传递生人举荐') {
  const forward=sheng(t[0],t[1])&&sheng(t[1],t[2]),reverse=sheng(t[2],t[1])&&sheng(t[1],t[0]);
  add('初生中、中生末，或末生中、中生初',forward||reverse,t);
  const endpoint=forward?t[2]:reverse?t[0]:null;
  return answer(all()?'structure_matched':'definition_not_met',all()?['三传'+(forward?'顺':'逆')+'递生']:[],['B31'],{endpoint,endpoint_relation:endpoint?(sheng(stem,endpoint)?'日干生终点，为脱气':sheng(endpoint,stem)?'终点生日干':ke(endpoint,stem)?'终点克日干':'另查'):null,unsupported_extensions:['不由“人举荐”直接断有人帮助或事成；须查事类、递生终点和空实']});
 }
 if(label.law_number===46&&/^[昼夜]贵在干[前后]$/.test(label.segments.join('.'))) {
  const general=c.lessons[0].tianjiang,j=GENERALS.indexOf(general);
  const actual=j>=1&&j<=5?'干后':j>=6?'干前':null;
  add('北海按干上将前五/后六核贵在干前后',actual!==null,{day_upper_general:general,derived_noble_position:actual});
  if(!actual)return answer('needs_context',[],['D46','B46']);
  const matches=raw.endsWith(actual);
  return answer(matches?'structure_matched':'engine_basis_unproven',matches?['贵在'+actual]:[],['D46','B46'],{source_supported_information:['按北海明示核法，本盘贵在'+actual],unsupported_extensions:['《大全》本段给判辞未明算法，未找到支持引擎另一算法的书证','不能称为已证两书算法冲突；不由前后关系自动推出贵人差迭正格']});
 }
 if(raw==='47.贵虽在狱宜临干') {
  const noble=on('贵人'),prison='辰戌'.includes(noble?.di??'!');
  add('贵人临地盘辰或戌',prison,noble?{tian:noble.tian,di:noble.di}:null);
  const body=prison&&['乙','辛'].includes(stem)&&noble.di===home,house=prison&&noble.di===branch;
  const kind=body?'贵人临身，不以入狱论':house?'贵人入宅，不以入狱论':'贵人入狱';
  return answer(prison?'branch_matched':'definition_not_met',prison?[kind]:[],['D47','B47'],{exceptions:[{condition:'贵临乙辛寄宫',met:body},{condition:'贵临辰戌日支',met:house}],unsupported_extensions:prison&&!body&&!house?['标题是全法索引，非“宜临干”特例成立；不作宜投贵、有利结论']:[]});
 }
 if(label.law_number===30&&raw.includes('.B.狮兽冲宅格.')) {
  const tiger=on('白虎');add('白虎乘神冲支上神',opposite(tiger?.tian,u[2]),{tiger:tiger?.tian,branch_upper:u[2]});
  return answer(all()?'structure_matched':'definition_not_met',all()?['虎冲支上神结构']:[],['D30','B30'],{unsupported_extensions:['无具体家宅资料，不由格名虚构道路、狮兽或实际灾祸']});
 }
 if((label.law_number===61&&raw.includes('.A.虎鬼加干格.'))||(label.law_number===91&&/^([昼夜])$/.test(label.segments.join('.')))) {
  add('干上神乘白虎',c.lessons[0].tianjiang==='白虎',c.lessons[0].tianjiang);
  add('干上神克日干',ke(u[0],stem),{upper:u[0],stem});
  return answer(all()?'structure_matched':'definition_not_met',all()?['虎鬼加干']:[],['D61','B61'],{deduplicate_key:['虎鬼加干:'+u[0]],unsupported_extensions:['虎鬼类格不等于墓虎正格；病凶、升迁速等按具体占类核用']});
 }
 if(['61.干乘墓虎无占病.昼虎','61.干乘墓虎无占病.昼虎不临干'].includes(raw)) {
  const tiger=on('白虎'),tomb=TOMB[ELEMENT[stem]],atDay=tiger?.di===home;
  add('白虎乘日干五行墓神',tiger?.tian===tomb,{tiger:tiger?.tian,tomb});
  const combo=all();
  if(raw.endsWith('不临干'))add('该墓虎不临日干寄宫',!atDay,{ground:tiger?.di,home});
  else add('该墓虎临日干寄宫，或须查年命成用',atDay,{ground:tiger?.di,home});
  return answer(all()?'structure_matched':combo&&!raw.endsWith('不临干')?'needs_context':'definition_not_met',all()?['墓虎'+(atDay?'加干':'不临干，年命等成用条件另查')]:[],['D61'],{observed_relationships:combo?['白虎乘墓神'+tomb,...(atDay?['墓虎加干']:[])]:[],unsupported_extensions:['阴干十二长生与本段五行墓口径须分开；不凭该标签判病死','未临干时年命可能成用，年命未提供不能默认完整格成立']});
 }
 if(label.law_number===69&&raw.includes('.A.明暗二鬼格.')) {
  const direct=raw.endsWith('干明支暗'),light=direct?u[0]:u[2],dark=at(direct?u[2]:u[0])?.xungan;
  add('所列明鬼克日干',ke(light,stem),light);add('所列暗鬼旬遁干克日干',ke(dark,stem),dark);
  return answer(all()?'structure_matched':'definition_not_met',all()?['干支上明暗二鬼关系']:[],['B69'],{unsupported_extensions:['不等于白虎乘遁鬼正格成立；实际作用另核坐空、旺衰、制救']});
 }
 return answer('not_reviewed',[],[],{unsupported_extensions:['本工具尚未定义此细分类格；不能因为昼夜通过便采用判辞']});
}

export function reviewCandidates(c,rawText,{sourcesValid=false}={}) {
 const mode=c.nobleman?.zhouye;
 if(!['昼贵','夜贵'].includes(mode))throw Error('缺实际昼夜设置，不能按时钟或标签猜定');
 if(!Array.isArray(c.lessons)||c.lessons.length!==4||!Array.isArray(c.transmissions)||c.transmissions.length!==3||c.heaven_earth?.length!==12)throw Error('需要正式完整AI盘');
 if(typeof rawText!=='string')throw Error('缺原始毕法文本，不补造候选');
 const rows=rawText.split(/\r?\n/).map(s=>s.trim()).filter(Boolean).map((raw,i)=>{
  const label=parseLabel(raw),mode_condition=modeRequirement(label);
  const base={index:i+1,...label,mode_condition,checks:[],adoptable_information:[],evidence_ids:[]};
  if(label.kind!=='candidate')return {...base,status:'non_bifa_text'};
  if(label.label_error)return {...base,status:'label_error'};
  if(mode_condition.kind==='explicit'&&mode_condition.required!==mode)return {...base,status:'excluded_other_mode',reason:'当前'+mode+'，此项限定'+mode_condition.required};
  if(mode_condition.kind==='unresolved_wording')return {...base,status:'mode_wording_unresolved'};
  if(!sourcesValid)return {...base,status:'source_validation_required'};
  return {...base,...semanticCheck(label,c)};
 });
 const counts={};for(const r of rows)counts[r.status]=(counts[r.status]??0)+1;
 return {schema:'liuren-bifa-candidate-review-v1',datetime:c.datetime,actual_mode:mode,source_validated:sourcesValid,
  summary:{raw_label_count:rows.length,distinct_law_count:new Set(rows.filter(r=>r.kind==='candidate').map(r=>r.law_number)).size,counts},
  rows,scope:'昼夜筛选及已登记类格的来源条件核查；输出结构关系，不裁现实吉凶、旺衰分值或成败',
  limitations:['无昼夜后缀只表示候选未限，不证明双模式均成立','只有adoptable_information中的已核信息可作结构材料；完整判辞须依具体占类、气态与制救再判断','未定义、书证变动或引擎算法无书证的原标签不自动通过','本工具为独立核查入口，尚未自动接入正式盘或裁决核心']};
}

// Search the adopted conditions independently of the native lookup. This also
// finds supported relations omitted from the engine's candidate list.
export const REGISTERED_SCAN_LABELS=[
 '02.首尾相见始终宜.B.回环格','06.六阴相继尽昏迷.A.六阴格',
 '22.上下皆合两心齐.B.上下俱合格',
 '26.水日逢丁财动之.A.财乘丁马格.①财乘丁',
 '26.水日逢丁财动之.A.财乘丁马格.②财乘驿马',
 '26.水日逢丁财动之.A.财乘丁马格.④财乘日本.昼常',
 '26.水日逢丁财动之.A.财乘丁马格.④财乘日本.夜常',
 '27.传财化鬼财休觅.Ⅱ.传脱','31.三传递生人举荐','47.贵虽在狱宜临干',
 ...['昼','夜'].flatMap(mode=>[
  '30.屋宅宽广致人衰.B.狮兽冲宅格.'+mode+'虎',
  '61.干乘墓虎无占病.A.虎鬼加干格.'+mode,
  '91.虎乘干鬼凶速速.'+mode]),
 '61.干乘墓虎无占病.昼虎',
 '69.虎乘遁鬼殃非浅.A.明暗二鬼格.干明支暗',
 '69.虎乘遁鬼殃非浅.A.明暗二鬼格.干暗支明'
];
export function scanRegistered(c,{sourcesValid=false}={}) {
 return reviewCandidates(c,REGISTERED_SCAN_LABELS.join('\n'),{sourcesValid});
}

const ADOPTABLE=new Set(['structure_matched','relation_only','branch_matched']);
export function buildAIHandoff(review,scan) {
 if(!review.source_validated||!scan?.source_validated)throw Error('未核书证不能生成AI采用材料');
 const rows=[...review.rows,...scan.rows],seen=new Set(),items=[];
 for(const r of rows) {
  if(!ADOPTABLE.has(r.status)||!r.adoptable_information?.length||seen.has(r.raw_label))continue;
  seen.add(r.raw_label);
  items.push({id:'BF'+String(items.length+1).padStart(3,'0'),law_number:r.law_number,
   branch:r.segments.join('.'),normalized_information:r.adoptable_information,
   origin:review.rows.some(n=>n.raw_label===r.raw_label)?'引擎候选经独立条件核验':'独立扫描已登记条件',
   checks:r.checks,evidence_ids:r.evidence_ids,deduplicate_key:r.deduplicate_key??[],
   limits:r.unsupported_extensions??[],...(r.source_basis?{source_basis:r.source_basis}:{}),
   ...(r.extensions?{extensions:r.extensions}:{}),...(r.endpoint_relation?{endpoint_relation:r.endpoint_relation}:{}),
   ...(r.exceptions?{exceptions:r.exceptions}:{})});
 }
 const evidenceIds=new Set(items.flatMap(r=>r.evidence_ids));
 const evidence=review.evidence?.filter(e=>evidenceIds.has(e.id))??[];
 if(evidence.length!==evidenceIds.size||evidence.some(e=>e.valid!==true))throw Error('AI材料缺完整有效来源证据');
 return {schema:'liuren-bifa-ai-material-v1',chart_binding:review.chart_binding,datetime:review.datetime,actual_mode:review.actual_mode,
  adopted_definitions:{law22:'依用户决定采用《六壬大全》，B上下俱合格按纵向两组六合核'},
  instruction:'以下仅为经来源条件核验的结构材料，不是本问结论。按占类、位置、旺衰空实和制救选用；不得从七言标题补出未满足条件或断语。相同deduplicate_key不作独立重复证据；完整盘仍用于查漏。未列出不等于本盘不存在该法。',
  coverage:{registered_scan_labels:REGISTERED_SCAN_LABELS.length,all_100_laws_reviewed:false,all_native_250_labels_reviewed:false},
  items,evidence,
  audit_summary:{statuses:review.summary.counts,rejected_or_pending_count:review.rows.filter(r=>!ADOPTABLE.has(r.status)).length,
   note:'原始错误、错模式和待核标签保存在独立audit，不作为AI已成格材料；需要争点时查原审计'},
  auto_attached_to_adjudicator:false};
}

export async function reviewResolvedFile(filename) {
 const resolved=JSON.parse(norm(await fs.readFile(filename,'utf8')));
 if(resolved.ok!==true||resolved.facts?.schema!=='liuren-ai-chart-v1'||!resolved.archive?.path||!resolved.archive?.sha256)throw Error('需要带原归档哈希的正式resolved-chart结果');
 const bytes=await fs.readFile(resolved.archive.path);
 if(hash(bytes)!==resolved.archive.sha256)throw Error('源归档哈希不符，停止采用原标签');
 const archive=JSON.parse(norm(bytes.toString('utf8'))),facts=resolved.facts,sourceFacts=archive._direct?.facts;
 if(!sourceFacts||sourceFacts.nobleman?.actual_zhouye!==facts.nobleman?.zhouye||JSON.stringify(sourceFacts.pillars)!==JSON.stringify(facts.pillars)||sourceFacts.month_general!==facts.month_general)throw Error('AI盘与源归档的柱、将或昼夜不一致');
 const geometry=x=>({lessons:x.lessons.map(l=>[l.tianpan,l.dizhi,l.tianjiang]),transmissions:x.transmissions.map(t=>[t.diZhi,t.tianjiang]),heaven_earth:x.heaven_earth.map(r=>[r.tian,r.di,r.tianjiang,r.xungan]).sort((a,b)=>ZHI.indexOf(a[0])-ZHI.indexOf(b[0]))});
 if(JSON.stringify(geometry(facts))!==JSON.stringify(geometry(sourceFacts)))throw Error('AI盘与源归档的四课、三传或天地盘不一致');
 const sources=await loadSources();
 const scan=scanRegistered(facts,{sourcesValid:sources.valid});
 return {...reviewCandidates(facts,archive.bifa,{sourcesValid:sources.valid}),archive:resolved.archive,
  chart_binding:{archive_sha256:resolved.archive.sha256,chart_geometry_sha256:hash(JSON.stringify(geometry(facts))),condition_implementation_sha256:hash(await fs.readFile(fileURLToPath(import.meta.url))),rule_registry_sha256:hash(await fs.readFile(new URL('./liuren-bifa-source-rules.json',import.meta.url)))},
  independent_scan:scan,
  source_validation:sources.sources.map(s=>({path:s.path,sha256:s.sha256,valid:s.valid})),
  evidence:sources.sources.flatMap(s=>s.excerpts.map(e=>({...e,path:s.path,sha256:s.sha256,valid:s.valid})))};
}

if(isEntryPoint(process.argv[1],import.meta.url)) {
 try {
  const args=process.argv.slice(2);
  const handoff=args.includes('--handoff'),rest=args.filter(a=>a!=='--handoff');
  if(rest[0]!=='--chart'||!rest[1]||![2,4].includes(rest.length)||(rest.length===4&&rest[2]!=='--out'))throw Error('用法：node tools/liuren-bifa-audit.mjs --chart 正式盘结果.json [--handoff] [--out 新文件.json]');
  const reviewed=await reviewResolvedFile(rest[1]),result=handoff?buildAIHandoff(reviewed,reviewed.independent_scan):reviewed,json=JSON.stringify(result,null,2)+'\n';
  if(rest[3]){await fs.writeFile(rest[3],json,{flag:'wx'});process.stdout.write(JSON.stringify({ok:true,out:path.resolve(rest[3]),...(result.summary??{items:result.items.length,coverage:result.coverage})})+'\n');}
  else process.stdout.write(json);
 } catch(error){process.stderr.write('LIUREN_BIFA_AUDIT_ERROR: '+error.message+'\n');process.exitCode=1;}
}
