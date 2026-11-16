import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { pathToFileURL, fileURLToPath } from 'node:url';

const project = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const defaultPolicy = Object.freeze({
  calendar: 'gregorian', timezone: 'Asia/Shanghai', time_basis: 'civil', ordinary_method: 'datetime',
  settings: { yuejiang: '中气换将', guiren: '甲戊庚牛羊', zhouye: '自动选择', shehai: '孟仲季' },
});
const hash = (value) => crypto.createHash('sha256').update(value).digest('hex');
const readJson = (p) => JSON.parse(fs.readFileSync(p, 'utf8').replace(/^\uFEFF/, ''));
const writeJson = (p, data) => fs.writeFileSync(p, `${JSON.stringify(data, null, 2)}\n`, 'utf8');
const branches = [...'子丑寅卯辰巳午未申酉戌亥'];
const stems = [...'甲乙丙丁戊己庚辛壬癸'];
const validPillars = Array.from({ length: 60 }, (_, i) => stems[i % 10] + branches[i % 12]);

function field(text, name) {
  return text.split(/\r?\n/).find((line) => line.startsWith(`- ${name}：`))?.slice(name.length + 3).trim() ?? null;
}
function validDate(y, m, d) {
  const date = new Date(Date.UTC(y, m - 1, d));
  return y >= 1900 && y <= 2100 && date.getUTCFullYear() === y && date.getUTCMonth() + 1 === m && date.getUTCDate() === d;
}
const pad = (n) => String(n).padStart(2, '0');

export function parseTime(raw) {
  const cleaned = (raw || '').replace(/^\[当代\]中国公历纪元\d{4}年\s*/, '');
  const m = /^[。．，,\s]*(\d{4})(?:年|[-/])(\d{1,2})(?:月|[-/])(\d{1,2})日?\s*(.*)$/.exec(cleaned);
  if (!m) return { precision: 'unknown', datetime: null, issue: 'MISSING_CALENDAR_DATE' };
  const [y, month, d] = m.slice(1, 4).map(Number);
  if (!validDate(y, month, d)) return { precision: 'invalid', datetime: null, issue: 'INVALID_DATE' };
  const date = `${y}-${pad(month)}-${pad(d)}`;
  // Lunar labels alongside an explicit Gregorian date are annotations, not date conversion.
  const timePart = m[4].trim().replace(/^[（(][^()（）]*[）)]\s*/, '').replace(/[，,。]+$/, '').trim();
  const minute = /^(\d{1,2})(?:[:：]|时)(\d{1,2})分?(?=$|\s|[（(])/.exec(timePart);
  if (minute) {
    const [h, i] = minute.slice(1).map(Number);
    if (h > 23 || i > 59) return { precision: 'invalid', datetime: null, issue: 'INVALID_TIME' };
    const trailing = timePart.slice(minute[0].length).trim();
    if (/\d{4}(?:年|[-/])|\d{1,2}[:：]\d{1,2}|\d{1,2}时\d/.test(trailing)) return { precision: 'unknown', date, datetime: null, issue: 'MULTIPLE_TIME_CANDIDATES' };
    if (trailing && !/^(?:[（(][^()（）]*[）)]|星期[一二三四五六日天]|周[一二三四五六日天]|七月十六处暑|\s)+$/.test(trailing)) return { precision: 'unknown', date, datetime: null, issue: 'UNSUPPORTED_TIME_ANNOTATION' };
    return { precision: 'minute', date, datetime: `${date}T${pad(h)}:${pad(i)}` };
  }
  const hour = /^(\d{1,2})时$/.exec(timePart);
  if (hour && Number(hour[1]) < 24) return { precision: 'hour', date, hour: Number(hour[1]), datetime: null, issue: 'MINUTE_NOT_SUPPLIED' };
  if (/^[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]时$/.test(timePart) && validPillars.includes(timePart.slice(0, 2))) {
    return { precision: 'pillar-hour', date, hour_pillar: timePart.slice(0, 2), datetime: null, issue: 'HOUR_PILLAR_NEEDS_RESOLUTION' };
  }
  return { precision: 'unknown', date, datetime: null, issue: 'UNSUPPORTED_TIME_FORMAT' };
}

export function inspectCase(text, filename, { imageLedger = null, sourceRoot = null } = {}) {
  const sections = text.split(/^## 7\. 完整原文\r?\n/m);
  if (sections.length !== 2) throw new Error(`${filename}: 缺唯一完整原文章节`);
  const match = /^```text\r?\n([\s\S]*?)\r?\n```\s*$/.exec(sections[1]);
  if (!match) throw new Error(`${filename}: 完整原文代码块格式错误`);
  const raw = match[1];
  const metadata = sections[0];
  const id = field(metadata, '初级编号');
  if (!id || path.basename(filename, '.md') !== id || !/^raw-[A-Za-z0-9_-]+$/.test(id)) throw new Error(`${filename}: 编号与文件名不一致或不安全`);
  const originalTime = field(metadata, '起课时间原文');
  if (!originalTime) throw new Error(`${id}: 缺起课时间原文字段`);
  const normalized = field(metadata, '可直接规范化的时间');
  const timeSource = field(metadata, '时间来源');
  const declaredPrimary = /^题干盘图提取（(pan\/[A-Za-z0-9_.-]+\.(?:jpg|jpeg|png))(?=[，；）])/.exec(timeSource || '')?.[1];
  const primaryTime = /^(.+?)（(pan\/[A-Za-z0-9_.-]+\.(?:jpg|jpeg|png))）；另盘 (pan\/[A-Za-z0-9_.-]+\.(?:jpg|jpeg|png)) 记为 /.exec(originalTime);
  const timeSelection = primaryTime && primaryTime[2] === declaredPrimary && primaryTime[2] !== primaryTime[3]
    ? { basis: 'explicit_primary_image_reference', primary_image: declaredPrimary, excluded_alternate_image: primaryTime[3], selected_time_text: primaryTime[1] } : null;
  const p = parseTime(timeSelection?.selected_time_text || originalTime);
  const issues = p.issue ? [p.issue] : [];
  const question = metadata.split(/^## 3\. 背景、问题与要求\r?\n/m)[1]?.split(/^## 4\./m)[0] || '';
  const other = field(metadata, '报数等其他起课信息') || '';
  // Only inspect the question and time fields; never recover a date from answers or feedback.
  const chartInfo = field(metadata, '题干原载课式信息');
  const methodText = `${originalTime}\n${question}\n${other}\n${chartInfo || ''}`;
  if (/报数|活时|射时/.test(methodText)) issues.push('SPECIAL_DIVINATION_METHOD');
  if (/真太阳|[（(]真[）)]|当地时间|时区|夏令时|农历|阴历|UTC|GMT/.test(methodText)) issues.push('EXPLICIT_TIME_CONVENTION_NEEDS_REVIEW');
  const actualFirst = raw.split(/\r?\n/)[0];
  const sourceGroup = field(metadata, '来源组编号');
  const sharedGroup = sourceGroup && sourceGroup !== '无' ? sourceGroup : null;
  if (sharedGroup && !/^group-[A-Za-z0-9_-]+$/.test(sharedGroup)) throw new Error(`${id}: 来源组编号格式无效`);
  const matchesTimeLine = (line) => {
    const value = line?.trim();
    return Boolean(value && (originalTime === value || originalTime.startsWith(`${value}（`)));
  };
  const sourceTimeMatches = sharedGroup
    ? raw.split(/\r?\n/).some(matchesTimeLine)
    : matchesTimeLine(actualFirst);
  let imageEvidence = null;
  if (!sourceTimeMatches && imageLedger && sourceRoot && /^题干盘图提取（pan\//.test(timeSource || '')) {
    const imagePath = /^题干盘图提取（(pan\/[A-Za-z0-9_.-]+\.(?:jpg|jpeg|png))(?=[，；）])/.exec(timeSource)?.[1];
    const records = (imageLedger.images || []).filter((entry) => entry.file === imagePath);
    const entry = records.length === 1 ? records[0] : null;
    const fullPath = imagePath && path.resolve(sourceRoot, imagePath);
    const seq = /seq=(\d+)/.exec(field(metadata, '来源名称') || '')?.[1];
    if (entry && seq !== undefined && Number(seq) === entry.seq && fullPath && fs.existsSync(fullPath) && hash(fs.readFileSync(fullPath)) === entry.sha256) {
      const ledgerTime = /^(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})(?::00)?$/.exec(entry.time_norm || '');
      if (p.datetime && ledgerTime && p.datetime === `${ledgerTime[1]}T${ledgerTime[2]}` && (!timeSelection || imagePath === timeSelection.primary_image)) {
        imageEvidence = { file: imagePath, absolute_file: fullPath, sha256: entry.sha256, hash_origin: entry.sha256_origin || 'source_ledger', seq: entry.seq, transcription: 'existing_stage1_image_transcription', time_crosschecked_with_ledger: true, independently_visually_verified_this_run: false, declaration: timeSource };
      } else issues.push('IMAGE_LEDGER_TIME_MISMATCH');
    } else issues.push('IMAGE_EVIDENCE_INVALID');
  }
  if (!sourceTimeMatches && !imageEvidence) issues.push('TIME_FIELD_SOURCE_MISMATCH');
  if (p.datetime && normalized) {
    const n = /^(\d{4}-\d{2}-\d{2})[ T](\d{2}:\d{2})/.exec(normalized);
    if (n && `${n[1]}T${n[2]}` !== p.datetime) issues.push('NORMALIZED_TIME_MISMATCH');
  }
  const settings = {};
  for (const [key, options] of Object.entries({ yuejiang: ['中气换将', '交节换将', '日躔换将'], guiren: ['甲戊庚牛羊', '甲羊戊庚牛'], shehai: ['孟仲季', '深度'] })) {
    const explicit = options.filter((value) => originalTime.includes(value));
    if (explicit.length === 1) settings[key] = explicit[0];
    else if (explicit.length > 1) issues.push('CONFLICTING_SOURCE_SETTINGS');
  }
  if (/所用的换将法为日躔换将/.test(chartInfo || '')) settings.yuejiang = '日躔换将';
  const primaryChart = (chartInfo || '').split(/另盘|；pan\//)[0];
  const zhouye = ['昼贵', '夜贵'].filter((value) => primaryChart.includes(value));
  if (zhouye.length === 1) settings.zhouye = zhouye[0];
  else if (zhouye.length > 1) issues.push('CONFLICTING_SOURCE_SETTINGS');
  const pillarMatch = /四柱[：\s]*([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s+([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s+([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])\s+([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])/.exec(primaryChart);
  const monthGeneral = /月将[：:\s]*([子丑寅卯辰巳午未申酉戌亥])/.exec(primaryChart)?.[1] || null;
  const day = /([甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥])日/.exec(originalTime)?.[1] || null;
  return {
    id, filename, shared_original_group: sharedGroup, original_time: originalTime, normalized_time_field: normalized,
    parsed_time: p, issues: [...new Set(issues)],
    image_evidence: imageEvidence, source_settings: settings, time_selection: timeSelection,
    source_locator: field(metadata, '原文定位'),
    constraints: { day_pillar: day, source_pillars: pillarMatch ? pillarMatch.slice(1) : null, source_month_general: monthGeneral, source_chart_description: chartInfo, other_input: other },
    source_text_sha256: hash(raw), case_file_sha256: hash(text),
    staging_only: true,
  };
}

function policyCheck(policy) {
  if (policy.calendar !== 'gregorian' || policy.timezone !== 'Asia/Shanghai' || policy.time_basis !== 'civil' || policy.ordinary_method !== 'datetime') {
    throw new Error('本脚本只适配公历、Asia/Shanghai、民用正时；其他约定请单独实现，不静默转换。');
  }
}
function resolvedInput(item, resolution, policy, acceptConfirmed) {
  if (!resolution) return { input: item.issues.length ? null : { datetime: item.parsed_time.datetime }, resolution: null };
  if (resolution.status !== 'confirmed' || !acceptConfirmed) return { input: null, issue: 'RESOLUTION_AWAITING_REVIEW', resolution };
  if (!resolution.evidence?.trim() || !resolution.reviewed_by?.trim()) throw new Error(`${item.id}: 已确认补全缺少证据或复核者`);
  if (resolution.case_file_sha256 !== item.case_file_sha256) throw new Error(`${item.id}: 补全依据对应旧版案例，请重新核对哈希`);
  if (resolution.method !== 'datetime') throw new Error(`${item.id}: 暂不支持该补全起课方法，不能把活时报数冒充正时`);
  if (item.issues.includes('TIME_FIELD_SOURCE_MISMATCH')) throw new Error(`${item.id}: 时间字段不对应原文，先修资料`);
  if (item.issues.includes('EXPLICIT_TIME_CONVENTION_NEEDS_REVIEW')) throw new Error(`${item.id}: 来源有其他时间约定，须单独适配`);
  if (typeof resolution.datetime !== 'string' || !/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(resolution.datetime)) throw new Error(`${item.id}: 补全时间格式应为YYYY-MM-DDTHH:mm`);
  if (item.parsed_time.date && !resolution.datetime.startsWith(`${item.parsed_time.date}T`)) throw new Error(`${item.id}: 补全改变了原文明示日期`);
  if (item.parsed_time.datetime && resolution.datetime !== item.parsed_time.datetime) throw new Error(`${item.id}: 补全改变了原文明示分钟`);
  if (item.parsed_time.precision === 'hour' && Number(resolution.datetime.slice(11, 13)) !== item.parsed_time.hour) throw new Error(`${item.id}: 补全改变了原文小时`);
  return { input: { datetime: resolution.datetime }, resolution };
}

export function chartFacts(result) {
  const { summary, key_shensha, ...facts } = result.facts;
  return facts; // Exclude embedded interpretive summary; never include question, answer, or feedback.
}

export async function buildBatch({ inputDir, outputDir, engineRoot, policy = defaultPolicy, resolutions = {}, acceptConfirmed = false, only = null, createChart, imageLedger = null, sourceRoot = null }) {
  policyCheck(policy);
  if (path.resolve(inputDir) === path.resolve(outputDir)) throw new Error('输出目录不能等于输入资料目录');
  const files = fs.readdirSync(inputDir).filter((name) => /^raw-.*\.md$/.test(name)).sort();
  const allItems = files.map((name) => inspectCase(fs.readFileSync(path.join(inputDir, name), 'utf8'), name, { imageLedger, sourceRoot }));
  const items = only ? allItems.filter((item) => item.id === only) : allItems;
  if (!items.length) throw new Error('未找到待处理案例');
  if (!only && Object.keys(resolutions).some((id) => !allItems.some((item) => item.id === id))) throw new Error('补全表含当前来源不存在的编号');
  fs.mkdirSync(outputDir, { recursive: true });
  const fingerprint = hash(JSON.stringify({ script_sha256: hash(fs.readFileSync(fileURLToPath(import.meta.url))), policy, items: items.map((item) => [item.id, item.case_file_sha256, item.image_evidence]), resolutions, acceptConfirmed }));
  const existingIndex = path.join(outputDir, '_排盘索引.json');
  if (fs.existsSync(existingIndex) && readJson(existingIndex).run_input_sha256 !== fingerprint) {
    throw new Error('输出目录已有不同输入或设置的批次；请指定新的输出目录保留旧盘');
  }
  const rows = [], special = [], template = {};
  for (const item of items) {
    let artifact = {
      schema: 'staged-case-chart-v1', case_id: item.id, stage: '初级资料', official_library_eligible: false,
      status: 'needs_resolution', usable_for_batch_analysis: false,
      source: { file: item.filename, absolute_file: path.resolve(inputDir, item.filename), locator: item.source_locator, shared_original_group: item.shared_original_group, case_file_sha256: item.case_file_sha256, original_time: item.original_time, source_text_sha256: item.source_text_sha256, image_evidence: item.image_evidence },
      time: item.parsed_time, time_selection: item.time_selection,
      policy: { ...policy, source_status: 'explicit_batch_assumptions_not_source_facts' },
      source_settings: item.source_settings, effective_settings: { ...policy.settings, ...item.source_settings },
      issues: [...item.issues], resolution: null, chart_input: null, facts: null,
    };
    try {
      const resolved = resolvedInput(item, resolutions[item.id], policy, acceptConfirmed);
      artifact.resolution = resolved.resolution;
      if (resolved.issue) artifact.issues.push(resolved.issue);
      if (resolved.input) {
        const request = { mode: 'datetime', ...resolved.input, timezone: policy.timezone, time_basis: policy.time_basis, settings: { ...policy.settings, ...item.source_settings }, participants: [] };
        const result = await createChart(request);
        const errors = [...result.validation.errors];
        if (!result.validation.ok && !errors.length) errors.push({ code: 'ENGINE_VALIDATION_REJECTED', message: '引擎未通过校验' });
        if (item.constraints.day_pillar && item.constraints.day_pillar !== result.facts.day_pillar) errors.push({ code: 'DAY_PILLAR_CONSTRAINT_MISMATCH', message: '补全日期与原文干支日不符' });
        if (item.parsed_time.hour_pillar && item.parsed_time.hour_pillar !== result.facts.hour_pillar) errors.push({ code: 'HOUR_PILLAR_CONSTRAINT_MISMATCH', message: '补全时间与原文时柱不符' });
        const sourceComparison = { pillars: item.constraints.source_pillars, generated_pillars: result.facts.pillars, month_general: item.constraints.source_month_general, generated_month_general: result.facts.month_general };
        if (sourceComparison.pillars && JSON.stringify(sourceComparison.pillars) !== JSON.stringify(result.facts.pillars)) errors.push({ code: 'SOURCE_PILLARS_MISMATCH', message: '程序四柱与初级资料转录的题干四柱不一致，须复核图源或历法约定' });
        if (sourceComparison.month_general && sourceComparison.month_general !== result.facts.month_general) errors.push({ code: 'SOURCE_MONTH_GENERAL_MISMATCH', message: '程序月将与初级资料转录的月将不一致，须复核图源或换将约定' });
        artifact = {
          ...artifact, status: errors.length ? 'chart_validation_blocked' : 'generated_under_recorded_assumptions',
          usable_for_batch_analysis: !errors.length, chart_input: result.input, facts: chartFacts(result),
          validation: { ...result.validation, ok: !errors.length, status: errors.length ? 'blocked' : result.validation.status, errors },
          conventions: result.conventions, engine: result.engine, provenance: result.provenance,
          source_comparison: sourceComparison,
          historical_date_independently_verified: false,
        };
      }
    } catch (error) {
      artifact.status = 'error';
      artifact.issues.push(error.code || 'BATCH_CASE_ERROR');
      artifact.error = error.message;
    }
    writeJson(path.join(outputDir, `${item.id}.json`), artifact);
    rows.push({ case_id: item.id, file: `${item.id}.json`, status: artifact.status, usable_for_batch_analysis: artifact.usable_for_batch_analysis });
    if (!artifact.usable_for_batch_analysis) {
      special.push({ ...item, chart_status: artifact.status, error: artifact.error || null, resolution: artifact.resolution, suggestion: '保留原字段；只用题干约束与外部来源补全，禁止用反馈倒推。没有唯一依据则保持未决。' });
      template[item.id] = { status: 'proposed', case_file_sha256: item.case_file_sha256, datetime: null, method: null, evidence: '', reviewed_by: '', candidate_dates: [], missing_fields: item.issues, constraints: item.constraints };
    }
    console.log(`${item.id}: ${artifact.status}`);
  }
  const counts = rows.reduce((acc, row) => ({ ...acc, [row.status]: (acc[row.status] || 0) + 1 }), {});
  const index = { schema: 'staged-chart-batch-v1', run_input_sha256: fingerprint, source_directory: path.resolve(inputDir), engine_root: engineRoot, policy, total: rows.length, analysis_usable: rows.filter((row) => row.usable_for_batch_analysis).length, counts, files: rows };
  writeJson(existingIndex, index);
  writeJson(path.join(outputDir, '_特殊案例.json'), { schema: 'staged-chart-unresolved-v1', count: special.length, cases: special });
  writeJson(path.join(outputDir, '_日期方法补全.template.json'), { schema: 'staged-chart-resolutions-v1', warning: 'AI只能填proposed；人工核对后改confirmed，另以--accept-confirmed明确启用。确认标记不等于外部真实性证明。', resolutions: template });
  return index;
}

function parseArgs(args) {
  const opts = {};
  for (let i = 0; i < args.length; i++) {
    const name = args[i];
    if (!name.startsWith('--')) throw new Error(`无法识别参数：${name}`);
    if (name === '--accept-confirmed') { opts.acceptConfirmed = true; continue; }
    if (!['--input', '--output', '--policy', '--engine-root', '--resolutions', '--case', '--start', '--end', '--day-pillar', '--image-ledger', '--source-root'].includes(name)) throw new Error(`未知参数：${name}`);
    if (!args[i + 1] || args[i + 1].startsWith('--')) throw new Error(`${name}缺值`);
    opts[name.slice(2)] = args[++i];
  }
  return opts;
}

async function main() {
  const [command = 'help', ...args] = process.argv.slice(2);
  if (command === 'help') {
    console.log('node tools/batch-case-charts.mjs build --input <案例目录> --output <新输出目录> [--policy <JSON>] [--engine-root <工作流目录>] [--resolutions <JSON> --accept-confirmed] [--case <初级编号>]\nnode tools/batch-case-charts.mjs candidates --start YYYY-MM-DD --end YYYY-MM-DD --day-pillar 丁巳 --output <JSON> [--engine-root <工作流目录>]\n候选查询必须指定范围，最长366天；不会把候选自动认定为历史日期。');
    return;
  }
  if (!['build', 'candidates'].includes(command)) throw new Error('仅支持build、candidates、help');
  const opts = parseArgs(args);
  const engineRoot = path.resolve(opts['engine-root'] || path.join(project, 'materials/vendor/liuren-chart-legacy-20261102'));
  const adapter = await import(pathToFileURL(path.join(engineRoot, 'adapters', 'chart.mjs')).href);
  if (command === 'candidates') {
    if (!opts.start || !opts.end || !opts['day-pillar'] || !opts.output) throw new Error('candidates需要--start、--end、--day-pillar、--output');
    const result = await adapter.calendarCandidates({ start: opts.start, end: opts.end, day_pillars: [opts['day-pillar']] });
    const out = path.resolve(opts.output);
    if (fs.existsSync(out)) throw new Error('候选输出文件已存在，请换名以保留上次结果');
    fs.mkdirSync(path.dirname(out), { recursive: true });
    writeJson(out, { ...result, historical_date_selected: null, warning: '所列为指定范围内所有匹配日；范围本身需来源依据。日柱和时柱约束不证明唯一历史时间。' });
    console.log(`候选日期：${result.days.length}，未选择历史日期。`);
    return;
  }
  if (!opts.input || !opts.output) throw new Error('build需要--input和--output');
  const result = await buildBatch({
    inputDir: path.resolve(opts.input), outputDir: path.resolve(opts.output), engineRoot,
    policy: opts.policy ? readJson(opts.policy) : defaultPolicy,
    resolutions: opts.resolutions ? readJson(opts.resolutions).resolutions : {},
    acceptConfirmed: opts.acceptConfirmed || false, only: opts.case || null, createChart: adapter.createChart,
    imageLedger: opts['image-ledger'] ? readJson(opts['image-ledger']) : null,
    sourceRoot: opts['source-root'] ? path.resolve(opts['source-root']) : null,
  });
  console.log(JSON.stringify({ total: result.total, analysis_usable: result.analysis_usable, counts: result.counts }));
  if (result.counts.error || result.counts.chart_validation_blocked) process.exitCode = 1;
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main().catch((error) => { console.error(error.message); process.exitCode = 1; });
}
