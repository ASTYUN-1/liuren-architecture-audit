// Deterministic selection layer. Never mutates a chart or predicts outcomes.
import fs from 'node:fs/promises';
import { isEntryPoint } from './liuren-direct.mjs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { correctEngineShensha, correctedRawExport } from './liuren-engine-shensha.mjs';

const ROOT = fileURLToPath(new URL('../', import.meta.url));
const ZHI = [...'子丑寅卯辰巳午未申酉戌亥'];
const GAN = [...'甲乙丙丁戊己庚辛壬癸'];
const GENERALS = ['贵人','腾蛇','朱雀','六合','勾陈','青龙','天空','白虎','太常','玄武','太阴','天后'];
const hash = b => crypto.createHash('sha256').update(b).digest('hex');
const readJSON = async p => JSON.parse((await fs.readFile(p, 'utf8')).replace(/^\uFEFF/, ''));
const mod = n => (n % 12 + 12) % 12;
const ascii = v => JSON.stringify(v).replace(/[\u007f-\uffff]/g, c => '\\u'+c.charCodeAt(0).toString(16).padStart(4,'0'));

export async function loadShenshaPolicy(root = ROOT) {
  const pointer = await readJSON(path.join(root,'.opencode/liuren-active.json'));
  const runtime = path.resolve(root,pointer.runtime);
  if (!runtime.startsWith(path.resolve(root)+path.sep)) throw new Error('神煞运行包超出项目');
  const manifest = await readJSON(path.join(runtime,'manifest.json'));
  if (manifest.release !== pointer.release || manifest.version !== pointer.methodVersion) throw new Error('神煞活动指针不一致');
  const serialized = '{'+Object.keys(manifest.files).sort().map(k=>ascii(k)+': '+ascii(manifest.files[k])).join(', ')+'}';
  if (hash(serialized)!==manifest.version) throw new Error('神煞清单身份不一致');
  const rel = manifest.shenshaPolicyFile;
  if (!rel) throw new Error('当前运行包没有确定的神煞采用表；不可回退使用未核引擎标签');
  const target = path.resolve(runtime,rel);
  if (!target.startsWith(runtime+path.sep)) throw new Error('神煞表路径越界');
  const bytes = await fs.readFile(target);
  if (hash(bytes)!==manifest.files[rel]) throw new Error('神煞采用表哈希不一致');
  const policy = JSON.parse(bytes.toString('utf8'));
  if (policy.schema!=='liuren-shensha-policy-v1') throw new Error('神煞表格式不支持：'+String(policy.schema));
  if (policy.release!==pointer.release) throw new Error(
    '神煞表版本不一致：活动='+pointer.release+'，采用表='+String(policy.release)+'；配置故障，重复起课无效');
  return {policy,sha256:hash(bytes)};
}

// Both public chart routes preflight before engine/archive side effects.
// One policy snapshot is used throughout a request, including its saved export.
export async function runChartWithShensha(createResult, {persist=true, policyRoot=ROOT}={}) {
  const loadedPolicy=await loadShenshaPolicy(policyRoot);
  return enrichChartResult(await createResult(), {persist, loadedPolicy});
}

export function factsForShensha(record) {
  if (!record || typeof record!=='object' || Array.isArray(record)) throw new Error('需要完整课盘 JSON');
  if (record.validation?.ok===false || record._direct?.validation?.ok===false) throw new Error('原课盘验证未通过，不能采用其神煞');
  if (record._direct?.facts) return record._direct.facts;
  if (record.facts) return record.facts;
  if (record.schema==='liuren-chart-facts-v1') return record;
  // Older native exports lack _direct. Read their own pillars/settings only.
  if (Array.isArray(record.basic?.pillars) && Array.isArray(record.tiandipan)) {
    const p=record.basic.pillars, settings=record.basic.settings||{};
    let actual=settings.zhouye;
    if (actual==='自动选择' && ZHI.includes(p[3]?.[1])) actual=[...'卯辰巳午未申'].includes(p[3][1])?'昼贵':'夜贵';
    return {schema:'liuren-chart-facts-v1',pillars:p,year_pillar:p[0],month_pillar:p[1],day_pillar:p[2],
      day_stem:p[2]?.[0],day_branch:p[2]?.[1],month_branch:p[1]?.[1],xun:record.basic.xun,
      void_branches:record.basic.xunkong,heaven_earth:record.tiandipan,
      nobleman:{rule:settings.guiren,actual_zhouye:actual}};
  }
  throw new Error('没有可核的完整课盘字段；不从报告文字猜测或重新起课');
}

export function resolveShensha(facts, policy, policySha256 = null) {
  if (!facts || typeof facts!=='object' || Array.isArray(facts)) throw new Error('缺少课盘 facts');
  const input={},problems={},rows=Array.isArray(facts.heaven_earth)?facts.heaven_earth:[];
  function reference(key, explicit, derived, alphabet) {
    const present=v=>v!==undefined && v!==null && v!=='';
    if (present(explicit) && !alphabet.includes(explicit)) problems[key]='参数不合法';
    else if (present(explicit) && present(derived) && explicit!==derived) problems[key]='字段与四柱矛盾';
    else if (present(derived) && !alphabet.includes(derived)) problems[key]='四柱字段不合法';
    input[key]=present(explicit)?explicit:derived??null;
  }
  function pillar(key,index) {
    const explicit=facts[key],derived=facts.pillars?.[index];
    if (explicit && derived && explicit!==derived) return {error:'四柱重复字段矛盾'};
    const value=explicit||derived;
    if (!value) return {};
    if (typeof value!=='string' || value.length!==2 || !GAN.includes(value[0]) || !ZHI.includes(value[1]) || GAN.indexOf(value[0])%2!==ZHI.indexOf(value[1])%2) return {error:'干支柱不合法'};
    return {value};
  }
  const y=pillar('year_pillar',0),d=pillar('day_pillar',2);
  // A manual chart may deliberately specify only the month branch.
  const mp=facts.month_pillar||facts.pillars?.[1];
  let mb=typeof mp==='string' && mp.length===1?mp:mp?.[1];
  reference('year_stem',null,y.value?.[0],GAN); reference('year_branch',null,y.value?.[1],ZHI);
  reference('day_stem',facts.day_stem,d.value?.[0],GAN); reference('day_branch',facts.day_branch,d.value?.[1],ZHI);
  reference('month_branch',facts.month_branch,mb,ZHI);
  if (y.error) for (const k of ['year_stem','year_branch']) problems[k]=y.error;
  if (d.error) for (const k of ['day_stem','day_branch','xun']) problems[k]=d.error;
  if (facts.month_pillar && facts.pillars?.[1] && facts.month_pillar!==facts.pillars[1]) problems.month_branch='月柱重复字段矛盾';
  const monthOffset=ZHI.includes(input.month_branch)?mod(ZHI.indexOf(input.month_branch)-2):null;
  input.month_index=monthOffset===null?null:monthOffset+1;
  input.season=monthOffset===null?null:['春','夏','秋','冬'][Math.floor(monthOffset/3)];
  if (problems.month_branch) problems.month_index=problems.season=problems.month_branch;
  // Derive the xun from a valid day; never silently trust a contradicting xun tag.
  const gi=GAN.indexOf(input.day_stem),zi=ZHI.indexOf(input.day_branch);
  if (gi>=0 && zi>=0 && gi%2!==zi%2) {
    for (const k of ['day_stem','day_branch','xun']) problems[k]='日干支阴阳不配';
  }
  input.xun=gi>=0 && zi>=0 && gi%2===zi%2?'甲'+ZHI[mod(zi-gi)]:null;
  const x=facts.xun;
  const xunTag=Array.isArray(x)?x[0]:typeof x==='string'?x.replace(/旬$/,''):null;
  if (xunTag && input.xun && xunTag!==input.xun) problems.xun='旬名与日柱矛盾';
  if (problems.day_stem || problems.day_branch) problems.xun='日柱参数有冲突';
  const coordinatesOK=rows.length===12 && new Set(rows.map(r=>r?.di)).size===12 && new Set(rows.map(r=>r?.tian)).size===12 &&
    rows.every(r=>r && ZHI.includes(r.di) && ZHI.includes(r.tian) && GENERALS.includes(r.tianjiang));
  const nobles=facts.nobleman||{};
  const nobleTable=policy.nobleman_tables[nobles.rule];
  const opposite=nobles.actual_zhouye==='昼贵'?'夜贵':nobles.actual_zhouye==='夜贵'?'昼贵':null;
  input.opposite_nobleman=nobleTable && opposite && gi>=0?nobleTable[opposite][gi]:null;
  if (problems.day_stem) problems.opposite_nobleman=problems.day_stem;
  if (nobles.rule && !nobleTable) problems.opposite_nobleman='未登记本盘贵人起例';
  if (nobleTable && opposite && gi>=0 && nobles.heaven_branch && nobles.heaven_branch!==nobleTable[nobles.actual_zhouye][gi]) problems.opposite_nobleman='贵人起例与本盘贵人支位冲突';
  const items=policy.rules.map(rule=>{
    const value=input[rule.basis];
    const base={id:rule.id,name:rule.name,basis:value??null};
    if (problems[rule.basis]) return {...base,status:'invalid_input',reason:problems[rule.basis]};
    if (value===null || value===undefined) return {...base,status:'missing_input',reason:rule.basis};
    if (rule.unsupported_basis?.includes(value)) return {...base,status:'disabled',reason:rule.unsupported_reason};
    const index=rule.basis==='opposite_nobleman'?null:policy.indices[rule.basis]?.indexOf(value);
    if (rule.basis!=='opposite_nobleman' && !(index>=0)) return {...base,status:'invalid_input',reason:'基准未登记'};
    const entry=rule.basis==='opposite_nobleman'?value:rule.table[index];
    const branches=Array.isArray(entry)?entry:[entry];
    if (!branches.length || !branches.every(b=>ZHI.includes(b))) throw new Error('神煞采用表定义不完整 '+rule.id);
    if (!coordinatesOK) return {...base,status:'invalid_input',computed_branches:branches,reason:'缺少完整且唯一的天地盘坐标与乘将'};
    const places=branches.map(b=>{
      const place=rows.find(r=>r.tian===b);
      return {tian:b,di:place.di,jiang:place.tianjiang};
    });
    const observed=rows.filter(r=>Array.isArray(r.shensha) && r.shensha.some(n=>rule.aliases.includes(n))).map(r=>r.tian);
    const same=observed.length===branches.length && branches.every(b=>observed.includes(b));
    const engineCheck=rule.engine_comparison==='ambiguous_same_name'?'同名跨基准不自动归属':observed.length?(same?'一致':'不同，采用重算'):'原标签未列，采用重算';
    const out={...base,status:'resolved',places,engine_check:engineCheck};
    if (observed.length && !same) out.engine_tian=observed;
    return out;
  });
  const recognized=new Set(policy.rules.flatMap(r=>r.aliases));
  const observedNames=[...new Set(rows.flatMap(r=>Array.isArray(r.shensha)?r.shensha:[]))];
  const disabled=policy.disabled.filter(n=>observedNames.includes(n));
  const unregistered=observedNames.filter(n=>!recognized.has(n) && !policy.disabled.includes(n));
  return {schema:'liuren-shensha-resolution-v1',release:policy.release,policy_sha256:policySha256,
    coordinate_contract:'所有神煞只归属places.tian（天盘支）；places.di仅为所临地盘，无神煞归属。午加丑而煞属午，绝不记为煞在丑。',
    place_fields:{tian:'神煞所属天盘支',di:'该天盘支所临地盘',jiang:'该天盘支所乘天将'},
    calendar:'月序按月建节月寅起、季随月建；年沿原盘年柱；项目约定',
    meaning:'resolved只允许进入取用，不代表与本问相关、有效或已有吉凶结论。未采用项禁止作背景风险。',
    items,disabled_names:policy.disabled,disabled_observed_names:disabled,unregistered_names:unregistered,
    unregistered_policy:'原引擎这些名称不自动采用；关系状态回理气核，专项神煞补齐可复算来源与条件记录再用。',
    evidence_policy:'别名同项不计多证；同位异项也不自动构成独立验证；刃空不推定伤浅。'};
}

export async function shenshaForChart(record) {
  const {policy,sha256}=await loadShenshaPolicy();
  return resolveShensha(factsForShensha(record),policy,sha256);
}

// A sidecar keeps historical engine archives and adapter fingerprints immutable.
export async function enrichChartResult(result, { persist = true, loadedPolicy } = {}) {
  if (!result?.facts || result.error) return result;
  const {policy,sha256}=loadedPolicy || await loadShenshaPolicy();
  let resolution=result.validation?.ok===true
    ? resolveShensha(result.facts,policy,sha256)
    : {schema:'liuren-shensha-resolution-v1',release:policy.release,policy_sha256:sha256,
       status:'chart_unusable',items:[],reason:'原盘验证未通过，所有神煞本盘不采用；保留完整原档供核查'};
  let facts=result.facts,engine_corrections=[],correctedArchive=null;
  if(result.validation?.ok===true) {
    const corrected=correctEngineShensha(result.facts,policy,resolution);
    facts=corrected.facts;engine_corrections=corrected.changes;
    resolution=resolveShensha(facts,policy,sha256);
  }
  let shensha_archive=null;
  if (persist && result.archive?.path) {
    const raw=await fs.readFile(result.archive.path);
    if (hash(raw)!==result.archive.sha256) throw new Error('原盘归档哈希变化，停止保存神煞采用记录');
    const source=JSON.parse(raw.toString('utf8'));
    if (JSON.stringify(source._direct?.facts)!==JSON.stringify(result.facts)) throw new Error('返回facts与原盘归档不一致');
    const base=result.archive.path.replace(/\.json$/i,'');
    if(result.validation?.ok===true) {
      const { _direct:legacyMetadata,...legacyRaw }=source;
      const correctedRaw=correctedRawExport(legacyRaw,facts);
      const record={...correctedRaw,_direct:{...legacyMetadata,schema:'liuren-direct-corrected-export-v1',
        adapter_version:policy.release,facts,shensha_resolution:resolution,
        legacy_archive:result.archive,engine_corrections,
        engine:{...legacyMetadata.engine,id:'liuren-shensha-policy-engine-v1',algorithm_modified:true,
          modified_scope:'shensha calculation/export only',base_engine:legacyMetadata.engine?.id,policy_sha256:sha256},
        raw_sha256:hash(JSON.stringify(correctedRaw))}};
      const target=base+'.corrected-'+sha256.slice(0,16)+'.json';
      const bytes=JSON.stringify(record,null,2)+'\n';
      try{await fs.writeFile(target,bytes,{encoding:'utf8',flag:'wx'});}
      catch(error){if(error.code!=='EEXIST'||await fs.readFile(target,'utf8')!==bytes)throw error;}
      correctedArchive={path:target,sha256:hash(bytes),raw_sha256:record._direct.raw_sha256};
    }
    const target=base+'.shensha-'+sha256.slice(0,16)+'.json';
    const bytes=JSON.stringify({schema:'liuren-shensha-sidecar-v1',source_archive:result.archive,
      corrected_archive:correctedArchive,engine_corrections,shensha_resolution:resolution},null,2)+'\n';
    try {await fs.writeFile(target,bytes,{encoding:'utf8',flag:'wx'});}
    catch(error) {
      if(error.code!=='EEXIST' || await fs.readFile(target,'utf8')!==bytes) throw error;
    }
    shensha_archive={path:target,sha256:hash(bytes)};
  }
  return {...result,facts,archive:correctedArchive||result.archive,legacy_archive:correctedArchive?result.archive:null,
    provenance:{...result.provenance,shensha_corrected:result.validation?.ok===true,shensha_policy_sha256:sha256},
    engine_version:'liuren-shensha-policy-engine-v1',engine_corrections,shensha_resolution:resolution,shensha_archive,
    field_notes:{...result.field_notes,shensha:'facts.heaven_earth已按固定表修正；神煞归属天盘tian，地盘di仅为所临，不存在地盘神煞。',
      raw:'archive为当前采用的修正版完整JSON；legacy_archive保留原引擎输出用于比对；不从旧标签覆盖修正版。'}};
}

if (isEntryPoint(process.argv[1], import.meta.url)) {
  try {
    if (process.argv.length!==4 || process.argv[2]!=='--chart') throw new Error('使用 node tools/liuren-shensha.mjs --chart 原盘JSON；不重起课');
    const result=await shenshaForChart(await readJSON(process.argv[3]));
    process.stdout.write(JSON.stringify(result)+'\n');
  } catch (error) {process.stderr.write('LIUREN_SHENSHA_ERROR: '+error.message+'\n');process.exitCode=2;}
}
