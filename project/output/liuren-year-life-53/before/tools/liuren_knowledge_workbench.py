"""Read-only source inventory and evidence-checked research overlay. Standard library only.

Indexing is not reading, source_checked is a supplied semantic declaration, and neither
is an independent validation of a prediction. No provider calls or production writes.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = 'output/liuren-knowledge-20261102'
OVERLAY = 'knowledge/liuren-research/20261102'
BATCH = 'docs/初级案例整理/初级案例资料/qqwb20261019-有效201例-修订版'
CATALOG = 'docs/经验库梳理/20261019/data/catalog.json'
DEVELOPMENT = 'docs/判断流程优化/20261019/开发样本.json'
TRIAL = 'output/professional-original-output-20261025/trial/selection.json'
TEXT_SUFFIXES = {'.md', '.txt', '.json', '.csv'}
SOURCE_PREFIXES = ('案例项目库/', '经验日志/', 'books/', '书籍库/',
                   'docs/初级案例整理/', 'docs/经验库梳理/', 'docs/判断流程优化/',
                   'docs/六壬知识整理-20261102/')
BIFA_EVIDENCE_PATHS = {'课程写作/整理本/毕法赋全解/原始资料/毕法赋全解DeepSeek转录.md',
                       '课程写作/整理本/毕法赋全解/校勘记录.md'}
ROLES = {'原书断语', '原载反馈', '原载作答', '后人注解', '旧AI归纳', '本轮解释'}
RELATIONS = {'同源复写', '合并候选', '条件分支', '冲突', '修订', '依赖'}
SELECTED_EXPOSED = {'raw-qqwb20261019-' + x for x in ('0002', '0026', '0037', '0200')}
PROGRESS = OUTPUT + '/reading-progress.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def stable(prefix, value):
    return prefix + digest(value.encode('utf-8'))[:20]


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def safe_path(root, relative, *, internal=False, exposed=()):
    """Reject traversal, absolute/drive paths, secret names and escaping symlinks.

    Reserved answer bytes must not be opened by the inventory or next command.
    Answer evidence is opt-in per already exposed case, never blanket opt-in.
    """
    if not isinstance(relative, str) or '\\' in relative or ':' in relative:
        raise ValueError('路径须为项目内正斜杠相对路径')
    part = PurePosixPath(relative)
    if part.is_absolute() or '..' in part.parts or str(part) != relative:
        raise ValueError('拒绝绝对、越界或非规范路径')
    if any(x.startswith('.') or re.search(r'(secret|credential|private.?key|id_rsa|id_ed25519)', x, re.I)
           for x in part.parts):
        raise ValueError('拒绝隐藏配置或凭据路径')
    if part.suffix.lower() not in TEXT_SUFFIXES:
        raise ValueError('仅允许批准的文本资料后缀')
    is_internal = relative.startswith((OVERLAY + '/', OUTPUT + '/')) or relative in {CATALOG, DEVELOPMENT, TRIAL}
    if not relative.startswith(SOURCE_PREFIXES) and relative not in BIFA_EVIDENCE_PATHS and not (internal and is_internal):
        raise ValueError('资料不在批准来源目录')
    if relative.startswith(BATCH + '/'):
        tail = relative[len(BATCH) + 1:]
        sensitive = tail.startswith(('analysis-ready/private/', 'cases/', 'raw/', 'review/'))
        if sensitive and PurePosixPath(tail).stem not in exposed:
            raise ValueError('预留答案禁止读取；只可使用manifest元数据')
    target = (root / relative).resolve()
    if not target.is_relative_to(root.resolve()):
        raise ValueError('符号链接越出项目目录')
    # An in-root symlink must not redirect a public source to an unapproved secret.
    resolved_relative = target.relative_to(root.resolve()).as_posix()
    if resolved_relative != relative:
        raise ValueError('来源路径含重定向链接，需显式核对真实来源')
    return target


def read_bytes(root, relative, **kwargs):
    if relative == 'docs/六壬知识整理-20261102/引擎古例参考源/古例全文.md':
        from liuren_book_cases import verify_engine_reference_chain
        verify_engine_reference_chain(root)
    return safe_path(root, relative, **kwargs).read_bytes()


def load_json(root, relative, **kwargs):
    return json.loads(read_bytes(root, relative, **kwargs).decode('utf-8-sig'))


def text_lines(data):
    return decode_source(data)[0].splitlines()


def decode_source(data):
    if data.startswith((b'\xff\xfe', b'\xfe\xff')):
        return data.decode('utf-16'), 'utf-16-bom'
    try:
        return data.decode('utf-8-sig'), 'utf-8-sig'
    except UnicodeDecodeError:
        return data.decode('gb18030'), 'gb18030-fallback-needs-visual-spot-check'


def optional_json(root, path, default):
    if not (root / path).exists():
        return default
    return load_json(root, path, internal=True)


def exposure_inventory(root, manifest, records):
    development = optional_json(root, DEVELOPMENT, {})
    known = set(development.get('excluded_from_independent_evaluation', []))
    trial = optional_json(root, TRIAL, {})
    trial_ids = set(re.findall(r'raw-qqwb20261019-\d{4}[a-z]?', json.dumps(trial)))
    current = set()
    for record in records:
        for ref in record.get('evidence_refs', []):
            cid = ref.get('case_id', '')
            if cid.startswith('raw-qqwb20261019-') and ref.get('role') in {'原载反馈', '原载作答'}:
                current.add(cid)
            current.update(re.findall(r'raw-qqwb20261019-\d{4}[a-z]?', ref.get('path', '')))
    cases = []
    for item in manifest.get('cases', []):
        cid = item['case_id']
        reasons = []
        if cid in known:
            reasons.append('20261019方法开发已列为曝光')
        if cid in trial_ids:
            reasons.append('20261025实测已使用公开题面；未据此断言读取过答案')
        if cid in current:
            reasons.append('本轮规则或审查引用；用于方法开发')
        cases.append({'case_id': cid, 'exposure': 'known_exposed' if reasons else 'unknown_history',
                      'reasons': reasons or ['历史读取轨迹不完整；不能称干净盲测/holdout'],
                      'answer_access': 'reserved_not_opened_by_workbench',
                      'clean_holdout': False})
    return {'development_case_ids': sorted(known), 'trial_case_ids': sorted(trial_ids),
            'current_reference_case_ids': sorted(current), 'cases': cases,
            'clean_holdout_count': 0,
            'limitation': '已知曝光清单不等于全历史审计。未知组保持未知；本工具不打开预留答案。'}


def selected_exposed_tokens(root):
    """Only specifically selected cases, independently confirmed by the old exposure ledger."""
    known = set(optional_json(root, DEVELOPMENT, {}).get('excluded_from_independent_evaluation', []))
    selected = SELECTED_EXPOSED.intersection(known)
    tokens = set(selected)
    manifest = optional_json(root, BATCH + '/analysis_manifest.json', {})
    for case in manifest.get('cases', []):
        if case.get('case_id') in selected:
            for key in ('public_path', 'private_path'):
                if case.get(key):
                    tokens.add(Path(case[key]).stem)
    return tokens


def load_records(root):
    records, problems = [], []
    for folder in ('rules', 'audits'):
        directory = root / OVERLAY / folder
        for path in sorted(directory.glob('*.json')):
            relative = path.relative_to(root).as_posix()
            try:
                values = load_json(root, relative, internal=True)
                if not isinstance(values, list):
                    raise ValueError('顶层必须为对象数组')
                for number, value in enumerate(values, 1):
                    if not isinstance(value, dict):
                        raise ValueError(f'第{number}项不是对象')
                    records.append(dict(value, _record_file=relative, _record_index=number))
            except (ValueError, OSError) as error:
                problems.append({'record_file': relative, 'error': str(error)})
    return records, problems


def load_families(root, records, legacy_entries, validation):
    """Explicit editorial groups only. A family never adds evidence or merges events."""
    families, issues = [], []
    known_rules = {r.get('id') for r in records if r.get('schema') == 'liuren-rule-card-v1'
                   and isinstance(r.get('id'), str)}
    legacy_ids = {e['id'] for e in legacy_entries}
    checks = {c['id']: c for c in validation['records'] if isinstance(c.get('id'), str)}
    seen = set()
    for path in sorted((root / OVERLAY / 'families').glob('*.json')):
        relative = path.relative_to(root).as_posix()
        try:
            values = load_json(root, relative, internal=True)
            if not isinstance(values, list):
                raise ValueError('规则族顶层须为对象数组')
            for family in values:
                errors = []
                if not isinstance(family, dict):
                    raise ValueError('规则族须为对象')
                for key in ('id', 'title', 'rule_ids', 'legacy_entry_ids', 'merge_type',
                            'common_method', 'preserved_branches', 'unresolved'):
                    if key not in family:
                        errors.append('规则族缺字段:' + key)
                fid = family.get('id')
                if not isinstance(fid, str) or not fid or fid in seen:
                    errors.append('规则族ID缺失或重复')
                if isinstance(fid, str):
                    seen.add(fid)
                for key, identities in (('rule_ids', known_rules), ('legacy_entry_ids', legacy_ids)):
                    array = family.get(key)
                    if not isinstance(array, list) or any(not isinstance(x, str) for x in array):
                        errors.append('规则族ID数组无效:' + key)
                    else:
                        errors.extend('规则族目标不存在:' + x for x in array if x not in identities)
                if errors:
                    issues.append({'record_file': relative, 'family_id': fid, 'errors': errors})
                    continue
                links = [{'id': rid, 'mechanical_state': checks[rid]['mechanical_state'],
                          'semantic_review_state': checks[rid]['semantic_review_state']}
                         for rid in family['rule_ids'] if rid in checks]
                families.append(dict(family, _record_file=relative, linked_card_states=links,
                                     identity='人工显式分组；不是新增证据、独立案例或已验证方法',
                                     independent_validation_increment=0))
        except (ValueError, OSError) as error:
            issues.append({'record_file': relative, 'error': str(error)})
    return families, issues


def remaining_spans(start, end, covered):
    cursor, remaining = start, []
    for a, b in sorted(covered):
        if b < cursor or a > end:
            continue
        if a > cursor:
            remaining.append((cursor, min(end, a - 1)))
        cursor = max(cursor, b + 1)
        if cursor > end:
            break
    if cursor <= end:
        remaining.append((cursor, end))
    return remaining


def reading_progress(root, records, validation):
    """Validate explicit human/model reading declarations; never infer reading from indexing."""
    declarations, issues = [], []
    try:
        manual = optional_json(root, PROGRESS, [])
        if not isinstance(manual, list):
            raise ValueError('reading-progress顶层须为数组')
    except (ValueError, OSError) as error:
        manual = []
        issues.append({'progress_file': PROGRESS, 'error': str(error)})
    declarations.extend(dict(item, declaration_origin='operator_cli') if isinstance(item, dict) else item
                        for item in manual)
    eligible = {c['id'] for c in validation['records'] if c['eligible_for_search']}
    for card in records:
        if not isinstance(card.get('id'), str) or card['id'] not in eligible:
            continue
        spans = card.get('read_spans', [])
        if not isinstance(spans, list):
            issues.append({'record_id': card['id'], 'error': 'read_spans须为数组，未计阅读进度'})
            continue
        refs = card.get('evidence_refs', []) + card.get('source_case_refs', [])
        for span in spans:
            if not isinstance(span, dict):
                issues.append({'record_id': card['id'], 'error': 'read_spans项须为对象'})
                continue
            hashes = {r['sha256'] for r in refs if r.get('path') == span.get('path')}
            if len(hashes) != 1:
                issues.append({'record_id': card['id'], 'path': span.get('path'),
                               'error': '阅读声明缺同路径已核原源hash，未计进度'})
                continue
            declarations.append(dict(span, sha256=next(iter(hashes)), outcome='extracted',
                                     note=span.get('reading_scope', '卡作者声明实际阅读范围'),
                                     linked_record_ids=[card['id']], declaration_origin='source_checked_card_read_spans'))
    known_ids = {r['id'] for r in records if isinstance(r.get('id'), str)}
    valid, cache = [], {}
    selected = selected_exposed_tokens(root)
    for item in declarations:
        try:
            if not isinstance(item, dict):
                raise ValueError('阅读进度项须为对象')
            path = item['path']
            if path not in cache:
                cache[path] = read_bytes(root, path, exposed=selected)
            data = cache[path]
            a, b = item['line_start'], item['line_end']
            if type(a) is not int or type(b) is not int or not (1 <= a <= b <= len(text_lines(data))):
                raise ValueError('阅读声明行号越界')
            if item.get('sha256') != digest(data):
                raise ValueError('阅读声明来源hash变化，须复核')
            if item.get('outcome') not in ('extracted', 'no_new', 'needs_review'):
                raise ValueError('阅读outcome无效')
            if not isinstance(item.get('note'), str) or not item['note'].strip():
                raise ValueError('阅读声明须有实际处理说明note')
            links = item.get('linked_record_ids', [])
            if not isinstance(links, list) or any(not isinstance(x, str) or x not in known_ids for x in links):
                raise ValueError('阅读声明关联记录不存在或类型无效')
            if item['outcome'] == 'extracted' and not links:
                raise ValueError('extracted须关联实际规则/审查记录')
            valid.append(item)
        except (ValueError, OSError, TypeError, KeyError, UnicodeError) as error:
            issues.append({'path': item.get('path') if isinstance(item, dict) else None,
                           'error': str(error), 'counted_as_read': False})
    return {'declarations': valid, 'issues': issues,
            'identity': '操作者/卡作者实际阅读声明；不等于机器证明理解或独立效果验证'}


def record_reading(root, result, *, path, line_start, line_end, sha256, outcome, note, linked_record_ids=()):
    item = {'id': stable('LP26-', f'{path}:{line_start}:{line_end}:{sha256}:{outcome}'),
            'path': path, 'line_start': line_start, 'line_end': line_end, 'sha256': sha256,
            'outcome': outcome, 'note': note, 'linked_record_ids': list(linked_record_ids),
            'declared_at': datetime.now(timezone.utc).isoformat()}
    # Use the same validator before persisting; leave the previous progress intact on failure.
    existing = optional_json(root, PROGRESS, [])
    if not isinstance(existing, list):
        raise ValueError('现有进度文件不是数组，先修复再追加')
    data = read_bytes(root, path, exposed=selected_exposed_tokens(root))
    lines = text_lines(data)
    if sha256 != digest(data) or not (1 <= line_start <= line_end <= len(lines)):
        raise ValueError('当前源hash或行号不符，拒绝登记阅读')
    if outcome not in ('extracted', 'no_new', 'needs_review') or not note.strip():
        raise ValueError('须提供有效outcome和实际处理说明')
    known = {r['id'] for r in result['records'] if isinstance(r.get('id'), str)}
    if any(x not in known for x in linked_record_ids) or (outcome == 'extracted' and not linked_record_ids):
        raise ValueError('关联记录不存在；extracted须有规则/审查ID')
    previous = [x for x in existing if isinstance(x, dict) and x.get('path') == path
                and x.get('line_start') == line_start and x.get('line_end') == line_end]
    item['supersedes'] = [{'id': x.get('id'), 'sha256': x.get('sha256'), 'outcome': x.get('outcome')}
                          for x in previous]
    existing = [x for x in existing if x not in previous]
    existing.append(item)
    target = safe_path(root, PROGRESS, internal=True)
    atomic_json(target, existing)
    return {'recorded': item, 'warning': '仅登记操作者实际阅读声明，未自动升级任何规则语义状态；运行build刷新覆盖表。'}


def windows(lines, size=100):
    """Bounded reading windows, never inferred case/event boundaries."""
    for start in range(0, len(lines), size):
        end = min(start + size, len(lines))
        if any(x.strip() for x in lines[start:end]):
            title = next((x.strip().lstrip('#').strip() for x in lines[start:end]
                          if re.match(r'^#{1,6}\s|^第.{1,12}[章章节回]|^\d+[、.．]', x)), '')
            yield start + 1, end, title[:120]


def build_assets(root):
    assets, tasks, problems = [], [], []
    data_by_path = {}
    for directory in ('案例项目库', '经验日志', 'books', '书籍库'):
        for path in sorted((root / directory).rglob('*')):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            relative = path.relative_to(root).as_posix()
            try:
                data = read_bytes(root, relative)
                decoded, encoding = decode_source(data)
                lines = decoded.splitlines()
            except (ValueError, OSError, UnicodeError) as error:
                problems.append({'path': relative, 'error': str(error)})
                continue
            data_by_path[relative] = data
            auxiliary = path.name.startswith('_') or path.name.lower() in {'readme.md', 'skill.md'}
            if directory == '案例项目库':
                kind = 'classical_annotation' if '一字诀玉连环注解' in relative else 'legacy_case'
                if auxiliary or (kind == 'legacy_case' and not re.match(r'case-\d+', path.name)):
                    kind = 'case_metadata'
            elif directory == '经验日志':
                kind = 'experience_source' if not auxiliary else 'experience_metadata'
            else:
                kind = 'book_text' if path.suffix.lower() in {'.txt', '.md'} and not auxiliary else 'book_auxiliary'
            asset = {'id': stable('LS26-', relative), 'path': relative, 'kind': kind,
                     'sha256': digest(data), 'byte_count': len(data), 'line_count': len(lines),
                     'encoding': encoding,
                     'line_start': 1 if lines else 0, 'line_end': len(lines),
                     'semantic_state': 'pending', 'source_origin_identity': 'unconfirmed',
                     'event_count': None, 'independent_validation_count': 0}
            out_of_scope = '八字书籍/' in relative or any(x in path.name for x in ('三命通会', '滴天髓', '子平', '渊海'))
            asset['scope'] = 'other_tradition_inventory_only' if out_of_scope else 'liuren_or_context_pending_classification'
            if '汇选' in path.name:
                asset['case_boundary_status'] = 'mixed_titles_authors_multiple_cases_pending_review'
                asset['case_boundary_note'] = '目录标题、作者标题与逐例边界混杂，尤其第三章作者下可能多例；标题数不能当案例数。'
            assets.append(asset)
            if not out_of_scope and kind not in {'case_metadata', 'experience_metadata', 'book_auxiliary'}:
                for a, b, title in windows(lines):
                    tasks.append({'id': stable('LT26-', f'{relative}:{a}:{b}'),
                                  'asset_id': asset['id'], 'path': relative, 'line_start': a,
                                  'line_end': b, 'sha256': asset['sha256'], 'heading_hint': title,
                                  'kind': kind, 'state': 'pending', 'visibility': 'source',
                                  'boundary': '阅读窗口，非独立案例边界；续读相邻窗口核对上下文'})
    # Existing experience annotations are imported as links, never upgraded to read.
    legacy_entries, legacy_status = [], {}
    if (root / CATALOG).exists():
        import experience_retrieval
        files = {p: d for p, d in data_by_path.items() if p.startswith('经验日志/')
                 and not Path(p).name.startswith('_') and Path(p).name not in experience_retrieval.STOP_FILES
                 and p.endswith('.md')}
        index = experience_retrieval.build_index(root, files=files,
                                                catalog_bytes=read_bytes(root, CATALOG, internal=True))
        legacy_entries = index['entries']
        legacy_status = index['status']
        by_path = {x['path']: x for x in assets}
        for entry in legacy_entries:
            if entry['source'] in by_path:
                by_path[entry['source']].setdefault('legacy_entry_ids', []).append(entry['id'])
    groups = defaultdict(list)
    for asset in assets:
        groups[asset['sha256']].append(asset['id'])
    identical = [{'sha256': sha, 'asset_ids': ids,
                  'status': 'identical_bytes_only_origin_unconfirmed', 'merge_events': False}
                 for sha, ids in groups.items() if len(ids) > 1]
    return assets, tasks, legacy_entries, legacy_status, identical, problems


def batch_inventory(root):
    relative = BATCH + '/analysis_manifest.json'
    if not (root / relative).exists():
        return {}, [], [], []
    manifest = load_json(root, relative)
    assets, public_tasks, private_tasks = [], [], []
    for item in manifest.get('cases', []):
        cid = item['case_id']
        for visibility in ('public', 'private'):
            rel = BATCH + '/' + item[visibility + '_path']
            # Private hash is copied from manifest; never open its bytes, even for hashing.
            declared_hash = item.get(visibility + '_sha256')
            asset = {'id': stable('LS26-', rel), 'path': rel, 'kind': 'question201_' + visibility,
                     'case_id': cid, 'sha256': declared_hash, 'hash_basis': 'manifest_declared',
                     'semantic_state': 'pending', 'event_count': None,
                     'independent_validation_count': 0}
            if visibility == 'public':
                data = read_bytes(root, rel)
                asset.update(sha256=digest(data), hash_basis='current_bytes',
                             manifest_hash_match=digest(data) == declared_hash,
                             byte_count=len(data), line_count=len(text_lines(data)))
            else:
                asset['content_access'] = 'reserved_not_opened'
            assets.append(asset)
            task = {'id': stable('LT26-', rel), 'asset_id': asset['id'], 'path': rel,
                    'case_id': cid, 'sha256': asset['sha256'], 'visibility': visibility,
                    'kind': 'question201_' + visibility,
                    'state': 'pending' if visibility == 'public' else 'reserved',
                    'line_start': 1 if visibility == 'public' else None,
                    'line_end': asset.get('line_count', 0) if visibility == 'public' else None,
                    'answer_access': 'forbidden_until_public_analysis_frozen_and_explicitly_selected',
                    'has_assignment_reference': item.get('has_assignment_reference'),
                    'has_explicit_feedback': item.get('has_explicit_feedback')}
            (public_tasks if visibility == 'public' else private_tasks).append(task)
    return manifest, assets, public_tasks, private_tasks


def validate_records(root, records, legacy_entries, assets, initial_errors=()):
    checks = []
    ids = [r.get('id') for r in records]
    id_counts = Counter(x for x in ids if isinstance(x, str))
    legacy_ids = {e['id'] for e in legacy_entries}
    case_paths = {a['path'] for a in assets if a['kind'] in {'legacy_case', 'classical_annotation'}}
    known_cases = {a.get('case_id') for a in assets if a.get('case_id')}
    # Library IDs are path-derived; repeated case-001 is never a global identity.
    known_cases |= {a['id'] for a in assets if a['path'] in case_paths}
    known_cases |= {Path(p).stem for p in case_paths}
    # Book-case registration is its own source-preserving layer. Fragments can
    # support limited methods while only complete cases may enter the library.
    from liuren_book_cases import BIFA_TRANSCRIPT_SOURCE, validated_cases
    book_registry = validated_cases(root)
    known_cases |= {r['id'] for r in book_registry['valid_records']}
    known_cases |= {r['source_case_identity'] for r in book_registry['valid_records']}
    known_cases |= {identity for r in book_registry['valid_records'] for identity in r.get('additional_source_case_identities', [])}
    reference_cache = {}
    reference_derived = {}
    exposed_tokens = selected_exposed_tokens(root)
    for record in records:
        errors = []
        rid = record.get('id') if isinstance(record.get('id'), str) else None
        rule = record.get('schema') == 'liuren-rule-card-v1'
        audit = record.get('schema') == 'liuren-audit-v1'
        if not (rule or audit):
            errors.append('schema未知')
        if not isinstance(rid, str) or not rid.startswith('LR26-' if rule else 'LA26-'):
            errors.append('ID前缀无效')
        if isinstance(rid, str) and id_counts[rid] != 1:
            errors.append('ID重复')
        if record.get('review_state') not in ('pending', 'source_checked'):
            errors.append('review_state无效')
        common = ['title', 'evidence_refs', 'limitations']
        required = common + (['categories', 'claim_origin', 'status', 'conditions', 'exclusions',
                              'conclusion', 'reasoning_steps', 'alternatives', 'support_case_ids',
                              'counterexample_case_ids', 'legacy_entry_ids', 'relations',
                              'independent_validation_count'] if rule else
                             ['target_entry_ids', 'target_case_paths', 'disposition', 'finding',
                              'reasoning', 'replacement_rule_ids'])
        for key in required:
            if key not in record:
                errors.append('缺字段:' + key)
        list_fields = (['categories', 'conditions', 'exclusions', 'reasoning_steps', 'alternatives',
                        'limitations'] if rule else ['reasoning', 'limitations'])
        for key in list_fields:
            if not isinstance(record.get(key), list) or not record[key] or any(
                    not isinstance(x, str) or not x.strip() for x in record[key]):
                errors.append('必需非空文本数组:' + key)
        for key in (['title', 'conclusion'] if rule else ['title', 'finding']):
            if not isinstance(record.get(key), str) or not record[key].strip():
                errors.append('必需非空文本:' + key)
        for key in (['support_case_ids', 'counterexample_case_ids', 'legacy_entry_ids', 'relations']
                    if rule else ['target_entry_ids', 'target_case_paths', 'replacement_rule_ids']):
            if not isinstance(record.get(key), list):
                errors.append('必需数组:' + key)
        id_arrays = (['support_case_ids', 'counterexample_case_ids', 'legacy_entry_ids'] if rule else
                     ['target_entry_ids', 'target_case_paths', 'replacement_rule_ids'])
        malformed = False
        for key in id_arrays:
            if not isinstance(record.get(key), list) or any(not isinstance(x, str) for x in record[key]):
                errors.append('ID/路径须为文本数组:' + key)
                malformed = True
        if not isinstance(record.get('relations', []), list):
            malformed = True
        if malformed:
            checks.append({'id': rid, 'record_file': record.get('_record_file'),
                           'semantic_review_state': record.get('review_state'),
                           'mechanical_state': 'blocked', 'eligible_for_search': False,
                           'errors': errors, 'evidence_checks': []})
            continue
        if rule:
            if record.get('claim_origin') not in ('原文明示', '文本可推知', '本轮归纳'):
                errors.append('claim_origin无效')
            if record.get('status') not in ('candidate', 'source_method', 'suspended'):
                errors.append('status无效')
            if record.get('independent_validation_count') != 0:
                errors.append('本轮无独立验证证据，independent_validation_count须为0')
        elif record.get('disposition') not in ('retain', 'narrow', 'revise', 'suspend', 'pending'):
            errors.append('disposition无效')
        refs = record.get('evidence_refs')
        if not isinstance(refs, list) or not refs:
            errors.append('缺实际证据')
            refs = []
        case_refs = record.get('source_case_refs', [])
        if not isinstance(case_refs, list):
            errors.append('source_case_refs须为数组')
            case_refs = []
        for ref in case_refs:
            if not isinstance(ref, dict):
                errors.append('source_case_refs元素须为对象')
                continue
            expected_id = f"book:{ref.get('path')}:L{ref.get('line_start')}-L{ref.get('line_end')}"
            if ref.get('case_id') != expected_id or not (
                    str(ref.get('path', '')).startswith(('books/', '书籍库/'))
                    or ref.get('path') == BIFA_TRANSCRIPT_SOURCE):
                errors.append('书案注册ID须精确等于book:path:Lstart-Lend')
        evidence_checks = []
        for ref in refs + case_refs:
            ref_errors = []
            if not isinstance(ref, dict):
                errors.append('证据不是对象')
                continue
            try:
                path = ref['path']
                if path not in reference_cache:
                    reference_cache[path] = read_bytes(root, path, exposed=exposed_tokens)
                data = reference_cache[path]
                if path not in reference_derived:
                    reference_derived[path] = (text_lines(data), digest(data))
                lines, source_digest = reference_derived[path]
                a, b = ref['line_start'], ref['line_end']
                if type(a) is not int or type(b) is not int or not (1 <= a <= b <= len(lines)):
                    raise ValueError('行号越界')
                if ref.get('sha256') != source_digest:
                    ref_errors.append('source_hash_changed')
                if ref.get('quote') != '\n'.join(lines[a - 1:b]):
                    ref_errors.append('quote_mismatch_or_noncontinuous')
                if not isinstance(ref.get('role'), str) or ref.get('role') not in ROLES:
                    ref_errors.append('role无效')
            except (ValueError, KeyError, TypeError, OSError, UnicodeError) as error:
                ref_errors.append(str(error))
            evidence_checks.append({'path': ref.get('path'), 'errors': ref_errors})
            errors.extend('证据:' + e for e in ref_errors)
        for target in record.get('legacy_entry_ids', []) + record.get('target_entry_ids', []):
            if target not in legacy_ids:
                errors.append('旧条目ID不存在:' + str(target))
        for path in record.get('target_case_paths', []):
            if path not in case_paths:
                errors.append('案例路径不存在:' + str(path))
        for cid in record.get('support_case_ids', []) + record.get('counterexample_case_ids', []):
            book = re.fullmatch(r'book:(.+):L(\d+)-L?(\d+)', cid)
            registered_book_case = False
            if book:
                path, a, b = book[1], int(book[2]), int(book[3])
                registered_book_case = path.startswith(('books/', '书籍库/')) and a <= b and any(
                    ref.get('path') == path and type(ref.get('line_start')) is int and
                    type(ref.get('line_end')) is int and ref['line_start'] <= a <= b <= ref['line_end']
                    for ref in refs + case_refs if isinstance(ref, dict))
            if cid not in known_cases and cid not in case_paths and not registered_book_case:
                errors.append('案例ID未注册:' + str(cid))
        for ref in refs + case_refs:
            if not isinstance(ref, dict) or 'case_id' not in ref:
                continue
            cid = ref['case_id']
            if not isinstance(cid, str):
                errors.append('证据case_id须为文本')
                continue
            if cid in known_cases or cid in case_paths:
                continue
            book = re.fullmatch(r'book:(.+):L(\d+)-L?(\d+)', cid)
            registered = False
            if book:
                path, a, b = book[1], int(book[2]), int(book[3])
                registered = path.startswith(('books/', '书籍库/')) and any(
                    full.get('path') == path and type(full.get('line_start')) is int
                    and type(full.get('line_end')) is int and full['line_start'] <= a <= b <= full['line_end']
                    for full in refs + case_refs if isinstance(full, dict))
            if not registered:
                errors.append('证据案例ID未注册:' + cid)
        for target in record.get('replacement_rule_ids', []):
            if target not in ids or not isinstance(target, str) or not target.startswith('LR26-'):
                errors.append('替换规则不存在:' + str(target))
        for relation in record.get('relations', []):
            if not isinstance(relation, dict):
                errors.append('关系不是对象')
                continue
            if not isinstance(relation.get('type'), str) or relation.get('type') not in RELATIONS or not isinstance(relation.get('reason'), str) or not relation.get('reason', '').strip():
                errors.append('关系类型/理由缺失')
            if not isinstance(relation.get('target_id'), str) or relation.get('target_id') not in ids + list(legacy_ids):
                errors.append('关系目标不存在:' + str(relation.get('target_id')))
        checks.append({'id': rid, 'record_file': record.get('_record_file'),
                       'semantic_review_state': record.get('review_state'),
                       'mechanical_state': 'blocked' if errors else 'pass',
                       'eligible_for_search': not errors and record.get('review_state') == 'source_checked',
                       'errors': errors, 'evidence_checks': evidence_checks})
    # Block transitive dependencies and replacements of invalid source cards.
    blocked = {c['id'] for c in checks if c['mechanical_state'] == 'blocked' and isinstance(c['id'], str)}
    by_id = {r['id']: r for r in records if isinstance(r.get('id'), str)}
    while True:
        changed = False
        for record, check in zip(records, checks):
            deps = list(record.get('replacement_rule_ids') or []) + [r.get('target_id') for r in (record.get('relations') or [])
                              if isinstance(r, dict) and r.get('type') == '依赖']
            broken = [x for x in deps if isinstance(x, str) and x in blocked]
            replacement_active_required = [x for x in (record.get('replacement_rule_ids') or [])
                        if not (record.get('schema') == 'liuren-audit-v1' and record.get('disposition') == 'suspend'
                                and x in by_id and by_id[x].get('status') == 'suspended')]
            strict_deps = replacement_active_required + [r.get('target_id') for r in (record.get('relations') or [])
                            if isinstance(r, dict) and r.get('type') == '依赖']
            broken += [x for x in strict_deps if isinstance(x, str) and x in by_id and
                       (by_id[x].get('review_state') != 'source_checked' or by_id[x].get('status') == 'suspended')]
            if broken and check['id'] not in blocked:
                check['errors'].append('关联记录失效:' + ','.join(broken))
                check.update(mechanical_state='blocked', eligible_for_search=False)
                blocked.add(check['id'])
                changed = True
        if not changed:
            break
    for record, check in zip(records, checks):
        check['target_entry_ids'] = record.get('target_entry_ids', [])
        check['target_case_paths'] = record.get('target_case_paths', [])
        check['related_status_notes'] = [
            {'target_id': rel.get('target_id'), 'type': rel.get('type'),
             'state': 'blocked' if rel.get('target_id') in blocked else by_id[rel['target_id']].get('status'),
             'review_state': by_id[rel['target_id']].get('review_state'),
             'note': '非依赖关联保留其自身身份，不据此断言本卡失效或方法已验证'}
            for rel in (record.get('relations') or []) if isinstance(rel, dict)
            and isinstance(rel.get('target_id'), str) and rel['target_id'] in by_id
            and rel.get('type') != '依赖'
            and (rel['target_id'] in blocked or by_id[rel['target_id']].get('status') == 'suspended'
                 or by_id[rel['target_id']].get('review_state') != 'source_checked')]
    return {'schema': 'liuren-mechanical-validation-v1', 'records': checks,
            'load_errors': list(initial_errors), 'record_count': len(records),
            'passed': sum(c['mechanical_state'] == 'pass' for c in checks),
            'blocked': sum(c['mechanical_state'] == 'blocked' for c in checks), 'complete': False,
            'valid': not initial_errors and all(c['mechanical_state'] == 'pass' for c in checks),
            'warning': '机械通过仅证明字段和引用相符；不证明语义正确、全面精读或预测效果。空集不表示知识整理完成。'}


def build(root=ROOT):
    root = Path(root).resolve()
    records, load_errors = load_records(root)
    assets, tasks, entries, legacy_status, byte_groups, problems = build_assets(root)
    manifest, batch_assets, public_tasks, private_tasks = batch_inventory(root)
    assets.extend(batch_assets)
    exposure = exposure_inventory(root, manifest, records)
    validation = validate_records(root, records, entries, assets, load_errors + problems)
    families, family_errors = load_families(root, records, entries, validation)
    validation['load_errors'].extend(family_errors)
    validation['valid'] = validation['valid'] and not family_errors
    by_id = {r.get('id'): r for r in records if isinstance(r.get('id'), str)}
    checked = [by_id[c['id']] for c in validation['records'] if c['eligible_for_search']]
    reviewed_entries = {x for r in checked for x in r.get('target_entry_ids', [])}
    reviewed_cases = {x for r in checked for x in r.get('target_case_paths', [])}
    # Evidence spans are partial reading claims; no coverage is inferred beyond their exact lines.
    spans = defaultdict(list)
    for r in checked:
        for ref in r.get('evidence_refs', []) + r.get('source_case_refs', []):
            spans[ref['path']].append((ref['line_start'], ref['line_end'], r['id']))
    for task in tasks:
        refs = [rid for a, b, rid in spans.get(task['path'], [])
                if a <= task['line_end'] and b >= task['line_start']]
        if refs:
            task['referenced_by'] = sorted(set(refs))
            task['state'] = 'partially_referenced_pending_full_review'
    for asset in assets:
        asset['declared_checked_spans'] = [{'line_start': a, 'line_end': b, 'record_id': rid}
                                           for a, b, rid in spans.get(asset['path'], [])]
        # Even a source_checked audit is not proof every line of the source was read.
        asset['semantic_state'] = 'partial_evidence_checked' if asset['declared_checked_spans'] else 'pending'
    progress = reading_progress(root, records, validation)
    followups = [dict(d, id=stable('LT26-FOLLOWUP-', f"{d['path']}:{d['line_start']}:{d['line_end']}"),
                      kind='review_followup', visibility='source', state='pending_review')
                 for d in progress['declarations'] if d['outcome'] == 'needs_review']
    validation['reading_progress_issues'] = progress['issues']
    validation['valid'] = validation['valid'] and not progress['issues']
    read_by_path = defaultdict(list)
    for declaration in progress['declarations']:
        read_by_path[declaration['path']].append((declaration['line_start'], declaration['line_end']))
    for task in tasks + public_tasks:
        gaps = remaining_spans(task['line_start'], task['line_end'], read_by_path.get(task['path'], []))
        task['unread_spans'] = [{'line_start': a, 'line_end': b} for a, b in gaps]
        if not gaps:
            task['state'] = 'fully_read_declared'
        elif gaps != [(task['line_start'], task['line_end'])]:
            task['state'] = 'partially_read_declared'
    for asset in assets:
        total = asset.get('line_count')
        if total:
            gaps = remaining_spans(1, total, read_by_path.get(asset['path'], []))
            asset['reading_state'] = 'fully_read_declared' if not gaps else 'pending_or_partial'
            asset['unread_line_count'] = sum(b - a + 1 for a, b in gaps)
    legacy_entry_tasks = []
    for entry in entries:
        audits = [r['id'] for r in checked if entry['id'] in r.get('target_entry_ids', [])]
        legacy_entry_tasks.append({'id': stable('LT26-ENTRY-', entry['id']), 'legacy_entry_id': entry['id'],
            'path': entry['source'], 'line_start': entry['line_start'], 'line_end': entry['line_end'],
            'sha256': entry['source_sha256'], 'kind': 'legacy_entry', 'visibility': 'source',
            'state': 'source_checked_audit' if audits else 'pending', 'review_record_ids': audits})
    checked_lines = sum(len({i for a, b, _ in values for i in range(a, b + 1)})
                        for values in spans.values())
    method_case_ids = sorted({cid for r in checked for cid in r.get('support_case_ids', [])} |
                             {ref['case_id'] for r in checked for ref in r.get('source_case_refs', [])
                              if ref.get('case_id')})
    selected_answer_paths = sorted({ref['path'] for r in checked for ref in r.get('evidence_refs', [])
                                   if ref.get('path', '').startswith(BATCH + '/cases/') or
                                   ref.get('path', '').startswith(BATCH + '/analysis-ready/private/')})
    risks = [{'id': stable('LQ26-', e['id']), 'legacy_entry_id': e['id'], 'path': e['source'],
              'line_start': e['line_start'], 'line_end': e['line_end'],
              'reason': '自动绝对化用语筛查，需逐条核条件及实际反馈', 'state': 'pending',
              'is_semantic_audit': False}
             for e in entries if re.search(r'必[然定有无成死败]|一定|无不|百分之百|百[发占]百[中验]|均应验',
                                           e.get('source_excerpt', ''))]
    coverage = {'schema': 'liuren-knowledge-coverage-v1',
                'asset_counts': dict(Counter(a['kind'] for a in assets)),
                'scope_counts': dict(Counter(a.get('scope', 'question201') for a in assets)),
                'legacy_index': legacy_status, 'legacy_entry_count': len(entries),
                'legacy_entries_semantically_audited': len(reviewed_entries),
                'case_paths_semantically_audited': len(reviewed_cases),
                'source_files_with_checked_evidence': len(spans),
                'checked_evidence_line_union_count': checked_lines,
                'traceable_method_case_ids': method_case_ids,
                'traceable_method_case_count': len(method_case_ids),
                'full_source_read_count': sum(a.get('reading_state') == 'fully_read_declared' for a in assets),
                'reading_window_count': len(tasks),
                'reading_windows_fully_reviewed': 0,
                'reading_windows_fully_read_declared': sum(t['state'] == 'fully_read_declared' for t in tasks),
                'pending_reading_windows': sum(t['state'] != 'fully_read_declared' for t in tasks),
                'explicit_reading_declarations': len(progress['declarations']),
                'declared_read_line_union_count': sum(len({i for a, b in intervals for i in range(a, b + 1)})
                                                       for intervals in read_by_path.values()),
                'unresolved_reading_reviews': len(followups),
                'reading_outcomes': dict(Counter(d['outcome'] for d in progress['declarations'])),
                'pending_legacy_entry_audits': len(entries) - len(reviewed_entries),
                'partially_referenced_windows': sum(bool(t.get('referenced_by')) for t in tasks),
                'new_rule_count': sum(r.get('schema') == 'liuren-rule-card-v1' for r in records),
                'audit_count': sum(r.get('schema') == 'liuren-audit-v1' for r in records),
                'explicit_rule_family_count': len(families),
                'eligible_checked_record_count': len(checked),
                'question201': {'manifest_counts': manifest.get('counts', {}),
                                'source_records': len(manifest.get('cases', [])),
                                'explicit_feedback_sources': sum(bool(x.get('has_explicit_feedback')) for x in manifest.get('cases', [])),
                                'public_tasks': len(public_tasks), 'private_reserved_tasks': len(private_tasks),
                                'private_answer_files_opened': 0,
                                'inventory_reserved_answer_files_opened': 0,
                                'selected_exposed_answer_sources_verified': selected_answer_paths,
                                'independent_event_count': None},
                'risk_queue_count': len(risks), 'complete': False,
                'independent_validation_count': 0,
                'limitations': ['窗口/标题不是独立案例数；混编书籍须另核作者、案例和跨书转引。',
                                '238旧案例等文件数量不等于独立事件；同案多作答不增加事件数。',
                                '808旧批注和自动片段不是本轮精读完成数量。',
                                'hash相同只能说明字节相同；未确证同源不合并事件。',
                                'source_checked是外部逐条审读声明，程序不自动产生该状态。',
                                '书籍全文仍需逐窗阅读；部分证据不代表整窗或整书已读。']}
    coverage['limitations'].append('201份有作答来源均可供方法提取；14仅是manifest明确反馈标签，不是可用样本总数。身份待核不等于无参照价值。')
    return {'schema': 'liuren-knowledge-workbench-v1', 'built_at': datetime.now(timezone.utc).isoformat(),
            'assets': assets, 'tasks': tasks, 'public_tasks': public_tasks, 'private_tasks': private_tasks,
            'legacy_entries': entries, 'identical_byte_groups': byte_groups,
            'records': records, 'validation': validation, 'coverage': coverage,
            'exposure': exposure, 'risk_queue': risks, 'families': families,
            'reading_progress': progress, 'legacy_entry_tasks': legacy_entry_tasks,
            'review_followups': followups}


def validated_records(root=ROOT):
    """Public, read-only integration API. Never writes cache or modifies base entries.

    rules/audits: original cards plus their source file/index; only current hash/quote
    valid and declared source_checked cards. issues: load or per-card failures,
    pending cards included as explicit gaps. summary distinguishes all counts.
    """
    root = Path(root).resolve()
    all_records, load_errors = load_records(root)
    entries, assets = [], []
    if (root / CATALOG).exists():
        import experience_retrieval
        files = {p.relative_to(root).as_posix(): read_bytes(root, p.relative_to(root).as_posix())
                 for p in sorted((root / '经验日志').rglob('*.md'))
                 if not p.name.startswith('_') and p.name not in experience_retrieval.STOP_FILES}
        entries = experience_retrieval.build_index(root, files=files,
                    catalog_bytes=read_bytes(root, CATALOG, internal=True))['entries']
    for path in sorted((root / '案例项目库').rglob('*.md')):
        rel = path.relative_to(root).as_posix()
        if path.name.startswith('_') or path.name.lower() == 'readme.md':
            continue
        if re.match(r'case-\d+', path.name) or '一字诀玉连环注解/' in rel:
            assets.append({'id': stable('LS26-', rel), 'path': rel,
                           'kind': 'classical_annotation' if '一字诀玉连环注解/' in rel else 'legacy_case'})
    manifest = optional_json(root, BATCH + '/analysis_manifest.json', {})
    assets.extend({'case_id': c['case_id'], 'path': BATCH + '/' + c['public_path'],
                   'kind': 'question201_public'} for c in manifest.get('cases', []))
    validation = validate_records(root, all_records, entries, assets, load_errors)
    families, family_errors = load_families(root, all_records, entries, validation)
    validation['load_errors'].extend(family_errors)
    validation['valid'] = validation['valid'] and not family_errors
    eligible = {c['id'] for c in validation['records'] if c['eligible_for_search']}
    records = [r for r in all_records if isinstance(r.get('id'), str) and r['id'] in eligible]
    return {'rules': [r for r in records if r['schema'] == 'liuren-rule-card-v1'],
            'audits': [r for r in records if r['schema'] == 'liuren-audit-v1'],
            'families': families,
            'issues': validation['load_errors'] + [c for c in validation['records']
                                                            if not c['eligible_for_search']],
            'summary': {'record_count': len(all_records), 'eligible_count': len(records),
                        'mechanical_valid': validation['valid'],
                        'explicit_rule_family_count': len(families),
                        'semantic_validation': 'external_review_declaration_only',
                        'independent_validation_count': 0, 'complete': False}}


def write_outputs(root, result):
    files = {'manifest.json': {'schema': result['schema'], 'built_at': result['built_at'],
                               'assets': result['assets'], 'identical_byte_groups': result['identical_byte_groups']},
             'queue.json': result['tasks'], 'public-201-queue.json': result['public_tasks'],
             'private-201-reserved.json': result['private_tasks'], 'legacy-entry-links.json': result['legacy_entries'],
             'validation.json': result['validation'], 'coverage.json': result['coverage'],
             'exposure.json': result['exposure'], 'risk-queue.json': result['risk_queue']}
    files['rule-families.json'] = result['families']
    files['reading-coverage.json'] = result['reading_progress']
    files['legacy-entry-queue.json'] = result['legacy_entry_tasks']
    files['review-followups.json'] = result['review_followups']
    for name, value in files.items():
        path = safe_path(root, OUTPUT + '/' + name, internal=True)
        atomic_json(path, value)
    c = result['coverage']
    report = ['# 六壬知识整理覆盖报告', '', f"构建时间：{result['built_at']}", '',
              '索引、机械校验、语义审查和独立效果验证分别统计。', '',
              f"资产 {len(result['assets'])}；阅读窗口 {len(result['tasks'])}；待读/部分已读 {c['pending_reading_windows']}。",
              f"规则卡 {c['new_rule_count']}；审查卡 {c['audit_count']}；可检索已核记录 {c['eligible_checked_record_count']}。",
              f"旧条目实际关联审查 {c['legacy_entries_semantically_audited']}；案例路径关联审查 {c['case_paths_semantically_audited']}。",
              f"操作者声明整源已读 {c['full_source_read_count']}；仍不等于整源完成语义审查。独立效果验证 0；完成状态 false。", '',
              '201题资产登记只读manifest与public；预留答案打开数0。验证规则引用时只读取明确选中且历史已曝光的作答源。',
              f"已核证据并集 {c['checked_evidence_line_union_count']} 行；可追溯方法案例身份 {c['traceable_method_case_count']} 个，非独立事件计数。",
              '已知曝光与历史未知分列；干净holdout数量0。', '',
              '自动风险队列只供排查，不能计作已完成语义审查。相同字节只分组，未核同源不合并事件。', '',
              *c['limitations']]
    path = safe_path(root, OUTPUT + '/report.md', internal=True)
    path.write_text('\n'.join(report) + '\n', encoding='utf-8')


def search(result, query, limit=8, exclude=()):
    terms = [x for x in re.split(r'[\s,，、]+', query) if x]
    eligible = {c['id'] for c in result['validation']['records'] if c['eligible_for_search']}
    selected = []
    for record in result['records']:
        if record.get('id') not in eligible:
            continue
        body = json.dumps(record, ensure_ascii=False).lower()
        if any(term.lower() in body for term in exclude if term):
            continue
        score = sum(body.count(x.lower()) for x in terms)
        if score or not terms:
            selected.append((score, record))
    selected.sort(key=lambda x: (-x[0], x[1]['id']))
    answer = []
    for score, record in selected[:limit]:
        item = dict(record, retrieval_score=score,
                    identity='已声明逐条核原文且机械通过；非独立效果验证')
        legacy = set(record.get('legacy_entry_ids', []) + record.get('target_entry_ids', []))
        item['linked_audits'] = [a for a in result['records'] if a.get('schema') == 'liuren-audit-v1'
                                  and a.get('id') in eligible and
                                  (record['id'] in a.get('replacement_rule_ids', []) or
                                   legacy.intersection(a.get('target_entry_ids', [])))]
        item['rule_families'] = [{'id': f['id'], 'title': f['title'], 'common_method': f['common_method'],
                                  'preserved_branches': f['preserved_branches'], 'unresolved': f['unresolved'],
                                  'identity': f['identity']} for f in result.get('families', [])
                                 if record['id'] in f['rule_ids'] or legacy.intersection(f['legacy_entry_ids'])]
        answer.append(item)
    return {'query': query, 'results': answer, 'blocked_or_pending_omitted':
            [c['id'] for c in result['validation']['records'] if not c['eligible_for_search']],
            'warning': '相关性排序不代表正确率；使用前阅读条件、排除、反证及完整连续证据。'}


def next_packet(root, result, *, kind=None, limit=1, max_chars=7000, task_id=None, from_line=None):
    candidates = result['tasks'] + result['public_tasks'] + result.get('legacy_entry_tasks', []) + result.get('review_followups', [])
    if kind:
        candidates = [t for t in candidates if t['kind'] == kind]
    if task_id:
        candidates = [t for t in candidates if t['id'] == task_id]
        if not candidates:
            raise ValueError('任务ID不存在或属于预留私有答案')
    else:
        candidates = [t for t in candidates if t['state'] not in {'fully_read_declared', 'source_checked_audit'}]
    if from_line is not None and not task_id:
        raise ValueError('--from-line须与--task-id一同使用')
    packets = []
    for task in candidates[:limit]:
        data = read_bytes(root, task['path'])
        if digest(data) != task['sha256']:
            packets.append({'task': task, 'blocked': '来源变化，重新build并复核旧证据'})
            continue
        lines = text_lines(data)
        a, b = task['line_start'], task['line_end']
        if from_line is not None:
            if not a <= from_line <= b:
                raise ValueError('续读行号须位于所选阅读窗口内')
            a = from_line
        elif 'unread_spans' in task:
            if not task['unread_spans']:
                continue
            a, b = task['unread_spans'][0]['line_start'], task['unread_spans'][0]['line_end']
        target_end = b
        b = min(b, a + 99)
        selected, count = [], 0
        for index in range(a - 1, b):
            line = lines[index]
            if count + len(line) + 1 > max_chars:
                break
            selected.append(line)
            count += len(line) + 1
        if not selected:
            packets.append({'task': task, 'blocked': '首行超过字符预算；明确选择更大max-chars后再读，未伪造截断证据'})
            continue
        end = a + len(selected) - 1
        packets.append({'task': task, 'evidence_window': {'path': task['path'], 'line_start': a,
                        'line_end': end, 'quote': '\n'.join(selected), 'sha256': digest(data)},
                        'remaining_from_line': end + 1 if end < target_end else None,
                        'resume_command': f"python -X utf8 tools/liuren_knowledge_workbench.py next --task-id {task['id']} --from-line {end + 1}" if end < target_end else None,
                        'steps': ['读本窗口及相邻上下文，核清作者/题目/断语/反馈身份；窗口可能跨案或只含一案片段。',
                                  '按数据约定追加规则或审查JSON；保留适用条件、反证及未决问题；不强制每窗产新规则。',
                                  '仅逐条实际核读后写source_checked，不将检索或程序切段计为已读。',
                                  '运行 validate，再 search 检查检索身份；源变更则先复核，禁止沿用旧hash。',
                                  '201题public初判冻结之前，不读取private；未知历史曝光不得称盲测。']})
    return {'packets': packets, 'private_answers_included': False,
            'resume': '按remaining_from_line继续；引用跨度与任务窗口分开计数，索引构建永不自动标精读完成。'}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    for command in ('build', 'validate', 'status'):
        p = sub.add_parser(command)
        if command == 'build':
            p.add_argument('--memory', action='store_true', help='仅在内存构建，不写派生输出')
    p = sub.add_parser('search')
    p.add_argument('query')
    p.add_argument('--limit', type=int, default=8)
    p.add_argument('--exclude', action='append', default=[], help='排除本案原始ID/证据路径等；可重复')
    p = sub.add_parser('next')
    p.add_argument('--kind', choices=['legacy_case', 'classical_annotation', 'experience_source', 'book_text', 'question201_public', 'legacy_entry', 'review_followup'])
    p.add_argument('--limit', type=int, default=1)
    p.add_argument('--max-chars', type=int, default=7000)
    p.add_argument('--task-id')
    p.add_argument('--from-line', type=int)
    p = sub.add_parser('record-reading', help='显式登记实际读过的区间；构建不自动生成该声明')
    p.add_argument('--path', required=True)
    p.add_argument('--line-start', type=int, required=True)
    p.add_argument('--line-end', type=int, required=True)
    p.add_argument('--sha256', required=True)
    p.add_argument('--outcome', choices=['extracted', 'no_new', 'needs_review'], required=True)
    p.add_argument('--note', required=True)
    p.add_argument('--linked-record-id', action='append', default=[])
    args = parser.parse_args(argv)
    try:
        result = build(ROOT)
        if args.command == 'build':
            if not args.memory:
                write_outputs(ROOT, result)
            answer = {'output': None if args.memory else OUTPUT, 'coverage': result['coverage'],
                      'mechanical_valid': result['validation']['valid']}
        elif args.command == 'validate':
            answer = result['validation']
        elif args.command == 'status':
            answer = result['coverage']
        elif args.command == 'search':
            answer = search(result, args.query, max(1, min(args.limit, 30)), exclude=args.exclude)
        elif args.command == 'record-reading':
            answer = record_reading(ROOT, result, path=args.path, line_start=args.line_start,
                                    line_end=args.line_end, sha256=args.sha256, outcome=args.outcome,
                                    note=args.note, linked_record_ids=args.linked_record_id)
        else:
            answer = next_packet(ROOT, result, kind=args.kind, limit=max(1, min(args.limit, 15)),
                                 max_chars=max(100, min(args.max_chars, 30000)), task_id=args.task_id,
                                 from_line=args.from_line)
        print(json.dumps(answer, ensure_ascii=False, indent=2))
        return 0 if args.command == 'record-reading' or result['validation']['valid'] else 2
    except (OSError, ValueError, UnicodeError) as error:
        print(json.dumps({'error': str(error), 'complete': False}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())
