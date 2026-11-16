import fs from 'node:fs/promises';
import { default as tool } from '../../.opencode/tools/liuren_materials.ts';

const context = { abort: new AbortController().signal };
const scope = JSON.parse(await tool.execute({ action: 'scope' }, context));
const original = JSON.parse(await tool.execute({ action: 'read', path: 'runtime/liuren/20261103-local-restore-01/methods/positioning.md', start: 1, count: 10 }, context));
let denied = false;
try { await tool.execute({ action: 'read', path: 'docs/跨会话继续开发指南.md' }, context); }
catch (error) { denied = /超出本机研判资料范围/.test(error.message); }
if (!denied || !original.text.includes('1:')) throw new Error('scope guard failed');
const methods = await tool.execute({ action: 'methods', domains: ['lost-person-object'], timing: true, batch: 1 }, context);
if (!methods.includes('LIUREN_TEXT_BEGIN') || !methods.includes('LIUREN_BATCH_END 1')) throw new Error('method loading failed');
const retrieval = await tool.execute({ action: 'retrieve', case_query: '失物 藏匿 位置', experience_query: '失物 方位 应期', category: '失物占', limit: 3 }, context);
if (!retrieval.includes('案例问题级检索') || !retrieval.includes('经验细粒度检索')) throw new Error('retrieval routes failed');
const scan = JSON.parse(await tool.execute({ action: 'scan', library: 'methods', query: '应期', limit: 5 }, context));
if (!scan.hits.length || scan.hits.some(hit => hit.path.startsWith('docs/') || hit.path.includes('/archive/'))) throw new Error('scan escaped scope');
const report = { host: { execPath: process.execPath, electron: process.versions.electron, node: process.versions.node },
  scope, original_lines: original.end, development_doc_denied: denied, methods_bytes: Buffer.byteLength(methods),
  both_retrievals_returned: true, scan_paths: scan.hits.map(h => h.path), model_calls: 0 };
await fs.writeFile(new URL('./native-smoke.json', import.meta.url), JSON.stringify(report, null, 2) + '\n');
console.log(JSON.stringify({ development_doc_denied: denied, both_retrievals_returned: true, scan_paths: report.scan_paths, host: report.host }));
