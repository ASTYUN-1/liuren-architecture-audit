"""Validate and import explicitly reviewed whole book cases. No model or network calls.

Source completeness is an editorial declaration, never inferred from a heading count.
Every retrieval verifies the registry, current source bytes and generated-file bytes.
"""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
BASE = 'knowledge/liuren-research/20261102'
DIRECTORY = BASE + '/book-cases'
STATE = 'output/liuren-knowledge-20261102/book-case-imports.json'
BOOKS = {
    'MODERN': '书籍库/现代著作/当代壬占汇选第五版.md',
    'ANCIENT': '书籍库/现代著作/《壬占汇选》.txt',
    'SHAO': '书籍库/经典古籍/唐宋/六壬断案-宋-邵彦和.txt',
    'BIFA': '书籍库/北海闲人/毕法赋全解-正式整理本.md',
}
BIFA_TRANSCRIPT_SOURCE = '课程写作/整理本/毕法赋全解/原始资料/毕法赋全解DeepSeek转录.md'
SUPPLEMENTS = {BIFA_TRANSCRIPT_SOURCE,
               '课程写作/整理本/毕法赋全解/校勘记录.md'}
ENGINE_REFERENCE_DIR = 'docs/六壬知识整理-20261102/引擎古例参考源'
ENGINE_REFERENCE_MD = ENGINE_REFERENCE_DIR + '/古例全文.md'
CATEGORIES = {'事业占', '财运占', '感情占', '学业占', '健康占', '出行占', '失物占', '官讼占', '家宅占', '天时占',
              '来意占', '终身占', '射覆占', '杂事占', '胎产占'}
FEEDBACK = {'原载反馈', '原载断语与结果混合', '未载明确反馈', '身份待核'}
ROLES = {'原书断语', '原载反馈', '原载作答', '后人注解', '旧AI归纳', '本轮解释'}
ID_RE = re.compile(r'BK26-(MODERN|ANCIENT|SHAO|BIFA)-\d{3,}')
IDENTITY_RE = re.compile(r'book:(.+):L(\d+)-L?(\d+)')
HEADER = '<!-- LIUREN_BOOK_CASE '


def sha(data):
    return hashlib.sha256(data).hexdigest()


def path_in_root(root, relative):
    if not isinstance(relative, str) or ':' in relative or '\\' in relative:
        raise ValueError('路径须为项目内正斜杠相对路径')
    part = PurePosixPath(relative)
    if part.is_absolute() or '..' in part.parts or str(part) != relative:
        raise ValueError('拒绝绝对/越界/非规范路径')
    if any(x.startswith('.') or re.search(r'(secret|credential|private.?key|id_rsa|id_ed25519)', x, re.I)
           for x in part.parts):
        raise ValueError('拒绝配置、凭据或隐藏路径')
    root = Path(root).resolve()
    target = (root / relative).resolve()
    if not target.is_relative_to(root) or target.relative_to(root).as_posix() != relative:
        raise ValueError('拒绝越界或重定向链接')
    return target


def source_path(root, relative):
    if relative == ENGINE_REFERENCE_MD:
        verify_engine_reference_chain(root)
    elif relative not in set(BOOKS.values()) | SUPPLEMENTS:
        raise ValueError('非本轮批准原书/校勘来源')
    return path_in_root(root, relative)


def verify_engine_reference_chain(root):
    original_bytes = path_in_root(root, ENGINE_REFERENCE_DIR + '/古例原始对象.json').read_bytes()
    original = json.loads(original_bytes.decode('utf-8-sig'))
    if original.get('schema') != 'liuren-engine-ancient-reference-v1' or original.get('source', {}).get('path') != '排盘工具魔改/js/data.js' or not isinstance(original.get('entries'), list):
        raise ValueError('引擎古例导出结构/固定来源不符')
    source_hash = original['source']['sha256']
    engine_data = path_in_root(root, '排盘工具魔改/js/data.js').read_bytes()
    manifest = json.loads(path_in_root(root, 'tools/liuren-direct/legacy-engine-manifest.json').read_text(encoding='utf-8-sig'))
    declared = next((x['sha256'] for x in manifest['files'] if x['path'] == 'js/data.js'), None)
    if sha(engine_data) != source_hash or declared != source_hash:
        raise ValueError('引擎古例参考源与当前引擎指纹不一致')
    markdown_bytes = path_in_root(root, ENGINE_REFERENCE_MD).read_bytes()
    markdown = markdown_bytes.decode('utf-8-sig')
    blocks = re.findall(r'^```json\n(\{[\s\S]*?\n\})\n```\s*$', markdown, re.M)
    headings = re.findall(r'^## ENGINE-ANCIENT-(\d+)\s*$', markdown, re.M)
    if source_hash not in markdown or len(blocks) != len(original['entries']) or headings != [f'{i + 1:04}' for i in range(len(blocks))]:
        raise ValueError('引擎古例全文覆盖/顺序或来源链不一致')
    if any(json.loads(block) != entry for block, entry in zip(blocks, original['entries'])):
        raise ValueError('引擎古例全文对象已被改写，须重做导出核对')
    return {'source_sha256': source_hash, 'export_sha256': sha(original_bytes),
            'markdown_sha256': sha(markdown_bytes), 'count': len(blocks), 'roundtrip_equal': True}


def decode(data):
    if data.startswith((b'\xff\xfe', b'\xfe\xff')):
        return data.decode('utf-16')
    try:
        return data.decode('utf-8-sig')
    except UnicodeDecodeError:
        return data.decode('gb18030')


def atomic_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as out:
            json.dump(value, out, ensure_ascii=False, indent=2)
            out.write('\n')
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def read_json(root, relative, default=None):
    path = path_in_root(root, relative)
    if not path.exists() and default is not None:
        return default
    return json.loads(path.read_text(encoding='utf-8-sig'))


def output_path(record):
    return f"案例项目库/{record['category']}/case-book-{record['id']}.md"


def load_registry(root):
    records, issues = [], []
    for path in sorted((Path(root) / DIRECTORY).glob('*.json')):
        relative = path.relative_to(root).as_posix()
        try:
            values = read_json(root, relative)
            if not isinstance(values, list) or any(not isinstance(x, dict) for x in values):
                raise ValueError('登记文件须为对象数组')
            records.extend(dict(x, _registry_file=relative, _registry_index=i + 1)
                           for i, x in enumerate(values))
        except (ValueError, OSError) as error:
            issues.append({'registry_file': relative, 'error': str(error)})
    return records, issues


def rule_ids(root):
    result = set()
    for path in sorted((Path(root) / BASE / 'rules').glob('*.json')):
        try:
            values = read_json(root, path.relative_to(root).as_posix())
            if isinstance(values, list):
                result.update(x['id'] for x in values if isinstance(x, dict) and isinstance(x.get('id'), str))
        except (ValueError, OSError):
            continue
    return result


def image_dependencies(root, path, quote):
    """Inspect local image presence without fetching external resources or opening arbitrary files."""
    targets = re.findall(r'<img\b[^>]*\bsrc\s*=\s*["\']([^"\']+)["\']', quote, re.I)
    targets += re.findall(r'!\[[^\]]*\]\(<?([^\s)>]+)>?(?:\s+["\'][^)]*)?\)', quote)
    result = []
    for value in dict.fromkeys(targets):
        if value.startswith('data:'):
            result.append({'reference': value[:64], 'state': 'embedded_in_source'})
        elif re.match(r'^(?:https?:)?//', value, re.I):
            result.append({'reference': value, 'state': 'external_unverified'})
        else:
            try:
                relative = (PurePosixPath(path).parent / unquote(value.split('#', 1)[0].split('?', 1)[0])).as_posix()
                # Resolve safe relative image paths, including legitimate parent assets paths.
                target = (Path(root) / relative).resolve()
                if not target.is_relative_to(Path(root).resolve()):
                    raise ValueError('图引用越出项目')
                relative = target.relative_to(Path(root).resolve()).as_posix()
                if not relative.startswith(('书籍库/', '课程写作/整理本/毕法赋全解/')):
                    raise ValueError('图引用越出批准资料目录')
                target = path_in_root(root, relative)
                if target.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg', '.bmp'}:
                    raise ValueError('图引用后缀不在图片白名单')
                result.append({'reference': value, 'path': relative,
                               'state': 'present' if target.is_file() else 'missing'})
            except (ValueError, OSError) as error:
                result.append({'reference': value, 'state': 'blocked', 'error': str(error)})
    return result


def verify_reconstruction_artifact(root, link, case_id, review):
    verifier = Path(__file__).with_name('liuren_book_reconstruction_verify.mjs')
    node = shutil.which('node')
    if not node:
        raise ValueError('只读复原核验需要既有Node运行时')
    process = subprocess.run([node, str(verifier)], input=json.dumps(
        {'root': str(Path(root).resolve()), 'link': link, 'case_id': case_id, 'review': review}, ensure_ascii=False),
        text=True, encoding='utf-8', capture_output=True, timeout=30)
    try:
        value = json.loads(process.stdout)
    except ValueError as error:
        raise ValueError('只读复原核验器未返回JSON') from error
    if process.returncode or not value.get('ok'):
        raise ValueError('只读复原核验失败:' + str(value.get('error', process.stderr[:200])))
    return value


def reconstruction_links(root, record, verifier=None):
    """Keep derived engine evidence separate from original-source quotations."""
    links = record.get('reconstruction_refs', [])
    if not isinstance(links, list):
        raise ValueError('reconstruction_refs须为数组')
    checked = []
    for link in links:
        if not isinstance(link, dict) or not re.fullmatch(r'RC26-[A-Za-z0-9-]{1,58}', link.get('id', '')):
            raise ValueError('复原链接ID无效')
        expected_path = f"output/liuren-book-cases-20261102/reconstructions/{link['id']}.json"
        if link.get('result_path') != expected_path:
            raise ValueError('复原结果须在固定ID路径')
        data = path_in_root(root, expected_path).read_bytes()
        if sha(data) != link.get('result_sha256'):
            raise ValueError('复原结果hash变化')
        result = json.loads(data.decode('utf-8-sig'))
        if result.get('schema') != 'liuren-book-reconstruction-result-v1' or result.get('id') != link['id'] or result.get('case_id') != record.get('id'):
            raise ValueError('复原结果schema/案例身份不符')
        if link.get('review_state') not in ('pending', 'source_checked') or not isinstance(link.get('note'), str) or not link['note'].strip():
            raise ValueError('复原链接须保留复核状态和身份说明')
        if link['review_state'] == 'source_checked':
            review_path = link.get('review_path')
            if not isinstance(review_path, str) or not review_path.startswith('output/liuren-book-cases-20261102/') or not review_path.endswith('.json'):
                raise ValueError('复原复核须为本轮专用output内JSON')
            review_bytes = path_in_root(root, review_path).read_bytes()
            if sha(review_bytes) != link.get('review_sha256'):
                raise ValueError('复原复核hash变化')
            review = json.loads(review_bytes.decode('utf-8-sig'))
            reviews = review.get('reviews', [review]) if isinstance(review, dict) else []
            matching = [x for x in reviews if isinstance(x, dict)
                    and x.get('case_id') == record.get('id') and x.get('result_id') == link['id']
                    and x.get('semantic_review_state') == 'source_checked'
                    and x.get('result_path') == expected_path and x.get('result_sha256') == link['result_sha256']] if isinstance(reviews, list) else []
            if len(matching) != 1:
                raise ValueError('复核JSON没有该案例/结果/hash的source_checked声明')
            verified = (verifier or verify_reconstruction_artifact)(root, link, record['id'], matching[0])
            checked.append(dict(link, _verified=verified))
        else:
            checked.append(dict(link))
    return checked


def validated_cases(root=ROOT):
    root = Path(root).resolve()
    records, load_issues = load_registry(root)
    counts = Counter(x.get('id') for x in records if isinstance(x.get('id'), str))
    known = {x['id'] for x in records if isinstance(x.get('id'), str)} | {
        x['source_case_identity'] for x in records if isinstance(x.get('source_case_identity'), str)}
    known_rules = rule_ids(root)
    checks, cache, derived = [], {}, {}
    pending = []
    def defer_reconstruction(root, link, case_id, review):
        result = {}
        pending.append((dict(root=str(root),link=link,case_id=case_id,review=review),result))
        return result
    for record in records:
        errors, warnings, dependencies = [], [], []
        rid = record.get('id') if isinstance(record.get('id'), str) else None
        match = ID_RE.fullmatch(rid or '')
        if record.get('schema') != 'liuren-book-case-v1' or not match:
            errors.append('schema或案例ID无效')
        if rid and counts[rid] != 1:
            errors.append('案例ID重复')
        for key in ('title', 'book_title', 'category', 'source_case_identity', 'boundary_note', 'question'):
            if not isinstance(record.get(key), str) or not record[key].strip():
                errors.append('必需非空文本:' + key)
        for key in ('authors', 'missing_fields', 'method_rule_ids', 'same_event_ids', 'notes'):
            if not isinstance(record.get(key), list) or any(not isinstance(x, str) or not x.strip() for x in record[key]):
                errors.append('必需文本数组:' + key)
        if isinstance(record.get('authors'), list) and not record['authors']:
            errors.append('作者须照原载，未知写未知')
        if record.get('category') not in tuple(CATEGORIES):
            errors.append('占类不在常规10类及批准专类安全白名单')
        if record.get('review_state') not in ('pending', 'source_checked'):
            errors.append('review_state无效')
        if record.get('completeness') not in ('complete', 'fragment', 'pending'):
            errors.append('completeness无效')
        if record.get('feedback_status') not in tuple(FEEDBACK):
            errors.append('反馈身份无效；不自动推定验')
        refs = record.get('source_refs')
        if not isinstance(refs, list) or not refs:
            errors.append('source_refs须为非空连续证据数组')
            refs = []
        for ref in refs:
            try:
                if not isinstance(ref, dict):
                    raise ValueError('source_ref须为对象')
                path = ref['path']
                if path not in cache:
                    cache[path] = source_path(root, path).read_bytes()
                data = cache[path]
                if path not in derived:
                    derived[path] = (decode(data).splitlines(), sha(data))
                lines, source_digest = derived[path]
                a, b = ref['line_start'], ref['line_end']
                if type(a) is not int or type(b) is not int or not (1 <= a <= b <= len(lines)):
                    raise ValueError('行号越界')
                if ref.get('sha256') != source_digest:
                    errors.append('source_hash_changed:' + path)
                if ref.get('quote') != '\n'.join(lines[a - 1:b]):
                    errors.append('quote_mismatch_or_noncontinuous:' + path)
                if ref.get('role') not in tuple(ROLES):
                    errors.append('source_ref角色须保留原文身份')
                dependencies.extend(image_dependencies(root, path, ref.get('quote', '')))
            except (ValueError, OSError, KeyError, TypeError, UnicodeError) as error:
                errors.append('证据:' + str(error))
        identity = IDENTITY_RE.fullmatch(record.get('source_case_identity', '') if isinstance(record.get('source_case_identity'), str) else '')
        first = refs[0] if refs and isinstance(refs[0], dict) else {}
        if not identity or not first or (identity[1], int(identity[2]), int(identity[3])) != (
                first.get('path'), first.get('line_start'), first.get('line_end')):
            errors.append('原书身份须精确等于首source_ref主案完整范围')
        elif match and identity[1] not in ({BOOKS['BIFA'], BIFA_TRANSCRIPT_SOURCE}
                                         if match[1] == 'BIFA' else {BOOKS[match[1]]}):
            errors.append('案例ID书码与主原书不符')
        additional = record.get('additional_source_case_identities', [])
        if not isinstance(additional, list) or any(not isinstance(x, str) for x in additional):
            errors.append('additional_source_case_identities须为精确身份文本数组')
            additional = []
        declared_event_refs = {f"book:{r.get('path')}:L{r.get('line_start')}-L{r.get('line_end')}"
                               for r in refs if isinstance(r, dict) and r.get('same_event') is not False
                               and r.get('dependency_type') not in ('borrowed_chart', 'borrowed_context')}
        if len(set(additional)) != len(additional) or any(not IDENTITY_RE.fullmatch(x) or x not in declared_event_refs for x in additional):
            errors.append('补充同案身份须精确绑定已附的非借用同案原文段，不由局部方法证据另造身份')
        if isinstance(record.get('method_rule_ids'), list):
            for value in record['method_rule_ids']:
                if not isinstance(value, str) or value not in known_rules:
                    errors.append('关联方法ID不存在:' + str(value))
        if isinstance(record.get('same_event_ids'), list):
            for value in record['same_event_ids']:
                if not isinstance(value, str) or value not in known:
                    errors.append('同源目标未登记:' + str(value))
        body = '\n'.join(r.get('quote', '') for r in refs if isinstance(r, dict) and isinstance(r.get('quote'), str))
        if record.get('completeness') == 'complete' and re.search(r'断语遗失|断[语辞]阙|关键盘图缺失|课盘遗失', body):
            errors.append('原文明示关键内容遗失，不得标complete')
        if record.get('completeness') == 'complete' and '课式同前' in body and len(refs) < 2:
            errors.append('课式同前未附必要承接原文')
        optional = record.get('noncritical_image_refs', [])
        if not isinstance(optional, list) or any(not isinstance(x, str) for x in optional):
            errors.append('noncritical_image_refs须为文本数组')
            optional = []
        unresolved = [d for d in dependencies if d['state'] in {'missing', 'blocked', 'external_unverified'}
                      and d['reference'] not in optional]
        if unresolved and record.get('completeness') == 'complete':
            errors.append('图依赖缺失/未核；关键性未声明，complete须先复核')
        elif unresolved:
            warnings.append('图依赖尚有缺口，保留残缺身份')
        chart = record.get('chart_fields', {})
        if not isinstance(chart, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in chart.items()):
            errors.append('chart_fields须为原载文本字段对象')
        elif any(re.sub(r'\s+', '', value) not in re.sub(r'\s+', '', body) for value in chart.values()):
            errors.append('chart_fields存在未能逐字定位于原文的值，禁止重推盘冒充原载')
        try:
            record['_reconstruction_links'] = reconstruction_links(root, record, defer_reconstruction)
        except (ValueError, OSError, KeyError, TypeError, UnicodeError, subprocess.SubprocessError) as error:
            errors.append('复原链接:' + str(error))
        checks.append({'id': rid, 'registry_file': record.get('_registry_file'),
                       'mechanical_state': 'blocked' if errors else 'pass', 'errors': errors,
                       'warnings': warnings, 'image_dependencies': dependencies,
                       'eligible_for_import': not errors and record.get('review_state') == 'source_checked'
                                              and record.get('completeness') == 'complete'})
    if pending:
        verifier = Path(__file__).with_name('liuren_book_reconstruction_verify.mjs')
        node = shutil.which('node')
        try:
            if not node: raise ValueError('只读复原核验需要既有Node运行时')
            process = subprocess.run([node,str(verifier)],input=json.dumps({'requests':[task for task,_ in pending]},ensure_ascii=False),
                text=True,encoding='utf-8',capture_output=True,timeout=30)
            batch = json.loads(process.stdout)
            results = batch.get('results', [])
            if process.returncode or len(results)!=len(pending): raise ValueError('批量只读复原核验响应不完整')
        except (OSError,ValueError,subprocess.TimeoutExpired) as error:
            results=[dict(ok=False,error=str(error)) for _ in pending]
        failures = {}
        for (task, dest), result in zip(pending,results):
            dest.update(result)
            if not result.get('ok'): failures.setdefault(task['case_id'],[]).append('只读复原核验失败:'+str(result.get('error')))
        for record, check in zip(records,checks):
            if record.get('id') in failures:
                check['errors'].extend(failures[record['id']])
                check.update(mechanical_state='blocked',eligible_for_import=False)
    valid = [r for r, c in zip(records, checks) if c['mechanical_state'] == 'pass']
    return {'records': records, 'valid_records': valid, 'checks': checks,
            'issues': load_issues + [c for c in checks if c['mechanical_state'] == 'blocked'],
            'summary': {'registered': len(records), 'mechanical_pass': len(valid),
                        'eligible_complete': sum(c['eligible_for_import'] for c in checks),
                        'fragment': sum(r.get('completeness') == 'fragment' for r in records),
                        'pending': sum(r.get('review_state') == 'pending' or r.get('completeness') == 'pending' for r in records),
                        'valid': not load_issues and len(valid) == len(records),
                        'semantic_identity': '负责人声明整案边界；机械核对不证明语义完整',
                        'independent_validation_count': 0, 'complete': False}}


def record_digest(record):
    return sha(json.dumps({k: v for k, v in record.items() if not k.startswith('_')},
                          ensure_ascii=False, sort_keys=True).encode('utf-8'))


def render(record):
    meta = {'schema': 'liuren-book-case-generated-v1', 'id': record['id'],
            'source_case_identity': record['source_case_identity'], 'registry_file': record['_registry_file'],
            'registry_sha256': record_digest(record)}
    fields = record.get('chart_fields', {})
    chart = ' | '.join(f'{k}={v}' for k, v in fields.items() if k in {'课体', '发用', '三传', '日干', '四柱', '类神', '年命'})
    feedback_label = {'原载反馈': '原载反馈（未独立核验）', '原载断语与结果混合': '原载断语与结果混合',
                      '未载明确反馈': '未载', '身份待核': '身份待核'}[record['feedback_status']]
    parts = [f"<!-- META: 占类={record['category']} | 编号={record['id']} | 来源ID={record['id']} | 反馈={feedback_label} | 经验状态=原载方法参照、非独立验证" + (' | ' + chart if chart else '') + ' -->',
             HEADER + json.dumps(meta, ensure_ascii=False, separators=(',', ':')) + ' -->',
             '# ' + record['title'], '',
             '本档为原书整案来源保存。生成时负责人声明source_checked/complete；当前有效性须由原书、登记与生成hash重新校验。',
             '反馈身份：' + record['feedback_status'] + '。原载称验不自动改写为独立验证。', '',
             '## 问题', '【本轮忠实概括，非原文新事实】' + record['question'], '',
             '## 来源与边界', '书名：' + record['book_title'],
             '原书单案身份：' + record['source_case_identity'],
             '署名（按原载）：' + '、'.join(record['authors']),
             '完整边界声明：' + record['boundary_note'], '', '## 原载全文']
    for number, ref in enumerate(record['source_refs'], 1):
        quote = ref['quote']
        # Fence length must exceed every backtick run in the original, preserving it verbatim.
        width = max([3] + [len(x) + 1 for x in re.findall(r'`+', quote)])
        fence = '`' * width
        parts += ['', f"### 原文段{number} · {ref['role']}",
                  f"来源：{ref['path']} L{ref['line_start']}-L{ref['line_end']}；SHA256 {ref['sha256']}",
                  fence + 'text', quote, fence]
    parts += ['', '## 缺项与图像依赖', '\n'.join('- ' + x for x in record['missing_fields']) or '原登记未列关键缺项；仍不等于逐项盘式核算通过。',
              '课盘状态：' + record.get('chart_status', '仅保留原载，未重新推盘'), '',
              '## 同源与关联方法', '已确认同源：' + ('、'.join(record['same_event_ids']) or '未登记；不强行合并跨书事件'),
              '关联方法：' + ('、'.join(record['method_rule_ids']) or '本案暂未另产方法卡'), '',
              '## 编者与本轮说明', '\n'.join('- ' + x for x in record['notes']) or '按原载保存；不补写反馈。', '']
    classification = {k: record[k] for k in ('subcategories', 'taxonomy', 'judgment_logic', 'logic_tags', 'logic_stages', 'method_coverage', 'chart_consistency', 'text_consistency', 'completeness_review') if k in record}
    if classification:
        parts += ['## 分类交叉标签（登记原样，非自动语义归并）',
                  '```json', json.dumps(classification, ensure_ascii=False, indent=2), '```', '']
    if record.get('reconstruction_refs'):
        parts += ['## 引擎衍生复原与人工复核（不是原书原载）',
                  '只保存可核链接；原盘残缺、设置约定及冲突以复核说明为准，不自动升级完整性或断验。',
                  '```json', json.dumps(record['reconstruction_refs'], ensure_ascii=False, indent=2), '```', '']
        for link in record.get('_reconstruction_links', []):
            verified = link.get('_verified', {})
            for number, group in enumerate(verified.get('groups', []), 1):
                parts += [f"### {link['id']} 完整等价结构组{number}",
                          '原图残损身份保留。下列是现有引擎完整facts的展示代表，不是选择唯一设置；等价比较只排除明列设置标签。',
                          '全部候选、原始归档和未核设置见上列结果/复核链接；本附录不证明现实断验。',
                          '```json', json.dumps(group, ensure_ascii=False, indent=2), '```', '']
    return '\n'.join(parts).encode('utf-8')


def import_cases(root=ROOT):
    root = Path(root).resolve()
    validated = validated_cases(root)
    previous = read_json(root, STATE, {'imports': {}})
    if not isinstance(previous, dict) or not isinstance(previous.get('imports'), dict):
        raise ValueError('旧导入清单格式无效，禁止覆盖产物')
    if any(not isinstance(x, dict) for x in previous['imports'].values()):
        raise ValueError('旧导入清单条目格式无效，禁止覆盖产物')
    tracked = previous['imports']
    current, actions = {}, []
    for record, check in zip(validated['records'], validated['checks']):
        rid = check['id']
        if not isinstance(rid, str) or not ID_RE.fullmatch(rid):
            continue
        old = tracked.get(rid, {})
        if not check['eligible_for_import']:
            if old:
                current[rid] = dict(old, state='blocked', errors=check['errors'] or ['登记未同时complete/source_checked'])
            actions.append({'id': rid, 'action': 'not_imported', 'reason': check['errors'] or ['残缺/待核登记保留，不生成案例']})
            continue
        relative = output_path(record)
        target = path_in_root(root, relative)
        expected = render(record)
        if old.get('path') and old['path'] != relative and path_in_root(root, old['path']).exists():
            current[rid] = dict(old, state='blocked', errors=['分类改变，旧产物仍在；需显式迁移，工具不静默复制'])
            actions.append({'id': rid, 'action': 'conflict', 'reason': current[rid]['errors']})
            continue
        if target.exists():
            actual = target.read_bytes()
            if actual == expected:
                action = 'unchanged'
            elif old.get('generated_sha256') == sha(actual) and old.get('path') == relative:
                action = 'updated_managed'
            else:
                current[rid] = dict(old, path=relative, state='conflict', errors=['人工改动或未受管已有文件，禁止覆盖'])
                actions.append({'id': rid, 'action': 'conflict', 'reason': current[rid]['errors']})
                continue
        else:
            action = 'created'
        if action != 'unchanged':
            target.parent.mkdir(parents=True, exist_ok=True)
            fd, name = tempfile.mkstemp(prefix=target.name + '.', suffix='.tmp', dir=target.parent)
            try:
                with os.fdopen(fd, 'wb') as stream:
                    stream.write(expected)
                os.replace(name, target)
            finally:
                Path(name).unlink(missing_ok=True)
        current[rid] = {'path': relative, 'state': 'active', 'generated_sha256': sha(expected),
                        'registry_sha256': record_digest(record), 'source_case_identity': record['source_case_identity']}
        actions.append({'id': rid, 'action': action, 'path': relative})
    for rid, old in tracked.items():
        if rid not in current:
            current[rid] = dict(old, state='blocked', errors=['登记撤销/损坏；产物保留但检索排除'])
    state = {'schema': 'liuren-book-case-imports-v1', 'updated_at': datetime.now(timezone.utc).isoformat(),
             'imports': current}
    atomic_json(path_in_root(root, STATE), state)
    return {'actions': actions, 'summary': validated['summary'], 'issues': validated['issues'],
            'active': sum(x['state'] == 'active' for x in current.values()),
            'blocked_or_conflict': sum(x['state'] != 'active' for x in current.values())}


def artifact_status(root, relative, data, validated=None):
    """Read-only. Never trust a generated document's old source_checked header alone."""
    checked = validated or validated_cases(root)
    name = PurePosixPath(relative).name
    match = re.fullmatch(r'case-book-(BK26-(?:MODERN|ANCIENT|SHAO|BIFA)-\d{3,})\.md', name)
    if not match:
        return {'managed': False, 'eligible': True}
    rid = match[1]
    pairs = [(r, c) for r, c in zip(checked['records'], checked['checks']) if r.get('id') == rid]
    if len(pairs) != 1 or not pairs[0][1]['eligible_for_import']:
        return {'managed': True, 'eligible': False, 'id': rid, 'reason': '登记缺失、来源变化或完整性/审读未通过'}
    record, _ = pairs[0]
    if relative != output_path(record) or data != render(record):
        return {'managed': True, 'eligible': False, 'id': rid, 'reason': '产物/分类/登记不一致或存在人工改动；先复核，禁止冒充有效整案'}
    return {'managed': True, 'eligible': True, 'id': rid, 'record': record,
            'source_case_identity': record['source_case_identity']}


def provenance(root, checked=None):
    """Map precise source spans to events; a plain book path never identifies an event."""
    checked = checked or validated_cases(root)
    records = checked['valid_records']
    result = []
    for record in records:
        if record['review_state'] != 'source_checked':
            continue
        keys = {record['id'], record['source_case_identity'], output_path(record), *record['same_event_ids']}
        ranges, dependency_keys = [], set()
        for index, ref in enumerate(record['source_refs']):
            if ref['path'] in set(BOOKS.values()) | SUPPLEMENTS | {ENGINE_REFERENCE_MD}:
                span_id = f"book:{ref['path']}:L{ref['line_start']}-L{ref['line_end']}"
                borrowed = index > 0 and (ref.get('same_event') is False or ref.get('dependency_type') in {'borrowed_chart', 'borrowed_context'})
                if borrowed:
                    dependency_keys.add(span_id)
                else:
                    ranges.append((ref['path'], ref['line_start'], ref['line_end'], ref['quote'].splitlines()))
                    keys.add(span_id)
        result.append({'id': record['id'], 'keys': keys, 'ranges': ranges, 'dependency_keys': dependency_keys})
    return result


def compact_provenance(mappings):
    return [{'id': m['id'], 'keys': sorted(m['keys']),
             'dependency_keys': sorted(m.get('dependency_keys', [])),
             'ranges': [[path, a, b, ['x' if line.strip() else '' for line in lines]]
                        for path, a, b, lines in m['ranges']]} for m in mappings]


def filter_retrieval_sources(root, files):
    candidates = {p: data for p, data in files.items()
                  if PurePosixPath(p).name.startswith('case-book-') or
                  any(line.startswith(HEADER.encode('utf-8')) for line in data.splitlines()[:2])}
    if not candidates:
        return files, {'active': 0, 'issues': []}, {}
    checked = validated_cases(root)
    filtered, metadata = dict(files), {}
    issues = list(checked['issues'])
    for relative, data in candidates.items():
        status = artifact_status(root, relative, data, checked)
        if not status['managed'] or not status['eligible']:
            filtered.pop(relative, None)
            issues.append({'source': relative, 'error': status.get('reason', '生成标记与案例文件名不一致')})
        else:
            metadata[relative] = status['record']
    return filtered, {'active': len(metadata), 'issues': issues,
                     'validation_identity': '按当前登记、原源与产物全文核对；失效整案不参与检索'}, metadata


def expand_identities(values, mappings, *, include_dependencies=False):
    # Same fixed-point closure, but visit each new identity/mapping only once.
    # No cache crosses calls: every caller still builds maps from current sources.
    result = set(values)
    by_key, ranges = {}, {}
    for number, mapping in enumerate(mappings):
        for key in mapping['keys']:
            by_key.setdefault(key, set()).add(number)
        for source, a, b, lines in mapping['ranges']:
            ranges.setdefault(source, []).append((number, a, b, lines))
    pending, expanded = list(result), set()
    while pending:
        value = pending.pop()
        matches = set(by_key.get(value, ()))
        parsed = IDENTITY_RE.fullmatch(value) if isinstance(value, str) else None
        if parsed:
            source, start, end = parsed[1], int(parsed[2]), int(parsed[3])
            for number, a, b, lines in ranges.get(source, ()):
                left, right = max(a, start), min(b, end)
                if left <= right and any(x.strip() for x in lines[left-a:right-a+1]):
                    matches.add(number)
        for number in matches - expanded:
            expanded.add(number)
            mapping = mappings[number]
            additions = set(mapping['keys'])
            if include_dependencies:
                additions.update(mapping.get('dependency_keys', []))
            fresh = additions-result
            result.update(fresh)
            pending.extend(fresh)
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['validate', 'import', 'status'])
    args = parser.parse_args(argv)
    try:
        if args.command == 'import':
            result = import_cases(ROOT)
            valid = result['summary']['valid'] and not result['blocked_or_conflict']
        else:
            result = validated_cases(ROOT)
            valid = result['summary']['valid']
            result = {'summary': result['summary'], 'checks': result['checks'], 'issues': result['issues']}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if valid else 2
    except (ValueError, OSError) as error:
        print(json.dumps({'error': str(error), 'complete': False}, ensure_ascii=False))
        return 2


if __name__ == '__main__':
    sys.exit(main())
