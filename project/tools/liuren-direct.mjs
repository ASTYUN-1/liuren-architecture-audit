import fs from 'node:fs/promises';
import { realpathSync } from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { createChart } from './liuren-direct/chart.mjs';
import { TRANSPORT_ROOT } from './liuren-tool-transport.mjs';
import {LIFE_INPUT_FIELDS} from './liuren-year-life.mjs';

export const ROOT = fileURLToPath(new URL('../', import.meta.url));
export function isEntryPoint(argvPath, moduleUrl) {
  if (!argvPath) return false;
  // Windows may put \\?\ in argv[1] while import.meta.url uses an ordinary
  // file URL. String comparison silently skipped main() for that same file.
  const canonical = filename => {
    const resolved = realpathSync.native(filename);
    return process.platform === 'win32' ? resolved.toLowerCase() : resolved;
  };
  try {
    return canonical(argvPath) === canonical(fileURLToPath(moduleUrl));
  } catch (error) {
    // Compiled Bun hosts expose a virtual argv entry that has no disk path.
    if (error.code === 'ENOENT' || error.code === 'ENOTDIR') return false;
    throw error;
  }
}
const digest = value => crypto.createHash('sha256').update(JSON.stringify(value)).digest('hex');
function fail(code, message) { throw Object.assign(new Error(message), { code }); }
export function beijingMinute(now = new Date()) {
  return new Date(now.getTime() + 8 * 3600000).toISOString().slice(0, 16) + ':00+08:00';
}

export function prepareRequest(request, now = new Date()) {
  if (!request || typeof request !== 'object' || Array.isArray(request)) fail('INVALID_INPUT', '输入须为排盘参数对象。');
  const allowed = new Set(['mode', 'datetime', 'timezone', 'time_basis', 'settings', 'pillars', 'month_general', 'reference_datetime', 'participants', 'declared_life', 'label']);
  for (const key of Object.keys(request)) if (!allowed.has(key)) fail('UNKNOWN_PARAMETER', `不支持参数 ${key}；不静默忽略。`);
  const { label = '起课', ...input } = structuredClone(request);
  if (typeof label !== 'string' || !/^[\p{L}\p{N}_-]{1,32}$/u.test(label)) fail('INVALID_LABEL', 'label须为1—32个文字、数字、下划线或连字符，使用代号，不填姓名。');
  const mode = input.mode ?? 'datetime';
  if (input.timezone !== undefined && input.timezone !== 'Asia/Shanghai') fail('UNSUPPORTED_TIMEZONE', '仅支持Asia/Shanghai；不静默忽略时区。');
  if (input.time_basis !== undefined && input.time_basis !== 'civil') fail('UNSUPPORTED_CONVENTION', '仅支持civil民用钟表时间。');
  if (!['datetime', 'now', 'manual-pillars'].includes(mode)) fail('UNSUPPORTED_MODE', '仅支持datetime、now、manual-pillars；活时报数/真太阳时不能冒充正时。');
  if (mode === 'now') {
    if (input.datetime !== undefined) fail('CONFLICTING_INPUT', 'now不能同时指定datetime。');
    input.mode = 'datetime'; input.datetime = beijingMinute(now);
  } else input.mode = mode;
  if (mode !== 'manual-pillars' && ['pillars', 'month_general', 'reference_datetime'].some(key => input[key] !== undefined)) fail('CONFLICTING_INPUT', '正时不能混入四柱模式参数。');
  if (mode === 'manual-pillars' && input.datetime !== undefined) fail('CONFLICTING_INPUT', '四柱模式使用reference_datetime显示参考日期，不接受datetime冒认真实占时。');
  if (input.pillars) for (const key of Object.keys(input.pillars)) if (!['year', 'month_branch', 'day', 'hour_branch'].includes(key)) fail('UNKNOWN_PARAMETER', `不支持pillars.${key}。`);
  for (const [key, keys] of [['participants', LIFE_INPUT_FIELDS], ['declared_life', LIFE_INPUT_FIELDS]]) {
    if (input[key] !== undefined && !Array.isArray(input[key])) fail('INVALID_INPUT', `${key}须为数组。`);
    for (const person of input[key] || []) {
      if (!person || typeof person !== 'object' || Array.isArray(person)) fail('INVALID_INPUT', `${key}成员须为对象。`);
      for (const field of Object.keys(person)) if (!keys.includes(field)) fail('UNKNOWN_PARAMETER', `${key}不支持${field}；只传结构化年命参数，不传姓名或原问。`);
    }
  }
  return { input, label, requestedMode: mode };
}

export async function runChart(request, { archiveRoot = path.join(ROOT, '排盘存档/六壬'), persist = true, now = new Date() } = {}) {
  const start = performance.now();
  const prepared = prepareRequest(request, now);
  const chart = await createChart(prepared.input);
  // Preserve every native field in the archive. Interpretive summaries are not facts.
  const { summary, key_shensha, ...facts } = chart.facts;
  const metadata = {
    schema: 'liuren-direct-export-v1', adapter_version: '20261030-direct-01',
    generated_at: now.toISOString(), requested_mode: prepared.requestedMode,
    input: chart.input, facts, validation: chart.validation,
    conventions: chart.conventions, provenance: chart.provenance, engine: chart.engine,
    raw_sha256: digest(chart.raw),
  };
  const record = { ...chart.raw, _direct: metadata };
  let archive = null;
  if (persist) {
    await fs.mkdir(archiveRoot, { recursive: true });
    const stamp = beijingMinute(now).slice(0, 10).replaceAll('-', '') + '-' + new Date(now.getTime() + 8 * 3600000).toISOString().slice(11, 19).replaceAll(':', '');
    const filename = `六壬-${stamp}-${prepared.label}-${crypto.randomUUID()}.json`;
    const fullpath = path.join(archiveRoot, filename);
    await fs.writeFile(fullpath, JSON.stringify(record, null, 2) + '\n', { encoding: 'utf8', flag: 'wx' });
    archive = { path: fullpath, sha256: crypto.createHash('sha256').update(await fs.readFile(fullpath)).digest('hex'), raw_sha256: metadata.raw_sha256 };
  }
  return {
    ok: chart.validation.ok, schema: 'liuren-direct-result-v1', adapter_version: metadata.adapter_version,
    input: chart.input, facts, validation: chart.validation, conventions: chart.conventions,
    provenance: chart.provenance, archive, elapsed_ms: Math.round(performance.now() - start),
    field_notes: { shensha: 'facts.heaven_earth保留全部12宫神煞；不是keyShensha摘要。', raw: 'archive.path为完整原页面JSON，_direct为附加输入/校验/来源记录。', interpretation: '原页面断语保存在归档中；不是程序事实或本问结论。' },
  };
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length === 2 && args[0] === '--exchange') {
    // Tool-to-CLI transport uses files, never stdin/stdout as the result channel.
    const base = await fs.realpath(TRANSPORT_ROOT);
    const directory = await fs.realpath(args[1]);
    if (path.dirname(directory).toLowerCase() !== base.replace(/[\\/]$/, '').toLowerCase() || !path.basename(directory).startsWith('request-')) fail('INVALID_EXCHANGE_PATH', '排盘交接目录须由本机工具创建。');
    const request = JSON.parse(await fs.readFile(path.join(directory, 'request.json'), 'utf8'));
    if (request.schema !== 'liuren-tool-request-v1' || !/^[a-f0-9-]{36}$/.test(request.request_id || '')) fail('INVALID_EXCHANGE_REQUEST', '排盘请求标识无效。');
    let result;
    try { result = await runChart(request.input); process.exitCode = result.ok ? 0 : 2; }
    catch (error) { result = { ok: false, error: { code: error.code || 'DIRECT_CHART_ERROR', message: error.message } }; process.exitCode = 1; }
    await fs.writeFile(path.join(directory, 'response.json'), JSON.stringify({ schema: 'liuren-tool-response-v1', request_id: request.request_id, result }) + '\n', { encoding: 'utf8', flag: 'wx' });
    return;
  }
  if (args.length === 1 && args[0] === '--help') {
    console.log('node tools/liuren-direct.mjs --datetime 2026-10-29T15:20\nnode tools/liuren-direct.mjs --now\nnode tools/liuren-direct.mjs --input <UTF-8 JSON>\nnode tools/liuren-direct.mjs --stdin\n默认自动归档完整JSON至排盘存档/六壬；标准输出为事实、校验和文件路径。');
    return;
  }
  let request;
  if (args.length === 1 && args[0] === '--stdin') request = JSON.parse(await new Promise((resolve, reject) => { let data = ''; process.stdin.setEncoding('utf8'); process.stdin.on('data', chunk => { data += chunk; }); process.stdin.on('end', () => resolve(data.replace(/^\uFEFF/, ''))); process.stdin.on('error', reject); }));
  else if (args.length === 1 && args[0] === '--now') request = { mode: 'now' };
  else if (args.length === 2 && args[0] === '--datetime') request = { datetime: args[1] };
  else if (args.length === 2 && args[0] === '--input') request = JSON.parse((await fs.readFile(args[1], 'utf8')).replace(/^\uFEFF/, ''));
  else fail('CLI_ARGUMENT', '使用--datetime <时间>、--now、--input <JSON>或--stdin；--help查看说明。');
  const result = await runChart(request);
  process.stdout.write(JSON.stringify(result) + '\n');
  if (!result.ok) process.exitCode = 2;
}
if (isEntryPoint(process.argv[1], import.meta.url)) {
  main().catch(error => { process.stdout.write(JSON.stringify({ ok: false, error: { code: error.code || 'DIRECT_CHART_ERROR', message: error.message } }) + '\n'); process.exitCode = 1; });
}
