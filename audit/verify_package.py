"""Verify the exported package's complete checksum list; no network/model calls."""
from pathlib import Path
import hashlib
import json
import os

root=Path(__file__).resolve().parents[1]
if os.name=='nt' and not str(root).startswith('\\\\?\\'):root=Path('\\\\?\\'+str(root))
rows=[]
for line in (root/'SHA256SUMS.txt').read_text('utf-8').splitlines():
    expected,name=line.split('  ',1)
    p=root/name
    actual=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    rows.append({'path':name,'ok':actual==expected})
declared={r['path'] for r in rows}|{'SHA256SUMS.txt'}
actual={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
result={'ok':all(r['ok'] for r in rows) and declared==actual,'verified':len(rows),'mismatches':[r['path'] for r in rows if not r['ok']],'unexpected':sorted(actual-declared),'missing':sorted(declared-actual)}
print(json.dumps(result,ensure_ascii=False,indent=2))
raise SystemExit(0 if result['ok'] else 2)
