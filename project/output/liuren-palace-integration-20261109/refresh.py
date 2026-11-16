from pathlib import Path
import json,hashlib,os
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=load(ROOT/'.opencode/liuren-active.json');assert p['release']=='20261109-palace-strength-34'
r=ROOT/p['runtime'];evidence=(OUT/'current-wire.json').relative_to(ROOT).as_posix()
wire=load(ROOT/evidence);assert wire['exitCode']==0 and wire['requests'] and wire['realModelCalled'] is False
assert all(sha(ROOT/rel)==h for rel,h in wire['implementationSha256'].items())
for file in ['loader-contract.json','manifest.json']:
 d=load(r/file);d['computeInterface'].update(transportEvidence=evidence,transportValidation='fresh OpenCode outbound schema to loopback synthetic provider; strength execution separately tested')
 if file=='loader-contract.json':
  for rel in ['tools/liuren-palace-strength.mjs','tools/liuren-strength-engine.mjs','tools/liuren-strength-rules.mjs','tools/liuren-strength-profile.json','tools/liuren-codex.mjs']:d['sourceHashes'][rel]=sha(ROOT/rel)
  d['sourceHashes']={rel:sha(ROOT/rel) for rel in d['sourceHashes']}
 dump(r/file,d)
m=load(r/'manifest.json');m['files']={rel:sha(r/rel) for rel in m['files']};m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(r/'manifest.json',m)
p['methodVersion']=m['version'];p['workflowImplementation']={rel:sha(ROOT/rel) for rel in p['workflowImplementation']}
p['computeInterface'].update(transportEvidence=evidence,strengthAction=True)
tmp=ROOT/'.opencode/liuren-active.palace34.tmp';dump(tmp,p);os.replace(tmp,ROOT/'.opencode/liuren-active.json')
a=load(OUT/'activation.json');a['methodVersion']=m['version'];dump(OUT/'activation.json',a)
print('Refreshed candidate34 with current schema capture')
