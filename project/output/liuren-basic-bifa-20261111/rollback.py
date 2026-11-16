"""Restore only this release's known files; retain all chart/test evidence."""
from pathlib import Path
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=load(OUT/'before.json');after=load(OUT/'after.json')
pointer=load(ROOT/'.opencode/liuren-active.json')
assert pointer['release']==after['release'],'Another release is active; do not overwrite it.'
for rel,h in after['files'].items():assert sha(ROOT/rel)==h,'Changed after this release: '+rel
for rel,h in before['files'].items():assert sha(OUT/'before'/rel)==h,'Backup changed: '+rel
for rel,h in before['frozen'].items():assert sha(ROOT/rel)==h,'Frozen runtime changed: '+rel
for rel in sorted(before['files'],key=lambda r:r=='.opencode/liuren-active.json'):
 dest=ROOT/rel;temp=dest.with_name(dest.name+'.bifa42-rollback.tmp')
 with temp.open('xb') as handle:handle.write((OUT/'before'/rel).read_bytes())
 os.replace(temp,dest)
print('Restored',before['release'],'; restart OpenCode. New evidence and runtime42 retained.')
