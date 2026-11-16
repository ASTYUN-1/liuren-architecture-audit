import fs from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { resolveNodeExecutable } from '../../tools/liuren-node-runtime.mjs';
import { default as tool } from '../../.opencode/tools/liuren_chart.ts';

const selected = await resolveNodeExecutable();
const results = [];
for (let i = 0; i < 3; i++) {
  const input = i === 2 ? { datetime: '2024-02-30T23:32' } : { datetime: '2024-03-29T23:32', label: '桌面宿主修复验收' };
  const result = JSON.parse(await tool.execute(input, { abort: new AbortController().signal }));
  if (i < 2) {
    if (!result.ok || !result.validation.ok || result.facts.heaven_earth.length !== 12 ||
        result.facts.lessons.length !== 4 || result.facts.transmissions.length !== 3) throw new Error('incomplete chart');
    const raw = JSON.parse(await fs.readFile(result.archive.path, 'utf8'));
    if (raw.schema !== 'liuren-paipan-v1' || !raw._direct.provenance.engine_hash_verified) throw new Error('invalid archive');
    results.push({ call: i + 1, ok: result.ok, datetime: result.input.datetime, pillars: result.facts.pillars,
      palaces: result.facts.heaven_earth.length, lessons: result.facts.lessons.length,
      transmissions: result.facts.transmissions.length, archive: result.archive.path,
      archive_sha256: result.archive.sha256, validation: result.validation });
  } else {
    if (result.ok || result.error?.code !== 'INVALID_DATETIME') throw new Error('missing input error');
    results.push({ call: i + 1, ok: result.ok, error: result.error });
  }
}
const report = { host: { execPath: process.execPath, node: process.versions.node, electron: process.versions.electron, bun: process.versions.bun },
  selected_node: selected, model_calls: 0, results };
const name = process.versions.electron ? 'desktop' : 'node';
await fs.writeFile(new URL(`host-smoke-${name}.json`, import.meta.url), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify(report));
