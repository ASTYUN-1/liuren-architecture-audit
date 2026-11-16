from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
audit=json.loads((OUT/'验收摘要.json').read_text('utf8'))
backups=[p for p in (OUT/'before').rglob('*') if p.is_file()]
for b in backups:
 rel=b.relative_to(OUT/'before').as_posix();target=ROOT/rel
 assert sha(target)==audit['after'][rel], '后续编辑，停止回退：'+rel
pointer='.opencode/liuren-active.json'
for b in sorted(backups,key=lambda p:p.relative_to(OUT/'before').as_posix()==pointer):
 target=ROOT/b.relative_to(OUT/'before');shutil.copy2(b,target)
print('Restored pre-integration files and pointer; retained archives and new runtime.')
