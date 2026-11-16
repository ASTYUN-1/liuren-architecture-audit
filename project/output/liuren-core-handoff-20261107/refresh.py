"""Refresh current local31 identities; never rewrite a frozen release."""
from pathlib import Path
import hashlib,json,os
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='')
p=load(ROOT/'.opencode/liuren-active.json');assert p['release']=='20261107-slim-31'
R=ROOT/p['runtime'];c=load(R/'loader-contract.json');m=load(R/'manifest.json')
c['sourceHashes']={rel:sha(ROOT/rel) for rel in c['sourceHashes']};dump(R/'loader-contract.json',c)
m['files']={rel:sha(R/rel) for rel in m['files']}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(R/'manifest.json',m)
p['methodVersion']=m['version'];p['files']={rel:sha(ROOT/'.opencode/skills'/rel) for rel in p['files']}
p['workflowImplementation']={rel:sha(ROOT/rel) for rel in p['workflowImplementation']}
p['bookRetrieval']['files']={rel:sha(ROOT/rel) for rel in p['bookRetrieval']['files']}
temp=ROOT/'.opencode/liuren-active.core31.tmp';dump(temp,p);os.replace(temp,ROOT/'.opencode/liuren-active.json')
before=load(OUT/'before.json');assert all(sha(ROOT/'runtime/liuren/20261107-slim-30'/rel)==h for rel,h in before['frozen30'].items())
a=load(OUT/'activation.json');a['after']={rel:sha(ROOT/rel) for rel in a['before']};a['frozen30Intact']=True
a['newFiles']=['tools/liuren-core-handoff.mjs','tools/tests/liuren-core-handoff.test.mjs']
dump(OUT/'activation.json',a)
print('Local31 hashes refreshed; frozen30 intact')
