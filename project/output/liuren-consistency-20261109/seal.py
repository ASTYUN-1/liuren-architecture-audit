"""Seal the current candidate's source hashes after verification repairs."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
before=load(OUT/'before.json')
assert all(sha(ROOT/rel)==h for rel,h in before['frozen'].items())
pointer=load(ROOT/'.opencode/liuren-active.json')
assert pointer['release']=='20261109-consistency-39'
runtime=ROOT/pointer['runtime']
capture=OUT/'current-wire.json'
if capture.is_file():
    wire=load(capture)
    assert wire['exitCode']==0 and wire['requests'] and wire['realModelCalled'] is False
    assert all(sha(ROOT/rel)==h for rel,h in wire['implementationSha256'].items())
    pointer['computeInterface']['transportEvidence']='output/liuren-consistency-20261109/current-wire.json'
loader=load(runtime/'loader-contract.json')
if capture.is_file():loader['computeInterface']=pointer['computeInterface']
loader['sourceHashes']={rel:sha(ROOT/rel) for rel in loader['sourceHashes']}
write(runtime/'loader-contract.json',loader)
manifest=load(runtime/'manifest.json')
if capture.is_file():manifest['computeInterface']=pointer['computeInterface']
manifest['files']={rel:sha(runtime/rel) for rel in manifest['files']}
manifest['version']=hashlib.sha256(json.dumps(manifest['files'],sort_keys=True).encode()).hexdigest()
write(runtime/'manifest.json',manifest)
pointer['methodVersion']=manifest['version']
pointer['workflowImplementation']={rel:sha(ROOT/rel) for rel in pointer['workflowImplementation']}
write(ROOT/'.opencode/liuren-active.json',pointer)
write(OUT/'after.json',{'release':pointer['release'],'files':{rel:sha(ROOT/rel) for rel in before['files']},'added':{rel:sha(ROOT/rel) for rel in ['tools/liuren-consistency-audit.mjs','tools/tests/liuren-consistency-audit.test.mjs','docs/本机六壬一致性核对-39.md']}})
print('Sealed current candidate; previous frozen release unchanged')
