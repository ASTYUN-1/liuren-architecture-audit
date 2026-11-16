"""Hash-guarded rollback. Default is a dry run; never recreate a stale Git lock."""
from pathlib import Path
import json,hashlib,shutil,sys
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1].resolve()
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=load(OUT/'activation.json')
assert load(ROOT/'.opencode/liuren-active.json')['release']==a['release']
for rel,row in a['changedFiles'].items():
    target=(ROOT/rel).resolve();assert target.is_relative_to(ROOT)
    assert sha(target)==row['after'],'Concurrent changes; refusing overwrite: '+rel
    assert sha(OUT/'before'/rel)==row['before'],rel
for rel,h in a['newFiles'].items():
    target=(ROOT/rel).resolve();assert target.is_relative_to(ROOT)
    assert target.is_file() and sha(target)==h,'Concurrent changes; refusing removal: '+rel
if '--apply' not in sys.argv:
    print('Preflight passed. --apply restores only this change set; frozen runtimes, logs and lock evidence remain.')
    raise SystemExit(0)
for rel in sorted(a['changedFiles'],key=lambda r:r=='.opencode/liuren-active.json'):
    shutil.copyfile(OUT/'before'/rel,ROOT/rel)
for rel in a['newFiles']:(ROOT/rel).unlink()
print('Restored pre-change files. Restart OpenCode. No runtime/logs deleted and no lock recreated.')
