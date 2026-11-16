from pathlib import Path
import hashlib,json,os,shutil,sys
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((OUT/'local-fix.json').read_text('utf-8'))
assert all(sha(OUT/'before-fix'/rel)==h for rel,h in r['before'].items()),'Backup changed'
assert all(sha(ROOT/rel)==h for rel,h in r['after'].items()),'Files changed after repair; preserve and resolve manually'
if '--apply' not in sys.argv:print('Preview: restore local interface and 26 pointer; no runtime deleted. Use --apply to restore.')
else:
 for rel in [k for k in r['before'] if k!='.opencode/liuren-active.json']+['.opencode/liuren-active.json']:
  p=ROOT/rel;tmp=p.with_name(p.name+'.rollback27.tmp');shutil.copyfile(OUT/'before-fix'/rel,tmp);os.replace(tmp,p)
 print('Restored local 26 configuration; restart OpenCode and start a new session.')
