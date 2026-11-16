"""Bind natural-language quantity recognition in a fresh immutable build."""
from pathlib import Path
import hashlib,json,os,shutil
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
enc=lambda d:(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=load(R/'.opencode/liuren-active.json');OLD='20261111-numeric-answer-47';NEW=OLD+'-final'
assert p['release']==OLD
frozen={f.relative_to(R).as_posix():sha(f) for f in (R/p['runtime']).rglob('*') if f.is_file()}
runtime=R/'runtime/liuren'/NEW;assert not runtime.exists();shutil.copytree(R/p['runtime'],runtime)
pending={}
for rel in ['opencode.json','README.md','目录总索引.md']:
 pending[rel]=(R/rel).read_text('utf-8').replace('runtime/liuren/'+OLD,'runtime/liuren/'+NEW).replace('指向 `'+OLD+'`','指向 `'+NEW+'`').encode()
current_sha=lambda f:hashlib.sha256(pending[f]).hexdigest() if f in pending else sha(R/f)
for name in ['loader-contract.json','references/shensha-policy.json','references/shensha-authority-evidence.json','references/confirmed-policy-register.json','reading-route.json']:
 d=load(runtime/name);d['release']=NEW
 if name=='loader-contract.json':
  d['parentRelease']=OLD;d['sourceHashes']={f:current_sha(f) for f in d['sourceHashes']}
 (runtime/name).write_bytes(enc(d))
m=load(runtime/'manifest.json');m.update(release=NEW,parentRelease=OLD)
if 'bookRetrieval' in m:m['bookRetrieval']['compatibleMethodRelease']=NEW
m['files']={f:sha(runtime/f) for f in m['files']};m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest()
(runtime/'manifest.json').write_bytes(enc(m))
p.update(release=NEW,runtime=runtime.relative_to(R).as_posix(),previousRelease=OLD,methodVersion=m['version'])
p['bookRetrieval']['compatibleMethodRelease']=NEW;p['workflowImplementation']={f:current_sha(f) for f in p['workflowImplementation']}
pending['.opencode/liuren-active.json']=enc(p)
for rel in sorted(pending,key=lambda f:f=='.opencode/liuren-active.json'):
 target=R/rel;tmp=target.with_name(target.name+'.final47.tmp');tmp.write_bytes(pending[rel]);os.replace(tmp,target)
assert all(sha(R/f)==h for f,h in frozen.items())
before=load(O/'before.json');assert all(sha(R/f)==h for f,h in before['frozen'].items())
(O/'final.json').write_bytes(enc({'release':NEW,'runtime':p['runtime'],'frozen46_unchanged':True,'interim47_unchanged':True,'interim47_hashes':frozen,'files':{f:sha(R/f) for f in list(before['files'])+['tools/liuren-flow-control.mjs','tools/tests/liuren-flow-control.test.mjs']}}))
print('Activated',NEW)
