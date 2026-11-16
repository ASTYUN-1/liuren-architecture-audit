"""Restore the previous local release only if all current files still match this patch."""
from pathlib import Path
import argparse,hashlib,json,os
parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=load(OUT/'before.json');after=load(OUT/'after.json')
assert load(ROOT/'.opencode/liuren-active.json')['release']=='20261111-book-logic-41'
targets=[]
for rel,h in before['files'].items():
 dest=(ROOT/rel).resolve();backup=(OUT/'before'/rel).resolve()
 assert dest.is_relative_to(ROOT) and backup.is_relative_to(OUT/'before')
 assert sha(backup)==h,'Backup changed: '+rel
 assert sha(dest)==after['files'][rel],'Later edits exist; preserve them: '+rel
 targets.append((rel,dest,backup))
if args.check:print('Rollback guards passed:',len(targets),'files; no writes')
else:
 for rel,dest,backup in sorted(targets,key=lambda row:row[0]=='.opencode/liuren-active.json'):
  tmp=dest.with_name(dest.name+'.book41-rollback.tmp')
  with tmp.open('xb') as f:f.write(backup.read_bytes())
  os.replace(tmp,dest)
 assert all(sha(ROOT/p)==h for p,h in before['files'].items())
 print('Restored40; restart OpenCode. New runtime, source evidence and research candidates retained for history.')
