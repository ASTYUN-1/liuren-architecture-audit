"""Restore the exact former local binding; refuse to overwrite later edits."""
from pathlib import Path
import json,hashlib,shutil,os
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=load(OUT/'before.json');after=load(OUT/'after.json')
assert load(ROOT/'.opencode/liuren-active.json')['release']=='20261109-guanshen-36'
assert all(sha(ROOT/f)==h for f,h in after['files'].items()),'Later edits present; preserve and review before rollback'
for f,h in before['files'].items():assert sha(OUT/'before'/f)==h
for f in [x for x in before['files'] if x!='.opencode/liuren-active.json']+['.opencode/liuren-active.json']:
 target=ROOT/f;tmp=target.with_name(target.name+'.rollback36.tmp');shutil.copy2(OUT/'before'/f,tmp);os.replace(tmp,target)
print('Restored',before['release'],'; retained the inactive new runtime and audit evidence')
