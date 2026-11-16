"""Restore only task-owned backed-up files; retain the new frozen release for history."""
from pathlib import Path
import json,hashlib,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
B=read(OUT/'before-manifest.json');R=read(OUT/'activation-receipt.json')
for rel,d in R['live'].items():assert sha(ROOT/rel)==d,'changed since activation: '+rel
for rel,d in B['live'].items():assert sha(OUT/'before'/rel)==d,rel
for rel in [r for r in B['live'] if r!='.opencode/liuren-active.json']+['.opencode/liuren-active.json']:shutil.copyfile(OUT/'before'/rel,ROOT/rel)
print(json.dumps({'restored':B['parentRelease'],'retainedInactiveRuntime':R['runtime'],'retainedUnusedHelper':'tools/liuren-event-positioning.mjs'}))
