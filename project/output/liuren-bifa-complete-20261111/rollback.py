"""Rollback only this task's unchanged outputs; refuse to overwrite later work."""
from pathlib import Path
import json,hashlib,os
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=load(O/'before.json');after=load(O/'after.json')
assert load(R/'.opencode/liuren-active.json')['release']==after['release']
for rel,h in after['files'].items():assert sha(R/rel)==h,'later change: '+rel
for rel,h in after.get('created_test_files',{}).items():
 assert (R/rel).resolve().is_relative_to(R.resolve())
 assert sha(R/rel)==h,'later change: '+rel
for rel in sorted(before['files'],key=lambda s:s=='.opencode/liuren-active.json'):
 target=R/rel;temp=target.with_name(target.name+'.rollback43.tmp');temp.write_bytes((O/'before'/rel).read_bytes());os.replace(temp,target)
for rel in after.get('created_test_files',{}):
 (R/rel).unlink()
print('Restored',before['release'],'; 43 evidence and frozen runtime retained')
