from pathlib import Path
import json,hashlib,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
B=load(OUT/'before-manifest.json');p=load(OUT/'candidate-active.json');H=load(OUT/'host-chain.json');C=load(OUT/'candidate-manifest.json')
assert sha(ROOT/'.opencode/liuren-active.json')==B['live']['.opencode/liuren-active.json']
assert H['finished'] and H['exitCode']==0 and not H['failures'] and H['childModelAndHighVerified']
assert H['candidateRuntimeSha256']==C['runtime']
for rel,d in B['runtime'].items():assert sha(ROOT/B['parentRuntime']/rel)==d,rel
for rel,d in C['runtime'].items():assert sha(OUT/'candidate-runtime'/rel)==d,rel
for rel,d in H['implementationSha256'].items():assert sha(ROOT/rel)==d,rel
for group in [p['workflowImplementation'],load(OUT/'candidate-runtime/loader-contract.json')['sourceHashes'],p['bookRetrieval']['files']]:
 for rel,d in group.items():assert sha(ROOT/rel)==d,rel
assert 'pass 141' in (OUT/'regression-tests.log').read_text('utf-8-sig')
dest=ROOT/p['runtime'];assert not dest.exists();shutil.copytree(OUT/'candidate-runtime',dest)
tmp=ROOT/'.opencode/liuren-active.json.usage-installing';assert not tmp.exists();shutil.copyfile(OUT/'candidate-active.json',tmp);tmp.replace(ROOT/'.opencode/liuren-active.json')
receipt={'release':p['release'],'previousRelease':B['parentRelease'],'oldRuntimeUnchanged':True,'restartOpenCodeRequired':True,'externalModelValidated':False,'hostEvidence':H['scope'],'live':{rel:sha(ROOT/rel) for rel in B['live']},'runtimeFiles':C['runtime']}
(OUT/'activation-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'release':p['release'],'oldRuntimeUnchanged':True}))
