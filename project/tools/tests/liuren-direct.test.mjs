import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { ROOT, runChart, prepareRequest, beijingMinute, isEntryPoint } from '../liuren-direct.mjs';
import { pathToFileURL, fileURLToPath } from 'node:url';

const hash = v => crypto.createHash('sha256').update(JSON.stringify(v)).digest('hex');
const artifactRoot = path.join(ROOT, 'output/本机直接排盘-20261030/test-artifacts', crypto.randomUUID());
const direct = input => runChart(input, { persist: false });

test('CLI entry identity accepts Windows namespaced paths but imports do not execute main', () => {
  const script = path.join(ROOT, 'tools/liuren-direct.mjs');
  const url = pathToFileURL(script).href;
  assert.equal(isEntryPoint(script, url), true);
  assert.equal(isEntryPoint(undefined, url), false);
  assert.equal(isEntryPoint(fileURLToPath(import.meta.url), url), false);
  if (process.platform === 'win32') {
    assert.equal(isEntryPoint(path.toNamespacedPath(script), url), true);
    assert.equal(isEntryPoint(script.toLowerCase(), url), true);
  }
  const imported = spawnSync(process.execPath, ['--input-type=module', '-e', `await import(${JSON.stringify(url)})`], { cwd: ROOT, encoding: 'utf8', windowsHide: true });
  assert.equal(imported.status, 0, imported.stderr);
  assert.equal(imported.stdout, '');
});

test('cold subprocess via namespaced CLI path returns complete JSON on the very first stdin request', () => {
  const script = path.toNamespacedPath(path.join(ROOT, 'tools/liuren-direct.mjs'));
  for (let attempt = 0; attempt < 3; attempt++) {
    const child = spawnSync(process.execPath, [script, '--stdin'], {
      cwd: ROOT, encoding: 'utf8', windowsHide: true,
      input: JSON.stringify({ datetime: '2026-08-04T14:32', label: '冷启动回归' }),
    });
    assert.equal(child.status, 0, child.stderr);
    assert.ok(child.stdout.length > 0, `empty stdout on cold invocation ${attempt + 1}`);
    const result = JSON.parse(child.stdout);
    assert.equal(result.ok, true);
    assert.deepEqual(result.facts.pillars, ['丙午', '乙未', '庚戌', '癸未']);
    assert.equal(result.facts.heaven_earth.length, 12);
    assert.equal(result.validation.ok, true);
    assert.ok(result.archive.path.endsWith('.json'));
  }
  const invalid = spawnSync(process.execPath, [script, '--stdin'], { cwd: ROOT, encoding: 'utf8', windowsHide: true, input: JSON.stringify({ datetime: '2026-02-30T15:20' }) });
  assert.equal(invalid.status, 1);
  assert.equal(JSON.parse(invalid.stdout).error.code, 'INVALID_DATETIME');
});

test('original historic exports: four pillars, all 12 palaces and shensha, lessons, transmissions and native interpretations', async () => {
  const fixtures = JSON.parse(await fs.readFile(new URL('./fixtures/liuren-historical-hashes.json', import.meta.url), 'utf8'));
  for (const fixture of fixtures) {
    const result = await runChart({ datetime: fixture.datetime }, { archiveRoot: artifactRoot });
    assert.equal(result.ok, true);
    const raw = JSON.parse(await fs.readFile(result.archive.path, 'utf8'));
    for (const [key, expected] of Object.entries(fixture.field_sha256)) assert.equal(hash(raw[key]), expected, `${fixture.datetime}: ${key}`);
    assert.deepEqual(result.facts.heaven_earth.map(p => p.shensha), raw.tiandipan.map(p => p.shensha));
    assert.equal(result.facts.summary, undefined);
    assert.equal(result.facts.key_shensha, undefined);
  }
});

test('now is captured once in Beijing time across midnight and independent of parent TZ', async () => {
  const now = new Date('2026-10-29T16:01:59Z');
  assert.equal(beijingMinute(now), '2026-10-30T00:01:00+08:00');
  const prepared = prepareRequest({ mode: 'now' }, now);
  const result = await runChart({ mode: 'now' }, { persist: false, now });
  assert.equal(result.input.datetime, prepared.input.datetime);
  assert.equal(result.ok, true);
  const oldTZ = process.env.TZ;
  const child = spawnSync(process.execPath, ['tools/liuren-direct.mjs', '--datetime', '2026-08-04T14:32'], { cwd: ROOT, encoding: 'utf8', windowsHide: true, env: { ...process.env, TZ: 'America/New_York' } });
  assert.equal(child.status, 0, child.stderr);
  assert.deepEqual(JSON.parse(child.stdout).facts.pillars, ['丙午', '乙未', '庚戌', '癸未']);
  assert.equal(process.env.TZ, oldTZ);
});

test('manual pillars retain repeated transmission slots without inventing an event date', async () => {
  const result = await direct({ mode: 'manual-pillars', pillars: { year: '甲子', month_branch: '子', day: '乙丑', hour_branch: '子' }, month_general: '午' });
  assert.equal(result.ok, true);
  assert.equal(result.facts.transmission_sequence, '戌辰戌');
  assert.equal(result.facts.transmissions.length, 3);
  assert.equal(result.facts.event_datetime, null);
  assert.equal(result.facts.lunar, null);
});

test('fixed nobleman settings reach the native engine and explicit life stays separate', async () => {
  const day = await direct({ datetime: '2026-08-04T14:32' });
  const night = await direct({ datetime: '2026-08-04T14:32', settings: { zhouye: '夜贵' }, declared_life: [{ birth_pillar: '庚午' }] });
  assert.equal(night.ok, true);
  assert.equal(night.facts.nobleman.actual_zhouye, '夜贵');
  assert.notDeepEqual(day.facts.heaven_earth.map(p => p.tianjiang), night.facts.heaven_earth.map(p => p.tianjiang));
  assert.equal(night.facts.declared_life[0].birth_pillar, '庚午');
  assert.equal(night.facts.year_life_verified, false);
});

test('invalid dates, conflicting modes, unsupported conventions and unrecognized fields fail rather than default', async () => {
  for (const input of [
    { datetime: '2026-02-30T15:20' }, { datetime: '2026-08-04T14:32:05' },
    { datetime: '2026-08-04T14:32', timezone: 'Asia/Tokyo' },
    { datetime: '2026-08-04T14:32', time_basis: 'solar' },
    { mode: 'now', datetime: '2026-08-04T14:32' }, { mode: 'number', number: 8 },
    { datetime: '2026-08-04T14:32', month_general: '午' },
    { mode: 'manual-pillars', pillars: { year: '甲子' } },
    { datetime: '2026-08-04T14:32', label: '../escape' },
    { datetime: '2026-08-04T14:32', participants: [{ sex: '男', birth_year: 1990, name: 'private' }] },
  ]) await assert.rejects(direct(input), undefined, JSON.stringify(input));
});

test('same-minute solar term discrepancy blocks use but keeps a complete review artifact', async () => {
  const result = await runChart({ datetime: '2026-07-23T03:13' }, { archiveRoot: artifactRoot });
  assert.equal(result.ok, false);
  assert.ok(result.validation.errors.some(e => e.code === 'SOLAR_TERM_MINUTE_BOUNDARY'));
  const record = JSON.parse(await fs.readFile(result.archive.path, 'utf8'));
  assert.equal(record.schema, 'liuren-paipan-v1');
  assert.equal(record._direct.validation.ok, false);
});

test('same timestamp and label never overwrite; archive hashes and complete exports match returned facts', async () => {
  const options = { archiveRoot: artifactRoot, now: new Date('2026-10-29T08:00:00Z') };
  const a = await runChart({ datetime: '2026-08-04T14:32' }, options);
  const before = await fs.readFile(a.archive.path);
  const b = await runChart({ datetime: '2026-08-04T14:32' }, options);
  assert.notEqual(a.archive.path, b.archive.path);
  assert.deepEqual(await fs.readFile(a.archive.path), before);
  assert.equal(crypto.createHash('sha256').update(before).digest('hex'), a.archive.sha256);
  const record = JSON.parse(before);
  const { _direct, ...raw } = record;
  assert.equal(hash(raw), a.archive.raw_sha256);
  assert.deepEqual(_direct.facts, a.facts);
  assert.equal(record.tiandipan.length, 12);
  assert.equal(record.sike.length, 4);
  assert.equal(record.sanchuan.length, 3);
});

test('OpenCode native tool schema and real subprocess invocation return facts and a saved full export', async () => {
  const { default: tool } = await import('../../.opencode/tools/liuren_chart.ts');
  const { tool: helper } = await import('../../.opencode/node_modules/@opencode-ai/plugin/dist/tool.js');
  const schema = helper.schema.object(tool.args).strict();
  assert.equal(schema.safeParse({ datetime: '2026-08-04T14:32', settings: { wrong: true } }).success, false);
  const args = schema.parse({ datetime: '2026-08-04T14:32', label: '工具验收' });
  const result = JSON.parse(await tool.execute(args, { abort: new AbortController().signal }));
  assert.equal(result.ok, true);
  assert.deepEqual(result.facts.pillars, ['丙午', '乙未', '庚戌', '癸未']);
  assert.equal(result.facts.heaven_earth.length, 12);
  const saved = JSON.parse(await fs.readFile(result.archive.path, 'utf8'));
  assert.equal(saved.schema, 'liuren-paipan-v1');
  assert.equal(saved._direct.provenance.engine_hash_verified, true);
});
