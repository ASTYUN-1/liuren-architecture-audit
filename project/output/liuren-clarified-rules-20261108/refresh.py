"""Refresh hashes after an in-progress local33 repair; pointer replaced last."""
from pathlib import Path
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text('utf-8-sig'))
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=load(ROOT/'.opencode/liuren-active.json');assert p['release']=='20261108-clarified-33'
r=ROOT/p['runtime'];b=load(OUT/'before.json')
assert all(sha(ROOT/'runtime/liuren'/b['release']/rel)==h for rel,h in b['frozen32'].items())
assert all(sha(ROOT/rel)==h for rel,h in b['sourceBooks'].items())
c=load(r/'loader-contract.json');c['sourceHashes']={rel:sha(ROOT/rel) for rel in c['sourceHashes']};dump(r/'loader-contract.json',c)
m=load(r/'manifest.json');m['files']={rel:sha(r/rel) for rel in m['files']};m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(r/'manifest.json',m)
p['methodVersion']=m['version'];p['files']={rel:sha(ROOT/'.opencode/skills'/rel) for rel in p['files']}
p['workflowImplementation']={rel:sha(ROOT/rel) for rel in p['workflowImplementation']}
p['bookRetrieval']['files']={rel:sha(ROOT/rel) for rel in p['bookRetrieval']['files']}
tmp=ROOT/'.opencode/liuren-active.clarified33.tmp';dump(tmp,p);os.replace(tmp,ROOT/'.opencode/liuren-active.json')
a=load(OUT/'activation.json');a['methodVersion']=m['version'];a['after']={rel:sha(ROOT/rel) for rel in a['after']}
a['installedSkillAfter']={rel:sha(Path('C:/Users/QLMa_/.codex/skills/daliuren-codex')/rel) for rel in ['SKILL.md','references/host.md']};dump(OUT/'activation.json',a)
print('Refreshed local33 hashes; pointer published last.')
