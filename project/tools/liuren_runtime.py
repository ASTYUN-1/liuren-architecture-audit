"""Deterministic candidate packaging. No model calls and no active-skill writes."""
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'knowledge/liuren'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def safe_file(base, name):
    if not isinstance(name, str) or '\\' in name or ':' in name or any(x in ('', '.', '..') for x in name.split('/')):
        raise ValueError('invalid runtime path: ' + str(name))
    p = base / name
    if any(q.is_symlink() for q in [p, *p.parents] if q != base.parent):
        raise ValueError('symlink forbidden')
    if not p.resolve().is_relative_to(base.resolve()):
        raise ValueError('runtime path escapes root')
    return p


def content_version(files, mode):
    return sha(json.dumps({'files': files, 'mode': mode}, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode())


def build(output, mode='enhanced', source=SOURCE):
    output, source = Path(output).resolve(), Path(source).resolve()
    active = ROOT / '.opencode'
    if output == ROOT or output.is_relative_to(active) or active.is_relative_to(output) or output.is_relative_to(source) or source.is_relative_to(output):
        raise ValueError('protected output directory')
    if output.exists():
        raise ValueError('output must not exist')
    m = json.loads((source / 'manifest.json').read_text('utf-8'))
    if mode not in ('structural', 'enhanced'):
        raise ValueError('invalid mode')
    # Verify maintenance assets before making a package. No silent stale snapshots.
    for name, expected in m['files'].items():
        if sha(safe_file(source, name).read_bytes()) != expected:
            raise ValueError('maintenance hash mismatch: ' + name)
    output.mkdir(parents=True)
    refs = output / '.opencode/skills/daliuren/refs/runtime'
    shutil.copytree(source, refs)
    if mode == 'structural':
        shutil.copyfile(refs / 'sources/structural-core.md', refs / 'core.md')
    modules = {k: {**v, 'id': f'skill:daliuren/refs/runtime/{v["file"]}'} for k, v in m['modules'].items()}
    entry = output / '.opencode/skills/daliuren/SKILL.md'
    entry.write_text('---\nname: daliuren\ndescription: 大六壬单事研判；按北海三步法定位对象，核课传理气、制救和反证。纯排盘、出生推命与资料维护另用原入口。\n---\n\n'
                     '# 大六壬单事研判候选\n\n'
                     f'模式：{mode}。本包仅供本地验收；不代表预测准确率已验证。\n\n'
                     '先完整读取 [判断核心](refs/runtime/core.md) 和 [证据纪律](refs/runtime/evidence.md)，固定原问和成功标准。'
                     '再读对应占类及 [神煞基础](refs/runtime/mechanisms/shensha.md)；按关键关系触发完整机制，不按吉凶名目投票。\n\n'
                     '旧方法名见 [模块清单](refs/runtime/manifest.json) 的 legacyAliases；它们是同一规则的模块别名，不是八套另起的流程。'
                     '同版本完整已读内容可复用。来源档案是查证材料，历史说明不改变当前入口。\n\n'
                     + '\n'.join(f'- [{k}](refs/runtime/{v["file"]})：{v["when"]}' for k, v in modules.items()) + '\n', encoding='utf-8')
    files = {p.relative_to(output).as_posix(): sha(p.read_bytes()) for p in sorted(output.rglob('*')) if p.is_file()}
    runtime = dict(schemaVersion=2, mode=mode, version=content_version(files, mode), files=files,
                   modules=modules, required=['core', 'evidence', 'shensha'], routes=m['routes'],
                   legacyAliases=m['legacyAliases'], entryId='skill:daliuren/SKILL.md', scope='single-event')
    write_json(output / 'liuren-runtime.json', runtime)
    verify(output)
    return runtime


def verify(candidate, baseline=None):
    candidate = Path(candidate).resolve()
    m = json.loads((candidate / 'liuren-runtime.json').read_text('utf-8'))
    if m['schemaVersion'] != 2 or m['version'] != content_version(m['files'], m['mode']):
        raise ValueError('runtime identity mismatch')
    actual = {p.relative_to(candidate).as_posix() for p in candidate.rglob('*') if p.is_file()}
    if actual != set(m['files']) | {'liuren-runtime.json'}:
        raise ValueError('unbound or missing candidate file')
    for name, expected in m['files'].items():
        if sha(safe_file(candidate, name).read_bytes()) != expected:
            raise ValueError('candidate hash mismatch: ' + name)
    seen, visiting = set(), set()
    def visit(key):
        if key in visiting:
            raise ValueError('cyclic module dependency')
        if key in seen:
            return
        v = m['modules'][key]
        if v['id'] != 'skill:daliuren/refs/runtime/' + v['file'] or '.opencode/skills/daliuren/refs/runtime/' + v['file'] not in m['files']:
            raise ValueError('module binding missing')
        visiting.add(key)
        for dep in v['requires']:
            visit(dep)
        visiting.remove(key); seen.add(key)
    for key in m['modules']:
        visit(key)
    for group in [m['required'], *m['routes'].values(), *m['legacyAliases'].values()]:
        for key in group:
            if key not in m['modules']:
                raise ValueError('unknown routed module')
    refs = candidate / '.opencode/skills/daliuren/refs/runtime'
    maintenance = json.loads((refs / 'manifest.json').read_text('utf-8'))
    expected_modules = {k: {**v, 'id': f'skill:daliuren/refs/runtime/{v["file"]}'} for k, v in maintenance['modules'].items()}
    if (m['modules'] != expected_modules or m['routes'] != maintenance['routes'] or
            m['legacyAliases'] != maintenance['legacyAliases'] or m['required'] != ['core', 'evidence', 'shensha']):
        raise ValueError('runtime metadata binding mismatch')
    migration = json.loads((refs / 'migration-map.json').read_text('utf-8'))
    coverage, source_text, target_text = {}, {}, {}
    for row in migration:
        if row['snapshot'] not in source_text:
            raw = safe_file(refs, row['snapshot']).read_bytes()
            source_text[row['snapshot']] = (sha(raw), raw.decode('utf-8-sig').replace('\r\n', '\n'))
        source_hash, text = source_text[row['snapshot']]
        if source_hash != row['sourceHash']:
            raise ValueError('migration source hash mismatch')
        old = text[row['start']:row['end']]
        if sha(old.encode()) != row['oldTextHash']:
            raise ValueError('migration paragraph mismatch')
        if row['targetFile'] not in target_text:
            target_text[row['targetFile']] = safe_file(refs, row['targetFile']).read_text('utf-8')
        target = target_text[row['targetFile']]
        if row['action'] != 'historical-reference' and row['renderedText'] not in target:
            raise ValueError('migrated paragraph missing')
        coverage.setdefault(row['snapshot'], []).append((row['start'], row['end'], row['oldTextHash']))
    expected_sources = {p.relative_to(refs).as_posix() for p in (refs / 'sources/snapshots/.opencode/skills').rglob('*.md')}
    if set(coverage) != expected_sources:
        raise ValueError('migration source coverage incomplete')
    for name, spans in coverage.items():
        text = safe_file(refs, name).read_text('utf-8-sig')
        expected = [(p.start(), p.end(), sha(p.group().encode())) for p in re.finditer(r'\S.*?(?=\n\s*\n|\Z)', text, re.S)]
        if sorted(spans) != expected:
            raise ValueError('migration paragraph coverage incomplete: ' + name)
    # All Markdown links generated by migration are local and hash bound. Ignore code examples.
    broken = []
    for path in [candidate / '.opencode/skills/daliuren/SKILL.md', *[refs / v['file'] for v in m['modules'].values()]]:
        text = re.sub(r'```.*?```|<!--.*?-->', '', path.read_text('utf-8'), flags=re.S)
        for target in re.findall(r'\[[^\]\n]+\]\((<[^>]+>|[^\s)]+)\)', text):
            target = target.strip('<>').split('#')[0]
            if not target or target.startswith(('http:', 'https:')):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.is_relative_to(candidate) or not resolved.is_file():
                broken.append(str(path.relative_to(candidate)) + ': ' + target)
    if broken:
        raise ValueError('broken runtime links: ' + json.dumps(broken, ensure_ascii=False))
    if baseline:
        base = Path(baseline)
        inventory = json.loads((base / 'inventory.json').read_text('utf-8'))
        for row in inventory:
            if sha(safe_file(base, row['path']).read_bytes()) != row['sha256']:
                raise ValueError('baseline changed')
        covered = {row['sourcePath'] for row in migration}
        required = {r['path'] for r in inventory if r['path'].startswith('.opencode/skills/') and r['path'].endswith('.md') and not re.search(r'test-(prompts|results)', r['path'])}
        if not required <= covered:
            raise ValueError('unmapped sources: ' + str(required - covered))
    return dict(version=m['version'], mode=m['mode'], files=len(m['files']), paragraphs=len(migration), modules=len(m['modules']), links='passed')
