"""Restore backed-up local files; retain both frozen runtimes. --check is read-only."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
before=read(OUT/'before-manifest.json');after=read(OUT/'activation-receipt.json')
for rel,d in after['files'].items():assert sha(ROOT/rel)==d,'Later edit; rollback refused: '+rel
for rel,d in before['live'].items():assert sha(OUT/'before'/rel)==d,'Backup changed: '+rel
for rel,d in before['runtime'].items():assert sha(ROOT/before['parentRuntime']/rel)==d,'Parent changed: '+rel
if args.check:print(json.dumps({'status':'rollback-ready','restoreRelease':before['parentRelease'],'restoreFiles':len(before['live'])}));raise SystemExit()
paths=[r for r in before['live'] if r!='.opencode/liuren-active.json']+['.opencode/liuren-active.json']
for rel in paths:
 dst=(ROOT/rel).resolve();assert dst.is_relative_to(ROOT.resolve())
 tmp=dst.with_name(dst.name+'.flow12-rollback');assert not tmp.exists()
 shutil.copyfile(OUT/'before'/rel,tmp);tmp.replace(dst)
for rel in before['newFiles']:
 target=(ROOT/rel).resolve();assert target.is_relative_to(ROOT.resolve())
 if target.is_file():target.unlink()
print(json.dumps({'status':'restored','release':before['parentRelease'],'runtimesRetained':True}))
