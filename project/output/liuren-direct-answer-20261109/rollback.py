"""Restore this release's exact backups only if no subsequent edits would be lost."""
from pathlib import Path
import argparse,hashlib,json,os
parser=argparse.ArgumentParser()
parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[2])
parser.add_argument('--check',action='store_true')
args=parser.parse_args()
root=args.root.resolve();out=root/'output/liuren-direct-answer-20261109'
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=load(out/'before.json');after=load(out/'after.json')
assert load(root/'.opencode/liuren-active.json')['release']=='20261109-direct-answer-40','Active release has changed; do not overwrite it'
targets=[]
for rel,h in before['files'].items():
    dest=(root/rel).resolve();backup=(out/'before'/rel).resolve()
    assert dest.is_relative_to(root) and backup.is_relative_to(out/'before')
    assert sha(backup)==h,'Backup changed: '+rel
    assert sha(dest)==after['files'][rel],'Later edit detected; preserve it: '+rel
    targets.append((rel,dest,backup))
if args.check:
    print('Rollback check passed:',len(targets),'files; no writes')
else:
    # Publish the old active pointer last; retain the new runtime and all run artifacts.
    for rel,dest,backup in sorted(targets,key=lambda row:row[0]=='.opencode/liuren-active.json'):
        tmp=dest.with_name(dest.name+'.direct-answer-rollback.tmp')
        with tmp.open('xb') as handle:handle.write(backup.read_bytes())
        os.replace(tmp,dest)
    assert all(sha(root/rel)==h for rel,h in before['files'].items())
    print('Restored previous local release; restart OpenCode. All task artifacts retained.')
