"""Restore the pre-54 workspace after verifying exact backup and live hashes.

Use --apply to restore workspace files. The installed Codex skill is checked and
restored separately from installed-skill-before if filesystem permission allows.
The 54 runtime and test evidence are retained for diagnosis, never deleted.
"""
from pathlib import Path
import json,hashlib,shutil,sys
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=load(O/'before.json');a=load(O/'after.json')
assert all(sha(O/'before'/f)==h for f,h in b['files'].items()),'Backup changed'
assert all(sha(R/f)==h for f,h in a['files'].items()),'Later live changes: separate before rollback'
assert all(sha(R/f)==h for f,h in a['new_file_hashes'].items()),'New files changed'
if '--apply' in sys.argv:
 for f in b['files']:shutil.copy2(O/'before'/f,R/f)
 # Unused new modules remain present; old pointers do not load their new policy.
 print('Workspace restored to',b['release'],'; restore installed skill from',O/'installed-skill-before')
else:print('Verified rollback preview:',b['release'],'files',len(b['files']),'; no writes')
