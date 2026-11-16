"""Freeze one cross-owner stage snapshot after owners stop writing their data."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import runpy
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import liuren_book_cases as books
import liuren_knowledge_workbench as workbench
import case_retrieval as cases
import experience_retrieval as experiences

BASE = ROOT / 'knowledge/liuren-research/20261102'
OUT = ROOT / 'output/liuren-knowledge-20261102/book-case-acceptance.json'

def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

frozen = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
          for folder in ['book-cases', 'rules', 'audits', 'families', 'method-reviews']
          for p in sorted((BASE / folder).glob('*.json'))}
imported = books.import_cases(ROOT)
print(json.dumps({'phase': 'import', 'summary': imported['summary'],
                  'active': imported['active'], 'blocked': imported['blocked_or_conflict']}, ensure_ascii=False), flush=True)
case_index = cases.ensure_index(ROOT, refresh=True)
print(json.dumps({'phase': 'case_index', 'status': case_index['status']}, ensure_ascii=False), flush=True)
experience_index = experiences.ensure_index(ROOT, refresh=True)
methods = workbench.validated_records(ROOT)
registry = books.validated_cases(ROOT)
after = {rel: hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() for rel in frozen}
if frozen != after:
    raise RuntimeError('Owner registry changed during final import/index; snapshot must not be accepted')
data = read(OUT) if OUT.exists() else {}
shao_review = read(BASE / 'method-reviews/shao.json')
shao_cards = {name: len(read(BASE / ('rules/' + name + '.json')))
              for name in ['book-shao', 'book-shao-c-review', 'book-shao-canonical']}
by_book = {}
for path in sorted((BASE / 'book-cases').glob('*.json')):
    records = read(path)
    by_book[path.stem] = {'cases': len(records), 'completeness': dict(Counter(r['completeness'] for r in records))}
queries = ['独足 泽 船 陆行', '两巳 四八 七十二', '丑勾 用旧', '申医药 巳厨灶 汤伤', '干神归支', '制鬼良医', '三传递克', '年命填空']
query_results = {q: [r['entry']['id'] for r in experiences.retrieve(experience_index, query=q, limit=8)['results']]
                 for q in queries}
probes = {}
by_id = {entry['id']: entry for entry in experience_index['entries']}
for rid in ['LR26-SHAO-CANON-WATER-LAND', 'LR26-BOOK-SHAO-C049', 'LR26-BOOK-SHAO-C150']:
    entry = by_id.get(rid)
    probes[rid] = {'present': entry is not None,
                  'conclusion': entry.get('summary') if entry else None,
                  'reasoning_steps': entry.get('reasoning_steps', []) if entry else []}
data.update({
    'schema': 'liuren-book-case-acceptance-v2',
    'checked_at': datetime.now(timezone.utc).isoformat(),
    'book_summary': registry['summary'], 'book_breakdown': by_book,
    'case_errors': registry['issues'],
    'import_actions': dict(Counter(x['action'] for x in imported['actions'])),
    'active_imports': imported['active'], 'blocked_imports': imported['blocked_or_conflict'],
    'case_index_cases': len(case_index['cases']), 'book_index': case_index['status'].get('book_case_imports'),
    'methods_summary': methods['summary'], 'method_issues': methods['issues'],
    'experience_index_status': experience_index['status'],
    'current_experience_queries': query_results, 'specific_rule_probes': probes,
    'shao': dict(by_book['shao'], method_cards=sum(shao_cards.values()),
                 original_source_cards=shao_cards['book-shao'],
                 supplemental_source_cards=shao_cards['book-shao-c-review'],
                 canonical_retrieval_rules=shao_cards['book-shao-canonical'],
                 source_coverage_audit='output/liuren-book-cases-20261102/shao-full-source-coverage-audit.json',
                 method_review_complete=False, c_reviewed_cases=len(shao_review),
                 c_subjudgments=sum(len(r['subjudgments']) for r in shao_review),
                 c_supplemental_cards=shao_cards['book-shao-c-review'],
                 c_unreviewed_cases=223-len(shao_review),
                 reviewed_with_method_gaps=sum(not r['method_extraction_complete'] for r in shao_review)),
    'source_registry_sha256': frozen, 'source_registry_stable_during_build': True,
    'validation_note': '阶段停止快照；机械通过、登记完整、可检索、方法审查和独立验证分别统计。全部书、旧库、逐案方法审查及同条件去重尚未完成；独立验证为0。',
    'independent_validation_count': 0, 'complete': False,
})
books.atomic_json(OUT, data)
runpy.run_path(str(ROOT / 'output/liuren-book-cases-20261102/refresh_fragment_queue.py'))
print(json.dumps({'phase': 'final', 'books': data['book_summary'],
                  'active': data['active_imports'], 'blocked': data['blocked_imports'],
                  'methods': data['methods_summary'], 'probes': probes,
                  'queries': query_results}, ensure_ascii=False), flush=True)
if not registry['summary']['valid'] or methods['issues'] or imported['blocked_or_conflict'] or not all(p['present'] for p in probes.values()):
    sys.exit(1)
