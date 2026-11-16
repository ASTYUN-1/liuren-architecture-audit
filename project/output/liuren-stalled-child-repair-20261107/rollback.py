from pathlib import Path
import hashlib,json,os,shutil,sys
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
record=json.loads((OUT/'local-fix.json').read_text('utf-8'))
assert all(sha(OUT/'before-fix'/rel)==h for rel,h in record['before'].items()),'Backup changed'
assert all(sha(ROOT/rel)==h for rel,h in record['after'].items()),'Files changed since repair; preserve later edits before rollback'
if '--apply' not in sys.argv:print('Preview: restore local release 27 and prior implementation; no runtime deleted. Pass --apply to restore.')
else:
 for rel in [k for k in record['before'] if k!='.opencode/liuren-active.json']+['.opencode/liuren-active.json']:
  dest=ROOT/rel;tmp=dest.with_name(dest.name+'.rollback28.tmp');shutil.copyfile(OUT/'before-fix'/rel,tmp);os.replace(tmp,dest)
 print('Restored local release 27; restart OpenCode to load the previous implementation.')
