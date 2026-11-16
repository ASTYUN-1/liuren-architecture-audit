"""Preview by default. Restore exact release files only; retain all runtime packages."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text('utf-8-sig'))
arg=argparse.ArgumentParser();arg.add_argument('--apply',action='store_true');arg.add_argument('--include-global',action='store_true');args=arg.parse_args()
a=load(OUT/'activation.json');b=load(OUT/'before.json');pairs=[]
for rel,expected in a['after'].items():
    src=OUT/'before'/rel;dst=(ROOT/rel).resolve();assert dst.is_relative_to(ROOT)
    assert sha(src)==b['files'][rel]
    if sha(dst)!=expected:raise SystemExit('Changed after release; refusing overwrite: '+rel)
    pairs.append((src,dst))
if args.include_global:
    for rel,expected in a['installedSkillAfter'].items():
        src=OUT/'before/installed-skill'/rel;dst=Path('C:/Users/QLMa_/.codex/skills/daliuren-codex')/rel
        if sha(dst)!=expected:raise SystemExit('Installed skill changed; refusing overwrite: '+rel)
        assert sha(src)==sha(OUT/'before/integrations/codex/daliuren-codex'/rel)
        pairs.append((src,dst))
pairs.sort(key=lambda pair:pair[1].name=='liuren-active.json')
print(('APPLY' if args.apply else 'PREVIEW')+': '+str(len(pairs))+' files; retain new runtime, evidence and historical packets.')
if args.apply:
    for src,dst in pairs:dst.write_bytes(src.read_bytes())
    print('Restored local32. Restart OpenCode before new judgments.')
