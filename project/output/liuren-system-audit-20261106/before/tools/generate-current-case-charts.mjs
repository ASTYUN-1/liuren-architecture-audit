import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { buildBatch } from './batch-case-charts.mjs';

// Deterministic three-source batch. Never dispatches an LLM or writes to the case library.
const project = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const output = path.resolve(process.argv[2] || path.join(project, 'docs/初级案例整理/盘面资料/batch-20261018'));
const qqRoot = path.join(project, '资料来源/qq-homework-20261018');
const engineRoot = path.join(project, 'materials/vendor/liuren-chart-legacy-20261102');
const { createChart } = await import(pathToFileURL(path.join(engineRoot, 'adapters/chart.mjs')).href);
const hash = (v) => crypto.createHash('sha256').update(v).digest('hex');
const write = (name, v) => fs.writeFileSync(path.join(output, name), JSON.stringify(v, null, 2) + '\n');
if (fs.existsSync(output)) throw new Error('请使用不存在的新输出目录，保留上次结果');
fs.mkdirSync(output, { recursive: true });

const ledgerPath = path.join(qqRoot, 'stage1_v2/ledger.json');
const ledgerBytes = fs.readFileSync(ledgerPath);
const ledger = JSON.parse(ledgerBytes.toString('utf8').replace(/^\uFEFF/, ''));
const added = [];
for (const entry of ledger.images) {
  if (!entry.sha256 && /^pan\/[A-Za-z0-9_.-]+\.(jpg|jpeg|png)$/.test(entry.file)) {
    entry.sha256 = hash(fs.readFileSync(path.join(qqRoot, entry.file)));
    entry.sha256_origin = 'computed_from_local_image_for_this_run';
    added.push({ file: entry.file, sha256: entry.sha256 });
  }
}
ledger.snapshot_provenance = { original_file: ledgerPath, original_file_sha256: hash(ledgerBytes), added_hashes: added, note: '仅对原台账缺失指纹的本地图像计算当前SHA256；不修改源台账，不表示历史图像真实性或转录已被独立核验。' };
write('_图像台账快照.json', ledger);

const sources = [
  { name: 'anli001', inputDir: path.join(project, 'docs/初级案例整理/初级案例资料/anli001') },
  { name: 'anli002', inputDir: path.join(project, 'docs/初级案例整理/初级案例资料/anli002') },
  { name: 'qqwb20261018', inputDir: path.join(qqRoot, 'stage1_v2/cases'), imageLedger: ledger, sourceRoot: qqRoot },
];
const all = [], batches = [];
for (const source of sources) {
  const outputDir = path.join(output, source.name);
  const index = await buildBatch({ ...source, outputDir, engineRoot, createChart });
  batches.push({ source: source.name, output_directory: outputDir, total: index.total, analysis_usable: index.analysis_usable, counts: index.counts });
  for (const row of index.files) {
    const chartPath = path.join(outputDir, row.file);
    const bytes = fs.readFileSync(chartPath);
    const chart = JSON.parse(bytes);
    const caseBytes = fs.readFileSync(chart.source.absolute_file, 'utf8');
    if (hash(caseBytes) !== chart.source.case_file_sha256) throw new Error(`来源已改变：${row.case_id}`);
    if (chart.facts && (chart.facts.heaven_earth.length !== 12 || chart.facts.lessons.length !== 4 || chart.facts.transmissions.length !== 3 || chart.facts.summary !== undefined || chart.facts.key_shensha !== undefined)) throw new Error(`盘面结构或纯净性错误：${row.case_id}`);
    if (chart.usable_for_batch_analysis && !chart.validation.ok) throw new Error(`状态错误：${row.case_id}`);
    all.push({ ...row, source: source.name, file: chartPath, sha256: hash(bytes), has_chart_facts: Boolean(chart.facts), issues: chart.issues, validation_errors: chart.validation?.errors || [] });
  }
}
if (all.length !== 128 || new Set(all.map((r) => r.case_id)).size !== 128) throw new Error('128案数量或编号校验失败');
const counts = {
  total: all.length, chart_facts_generated: all.filter((r) => r.has_chart_facts).length,
  analysis_usable: all.filter((r) => r.usable_for_batch_analysis).length,
  needs_resolution: all.filter((r) => r.status === 'needs_resolution').length,
  chart_validation_blocked: all.filter((r) => r.status === 'chart_validation_blocked').length,
  error: all.filter((r) => r.status === 'error').length,
};
write('_批次总索引.json', { schema: 'staged-chart-combined-v1', generated_at: new Date().toISOString(), node: process.execPath, script_sha256: hash(fs.readFileSync(fileURLToPath(import.meta.url))), batch_script_sha256: hash(fs.readFileSync(path.join(project, 'tools/batch-case-charts.mjs'))), counts, batches, files: all, official_library_eligible: false });
write('_可分析盘面清单.json', { count: counts.analysis_usable, files: all.filter((r) => r.usable_for_batch_analysis) });
write('_待核盘面清单.json', { count: all.length - counts.analysis_usable, files: all.filter((r) => !r.usable_for_batch_analysis) });
const report = [
  '# 128案程序化排盘结果', '',
  `- 案例总数：${counts.total}`, `- 含程序盘面：${counts.chart_facts_generated}`, `- 可进入后续分析：${counts.analysis_usable}`, `- 时间或方法待核，尚无盘面：${counts.needs_resolution}`, `- 已生成但与来源字段冲突，暂停分析：${counts.chart_validation_blocked}`, `- 运行错误：${counts.error}`, '',
  '| 来源 | 案例数 | 可分析 | 输入待核 | 盘面冲突 |', '| --- | ---: | ---: | ---: | ---: |',
  ...batches.map((b) => `| ${b.source} | ${b.total} | ${b.analysis_usable} | ${b.counts.needs_resolution || 0} | ${b.counts.chart_validation_blocked || 0} |`), '',
  '所有案例均保留为初级资料，未进行AI分析或正式入库。输入案例文件只读；每份JSON绑定案例哈希，盘图输入另绑定图像指纹。原台账缺指纹的2张图仅新增本次快照指纹，不冒充历史核验。', '',
  '普通输入依照批次记录的公历、北京时间及排盘规则生成；题干明确设置优先并记入source_settings/effective_settings。盘图时间采用既有整理转录并与台账交叉核对，本次未逐图独立复核。', '',
  '只分发_可分析盘面清单.json中的条目。_待核盘面清单.json集中记录缺失时间、特殊方法、图源关联与四柱/月将冲突；含facts的冲突盘面也不得自动送入分析。鱼获零归等缺唯一日期的输入保持未决。', '',
  '盘面结构、全部案例哈希及索引已程序校验；不以结构通过证明原始转录或术理全部正确。', '',
  '## 盘面冲突', '',
  ...all.filter((r) => r.status === 'chart_validation_blocked').map((r) => `- ${r.case_id}：${r.validation_errors.map((e) => e.code).join('、')}`), '',
  '## 输入待核', '',
  ...all.filter((r) => r.status === 'needs_resolution').map((r) => `- ${r.case_id}：${r.issues.join('、')}`), '',
].join('\n');
fs.writeFileSync(path.join(output, '使用说明.md'), report);
console.log(JSON.stringify({ output, ...counts }));
if (counts.error) process.exitCode = 1;
