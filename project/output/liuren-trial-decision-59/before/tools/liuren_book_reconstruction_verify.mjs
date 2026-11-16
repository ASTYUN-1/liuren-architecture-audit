// Read-only B1 bridge: reuses B5's strict cache verifier, never recalculates.
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import { reconstruct, projectPath, OUTPUT } from './liuren_book_reconstruction.mjs';
import { isEntryPoint } from './liuren-direct.mjs';
const sha = value => crypto.createHash('sha256').update(value).digest('hex');
const deny = message => { throw new Error(message); };
const LABELS = new Set(['nobleman.rule', 'nobleman.requested_zhouye', 'nobleman.actual_zhouye']);
function structural(facts, excluded) {
  const copy = structuredClone(facts);
  for (const item of excluded) {
    if (!LABELS.has(item)) deny('只可排除三个明确的贵人设置标签，不能忽略其他facts差异。');
    const [parent, key] = item.split('.'); if (copy[parent]) delete copy[parent][key];
  }
  return copy;
}
export async function verifyArtifact({ root, link, case_id, review }) {
  if (link.result_path !== `${OUTPUT}/${link.id}.json`) deny('复原结果路径与ID不同。');
  const bytes = await fs.readFile(await projectPath(root, link.result_path));
  if (sha(bytes) !== link.result_sha256) deny('结果文件hash变化。');
  if (!review.request_path?.startsWith('output/liuren-book-cases-20261102/') || !review.request_path.endsWith('.json')) deny('请求路径不在批准output目录。');
  const request = JSON.parse((await fs.readFile(await projectPath(root, review.request_path), 'utf8')).replace(/^\uFEFF/, ''));
  if (request.id !== link.id || request.case_id !== case_id || sha(JSON.stringify(request)) !== review.request_sha256) deny('复核请求ID/案例/hash不符。');
  const result = await reconstruct(request, { root, persist: true, engineRunner: async () => deny('只读核验禁止重算缺失结果。') });
  if (!result.reused || result.id !== link.id || result.case_id !== case_id) deny('结果未通过只读缓存核验。');
  const groups = [];
  const excluded = review.excluded_setting_label_paths || [];
  if (!Array.isArray(excluded) || new Set(excluded).size !== excluded.length) deny('排除标签无效。');
  for (const group of review.equivalent_candidate_groups || []) {
    if (!Array.isArray(group.candidate_ids) || !group.candidate_ids.length || new Set(group.candidate_ids).size !== group.candidate_ids.length) deny('等价候选组为空或重复。');
    const candidates = group.candidate_ids.map(id => result.candidates.find(x => x.id === id));
    if (candidates.some(x => !x || !x.engine_structure_ok || !x.all_constraints_match || !x.comparisons.every(y => y.match))) deny('等价组含未通过原载结构约束的候选。');
    const first = structural(candidates[0].facts, excluded);
    if (candidates.some(x => JSON.stringify(structural(x.facts, excluded)) !== JSON.stringify(first))) deny('等价组存在设置标签以外的完整facts差异。');
    if (group.structural_facts_sha256 && sha(JSON.stringify(first)) !== group.structural_facts_sha256) deny('等价结构hash不符。');
    groups.push({ candidate_ids: group.candidate_ids, excluded_setting_label_paths: excluded,
      representative_candidate_id: candidates[0].id, representative_is_selection: false,
      settings_variants: candidates.map(x => ({ id: x.id, settings: x.input.settings })),
      facts: candidates[0].facts, structural_facts_sha256: sha(JSON.stringify(first)),
      raw_archives: candidates.map(x => ({ id: x.id, ...x.archive })) });
  }
  return { ok: true, id: result.id, original_source_condition: result.original_source_condition,
    raw_archives_verified: result.candidates.length, all_candidate_ids: result.candidates.map(x => x.id), groups };
}
if (isEntryPoint(process.argv[1], import.meta.url)) {
  try {
    const request = JSON.parse(await new Promise((resolve, reject) => { let s = ''; process.stdin.setEncoding('utf8'); process.stdin.on('data', x => { s += x; }); process.stdin.on('end', () => resolve(s)); process.stdin.on('error', reject); }));
    if (Array.isArray(request.requests)) {
      const results = [];
      for (const item of request.requests) {
        try { results.push(await verifyArtifact(item)); }
        catch (error) { results.push({ ok: false, error: error.message }); }
      }
      process.stdout.write(JSON.stringify({ ok: results.every(x => x.ok), results }) + '\n');
    } else process.stdout.write(JSON.stringify(await verifyArtifact(request)) + '\n');
  } catch (error) { process.stdout.write(JSON.stringify({ ok: false, error: error.message }) + '\n'); process.exitCode = 2; }
}
