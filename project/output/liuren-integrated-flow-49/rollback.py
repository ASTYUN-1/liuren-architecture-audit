"""Restore the saved live files only; refuse to overwrite subsequent edits."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=load(O/'before.json');after=load(O/'after.json')
assert load(R/'.opencode/liuren-active.json')['release']==after['release'],'Active version changed'
for f,h in after['files'].items():assert sha(R/f)==h,'Subsequent edit; stop: '+f
for f,h in before['files'].items():assert sha(O/'before'/f)==h,'Backup changed: '+f
for f in sorted(before['files'],key=lambda f:f=='.opencode/liuren-active.json'):shutil.copyfile(O/'before'/f,R/f)
print('Restored',before['release'],'; candidate runtime and new docs/tests kept inactive; restart OpenCode')
