"""Install without overwriting a release; verify all bytes before switching active."""
from pathlib import Path
import json,hashlib,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
B=read(OUT/'before-manifest.json');C=read(OUT/'candidate-manifest.json')
log=(OUT/'preflight-tests.log').read_text('utf-8-sig');assert 'pass 118' in log and 'fail 0' in log,'preflight tests'
assert sha(ROOT/'.opencode/liuren-active.json')==B['live']['.opencode/liuren-active.json'],'active changed'
for rel,d in B['runtime'].items():assert sha(ROOT/B['parentRuntime']/rel)==d,rel
for rel,d in C['live'].items():assert sha(ROOT/rel)==d,rel
for rel,d in C['runtime'].items():assert sha(OUT/'candidate-runtime'/rel)==d,rel
assert sha(OUT/'candidate-active.json')==C['activeSha256']
p=read(OUT/'candidate-active.json');dest=(ROOT/p['runtime']).resolve()
manifest=read(OUT/'candidate-runtime/manifest.json')
assert read(OUT/'candidate-runtime'/manifest['shenshaPolicyFile'])['release']==p['release'],'policy/release mismatch'
wire=read(OUT/'current-wire.json');assert wire['exitCode']==0 and wire['realModelCalled'] is False
for rel,d in wire['implementationSha256'].items():assert sha(ROOT/rel)==d,'stale wire capture: '+rel
assert dest.is_relative_to((ROOT/'runtime/liuren').resolve()) and not dest.exists()
shutil.copytree(OUT/'candidate-runtime',dest)
for rel,d in C['runtime'].items():assert sha(dest/rel)==d,rel
tmp=ROOT/'.opencode/liuren-active.json.event14-installing';assert not tmp.exists()
shutil.copyfile(OUT/'candidate-active.json',tmp);tmp.replace(ROOT/'.opencode/liuren-active.json')
receipt={'release':p['release'],'previousRelease':B['parentRelease'],'runtime':p['runtime'],'methodVersion':p['methodVersion'],'live':{**C['live'],'.opencode/liuren-active.json':sha(ROOT/'.opencode/liuren-active.json')},'runtimeFiles':C['runtime'],'preflightTestLogSha256':sha(OUT/'preflight-tests.log'),'externalModelCalled':False,'websiteChanged':False,'restartOpenCodeRequired':True}
(OUT/'activation-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'active','release':p['release'],'runtimeFiles':len(C['runtime'])}))
