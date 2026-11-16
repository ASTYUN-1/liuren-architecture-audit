import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { parseTime, inspectCase, buildBatch, defaultPolicy } from '../batch-case-charts.mjs';

function source({ time = '2024年3月11日1:10', normalized = '2024-03-11 01:10', extra = '未注明', question = '占考试是否通过', feedback = '反馈：通过', id = 'raw-test-0001' } = {}) {
  return `<!-- RAW_META: 资料阶段=初级 -->
# 测试
## 1. 来源与状态
- 初级编号：${id}
- 原文定位：第1—4行
## 2. 起课信息与人物
- 起课时间原文：${time}
- 可直接规范化的时间：${normalized}
- 报数等其他起课信息：${extra}
- 题干原载课式信息：未提供
## 3. 背景、问题与要求
${question}
## 4. 明确标注的反馈
${feedback}
## 5. 作答及其他未核验内容
未提供
## 6. 待核事项
无
## 7. 完整原文
\`\`\`text
${time}
${question}
${feedback}
\`\`\`
`;
}
function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'case-chart-test-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  const inputDir = path.join(root, 'input');
  const outputDir = path.join(root, 'output');
  fs.mkdirSync(inputDir);
  return { root, inputDir, outputDir };
}
const fakeEngine = async (request) => ({
  input: request, facts: { day_pillar: '甲子', hour_pillar: '甲子', lessons: [1, 2, 3, 4], summary: '解释性断语', key_shensha: ['解释'] },
  validation: { ok: true, errors: [] }, engine: { id: 'test-engine' }, conventions: {}, provenance: {},
});

test('validates dates, normalizes only explicit minute precision', () => {
  assert.equal(parseTime('2002年7月1日10:4').datetime, '2002-07-01T10:04');
  assert.equal(parseTime('。2022年9月22日 11:52，').datetime, '2022-09-22T11:52');
  for (const text of ['2024年2月30日12:00', '2024年3月1日24:00', '2024年3月1日12:60']) assert.equal(parseTime(text).precision, 'invalid');
  assert.equal(parseTime('2024年9月11日15时').datetime, null);
  assert.equal(parseTime('2022年6月6日庚辰时').hour_pillar, '庚辰');
  assert.equal(parseTime('时间：丁巳日，伏吟局').issue, 'MISSING_CALENDAR_DATE');
});

test('accepts explicit Gregorian formats with lunar labels but refuses mixed candidate times', () => {
  for (const value of ['2026-09-27(八月十七) 14:10', '2026年09月27日 14时10分(八月十七)', '2026年9月27日(八月十七)14:10', '2026/09/27 14:10']) {
    assert.equal(parseTime(value).datetime, '2026-09-27T14:10');
  }
  assert.equal(parseTime('[当代]中国公历纪元2026年 2026年8月28日 9时24分 星期五 七月十六处暑 (正时, 甲戊庚牛羊、卯酉夜、孟仲季、交节换将)').datetime, '2026-08-28T09:24');
  assert.equal(parseTime('2026-07-26 15:34；另盘2026-07-26 15:36').datetime, null);
  assert.equal(parseTime('2026-09-27(八月十七) 14:10 猜测').datetime, null);
});

test('special methods and true-time markers in original chart metadata block ordinary generation', () => {
  assert.ok(inspectCase(source().replace('题干原载课式信息：未提供', '题干原载课式信息：活时起课 巳时'), 'raw-test-0001.md').issues.includes('SPECIAL_DIVINATION_METHOD'));
  assert.ok(inspectCase(source({ time: '2026-10-04 19:44 (真)' }), 'raw-test-0001.md').issues.includes('EXPLICIT_TIME_CONVENTION_NEEDS_REVIEW'));
  const item = inspectCase(source().replace('题干原载课式信息：未提供', '题干原载课式信息：所用的换将法为日躔换将，另一方法中气换将'), 'raw-test-0001.md');
  assert.equal(item.source_settings.yuejiang, '日躔换将');
});

test('image transcription requires matching time, source sequence, image hash and declared primary image', (t) => {
  const dirs = fixture(t);
  fs.mkdirSync(path.join(dirs.root, 'pan'));
  fs.writeFileSync(path.join(dirs.root, 'pan/002_1.jpg'), 'test-image-bytes');
  const sha256 = crypto.createHash('sha256').update('test-image-bytes').digest('hex');
  const imageLedger = { images: [{ file: 'pan/002_1.jpg', seq: 2, sha256, time_norm: '2024-03-11 01:10' }] };
  const text = source().replace('- 原文定位：', '- 来源名称：QQ / seq=2\n- 时间来源：题干盘图提取（pan/002_1.jpg）\n- 原文定位：').replace('```text\n2024年3月11日1:10', '```text\n作业发布时间另载');
  const inspect = (value = text) => inspectCase(value, 'raw-test-0001.md', { imageLedger, sourceRoot: dirs.root });
  assert.ok(!inspect().issues.includes('TIME_FIELD_SOURCE_MISMATCH'));
  assert.equal(inspect().image_evidence.independently_visually_verified_this_run, false);
  const multi = text.replace('- 起课时间原文：2024年3月11日1:10', '- 起课时间原文：2024年3月11日1:10（pan/002_1.jpg）；另盘 pan/002_2.jpg 记为 2024-03-11 01:20');
  assert.equal(inspect(multi).parsed_time.datetime, '2024-03-11T01:10');
  assert.equal(inspect(multi).time_selection.primary_image, 'pan/002_1.jpg');
  assert.equal(inspect(multi).issues.length, 0);
  assert.ok(inspect(text.replace('seq=2', 'seq=3')).issues.includes('IMAGE_EVIDENCE_INVALID'));
  assert.ok(inspect(text.replace('2024年3月11日1:10', '2024年3月11日2:10')).issues.includes('IMAGE_LEDGER_TIME_MISMATCH'));
  fs.writeFileSync(path.join(dirs.root, 'pan/002_1.jpg'), 'changed');
  assert.ok(inspect().issues.includes('IMAGE_EVIDENCE_INVALID'));
});

test('source pillar mismatch retains generated facts but prevents analysis eligibility', async (t) => {
  const dirs = fixture(t);
  fs.writeFileSync(path.join(dirs.inputDir, 'raw-test-0001.md'), source().replace('题干原载课式信息：未提供', '题干原载课式信息：四柱 丙午 丁酉 辛卯 己亥'));
  const result = await buildBatch({ ...dirs, createChart: fakeEngine });
  assert.equal(result.counts.chart_validation_blocked, 1);
  const chart = JSON.parse(fs.readFileSync(path.join(dirs.outputDir, 'raw-test-0001.json')));
  assert.ok(chart.facts);
  assert.ok(chart.validation.errors.some((e) => e.code === 'SOURCE_PILLARS_MISMATCH'));
});

test('shared group preserves whole original while selecting the declared child time', () => {
  const text = source({ time: '2019年9月29日21:45', normalized: '2019-09-29 21:45' })
    .replace('- 原文定位：', '- 来源组编号：group-test-0001\n- 原文定位：')
    .replace('```text\n', '```text\n铸印课二则：\n2019年8月29日23:39\n戌命男问能否升职\n');
  const item = inspectCase(text, 'raw-test-0001.md');
  assert.equal(item.shared_original_group, 'group-test-0001');
  assert.equal(item.parsed_time.datetime, '2019-09-29T21:45');
  assert.ok(!item.issues.includes('TIME_FIELD_SOURCE_MISMATCH'));
  const undeclared = text.replace('- 来源组编号：group-test-0001\n', '');
  assert.ok(inspectCase(undeclared, 'raw-test-0001.md').issues.includes('TIME_FIELD_SOURCE_MISMATCH'));
  const missingTime = text.replace('```text\n', '```text\n2\n').replace(/(```text[\s\S]*)2019年9月29日21:45/, '$1时间缺失');
  assert.ok(inspectCase(missingTime, 'raw-test-0001.md').issues.includes('TIME_FIELD_SOURCE_MISMATCH'));
});

test('uses time and question fields; feedback dates do not become chart input', () => {
  const text = source({ feedback: '反馈：2025年6月6日12:00，报数24，出国后按当地时间' });
  const item = inspectCase(text, 'raw-test-0001.md');
  assert.equal(item.parsed_time.datetime, '2024-03-11T01:10');
  assert.deepEqual(item.issues, []);
  assert.ok(inspectCase(source({ question: '占项目前景，报数24' }), 'raw-test-0001.md').issues.includes('SPECIAL_DIVINATION_METHOD'));
  assert.ok(inspectCase(source({ question: '按当地时间起课' }), 'raw-test-0001.md').issues.includes('EXPLICIT_TIME_CONVENTION_NEEDS_REVIEW'));
});

test('rejects filename mismatch, source-time mismatch and conflicting normalized time', () => {
  assert.throws(() => inspectCase(source(), 'raw-test-9999.md'));
  const conflict = inspectCase(source({ normalized: '2024-03-11 02:10' }), 'raw-test-0001.md');
  assert.ok(conflict.issues.includes('NORMALIZED_TIME_MISMATCH'));
  const changedRaw = source().replace('```text\n2024年3月11日1:10', '```text\n2024年3月12日1:10');
  assert.ok(inspectCase(changedRaw, 'raw-test-0001.md').issues.includes('TIME_FIELD_SOURCE_MISMATCH'));
});

test('batch preserves source and separates unresolved input; analysis payload excludes interpretation and feedback', async (t) => {
  const dirs = fixture(t);
  const first = source();
  fs.writeFileSync(path.join(dirs.inputDir, 'raw-test-0001.md'), first);
  fs.writeFileSync(path.join(dirs.inputDir, 'raw-test-0002.md'), source({ id: 'raw-test-0002', time: '时间：丁巳日，干上未乘朱雀，子丑旬空。伏吟局', normalized: '不转换' }));
  const requests = [];
  const result = await buildBatch({ ...dirs, policy: defaultPolicy, createChart: async (r) => { requests.push(r); return fakeEngine(r); } });
  assert.equal(result.total, 2);
  assert.equal(result.analysis_usable, 1);
  assert.equal(requests.length, 1);
  assert.equal(fs.readFileSync(path.join(dirs.inputDir, 'raw-test-0001.md'), 'utf8'), first);
  const chart = JSON.parse(fs.readFileSync(path.join(dirs.outputDir, 'raw-test-0001.json')));
  assert.equal(chart.facts.summary, undefined);
  assert.equal(chart.facts.key_shensha, undefined);
  assert.equal(chart.official_library_eligible, false);
  assert.ok(!JSON.stringify(chart).includes('反馈：通过'));
  const special = JSON.parse(fs.readFileSync(path.join(dirs.outputDir, '_特殊案例.json')));
  assert.equal(special.cases[0].constraints.day_pillar, '丁巳');
});

test('proposals never auto-generate; confirmed resolution needs explicit opt-in and source hash', async (t) => {
  const dirs = fixture(t);
  const text = source({ time: '2024年9月11日15时', normalized: '不转换' });
  fs.writeFileSync(path.join(dirs.inputDir, 'raw-test-0001.md'), text);
  const item = inspectCase(text, 'raw-test-0001.md');
  const resolution = { status: 'proposed', datetime: '2024-09-11T15:30', method: 'datetime', evidence: '补充来源', reviewed_by: '人工', case_file_sha256: item.case_file_sha256 };
  let calls = 0;
  const createChart = async (r) => { calls++; return fakeEngine(r); };
  const run = (name, acceptConfirmed, value) => buildBatch({ ...dirs, outputDir: path.join(dirs.root, name), createChart, acceptConfirmed, resolutions: { [item.id]: value } });
  assert.equal((await run('proposed', true, resolution)).analysis_usable, 0);
  resolution.status = 'confirmed';
  assert.equal((await run('not-accepted', false, resolution)).analysis_usable, 0);
  assert.equal((await run('accepted', true, resolution)).analysis_usable, 1);
  assert.equal((await run('stale', true, { ...resolution, case_file_sha256: 'old' })).counts.error, 1);
  assert.equal((await run('wrong-hour', true, { ...resolution, datetime: '2024-09-11T16:30' })).counts.error, 1);
  assert.equal(calls, 1);
});

test('checks original day/hour constraints and isolates per-case engine failures', async (t) => {
  const dirs = fixture(t);
  const text = source({ time: '时间：丁巳日，伏吟局', normalized: '不转换' });
  fs.writeFileSync(path.join(dirs.inputDir, 'raw-test-0001.md'), text);
  const item = inspectCase(text, 'raw-test-0001.md');
  const result = await buildBatch({ ...dirs, createChart: fakeEngine, acceptConfirmed: true, resolutions: { [item.id]: { status: 'confirmed', datetime: '2024-09-11T15:30', method: 'datetime', evidence: '测试', reviewed_by: '人工', case_file_sha256: item.case_file_sha256 } } });
  assert.equal(result.analysis_usable, 0);
  assert.equal(result.counts.chart_validation_blocked, 1);
  const chart = JSON.parse(fs.readFileSync(path.join(dirs.outputDir, 'raw-test-0001.json')));
  assert.ok(chart.validation.errors.some((e) => e.code === 'DAY_PILLAR_CONSTRAINT_MISMATCH'));
  assert.equal(chart.validation.status, 'blocked');
});

test('engine failure does not stop other cases or mark a rejected chart usable', async (t) => {
  const dirs = fixture(t);
  fs.writeFileSync(path.join(dirs.inputDir, 'raw-test-0001.md'), source());
  fs.writeFileSync(path.join(dirs.inputDir, 'raw-test-0002.md'), source({ id: 'raw-test-0002' }));
  fs.writeFileSync(path.join(dirs.inputDir, 'raw-test-0003.md'), source({ id: 'raw-test-0003' }));
  let n = 0;
  const result = await buildBatch({ ...dirs, createChart: async (r) => {
    n++;
    if (n === 1) throw new Error('test engine unavailable');
    const chart = await fakeEngine(r);
    if (n === 2) chart.validation.ok = false;
    return chart;
  } });
  assert.equal(result.total, 3);
  assert.equal(result.analysis_usable, 1);
  assert.equal(result.counts.error, 1);
  assert.equal(result.counts.chart_validation_blocked, 1);
});

test('refuses unsupported policies and prevents overwriting a different source batch', async (t) => {
  const dirs = fixture(t);
  const input = path.join(dirs.inputDir, 'raw-test-0001.md');
  fs.writeFileSync(input, source());
  await assert.rejects(buildBatch({ ...dirs, createChart: fakeEngine, policy: { ...defaultPolicy, timezone: 'UTC' } }));
  await buildBatch({ ...dirs, createChart: fakeEngine });
  fs.writeFileSync(input, source({ feedback: '反馈：未过' }));
  await assert.rejects(buildBatch({ ...dirs, createChart: fakeEngine }), /不同输入/);
});
