"""Refresh this unpublished consolidation after verified repairs; never touch its parent."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
enc=lambda d:(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf8')
b=load(O/'before.json');p=load(R/'.opencode/liuren-active.json')
assert p['release']=='20261112-consistency-52'
assert all(sha(R/f)==h for f,h in b['frozen'].items()),'Parent bytes changed'
T=R/p['runtime'];m=load(T/'manifest.json')
p['computeInterface']['transportEvidence']='output/liuren-global-consistency-52/native-schema.json'
p['computeInterface']['transportValidation']='actual native schema serialization and root reconstruction; no HTTP request captured and no model called'
p['workflowImplementation']={f:sha(R/f) for f in p['workflowImplementation']}
p['files']={f:sha(R/'.opencode/skills'/f) for f in p['files']}
for f in p['bookRetrieval']['files']:p['bookRetrieval']['files'][f]=sha(R/f)
for item in p.get('localModuleOverrides',{}).values():item['sha256']=sha(R/item['file'])
contract=load(T/'loader-contract.json')
contract['sourceHashes']={f:sha(R/f) for f in contract['sourceHashes']}
for key in ['flowControl','slimming','adjudication','computeInterface','bookRetrieval']:contract[key]=p[key];m[key]=p[key]
(T/'loader-contract.json').write_bytes(enc(contract))
m['files']={f:sha(T/f) for f in m['files']}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest()
(T/'manifest.json').write_bytes(enc(m));p['methodVersion']=m['version']
(R/'.opencode/liuren-active.json').write_bytes(enc(p))
after={'release':p['release'],'runtime':p['runtime'],'files':{f:sha(R/f) for f in b['files']},
 'new_files':['tools/tests/liuren-workflow-consistency.test.mjs'],
 'parent_unchanged':True,'predictive_validation_count':0,'real_model_call_count':0}
after['new_file_hashes']={f:sha(R/f) for f in after['new_files']}
(O/'after.json').write_bytes(enc(after));print('Sealed',p['release'],m['version'])
