"""Restore only the backed up files when no later changes would be overwritten."""
from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=load(O/'before.json');after=load(O/'after.json')
pointer=load(R/'.opencode/liuren-active.json')
assert pointer['release']==after['release'],'Refusing to overwrite a newer active release'
for f,h in after['files'].items():assert sha(R/f)==h,'Later edits: '+f
for f,h in before['files'].items():assert sha(O/'before'/f)==h,'Backup changed: '+f
for f in sorted(before['files'],key=lambda f:f=='.opencode/liuren-active.json'):
 shutil.copyfile(O/'before'/f,R/f)
print('Restored',before['release'],'; new files and frozen44 retained as inactive evidence')
