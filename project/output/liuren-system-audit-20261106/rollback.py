"""Restore only this audit's edits; refuse to overwrite any later changes."""
from pathlib import Path
import json,hashlib,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
B=read(OUT/'before-manifest.json');A=read(OUT/'activation-receipt.json')
assert read(ROOT/'.opencode/liuren-active.json')['release']==A['release'],'not the installed release'
for rel,digest in A['live'].items():assert sha(ROOT/rel)==digest,'later change: '+rel
for rel in A['live']:
 if rel in B['live']:assert sha(OUT/'before'/rel)==B['live'][rel],rel
for rel in A['live']:
 if rel=='.opencode/liuren-active.json':continue
 target=(ROOT/rel).resolve();assert target.is_relative_to(ROOT.resolve())
 if rel in B['live']:shutil.copyfile(OUT/'before'/rel,target)
 else:target.unlink()  # Exact newly introduced file; no recursive removal.
tmp=ROOT/'.opencode/liuren-active.json.system-audit-rollback';assert not tmp.exists()
shutil.copyfile(OUT/'before/.opencode/liuren-active.json',tmp);tmp.replace(ROOT/'.opencode/liuren-active.json')
for rel in A['live']:
 if rel in B['live']:assert sha(ROOT/rel)==B['live'][rel],rel
print(json.dumps({'restored':B['parentRelease'],'frozen18Preserved':True,'restartOpenCodeRequired':True}))
