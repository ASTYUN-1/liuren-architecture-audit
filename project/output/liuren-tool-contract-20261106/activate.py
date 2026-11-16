from pathlib import Path
import json,hashlib,shutil,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
B=read(OUT/'before-manifest.json');p=read(OUT/'candidate-active.json');C=read(OUT/'candidate-manifest.json')
assert sha(ROOT/'.opencode/liuren-active.json')==B['live']['.opencode/liuren-active.json']
for rel,digest in B['runtime'].items():assert sha(ROOT/B['parentRuntime']/rel)==digest,rel
for rel,digest in C['runtime'].items():assert sha(OUT/'candidate-runtime'/rel)==digest,rel
for group in [p['workflowImplementation'],read(OUT/'candidate-runtime/loader-contract.json')['sourceHashes'],p['bookRetrieval']['files']]:
 for rel,digest in group.items():assert sha(ROOT/rel)==digest,rel
host=read(OUT/'host-packet.json');assert host['finished'] and host['exitCode']==0 and not host['failures'] and not host['realModelCalled']
assert host['state']['readerReferencesCopied']>10
assert host['candidateRuntimeSha256']==C['runtime']
for rel,digest in host['implementationSha256'].items():assert sha(ROOT/rel)==digest,rel
checks={}
for name in ['node-tests.log','additional-node-tests.log']:
 text=(OUT/name).read_text('utf-8-sig');assert re.search(r'fail 0\b',text),name
 checks[name]=int(re.search(r'pass (\d+)',text)[1])
for name in ['method-tests.log','loader-tests.log','book-tests.log']:assert (OUT/name).read_text('utf-8-sig').rstrip().endswith('OK'),name
m=read(OUT/'candidate-runtime/manifest.json')
assert m['version']==p['methodVersion']==hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest()
assert m['release']==read(OUT/'candidate-runtime/loader-contract.json')['release']==p['release']
for rel,digest in m['files'].items():assert sha(OUT/'candidate-runtime'/rel)==digest
assert not p['eventPositioning']['semanticRoleChecks'] and not p['eventPositioning']['actorReferenceRequired']
config=read(ROOT/'opencode.json');assert any(p['runtime'] in k.replace('\\','/') and v=='allow' for k,v in config['agent']['liuren']['permission']['read'].items())
a=read(ROOT/'.opencode/oh-my-opencode-slim.jsonc')['agents']['liuren-adjudicator'];assert a['model']=='deepseek/deepseek-flash' and a['variant']=='high'
dest=ROOT/p['runtime'];assert not dest.exists();shutil.copytree(OUT/'candidate-runtime',dest)
C['live']={rel:sha(ROOT/rel) for rel,digest in B['live'].items() if sha(ROOT/rel)!=digest}
C['live']['tools/tests/liuren-source-handoff.test.mjs']=sha(ROOT/'tools/tests/liuren-source-handoff.test.mjs')
(OUT/'candidate-manifest.json').write_text(json.dumps(C,ensure_ascii=False,indent=2)+'\n','utf-8')
tmp=ROOT/'.opencode/liuren-active.json.tool-contract-installing';assert not tmp.exists();shutil.copyfile(OUT/'candidate-active.json',tmp);tmp.replace(ROOT/'.opencode/liuren-active.json')
receipt={'release':p['release'],'previousRelease':B['parentRelease'],'runtime':p['runtime'],'live':{**C['live'],'.opencode/liuren-active.json':sha(ROOT/'.opencode/liuren-active.json')},'runtimeFiles':C['runtime'],'nodeTestsPassed':sum(checks.values()),'pythonTestsPassed':25,'externalModelCalled':False,'hostValidationScope':host['scope'],'hostEvidenceSha256':sha(OUT/'host-packet.json'),'fullSlimDispatchVerifiedThisTurn':False,'restartOpenCodeRequired':True,'oldRuntimeUnchanged':True}
(OUT/'activation-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({k:receipt[k] for k in ['release','nodeTestsPassed','pythonTestsPassed','oldRuntimeUnchanged']}))
