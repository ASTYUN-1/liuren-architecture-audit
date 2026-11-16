"""Snapshot the source inventory for the non-destructive experience review."""
from pathlib import Path
import hashlib
import json
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/经验库梳理/20261019'

def group(name):
    if name.startswith('_') or name == 'README.md':
        return 'support'
    if 'raw-' in name:
        return 'new'
    if name.startswith(('古籍-', '提取-', '推命参考-', '六壬推命')):
        return 'books'
    return 'history'

def main():
    (OUT / 'data').mkdir(parents=True, exist_ok=True)
    (OUT / 'work').mkdir(exist_ok=True)
    if (OUT / 'data/source-manifest.json').exists():
        raise SystemExit('快照已存在，不覆盖整理前哈希。请为后续整理选择新的快照目录。')
    records = []
    for path in sorted((ROOT / '经验日志').glob('*.md')):
        raw = path.read_bytes()
        lines = raw.decode('utf-8-sig').splitlines()
        records.append(dict(path=path.relative_to(ROOT).as_posix(), group=group(path.name),
                            bytes=len(raw), lines=len(lines), sha256=hashlib.sha256(raw).hexdigest(),
                            headings=[dict(line=i, title=line) for i, line in enumerate(lines,1)
                                      if line.startswith('#')]))
    cases = []
    for path in sorted((ROOT / '案例项目库').rglob('*.md')):
        raw = path.read_bytes()
        cases.append(dict(path=path.relative_to(ROOT).as_posix(), sha256=hashlib.sha256(raw).hexdigest()))
    manifest = dict(created_at=datetime.now().isoformat(timespec='seconds'),
                    scope='经验日志根目录全部 Markdown；案例库用于来源交叉核对，不重做全部案例分析',
                    sources=records, case_snapshot=cases)
    (OUT/'data/source-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    counts = {g:sum(r['group']==g for r in records) for g in ('history','books','new','support')}
    print(json.dumps(counts, ensure_ascii=False))

if __name__ == '__main__':
    main()
