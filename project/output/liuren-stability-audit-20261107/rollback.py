from pathlib import Path
import hashlib,json,os,shutil,sys
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((OUT/'local-fix.json').read_text('utf-8'))
assert all(sha(OUT/'before-fix'/rel)==h for rel,h in r['before'].items()),'Backup changed'
assert all(sha(ROOT/rel)==h for rel,h in r['after'].items()),'Later edits detected; preserve them before rollback'
if '--apply' not in sys.argv:print('Preview: restore local 28 code/config and MCP policy, pointer last. New files and runtimes retained. Use --apply to restore.')
else:
 for rel in [k for k in r['before'] if k!='.opencode/liuren-active.json']+['.opencode/liuren-active.json']:
  dest=ROOT/rel;tmp=dest.with_name(dest.name+'.rollback29.tmp');shutil.copyfile(OUT/'before-fix'/rel,tmp);os.replace(tmp,dest)
 print('Restored local release 28. Restart OpenCode to reload.')
