from pathlib import Path
import copy,hashlib,json,os
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8',newline='')
flow=load(OUT/'flow-result.json');length=load(OUT/'length-result.json');mcp=load(OUT/'mcp-result.json')
assert all(v['finished'] and not v['failures'] and all(t['status']=='completed' for t in v['toolResults']) for v in [flow,length,mcp])
assert len(mcp['toolResults'])==8
assert length['childRequests'] and all(r['reasoning_effort']=='high' and not r['outputBudgetKeys'] for r in length['childRequests'])
p=load(ROOT/'.opencode/liuren-active.json');runtime=ROOT/p['runtime'];m=load(runtime/'manifest.json');contract=load(runtime/'loader-contract.json')
assert p['release']=='20261107-slim-29'
m['stability']['validation']='verified native global/project autoload normal flow, length recovery, 8 MCP calls and separate minimal live model tool call'
m['computeInterface']['transportValidation']='native desktop global/project config; no composition wrapper; normal and length recovery both delivered full report'
m['outputRecovery'].update(validation=m['computeInterface']['transportValidation'],evidence=OUT.relative_to(ROOT).as_posix()+'/validation-summary.json')
for k in ['stability','computeInterface','outputRecovery']:contract[k]=copy.deepcopy(m[k]);p[k]=copy.deepcopy(m[k])
contract['sourceHashes']={rel:sha(ROOT/rel) for rel in contract['sourceHashes']};dump(runtime/'loader-contract.json',contract)
m['files']={rel:sha(runtime/rel) for rel in m['files']};m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(runtime/'manifest.json',m)
p['methodVersion']=m['version'];p['workflowImplementation']={rel:sha(ROOT/rel) for rel in p['workflowImplementation']};p['bookRetrieval']['files']={rel:sha(ROOT/rel) for rel in p['bookRetrieval']['files']}
tmp=ROOT/'.opencode/liuren-active.finalize29.tmp';dump(tmp,p);os.replace(tmp,ROOT/'.opencode/liuren-active.json')
before=load(OUT/'before-sha256.json');dump(OUT/'local-fix.json',{'release':p['release'],'previousRelease':'20261107-slim-28','websiteChanged':False,'before':before,'after':{rel:sha(ROOT/rel) for rel in before}})
for hashes,base in [(m['files'],runtime),(contract['sourceHashes'],ROOT),(p['workflowImplementation'],ROOT),(p['bookRetrieval']['files'],ROOT)]:assert all(sha(base/rel)==value for rel,value in hashes.items())
old=ROOT/'runtime/liuren/20261107-slim-28';oldmanifest=load(old/'manifest.json');assert all(sha(old/rel)==value for rel,value in oldmanifest['files'].items())
changed=[rel for rel,value in oldmanifest['files'].items() if sha(runtime/rel)!=value]
assert set(changed)=={'loader-contract.json','references/deterministic-tools.md','references/shensha-policy.json'},changed
assert p['flowControl']['enabled'] is True and 'maxOutputTokens' not in p['adjudication']
dump(OUT/'integrity.json',{'release':p['release'],'methodVersion':m['version'],'frozen28Intact':True,'professionalMethodBodiesUnchanged':True,'changedRuntimeFiles':changed,'sourceHashesConsistent':True})
print('Final 29 hashes consistent; frozen 28 intact; professional method bodies unchanged')
