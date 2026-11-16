import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { executeChartTool } from '../liuren-tool-transport.mjs';

const scriptPath = fileURLToPath(new URL('../liuren-direct.mjs', import.meta.url));
const options = { nodePath: process.execPath, scriptPath };
const valid = { datetime: '2026-08-04T14:32', label: '文件传输回归' };

test('first call returns a full chart even when all subprocess output is discarded and replaced by CRLF', async () => {
  let launches = 0, exchange;
  const result = JSON.parse(await executeChartTool(valid, { ...options, launch: async (node, script, directory) => {
    launches++; exchange = directory;
    const child = spawnSync(node, [script, '--exchange', directory], { windowsHide: true, stdio: 'ignore' });
    return { code: child.status, signal: child.signal, stdout: '\r\n', stderr: '' };
  } }));
  assert.equal(launches, 1);
  assert.equal(result.ok, true);
  assert.equal(result.facts.heaven_earth.length, 12);
  assert.deepEqual(result.facts.pillars, ['丙午', '乙未', '庚戌', '癸未']);
  assert.equal(JSON.parse(await fs.readFile(result.archive.path, 'utf8')).schema, 'liuren-paipan-v1');
  await assert.rejects(fs.access(exchange));
});

test('a sex supplement merges with a single-branch life and survives cold transport', async () => {
  const input = { datetime: '2026-10-25T20:53', mode: 'datetime', time_basis: 'civil', timezone: 'Asia/Shanghai', participants: [{ sex: '男' }], declared_life: [{ birth_pillar: '亥', sex: '男' }] };
  const result = JSON.parse(await executeChartTool(input, options));
  assert.equal(result.ok, true);
  assert.equal(result.facts.year_life.participants[0].birth.branch,'亥');
  assert.ok(result.facts.year_life.participants[0].xingnian.branch);
  const { participants, ...onlyLife } = input;
  const life = JSON.parse(await executeChartTool(onlyLife, options));
  assert.equal(life.ok, true);
  assert.equal(life.facts.year_life.participants[0].birth.branch,'亥');
  const incomplete=JSON.parse(await executeChartTool({datetime:input.datetime,participants:[{sex:'男'}]},options));
  assert.equal(incomplete.ok,false);assert.equal(incomplete.error.code,'INVALID_YEAR_LIFE');
});

test('concurrent requests keep identities and results separate', async () => {
  const [a, b] = (await Promise.all([
    executeChartTool(valid, options),
    executeChartTool({ datetime: '2026-02-30T12:00' }, options),
  ])).map(JSON.parse);
  assert.equal(a.ok, true);
  assert.equal(b.ok, false);
  assert.equal(b.error.code, 'INVALID_DATETIME');
});

test('missing response and a foreign request ID are rejected without a second chart attempt', async () => {
  let calls = 0, directory;
  await assert.rejects(executeChartTool(valid, { ...options, launch: async (_, __, dir) => {
    calls++; directory = dir;
    return { code: 0, stdout: '\r\n', stderr: '' };
  } }), /结果文件缺失/);
  assert.equal(calls, 1);
  await assert.rejects(fs.access(directory));
  await assert.rejects(executeChartTool(valid, { ...options, launch: async (_, __, dir) => {
    await fs.writeFile(path.join(dir, 'response.json'), JSON.stringify({ schema: 'liuren-tool-response-v1', request_id: 'another-request', result: { ok: false, error: { code: 'INVALID_DATETIME' } } }));
    return { code: 1, stdout: '', stderr: '' };
  } }), /标识/);
});

test('cancelled invocation cannot start a chart', async () => {
  const controller = new AbortController(); controller.abort();
  await assert.rejects(executeChartTool(valid, { ...options, signal: controller.signal, launch: async () => { throw new Error('must not start'); } }), /已取消/);
});
