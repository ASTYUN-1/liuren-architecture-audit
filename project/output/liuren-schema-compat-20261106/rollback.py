"""Restore 10 local files, retain both frozen runtimes; --check never writes."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text('utf-8-sig'))
args=argparse.ArgumentParser();args.add_argument('--check',action='store_true');args=args.parse_args()
before=read(OUT/'before-manifest.json');after=read(OUT/'activation-receipt.json')
for rel,d in after['files'].items():
 if not (ROOT/rel).is_file() or sha(ROOT/rel)!=d:raise ValueError('Later edit; rollback refused: '+rel)
for rel,d in before['live'].items():
 if sha(OUT/'before'/rel)!=d:raise ValueError('Backup changed: '+rel)
for rel,d in before['runtime'].items():
 if sha(ROOT/before['parentRuntime']/rel)!=d:raise ValueError('Frozen parent changed: '+rel)
if args.check:print(json.dumps({'status':'rollback-ready','restoreRelease':before['parentRelease'],'restoreFiles':len(before['live'])}));raise SystemExit()
for rel in [r for r in before['live'] if r!='.opencode/liuren-active.json']+['.opencode/liuren-active.json']:
 dst=ROOT/rel;tmp=dst.with_name(dst.name+'.schema11-rollback')
 if tmp.exists():raise ValueError('Existing rollback temp')
 shutil.copyfile(OUT/'before'/rel,tmp);tmp.replace(dst)
# Remove only explicitly registered new files, already checked against installed bytes.
for rel in before['newFiles']:
 target=(ROOT/rel).resolve()
 if not target.is_relative_to(ROOT.resolve()):raise ValueError('Invalid new file target')
 if target.is_file():target.unlink()
print(json.dumps({'status':'restored','release':before['parentRelease'],'runtimesRetained':True}))
