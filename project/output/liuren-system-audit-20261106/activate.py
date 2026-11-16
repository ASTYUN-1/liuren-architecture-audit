"""Install immutable18 only after bound local evidence passes; no model calls."""
from pathlib import Path
import json,hashlib,shutil,re
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
B=read(OUT/'before-manifest.json');C=read(OUT/'candidate-manifest.json');p=read(OUT/'candidate-active.json')
assert sha(ROOT/'.opencode/liuren-active.json')==B['live']['.opencode/liuren-active.json'],'active changed after backup'
assert sha(OUT/'candidate-active.json')==C['activeSha256']
for base,items in [(ROOT,C['live']),(ROOT/B['parentRuntime'],B['runtime']),(OUT/'candidate-runtime',C['runtime'])]:
 for rel,digest in items.items():assert sha(base/rel)==digest,rel
m=read(OUT/'candidate-runtime/manifest.json');loader=read(OUT/'candidate-runtime/loader-contract.json')
assert m['release']==p['release']==loader['release']==B['newRelease']
assert m['adjudication']==loader['adjudication']==p['adjudication']
assert 'input-v2' in json.dumps(p['adjudication']) and 'output-v2' in json.dumps(p['adjudication'])
assert m['version']==p['methodVersion']==hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest()
for rel,digest in m['files'].items():assert sha(OUT/'candidate-runtime'/rel)==digest,rel
assert read(OUT/'candidate-runtime'/m['shenshaPolicyFile'])['release']==p['release']
for entries in [p['workflowImplementation'],loader['sourceHashes']]:
 for rel,digest in entries.items():assert sha(ROOT/rel)==digest,rel
assert not p['eventPositioning']['semanticRoleChecks'] and not p['eventPositioning']['actorReferenceRequired']
permission=read(ROOT/'opencode.json')['agent']['liuren']['permission']['read']
assert any(p['runtime'] in k.replace('\\','/') and v=='allow' for k,v in permission.items())
assert not any('/runtime/liuren/' in k.replace('\\','/') and p['release'] not in k and v=='allow' for k,v in permission.items())
cfg=read(ROOT/'.opencode/oh-my-opencode-slim.jsonc')['agents']['liuren-adjudicator']
assert cfg['model']=='deepseek/deepseek-flash' and cfg['variant']=='high' and cfg['options']['reasoningEffort']=='high'
host=read(OUT/'host-chain.json');wire=read(OUT/'current-wire.json')
assert host['finished'] and host['exitCode']==0 and not host['failures'] and host['loopbackOnly'] and not host['realModelCalled']
assert host['childModelAndHighVerified'] and host['state']['child_pages']>0
assert host['candidateRuntimeSha256']==C['runtime'],'host test ran another candidate'
assert sha(OUT/'synthetic-fixture.json')==host['fixtureSha256']
assert wire['exitCode']==0 and wire['loopbackOnlyProvider'] and not wire['realModelCalled']
for evidence in [host,wire]:
 for rel,digest in evidence['implementationSha256'].items():assert sha(ROOT/rel)==digest,rel
for req in wire['requests']:
 assert not req['referenceErrors']
 for t in req['tools']:assert '"$ref"' not in json.dumps(t['parameters'])
events=[json.loads(t) for t in (OUT/'host-cli.log').read_text(encoding='utf-8').splitlines() if t.startswith('{')]
tasks=[e for e in events if e.get('type')=='tool_use' and e.get('part',{}).get('tool')=='task']
assert len(tasks)==1 and tasks[0]['part']['state']['status']=='completed'
checks={}
for name in ['final-node-tests.log','additional-node-tests.log']:
 t=(OUT/name).read_text(encoding='utf-8-sig');n=re.search(r'pass (\d+)',t)
 assert n and int(n[1])>0 and re.search(r'fail 0\b',t),name
 checks[name]={'pass':int(n[1]),'sha256':sha(OUT/name)}
for name in ['method-loader-tests.log','material-scope-tests.log','single-method-tests.log','book-search-tests.log']:
 t=(OUT/name).read_text(encoding='utf-8-sig');assert re.search(r'\bOK(?: \(skipped=1\))?\s*$',t),name
 checks[name]={'sha256':sha(OUT/name)}
dest=(ROOT/p['runtime']).resolve();assert dest.is_relative_to((ROOT/'runtime/liuren').resolve()) and not dest.exists()
shutil.copytree(OUT/'candidate-runtime',dest)
for rel,digest in C['runtime'].items():assert sha(dest/rel)==digest,rel
tmp=ROOT/'.opencode/liuren-active.json.system-audit-installing';assert not tmp.exists()
shutil.copyfile(OUT/'candidate-active.json',tmp);tmp.replace(ROOT/'.opencode/liuren-active.json')
receipt={'release':p['release'],'previousRelease':B['parentRelease'],'runtime':p['runtime'],'methodVersion':p['methodVersion'],'runtimeFiles':C['runtime'],'live':{**C['live'],'.opencode/liuren-active.json':sha(ROOT/'.opencode/liuren-active.json')},'checks':checks,'hostEvidenceSha256':sha(OUT/'host-chain.json'),'wireEvidenceSha256':sha(OUT/'current-wire.json'),'websiteChanged':False,'externalModelCalled':False,'restartOpenCodeRequired':True}
(OUT/'activation-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'active':p['release'],'runtimeFiles':len(C['runtime']),'nodeTestsPassed':sum(c.get('pass',0) for c in checks.values()),'oldRuntimeUnchanged':True}))
