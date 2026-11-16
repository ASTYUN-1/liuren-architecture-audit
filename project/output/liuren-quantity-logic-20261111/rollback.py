"""Restore recorded local files only if this release is still active and unchanged."""
from pathlib import Path
import hashlib
import json
import os

R=Path(__file__).resolve().parents[2]
O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=load(O/'before.json');after=load(O/'after.json')
assert load(R/'.opencode/liuren-active.json')['release']==after['release'],'A later release is active'
assert all(sha(R/f)==h for f,h in after['files'].items()),'Later edits exist; inspect before restoring'
assert all(sha(O/'before'/f)==h for f,h in before['files'].items()),'Backup changed'
for rel in sorted(before['files'],key=lambda f:f=='.opencode/liuren-active.json'):
    target=R/rel;tmp=target.with_name(target.name+'.rollback46.tmp')
    tmp.write_bytes((O/'before'/rel).read_bytes());os.replace(tmp,target)
print('Restored',before['release'],'; retained runtime46 and audit records for provenance')
