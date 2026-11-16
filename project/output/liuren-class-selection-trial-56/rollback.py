"""Restore the exact 55 active configuration, only if these files remain at 56 hashes."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=load(O/'before.json');a=load(O/'after.json')
changed=[f for f,h in a['files'].items() if not (R/f).is_file() or sha(R/f)!=h]
if changed:raise SystemExit('Files changed after 56; refusing to overwrite: '+', '.join(changed))
for f,h in b['files'].items():
 if sha(O/'before'/f)!=h:raise SystemExit('Backup mismatch: '+f)
for f in b['files']:shutil.copy2(O/'before'/f,R/f)
print('Restored 55; restart OpenCode. Frozen 56 retained for evidence.')
