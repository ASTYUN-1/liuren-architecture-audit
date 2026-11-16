"""Read-only checks for the proposal review; writes evidence only beside this file.

Does not change skills, pointers, knowledge cards, source books, or frozen packages.
Does not read reserved answer files or call a model.
"""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import hashlib
import importlib.util
import json
import sys

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(ROOT / 'tools'))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def rel(path):
    return path.relative_to(ROOT).as_posix()


def main():
    active = load(ROOT / '.opencode/liuren-active.json')
    runtime = ROOT / active['runtime']
    manifest = load(runtime / 'manifest.json')
    prior = load(OUT / 'module-map.json')
    spec = importlib.util.spec_from_file_location('proposal_method_loader', ROOT / 'tools/load-liuren-methods.py')
    loader = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loader)
    resolved_runtime, resolved_manifest = loader.active(ROOT)
    actual = []
    for module_id, item in manifest['modules'].items():
        path, body, file_hash = loader.content(resolved_runtime, resolved_manifest, module_id)
        actual.append(dict(id=module_id, registered_file=rel(runtime / item['file']),
                           effective_file=rel(path), sha256=file_hash,
                           bytes=len(body.encode('utf-8'))))

    import liuren_knowledge_workbench as wb
    workbench = wb.build(ROOT)
    coverage = workbench['coverage']
    from liuren_material_scope import MaterialScope
    scope = MaterialScope(ROOT)
    lecture = '书籍库/北海闲人/北海闲人，特训班讲义.txt'
    try:
        scope.read(lecture, start=6, count=3)
        lecture_read = dict(ok=True)
    except (ValueError, UnicodeError, OSError) as exc:
        lecture_read = dict(ok=False, error_type=type(exc).__name__, error=str(exc))

    sources = []
    for row in load(OUT / 'source-notes.json')['sources']:
        raw = (ROOT / row['file']).read_bytes()
        lines = raw.decode(row['encoding']).split('\n')
        source = dict(path=row['file'], encoding=row['encoding'],
                      sha256=digest(ROOT / row['file']), historical_hash_matches=digest(ROOT / row['file']) == row['sha256'])
        source['windows_match'] = all('\n'.join(x.rstrip('\r') for x in lines[w['lf_start']-1:w['lf_end']]) == w['text'] for w in row['windows'])
        sources.append(source)

    void_paths = [runtime / 'methods/void.md', ROOT / 'knowledge/liuren-v3/methods/void.md',
                  ROOT / active['authoringSource'] / 'methods/void.md']
    voids = []
    for path in void_paths:
        item = dict(path=rel(path), exists=path.exists())
        if path.exists():
            item.update(sha256=digest(path), matches=[dict(lf=n, text=line.rstrip('\r'))
                for n, line in enumerate(path.read_bytes().decode('utf-8-sig').split('\n'), 1)
                if '吉神空亡喜落空' in line])
        voids.append(item)

    source_paths = sorted((ROOT / active['authoringSource']).rglob('*'))
    protected = {ROOT / '.opencode/liuren-active.json', ROOT / 'opencode.json', ROOT / 'AGENTS.md',
                 ROOT / 'README.md', ROOT / '目录总索引.md'}
    protected.update(runtime / name for name in manifest['files'])
    protected.add(runtime / 'manifest.json')
    protected.update(p for p in source_paths if p.is_file())
    protected.update(p for p in (ROOT / '.opencode/skills/liuren').rglob('*') if p.is_file())
    protected.update(ROOT / name for name in active['workflowImplementation'])
    protected.update(ROOT / item['file'] for item in active.get('localModuleOverrides', {}).values())
    protected.update(ROOT / x['path'] for x in sources)
    protected.update(ROOT / name for name in ['docs/本机六壬完整研判流程.md', 'docs/本机OpenCode完整输出规则.md',
                     'tools/liuren_material_scope.py', 'tools/liuren_research_overlay.py'])
    protected.update(p for p in (ROOT / 'knowledge/liuren-research/20261102').rglob('*.json'))
    hashes = {rel(p): digest(p) for p in sorted(protected) if p.is_file()}
    result = dict(checked_at=datetime.now(timezone(timedelta(hours=8))).isoformat(),
        purpose='方案审查的只读结构、来源及资料可达性核验；不是59模块逐条语义验收或预测验证',
        baseline=dict(release=active['release'], methodVersion=active['methodVersion'], authoringSource=active['authoringSource'],
            authoring_source_has_manifest=(ROOT / active['authoringSource'] / 'manifest.json').exists(),
            entries=len(list((ROOT / '.opencode/skills/liuren').rglob('SKILL.md'))), modules=len(manifest['modules']),
            required=len(manifest['required']), domains=len(manifest['domains']), domain_ids=manifest['domains'],
            historical_inventory_pointer_matches=digest(ROOT / '.opencode/liuren-active.json') == prior['active_pointer_sha256'],
            historical_inventory_modules_match=set(manifest['modules']) == {x['id'] for x in prior['modules']},
            registered_file_mismatches=[name for name, value in manifest['files'].items() if digest(runtime / name) != value]),
        effective_modules=actual, source_note_checks=sources, known_void_error=voids,
        lecture_scope_read=lecture_read,
        scope_checks=dict(proposal_output_permitted=scope.permitted(OUT / '原文研读笔记.md'),
                          current_revision_entry_permitted=scope.permitted(ROOT / active['authoringSource'] / 'entry.md'),
                          current_revision_files_in_research_scan=sum(p.is_relative_to(ROOT / active['authoringSource']) for p in scope.files('research'))),
        knowledge_summary={key: coverage[key] for key in ['new_rule_count', 'audit_count', 'explicit_rule_family_count',
            'eligible_checked_record_count', 'full_source_read_count', 'pending_reading_windows',
            'independent_validation_count', 'complete']},
        knowledge_validation=workbench['validation'], protected_file_hashes_before_document_edit=hashes,
        limitations=['工作台的语义状态是既有登记，不是本轮重新精读确认。',
                     '资料扫描可达不表示已有真实会话误采用该材料。',
                     '未测试真实OpenCode会话、模型调用、完整历法算法或预测效果。'])
    target = OUT / '方案审查核验.json'
    if target.exists():
        raise FileExistsError('Preserve previous review evidence: ' + str(target))
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    summary = {k: result[k] for k in ['baseline', 'source_note_checks', 'known_void_error', 'lecture_scope_read',
        'scope_checks', 'knowledge_summary']}
    summary['knowledge_validation'] = {k: result['knowledge_validation'][k]
        for k in ['valid', 'record_count', 'passed', 'blocked', 'complete']}
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print('protected_file_count=' + str(len(hashes)))


if __name__ == '__main__':
    main()
