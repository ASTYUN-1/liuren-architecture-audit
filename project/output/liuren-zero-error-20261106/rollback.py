from pathlib import Path
import json,hashlib,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=load(OUT/'activation.json')
assert load(ROOT/'.opencode/liuren-active.json')['release']==a['release']
for rel,row in a['changedFiles'].items():
    assert sha(ROOT/rel)==row['after'],'Current file changed; refusing to overwrite: '+rel
    assert sha(OUT/'before'/rel)==row['before'],rel
for rel,row in a['changedFiles'].items():shutil.copyfile(OUT/'before'/rel,ROOT/rel)
print('Restored backed-up files; runtime snapshots and experiment artifacts retained')
