"""Rebuild the C-stage mechanical evidence snapshot; no semantic completion inference."""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools'))
import liuren_book_cases as books
import liuren_knowledge_workbench as workbench

BASE = ROOT / 'knowledge/liuren-research/20261102'
def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))

reviews = read(BASE / 'method-reviews/shao.json')
cards = read(BASE / 'rules/book-shao-c-review.json')
canonical_cards = read(BASE / 'rules/book-shao-canonical.json')
families = read(BASE / 'families/book-shao.json')
all_cards = {x['id']: x for path in (BASE / 'rules').glob('*.json') for x in read(path)}
case_map = {x['id']: x for x in read(BASE / 'book-cases/shao.json')}
errors = []
seen = set()
cache = {}
for review in reviews:
    cid = review['case_id']
    if cid in seen:
        errors.append(cid + ': duplicate review')
    seen.add(cid)
    if review['source_case_identity'] != case_map[cid]['source_case_identity']:
        errors.append(cid + ': source identity mismatch')
    for sub in review['subjudgments']:
        if not sub.get('judgment_stage_tags') or not sub.get('judgment') or not sub.get('method_note'):
            errors.append(sub['id'] + ': missing substantive field')
        for rid in sub['rule_ids']:
            if rid not in all_cards or rid not in case_map[cid]['method_rule_ids']:
                errors.append(sub['id'] + ': rule/case link missing ' + rid)
        for ref in sub['evidence_refs']:
            data = cache.setdefault(ref['path'], (ROOT / ref['path']).read_bytes())
            if hashlib.sha256(data).hexdigest() != ref['sha256']:
                errors.append(sub['id'] + ': hash changed')
            lines = books.decode(data).splitlines()
            if '\n'.join(lines[ref['line_start'] - 1:ref['line_end']]) != ref['quote']:
                errors.append(sub['id'] + ': quote/line mismatch')
for card in cards + canonical_cards:
    assigned = [f for f in families if card['id'] in f['rule_ids']]
    if not assigned:
        errors.append(card['id'] + ': no canonical family')
    for family in assigned:
        if card['id'] not in {x['source_rule_id'] for x in family['canonical_rule']['source_rule_map']}:
            errors.append(card['id'] + ': no canonical source map')

registry = books.validated_cases(ROOT)
methods = workbench.validated_records(ROOT)
result = {
    'schema': 'liuren-shao-c-batch-acceptance-v1',
    'reviewed_cases': len(reviews),
    'subjudgments': sum(len(x['subjudgments']) for x in reviews),
    'supplemental_cards': len(cards),
    'canonical_retrieval_rules': len(canonical_cards),
    'total_shao_rules': len(read(BASE / 'rules/book-shao.json')) + len(cards) + len(canonical_cards),
    'reviewed_ids': [x['case_id'] for x in reviews],
    'current_source_extraction_complete_cases': sum(x['method_extraction_complete'] for x in reviews),
    'source_gap_cases': [{'case_id': x['case_id'], 'remaining': x['remaining_actions']} for x in reviews if not x['method_extraction_complete']],
    'all_223_reviewed': len(reviews) == len(case_map),
    'all_book_method_cards_deduplicated': False,
    'evidence_tag_link_errors': errors,
    'mechanical_source_link_pass': not errors,
    'book_registry_summary': registry['summary'],
    'method_registry_summary': methods['summary'],
    'method_registry_issues': methods['issues'],
    'independent_validation_count': 0,
}
books.atomic_json(ROOT / 'output/liuren-book-cases-20261102/shao-c-batch-acceptance.json', result)
print(json.dumps({k: v for k, v in result.items() if k not in {'reviewed_ids', 'source_gap_cases'}}, ensure_ascii=False))
sys.exit(0 if not errors and registry['summary']['valid'] and not methods['issues'] else 1)
