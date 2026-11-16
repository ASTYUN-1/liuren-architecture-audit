"""Live, source-backed experience retrieval. Ranking never changes validation.

Reviewed annotations are retained only while their exact quote can be located.
New/edited sections enter as unreviewed source fragments, never inferred rules.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = Path('docs/经验库梳理/20261019/data/catalog.json')
CACHE = Path('output/experience-index-v2/index.json')
VERSION = 'experience-retrieval-2.1'
ALIASES = {'交易占': '财运占', '考试占': '学业占', '疾病占': '健康占', '灾厄占': '健康占',
           '行人占': '出行占', '宅门占': '家宅占', '胎产占': '感情占', '比赛占': '事业占',
           '推命占': '推命', '射覆占': '射覆', '杂事占': '杂事', '来意占': '来意'}
SYNONYMS = [('反吟', '返吟'), ('腾蛇', '螣蛇'), ('空亡', '旬空'), ('填实', '填空'),
            ('考试', '考学', '科场', '科目二'), ('讨薪', '欠薪', '讨债', '索债'),
            ('技巧', '技法', '方法')]
STOP_FILES = {'README.md', '_template.md', '_metadata_index.md'}


def load_json(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as out:
            json.dump(data, out, ensure_ascii=False, indent=2)
            out.write('\n')
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def normalize(text):
    text = text.lower()
    for words in SYNONYMS:
        for word in words[1:]:
            text = text.replace(word, words[0])
    return text


def category(value):
    return ALIASES.get(value, value)


def source_files(root):
    directory = root / '经验日志'
    if not directory.is_dir():
        raise ValueError(f'经验日志目录缺失：{directory}')
    return {p.relative_to(root).as_posix(): p.read_bytes()
            for p in sorted(directory.rglob('*.md'))
            if not p.name.startswith('_') and p.name not in STOP_FILES}


def fingerprint(files, catalog_bytes):
    return sha((VERSION + sha(catalog_bytes) + json.dumps(
        [(name, sha(data)) for name, data in files.items()], ensure_ascii=False)).encode())


def sections(lines):
    """Bounded fallback sections. Code fences and META examples are not boundaries."""
    starts = [0]
    fence = False
    for i, line in enumerate(lines):
        if line.lstrip().startswith(('```', '~~~')):
            fence = not fence
        if not fence and (re.match(r'^#{1,6}\s+\S', line) or line.startswith('<!-- META:')):
            starts.append(i)
    starts = sorted(set(starts + [len(lines)]))
    for a, b in zip(starts, starts[1:]):
        # Split long source sections without dropping lines.
        for start in range(a, b, 60):
            end = min(start + 60, b)
            if any(x.strip() and not x.startswith('<!--') for x in lines[start:end]):
                yield start, end


def locate_quote(lines, entry):
    quote = entry['source_excerpt'].splitlines()
    start = entry['line_start'] - 1
    if lines[start:start + len(quote)] == quote:
        return start, start + len(quote), '原文已核对'
    hits = [i for i in range(len(lines) - len(quote) + 1)
            if lines[i:i + len(quote)] == quote]
    if len(hits) == 1:
        return hits[0], hits[0] + len(quote), '原文未变，行号已重定位'
    return None


def build_index(root=ROOT, files=None, catalog_bytes=None):
    files = source_files(root) if files is None else files
    catalog_bytes = (root / SNAPSHOT).read_bytes() if catalog_bytes is None else catalog_bytes
    catalog = json.loads(catalog_bytes.decode('utf-8-sig'))
    old_by_source = defaultdict(list)
    for entry in catalog['entries']:
        old_by_source[entry['source']].append(entry)
    original_hashes = {s['path']: s['sha256'] for s in catalog['sources']}
    entries, stale, changed = [], [], []
    for source, data in files.items():
        lines = data.decode('utf-8-sig').splitlines()
        text = '\n'.join(lines)
        unchanged = sha(data) == original_hashes.get(source)
        if not unchanged:
            changed.append(source)
        covered = set()
        for old in old_by_source[source]:
            found = locate_quote(lines, old)
            if found is None:
                stale.append({'id': old['id'], 'source': source, 'reason': '原文变更或重复定位，旧批注暂不用于检索'})
                continue
            a, b, state = found
            entry = dict(old, line_start=a + 1, line_end=b, source_sha256=sha(data),
                         location_status=state, independent_validation_increment=0)
            if not unchanged:
                # A matching quote does not prove surrounding conditions are unchanged.
                entry['annotation_status'] = '来源已变更，批注需复核'
                entry['caveat'] += ' 来源文件有变更；虽已定位相同原句，摘要与条件须结合当前上下文复核。'
            else:
                entry['annotation_status'] = '已整理批注，非独立实证验证'
            entries.append(entry)
            covered.update(range(a, b))
        # Reviewed unchanged sources keep their curated granularity.
        if unchanged and old_by_source[source]:
            continue
        for a, b in sections(lines):
            if all(i in covered or not lines[i].strip() for i in range(a, b)):
                continue
            excerpt = '\n'.join(lines[a:b])
            title = next((re.sub(r'^#+\s*', '', x).strip() for x in lines[a:b]
                          if x.strip() and not x.startswith('<!--')), Path(source).stem)[:120]
            cats = sorted({category(c) for c in [*ALIASES, *ALIASES.values(), '事业占', '失物占',
                                               '官讼占', '天时占', '出行占', '家宅占', '健康占', '学业占', '财运占', '感情占']
                           if c in text[:1600] or c in source}) or ['待分类']
            entries.append(dict(id='U-' + sha((source + ':' + str(a) + ':' + excerpt).encode())[:16],
                                source=source, line_start=a + 1, line_end=b, title=title,
                                summary='新增或变更原文片段，尚未做技巧归类及条件核对。',
                                categories=cats, method_tags=[], kind='原文片段',
                                verification='未整理待核', source_excerpt=excerpt,
                                source_claim='仅保留原文，不推定验证情况',
                                caveat='不能把自动分段、原文称验或本次检索当作规则验证。',
                                case_refs=[], independent_validation_increment=0,
                                source_sha256=sha(data), location_status='当前原文',
                                annotation_status='未整理待核'))
    live_ids = {e['id'] for e in entries}
    relations = [r for r in catalog['relations'] if all(m in live_ids for m in r['members'])]
    missing = sorted(set(old_by_source) - set(files))
    return dict(schema=VERSION, built_at=datetime.now().isoformat(timespec='seconds'),
                fingerprint=fingerprint(files, catalog_bytes), entries=entries, relations=relations,
                status=dict(source_files=len(files), entries=len(entries),
                            curated_entries=sum(not e['id'].startswith('U-') for e in entries),
                            unreviewed_fragments=sum(e['id'].startswith('U-') for e in entries),
                            changed_or_new_sources=changed, missing_sources=missing,
                            stale_annotations=stale, independent_validation_increment=0))


def ensure_index(root=ROOT, refresh=False):
    # Existing batch/archive callers also load this file through importlib by path.
    import sys
    tools_path = str(Path(__file__).resolve().parent)
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    from liuren_research_overlay import apply_experience
    files = source_files(root)
    catalog_bytes = (root / SNAPSHOT).read_bytes()
    key = fingerprint(files, catalog_bytes)
    path = root / CACHE
    if not refresh and path.exists():
        try:
            cached = load_json(path)
            if cached.get('fingerprint') == key:
                return apply_experience(cached, root)
        except (ValueError, OSError):
            pass
    index = build_index(root, files, catalog_bytes)
    atomic_json(path, index)
    return apply_experience(index, root)


def query_terms(query):
    return list(dict.fromkeys(normalize(x) for x in re.split(r'[\s,，、;；|]+', query) if x))


def reference_locators(value):
    """Preserve identity/role/positions; quote bodies are read by ID, never silently cut."""
    if isinstance(value, list):
        return [reference_locators(item) for item in value]
    if not isinstance(value, dict):
        return value
    result = {key: reference_locators(item) for key, item in value.items() if key != 'quote'}
    if 'quote' in value:
        result.update(quote_sha256=sha(value['quote'].encode('utf-8')), quote_chars=len(value['quote']),
                      quote_body_in_packet=False)
    return result


def retrieve(index, query='', categories=(), kind='', limit=8, exclude=(), match_all=False,
             preferred_categories=(), include_suspended=False):
    if index.get('book_case_identity_map'):
        from liuren_book_cases import expand_identities
        exclude = expand_identities(exclude, index['book_case_identity_map'])
    terms = query_terms(query)
    cats = {category(c) for c in categories if c}
    preferred = {category(c) for c in preferred_categories}
    by_id = {e['id']: e for e in index['entries']}
    relations_by_id = defaultdict(list)
    parent = {key: key for key in by_id}

    def find(key):
        while parent[key] != key:
            parent[key] = parent[parent[key]]
            key = parent[key]
        return key

    # Collapse only explicit same-source rewrites, not merely similar techniques.
    for relation in index['relations']:
        for member in relation['members']:
            relations_by_id[member].append(relation)
        if relation['type'] == '同源复写':
            for member in relation['members'][1:]:
                parent[find(member)] = find(relation['members'][0])
    excluded_ids = set()
    for e in index['entries']:
        identity = ' '.join([e['source'], e['title'], e['source_excerpt'], *e.get('case_refs', [])])
        if any(term and term in identity for term in exclude):
            excluded_ids.add(find(e['id']))
    ranked = []
    for e in index['entries']:
        if find(e['id']) in excluded_ids or (kind and e['kind'] != kind):
            continue
        if not include_suspended and e.get('research_status', e.get('status')) == 'suspended':
            continue
        # Untagged fresh fragments remain searchable; category cannot silently hide them.
        ecats = {category(c) for c in e['categories']}
        if cats and not cats.intersection(ecats) and not ecats.intersection({'通用', '待分类'}):
            continue
        title = normalize(e['title'])
        tags = normalize(' '.join(e.get('method_tags', [])))
        condition_text = '\n'.join(e.get('conditions', []) + e.get('exclusions', []))
        body = normalize(e['summary'] + '\n' + e['source_excerpt'] + '\n' + condition_text)
        hits = [t for t in terms if t in title or t in tags or t in body]
        if terms and (not hits or (match_all and len(hits) != len(terms))):
            continue
        score = sum(5 * (t in title) + 3 * (t in tags) + 1 * (t in body) for t in hits)
        score += 2 if cats.intersection(ecats) else 0
        score += 4 if preferred.intersection(ecats) else 0
        ranked.append((score, e, hits))
    ranked.sort(key=lambda row: (-row[0], row[1]['id']))
    groups = {}
    for score, e, hits in ranked:
        group = find(e['id'])
        if group in groups:
            groups[group]['also_matched_ids'].append(e['id'])
            groups[group]['also_matched_entries'].append({k: e[k] for k in
                ['id', 'source', 'line_start', 'title', 'summary', 'verification']})
            continue
        touching = relations_by_id[e['id']]
        # Return short opposing/conditional context even if its own keywords differ.
        related = []
        for rel in touching:
            if rel['type'] not in {'条件差异', '冲突待核', '高度重复候选', '同源复写'}:
                continue
            for member in rel['members']:
                if member != e['id'] and member in by_id and find(member) not in excluded_ids:
                    other = by_id[member]
                    if not include_suspended and other.get('research_status', other.get('status')) == 'suspended':
                        continue
                    related.append(dict(id=member, type=rel['type'], reason=rel['reason'],
                                        source=other['source'], line_start=other['line_start'],
                                        summary=other['summary'][:260], verification=other['verification']))
        refs = e.get('case_refs', [])
        groups[group] = dict(entry=e, relevance_score=score, matched_terms=hits,
                             source_group=group, also_matched_ids=[], also_matched_entries=[], related=related[:6],
                             origin_keys=sorted(set([e['source'], *refs, *re.findall(
                                 r'raw-[A-Za-z0-9]+-\d{4}[a-z]?(?![A-Za-z0-9])',
                                 e['source'] + '\n' + e['source_excerpt'])])))
    results = list(groups.values())
    return dict(schema=VERSION, query=query, categories=sorted(cats),
                total_matching_units=len(ranked), total_source_groups=len(results),
                score_semantics='关键词相关性排序，不是正确率或经验置信度；同源跨库引用不增加证据次数。',
                index_status=index['status'], excluded_source_groups=len(excluded_ids),
                coverage=dict(matched_source_groups=len(results), returned_ids=[x['entry']['id'] for x in results[:limit]],
                    omitted_ids=[x['entry']['id'] for x in results[limit:]],
                    complete=len(results) <= limit, applicability_evaluated=False,
                    full_record_command='python -X utf8 tools/liuren-workflow.py read --run RUN --id ID',
                    review_mode=include_suspended),
                results=results[:limit])


def render(result):
    status = result['index_status']
    lines = ['# 经验细粒度检索', '', f"匹配单元 {result['total_matching_units']}；归并后 {result['total_source_groups']} 组；本次显示 {len(result['results'])} 组。",
             result['score_semantics'],
             f"索引：{status['curated_entries']} 个已整理单元，{status['unreviewed_fragments']} 个待整理片段；失效批注 {len(status['stale_annotations'])}。", '']
    for row in result['results']:
        e = row['entry']
        lines.extend([f"## {e['id']} {e['title']}",
                      f"类型：{e['kind']}；验证：{e['verification']}；批注：{e['annotation_status']}",
                      f"相关性：{row['relevance_score']}；命中词：{'、'.join(row['matched_terms'])}",
                      f"来源：{e['source']}:{e['line_start']}；原文结束行：{e['line_end']}",
                      f"摘要：{e['summary']}", f"限制：{e['caveat']}",
                      f"同源组：{row['source_group']}；同案线索：{'；'.join(row['origin_keys'])}",
                      '原文片段（完整判断请读取上述位置及上下文）：', e['source_excerpt'][:1200]])
        if e.get('research_card_path'):
            lines += [f"规则卡：{e['research_card_path']}（ID {e['id']}）",
                      '成立条件：' + '；'.join(e['conditions']),
                      '排除与缺口：' + '；'.join(e['exclusions']),
                      '判断步骤：' + '；'.join(e['reasoning_steps']),
                      '其他解释与反证：' + '；'.join(e['alternatives'])]
            if e.get('reference_value'):
                lines.append('可取内容：' + str(e['reference_value']))
        for notice in e.get('review_notices', []):
            lines.append(f"审查 {notice['id']}【{notice['action']}】：{notice['finding']}；记录：{notice['record_file']}")
            if notice.get('reference_value'):
                value = notice['reference_value']
                lines.append('保留价值：' + ('；'.join(value) if isinstance(value, list) else value))
            lines.append('处置范围：' + notice['action_scope'])
            if notice['replacement_rule_ids']:
                lines.append('修订规则：' + '、'.join(notice['replacement_rule_ids']))
        for family in e.get('rule_families', []):
            lines.append(f"规则族 {family['id']}：{family['title']}（{family['merge_type']}）")
        if row['also_matched_ids']:
            lines.append('合并显示的同源命中：' + '、'.join(row['also_matched_ids']))
            for other in row['also_matched_entries']:
                lines.append(f"同源方法 {other['id']} {other['source']}:{other['line_start']}｜{other['summary']}｜{other['verification']}")
        for rel in row['related']:
            lines.append(f"关联[{rel['type']}] {rel['id']} {rel['source']}:{rel['line_start']}｜{rel['summary']}｜{rel['verification']}｜{rel['reason']}")
        lines.append('')
    if not result['results']:
        lines.append('未找到候选；改用较短关键词或取消占类过滤，不将无命中视为不存在该方法。')
    if status.get('research_issues'):
        lines.append('本轮审查/规则存在待核或失效记录：' + json.dumps(status['research_issues'], ensure_ascii=False))
    return '\n'.join(lines) + '\n'


def evidence_packet(public, source_id='', root=ROOT, limit=8, extra_query='', exclude_sources=(), index=None):
    facts = public['facts']
    question = public['question']
    # Only public question and program-generated chart facts determine retrieval.
    vocabulary = ['考试', '科目二', '应期', '取数', '病', '婚', '工作', '财', '交易', '讨薪',
                  '失物', '行人', '官讼', '生产', '射覆', '金额', '空亡', '救神']
    terms = [*facts.get('chart_types', []), *[t for t in vocabulary if t in question]]
    terms += re.split(r'[\s,，、]+', extra_query) if extra_query else []
    # Question-based category hints only boost ranking; never hard-filter recall.
    hints = {'学业占': r'考试|考学|科目[一二三四]|科场|录取|上岸',
             '健康占': r'疾病|病情|手术|健康|住院|诊断',
             '财运占': r'交易|欠薪|讨债|金额|生意|拍卖|利润|工程款',
             '事业占': r'工作|升职|调动|求职|应聘',
             '感情占': r'恋爱|婚姻|分手|女友|男友|结婚',
             '失物占': r'失物|丢失|遗失', '出行占': r'出行|行人|旅行',
             '官讼占': r'官司|诉讼|官讼'}
    preferred = [name for name, pattern in hints.items() if re.search(pattern, question)]
    index = ensure_index(root) if index is None else index
    exclude = list(exclude_sources) + ([source_id] if source_id else [])
    if source_id:
        for path in (root / '案例项目库').rglob('case-*.md'):
            if source_id in path.read_text(encoding='utf-8-sig'):
                exclude.append(path.relative_to(root).as_posix())
    result = retrieve(index, ' '.join(dict.fromkeys(terms)), limit=limit, exclude=exclude,
                      preferred_categories=preferred)
    result['category_hints'] = preferred
    status = result['index_status']
    result['index_status'] = {k: v for k, v in status.items() if not isinstance(v, list)}
    result['index_status']['stale_annotation_count'] = len(status['stale_annotations'])
    if status.get('research_issues'):
        result['index_status']['research_issue_count'] = len(status['research_issues'])
        result['index_status']['research_issues'] = [{k: issue[k] for k in ('id', 'record_file', 'errors', 'error')
                                                    if k in issue} for issue in status['research_issues']]
    result['contamination_note'] = '已按来源编号及已定位同案路径排除；未建立联系的转引同案仍可能遗漏，须记录疑似污染。'
    # Keep batch packets small and source-backed; the model can read original context.
    for row in result['results']:
        e = row['entry']
        research = {k: e[k] for k in ('research_card_path', 'research_status', 'conditions', 'exclusions',
            'reasoning_steps', 'alternatives', 'limitations', 'review_notices', 'reference_value', 'rule_families',
            'research_record', 'schema', 'review_state', 'status', 'claim_origin', 'support_case_ids',
            'counterexample_case_ids', 'legacy_entry_ids', 'relations', 'source_case_refs', 'source_case_ids',
            'independent_validation_count', 'branch_selector', 'member_rule_ids', 'canonical_scope',
            'qualification', 'evidence_refs', 'case_refs') if k in e}
        e = {k: e[k] for k in ['id', 'source', 'line_start', 'line_end', 'title', 'summary',
                               'categories', 'kind', 'verification', 'caveat', 'annotation_status',
                               'source_sha256', 'independent_validation_increment']}
        e.update(research)
        if 'research_record' in e:
            full = e.pop('research_record')
            e['full_record'] = dict(id=e['id'], path=e.get('research_card_path', e['source']),
                record_sha256=sha(json.dumps(full, ensure_ascii=False, sort_keys=True).encode()),
                read_by_id=True, quote_bodies_in_packet=False)
        for key in ('evidence_refs', 'source_case_refs'):
            if key in e:
                e[key] = reference_locators(e[key])
        original = row['entry']['source_excerpt']
        e['source_excerpt'] = original[:450]
        e['excerpt_truncated'] = len(original) > 450
        row['entry'] = e
        row['related'] = row['related'][:3]
        row['also_matched_entries_truncated_count'] = max(0, len(row['also_matched_entries']) - 4)
        row['also_matched_entries'] = row['also_matched_entries'][:4]
    # Bound repeated evidence tokens; IDs and positions allow reading full context.
    omitted = []
    while result['results'] and len(json.dumps(result, ensure_ascii=False)) > 9000:
        omitted.append(result['results'].pop()['entry']['id'])
    result['omitted_by_packet_budget'] = len(omitted)
    result['coverage']['omitted_ids'] = omitted[::-1] + result['coverage']['omitted_ids']
    result['coverage']['returned_ids'] = [row['entry']['id'] for row in result['results']]
    result['coverage']['complete'] = not result['coverage']['omitted_ids']
    result['coverage']['excerpt_truncated_ids'] = [row['entry']['id'] for row in result['results'] if row['entry']['excerpt_truncated']]
    result['coverage']['structural_fields_truncated'] = False
    result['coverage']['packet_over_budget'] = len(json.dumps(result, ensure_ascii=False)) > 9000
    return result
