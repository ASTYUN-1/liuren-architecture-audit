from pathlib import Path
import copy,hashlib,json,os
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='')
host=load(OUT/'host-chain.json');assert host['finished'] and host['exitCode']==0 and not host['failures']
assert host['childModelAndHighVerified']
p=load(ROOT/'.opencode/liuren-active.json');assert p['release']=='20261107-slim-28'
runtime=ROOT/p['runtime'];m=load(runtime/'manifest.json');contract=load(runtime/'loader-contract.json')
old=load(OUT/'before-fix/.opencode/liuren-active.json')
m['flowControl']={**old['flowControl'],**m['flowControl']}
m['adjudication']={**old['adjudication'],**m['adjudication']};m['adjudication'].pop('maxOutputTokens',None)
m['outputRecovery']['validation']='installed desktop host synthetic length/no-text -> same-child prompt -> submit -> deliver; request omits token cap'
m['computeInterface'].update(release=p['release'],transportEvidence=OUT.relative_to(ROOT).as_posix()+'/current-wire.json',transportValidation=m['outputRecovery']['validation'])
for k in ['adjudication','flowControl','outputRecovery','computeInterface']:contract[k]=copy.deepcopy(m[k]);p[k]=copy.deepcopy(m[k])
contract['sourceHashes']={rel:sha(ROOT/rel) for rel in contract['sourceHashes']};dump(runtime/'loader-contract.json',contract)
m['files']={rel:sha(runtime/rel) for rel in m['files']};m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(runtime/'manifest.json',m)
p['methodVersion']=m['version'];p['workflowImplementation']={rel:sha(ROOT/rel) for rel in p['workflowImplementation']}
p['bookRetrieval']['files']={rel:sha(ROOT/rel) for rel in p['bookRetrieval']['files']}
tmp=ROOT/'.opencode/liuren-active.finalize28.tmp';dump(tmp,p);os.replace(tmp,ROOT/'.opencode/liuren-active.json')
record=load(OUT/'local-fix.json');record['after']={rel:sha(ROOT/rel) for rel in record['before']};dump(OUT/'local-fix.json',record)
assert p['flowControl']['enabled'] is True
assert 'maxOutputTokens' not in p['adjudication']
for source,base in [(m['files'],runtime),(contract['sourceHashes'],ROOT),(p['workflowImplementation'],ROOT),(p['bookRetrieval']['files'],ROOT)]:assert all(sha(base/rel)==h for rel,h in source.items())
frozen=ROOT/old['runtime'];original=load(frozen/'manifest.json');assert original['version']==old['methodVersion'];assert all(sha(frozen/rel)==h for rel,h in original['files'].items())
print('Current hashes consistent; frozen 27 intact; host proof points to current wire capture')
