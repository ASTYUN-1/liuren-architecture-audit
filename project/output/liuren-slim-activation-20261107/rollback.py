"""Restore only this activation's exact files; default is read-only preview."""
from pathlib import Path
import hashlib
import json
import os
import shutil
import sys

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
record=json.loads((OUT/'activation.json').read_text('utf-8'))
for rel,digest in record['before'].items():
    assert sha(OUT/'before'/rel)==digest, 'Backup changed: '+rel
conflicts=[rel for rel,digest in record['after'].items() if sha(ROOT/rel)!=digest]
assert not conflicts,'Files changed after activation; preserve them and resolve manually: '+repr(conflicts)
if '--apply' not in sys.argv:
    print('Preview: restore '+str(len(record['before']))+' local files; pointer last. Use --apply to restore. No runtime is deleted.')
else:
    files=[rel for rel in record['before'] if rel!='.opencode/liuren-active.json']+['.opencode/liuren-active.json']
    for rel in files:
        p=ROOT/rel;tmp=p.with_name(p.name+'.rollback26.tmp');shutil.copyfile(OUT/'before'/rel,tmp);os.replace(tmp,p)
    assert all(sha(ROOT/rel)==digest for rel,digest in record['before'].items())
    print('Restored '+record['previousRelease']+' locally. Restart OpenCode and start a new session.')
