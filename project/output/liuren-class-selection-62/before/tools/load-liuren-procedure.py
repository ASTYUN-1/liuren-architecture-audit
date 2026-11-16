"""Bounded section reader for the three preserved specialist procedures."""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys

spec = importlib.util.spec_from_file_location('liuren_method_pages', Path(__file__).with_name('load-liuren-methods.py'))
pages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pages)
NAMES = ['liuren-cases', 'liuren-extract']


def procedure(runtime, manifest, name):
    if name not in NAMES:
        raise ValueError('unknown specialist')
    relative = ('archive/previous-package/.opencode/skills/daliuren/refs/runtime/'
                'sources/snapshots/.opencode/skills/' + name + '/SKILL.md')
    relative = manifest.get('procedureFiles', {}).get(name, relative)
    path = (runtime / relative).resolve()
    if not path.is_relative_to(runtime.resolve()):
        raise ValueError('procedure escapes candidate runtime')
    raw = path.read_bytes()
    if manifest['files'].get(relative) != pages.sha(raw):
        raise ValueError('specialist source hash mismatch')
    return path, raw.decode('utf-8-sig').replace('\r\n', '\n'), pages.sha(raw)


def sections(text):
    """Split real section/step headings; fenced example headings remain data."""
    lines = text.splitlines(keepends=True)
    starts, fence = [(0, '文件头与版本声明')], None
    for number, line in enumerate(lines):
        match = re.match(r'^\s*(`{3,}|~{3,})', line)
        if match:
            token = match[1][0]
            fence = None if token == fence else token
        elif fence is None and (line.startswith('## ') or re.match(r'^#{3,4} (步骤\s*\d+|[ER]\d+|正向查询|反向分析)', line)):
            starts.append((number, line.lstrip('# ').strip()))
    if fence:
        raise ValueError('source procedure has unclosed fence; cannot safely partition')
    result = []
    for index, (start, title) in enumerate(starts):
        end = starts[index + 1][0] if index + 1 < len(starts) else len(lines)
        result.append(dict(id=f'P{index:03}', title=title, lineStart=start + 1, lineEnd=end,
                           text=''.join(lines[start:end])))
    if ''.join(part['text'] for part in result) != text:
        raise ValueError('procedure partition incomplete')
    return result


def main():
    pages.configure_stdout()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['plan', 'read'])
    parser.add_argument('name', choices=NAMES)
    parser.add_argument('--part')
    parser.add_argument('--page', type=int)
    args = parser.parse_args()
    runtime, manifest = pages.active()
    path, text, hash_ = procedure(runtime, manifest, args.name)
    parts = sections(text)
    if args.command == 'plan':
        print(json.dumps(dict(release=manifest['release'], name=args.name, path=str(path), sha256=hash_,
            policy='Read the current wrapper first. Required method/boundary/operation sections and applicable steps must be read in full; examples are source material. Old installation paths do not override current grouped layout.',
            parts=[{k: v for k, v in part.items() if k != 'text'} | dict(pages=len(pages.page_text(part['text']))) for part in parts]), ensure_ascii=False, indent=2))
        return
    selected = next((part for part in parts if part['id'] == args.part), None)
    if not selected:
        raise ValueError('unknown procedure part; inspect plan first')
    chunks = pages.page_text(selected['text'])
    if args.page is None or not 1 <= args.page <= len(chunks):
        raise ValueError('invalid page; valid 1..' + str(len(chunks)))
    content = chunks[args.page - 1]
    receipt = dict(release=manifest['release'], procedure=args.name, part=args.part, page=args.page,
                   pages=len(chunks), sourceSha256=hash_, pageSha256=pages.sha(content.encode()),
                   chars=len(content), bytes=len(content.encode()), encoding='utf-8', newline='LF')
    print('LIUREN_PROCEDURE_BEGIN ' + json.dumps(receipt, ensure_ascii=False))
    sys.stdout.write(content)
    print('\nLIUREN_PROCEDURE_END ' + json.dumps(receipt, ensure_ascii=False))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, KeyError, OSError, json.JSONDecodeError) as exc:
        print('LIUREN_PROCEDURE_ERROR: ' + str(exc), file=sys.stderr)
        sys.exit(2)
