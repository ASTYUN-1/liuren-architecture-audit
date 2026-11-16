from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=load(O/'before.json');a=load(O/'after.json')
changed=[f for f,h in a['files'].items() if not (R/f).is_file() or sha(R/f)!=h]
if changed:raise SystemExit('Refusing changed files: '+', '.join(changed))
assert all(sha(O/'before'/f)==h for f,h in b['files'].items())
for f in b['files']:shutil.copy2(O/'before'/f,R/f)
# Keep the new review protocol and frozen 62 as research artifacts.
print('Restored 61 active files; restart OpenCode. Review protocol and frozen 62 retained.')
