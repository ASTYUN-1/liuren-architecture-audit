"""Build an immutable, hash-bound website knowledge snapshot; never edit source material.

Usage: python -X utf8 tools/build-knowledge-release.py --output <NEW directory>
The destination must not exist. No credentials or customer exports are copied.
"""
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
EXPANDED = ['sanbu-duanke', 'leishen-keti', 'renji-guanxi', 'yingpin-gongzuo', 'shengzhi-jiaxin', 'xiongsha-suduan']
SKILLS = set(['daliuren', 'sanbu-duanke', 'leishen-keti', 'kongwang-bianzhi', 'shensha-panduan', 'youlu-lilun', 'keti-qishi', 'jixiong-tiaozhi', 'yingqi-panduan', 'liuren-cases', 'lianai-panduan', 'cailu-panduan', 'yingpin-gongzuo', 'shengzhi-jiaxin', 'shiyun-zonghe', 'renji-guanxi', 'xiongsha-suduan', 'zhinan-zhanbing', 'yunchan-panduan'])
REVIEW = '''

## 网站扩展适用边界（本次发布复核）

以上问答录扩展保留作者原说、反例和勘误，不把个案概括为无条件法则。课体优先仅用于已确认其适用条件的特殊课格；不得取代主 skill 按具体占类选择类神/课体主线及冲突核查。必须核对固定盘的实际课格、旺衰、空墓、阴神和反证，不能仅见一象定论。古例来意推断不代替网站用户明确的问题，不能擅自断定无关的隐私或事件。生死、病因、脏腑与医药是古籍术语和历史材料，不能当作医学诊断、死亡预测或治疗指令；对客只能说明不确定性和就医建议。历史“必然”等措辞不是对当前用户结果的保证。网站适配规则与当前主 skill 优先，原文存疑和版本差异须明确记录。
'''

def sha(data):
    return hashlib.sha256(data).hexdigest()

def meta(line):
    m = re.match(r'^<!-- META:(.*?)-->', line)
    return dict((p.split('=', 1)[0].strip(), p.split('=', 1)[1].strip()) for p in m[1].split('|') if '=' in p) if m else {}

def feedback(value):
    s = value.replace('**', '').strip()
    if s in ['验', '✅', '已验证', '应验']: return 'verified'
    if s.startswith(('部分验', '部分应验')): return 'partial'
    if s in ['不验', '❌', '未应验']: return 'disproved'
    return 'unknown'

def decode(data):
    try: return data.decode('utf-8-sig'), 'utf-8-sig' if data.startswith(b'\xef\xbb\xbf') else 'utf-8'
    except UnicodeDecodeError: return data.decode('gb18030'), 'gb18030'

def sections(text, limit=6000):
    # Prefer line boundaries, but retain every code point even in huge single lines.
    part, size = '', 0
    for line in text.splitlines(keepends=True):
        if part and size + len(line.encode('utf-8')) > limit:
            yield part
            part, size = '', 0
        for c in line:
            n = len(c.encode('utf-8'))
            if size + n > limit:
                yield part
                part, size = '', 0
            part += c
            size += n
    if part: yield part

def build(root, output, current_workflow=False, stage1_source=None, liuren_runtime=None):
    if liuren_runtime and not current_workflow:
        raise ValueError('liuren-runtime requires explicit --current-workflow')
    if liuren_runtime:
        from liuren_runtime import verify
        verify(Path(liuren_runtime))
    output.mkdir(parents=True, exist_ok=False)
    manifest = {'schemaVersion': 1, 'policyVersion': 'liuren-specific-event-20261017', 'documents': [], 'files': {}, 'books': [], 'excluded': [], 'skillReview': []}
    def copy(p):
        rel = p.relative_to(root)
        dest = output / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(p, dest)
        return rel.as_posix()
    def exclude(p, reason):
        manifest['excluded'].append({'source': p.relative_to(root).as_posix(), 'reason': reason, 'hash': sha(p.read_bytes())})
    # Retain the engine and public-output policy used by the website.
    for directory in ['排盘工具魔改/js', 'website-skills', '.opencode/skills']:
        for p in sorted((root / directory).rglob('*')):
            if directory == '排盘工具魔改/js' and p.name not in ['lunar.js', 'data.js', 'api.js', 'guize.js', 'paipan.js']: continue
            if p.is_file() and not p.is_symlink(): copy(p)
    for name in ([] if current_workflow else EXPANDED):
        active = root / '.opencode/skills' / name / 'SKILL.md'
        source = root / 'books/beihai-xianren' / name / 'SKILL.md'
        a, b = active.read_text('utf-8-sig').splitlines(), source.read_text('utf-8-sig').splitlines()
        # Abort on future source deletions or substantive replacement, not silently overwrite.
        for tag, i, j, k, l in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if tag == 'delete': raise ValueError(f'unreviewed deletion: {name}:{i}')
            if tag == 'replace' and not all(x.startswith(('source_book:', '  用户', '- **composes-with**:')) for x in a[i:j]):
                raise ValueError(f'unreviewed replacement: {name}:{i}')
        deployed = output / active.relative_to(root)
        deployed.write_bytes(source.read_bytes() + REVIEW.encode('utf-8'))
        manifest['skillReview'].append({'skill': name, 'activeHash': sha(active.read_bytes()), 'sourceHash': sha(source.read_bytes()), 'deployedHash': sha(deployed.read_bytes()), 'decision': 'reviewed expansion with explicit applicability boundary; originals retained locally'})
    manifest['skillReview'].append({'skill': 'daliuren', 'activeHash': sha((root / '.opencode/skills/daliuren/SKILL.md').read_bytes()), 'decision': 'keep newer active rules unchanged'})
    # Index is consumed at build time and pinned together with each source file.
    for directory in ['案例项目库', '经验日志']:
        index = root / directory / '_metadata_index.md'
        copy(index)
        rows = [meta(s) for s in index.read_text('utf-8-sig').splitlines() if s.startswith('<!-- META:')]
        matched = set()
        for p in sorted((root / directory).rglob('*.md')):
            if p.name.startswith('_') or p.name == 'README.md': continue
            if directory == '经验日志' and any(x in p.name for x in ['推命', '终身', '八字']):
                exclude(p, 'life-reading/bazi research outside current event product'); continue
            raw = p.read_bytes()
            text, encoding = decode(raw)
            m = meta(text.splitlines()[0] if text else '')
            if not m and p.name != '提取-大六壬应期断诀窍.md' and not (current_workflow and directory == '经验日志'):
                exclude(p, 'not an approved knowledge entry'); continue
            candidates = [r for r in rows if (r.get('文件') == p.name if directory == '经验日志' else r.get('占类') == m.get('占类') and (p.stem == r.get('编号') or p.stem.startswith(r.get('编号', '\0') + '-')))]
            if len(candidates) > 1: raise ValueError(f'ambiguous index: {p}')
            idx = candidates[0] if candidates else {}
            if idx: matched.add(rows.index(idx))
            effective, origins, conflicts = dict(m), {k: 'source' for k in m}, []
            for k, v in idx.items():
                if k in ['文件', '编号'] or not v: continue
                if not effective.get(k) or effective[k] in ['未载', '-', '无记录']:
                    effective[k], origins[k] = v, 'index'
                elif effective[k] != v and not (k == '反馈' and feedback(effective[k]) == feedback(v)):
                    conflicts.append({'field': k, 'source': effective[k], 'index': v})
            kind = 'case' if directory == '案例项目库' and m.get('占类') != '古籍注解' else 'experience' if effective.get('占类') and effective['占类'] != '古籍注解' else 'reference'
            source = copy(p)
            doc = {'id': ('case:' if kind != 'reference' else 'reference:') + sha(source.encode())[:20], 'file': source, 'source': source, 'kind': kind, 'title': p.stem, 'meta': effective, 'metadataOrigins': origins, 'metadataConflicts': conflicts,
                   'provenance': {'sourceHash': sha(raw), 'encoding': encoding, 'indexSource': index.relative_to(root).as_posix(), 'indexHash': sha(index.read_bytes()), 'indexed': bool(idx), 'feedbackRaw': m.get('反馈', ''), 'indexFeedbackRaw': idx.get('反馈', ''), 'feedback': feedback(effective.get('反馈', ''))}}
            if kind == 'reference':
                parts = list(sections(text))
                assert ''.join(parts) == text
                offset, line = 0, 1
                for i, part in enumerate(parts):
                    file = f'_knowledge_sections/{sha(source.encode())[:20]}-{i+1:04}.md'
                    dest = output / file
                    dest.parent.mkdir(exist_ok=True)
                    dest.write_bytes(part.encode('utf-8'))
                    count = len(part.encode('utf-8'))
                    manifest['documents'].append({**doc, 'id': doc['id']+f':{i+1}', 'file': file, 'title': f'{p.stem} / {i+1}/{len(parts)}', 'provenance': {**doc['provenance'], 'decodedHash': sha(text.encode('utf-8')), 'section': i+1, 'sections': len(parts), 'decodedByteStart': offset, 'decodedByteEnd': offset+count, 'lineStart': line, 'lineEnd': line+part.count('\n')}})
                    offset += count
                    line += part.count('\n')
            else:
                manifest['documents'].append(doc)
        manifest.setdefault('indexes', []).append({'source': index.relative_to(root).as_posix(), 'rows': len(rows), 'matched': len(matched), 'unmatchedRows': [r for n, r in enumerate(rows) if n not in matched]})
    seen = {}
    for p in sorted((root / '书籍库').rglob('*')):
        if not p.is_file(): continue
        rel = p.relative_to(root).as_posix()
        reason = None
        if p.parts[len(root.parts) + 1] in ['八字书籍', '六壬命法'] or any(x in p.name for x in ['论命', '金口诀']): reason = 'outside current liuren specific-event method'
        elif p.name.startswith('_') or p.name == 'README.md' or any(x in p.name for x in ['修订报告', '任务书', '新建 文本']): reason = 'index, draft or review task; not source authority'
        raw = p.read_bytes()
        if not reason and sha(raw) in seen: reason = 'exact duplicate of ' + seen[sha(raw)]
        if reason: exclude(p, reason); continue
        seen[sha(raw)] = rel
        text, encoding = decode(raw)
        copy(p)
        parts = list(sections(text))
        assert ''.join(parts) == text and '\ufffd' not in text
        source_id, offset, line = sha(rel.encode())[:20], 0, 1
        for i, part in enumerate(parts):
            file = f'_knowledge_sections/{source_id}-{i+1:04}.md'
            dest = output / file
            dest.parent.mkdir(exist_ok=True)
            dest.write_bytes(part.encode('utf-8'))
            count = len(part.encode('utf-8'))
            manifest['documents'].append({'id': f'reference:{source_id}:{i+1}', 'file': file, 'source': rel, 'kind': 'reference', 'title': f'{p.stem} / {i+1}/{len(parts)}', 'meta': {},
                'provenance': {'sourceHash': sha(raw), 'encoding': encoding, 'decodedHash': sha(text.encode('utf-8')), 'section': i+1, 'sections': len(parts), 'decodedByteStart': offset, 'decodedByteEnd': offset+count, 'lineStart': line, 'lineEnd': line+part.count('\n'), 'feedback': 'source-text'}})
            offset += count
            line += part.count('\n')
        manifest['books'].append({'source': rel, 'hash': sha(raw), 'encoding': encoding, 'decodedHash': sha(text.encode('utf-8')), 'decodedBytes': offset, 'sections': len(parts)})
    if current_workflow:
        import case_retrieval
        import experience_retrieval
        case_index = case_retrieval.build_index(root)
        exp_index = experience_retrieval.build_index(root)
        # Keep the whole curated collection as private source material, but only
        # specific-event Liuren entries participate in this website's retrieval.
        for p in sorted((root / '经验日志').rglob('*.md')):
            if not p.is_symlink(): copy(p)
        all_exp_status = exp_index['status']
        approved = {d['source'] for d in manifest['documents']}
        exp_index['entries'] = [e for e in exp_index['entries'] if e['source'] in approved]
        active_ids = {e['id'] for e in exp_index['entries']}
        exp_index['relations'] = [r for r in exp_index['relations'] if all(m in active_ids for m in r['members'])]
        exp_index['status'] = {**all_exp_status, 'archived_entries': all_exp_status['entries'],
            'source_files': len({e['source'] for e in exp_index['entries']}),
            'archived_source_files': all_exp_status['source_files'],
            'entries': len(exp_index['entries']),
            'curated_entries': sum(not e['id'].startswith('U-') for e in exp_index['entries']),
            'unreviewed_fragments': sum(e['id'].startswith('U-') for e in exp_index['entries']),
            'scope': 'specific-event Liuren; Bazi/life-reading research archived separately'}
        for source in ['tools/case_retrieval.py', 'tools/experience_retrieval.py', 'tools/website-retrieval.py',
                       'docs/经验库梳理/20261019/data/catalog.json',
                       'docs/判断流程优化/20261019/方法观察.json', 'docs/判断流程优化/20261019/开发样本.json']:
            copy(root / source)
        exp_ids = {}
        for e in exp_index['entries']:
            raw = (root / e['source']).read_bytes()
            lines = raw.decode('utf-8-sig').splitlines()
            assert '\n'.join(lines[e['line_start']-1:e['line_end']]) == e['source_excerpt'], e['id']
            start, end = max(0, e['line_start']-9), min(len(lines), e['line_end']+8)
            text = '\n'.join(lines[start:end])
            identity = sha(('experience-entry:' + e['id']).encode())[:20]
            file = f'_retrieval_entries/{identity}.md'
            (output / file).parent.mkdir(exist_ok=True)
            (output / file).write_bytes(text.encode())
            doc_id = 'reference:' + identity
            exp_ids[e['id']] = doc_id
            manifest['documents'].append(dict(id=doc_id, file=file, source=e['source'], kind='reference',
                title=e['title'], meta={'经验条目': e['id'], '验证身份': e['verification']},
                provenance=dict(sourceHash=sha(raw), encoding='utf-8', feedback='unverified-experience',
                    lineStart=start+1, lineEnd=end)))
        for name, data in [('case-index.json', case_index), ('experience-index.json', exp_index)]:
            dest = output / '_retrieval' / name
            dest.parent.mkdir(exist_ok=True)
            dest.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        bindings = dict(case_ids={d['source']:d['id'] for d in manifest['documents'] if d['kind']=='case'},
                        experience_ids=exp_ids)
        (output / '_retrieval/bindings.json').write_text(json.dumps(bindings,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        manifest['retrieval'] = dict(schema='fine-grained-20261019', caseIndex='_retrieval/case-index.json',
            experienceIndex='_retrieval/experience-index.json', bindings='_retrieval/bindings.json',
            script='tools/website-retrieval.py', caseStatus=case_index['status'], experienceStatus=exp_index['status'],
            archivedExperienceStatus=all_exp_status)
        manifest['policyVersion'] = 'liuren-current-workflow-20261019'
        manifest['skillReview'] = [{'decision':'current project skill bytes preserved; website adapter supplies tool bindings'}]
        for relative in ['docs/初级案例整理/初级案例资料/anli001', 'docs/初级案例整理/初级案例资料/anli002',
                         'docs/初级案例整理/初级案例资料/qqwb20261019-有效201例-修订版',
                         'docs/初级案例整理/盘面资料/batch-20261018']:
            for p in sorted((root / relative).rglob('*')):
                if p.is_file() and not p.is_symlink(): copy(p)
        manifest['stage1Policy'] = 'Private archive only; not indexed as formal cases or verified rules.'
        if stage1_source:
            base = Path(stage1_source).resolve()
            count = 0
            for name in ['cases', 'charts', 'source', 'tables', 'ledger.json', 'report.md', 'review_queue.json']:
                origin = base / name
                for p in ([origin] if origin.is_file() else sorted(origin.rglob('*'))):
                    if p.is_file() and not p.is_symlink():
                        dest = output / 'docs/初级案例整理/初级案例资料/qqwb20261018-v2' / p.relative_to(base)
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copyfile(p, dest)
                        count += 1
            manifest['additionalStage1'] = {'batch':'qqwb20261018-v2', 'files':count,
                'caseFiles':len(list((base/'cases').glob('*.md'))), 'indexedAsFormal':False}
    if liuren_runtime:
        candidate = Path(liuren_runtime).resolve()
        runtime = json.loads((candidate / 'liuren-runtime.json').read_text('utf-8'))
        for name in [*runtime['files'], 'liuren-runtime.json']:
            dest = output / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(candidate / name, dest)
        manifest['liurenRuntime'] = {'protocol': 'liuren-v2', 'version': runtime['version'], 'mode': runtime['mode'], 'activation': 'explicit-constructor-only'}
    for p in sorted(output.rglob('*')):
        if p.is_file(): manifest['files'][p.relative_to(output).as_posix()] = sha(p.read_bytes())
    for d in manifest['documents']: d['hash'] = manifest['files'][d['file']]
    data = (json.dumps(manifest, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    (output / 'knowledge-manifest.json').write_bytes(data)
    print(json.dumps({'manifestHash': sha(data), 'files': len(manifest['files']), 'documents': len(manifest['documents']), 'books': len(manifest['books']), 'excluded': len(manifest['excluded']), 'kinds': {k: sum(d['kind']==k for d in manifest['documents']) for k in ['case', 'experience', 'reference']}, 'metadataConflicts': sum(bool(d.get('metadataConflicts')) for d in manifest['documents']), 'indexes': [{k:v for k,v in x.items() if k!='unmatchedRows'} for x in manifest['indexes']]}, ensure_ascii=False))
    return manifest

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--current-workflow', action='store_true', help='Preserve current skills and publish frozen fine-grained retrieval plus private stage-1 archive')
    parser.add_argument('--stage1-source', type=Path, help='Optional existing QQ stage1_v2 folder to preserve as a private archive')
    parser.add_argument('--liuren-runtime', type=Path, help='Verified local candidate; requires --current-workflow; default protocol remains legacy')
    args = parser.parse_args()
    build(ROOT, args.output.resolve(), current_workflow=args.current_workflow, stage1_source=args.stage1_source, liuren_runtime=args.liuren_runtime)
