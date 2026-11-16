"""Source-backed question retrieval. Scores describe relevance, never correctness.

No LLM, network, chart calculation, semantic rule validation or source rewriting.
"""
from __future__ import annotations

from collections import Counter, defaultdict
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path('output/case-index-v2/index.json')
VERSION = 'case-retrieval-2.0'
ALIASES = {'交易占': '财运占', '考试占': '学业占', '疾病占': '健康占', '灾厄占': '健康占',
           '行人占': '出行占', '宅门占': '家宅占', '比赛占': '事业占', '胎产占': '感情占'}
STEMS = '甲乙丙丁戊己庚辛壬癸'
BRANCHES = '子丑寅卯辰巳午未申酉戌亥'
GENERALS = ['贵人', '腾蛇', '朱雀', '六合', '勾陈', '青龙', '天空', '白虎', '太常', '玄武', '太阴', '天后']
ELEMENTS = dict(zip(STEMS, '木木火火土土金金水水'))
RAW_ID = r'raw-[A-Za-z0-9]+-\d{4}[a-z]?(?![A-Za-z0-9])'
TOPICS = {
    '录用': r'offer|录用|应聘|面试|入职|求职|秋招',
    '去留': r'去留|是去是留|离职|辞职|开除|工作.*动或不动',
    '满意度': r'满意|如意|理想.*工作',
    '调动': r'调动|调岗|轮岗|换岗',
    '应期': r'何时|什么时候|多久|哪[天月年日]|应期|时间|几[天月年日]',
    '数额': r'多少|金额|数额|额度|薪资|工资|价格|价位|比例|百分|几[成条只个元万分]',
    '考试': r'考试|考学|科目[一二三四1234]|上岸|考编|教师编|研究生.*录取|[四六46]级|雅思|托福|考研|高考|中考',
    '索款': r'讨债|索赔|赔偿|欠薪|讨薪|工程款|要回|要到钱',
    '诉讼': r'官司|诉讼|起诉|法律程序|打官司|官讼',
    '感情': r'恋爱|婚姻|结婚|分手|女友|男友|出轨|复合',
    '疾病': r'病情|疾病|手术|病危|住院|健康|生死',
    '生产': r'生产|顺产|剖腹|分娩|生[男女儿]|怀孕',
    '寻找': r'失物|丢失|遗失|找回|寻人|走失',
    '交易': r'交易|生意|买卖|成交|拍卖|利润',
    '出行': r'出行|旅行|行人|回乡|出差',
    '方位': r'方位|方向|哪里|何处|哪[里边方]',
}
CATEGORY_HINTS = {'事业占': {'录用', '去留', '满意度', '调动'}, '学业占': {'考试'},
                  '财运占': {'索款', '交易'}, '官讼占': {'诉讼'}, '健康占': {'疾病'},
                  '感情占': {'感情', '生产'}, '失物占': {'寻找'}, '出行占': {'出行'}}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=path.name, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as out:
            json.dump(value, out, ensure_ascii=False, indent=2)
            out.write('\n')
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def normalize(text):
    text = str(text).lower().replace('返吟', '反吟').replace('螣蛇', '腾蛇').replace('旬空', '空亡')
    digits = dict(zip('一二三四五六七八九十', ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']))
    text = re.sub(r'[一二三四五六七八九十](?=级|科|关)', lambda m: digits[m.group()], text)
    for pattern, replacement in [(r'offer', '录用'), (r'什么时候|何时', '应期'),
                                 (r'薪水|薪酬|薪资', '工资'), (r'打官司|起诉', '诉讼')]:
        text = re.sub(pattern, replacement, text)
    return text


def category(value):
    return ALIASES.get(value, value)


def topics(text):
    return [key for key, pattern in TOPICS.items() if re.search(pattern, text, re.I)]


def tokens(text):
    # Character bigrams support unsegmented Chinese; numbers and long Latin words stay intact.
    text = normalize(text)
    result = set(re.findall(r'[a-z]{2,}|\d{2,}', text))
    for run in re.findall(r'[\u4e00-\u9fff]+', text):
        result.update(run[i:i + 2] for i in range(len(run) - 1))
    return result - {'能否', '是否', '这个', '如何', '什么', '问题', '案例', '可以'}


def meta_fields(lines):
    result = {}
    for line in lines:
        if line.startswith('<!-- META:'):
            for part in line.removeprefix('<!-- META:').split('-->')[0].split('|'):
                if '=' in part:
                    key, value = part.split('=', 1)
                    if value.strip():
                        result.setdefault(key.strip(), value.strip())
    return result


def clean(line):
    return re.sub(r'^\s*(?:[-*]\s+|#{1,6}\s+)', '', line).replace('**', '').strip()


def explicit_fields(lines):
    fields = meta_fields(lines)
    keys = ['占类', '标题', '四柱', '课体', '发用', '中传', '末传', '三传', '日干', '类神',
            '技法', '月将', '旬空', '本命', '行年', '年命', '反馈', '来源ID']
    active = ''
    collecting = False
    for line in lines:
        s = clean(line)
        match = re.match(r'^(' + '|'.join(keys) + r')\s*[:：]\s*(.*)', s)
        if match:
            key, value = match.groups()
            # META values win; additional explicit fields fill gaps, never inferred chart state.
            if value.strip():
                fields.setdefault(key, value.strip())
            active = key if not value.strip() else ''
            collecting = bool(active and key not in fields)
        elif active and collecting and re.match(r'^\s+- ', line):
            fields[active] = (fields.get(active, '') + ',' + s).strip(',')
        else:
            active = ''
            collecting = False
    if not fields.get('日干'):
        pillars = re.findall(r'[' + STEMS + '][' + BRANCHES + ']', fields.get('四柱', ''))
        if len(pillars) == 4:
            fields['日干'] = pillars[2][0]
    if not fields.get('三传') and all(fields.get(k) for k in ['发用', '中传', '末传']):
        sequence = [re.search('[' + BRANCHES + ']', fields[k]) for k in ['发用', '中传', '末传']]
        if all(sequence):
            fields['三传'] = ''.join(x.group() for x in sequence)
    if not fields.get('发用') and fields.get('三传'):
        m = re.search(r'(?:初传\s*)?(?:[' + STEMS + r']?)([' + BRANCHES + r'])\s*[（(]([^）)]+)', fields['三传'])
        if m:
            fields['发用'] = f'{m[1]}({m[2]})'
    return fields


def section_spans(lines):
    starts = []
    fence = None
    for i, line in enumerate(lines):
        marker = re.match(r'^\s*(`{3,}|~{3,})(.*)$', line)
        if fence:
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= fence[1] and not marker[2].strip():
                fence = None
            continue
        if marker:
            fence = (marker[1][0], len(marker[1]))
            continue
        if not fence and re.match(r'^#{1,6}\s+', line):
            starts.append((i, clean(line), len(line) - len(line.lstrip('#'))))
    for i, (a, title, level) in enumerate(starts):
        b = next((pos for pos, _, lev in starts[i + 1:] if lev <= level), len(lines))
        yield a, b, title, level


def quote(lines, a, b):
    return {'line_start': a + 1, 'line_end': b, 'text': '\n'.join(lines[a:b])}


def question_units(lines, title, book=False):
    spans = list(section_spans(lines))
    if book:
        examples = [(a, b, t) for a, b, t, _ in spans if re.match(r'假令[一二三四五六七八九十\d]*\s*[:：]', t)]
        return [(a, b, t, '书籍假令，原文非现实占问') for a, b, t in examples] or [(0, len(lines), title, '书籍方法入口，非独立案例')]
    candidates = []
    for a, b, heading, _ in spans:
        if re.match(r'(?:问题|占问|Q)\s*[一二三四五六七八九十\d]+\s*[:：.、]', heading, re.I):
            candidates.append((a, a + 1, clean(lines[a]).lstrip('#').strip(), '明确子问标题，作答另读原文'))
    # Explicit question sections take precedence over result or analysis sections.
    for a, b, heading, _ in spans:
        if not re.fullmatch(r'(?:问题|占问|占问内容|原始问题|背景[、与及]问题|题目|题面)(?:[（(].*)?', heading):
            continue
        block = '\n'.join(lines[a + 1:b])
        matches = list(re.finditer(r'(?:\bQ\s*\d+|(?<![\d.])\d+[.、](?!\d))\s*[:：]?\s*', block, re.I))
        # A numbered list of answer options is not a list of separate questions.
        if matches and not re.search(r'Q\s*\d+', block, re.I) and sum(bool(re.search(r'[？?]|能否|是否|何时|多少|哪里|何理由', block[m.end():matches[i + 1].start() if i + 1 < len(matches) else len(block)])) for i, m in enumerate(matches)) < 2:
            matches = []
        if len(matches) > 1:
            for i, match in enumerate(matches):
                end = matches[i + 1].start() if i + 1 < len(matches) else len(block)
                text = block[match.start():end].strip()
                start = a + 1 + block[:match.start()].count('\n')
                stop = a + 1 + block[:end].rstrip('\n').count('\n') + 1
                candidates.append((start, min(stop, b), text, '明确编号子问，条件须连读同案背景'))
        elif block.strip():
            candidates.append((a + 1, b, block.strip(), '原问段落，未强行拆分隐含子问'))
    if not candidates:
        for a, b, heading, _ in spans:
            if heading == '原始信息':
                for i in range(a + 1, b):
                    if re.match(r'^(?:背景|问题|占问|题目|所问)\s*[:：]', clean(lines[i])):
                        candidates.append((i, i + 1, clean(lines[i]), '原始信息明确字段'))
    if not candidates:
        at = next((i for i, line in enumerate(lines) if line.startswith('# ')), 0)
        candidates = [(at, at + 1, title, '标题检索入口，原问未独立分段，须核原档')]
    result, seen = [], set()
    for unit in candidates:
        identity = re.sub(r'^(?:问题|Q)\s*\d+\s*[:：]?\s*', '', unit[2], flags=re.I)
        if identity not in seen:
            result.append(unit)
            seen.add(identity)
    return result


def evidence_identity(lines, fields, book):
    spans = list(section_spans(lines))
    assignment = [(a, b, t) for a, b, t, _ in spans if re.search(r'优秀作业|模范答案|未核验作答', t)]
    feedback = [(a, b, t) for a, b, t, _ in spans if re.search(r'反馈|实际结果', t)]
    return {'document_kind': '古籍注解／假令' if book else '案例档案',
            'historical_verdict': fields.get('反馈', '未载'),
            'selected_assignment': '有明确栏目，核对具体材料身份' if assignment else '未定位独立栏目，不等于没有作答',
            'feedback': '有结果／反馈栏目，内容及覆盖范围待核' if feedback else '未定位独立栏目，不自动认定真实结果',
            'feedback_locations': [quote(lines, a, min(b, a + 10)) for a, b, _ in feedback[:3]],
            'assignment_locations': [quote(lines, a, min(b, a + 5)) for a, b, _ in assignment[:2]],
            'experience_state': fields.get('经验状态', '未独立核验'),
            'independent_validation_increment': 0}


def source_files(root):
    directory = root / '案例项目库'
    if not directory.is_dir():
        raise ValueError(f'案例目录缺失：{directory}')
    return {p.relative_to(root).as_posix(): p.read_bytes() for p in sorted(directory.rglob('*.md'))
            if not p.name.startswith('_') and p.name not in {'README.md'} and 'template' not in p.name.lower()}


def legacy_rows(root):
    path = root / '案例项目库/_metadata_index.md'
    if not path.exists():
        return []
    return [meta_fields([line]) for line in path.read_text(encoding='utf-8-sig').splitlines() if line.startswith('<!-- META:')]


def build_index(root=ROOT, files=None, rows=None):
    root = Path(root)
    files = source_files(root) if files is None else files
    from liuren_book_cases import filter_retrieval_sources, provenance, expand_identities, compact_provenance
    files, book_status, book_metadata = filter_retrieval_sources(root, files)
    book_origins = provenance(root) if book_metadata else []
    rows = legacy_rows(root) if rows is None else rows
    records, units, mapped = [], [], defaultdict(list)
    legacy_path = root / '案例项目库/_metadata_index.md'
    legacy_line_numbers = [i + 1 for i, line in enumerate(legacy_path.read_text(encoding='utf-8-sig').splitlines())
                           if line.startswith('<!-- META:')] if legacy_path.exists() else []
    exact_locations = {(Path(source).parts[1], m.group()) for source in files
                       if (m := re.match(r'case-\d+', Path(source).name))}
    for source, data in files.items():
        lines = data.decode('utf-8-sig').splitlines()
        text = '\n'.join(lines)
        fields = explicit_fields(lines[:next((i for i, l in enumerate(lines) if l.startswith('# ')), len(lines))])
        # Read explicit fields from original/chart sections, not conclusions or later revisions.
        for a, b, heading, _ in section_spans(lines):
            if heading in {'原始信息', '课式', '课式数据', '排盘详细', '四课三传'}:
                for key, val in explicit_fields(lines[a:b]).items():
                    fields.setdefault(key, val)
        number = re.match(r'case-\d+', Path(source).name)
        number = number.group() if number else fields.get('编号', Path(source).stem)
        cat = fields.get('占类', Path(source).parts[1])
        candidates = [(i, row) for i, row in enumerate(rows) if row.get('编号') == number]
        folder = Path(source).parts[1]
        declared_header = set(re.findall(RAW_ID, fields.get('来源ID', '')))
        identity_matches = [(i, row) for i, row in candidates if declared_header.intersection(re.findall(RAW_ID, row.get('来源ID', '')))]
        exact = [(i, row) for i, row in candidates if row.get('占类') == folder]
        named = [(i, row) for i, row in candidates if row.get('占类') == cat
                 and (row.get('占类'), number) not in exact_locations]
        # Alias equivalence must not join e.g. 疾病占/case-001 and 灾厄占/case-001.
        aliases = [(i, row) for i, row in candidates if category(row.get('占类', '')) == category(cat)
                   and (row.get('占类'), number) not in exact_locations]
        matches = identity_matches or exact or named or aliases
        supplement = {}
        if len(matches) == 1:
            i, row = matches[0]
            mapped[i].append(source)
            # Old index fills absent fields only, explicitly labelled and reported on conflict.
            supplement = {key: val for key, val in row.items() if key not in fields}
        def comparable(key, val):
            if key == '占类':
                return category(val)
            if key in {'课体', '技法'}:
                return field_set(val.strip('[]').removesuffix('---'))
            return normalize(val).strip()
        legacy_conflicts = {key: {'source': fields[key], 'legacy': val} for _, row in matches
                            for key, val in row.items() if key in fields and comparable(key, fields[key]) != comparable(key, val)}
        effective = dict(supplement, **fields)
        title = fields.get('标题') or next((clean(x) for x in lines if x.startswith('# ')), Path(source).stem)
        book = cat == '古籍注解' or '一字诀玉连环注解' in source
        source_ids = sorted(set(re.findall(RAW_ID, text)))
        # References to other raw cases aren't declarations. Prefer explicit source fields.
        declared = sorted(set(re.findall(RAW_ID, ' '.join(fields.get(k, '') for k in ['来源ID', '来源编号', '源编号']))))
        if not declared:
            declared = sorted(set(re.findall(r'(?:来源ID|来源编号|源编号)\s*[:：=]\s*(' + RAW_ID + ')', text)))
        book_record = book_metadata.get(source)
        if book_record:
            declared = sorted(expand_identities({book_record['id'], book_record['source_case_identity'], source}, book_origins))
            source_ids = sorted(set(source_ids) | set(declared))
            # Borrowed previous-case charts contaminate a comparison, but are not
            # declarations that the two events are the same event.
            dependency_ids = set().union(*(m.get('dependency_keys', set()) for m in book_origins if m['id'] == book_record['id']))
            source_ids = sorted(set(source_ids) | expand_identities(dependency_ids, book_origins, include_dependencies=True))
        key = 'case-' + sha(source.encode())[:16]
        supporting = []
        context_locations = []
        for a, b, heading, _ in section_spans(lines):
            if re.search(r'经验提炼|技法提炼|证据与边界|原始断法|反推分析|复盘与边界', heading):
                supporting.append(dict(heading=heading, **quote(lines, a, min(b, a + 14))))
            if re.fullmatch(r'问题|占问|占问内容|原始问题|背景[、与及]问题|题目|题面', heading):
                context_locations.append(quote(lines, a, b))
        record = dict(id=key, source=source, source_sha256=sha(data), title=title,
                      category=category(cat), source_ids=declared, mentioned_source_ids=source_ids,
                      fields=effective, source_fields=fields, legacy_supplement=supplement,
                      legacy_index_location={'source': '案例项目库/_metadata_index.md',
                                             'line_start': legacy_line_numbers[matches[0][0]] if len(matches) == 1 and matches[0][0] < len(legacy_line_numbers) else None},
                      legacy_conflicts=legacy_conflicts, evidence=evidence_identity(lines, effective, book),
                      method_locations=supporting[:5], context_locations=context_locations[:3], origin_keys=declared or [source],
                      annotation_status='程序抽取检索字段，未进行术理或真实性核验')
        if book_record:
            record['book_case_id'] = book_record['id']
            record['book_source_identity'] = book_record['source_case_identity']
            record['original_category'] = book_record['category']
            record['classification'] = {k: book_record[k] for k in ('subcategories', 'taxonomy', 'judgment_logic', 'logic_tags') if k in book_record}
            record['source_refs'] = [{k: ref[k] for k in ('path', 'line_start', 'line_end', 'sha256', 'role')}
                                     for ref in book_record['source_refs']]
            record['evidence'].update(document_kind='书籍原载完整案例', feedback=book_record['feedback_status'],
                                      historical_verdict=book_record['feedback_status'],
                                      independent_validation_increment=0)
            record['annotation_status'] += '；整案原文已机械校验，完整性与反馈身份按登记，非独立验证'
        records.append(record)
        for a, b, question, status in question_units(lines, title, book):
            # Each hypothetical example keeps its own chart, never borrowing another example's.
            local = explicit_fields(lines[a:b]) if book else effective
            uid = key + '-q-' + sha((question + status).encode())[:12]
            units.append(dict(id=uid, case_id=key, source=source, question=question,
                              question_location=quote(lines, a, b), extraction_status=status,
                              topics=topics(question), fields=local,
                              event_key=(source + '#' + uid) if book else key,
                              unit_kind=('书籍假令' if '假令，' in status else '书籍方法') if book else '案例问题'))
    # Group only byte-identical copies or explicit common source identifiers.
    parent = {r['id']: r['id'] for r in records}
    def find(k):
        while k != parent[k]:
            parent[k] = parent[parent[k]]
            k = parent[k]
        return k
    identities = {}
    for r in records:
        for value in ['sha:' + r['source_sha256'], *['source:' + x for x in r['source_ids']]]:
            if value in identities:
                parent[find(r['id'])] = find(identities[value])
            identities[value] = r['id']
    for r in records:
        r['source_group'] = find(r['id'])
    origins = defaultdict(set)
    for r in records:
        origins[r['source_group']].update([r['source'], *r['source_ids']])
    for r in records:
        r['origin_keys'] = sorted(origins[r['source_group']])
    df = Counter()
    for u in units:
        df.update(tokens(u['question']))
    audit = {'legacy_rows': len(rows), 'mapped_rows': len(mapped),
             'unmapped_rows': [row for i, row in enumerate(rows) if i not in mapped],
             'ambiguous_rows': [dict(row=rows[i], files=ps) for i, ps in mapped.items() if len(ps) > 1],
             'files_without_unique_legacy_row': [r['source'] for r in records if r['source'] not in {p for ps in mapped.values() for p in ps}],
             'conflicting_files': [dict(source=r['source'], fields=r['legacy_conflicts']) for r in records if r['legacy_conflicts']]}
    return dict(schema=VERSION, cases=records, units=units, token_df=dict(df), legacy_audit=audit,
                book_case_identity_map=compact_provenance(book_origins),
                status={'source_files': len(records), 'case_files': sum(r['evidence']['document_kind'] == '案例档案' for r in records),
                        'book_files': sum(r['evidence']['document_kind'] != '案例档案' for r in records),
                        'question_units': len(units), 'explicit_question_units': sum('标题检索入口' not in u['extraction_status'] and u['unit_kind'] == '案例问题' for u in units),
                        'title_fallback_units': sum('标题检索入口' in u['extraction_status'] for u in units),
                        'source_groups': len({r['source_group'] for r in records}),
                        'book_case_imports': book_status,
                        'missing_fields': {k: sum(not r['fields'].get(k) for r in records if r['evidence']['document_kind'] == '案例档案') for k in ['课体', '发用', '三传', '日干', '类神']}})


def ensure_index(root=ROOT, refresh=False):
    import sys
    tools_path = str(Path(__file__).resolve().parent)
    if tools_path not in sys.path:
        sys.path.insert(0, tools_path)
    from liuren_research_overlay import apply_cases
    root = Path(root)
    files = source_files(root)
    from liuren_book_cases import filter_retrieval_sources
    _, book_status, _ = filter_retrieval_sources(root, files)
    rows = legacy_rows(root)
    fingerprint = sha((VERSION + sha(Path(__file__).read_bytes()) + json.dumps([(name, sha(data)) for name, data in files.items()], ensure_ascii=False)
                       + json.dumps(rows, ensure_ascii=False) + json.dumps(book_status, ensure_ascii=False, sort_keys=True)).encode())
    path = root / CACHE
    if not refresh and path.exists():
        try:
            cached = json.loads(path.read_text(encoding='utf-8'))
            if cached.get('fingerprint') == fingerprint:
                return apply_cases(cached, root)
        except (ValueError, OSError):
            pass
    index = build_index(root, files, rows)
    index['fingerprint'] = fingerprint
    atomic_json(path, index)
    return apply_cases(index, root)


def field_set(value):
    return set(re.split(r'[,，、·\s]+', normalize(value).strip('[]'))) - {''}


def sequence(value):
    return ''.join(re.findall('[' + BRANCHES + ']', value))[:3]


def branch_general(value):
    m = re.search('[' + BRANCHES + ']', value)
    return m.group() if m else '', next((g for g in GENERALS if g in normalize(value)), '')


def six_score(fields, query):
    score = dict.fromkeys(['占类', '课体', '发用', '类神', '三传', '日干'], 0)
    if query.get('占类') and category(fields.get('占类', '')) == category(query['占类']):
        score['占类'] = 25
    a, b = field_set(fields.get('课体', '')), field_set(query.get('课体', ''))
    if a and b:
        score['课体'] = round(20 * len(a & b) / len(a | b), 1)
    a, aj = branch_general(fields.get('发用', ''))
    b, bj = branch_general(query.get('发用', ''))
    if a and a == b:
        score['发用'] = 15 if aj and aj == bj else 8
    # Class god is a structured field; technique text is not a substitute.
    a, b = field_set(fields.get('类神', '')), field_set(query.get('类神', ''))
    if a and b:
        score['类神'] = round(15 * len(a & b) / len(a | b), 1)
    a, b = sequence(fields.get('三传', '')), sequence(query.get('三传', ''))
    def mode(s):
        return tuple((BRANCHES.index(s[i + 1]) - BRANCHES.index(s[i])) % 12 for i in range(2))
    if len(a) == len(b) == 3:
        score['三传'] = 15 if a == b else 8 if mode(a) == mode(b) else 0
    a, b = fields.get('日干', '')[:1], query.get('日干', '')[:1]
    if a in ELEMENTS and b in ELEMENTS and ELEMENTS[a] == ELEMENTS[b]:
        score['日干'] = 10
    return score


def retrieve(index, query='', fields=None, limit=8, exclude=(), strict=False, feedback='', kind=''):
    if limit < 1:
        raise ValueError('limit 必须大于0')
    fields = fields or {}
    if index.get('book_case_identity_map'):
        from liuren_book_cases import expand_identities
        exclude = expand_identities(exclude, index['book_case_identity_map'])
    qt, goal = tokens(query), set(topics(query))
    records = {r['id']: r for r in index['cases']}
    excluded = set()
    for r in index['cases']:
        identity = ' '.join([r['source'], r['id'], *r['mentioned_source_ids'], *r['source_ids'], *r['origin_keys']])
        if any(x and x in identity for x in exclude):
            excluded.add(r['source_group'])
    ranked = []
    for u in index['units']:
        r = records[u['case_id']]
        if r['source_group'] in excluded or (kind and u['unit_kind'] != kind):
            continue
        if feedback and r['evidence']['historical_verdict'] != feedback:
            continue
        uf = dict(u['fields'])
        uf.setdefault('占类', r['category'])
        dims = six_score(uf, fields)
        if strict and any(fields.get(k) and not dims[k] for k in dims):
            continue
        ut = tokens(u['question'])
        common = qt & ut
        context = ' '.join([r['title'], *[loc['text'] for loc in r['context_locations']]])
        context_hits = qt & tokens(context)
        # IDF-weighted query coverage + precision; no retrieval by outcome text.
        weight = lambda t: math.log(1 + (1 + len(index['units'])) / (1 + index['token_df'].get(t, 0)))
        denom = sum(weight(t) for t in qt) or 1
        lexical = sum(weight(t) for t in common) / denom
        lexical = min(1, lexical * (0.65 + 0.35 * len(common) / max(1, len(ut))))
        context_score = 5 * sum(weight(t) for t in context_hits) / denom
        overlap = goal & set(u['topics'])
        goal_score = 20 * len(overlap) / max(1, len(goal))
        method_text = normalize(r['fields'].get('技法', '') + '\n' + '\n'.join(x['text'] for x in r['method_locations']))
        method_hits = [t for t in re.split(r'[\s,，、]+', normalize(query)) if len(t) >= 2 and t in method_text]
        method_score = min(5, len(method_hits) * 2)
        chart = sum(dims.values())
        # Categories alone are weak; still allow the explicit category-only browse mode.
        has_question_match = bool(common or overlap or method_hits or context_hits)
        if (query or any(fields.values())) and not (has_question_match or chart):
            continue
        relevance = round(40 * lexical + context_score + goal_score + 0.30 * chart + method_score, 2)
        differences = []
        if goal - set(u['topics']):
            differences.append('本次目标未匹配：' + '、'.join(sorted(goal - set(u['topics']))))
        for key, value in fields.items():
            if value and key in dims and not dims[key]:
                differences.append(f'{key}不同或缺失（候选原值：{uf.get(key, "未载")}）')
        if not has_question_match and query:
            differences.append('仅盘面／占类命中，问题情境缺乏匹配，不可直接迁移结论')
        ranked.append(dict(unit=copy.deepcopy(u), case=r, relevance_score=relevance,
                           six_dimensions=dims, six_dimension_total=round(chart, 1),
                           question_score=round(40 * lexical + goal_score, 2), context_score=round(context_score, 2), method_score=method_score,
                           matched_terms=sorted(common), matched_goals=sorted(overlap), method_hits=method_hits,
                           differences=differences, origin_keys=r['origin_keys'], source_group=r['source_group'],
                           transfer_checks=['核对原问对象、时间范围、年命、旺衰空墓及例外',
                                            '历史结论、优秀作业与现实反馈分别核对，不能因相似或称验直接采信']))
    ranked.sort(key=lambda x: (-x['relevance_score'], -x['question_score'], x['unit']['id']))
    groups = {}
    for row in ranked:
        # Keep distinct questions, but return an event/source only once in a bounded packet.
        group = row['source_group'] if row['unit']['unit_kind'] == '案例问题' else row['unit']['event_key']
        if group in groups:
            groups[group]['also_matched_units'].append({k: row['unit'][k] for k in ['id', 'question', 'source', 'question_location']})
        else:
            row['also_matched_units'] = []
            groups[group] = row
    return dict(schema=VERSION, query=query, query_fields=fields, index_fingerprint=index.get('fingerprint'),
                index_status=index['status'], total_matching_units=len(ranked), total_source_groups=len(groups),
                excluded_source_groups=len(excluded), score_semantics='问题相关性与盘面六维分分列；无反馈乘数，不是命中率、置信度或独立验证数。',
                contamination_note='已按已知来源身份排除；未关联同案或转引仍可能遗漏，须核对原档。',
                results=list(groups.values())[:limit])


def public_fields(facts):
    trans = facts.get('transmissions', [])
    return {'课体': ','.join(facts.get('chart_types', [])),
            '发用': f'{trans[0].get("diZhi", "")}({trans[0].get("tianjiang", "")})' if trans else '',
            '三传': facts.get('transmission_sequence', ''), '日干': facts.get('day_stem', '')}


def compact(result, budget=12000):
    all_ids = [row['unit']['id'] for row in result['results']]
    if result['index_status'].get('research_issues'):
        result['index_status'] = copy.deepcopy(result['index_status'])
        issues = result['index_status']['research_issues']
        result['index_status']['research_issue_count'] = len(issues)
        result['index_status']['research_issues'] = [{k: issue[k] for k in ('id', 'record_file', 'errors', 'error')
                                                    if k in issue} for issue in issues]
    for row in result['results']:
        r = row['case']
        row['case'] = {k: r[k] for k in ['id', 'source', 'source_sha256', 'title', 'category', 'fields',
                                        'origin_keys', 'source_group', 'annotation_status', 'evidence',
                                        'legacy_supplement', 'legacy_conflicts', 'legacy_index_location']}
        if r.get('review_notices'):
            row['case']['review_notices'] = r['review_notices']
        for key in ('book_case_id', 'book_source_identity', 'original_category', 'classification',
                    'source_refs', 'independent_validation_count', 'method_review', 'method_dimensions'):
            if key in r:
                row['case'][key] = copy.deepcopy(r[key])
        if 'method_review' in row['case']:
            from experience_retrieval import reference_locators
            review = row['case']['method_review']
            review['record'] = reference_locators(review['record'])
            if 'subjudgments' in review['record']:
                review['subjudgments_count'] = len(review['record'].pop('subjudgments'))
                review['omitted_fields'] = ['subjudgments (full read by case ID)']
        # Identities are facts about source labelling, not independently verified outcomes.
        row['case']['evidence'] = {k: v for k, v in r['evidence'].items() if not k.endswith('_locations')}
        row['method_locations'] = [dict(heading=x['heading'], line_start=x['line_start'], line_end=x['line_end'],
                                        text=x['text'][:300], excerpt_truncated=len(x['text']) > 300)
                                   for x in r['method_locations'][:2]]
        row['also_matched_units'] = [{k: x[k] for k in ['id', 'question', 'source']} for x in row['also_matched_units'][:3]]
        # Long literal source questions are read via position; bounded packet is only a locator.
        for unit in [row['unit'], *row['also_matched_units']]:
            if len(unit['question']) > 650:
                unit['question'] = unit['question'][:650]
                unit['question_truncated'] = True
        loc = row['unit']['question_location']
        loc['text_truncated'] = len(loc['text']) > 650
        loc['text'] = loc['text'][:650]
    omitted = []
    while result['results'] and len(json.dumps(result, ensure_ascii=False)) > budget:
        omitted.append(result['results'].pop()['unit']['id'])
    result['omitted_by_packet_budget'] = len(omitted)
    result['coverage'] = dict(returned_ids=[row['unit']['id'] for row in result['results']],
        omitted_by_budget_ids=omitted[::-1], ranked_ids_before_budget=all_ids,
        total_matching_units=result['total_matching_units'], complete=not omitted and len(all_ids) == result['total_source_groups'],
        structural_fields_truncated=False, question_excerpt_limit=650, method_excerpt_limit=300,
        full_record_command='python -X utf8 tools/liuren-workflow.py read --run RUN --id ID',
        applicability_evaluated=False, packet_over_budget=len(json.dumps(result, ensure_ascii=False)) > budget)
    return result


def evidence_packet(public, source_id='', root=ROOT, limit=6):
    # Only public inputs drive first-stage retrieval. Private feedback never enters this function.
    question = public.get('question', '')
    index = ensure_index(root)
    charts = public.get('charts') or [{'facts': public.get('facts', {})}]
    packets = []
    for chart in charts:
        facts = chart.get('facts', {})
        fields = public_fields(facts)
        hints = [cat for cat, goals in CATEGORY_HINTS.items() if goals.intersection(topics(question))]
        # Use a category only when public question gives a unique hint; never filter other types.
        if len(hints) == 1:
            fields['占类'] = hints[0]
        result = retrieve(index, question, fields, limit, [source_id] if source_id else [])
        packets.append(dict(chart_id=chart.get('chart_id', ''), **compact(result)))
    if len(packets) == 1:
        return packets[0]
    return dict(schema='case-retrieval-multichart-v1', charts=packets,
                note='逐盘检索，不混用三传；多个子问与盘面角色以公开输入为准，同一来源不重复计证。')


def known_exclusions(index, source_id):
    """Share established case origins with experience retrieval before revealing feedback."""
    if not source_id:
        return []
    groups = {r['source_group'] for r in index['cases']
              if source_id in r['mentioned_source_ids'] or source_id in r['source_ids']}
    return sorted({value for r in index['cases'] if r['source_group'] in groups
                   for value in [r['source'], *r['source_ids']]})


def render(result):
    lines = ['# 案例问题级检索', '', result['score_semantics'],
             f"匹配单元 {result['total_matching_units']}；来源／事件组 {result['total_source_groups']}；显示 {len(result['results'])}。", '']
    for row in result['results']:
        u, r = row['unit'], row['case']
        loc = u['question_location']
        lines += [f"- {u['id']}｜{u['question']}", f"  来源：{r['source']}:{loc['line_start']}（结束行 {loc['line_end']}）",
                  f"  相关性 {row['relevance_score']}；问题分 {row['question_score']}；六维 {row['six_dimension_total']}：{row['six_dimensions']}",
                  f"  身份：{r['evidence']['document_kind']}；历史反馈字段：{r['evidence']['historical_verdict']}；{u['extraction_status']}",
                  '  差异：' + ('；'.join(row['differences']) or '字段匹配不代表情境、规则与结果相同'),
                  '  来源身份：' + '、'.join(row['origin_keys']), '']
        for notice in r.get('review_notices', []):
            lines.append(f"  审查 {notice['id']}【{notice['action']}】：{notice['finding']}；记录：{notice['record_file']}")
            if notice.get('reference_value'):
                value = notice['reference_value']
                lines.append('  保留价值：' + ('；'.join(value) if isinstance(value, list) else value))
            lines.append('  处置范围：' + notice['action_scope'])
    if result['index_status'].get('research_issues'):
        lines.append('审查待核/失效：' + json.dumps(result['index_status']['research_issues'], ensure_ascii=False))
    if not result['results']:
        lines.append('无候选；缩短问题、取消严格过滤或查经验／古籍，不编造参照。')
    return '\n'.join(lines) + '\n'
