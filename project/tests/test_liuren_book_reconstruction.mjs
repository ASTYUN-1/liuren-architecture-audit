import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { prepareReconstruction, reconstruct, verifyEvidence, verifyReferenceExport, compareFacts,
  projectPath, ENGINE_REFERENCE, OUTPUT } from '../tools/liuren_book_reconstruction.mjs';
import { verifyArtifact } from '../tools/liuren_book_reconstruction_verify.mjs';

const sha = value => crypto.createHash('sha256').update(value).digest('hex');
const SOURCE = '书籍库/北海闲人/毕法赋全解-正式整理本.md';
const MD = 'docs/六壬知识整理-20261102/引擎古例参考源/古例全文.md';
async function put(root, relative, data) {
  const target = path.join(root, relative); await fs.mkdir(path.dirname(target), { recursive: true });
  await fs.writeFile(target, data); return target;
}
async function fixture(t) {
  const root = await fs.mkdtemp(path.join(os.tmpdir(), 'liuren-book-reconstruction-'));
  t.after(() => fs.rm(root, { recursive: true, force: true }));
  const quote = '甲申年戌月丙子日戌时卯将，三传巳戌卯。';
  const sourceBytes = Buffer.from(quote + '\n'); await put(root, SOURCE, sourceBytes);
  const evidence = { path: SOURCE, sha256: sha(sourceBytes), line_start: 1, line_end: 1, quote, role: '原书断语' };
  const request = { schema: 'liuren-book-reconstruction-request-v1', id: 'RC26-TEST-001', case_id: 'BK26-BIFA-001',
    input: { mode: 'manual-pillars', pillars: { year: '甲申', month_branch: '戌', day: '丙子', hour_branch: '戌' }, month_general: '卯' },
    input_evidence: [evidence], input_sources: Object.fromEntries(['pillars.year', 'pillars.month_branch', 'pillars.day', 'pillars.hour_branch', 'month_general'].map(field => [field, '原载逐字段摘录；待人工复核语义。'])),
    constraints: [{ field: 'transmission_sequence', expected: '巳戌卯', evidence_refs: [evidence], extraction_review_state: 'source_checked' }] };
  const engineBytes = Buffer.from('// fixture engine data: never executed\n');
  await put(root, '排盘工具魔改/js/data.js', engineBytes);
  const manifest = { engine_id: 'fixture-original-engine', files: [{ path: 'js/data.js', sha256: sha(engineBytes) }] };
  await put(root, 'tools/liuren-direct/legacy-engine-manifest.json', JSON.stringify(manifest));
  for (const name of ['tools/liuren_book_reconstruction.mjs', 'tools/liuren-direct.mjs', 'tools/liuren-direct/chart.mjs', 'tools/liuren-direct/legacy-engine-worker.mjs']) await put(root, name, '// fixture adapter\n');
  const engine = { id: manifest.engine_id, manifest_hash: sha(JSON.stringify(manifest)), files: manifest.files,
    algorithm_modified: false, network: false, fallback: false };
  let calls = 0;
  const runner = async (input, { archiveRoot, persist }) => {
    calls++;
    const result = { ok: true, input, facts: { transmission_sequence: '巳戌卯', event_datetime: null },
      validation: { ok: true }, conventions: { manual_date_is_placeholder: true }, provenance: { engine_hash_verified: true } };
    if (persist) {
      const raw = { sanchuan: ['巳', '戌', '卯'] };
      const rawHash = sha(JSON.stringify(raw));
      const metadata = { ...result, engine, raw_sha256: rawHash }; delete metadata.ok;
      await fs.mkdir(archiveRoot, { recursive: true });
      const target = path.join(archiveRoot, `fixture-${calls}.json`);
      const bytes = Buffer.from(JSON.stringify({ ...raw, _direct: metadata }, null, 2) + '\n');
      await fs.writeFile(target, bytes);
      result.archive = { path: target, sha256: sha(bytes), raw_sha256: rawHash };
    }
    // The real direct result exposes engine identity inside the raw archive.
    return result;
  };
  return { root, request, evidence, runner, manifest, calls: () => calls };
}
const rejectsCode = (fn, code) => assert.rejects(fn, error => error.code === code);

test('unreviewed settings enumerate all eight combinations and preserve conflict notes', async t => {
  const f = await fixture(t); f.request.constraints[0].source_conflict_note = '主列与六亲列次序冲突，保留两者。';
  const prepared = await prepareReconstruction(f.request, { root: f.root });
  assert.equal(prepared.candidates.length, 8);
  assert.equal(new Set(prepared.candidates.map(x => JSON.stringify(x.settings))).size, 8);
  const result = await reconstruct(f.request, { root: f.root, engineRunner: f.runner, persist: false });
  assert.equal(result.selected_candidate_id, null); assert.equal(result.outcome_feedback_used_for_selection, false);
  assert.equal(result.semantic_review_state, 'pending'); assert.equal(result.book_case_complete_changed, false);
  assert.equal(result.candidates[0].comparisons[0].source_conflict_note, f.request.constraints[0].source_conflict_note);
  assert.equal(result.independent_prediction_validation_count, 0);
});

test('missing manual year and missing source binding are not guessed', async t => {
  const f = await fixture(t); delete f.request.input.pillars.year;
  await rejectsCode(() => prepareReconstruction(f.request, { root: f.root }), 'MISSING_INPUT_BINDING');
  f.request.input.pillars.year = '甲申'; delete f.request.input_sources['pillars.day'];
  await rejectsCode(() => prepareReconstruction(f.request, { root: f.root }), 'MISSING_INPUT_BINDING');
});

test('changed source bytes, altered quotation and unsafe paths fail closed', async t => {
  const f = await fixture(t);
  await rejectsCode(() => verifyEvidence([{ ...f.evidence, quote: '改写引文' }], { root: f.root }), 'QUOTE_MISMATCH');
  await rejectsCode(() => projectPath(f.root, '../outside.json'), 'UNSAFE_PATH');
  await rejectsCode(() => projectPath(f.root, '.codex/config.toml'), 'UNSAFE_PATH');
  await put(f.root, SOURCE, f.evidence.quote + '改\n');
  await rejectsCode(() => prepareReconstruction(f.request, { root: f.root }), 'SOURCE_CHANGED');
});

test('feedback evidence and unsupported constraint paths cannot select a chart', async t => {
  const f = await fixture(t);
  f.request.constraints[0].evidence_refs = [{ ...f.evidence, role: '原载反馈' }];
  await rejectsCode(() => prepareReconstruction(f.request, { root: f.root }), 'INVALID_EVIDENCE_ROLE');
  f.request.constraints[0].field = 'outcome.success';
  await rejectsCode(() => prepareReconstruction(f.request, { root: f.root }), 'UNSUPPORTED_CONSTRAINT');
});

test('candidate budget never silently truncates; reviewed setting needs source evidence', async t => {
  const f = await fixture(t); f.request.max_candidates = 4;
  await rejectsCode(() => prepareReconstruction(f.request, { root: f.root }), 'CANDIDATE_LIMIT');
  delete f.request.max_candidates; f.request.input.settings = { guiren: '甲戊庚牛羊' };
  f.request.settings_review = { guiren: { state: 'source_checked', note: '原载明确' } };
  await rejectsCode(() => prepareReconstruction(f.request, { root: f.root }), 'MISSING_EVIDENCE');
  f.request.settings_review.guiren.evidence_refs = [f.evidence];
  assert.equal((await prepareReconstruction(f.request, { root: f.root })).candidates.length, 4);
});

test('heaven-earth branch and numeric positions compare; general aliases are normalized', () => {
  const facts = { heaven_earth: [{ di: '子', tian: '巳' }], transmissions: [{ tianjiang: '螣蛇' }] };
  assert.equal(compareFacts(facts, [{ field: 'heaven_earth.子.tian', expected: '巳' }])[0].match, true);
  assert.equal(compareFacts(facts, [{ field: 'heaven_earth.0.tian', expected: '巳' }])[0].match, true);
  assert.equal(compareFacts(facts, [{ field: 'transmissions.0.tianjiang', expected: '蛇' }])[0].match, true);
});

test('persisted result reuses only intact raw records and recovers engine metadata', async t => {
  const f = await fixture(t);
  const first = await reconstruct(f.request, { root: f.root, engineRunner: f.runner });
  assert.equal(first.reused, false); assert.equal(first.candidates[0].engine.id, f.manifest.engine_id);
  const second = await reconstruct(f.request, { root: f.root, engineRunner: f.runner });
  assert.equal(second.reused, true); assert.equal(f.calls(), 8);
  await fs.appendFile(first.candidates[0].archive.path, '\n');
  await rejectsCode(() => reconstruct(f.request, { root: f.root, engineRunner: f.runner }), 'RAW_ARCHIVE_CHANGED');
  assert.equal(f.calls(), 8);
});

test('missing raw archive stops cache reuse instead of recomputing silently', async t => {
  const f = await fixture(t); const first = await reconstruct(f.request, { root: f.root, engineRunner: f.runner });
  await fs.unlink(first.candidates[0].archive.path);
  await rejectsCode(() => reconstruct(f.request, { root: f.root, engineRunner: f.runner }), 'RAW_ARCHIVE_MISSING');
  assert.equal(f.calls(), 8);
});

test('modified summary and same-ID changed request are preserved, never overwritten', async t => {
  const f = await fixture(t); await reconstruct(f.request, { root: f.root, engineRunner: f.runner });
  const changed = { ...f.request, notes: ['different request'] };
  await rejectsCode(() => reconstruct(changed, { root: f.root, engineRunner: f.runner }), 'RESULT_CONFLICT');
  const target = path.join(f.root, OUTPUT, `${f.request.id}.json`);
  const data = JSON.parse(await fs.readFile(target)); data.semantic_review_state = 'approved';
  await fs.writeFile(target, JSON.stringify(data));
  await rejectsCode(() => reconstruct(f.request, { root: f.root, engineRunner: f.runner }), 'RESULT_MODIFIED');
  assert.equal(f.calls(), 8);
});

test('current original engine files are rechecked even when a result is cached', async t => {
  const f = await fixture(t); await reconstruct(f.request, { root: f.root, engineRunner: f.runner });
  await put(f.root, '排盘工具魔改/js/data.js', '// changed engine');
  await rejectsCode(() => reconstruct(f.request, { root: f.root, engineRunner: f.runner }), 'ENGINE_SOURCE_CHANGED');
  assert.equal(f.calls(), 8);
});

test('engine reference requires explicit same-event review and ignores placeholder dates', async t => {
  const f = await fixture(t);
  const entry = { sizhu: { yg: '甲', yz: '申', mz: '戌', dg: '丙', dz: '子', hz: '戌', yuejiang: '卯' },
    Date: '2000-01-01', Time: '01:01', tys: 12345, cundang: { ws: '人工确认同案', dy: '原载断语', fk: '' },
    guiren: '甲戊庚牛羊', zhouye: '自动选择', shehai: '孟仲季' };
  const source = { schema: 'liuren-engine-ancient-reference-v1', source: { path: '排盘工具魔改/js/data.js',
    sha256: f.manifest.files[0].sha256, array: 'GuAnLi2' }, count: 1, entries: [entry] };
  const bytes = JSON.stringify(source, null, 2); await put(f.root, ENGINE_REFERENCE, bytes);
  await put(f.root, MD, `# 古例\n${source.source.sha256}\n\n## ENGINE-ANCIENT-0001\n\n\x60\x60\x60json\n${JSON.stringify(entry, null, 2)}\n\x60\x60\x60\n`);
  delete f.request.input; delete f.request.input_sources; delete f.request.input_evidence;
  f.request.engine_reference = { sha256: sha(bytes), index: 0, match_evidence: [f.evidence] };
  await rejectsCode(() => prepareReconstruction(f.request, { root: f.root }), 'UNREVIEWED_EVENT_MATCH');
  Object.assign(f.request.engine_reference, { same_event_review_state: 'source_checked', same_event_reason: '明确核对原载问事和日期字段。' });
  const prepared = await prepareReconstruction(f.request, { root: f.root });
  assert.equal(prepared.candidates.length, 8); assert.equal(prepared.candidates[0].pillars.year, '甲申');
  assert.equal(prepared.candidates[0].datetime, undefined); assert.equal(prepared.candidates[0].reference_datetime, undefined);
  assert.equal(prepared.sourceProvenance.ignored_placeholder_fields.Date, '2000-01-01');
  await put(f.root, MD, `${source.source.sha256}\n\x60\x60\x60json\n${JSON.stringify(entry, null, 2)}\n\x60\x60\x60\n`);
  await rejectsCode(() => verifyReferenceExport(f.root), 'ENGINE_EXPORT_ROUNDTRIP');
});

test('read-only B1 bridge verifies all raw archives and complete equivalent facts', async t => {
  const f = await fixture(t); const result = await reconstruct(f.request, { root: f.root, engineRunner: f.runner });
  const resultPath = `${OUTPUT}/${f.request.id}.json`;
  const requestPath = 'output/liuren-book-cases-20261102/test-request.json';
  await put(f.root, requestPath, JSON.stringify(f.request));
  const link = { id: f.request.id, result_path: resultPath, result_sha256: sha(await fs.readFile(path.join(f.root, resultPath))) };
  const review = { request_path: requestPath, request_sha256: sha(JSON.stringify(f.request)),
    excluded_setting_label_paths: [], equivalent_candidate_groups: [{ candidate_ids: result.matching_candidate_ids,
      structural_facts_sha256: sha(JSON.stringify(result.candidates[0].facts)) }] };
  const verified = await verifyArtifact({ root: f.root, link, case_id: f.request.case_id, review });
  assert.equal(verified.raw_archives_verified, 8); assert.equal(verified.groups.length, 1);
  assert.equal(verified.groups[0].candidate_ids.length, 8); assert.deepEqual(verified.groups[0].facts, result.candidates[0].facts);
  assert.equal(f.calls(), 8);
  review.excluded_setting_label_paths = ['transmission_sequence'];
  await assert.rejects(() => verifyArtifact({ root: f.root, link, case_id: f.request.case_id, review }), /只可排除三个/);
  review.excluded_setting_label_paths = [];
  await fs.unlink(result.candidates[0].archive.path);
  await rejectsCode(() => verifyArtifact({ root: f.root, link, case_id: f.request.case_id, review }), 'RAW_ARCHIVE_MISSING');
  assert.equal(f.calls(), 8);
});
