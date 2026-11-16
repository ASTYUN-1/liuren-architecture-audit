import test from 'node:test';
import assert from 'node:assert/strict';
import { realpathSync } from 'node:fs';
import { nodeCandidates, probeNodeExecutable, resolveNodeExecutable } from '../liuren-node-runtime.mjs';

const desktop = { execPath: 'C:\\Apps\\OpenCode.exe', env: { Path: 'C:\\broken;"C:\\Node";C:\\NODE' }, platform: 'win32', home: 'C:\\Users\\测试' };

test('desktop host without a Bun flag never becomes the interpreter; Windows Path and quoted entries work', () => {
  const candidates = nodeCandidates(desktop);
  assert.equal(candidates.some(p => /OpenCode\.exe/i.test(p)), false);
  assert.deepEqual(candidates.slice(0, 2), ['C:\\broken\\node.exe', 'C:\\Node\\node.exe']);
  assert.equal(candidates.filter(p => p.toLowerCase() === 'c:\\node\\node.exe').length, 1);
  assert.ok(candidates.some(p => p.endsWith('Programs\\nodejs\\node.exe')));
});

test('existing but unusable runtime is probed and skipped before selecting a working Node', async () => {
  const probed = [];
  const chosen = await resolveNodeExecutable({ ...desktop, exists: () => true, canonical: p => p,
    probe: async p => { probed.push(p); return p === 'C:\\Node\\node.exe'; } });
  assert.equal(chosen, 'C:\\Node\\node.exe');
  assert.deepEqual(probed, ['C:\\broken\\node.exe', 'C:\\Node\\node.exe']);
});

test('Bun executable also falls back, ordinary Node host remains a candidate', () => {
  assert.equal(nodeCandidates({ ...desktop, execPath: 'C:\\Apps\\bun.exe' }).includes('C:\\Apps\\bun.exe'), false);
  assert.equal(nodeCandidates({ ...desktop, execPath: 'C:\\Actual\\node.exe' })[0], 'C:\\Actual\\node.exe');
});

test('real interpreter evaluates the runtime probe; no-runtime and cancellation fail before any chart', async () => {
  assert.equal(await probeNodeExecutable(process.execPath), true);
  assert.equal(await resolveNodeExecutable(), realpathSync.native(process.execPath));
  await assert.rejects(resolveNodeExecutable({ ...desktop, exists: () => false }), /独立 Node.js/);
  const controller = new AbortController(); controller.abort();
  await assert.rejects(resolveNodeExecutable({ ...desktop, signal: controller.signal, exists: () => { throw new Error('must not inspect'); } }), /已取消/);
});
