from pathlib import Path
import json,hashlib,shutil,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
B=read(OUT/'before-manifest.json');P=read(OUT/'candidate-active.json');C=read(OUT/'candidate-manifest.json');H=read(OUT/'host-chain.json')
assert sha(ROOT/'.opencode/liuren-active.json')==B['live']['.opencode/liuren-active.json']
for rel,digest in B['runtime'].items():assert sha(ROOT/B['parentRuntime']/rel)==digest,rel
for rel,digest in C['runtime'].items():assert sha(OUT/'candidate-runtime'/rel)==digest,rel
for group in [P['workflowImplementation'],read(OUT/'candidate-runtime/loader-contract.json')['sourceHashes'],P['bookRetrieval']['files']]:
 for rel,digest in group.items():assert sha(ROOT/rel)==digest,rel
assert H['finished'] and H['exitCode']==0 and not H['failures'] and not H['realModelCalled']
assert H['childModelAndHighVerified'] and H['hostKind']=='installed-desktop-server' and H['state']['child_pages']>0
assert H['candidateRuntimeSha256']==C['runtime']
for rel,digest in H['implementationSha256'].items():assert sha(ROOT/rel)==digest,rel
node=(OUT/'node-tests.log').read_text('utf-8-sig');assert re.search(r'# fail 0\b',node);passed=int(re.search(r'# pass (\d+)',node)[1]);assert passed>=137
py=(OUT/'python-tests.log').read_text('utf-8-sig');assert py.rstrip().endswith('OK');assert 'Ran 25 tests' in py
assert all(x['accepted'] and x['byteEquivalentContent'] for x in read(OUT/'historical-regression.json')['results'])
M=read(OUT/'candidate-runtime/manifest.json');assert M['version']==P['methodVersion']==hashlib.sha256(json.dumps(M['files'],sort_keys=True).encode()).hexdigest()
assert M['adjudication']['outputSchema']==P['adjudication']['outputSchema']=='free-text-or-json-object'
for rel,digest in M['files'].items():assert sha(OUT/'candidate-runtime'/rel)==digest,rel
A=read(ROOT/'.opencode/oh-my-opencode-slim.jsonc')['agents']['liuren-adjudicator'];assert A['model']=='deepseek/deepseek-flash' and A['variant']=='high'
config=read(ROOT/'opencode.json');assert any(P['runtime'] in k.replace('\\','/') and v=='allow' for k,v in config['agent']['liuren']['permission']['read'].items())
dest=ROOT/P['runtime'];assert not dest.exists();shutil.copytree(OUT/'candidate-runtime',dest)
C['live']={rel:sha(ROOT/rel) for rel,digest in B['live'].items() if sha(ROOT/rel)!=digest}
(OUT/'candidate-manifest.json').write_text(json.dumps(C,ensure_ascii=False,indent=2)+'\n','utf-8')
tmp=ROOT/'.opencode/liuren-active.json.handoff-installing';assert not tmp.exists();shutil.copyfile(OUT/'candidate-active.json',tmp);tmp.replace(ROOT/'.opencode/liuren-active.json')
receipt={'release':P['release'],'previousRelease':B['parentRelease'],'runtime':P['runtime'],'live':{**C['live'],'.opencode/liuren-active.json':sha(ROOT/'.opencode/liuren-active.json')},'runtimeFiles':C['runtime'],'nodeTestsPassed':passed,'pythonTestsPassed':25,'externalModelCalled':False,'hostValidationScope':H['scope'],'hostEvidenceSha256':sha(OUT/'host-chain.json'),'fullSlimDispatchVerifiedThisTurn':True,'restartOpenCodeRequired':True,'oldRuntimeUnchanged':True,'professionalOutputFieldsEnforced':False}
(OUT/'activation-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({k:receipt[k] for k in ['release','nodeTestsPassed','pythonTestsPassed','oldRuntimeUnchanged','fullSlimDispatchVerifiedThisTurn']}))
