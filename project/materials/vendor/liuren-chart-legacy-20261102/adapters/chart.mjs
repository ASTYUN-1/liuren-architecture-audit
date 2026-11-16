import fs from 'node:fs';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const manifest = JSON.parse(fs.readFileSync(new URL('./legacy-engine-manifest.json', import.meta.url), 'utf8'));
const branches = [...'子丑寅卯辰巳午未申酉戌亥'];
const stems = [...'甲乙丙丁戊己庚辛壬癸'];
const sexagenary = Array.from({ length: 60 }, (_, i) => stems[i % 10] + branches[i % 12]);
const defaults = Object.freeze({ yuejiang: '中气换将', guiren: '甲戊庚牛羊', zhouye: '自动选择', shehai: '孟仲季' });
const options = {
  yuejiang: ['中气换将', '交节换将', '日躔换将'],
  guiren: ['甲戊庚牛羊', '甲羊戊庚牛'],
  zhouye: ['自动选择', '昼贵', '夜贵'],
  shehai: ['孟仲季', '深度'],
};
const hash = (value) => crypto.createHash('sha256').update(typeof value === 'string' ? value : JSON.stringify(value)).digest('hex');
const canonicalGeneral = (value) => ({ 螣蛇: '腾蛇' }[value] || value);

function fail(code, message, details = {}) { const error = new Error(message); error.code = code; error.details = details; throw error; }
function assertObject(value, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) fail('INVALID_INPUT', `${label}必须为对象。`);
}
function parseMinute(value, label = 'datetime') {
  if (typeof value !== 'string') fail('INVALID_DATETIME', `${label}需要YYYY-MM-DDTHH:mm（可附:00和+08:00）。`);
  const match = /^(\d{4})-(\d{2})-(\d{2})[T ](\d{2}):(\d{2})(?::00)?(?:\+08:00)?$/.exec(value);
  if (!match) fail('INVALID_DATETIME', `${label}需要北京时间分钟精度，不接受非零秒或其他时区。`);
  const [, ys, ms, ds, hs, is] = match;
  const [y, m, d, h, i] = [ys, ms, ds, hs, is].map(Number);
  const date = new Date(Date.UTC(y, m - 1, d, h, i));
  if (y < 1900 || y > 2100 || date.getUTCFullYear() !== y || date.getUTCMonth() + 1 !== m || date.getUTCDate() !== d || h > 23 || i > 59) {
    fail('INVALID_DATETIME', `${label}无效，当前支持1900—2100年有效公历日期。`);
  }
  return { date: `${ys}-${ms}-${ds}`, time: `${hs}:${is}`, iso: `${ys}-${ms}-${ds}T${hs}:${is}:00+08:00`, parts: { y, m, d, h, i } };
}
function normalizedSettings(request) {
  assertObject(request || {}, 'settings');
  for (const key of Object.keys(request || {})) {
    if (!(key in options)) fail('UNSUPPORTED_SETTING', `未支持设置${key}，拒绝忽略。`);
    if (!options[key].includes(request[key])) fail('INVALID_SETTING', `${key}必须为${options[key].join(' / ')}。`);
  }
  return { ...defaults, ...request };
}
function nativeParticipants(items = []) {
  if (!Array.isArray(items)) fail('INVALID_PARTICIPANTS', 'participants必须为数组。');
  return items.map((person, index) => {
    assertObject(person, `participants[${index}]`);
    if (!['男', '女'].includes(person.sex)) fail('INVALID_PARTICIPANT', '原工具年命参数需要明确sex为男或女。');
    if (person.birth_year !== undefined && person.age !== undefined) fail('INVALID_PARTICIPANT', 'birth_year与原工具age只能传一个。');
    const age = person.birth_year ?? person.age;
    if (!Number.isInteger(age) || (person.birth_year !== undefined ? age < 1900 || age > 2100 : age < 0 || age > 150)) {
      fail('INVALID_PARTICIPANT', 'birth_year需要1900—2100整数；age需要0—150的原工具年龄参数。');
    }
    return { name: person.name || `参与者${index + 1}`, sex: person.sex, age };
  });
}
function declaredLife(items = []) {
  if (!Array.isArray(items)) fail('INVALID_DECLARED_LIFE', 'declared_life须为数组，与原工具计算的participants分开。');
  return items.map((item, index) => {
    assertObject(item, `declared_life[${index}]`);
    if (!sexagenary.includes(item.birth_pillar)) fail('INVALID_DECLARED_LIFE', '用户明确提供的birth_pillar须为有效六十甲子；只给生年不可冒充已知本命。');
    if (item.sex !== undefined && !['男', '女'].includes(item.sex)) fail('INVALID_DECLARED_LIFE', 'sex若提供须为男或女。');
    if (item.name !== undefined && (typeof item.name !== 'string' || !item.name.trim())) fail('INVALID_DECLARED_LIFE', 'name须为非空字符串。');
    if (item.source !== undefined && (typeof item.source !== 'string' || !item.source.trim())) fail('INVALID_DECLARED_LIFE', 'source须为原问或用户提供依据的非空说明。');
    return { name: item.name || `参与者${index + 1}`, ...(item.sex ? { sex: item.sex } : {}), birth_pillar: item.birth_pillar, source: item.source || '用户明确提供', source_type: 'user-stated', independently_verified: false, eligible_as_declared_input: true };
  });
}
function normalizeRequest(input) {
  assertObject(input, '排盘请求');
  if (input.time_basis !== undefined && !['civil', 'civil-time'].includes(input.time_basis)) {
    fail('UNSUPPORTED_CONVENTION', '当前只支持civil/civil-time民用钟表时间；真太阳时等非民用时间约定尚未适配，不能静默按正时排盘。', { requested_time_basis: input.time_basis, supported: ['civil', 'civil-time'] });
  }
  if (input.timezone && input.timezone !== 'Asia/Shanghai') fail('UNSUPPORTED_TIMEZONE', '本适配器仅支持Asia/Shanghai；不能把其他时区当北京时间。');
  const mode = input.mode || 'datetime';
  if (!['datetime', 'manual-pillars'].includes(mode)) fail('UNSUPPORTED_MODE', '当前支持datetime或manual-pillars；活时/真太阳时须单独明确适配。');
  const settings = normalizedSettings(input.settings || {});
  const users = nativeParticipants(input.participants);
  const normalized = { ...structuredClone(input), mode, timezone: 'Asia/Shanghai', time_basis: 'civil', settings, participants: input.participants || [] };
  if (input.declared_life !== undefined) normalized.declared_life = declaredLife(input.declared_life);
  let date;
  const native = { ...settings, user: users, cundang: { ws: '', dy: '', fk: '', tag: 'workflow' } };
  if (mode === 'datetime') {
    date = parseMinute(input.datetime);
    if (normalized.participants.some((person) => person.birth_year > date.parts.y)) fail('INVALID_PARTICIPANT', '出生年不能晚于占课年。');
    normalized.datetime = date.iso;
    native.zhenghuoshi = '正时';
    native.sizhu = { yg: '甲', yz: '子', mz: '子', dg: '甲', dz: '子', hz: '子', yuejiang: '丑' };
  } else {
    assertObject(input.pillars, 'manual-pillars.pillars');
    const p = input.pillars;
    const missing = ['year', 'month_branch', 'day', 'hour_branch'].filter((key) => p[key] === undefined || p[key] === null || p[key] === '');
    if (input.month_general === undefined || input.month_general === null || input.month_general === '') missing.push('month_general');
    if (missing.length) fail('INPUT_REQUIRED', `完整四柱模式缺少必填信息：${missing.join('、')}。请提供真实来源，不得补造。`, { missing_fields: missing });
    if (!sexagenary.includes(p.year) || !sexagenary.includes(p.day)) fail('INVALID_PILLARS', 'year和day必须是有效六十甲子。');
    if (!branches.includes(p.month_branch) || !branches.includes(p.hour_branch) || !branches.includes(input.month_general)) {
      fail('INVALID_PILLARS', 'month_branch、hour_branch、month_general必须是单个地支。');
    }
    if (users.length) fail('MANUAL_PARTICIPANTS_UNSUPPORTED', '原四柱模式清空userinfo；请将已核年命作为独立研判信息保存，不能假装工具计算了年命。');
    date = parseMinute(input.reference_datetime || '2000-01-01T12:00', 'reference_datetime');
    native.zhenghuoshi = '四柱';
    native.sizhu = { yg: p.year[0], yz: p.year[1], mz: p.month_branch, dg: p.day[0], dz: p.day[1], hz: p.hour_branch, yuejiang: input.month_general };
    normalized.reference_datetime = input.reference_datetime ? date.iso : null;
  }
  native.Date = date.date;
  native.Time = date.time;
  return { normalized, native, date };
}
function executeWorker(request) {
  const result = spawnSync(process.execPath, [fileURLToPath(new URL('./legacy-engine-worker.mjs', import.meta.url))], {
    input: JSON.stringify(request), encoding: 'utf8', windowsHide: true, env: { ...process.env, TZ: 'Asia/Shanghai' }, timeout: 45000, maxBuffer: 4 * 1024 * 1024,
  });
  if (result.error) fail('ENGINE_EXECUTION_FAILED', result.error.message);
  let response;
  try { response = JSON.parse(result.stdout); } catch { fail('ENGINE_INVALID_RESPONSE', `原引擎子进程未输出有效JSON：${result.stderr?.slice(0, 500) || 'empty output'}`); }
  if (!response.ok) fail(response.error.code, response.error.message);
  return response.result;
}

function engineInfo() {
  return { id: manifest.engine_id, manifest_hash: hash(manifest), files: manifest.files, execution: manifest.execution, network: false, fallback: false, algorithm_modified: false };
}
function factsFromRaw(raw, input = null, native = null) {
  const pillars = raw.basic?.pillars || [];
  const lessons = (Array.isArray(raw.sike) ? raw.sike : []).map((row, index) => ({ index: index + 1, ...row }));
  const heavenEarth = (Array.isArray(raw.tiandipan) ? raw.tiandipan : []).map((row) => ({ ...row, tianjiang: canonicalGeneral(row?.tianjiang) }));
  const transmissions = (Array.isArray(raw.sanchuan) ? raw.sanchuan : []).map((row, index) => ({ index: index + 1, ...row, tianjiang: canonicalGeneral(row?.tianjiang), earth_position: native?.transmission_earth_positions?.[index] || heavenEarth.find((place) => place.tian === row?.diZhi)?.di || null }));
  const noblemanPosition = heavenEarth.find((row) => row.tianjiang === '贵人');
  const nextEarth = noblemanPosition ? branches[(branches.indexOf(noblemanPosition.di) + 1) % 12] : null;
  const nextGeneral = heavenEarth.find((row) => row.di === nextEarth)?.tianjiang;
  const actualDirection = nextGeneral === '腾蛇' ? '顺行' : nextGeneral === '天后' ? '逆行' : null;
  const dayHours = [...'卯辰巳午未申'];
  const selectedZhouye = raw.basic?.settings?.zhouye;
  const actualZhouye = selectedZhouye === '自动选择' ? (dayHours.includes(pillars[3]?.[1]) ? '昼贵' : '夜贵') : ['昼贵', '夜贵'].includes(selectedZhouye) ? selectedZhouye : null;
  return {
    schema: 'liuren-chart-facts-v1',
    pillars, year_pillar: pillars[0] || null, month_pillar: pillars[1] || null, day_pillar: pillars[2] || null, hour_pillar: pillars[3] || null,
    day_stem: pillars[2]?.[0] || null, day_branch: pillars[2]?.[1] || null, month_branch: pillars[1]?.[1] || null, hour_branch: pillars[3]?.[1] || null,
    month_general: raw.basic?.jiang || null, void_branches: raw.basic?.xunkong || [], xun: raw.basic?.xun || null,
    event_datetime: input?.mode === 'manual-pillars' ? null : input?.datetime || null,
    lunar: input?.mode === 'manual-pillars' ? null : raw.basic?.lunar || null,
    heaven_earth: heavenEarth, lessons, transmissions, transmission_sequence: transmissions.map((row) => row.diZhi).join(''), chart_types: raw.keti || [],
    summary: raw.summary || null, key_shensha: raw.keyShensha || [],
    participants: native?.userinfo || raw.userinfo || [], year_life_verified: false,
    declared_life: input?.declared_life || [],
    nobleman: { rule: native?.guiren_type || raw.basic?.settings?.guiren || null, requested_zhouye: selectedZhouye || null, actual_zhouye: actualZhouye, heaven_branch: noblemanPosition?.tian || null, earth_position: noblemanPosition?.di || null, direction: actualDirection, native_hour_label: native?.hour_based_zhouye_label || null, native_direction_label: native?.guiren_shunni_label || null },
    growth: native ? { day_stem: native.richangsheng, branches: native.branch_growth } : null,
    seasonal_strength: native?.seasonal_strength || null,
  };
}
function validateRaw(raw, input = null) {
  const checks = [];
  const add = (code, ok, detail, severity = 'error') => checks.push({ code, ok: Boolean(ok), severity, detail });
  add('schema', raw?.schema === 'liuren-paipan-v1', '原魔改工具JSON schema');
  add('pillars', Array.isArray(raw.basic?.pillars) && raw.basic.pillars.length === 4 && raw.basic.pillars.every((v) => sexagenary.includes(v)), '四柱必须是4个有效六十甲子');
  add('heaven_earth_count', Array.isArray(raw.tiandipan) && raw.tiandipan.length === 12, '天地盘必须有12宫');
  add('heaven_earth_permutation', Array.isArray(raw.tiandipan) && raw.tiandipan.length === 12 && branches.every((v) => raw.tiandipan.some((p) => p?.di === v)) && branches.every((v) => raw.tiandipan.some((p) => p?.tian === v)), '天地盘地支均为12地支的完整排列');
  add('lessons_count', Array.isArray(raw.sike) && raw.sike.length === 4, '四课须保留顺序，不去重');
  add('transmissions_count', Array.isArray(raw.sanchuan) && raw.sanchuan.length === 3 && raw.sanchuan.every((p) => branches.includes(p?.diZhi)), '三传须保留3个有序槽位，允许重复');
  add('month_general', branches.includes(raw.basic?.jiang), '月将须为单个地支');
  add('void_branches', Array.isArray(raw.basic?.xunkong) && raw.basic.xunkong.length === 2 && new Set(raw.basic.xunkong).size === 2 && raw.basic.xunkong.every((v) => branches.includes(v)), '旬空须为2个不同地支');
  if (Array.isArray(raw.tiandipan) && raw.tiandipan.length === 12 && raw.tiandipan.every((p) => p && typeof p === 'object')) {
    const offsets = raw.tiandipan.map((p) => (branches.indexOf(p.tian) - branches.indexOf(p.di) + 12) % 12);
    add('rotation_consistency', offsets.every((v) => v === offsets[0]), '12宫天地盘必须为同一旋转量');
    const hour = raw.basic?.pillars?.[3]?.[1];
    add('month_general_on_hour', raw.tiandipan.find((p) => p.di === hour)?.tian === raw.basic?.jiang, '月将加占时对应');
    const generalNames = ['贵人', '腾蛇', '朱雀', '六合', '勾陈', '青龙', '天空', '白虎', '太常', '玄武', '太阴', '天后'];
    add('generals_permutation', generalNames.every((v) => raw.tiandipan.some((p) => canonicalGeneral(p.tianjiang) === v)), '十二天将完整且不重复');
    const generalSteps = branches.map((branch, i) => {
      const here = generalNames.indexOf(canonicalGeneral(raw.tiandipan.find((p) => p.di === branch)?.tianjiang));
      const next = generalNames.indexOf(canonicalGeneral(raw.tiandipan.find((p) => p.di === branches[(i + 1) % 12])?.tianjiang));
      return (next - here + 12) % 12;
    });
    add('generals_order', generalSteps.every((v) => v === 1) || generalSteps.every((v) => v === 11), '十二天将顺序须连续顺排或逆排');
    const at = (branch) => raw.tiandipan.find((p) => p.tian === branch);
    add('lesson_generals', Array.isArray(raw.sike) && raw.sike.length === 4 && raw.sike.every((p) => p && canonicalGeneral(at(p.tianpan)?.tianjiang) === canonicalGeneral(p.tianjiang)), '四课天将与天盘神对应');
    add('transmission_generals', Array.isArray(raw.sanchuan) && raw.sanchuan.length === 3 && raw.sanchuan.every((p) => p && canonicalGeneral(at(p.diZhi)?.tianjiang) === canonicalGeneral(p.tianjiang)), '三传天将与天盘神对应');
  }
  if (input?.mode === 'manual-pillars') {
    add('manual_request_match', raw.basic?.pillars?.[0] === input.pillars.year && raw.basic?.pillars?.[2] === input.pillars.day && raw.basic?.pillars?.[1]?.[1] === input.pillars.month_branch && raw.basic?.pillars?.[3]?.[1] === input.pillars.hour_branch && raw.basic?.jiang === input.month_general, '四柱/将时与手工请求逐项一致');
  }
  const errors = checks.filter((c) => !c.ok && c.severity === 'error').map((c) => ({ code: c.code, message: c.detail }));
  return { ok: errors.length === 0, status: errors.length ? 'blocked' : 'structure-and-request-verified', checks, errors, warnings: [], prediction_accuracy_verified: false, whole_algorithm_exhaustively_verified: false };
}

export async function createChart(input) {
  const { normalized, native, date } = normalizeRequest(input);
  const before = structuredClone(native);
  const result = executeWorker({ operation: 'chart', native_input: native });
  // Supplement page omissions without replacing any original exported field.
  const raw = result.raw;
  raw.userinfo = result.native.userinfo;
  raw.nativeNobleman = { ...result.native, richangsheng: undefined, branch_growth: undefined, userinfo: undefined, seasonal_strength: undefined, transmission_earth_positions: undefined };
  const facts = factsFromRaw(raw, normalized, result.native);
  const validation = validateRaw(raw, normalized);
  validation.checks.push({ code: 'original_engine_executed', ok: true, severity: 'error', detail: '原文件SHA-256一致，调用原LiuRenPaiPan与原页面JSON导出器，无算法替代' });
  validation.warnings.push({ code: 'ENGINE_NOT_EXHAUSTIVELY_PROVEN', message: '当前通过输入、形状及基本关系核验；未证明原引擎所有历法/涉害/三传规则均正确。' });
  if (facts.participants.length) validation.warnings.push({ code: 'LEGACY_YEAR_LIFE_UNVERIFIED', message: '原userinfo以7月1日代表出生年取年柱，2月立春filter数组却读.d，且年龄口径未独立核验；年命/行年不得直接用于决定性判断。' });
  if (facts.nobleman.direction !== facts.nobleman.native_direction_label) validation.warnings.push({ code: 'LEGACY_NOBLEMAN_DIRECTION_LABEL', message: '原guiren_shunni标签按贵人天盘支判断，可能与实际天将排列不一致；facts.nobleman.direction从实际12宫排列读取。' });
  if (result.native.solar_terms_same_minute.length) {
    validation.errors.push({ code: 'SOLAR_TERM_MINUTE_BOUNDARY', message: '本分钟存在交节：原四柱按30秒计算、原月将节气比较按0秒，需明确秒级输入与复核，不能给出已验正式盘。' });
    validation.ok = false;
    validation.status = 'blocked';
  }
  if (normalized.mode === 'manual-pillars') validation.warnings.push({ code: 'MANUAL_DISPLAY_DATE', message: '手工四柱模式的原basic.datetime/nongli仅来自参考显示日期；不证明该课真实历史日期，facts.event_datetime为null。' });
  return {
    raw, facts, validation, input: normalized,
    conventions: { timezone: 'Asia/Shanghai', input_precision: 'minute', internal_seconds: 30, engine_day_boundary: 'original lunar.js getBaZi default; do not recalculate in LLM', manual_date_is_placeholder: normalized.mode === 'manual-pillars' && !input.reference_datetime, manual_reference_date: normalized.mode === 'manual-pillars' ? date.iso : null, settings: normalized.settings, native_input_before: before, native_input_after: result.native_input_after, settings_mutated_by_engine: JSON.stringify(before) !== JSON.stringify(result.native_input_after) },
    provenance: { source: 'copied legacy modified chart tool', export_method: 'execute original index.html JSON exporter in isolated VM', engine_hash_verified: true, timestamp_input_iso: normalized.mode === 'datetime' ? normalized.datetime : null },
    engine: engineInfo(),
  };
}

function coreSignature(raw, reference = raw) {
  return JSON.stringify({ pillars: raw.basic?.pillars, jiang: raw.basic?.jiang, xun: raw.basic?.xun, xunkong: raw.basic?.xunkong,
    tiandipan: (Array.isArray(raw.tiandipan) ? raw.tiandipan : []).map((p, i) => [p?.di, p?.tian, canonicalGeneral(p?.tianjiang), reference.tiandipan?.[i]?.xungan !== undefined ? p?.xungan : null]),
    sike: (Array.isArray(raw.sike) ? raw.sike : []).map((p) => [p?.tianpan, p?.dizhi, canonicalGeneral(p?.tianjiang)]),
    sanchuan: (Array.isArray(raw.sanchuan) ? raw.sanchuan : []).map((p) => [p?.liuqin, p?.tianGan, p?.diZhi, canonicalGeneral(p?.tianjiang), (p?.status || '').trim()]) });
}
export async function inspectChart(input) {
  let parsed = input;
  for (let count = 0; typeof parsed === 'string' && count < 3; count++) parsed = JSON.parse(parsed.replace(/^\uFEFF/, ''));
  assertObject(parsed, '待验盘JSON');
  const raw = parsed.raw || parsed;
  assertObject(raw, 'raw');
  const validation = validateRaw(raw, parsed.input || null);
  let replay = null;
  const settings = raw.basic?.settings;
  const chineseTime = /^(\d{4})年(\d{2})月(\d{2})日 (\d{2})时(\d{2})分$/.exec(raw.basic?.datetime || '');
  const importedTime = settings?.Date && settings?.Time ? `${settings.Date}T${settings.Time}` : chineseTime ? `${chineseTime[1]}-${chineseTime[2]}-${chineseTime[3]}T${chineseTime[4]}:${chineseTime[5]}` : null;
  const replayInput = parsed.input || (importedTime && settings?.zhenghuoshi === '正时' && Object.keys(defaults).every((key) => options[key].includes(settings[key])) ? {
    mode: 'datetime', datetime: importedTime, timezone: 'Asia/Shanghai',
    settings: Object.fromEntries(Object.keys(defaults).map((key) => [key, settings[key]])),
    participants: (settings.user || []).map((p) => ({ name: p.name, sex: p.sex, ...(Number(p.age) > 1800 ? { birth_year: Number(p.age) } : { age: Number(p.age) }) })),
  } : null);
  if (replayInput) {
    try {
      replay = await createChart(replayInput);
      validation.errors.push(...replay.validation.errors);
      const ok = coreSignature(raw) === coreSignature(replay.raw, raw);
      validation.checks.push({ code: 'original_engine_replay', ok, severity: 'error', detail: '原引擎按明确输入重排，比较四柱/将/空/12宫/4课/3传原字段' });
      if (!ok) validation.errors.push({ code: 'ENGINE_REPLAY_MISMATCH', message: '导入盘面与原引擎重排不符，保留原JSON供复核。' });
    } catch (error) { validation.errors.push({ code: error.code || 'REPLAY_FAILED', message: error.message }); }
  } else {
    validation.errors.push({ code: 'MISSING_REPLAY_INPUT', message: '缺明确排盘请求或完整正时设置；只能检查形状，不能作为已验正式盘。' });
  }
  validation.ok = validation.errors.length === 0;
  validation.status = validation.ok ? 'original-engine-replayed' : 'blocked';
  validation.warnings = replay?.validation.warnings || [];
  if (raw.tiandipan?.some((p) => p.xungan === undefined || p.nayin === undefined || p.shensha === undefined)) validation.warnings.push({ code: 'IMPORTED_OPTIONAL_FIELDS_MISSING', message: '导入档案未保留旬干/纳音/神煞全字段；重排比对只确认实际保留字段，不能声称完整原导出。' });
  return { raw, facts: replay ? factsFromRaw(raw, replay.input, { ...replay.raw.nativeNobleman, userinfo: replay.raw.userinfo }) : factsFromRaw(raw, parsed.input), validation, input: replay?.input || parsed.input || null, conventions: replay?.conventions || null, provenance: { source: 'imported-json', original_preserved: true, replayed: Boolean(replay), engine_hash_verified: Boolean(replay) }, engine: engineInfo() };
}

export async function calendarCandidates(input) {
  assertObject(input, '历法请求');
  const start = parseMinute(`${input.start}T12:00`).date;
  const end = parseMinute(`${input.end}T12:00`).date;
  const count = (Date.parse(`${end}T12:00:00+08:00`) - Date.parse(`${start}T12:00:00+08:00`)) / 86400000 + 1;
  if (count < 1 || count > 366) fail('INVALID_CALENDAR_RANGE', '日期区间需顺序正确且不超过366天（含首尾）。');
  for (const [key, allowed] of [['day_branches', branches], ['day_pillars', sexagenary]]) {
    if (input[key] !== undefined && (!Array.isArray(input[key]) || input[key].some((v) => !allowed.includes(v)))) fail('INVALID_CALENDAR_FILTER', `${key}包含无效条目。`);
  }
  if (input.timezone && input.timezone !== 'Asia/Shanghai') fail('UNSUPPORTED_TIMEZONE', '历法日期按Asia/Shanghai解释。');
  return { ...executeWorker({ operation: 'calendar', start, end, day_branches: input.day_branches || [], day_pillars: input.day_pillars || [] }), engine: engineInfo(), prediction: false };
}
