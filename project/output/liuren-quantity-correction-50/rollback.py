"""Restore only saved live files; preserve new artifacts and subsequent edits."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=load(O/'before.json');a=load(O/'after.json')
assert load(R/'.opencode/liuren-active.json')['release']==a['release'],'Active version changed'
assert set(a['files'])==set(b['files'])
for f,h in a['files'].items():assert sha(R/f)==h,'Subsequent edit; stop: '+f
for f,h in b['files'].items():assert sha(O/'before'/f)==h,'Backup changed: '+f
for f in sorted(b['files'],key=lambda f:f=='.opencode/liuren-active.json'):shutil.copyfile(O/'before'/f,R/f)
print('Restored',b['release'],'; new modules, tests and docs kept inactive; restart OpenCode')
