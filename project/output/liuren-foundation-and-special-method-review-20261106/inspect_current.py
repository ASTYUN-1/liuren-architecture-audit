"""Read-only workspace investigation; writes only a compact adjacent snapshot."""
from pathlib import Path
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import liuren_knowledge_workbench as workbench

def read(relative):
    return json.loads((ROOT / relative).read_text('utf-8-sig'))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

result = workbench.build(ROOT)
coverage = result['coverage']
validation = result['validation']
eligible_ids = {c['id'] for c in validation['records'] if c['eligible_for_search']}
eligible = [r for r in result['records'] if r.get('id') in eligible_ids]
rules = [r for r in eligible if r['schema'] == 'liuren-rule-card-v1']
catalog = read('docs/经验库梳理/20261019/data/catalog.json')
active = read('.opencode/liuren-active.json')
receipt = read('output/liuren-workflow-boundaries-20261106/activation-receipt.json')
snapshot = {
    'schema': 'liuren-foundation-review-snapshot-v1',
    'built_at': datetime.now(timezone.utc).isoformat(),
    'scope': 'offline maintenance investigation; no prediction retrieval or activation',
    'active_release': active['release'],
    'active_receipt_checks': {p: digest(ROOT/p) == h for p,h in receipt['files'].items()},
    'coverage': {k: coverage[k] for k in (
        'asset_counts', 'legacy_entry_count', 'legacy_entries_semantically_audited',
        'case_paths_semantically_audited', 'source_files_with_checked_evidence',
        'checked_evidence_line_union_count', 'new_rule_count', 'audit_count',
        'explicit_rule_family_count', 'eligible_checked_record_count',
        'pending_legacy_entry_audits', 'independent_validation_count', 'complete')},
    'legacy_index': coverage['legacy_index'],
    'catalog_kinds': dict(Counter(r['kind'] for r in catalog['entries'])),
    'catalog_verification_labels': dict(Counter(r['verification'] for r in catalog['entries'])),
    'validation_summary': {k: validation[k] for k in ('record_count','passed','blocked','valid','complete','warning')},
    'validation_load_errors': validation['load_errors'],
    'eligible_rules': len(rules),
    'eligible_rule_statuses': dict(Counter(r['status'] for r in rules)),
    'eligible_audits': sum(r['schema'] == 'liuren-audit-v1' for r in eligible),
    'blocked_or_pending_record_ids': [r['id'] for r in validation['records'] if not r['eligible_for_search']],
    'method_comparisons': [],
    'packet_summary': [],
    'review_examples': [],
    'limits': ['Counts are retrieval units, not independent rules or validated predictions.',
               'Source_checked and mechanical checks do not establish predictive accuracy.',
               'This script does not read held-out private answers or mark new reading complete.'],
}
snapshot['potential_retrieval_unit_count'] = coverage['legacy_entry_count'] + len(rules)
for relative in ('methods/timing.md','methods/quantity.md','references/quantity-sources.md'):
    versions = {}
    for release in (active['release'], active['previousRelease'], '20261105-restructure-01'):
        path = ROOT / 'runtime/liuren' / release / relative
        versions[release] = {'bytes': path.stat().st_size, 'sha256': digest(path)}
    snapshot['method_comparisons'].append({'file':relative,'versions':versions,
        'all_equal': len({v['sha256'] for v in versions.values()}) == 1})
repair = read('output/liuren-screen-repair-investigation-20261106/summary.json')
for item in repair['packetFiles']:
    raw = read(item['path'])
    packet = raw.get('packet', raw.get('input', raw))
    if 'chart' not in packet:
        snapshot['packet_summary'].append({'path':item['path'], 'wrapper_keys':list(raw)})
        continue
    plate = {r['di']:r['tian'] for r in packet['chart']['facts']['heaven_earth']}
    snapshot['packet_summary'].append({
        'path':item['path'], 'sha256_matches_prior_export':digest(ROOT/item['path']) == item['sha256'],
        'initial_yin_by_tian_on_di': {r['diZhi']:plate[r['diZhi']] for r in packet['chart']['facts']['transmissions']},
        'method_materials':[{'id':r['id'],'title':r['title'],'chars':len(r['quote'])} for r in packet['method_materials']],
        'special_method_observations':[r for r in packet['observations'] if r['kind']=='special_method'],
        'focus_issues': packet['focus_issues'],
    })
for audit in result['records']:
    if audit.get('id') in ('LA26-LEGACY-001','LA26-LEGACY-002','LA26-LEGACY-003'):
        snapshot['review_examples'].append({k:audit.get(k) for k in
            ('id','title','target_entry_ids','disposition','finding','limitations')})
target = Path(__file__).with_name('current-snapshot.json')
target.write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:snapshot[k] for k in ('active_release','coverage','validation_summary',
    'catalog_kinds','catalog_verification_labels','eligible_rules','eligible_rule_statuses',
    'eligible_audits','potential_retrieval_unit_count')},ensure_ascii=False,indent=2))
print('Active receipt matching:', sum(snapshot['active_receipt_checks'].values()), '/',len(snapshot['active_receipt_checks']))
print('Method comparisons:',[(r['file'],r['all_equal']) for r in snapshot['method_comparisons']])
print('Packets:',[(p['path'],p.get('initial_yin_by_tian_on_di'),p.get('wrapper_keys')) for p in snapshot['packet_summary']])
