"""Preview by default; restore only this task's files, preserving later edits."""
from pathlib import Path
import hashlib,json,os,shutil,sys
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=json.loads((OUT/'activation.json').read_text('utf-8'))
assert all(sha(OUT/'before'/rel)==h for rel,h in a['before'].items()),'Backup changed'
assert all(sha(ROOT/rel)==h for rel,h in a['after'].items()),'Later edits detected; preserve them before rollback'
if '--apply' not in sys.argv:print('Preview: restore local30 configuration and changed sources; retain runtime31, new helper/tests and evidence. Add --apply to restore.')
else:
 for rel in [r for r in a['before'] if r!='.opencode/liuren-active.json']+['.opencode/liuren-active.json']:
  dest=ROOT/rel;temp=dest.with_name(dest.name+'.rollback31.tmp');shutil.copyfile(OUT/'before'/rel,temp);os.replace(temp,dest)
 print('Restored local30. Restart OpenCode to reload. New unreferenced helper/tests and runtime31 retained for evidence.')
