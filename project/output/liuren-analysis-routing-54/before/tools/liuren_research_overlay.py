"""Attach source-checked research to local retrieval without rewriting old evidence.

Every load checks current source bytes. A supplied semantic review is not an
independent outcome validation. All evidence identities participate in exclusions.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re

OVERLAY = Path('knowledge/liuren-research/20261102')
LABELS = {'retain': '保留参照', 'narrow': '限缩适用范围', 'revise': '旧概括需修订',
          'suspend': '暂停采用该推断', 'pending': '争点待核'}


def identities(record):
    values = set(record.get('support_case_ids', []) + record.get('counterexample_case_ids', [])
                 + record.get('target_case_paths', []) + record.get('source_case_ids', []))
    for ref in record.get('evidence_refs', []) + record.get('source_case_refs', []):
        path = ref.get('path', '')
        # A source book can contain hundreds of different events. Keep span identity,
        # never make its plain path the common identity of every case in that book.
        if path.startswith(('书籍库/', 'books/', '课程写作/整理本/毕法赋全解/')) and type(ref.get('line_start')) is int and type(ref.get('line_end')) is int:
            values.add(f"book:{path}:L{ref['line_start']}-L{ref['line_end']}")
        elif path:
            values.add(path)
        if ref.get('case_id'):
            values.add(ref['case_id'])
    for value in list(values):
        values.update(re.findall(r'raw-[A-Za-z0-9]+-\d{4}[a-z]?(?![A-Za-z0-9])', value))
    return values


def fingerprint(root):
    """Identify the currently loaded rule/audit/family bytes, never predictive validity."""
    root = Path(root)
    files = [path for folder in ('rules', 'audits', 'families')
             for path in sorted((root / OVERLAY / folder).glob('*.json'))]
    identity = [(path.relative_to(root).as_posix(), hashlib.sha256(path.read_bytes()).hexdigest())
                for path in files]
    return hashlib.sha256(json.dumps(identity, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def load(root):
    root = Path(root)
    if not (root / OVERLAY).is_dir():
        return {'rules': [], 'audits': [], 'issues': [], 'summary': {'present': False}}
    from liuren_knowledge_workbench import validated_records
    result = validated_records(root)
    result['summary']['present'] = True
    result['summary']['overlayFingerprint'] = fingerprint(root)
    return result


def audit_notice(audit):
    return {'id': audit['id'], 'disposition': audit['disposition'],
            'action': LABELS[audit['disposition']], 'finding': audit['finding'],
            'reference_value': audit.get('reference_value', ''),
            'action_scope': audit.get('action_scope', '仅针对该审查明确指出的子判断，不否定整份作答'),
            'replacement_rule_ids': audit['replacement_rule_ids'],
            'record_file': audit['_record_file'],
            'evidence_locations': [{k: r[k] for k in ('path', 'line_start', 'line_end', 'sha256', 'role')}
                                   for r in audit['evidence_refs']],
            'limitations': audit['limitations']}


def load_failure(overlay):
    return any('id' not in item and ('error' in item or 'record_file' in item)
               for item in overlay['issues'])


def apply_experience(index, root):
    """Base cache stays unchanged; all new records are an ephemeral read overlay."""
    overlay = load(root)
    if not overlay['summary'].get('present'):
        return index
    result = copy.deepcopy(index)
    result['status']['research_overlay'] = overlay['summary']
    result['status']['research_issues'] = overlay['issues']
    by_id = {e['id']: e for e in result['entries']}
    if load_failure(overlay):
        for entry in result['entries']:
            entry['annotation_status'] += '；附加审查层加载不完整'
            entry['summary'] = '【审查层加载缺口，先核原文】' + entry['summary']
            entry['caveat'] = '【加载缺口】无法确认旧条目是否有关联修订，须修复审查数据或直接核原文；不能把缺失审查当作无问题。' + entry['caveat']
    from liuren_book_cases import provenance, expand_identities, compact_provenance
    book_origins = provenance(root)
    result['book_case_identity_map'] = compact_provenance(book_origins)
    record_identities = {r['id']: expand_identities(identities(r), book_origins, include_dependencies=True)
                         for r in overlay['rules'] + overlay['audits']}
    # Evidence drawn from legacy entries inherits their event/source identity.
    for record in overlay['rules'] + overlay['audits']:
        targets = record.get('legacy_entry_ids', []) + record.get('target_entry_ids', []) + [
            r['target_id'] for r in record.get('relations', [])]
        for old_id in targets:
            old = by_id.get(old_id)
            if old:
                record_identities[record['id']].update([old['source'], *old.get('case_refs', [])])
                record_identities[record['id']].update(re.findall(
                    r'raw-[A-Za-z0-9]+-\d{4}[a-z]?(?![A-Za-z0-9])', old.get('source_excerpt', '')))
        record_identities[record['id']] = expand_identities(record_identities[record['id']], book_origins, include_dependencies=True)
    # Dependency provenance must travel with rules and replacement audits.
    changed = True
    while changed:
        changed = False
        for record in overlay['rules'] + overlay['audits']:
            dest = record_identities[record['id']]
            before = len(dest)
            targets = record.get('replacement_rule_ids', []) + [r['target_id'] for r in record.get('relations', [])]
            for target in targets:
                dest.update(record_identities.get(target, set()))
            changed |= len(dest) != before
    for card in overlay['rules']:
        ref = card['evidence_refs'][0]
        body = {k: card[k] for k in ('conditions', 'exclusions', 'reasoning_steps', 'alternatives', 'limitations')}
        entry = dict(id=card['id'], source=ref['path'], line_start=ref['line_start'], line_end=ref['line_end'],
                     title=card['title'], summary=card['conclusion'], source_excerpt=ref['quote'],
                     categories=card['categories'], kind='审读规则',
                     method_tags=card.get('method_tags', card.get('logic_stages', [])),
                     verification='原文已核对；效果未独立验证',
                     caveat='；'.join(card['limitations']), case_refs=sorted(record_identities[card['id']]),
                     independent_validation_increment=0, source_sha256=ref['sha256'],
                     location_status='本轮证据逐段校验通过',
                     annotation_status=f"{card['claim_origin']}；{card['status']}，保留适用条件",
                     research_card_path=card['_record_file'], research_status=card['status'],
                     reference_value=card.get('reference_value', ''),
                     evidence_refs=card['evidence_refs'], **body)
        # Keep the authoring contract intact. Convenience labels never replace
        # support/counterexample axes, exact identities or branch selectors.
        entry['research_record'] = copy.deepcopy(card)
        for key in ('schema', 'review_state', 'status', 'claim_origin', 'support_case_ids',
                    'counterexample_case_ids', 'legacy_entry_ids', 'relations',
                    'source_case_refs', 'source_case_ids', 'independent_validation_count',
                    'branch_selector', 'member_rule_ids', 'canonical_scope'):
            if key in card:
                entry[key] = copy.deepcopy(card[key])
        entry['qualification'] = dict(source_checked=card.get('review_state', 'source_checked') == 'source_checked',
            suspended=card['status'] == 'suspended',
            adoption_candidate=card['status'] != 'suspended',
            semantic_applicability='must_be_recorded_for_current_question', independent_validation_count=0)
        if card['status'] == 'suspended':
            entry['summary'] = '【暂停采用，仅供审查】' + entry['summary']
        result['entries'].append(entry)
        by_id[entry['id']] = entry
    for card in overlay['rules']:
        for relation in card.get('relations', []):
            target = relation['target_id']
            if target in by_id and target != card['id']:
                # Link without merging individual methods merely because a source overlaps.
                kind = '冲突待核' if relation['type'] == '冲突' else '条件差异'
                result['relations'].append({'id': card['id'] + ':' + target, 'type': kind,
                                            'members': [card['id'], target], 'reason': relation['reason']})
    for audit in overlay['audits']:
        notice = audit_notice(audit)
        for target in audit['target_entry_ids']:
            entry = by_id.get(target)
            if not entry:
                continue
            entry.setdefault('review_notices', []).append(notice)
            entry['case_refs'] = sorted(set(entry.get('case_refs', [])) | record_identities[audit['id']])
            entry['annotation_status'] += '；本轮审查：' + notice['action']
            # Labels survive older renderers and compact serializers too.
            entry['caveat'] = f"【{notice['action']} {audit['id']}】{audit['finding']}；" + entry['caveat']
            if audit['disposition'] in {'revise', 'suspend', 'narrow', 'pending'}:
                entry.setdefault('historical_summary', entry['summary'])
                entry['summary'] = f"【{notice['action']}】历史摘录：" + entry['summary']
            for rule_id in audit['replacement_rule_ids']:
                if rule_id in by_id:
                    result['relations'].append({'id': audit['id'] + ':' + target + ':' + rule_id,
                                                'type': '条件差异', 'members': [target, rule_id],
                                                'reason': audit['finding']})
    for issue in overlay['issues']:
        for target in issue.get('target_entry_ids', []):
            if target in by_id:
                entry = by_id[target]
                entry['annotation_status'] += '；关联审查待核或证据失效'
                entry['caveat'] = '【审查缺口】关联审查未通过当前引用校验，复核前不得据旧摘要直接作结论。' + entry['caveat']
    for family in overlay.get('families', []):
        members = [key for key in family['rule_ids'] + family['legacy_entry_ids'] if key in by_id]
        label = {k: family[k] for k in ('id', 'title', 'merge_type')}
        for member in members:
            by_id[member].setdefault('rule_families', []).append(label)
        if family['merge_type'] == '同源归并':
            old_members = [key for key in family['legacy_entry_ids'] if key in by_id]
            if len(old_members) > 1:
                result['relations'].append({'id': family['id'], 'type': '同源复写',
                                            'members': old_members, 'reason': family['common_method']})
    result['status']['research_rule_entries'] = len(overlay['rules'])
    result['status']['research_audits'] = len(overlay['audits'])
    result['status']['entries'] = len(result['entries'])
    result['research_fingerprint'] = hashlib.sha256(json.dumps(overlay, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    return result


def apply_cases(index, root):
    """Case-level audit notices use the same validated evidence as rule retrieval."""
    overlay = load(root)
    if not overlay['summary'].get('present'):
        return index
    result = copy.deepcopy(index)
    result['status']['research_overlay'] = overlay['summary']
    result['status']['research_issues'] = overlay['issues']
    by_path = {r['source']: r for r in result['cases']}
    # Keep completion, derivation gaps and outcome limits on separate axes.
    # These side tables annotate the cited case; they never upgrade validation.
    review_dir = root / 'knowledge/liuren-research/20261102/method-reviews'
    reviews = {}
    current_hashes = {}
    def current_hash(relative):
        if relative not in current_hashes:
            path = root / relative
            current_hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
        return current_hashes[relative]
    if review_dir.exists():
        for path in sorted(review_dir.glob('*.json')):
            for review in json.loads(path.read_text('utf-8-sig')):
                refs = review.get('source_refs', [])
                if refs and all(current_hash(ref['path']) == ref['sha256'] for ref in refs):
                    reviews[review['case_id']] = dict(record=review, path=path.relative_to(root).as_posix(),
                        sha256=hashlib.sha256(path.read_bytes()).hexdigest())
    dimensions_path = root / 'output/liuren-modern-102-20261102/method-dimensions.json'
    dimensions = {x['case_id']: x for x in json.loads(dimensions_path.read_text('utf-8-sig'))} if dimensions_path.is_file() else {}
    for record in result['cases']:
        key = record.get('book_case_id')
        if key in reviews:
            record['method_review'] = copy.deepcopy(reviews[key])
            if key in dimensions:
                record['method_dimensions'] = dict(record=copy.deepcopy(dimensions[key]),
                    path=dimensions_path.relative_to(root).as_posix(),
                    sha256=hashlib.sha256(dimensions_path.read_bytes()).hexdigest())
    if load_failure(overlay):
        for record in result['cases']:
            record['annotation_status'] += '；附加审查层加载不完整，不能把缺失审查当作无问题'
    from liuren_book_cases import provenance, expand_identities
    book_origins = provenance(root)
    origins = {r['id']: expand_identities(identities(r), book_origins, include_dependencies=True) for r in overlay['rules'] + overlay['audits']}
    changed = True
    while changed:
        changed = False
        for item in overlay['rules'] + overlay['audits']:
            before = len(origins[item['id']])
            targets = item.get('replacement_rule_ids', []) + [r['target_id'] for r in item.get('relations', [])]
            for target in targets:
                origins[item['id']].update(origins.get(target, set()))
            changed |= before != len(origins[item['id']])
    for audit in overlay['audits']:
        for path in audit['target_case_paths']:
            record = by_path.get(path)
            if not record:
                continue
            record.setdefault('review_notices', []).append(audit_notice(audit))
            record['annotation_status'] += '；本轮审查：' + LABELS[audit['disposition']]
            linked = origins[audit['id']]
            record['origin_keys'] = sorted(set(record['origin_keys']) | linked)
            record['mentioned_source_ids'] = sorted(set(record['mentioned_source_ids']) | linked)
    for issue in overlay['issues']:
        for path in issue.get('target_case_paths', []):
            if path in by_path:
                by_path[path]['annotation_status'] += '；关联审查待核或证据失效，复核前不得据旧AI归纳直接作结论'
    for family in overlay.get('families', []):
        if family['merge_type'] != '同源归并':
            continue
        paths = {branch.get('source_path') for branch in family['preserved_branches']}
        groups = {by_path[path]['source_group'] for path in paths if path in by_path}
        members = [r for r in result['cases'] if r['source_group'] in groups]
        if len(members) > 1:
            keys = sorted({key for member in members for key in member['origin_keys']})
            for member in members:
                member['source_group'] = 'research:' + family['id']
                member['origin_keys'] = keys
                member['annotation_status'] += '；已核同源归并：' + family['id']
    result['status']['source_groups'] = len({r['source_group'] for r in result['cases']})
    return result
