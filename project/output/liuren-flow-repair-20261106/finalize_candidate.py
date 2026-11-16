"""Refresh and verify reviewed candidate hashes. Does not switch active."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
before=read(OUT/'before-manifest.json');candidate=OUT/'candidate-runtime'
for rel,d in before['runtime'].items():assert sha(ROOT/before['parentRuntime']/rel)==d,rel
loader=read(candidate/'loader-contract.json');loader['parentRelease']=before['parentRelease']
for rel in loader['sourceHashes']:loader['sourceHashes'][rel]=sha(ROOT/rel)
dump(candidate/'loader-contract.json',loader)
m=read(candidate/'manifest.json');m['status']='active'
m['files']={f.relative_to(candidate).as_posix():sha(f) for f in candidate.rglob('*') if f.is_file() and f.name!='manifest.json'}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(candidate/'manifest.json',m)
p=read(OUT/'candidate-active.json');p['methodVersion']=m['version']
for rel in p['workflowImplementation']:p['workflowImplementation'][rel]=sha(ROOT/rel)
for rel in p['bookRetrieval']['files']:p['bookRetrieval']['files'][rel]=sha(ROOT/rel)
for rel in p['files']:p['files'][rel]=sha(ROOT/'.opencode/skills'/rel)
dump(OUT/'candidate-active.json',p)
assert (candidate/'entry.md').read_bytes()==(ROOT/p['entry']).read_bytes()
slim=read(ROOT/'.opencode/oh-my-opencode-slim.jsonc');agent=slim['agents']['liuren-adjudicator']
assert agent['prompt']==(candidate/'references/adjudicator-prompt.md').read_text('utf8')
assert agent['model']=='deepseek/deepseek-flash'
assert 'high' in json.dumps(agent)
config=read(ROOT/'opencode.json');perms=config['agent']['liuren']['permission']
assert perms['task_result']==perms['liuren_adjudication_result']=='allow'
assert agent['permission']['liuren_adjudication_submit']=='allow'
assert p['experiment']['disableCaseExperience'] is True
assert len(m['required'])==14 and 'engine-shensha-output' in m['required']
wire=read(OUT/'current-wire.json');assert wire['exitCode']==0 and wire['realModelCalled'] is False
for rel,d in wire['implementationSha256'].items():assert sha(ROOT/rel)==d,rel
for req in wire['requests']:assert not req['referenceErrors']
log=(OUT/'candidate-tests.log').read_text('utf-8-sig');assert 'tests 156' in log and 'pass 156' in log and 'fail 0' in log
cm={'release':p['release'],'runtime':{f.relative_to(candidate).as_posix():sha(f) for f in candidate.rglob('*') if f.is_file()},'live':{r:sha(ROOT/r) for r in [*before['live'],*before['newFiles']] if r!='.opencode/liuren-active.json'},'activeSha256':sha(OUT/'candidate-active.json')}
dump(OUT/'candidate-manifest.json',cm)
dump(OUT/'candidate-checks.json',{'status':'passed','release':p['release'],'tests':156,'candidateManifestSha256':sha(OUT/'candidate-manifest.json'),'testLogSha256':sha(OUT/'candidate-tests.log'),'wireCaptureSha256':sha(OUT/'current-wire.json'),'oldRuntimeUnchanged':True,'promptMatches':True,'independentPredictiveValidation':False})
print(json.dumps({'status':'ready','release':p['release'],'runtimeFiles':len(cm['runtime']),'liveFiles':len(cm['live']),'tests':156},ensure_ascii=False))

