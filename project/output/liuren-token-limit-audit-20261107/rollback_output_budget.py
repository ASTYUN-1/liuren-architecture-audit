"""Guarded local rollback; retain diagnostic evidence and new runtime."""
from pathlib import Path
import hashlib,json,os,shutil,sys
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((OUT/'output-budget-activation.json').read_text('utf-8'))
assert all(sha(OUT/'before-output-budget'/rel)==h for rel,h in r['before'].items()),'Backup changed'
assert all(sha(ROOT/rel)==h for rel,h in r['after'].items()),'Later edits detected; preserve them before rollback'
if '--apply' not in sys.argv:print('Preview: restore local29 sources/configuration; retain runtime30 and evidence. Add --apply to restore.')
else:
 for rel in [k for k in r['before'] if k!='.opencode/liuren-active.json']+['.opencode/liuren-active.json']:
  dest=ROOT/rel;temp=dest.with_name(dest.name+'.rollback30.tmp');shutil.copyfile(OUT/'before-output-budget'/rel,temp);os.replace(temp,dest)
 print('Restored local29. Restart OpenCode to reload.')
