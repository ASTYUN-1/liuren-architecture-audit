"""Explicit material boundaries for the local divination agent, not a security sandbox."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOTS = {
    'cases': ['案例项目库'],
    'experience': ['经验日志'],
    'books': ['书籍库', 'books'],
    'research': ['knowledge/liuren-research', '资料来源/qq-homework-20261018'],
}
OPERATION_FILES = [
    'docs/本机OpenCode完整输出规则.md', 'docs/本机六壬完整研判流程.md',
    'docs/本机六壬高效执行.md', 'docs/本机六壬直接排盘.md',
    'docs/本机六壬资料检索范围.md', 'docs/初级案例整理/优秀作业参照规则.md',
    'docs/应期取数归纳-20261027/天干参与及奇门参照-补充审阅稿.md',
    'docs/应期取数归纳-20261027/核心归纳-审阅稿.md',
    'docs/应期取数归纳-20261027/原文证据摘录.md',
    'docs/应期取数归纳-20261027/天一群笔记专项核查.md',
]
EXCLUDED = {'candidate', 'candidates', '.candidate', '.candidates', 'archive', 'previous-package', 'node_modules', '.git', '__pycache__', '.cache', 'cache', 'backup', 'backups'}
TEXT_SUFFIXES = {'.md', '.txt', '.json', '.csv'}


# Exact byte identity only. No general legacy-encoding fallback is permitted.
SOURCE_ENCODINGS = {
    '书籍库/北海闲人/北海闲人，特训班讲义.txt': {
        'encoding': 'gb18030',
        'sha256': '4bc1a33167ba5b064890bfefa008b680568a79ca5db7c95d8bdca68b6f71ccc2',
        'line_mapping': 'one-based splitlines of decoded original bytes; no reflow',
    },
}


def decode_material(root, path):
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    relative = path.relative_to(root).as_posix()
    registered = SOURCE_ENCODINGS.get(relative)
    if registered and digest != registered['sha256']:
        raise ValueError('registered source hash changed; encoding/source review required: ' + relative)
    encoding = registered['encoding'] if registered else 'utf-8-sig'
    text = raw.decode(encoding)  # Strict; an unregistered legacy encoding fails visibly.
    return text, dict(fileSha256=digest, sourceEncoding=encoding,
                      lineMapping='decoded original splitlines; one-based; no reflow')


class MaterialScope:
    def __init__(self, root=ROOT):
        self.root = Path(root).resolve()
        spec = importlib.util.spec_from_file_location('scope_method_loader', Path(__file__).with_name('load-liuren-methods.py'))
        loader = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(loader)
        self.runtime, manifest = loader.active(self.root)
        # Exactly the file selected by action=method, including checked local overrides.
        self.method_files = {loader.content(self.runtime, manifest, key)[0]
                             for key in manifest['modules']}
        self.method_files.add(self.runtime / 'entry.md')
        # Only files registered by the current package; no historical runtime scan.
        self.method_files.update((self.runtime / rel).resolve() for rel in manifest['files']
                                 if Path(rel).suffix.lower() in TEXT_SUFFIXES)
        self.reference_map = json.loads((self.runtime / 'source-read-map.json').read_text('utf-8'))
        self.reference_files = {(self.root / item['path']).resolve(): item
                                for item in self.reference_map['aliases'].values()}
        self.roots = {key: [self.root / p for p in paths] for key, paths in SOURCE_ROOTS.items()}
        self.operation_files = {self.root / p for p in OPERATION_FILES}
        self.live_skills = self.root / '.opencode/skills/liuren'
        self.generated = self.root / 'tmp/liuren-materials'
        self.charts = self.root / '排盘存档/六壬'

    def permitted(self, target):
        candidate = Path(target)
        if not candidate.is_absolute():
            candidate = self.root / candidate
        resolved = candidate.resolve()
        if not resolved.is_relative_to(self.root):
            return False
        if resolved in self.reference_files:
            return True  # Exact original source identity only; checked on read.
        if any(part.lower() in EXCLUDED for part in resolved.relative_to(self.root).parts):
            return False
        exact = self.method_files | self.operation_files
        if resolved in exact:
            return True
        allowed = [p for paths in self.roots.values() for p in paths] + [self.live_skills, self.generated, self.charts]
        return any(resolved.is_relative_to(p) for p in allowed)

    def read(self, filename, start=1, count=160):
        if not 1 <= start or not 1 <= count <= 300:
            raise ValueError('start must be >=1, count within 1..300')
        path = Path(filename)
        if not path.is_absolute():
            path = self.root / path
        path = path.resolve()
        alias = self.reference_map['aliases'].get(path.relative_to(self.root).as_posix()) if path.is_relative_to(self.root) else None
        reference = alias or self.reference_files.get(path)
        if reference:
            path = (self.root / reference['path']).resolve()
            if hashlib.sha256(path.read_bytes()).hexdigest() != reference['sha256']:
                raise ValueError('source reference hash changed; review required')
        if not self.permitted(path):
            raise ValueError('超出本机研判资料范围；不读取开发文档、其他运行版本或历史备份。')
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            raise ValueError('本工具只读指定文本文件；PDF/图片可在允许资料目录中用原生 read。')
        text, source_identity = decode_material(self.root, path)
        lines = text.splitlines()
        if start > len(lines) and lines:
            raise ValueError('start exceeds file lines')
        last = min(len(lines), start + count - 1)
        return dict(source_identity, path=path.relative_to(self.root).as_posix(), start=start, end=last,
                    total_lines=len(lines), next_line=last + 1 if last < len(lines) else None,
                    text='\n'.join(f'{n}: {lines[n-1]}' for n in range(start, last + 1)),
                    reading_understanding='not_proven_by_output')

    def files(self, library):
        if library == 'methods':
            candidates = self.method_files
        elif library in self.roots:
            candidates = set()
            for root in self.roots[library]:
                if not root.is_dir() or not self.permitted(root):
                    continue
                for folder, directories, names in os.walk(root, followlinks=False):
                    directories[:] = [name for name in directories
                                      if name.lower() not in EXCLUDED and self.permitted(Path(folder) / name)]
                    candidates.update(Path(folder) / name for name in names)
        else:
            raise ValueError('library must be methods, cases, experience, books or research')
        return [p for p in sorted(candidates) if p.suffix.lower() in TEXT_SUFFIXES and self.permitted(p)]

    def scan(self, library, query, limit=40):
        if not 1 <= limit <= 100:
            raise ValueError('scan limit within 1..100')
        terms = [x for x in re.split(r'[\s,，、]+', query.strip()) if len(x) >= 2]
        if not terms or len(query) > 200:
            raise ValueError('使用至少两个字符的短关键词，查询最多200字符；不是全库通配符或正则。')
        hits, errors, scanned = [], [], 0
        files = self.files(library)
        for path in files:
            try:
                text, source_identity = decode_material(self.root, path)
            except (OSError, UnicodeError, ValueError) as exc:
                errors.append(dict(path=path.relative_to(self.root).as_posix(), error=type(exc).__name__))
                continue
            scanned += 1
            for n, line in enumerate(text.splitlines(), 1):
                found = [term for term in terms if term in line]
                if found:
                    hits.append(dict(path=path.relative_to(self.root).as_posix(), line=n,
                                     matched=found, text=line[:500], line_excerpt_truncated=len(line) > 500,
                                     **source_identity))
                    if len(hits) == limit:
                        return dict(library=library, hits=hits, files_scanned=scanned, eligible_files=len(files),
                                    limit_reached=True, complete=False, errors=errors,
                                    note='命中仅定位；缩窄关键词或读取该原档上下文，不代表没有更多资料。')
        return dict(library=library, hits=hits, files_scanned=scanned, eligible_files=len(files),
                    limit_reached=False, complete=not errors, errors=errors,
                    note='命中仅定位，采用前读取原档条件与反证。')

    def describe(self):
        return dict(libraries={k: [p.relative_to(self.root).as_posix() for p in v] for k, v in self.roots.items()},
                    methods=self.runtime.relative_to(self.root).as_posix() + ' (registered modules only)',
                    operation_files=OPERATION_FILES,
                    source_encodings=SOURCE_ENCODINGS,
                    candidate_exclusion='candidate/candidates/.candidate/.candidates path components; output remains outside scope',
                    read_only_records=['排盘存档/六壬', 'tmp/liuren-materials', '.opencode/skills/liuren'],
                    excluded='whole docs, web, mobile, ui-rebuild, output, old runtimes, archives, caches and arbitrary shell',
                    exceptions='Only the explicitly listed operation/professional source files in docs may be read; docs is never scanned.')
