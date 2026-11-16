"""Verify reviewed candidate; install runtime without overwrites; switch pointer last."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def install(src,dst):
 dst.parent.mkdir(parents=True,exist_ok=True);tmp=dst.with_name(dst.name+'.schema11-installing')
 if tmp.exists():raise ValueError('Existing install temp: '+str(tmp))
 shutil.copyfile(src,tmp);tmp.replace(dst)
before=read(OUT/'before-manifest.json');candidate=read(OUT/'candidate-manifest.json');checks=read(OUT/'candidate-checks.json')
if checks['status']!='passed' or checks['release']!=candidate['release']:raise ValueError('Candidate checks required')
if checks['candidateManifestSha256']!=sha(OUT/'candidate-manifest.json') or checks['testLogSha256']!=sha(OUT/'candidate-tests.log'):raise ValueError('Candidate or test evidence changed since review')
if checks['wireCaptureSha256']!=sha(OUT/'fixed-wire.json'):raise ValueError('Actual outbound schema capture changed since review')
for rel,digest in before['runtime'].items():
 if sha(ROOT/before['parentRuntime']/rel)!=digest:raise ValueError('Frozen parent changed: '+rel)
for rel,digest in candidate['live'].items():
 if sha(OUT/'candidate-live'/rel)!=digest:raise ValueError('Candidate bytes changed: '+rel)
 if rel in before['live'] and sha(ROOT/rel) not in [before['live'][rel],digest]:raise ValueError('Unexpected later edit: '+rel)
 if rel not in before['live'] and (ROOT/rel).exists() and sha(ROOT/rel)!=digest:raise ValueError('Conflicting new file: '+rel)
for rel,digest in candidate['runtime'].items():
 if sha(OUT/'candidate-runtime'/rel)!=digest:raise ValueError('Runtime candidate changed: '+rel)
pointer=read(OUT/'candidate-live/.opencode/liuren-active.json');dest=ROOT/pointer['runtime']
if dest.exists():raise ValueError('Refusing runtime overwrite')
shutil.copytree(OUT/'candidate-runtime',dest)
paths=[p for p in candidate['live'] if p!='.opencode/liuren-active.json']+['.opencode/liuren-active.json']
installed=[]
try:
 for rel in paths:install(OUT/'candidate-live'/rel,ROOT/rel);installed.append(rel)
 for rel in paths:
  if sha(ROOT/rel)!=candidate['live'][rel]:raise ValueError('Installed bytes mismatch '+rel)
except Exception:
 for rel in reversed(installed):
  if rel in before['live']:install(OUT/'before'/rel,ROOT/rel)
 raise
receipt={'release':pointer['release'],'previousRelease':before['parentRelease'],'runtime':pointer['runtime'],'methodVersion':pointer['methodVersion'],
 'files':{r:sha(ROOT/r) for r in paths},'runtimeFiles':{r.relative_to(dest).as_posix():sha(r) for r in dest.rglob('*') if r.is_file()},
 'externalModelCalled':False,'websiteChanged':False,'restartOpenCodeRequired':True}
(OUT/'activation-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'active','release':receipt['release'],'files':len(paths)},ensure_ascii=False))
