"""Publish the active modular methods over an unchanged production evidence corpus."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
PREFIX = '.opencode/skills/daliuren/refs/runtime/'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')


def build(base, output):
    if output.exists():
        raise ValueError('output exists; do not overwrite a frozen website package')
    pointer = json.loads((ROOT / '.opencode/liuren-active.json').read_text('utf-8'))
    local = ROOT / pointer['runtime']
    source = json.loads((local / 'manifest.json').read_text('utf-8'))
    if source['release'] != pointer['release'] or source['version'] != pointer['methodVersion']:
        raise ValueError('local active release mismatch')
    corpus = json.loads((base / 'knowledge-manifest.json').read_text('utf-8'))
    for name, expected in corpus['files'].items():
        path = base / name
        if sha(path.read_bytes()) != expected:
            raise ValueError('base corpus changed: ' + name)
        if name.startswith('.opencode/') or name == 'liuren-runtime.json':
            continue  # Legacy method entries are not installed in this release.
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    runtime = output / PREFIX
    shutil.copytree(local, runtime)
    for name, expected in source['files'].items():
        if sha((runtime / name).read_bytes()) != expected:
            raise ValueError('local method changed: ' + name)
    route = json.loads((runtime / 'reading-route.json').read_text('utf-8'))
    entry = (runtime / 'entry.md').read_text('utf-8')
    # Only the entry's host operations are adapted. All 47 method bodies stay exact.
    entry = entry.replace('所有相对链接以本文件所在目录为准；命令在项目根目录执行。',
                          '网站受限工具模式；下表读取要求与本地正式版一致，操作由网站工具执行。')
    entry = re.sub(r'^- 先判定占类及下表条件；.*$',
        '- 先 list_knowledge 查看模块和路由，再 register_questions 登记原问、事件主体、占类及条件。其 readingPlan 是本问分环节读取清单；用 read_knowledge 按 ID 完整读取，新增争点时修订并补读。', entry, flags=re.M)
    entry = re.sub(r'^- 分页用 .*$',
        '- read_knowledge 使用 JSON 传输，按 deliveryHash 读取全部 missingPages，complete=true 才算完整；其 pageHash 对返回 text 的 UTF-8 字节计算。文件哈希与适配后全文哈希分别记录，不使用本地 stdout 页凭证。读取完成不证明模型理解或正确采用。', entry, flags=re.M)
    entry = re.sub(r'\]\(<?((?:methods|references|domains|details)/[^)>]+)>?\)',
                   lambda m: '](skill:daliuren/refs/runtime/' + m[1] + ')', entry)
    entry = re.sub(r'`--(?:nianming|timing|condition [a-z-]+)`',
                   lambda m: '`conditions: ' + m[0].strip('`').replace('--condition ', '').replace('--', '') + '`', entry)
    entry = entry.replace('plan 参数', 'register_questions 参数')
    entry = entry.replace('本地无网站的 `register_questions`、`record_judgment` 工具。以报告的可核对记录交付；不可声称已执行不存在的调用或程序门禁。',
                          '网站使用 register_questions、record_judgment 记录十一环节摘要、角色关系和依赖；完整阅读由服务器分页覆盖校验。内部记录与公开报告分开。')
    (output / '.opencode/skills/daliuren/SKILL.md').write_text(entry, encoding='utf-8', newline='\n')
    modules = {key: dict(file=value['file'], id='skill:daliuren/refs/runtime/' + value['file'],
                        requires=value['requires'], when=value['trigger']) for key, value in source['modules'].items()}
    files = {p.relative_to(output).as_posix(): sha(p.read_bytes()) for p in (output / '.opencode').rglob('*') if p.is_file()}
    identity = dict(files=dict(sorted(files.items())), mode='enhanced')
    manifest = dict(schemaVersion=3, mode='enhanced', release=source['release'], localMethodVersion=source['version'],
        version=sha(json.dumps(identity, ensure_ascii=False, separators=(',', ':')).encode()), files=files,
        modules=modules, required=source['required'], routes={key: [key] for key in route['domains']},
        legacyAliases={}, entryId='skill:daliuren/SKILL.md', readingRoute=route)
    dump(output / 'liuren-runtime.json', manifest)
    # Original source archives are searchable evidence, never automatic method entries.
    documents = list(corpus['documents'])
    module_files = {value['file'] for value in source['modules'].values()}
    for path in sorted(runtime.rglob('*')):
        rel = path.relative_to(runtime).as_posix()
        if not path.is_file() or path.suffix not in ('.md', '.txt') or rel in module_files or rel == 'entry.md':
            continue
        raw = path.read_bytes()
        text = raw.decode('utf-8-sig')
        source_path = PREFIX + rel
        # Keep bounded original sections compatible with the existing reference index.
        chunks, current, size = [], [], 0
        for char in text:
            count = len(char.encode())
            if size + count > 6000:
                chunks.append(''.join(current)); current, size = [], 0
            current.append(char); size += count
        if current:
            chunks.append(''.join(current))
        identity = sha(('modular-source:' + rel).encode())[:20]
        for number, chunk in enumerate(chunks, 1):
            file = f'_modular_sources/{identity}-{number}.md'
            target = output / file
            target.parent.mkdir(exist_ok=True)
            target.write_bytes(chunk.encode())
            documents.append(dict(id=f'reference:{identity}:{number}', file=file, source=source_path,
                hash=sha(chunk.encode()), kind='reference', title=path.stem, meta={},
                provenance=dict(sourceHash=sha(raw), encoding='utf-8-sig' if raw.startswith(b'\xef\xbb\xbf') else 'utf-8',
                                feedback='unknown', section=number, sections=len(chunks))))
    corpus.update(policyVersion='liuren-modular-20261023-03', documents=documents)
    corpus['files'] = {p.relative_to(output).as_posix(): sha(p.read_bytes()) for p in sorted(output.rglob('*')) if p.is_file()}
    dump(output / 'knowledge-manifest.json', corpus)
    print(json.dumps(dict(release=source['release'], methodVersion=source['version'], runtimeVersion=manifest['version'],
        baseManifestHash=sha((base / 'knowledge-manifest.json').read_bytes()),
        manifestHash=sha((output / 'knowledge-manifest.json').read_bytes()), modules=len(modules),
        files=len(corpus['files']), documents=len(documents), output=str(output)), ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    build(args.base.resolve(), args.output.resolve())
