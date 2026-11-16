// Source-bound reconstruction via the existing engine. No algorithm replacement.
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { runChart, isEntryPoint } from './liuren-direct.mjs';

export const ROOT = fileURLToPath(new URL('../', import.meta.url));
export const OUTPUT = 'output/liuren-book-cases-20261102/reconstructions';
export const ENGINE_REFERENCE = 'docs/六壬知识整理-20261102/引擎古例参考源/古例原始对象.json';
const ENGINE_MARKDOWN = 'docs/六壬知识整理-20261102/引擎古例参考源/古例全文.md';
const MANIFEST = 'tools/liuren-direct/legacy-engine-manifest.json';
const BOOK_SOURCES = new Set([
  '书籍库/现代著作/当代壬占汇选第五版.md', '书籍库/现代著作/《壬占汇选》.txt',
  '书籍库/经典古籍/唐宋/六壬断案-宋-邵彦和.txt', '书籍库/北海闲人/毕法赋全解-正式整理本.md',
  '课程写作/整理本/毕法赋全解/原始资料/毕法赋全解DeepSeek转录.md',
  '课程写作/整理本/毕法赋全解/校勘记录.md',
]);
const ROLES = new Set(['原书断语', '原载反馈', '原载作答', '后人注解', '旧AI归纳', '本轮解释']);
const OPTIONS = { guiren: ['甲戊庚牛羊', '甲羊戊庚牛'], zhouye: ['昼贵', '夜贵'], shehai: ['孟仲季', '深度'] };
const hash = value => crypto.createHash('sha256').update(value).digest('hex');
const object = value => value && typeof value === 'object' && !Array.isArray(value);
function fail(code, message) { throw Object.assign(new Error(message), { code }); }
function requireObject(value, name) { if (!object(value)) fail('INVALID_REQUEST', `${name}须为对象。`); }
function canonical(value) {
  const aliases = { 螣蛇: '腾蛇', 蛇: '腾蛇', 常: '太常', 空: '天空', 后: '天后', 阴: '太阴', 虎: '白虎',
    龙: '青龙', 合: '六合', 勾: '勾陈', 朱: '朱雀', 玄: '玄武', 贵: '贵人' };
  return typeof value === 'string' ? aliases[value] || value : value;
}

export async function projectPath(root, relative, { existing = true } = {}) {
  if (typeof relative !== 'string' || relative.includes('\\') || relative.includes(':') || path.posix.isAbsolute(relative)
      || relative.split('/').some(x => x === '..' || x.startsWith('.')) || path.posix.normalize(relative) !== relative)
    fail('UNSAFE_PATH', '只接受规范项目相对路径，拒绝配置、绝对路径和越界。');
  const base = await fs.realpath(root);
  const target = path.resolve(base, ...relative.split('/'));
  if (!target.startsWith(base + path.sep)) fail('UNSAFE_PATH', '路径越出项目。');
  let current = base;
  for (const segment of relative.split('/')) {
    current = path.join(current, segment);
    try { if ((await fs.lstat(current)).isSymbolicLink()) fail('UNSAFE_PATH', '拒绝重定向链接。'); }
    catch (error) { if (error.code !== 'ENOENT') throw error; if (existing) throw error; }
  }
  return target;
}

export async function verifyEvidence(refs, { root = ROOT, allowFeedback = true } = {}) {
  if (!Array.isArray(refs) || !refs.length) fail('MISSING_EVIDENCE', '须有连续原文证据。');
  const checked = [];
  for (const ref of refs) {
    requireObject(ref, 'evidence_ref');
    if (ref.path === ENGINE_MARKDOWN) await verifyReferenceExport(root);
    else if (!BOOK_SOURCES.has(ref.path)) fail('UNAPPROVED_SOURCE', '证据须指向批准原书、毕法校勘或已核链的固定古例全文。');
    if (!ROLES.has(ref.role) || (!allowFeedback && ref.role === '原载反馈')) fail('INVALID_EVIDENCE_ROLE', '盘式约束不能由现实反馈选择；须用原载盘式/断语的可核证据。');
    const bytes = await fs.readFile(await projectPath(root, ref.path));
    if (hash(bytes) !== ref.sha256) fail('SOURCE_CHANGED', `${ref.path}原源hash变化。`);
    // All current approved reconstruction sources are UTF-8. Do not replace bad bytes.
    const text = new TextDecoder('utf-8', { fatal: true }).decode(bytes).replace(/^\uFEFF/, '');
    const lines = text.split(/\r\n|\n|\r/); if (lines.at(-1) === '') lines.pop();
    if (!Number.isInteger(ref.line_start) || !Number.isInteger(ref.line_end)
        || ref.line_start < 1 || ref.line_end < ref.line_start || ref.line_end > lines.length)
      fail('INVALID_SOURCE_RANGE', '证据行号越界。');
    if (lines.slice(ref.line_start - 1, ref.line_end).join('\n') !== ref.quote)
      fail('QUOTE_MISMATCH', '证据不是该连续范围的完整原文。');
    checked.push(structuredClone(ref));
  }
  return checked;
}

async function currentEngineFingerprint(root) {
  const manifestBytes = await fs.readFile(await projectPath(root, MANIFEST));
  const manifest = JSON.parse(manifestBytes);
  const adapterFiles = ['tools/liuren_book_reconstruction.mjs', 'tools/liuren-direct.mjs', 'tools/liuren-direct/chart.mjs',
    'tools/liuren-direct/legacy-engine-worker.mjs', MANIFEST];
  const adapters = [];
  for (const relative of adapterFiles) adapters.push({ path: relative, sha256: hash(await fs.readFile(await projectPath(root, relative))) });
  if (!Array.isArray(manifest.files) || !manifest.files.length) fail('INVALID_ENGINE_MANIFEST', '引擎manifest缺少原文件指纹。');
  for (const expected of manifest.files) {
    const bytes = await fs.readFile(await projectPath(root, `排盘工具魔改/${expected.path}`));
    if (hash(bytes) !== expected.sha256) fail('ENGINE_SOURCE_CHANGED', `原引擎${expected.path}与manifest不同，停止复用或计算。`);
  }
  return { engine_id: manifest.engine_id, manifest_hash: hash(JSON.stringify(manifest)), adapter_files: adapters,
           adapter_hash: hash(JSON.stringify(adapters)), original_files: manifest.files, original_files_verified: true,
           algorithm_modified: false, network: false };
}

// Verify the persisted raw record as well as the summary; missing or changed raw
// evidence must never make a cached reconstruction appear reproducible.
async function verifyArchive(candidate, requestId, root, fingerprint) {
  const archive = candidate.archive;
  if (!archive || typeof archive.path !== 'string') fail('MISSING_RAW_ARCHIVE', '持久复原须有原始引擎归档。');
  const base = await fs.realpath(root);
  const relative = path.relative(base, archive.path).split(path.sep).join('/');
  if (!relative.startsWith(`${OUTPUT}/raw/${requestId}/`)) fail('UNSAFE_RAW_ARCHIVE', '原始归档路径不属于该请求专用目录。');
  let bytes;
  try { bytes = await fs.readFile(await projectPath(root, relative)); }
  catch (error) { if (error.code === 'ENOENT') fail('RAW_ARCHIVE_MISSING', '原始引擎归档缺失，停止复用。'); throw error; }
  if (hash(bytes) !== archive.sha256) fail('RAW_ARCHIVE_CHANGED', '原始引擎归档hash变化，停止复用。');
  const record = JSON.parse(bytes);
  const { _direct: metadata, ...raw } = record;
  if (!metadata || hash(JSON.stringify(raw)) !== metadata.raw_sha256 || metadata.raw_sha256 !== archive.raw_sha256)
    fail('RAW_RECORD_CHANGED', '原始页面数据与归档元数据指纹不一致。');
  for (const key of ['input', 'facts', 'validation', 'conventions', 'provenance'])
    if (JSON.stringify(candidate[key]) !== JSON.stringify(metadata[key])) fail('RAW_SUMMARY_MISMATCH', `候选${key}与原始归档不一致。`);
  const engine = metadata.engine;
  if (engine?.id !== fingerprint.engine_id || engine?.manifest_hash !== fingerprint.manifest_hash
      || engine?.algorithm_modified !== false || engine?.network !== false || engine?.fallback !== false
      || candidate.provenance?.engine_hash_verified !== true)
    fail('UNVERIFIED_ENGINE_PROVENANCE', '原始归档引擎身份或原源验证声明不符。');
  if (candidate.engine && JSON.stringify(candidate.engine) !== JSON.stringify(engine))
    fail('RAW_SUMMARY_MISMATCH', '候选引擎身份与原始归档不一致。');
  return engine;
}

export async function verifyReferenceExport(root = ROOT) {
  const bytes = await fs.readFile(await projectPath(root, ENGINE_REFERENCE));
  const source = JSON.parse(bytes);
  if (source.schema !== 'liuren-engine-ancient-reference-v1' || source.source?.path !== '排盘工具魔改/js/data.js'
      || source.source?.array !== 'GuAnLi2' || !Array.isArray(source.entries) || source.count !== source.entries.length)
    fail('INVALID_ENGINE_REFERENCE', '固定古例导出源结构不符。');
  const engineBytes = await fs.readFile(await projectPath(root, source.source.path));
  const manifest = JSON.parse(await fs.readFile(await projectPath(root, MANIFEST), 'utf8'));
  if (hash(engineBytes) !== source.source.sha256 || manifest.files.find(x => x.path === 'js/data.js')?.sha256 !== source.source.sha256)
    fail('ENGINE_REFERENCE_DRIFT', '古例导出与当前原引擎data.js指纹不一致。');
  const mdBytes = await fs.readFile(await projectPath(root, ENGINE_MARKDOWN));
  const markdown = mdBytes.toString('utf8');
  const blocks = [...markdown.matchAll(/^```json\n(\{[\s\S]*?\n\})\n```\s*$/gm)].map(x => JSON.parse(x[1]));
  const headings = [...markdown.matchAll(/^## ENGINE-ANCIENT-(\d+)\s*$/gm)].map(x => x[1]);
  if (!markdown.includes(source.source.sha256) || blocks.length !== source.entries.length || headings.length !== source.entries.length
      || headings.some((x, i) => x !== String(i + 1).padStart(4, '0'))
      || JSON.stringify(blocks) !== JSON.stringify(source.entries))
    fail('ENGINE_EXPORT_ROUNDTRIP', '古例全文、原对象覆盖/顺序/内容不一致。');
  return { source, export_sha256: hash(bytes), markdown_sha256: hash(mdBytes), roundtrip_equal: true };
}

async function engineReference(ref, root) {
  requireObject(ref, 'engine_reference');
  if (ref.same_event_review_state !== 'source_checked' || typeof ref.same_event_reason !== 'string' || !ref.same_event_reason.trim())
    fail('UNREVIEWED_EVENT_MATCH', '古例同案关系须有明确逐案核对声明与理由，不能仅靠序号/标题匹配。');
  await verifyEvidence(ref.match_evidence, { root, allowFeedback: false });
  const exported = await verifyReferenceExport(root);
  if (ref.sha256 !== exported.export_sha256) fail('ENGINE_REFERENCE_CHANGED', '古例参考源hash不符。');
  const source = exported.source;
  if (source.schema !== 'liuren-engine-ancient-reference-v1' || source.source?.path !== '排盘工具魔改/js/data.js'
      || !Array.isArray(source.entries) || !Number.isInteger(ref.index) || ref.index < 0 || ref.index >= source.entries.length)
    fail('INVALID_ENGINE_REFERENCE', '古例参考源结构或0起序号无效。');
  const entry = source.entries[ref.index];
  const p = entry.sizhu;
  if (!object(p) || ['yg', 'yz', 'mz', 'dg', 'dz', 'hz', 'yuejiang'].some(k => typeof p[k] !== 'string' || !p[k]))
    fail('INCOMPLETE_ENGINE_REFERENCE', '古例sizhu不足，不猜补参数。');
  const input = { mode: 'manual-pillars', pillars: { year: p.yg + p.yz, month_branch: p.mz,
      day: p.dg + p.dz, hour_branch: p.hz }, month_general: p.yuejiang,
    settings: Object.fromEntries(['yuejiang', 'guiren', 'zhouye', 'shehai'].filter(k => entry[k] !== undefined).map(k => [k, entry[k]])) };
  return { input, source: { path: ENGINE_REFERENCE, sha256: exported.export_sha256, source_index: ref.index,
      source_id: entry.id ?? null, engine_source: source.source, curated_input_is_original_fact: false,
      same_event_review_state: ref.same_event_review_state, same_event_reason: ref.same_event_reason,
      match_evidence: ref.match_evidence, source_cundang: entry.cundang,
      ignored_placeholder_fields: { Date: entry.Date, Time: entry.Time, tys: entry.tys },
      note: '只使用显式sizhu/settings；Date/Time/tys占位不作为历史日期。古例整理输入仍须与原书核对。' } };
}

function fieldValue(input, field) {
  return field.split('.').reduce((value, key) => object(value) && Object.hasOwn(value, key) ? value[key] : undefined, input);
}

export async function prepareReconstruction(request, { root = ROOT } = {}) {
  requireObject(request, 'request');
  const allowed = new Set(['schema', 'id', 'case_id', 'input', 'input_evidence', 'input_sources', 'engine_reference',
    'settings_review', 'settings_mode', 'max_candidates', 'constraints', 'notes', 'original_source_condition']);
  for (const key of Object.keys(request)) if (!allowed.has(key)) fail('UNKNOWN_PARAMETER', `不支持${key}，不静默忽略。`);
  if (request.schema !== 'liuren-book-reconstruction-request-v1' || !/^RC26-[A-Za-z0-9-]{1,58}$/.test(request.id || '')
      || !/^BK26-(MODERN|ANCIENT|SHAO|BIFA)-\d{3,}$/.test(request.case_id || '')) fail('INVALID_ID', '复原请求schema/稳定ID/案例ID无效。');
  let input, sourceProvenance;
  if (request.engine_reference) {
    const reference = await engineReference(request.engine_reference, root);
    input = reference.input; sourceProvenance = reference.source;
    if (request.input) {
      requireObject(request.input, 'input');
      for (const key of Object.keys(request.input)) if (!['mode', 'pillars', 'month_general', 'label', 'settings'].includes(key))
        fail('CONFLICTING_ENGINE_INPUT', `古例输入不接受额外${key}；占位日期不能当历史日期。`);
      for (const key of ['mode', 'pillars', 'month_general']) if (request.input[key] !== undefined && JSON.stringify(request.input[key]) !== JSON.stringify(input[key]))
        fail('CONFLICTING_ENGINE_INPUT', '显式input与古例原输入不同；请分开提交候选，不覆盖原古例。');
      for (const [key, value] of Object.entries(request.input.settings || {})) if (input.settings[key] !== value)
        fail('CONFLICTING_ENGINE_INPUT', '显式设置与古例整理输入冲突；须分开说明候选。');
    }
  } else {
    requireObject(request.input, 'input');
    input = structuredClone(request.input);
    const refs = await verifyEvidence(request.input_evidence, { root, allowFeedback: false });
    if (!['datetime', 'manual-pillars'].includes(input.mode)) fail('UNSUPPORTED_MODE', '只复原明确datetime或manual-pillars，不接受now或补猜。');
    const fields = input.mode === 'manual-pillars' ? ['pillars.year', 'pillars.month_branch', 'pillars.day', 'pillars.hour_branch', 'month_general'] : ['datetime'];
    const bindings = Array.isArray(request.input_sources) ? request.input_sources : object(request.input_sources)
      ? Object.entries(request.input_sources).map(([field, note]) => ({ field, value: fieldValue(input, field), note,
          evidence_ref_indexes: refs.map((_, i) => i) })) : null;
    if (!bindings) fail('MISSING_INPUT_BINDINGS', '须逐字段说明输入来源input_sources。');
    for (const field of fields) {
      const value = fieldValue(input, field);
      const binding = bindings.find(x => object(x) && x.field === field);
      if (typeof value !== 'string' || !value || !binding || binding.value !== value || typeof binding.note !== 'string' || !binding.note.trim()
          || !Array.isArray(binding.evidence_ref_indexes) || !binding.evidence_ref_indexes.length
          || binding.evidence_ref_indexes.some(i => !Number.isInteger(i) || i < 0 || i >= refs.length))
        fail('MISSING_INPUT_BINDING', `${field}缺值/来源绑定，禁止猜补。`);
    }
    sourceProvenance = { input_evidence: refs, input_sources: bindings,
      identity: '字段值由负责人依连续原文明确摘录；机械核引文不证明语义摘录正确。' };
  }
  if (input.participants?.length || input.mode === 'now' || input.mode === 'manual-pillars' && input.datetime !== undefined)
    fail('UNSUPPORTED_INPUT', '复原不计算未经核定的年命，不接受now或用显示日期冒充手工课历史时间。');
  const reviews = request.settings_review || {};
  requireObject(reviews, 'settings_review');
  for (const key of Object.keys(reviews)) if (!(key in OPTIONS) && key !== 'yuejiang' && key !== 'state') fail('INVALID_SETTING_REVIEW', `未知设置核对项${key}。`);
  const unverified = [];
  for (const key of Object.keys(OPTIONS)) {
    const review = reviews[key];
    if (review?.state === 'source_checked') {
      if (typeof review.note !== 'string' || !review.note.trim()) fail('INVALID_SETTING_REVIEW', '已核设置须有核对说明。');
      await verifyEvidence(review.evidence_refs, { root, allowFeedback: false });
      if (input.settings?.[key] === undefined) fail('MISSING_REVIEWED_SETTING', `已核${key}却无输入值。`);
    } else unverified.push(key);
  }
  if (!Array.isArray(request.constraints) || !request.constraints.length) fail('MISSING_CONSTRAINTS', '须提供原载可核盘式约束；不以反馈选盘。');
  const constraints = [];
  for (const constraint of request.constraints) {
    requireObject(constraint, 'constraint');
    if (!/^(?:transmission_sequence|day_pillar|month_general|chart_types|transmissions\.[012]\.(?:diZhi|tianjiang)|lessons\.[0123]\.(?:tianpan|dizhi|tianjiang)|heaven_earth\.(?:[子丑寅卯辰巳午未申酉戌亥]|[0-9]|1[01])\.(?:tian|tianjiang)|nobleman\.(?:heaven_branch|earth_position|direction))$/.test(constraint.field || ''))
      fail('UNSUPPORTED_CONSTRAINT', '只比较白名单盘式字段，不接受结果/反馈或任意对象属性。');
    if (constraint.extraction_review_state !== 'source_checked' || !(typeof constraint.expected === 'string' || Array.isArray(constraint.expected) && constraint.expected.every(x => typeof x === 'string')))
      fail('UNREVIEWED_CONSTRAINT', '约束须为负责人核原文的显式文本/文本数组。');
    if (!['equals', 'contains'].includes(constraint.operator || 'equals')) fail('UNSUPPORTED_COMPARISON', '只支持equals或contains。');
    await verifyEvidence(constraint.evidence_refs, { root, allowFeedback: false });
    constraints.push(structuredClone(constraint));
  }
  const mode = request.settings_mode || 'enumerate_unverified';
  if (!['enumerate_unverified', 'preserve_unverified'].includes(mode)) fail('INVALID_SETTING_MODE', '设置模式无效。');
  let candidates = [structuredClone(input)];
  if (mode === 'enumerate_unverified') for (const key of unverified) candidates = candidates.flatMap(candidate =>
    OPTIONS[key].map(value => ({ ...structuredClone(candidate), settings: { ...candidate.settings, [key]: value } })));
  const cap = request.max_candidates ?? 8;
  if (!Number.isInteger(cap) || cap < 1 || cap > 16 || candidates.length > cap) fail('CANDIDATE_LIMIT', '候选数量超过明确预算，不静默截取或选择有利盘。');
  return { request: structuredClone(request), candidates, sourceProvenance, constraints,
    unverified_settings: unverified, settings_mode: mode,
    unresolved: [...unverified.map(x => `${x}原书设置未核；候选全部保留，不依据反馈选择。`),
      '引擎结构通过不等于穷尽验证全部排盘算法；仍须负责人核原文与复原关系。',
      '原图/原文残损状态保持；本模块不自动改complete，也不能复原遗失的断语。'] };
}

export function compareFacts(facts, constraints) {
  return constraints.map(constraint => {
    let actual;
    if (constraint.field.startsWith('heaven_earth.')) {
      const [, branch, field] = constraint.field.split('.');
      actual = /^\d+$/.test(branch) ? facts.heaven_earth?.[Number(branch)]?.[field] : facts.heaven_earth?.find(x => x.di === branch)?.[field];
    } else actual = constraint.field.split('.').reduce((value, key) => value?.[key], facts);
    const expected = constraint.expected;
    let match;
    if ((constraint.operator || 'equals') === 'contains') match = Array.isArray(actual)
      && (Array.isArray(expected) ? expected : [expected]).every(x => actual.map(canonical).includes(canonical(x)));
    else match = JSON.stringify(Array.isArray(actual) ? actual.map(canonical) : canonical(actual))
      === JSON.stringify(Array.isArray(expected) ? expected.map(canonical) : canonical(expected));
    return { field: constraint.field, expected, actual: actual ?? null, match,
      ...(constraint.source_conflict_note ? { source_conflict_note: constraint.source_conflict_note } : {}),
      evidence_refs: constraint.evidence_refs, extraction_review_state: constraint.extraction_review_state,
      identity: '原载盘式观察对照，不是结果反馈或预测命中率' };
  });
}

export async function reconstruct(request, { root = ROOT, engineRunner = runChart, persist = true } = {}) {
  const prepared = await prepareReconstruction(request, { root });
  const fingerprint = await currentEngineFingerprint(root);
  const requestHash = hash(JSON.stringify(request));
  const relative = `${OUTPUT}/${request.id}.json`;
  const target = await projectPath(root, relative, { existing: false });
  if (persist) {
    let existing = null;
    try { existing = JSON.parse(await fs.readFile(target, 'utf8')); }
    catch (error) { if (error.code !== 'ENOENT') throw error; }
    if (existing) {
      const { result_body_sha256: saved, ...body } = existing;
      if (saved !== hash(JSON.stringify(body))) fail('RESULT_MODIFIED', '现有复原结果被改动，禁止覆盖。');
      if (existing.request_sha256 !== requestHash || existing.engine_fingerprint.adapter_hash !== fingerprint.adapter_hash)
        fail('RESULT_CONFLICT', '同ID已有不同请求/引擎结果，请用新稳定ID另存，不覆盖历史。');
      for (const candidate of existing.candidates) await verifyArchive(candidate, request.id, root, fingerprint);
      return { ...existing, reused: true, output_path: relative };
    }
  }
  const candidates = [];
  for (const [index, input] of prepared.candidates.entries()) {
    const id = `${request.id}-C${String(index + 1).padStart(2, '0')}`;
    const result = await engineRunner({ ...input, label: id.slice(-32) }, {
      archiveRoot: await projectPath(root, `${OUTPUT}/raw/${request.id}`, { existing: false }), persist });
    const comparisons = compareFacts(result.facts || {}, prepared.constraints);
    const candidate = { id, input: result.input, engine: result.engine, facts: result.facts,
      validation: result.validation, conventions: result.conventions, provenance: result.provenance,
      archive: result.archive, comparisons,
      all_constraints_match: comparisons.every(x => x.match), engine_structure_ok: result.ok === true };
    if (persist) candidate.engine = await verifyArchive(candidate, request.id, root, fingerprint);
    candidates.push(candidate);
  }
  const matches = candidates.filter(x => x.engine_structure_ok && x.all_constraints_match).map(x => x.id);
  const result = { schema: 'liuren-book-reconstruction-result-v1', id: request.id, case_id: request.case_id,
    request_sha256: requestHash, engine_fingerprint: fingerprint, input_provenance: prepared.sourceProvenance,
    original_source_condition: request.original_source_condition || '原源完整性按书案登记，原图残损不抹去',
    state: matches.length ? (prepared.unverified_settings.length ? 'candidate_settings_unverified' : 'engine_reconstructed_pending_semantic_review') : 'constraint_conflict',
    settings_review: request.settings_review || {}, unverified_settings: prepared.unverified_settings,
    settings_mode: prepared.settings_mode, candidates, matching_candidate_ids: matches,
    selected_candidate_id: null, outcome_feedback_used_for_selection: false,
    semantic_review_state: 'pending', book_case_complete_changed: false,
    unresolved: prepared.unresolved, generated_at: new Date().toISOString(),
    independent_prediction_validation_count: 0 };
  result.result_body_sha256 = hash(JSON.stringify(result));
  if (persist) {
    await fs.mkdir(path.dirname(target), { recursive: true });
    await fs.writeFile(target, JSON.stringify(result, null, 2) + '\n', { encoding: 'utf8', flag: 'wx' });
  }
  return { ...result, reused: false, output_path: persist ? relative : null };
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length !== 2 || args[0] !== '--request') fail('CLI_ARGUMENT', 'node tools/liuren_book_reconstruction.mjs --request <项目内请求JSON>');
  if (!args[1].startsWith('output/liuren-book-cases-20261102/') || !args[1].endsWith('.json')) fail('UNAPPROVED_REQUEST_PATH', '请求只读本轮专用output目录JSON。');
  const request = JSON.parse((await fs.readFile(await projectPath(ROOT, args[1]), 'utf8')).replace(/^\uFEFF/, ''));
  const result = await reconstruct(request);
  process.stdout.write(JSON.stringify({ id: result.id, case_id: result.case_id, state: result.state,
    output_path: result.output_path, candidates: result.candidates.length, matching_candidate_ids: result.matching_candidate_ids,
    selected_candidate_id: null, semantic_review_state: result.semantic_review_state,
    unverified_settings: result.unverified_settings, reused: result.reused }) + '\n');
  if (!result.matching_candidate_ids.length) process.exitCode = 2;
}

if (isEntryPoint(process.argv[1], import.meta.url)) main().catch(error => {
  process.stdout.write(JSON.stringify({ ok: false, error: { code: error.code || 'RECONSTRUCTION_ERROR', message: error.message } }) + '\n');
  process.exitCode = 2;
});
