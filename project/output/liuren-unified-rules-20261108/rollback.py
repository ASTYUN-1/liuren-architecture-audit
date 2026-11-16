"""Preview by default; restore only exact recorded post-update files, retaining new runtime."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text('utf-8-sig'))
arg=argparse.ArgumentParser();arg.add_argument('--apply',action='store_true');arg.add_argument('--include-global',action='store_true');args=arg.parse_args()
a=load(OUT/'activation.json');b=load(OUT/'before.json');pairs=[]
for rel,expected in a['after'].items():
 dst=(ROOT/rel).resolve();assert dst.is_relative_to(ROOT)
 src=OUT/'before'/rel;assert sha(src)==b['files'][rel]
 if sha(dst)!=expected:raise SystemExit('Changed since release; refusing to overwrite: '+rel)
 pairs.append((src,dst))
if args.include_global:
 for rel,expected in a['globalSkillAfter'].items():
  src=OUT/'before/global-skill'/rel;dst=Path('C:/Users/QLMa_/.codex/skills/daliuren-codex')/rel
  assert sha(src)==b['globalSkill'][rel]
  if sha(dst)!=expected:raise SystemExit('Installed skill changed; refusing overwrite: '+rel)
  pairs.append((src,dst))
pairs.sort(key=lambda pair:pair[1].name=='liuren-active.json')
print(('APPLY' if args.apply else 'PREVIEW')+': '+str(len(pairs))+' exact backed-up files; keep new runtime/evidence and all historical packets.')
if args.apply:
 for src,dst in pairs:dst.write_bytes(src.read_bytes())
 print('Restored prior local files and pointer. Restart OpenCode before new tasks.')
