from pathlib import Path
import json,hashlib,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
B=load(OUT/'before-manifest.json');A=load(OUT/'activation-receipt.json')
for rel,d in A['live'].items():
 if sha(ROOT/rel)!=d:raise SystemExit('发布后又有修改，停止回滚：'+rel)
for rel,d in B['live'].items():
 assert sha(OUT/'before'/rel)==d,rel
for rel in B['live']:shutil.copyfile(OUT/'before'/rel,ROOT/rel)
print(json.dumps({'restored':B['parentRelease'],'preservedNewRuntimeAndEvidence':True}))
