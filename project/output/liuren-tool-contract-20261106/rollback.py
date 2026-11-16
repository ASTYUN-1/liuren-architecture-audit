from pathlib import Path
import json,hashlib,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
A=read(OUT/'activation-receipt.json');B=read(OUT/'before-manifest.json')
for rel,digest in A['live'].items():assert sha(ROOT/rel)==digest,'changed since install: '+rel
for rel,digest in B['live'].items():assert sha(OUT/'before'/rel)==digest
for rel in B['live']:
 if rel in A['live'] and rel!='.opencode/liuren-active.json':shutil.copy2(OUT/'before'/rel,ROOT/rel)
shutil.copy2(OUT/'before/.opencode/liuren-active.json',ROOT/'.opencode/liuren-active.json')
print('Restored '+B['parentRelease']+'; retained frozen packages, synthetic test and audit outputs.')
