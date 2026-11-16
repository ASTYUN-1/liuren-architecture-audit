"""Restore the previous active local tool layer; keep new evidence and runtime."""
from pathlib import Path
import json,hashlib,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=load(OUT/'before.json');after=load(OUT/'after.json')
assert load(ROOT/'.opencode/liuren-active.json')['release']=='20261109-deterministic-tools-35','only rollback current35'
changed=[rel for rel,digest in after['files'].items() if sha(ROOT/rel)!=digest]
assert not changed,'files changed after acceptance; preserve edits and review: '+str(changed)
for rel,digest in before['files'].items():
 src=OUT/'before'/rel;assert sha(src)==digest;shutil.copy2(src,ROOT/rel)
print('Restored',before['release'],'; retained new files as inactive evidence')
