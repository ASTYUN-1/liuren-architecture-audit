"""Install the new frozen runtime without overwrite, then switch active atomically."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
before=read(OUT/'before-manifest.json');cm=read(OUT/'candidate-manifest.json');check=read(OUT/'candidate-checks.json')
assert check['status']=='passed' and check['release']==cm['release']
for field,rel in [('candidateManifestSha256','candidate-manifest.json'),('testLogSha256','candidate-tests.log'),('wireCaptureSha256','current-wire.json')]:assert sha(OUT/rel)==check[field],rel
assert sha(ROOT/'.opencode/liuren-active.json')==before['live']['.opencode/liuren-active.json'],'Active changed since backup'
for rel,d in before['runtime'].items():assert sha(ROOT/before['parentRuntime']/rel)==d,rel
for rel,d in cm['live'].items():assert sha(ROOT/rel)==d,rel
for rel,d in cm['runtime'].items():assert sha(OUT/'candidate-runtime'/rel)==d,rel
assert sha(OUT/'candidate-active.json')==cm['activeSha256']
p=read(OUT/'candidate-active.json');dest=(ROOT/p['runtime']).resolve()
assert dest.is_relative_to((ROOT/'runtime/liuren').resolve()) and not dest.exists()
shutil.copytree(OUT/'candidate-runtime',dest)
for rel,d in cm['runtime'].items():assert sha(dest/rel)==d,rel
tmp=ROOT/'.opencode/liuren-active.json.flow12-installing';assert not tmp.exists()
shutil.copyfile(OUT/'candidate-active.json',tmp);tmp.replace(ROOT/'.opencode/liuren-active.json')
receipt={'release':p['release'],'previousRelease':before['parentRelease'],'runtime':p['runtime'],'methodVersion':p['methodVersion'],'files':{**cm['live'],'.opencode/liuren-active.json':sha(ROOT/'.opencode/liuren-active.json')},'runtimeFiles':cm['runtime'],'externalModelCalled':False,'websiteChanged':False,'restartOpenCodeRequired':True}
(OUT/'activation-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps({'status':'active','release':p['release'],'files':len(receipt['files'])},ensure_ascii=False))
