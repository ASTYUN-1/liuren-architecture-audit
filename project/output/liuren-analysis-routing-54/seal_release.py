"""Activate and seal the staged release after preserving rollback material."""
from pathlib import Path
import json, hashlib, re
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
b=load(O/'before.json'); old=b['release']; new='20261112-analysis-routing-54';T=R/'runtime/liuren'/new
assert all(sha(R/f)==h for f,h in b['frozen'].items()),'Frozen parent changed'
p=load(R/'.opencode/liuren-active.json');assert p['release'] in [old,new]
p.update(release=new,previousRelease=old,runtime='runtime/liuren/'+new,backup='output/liuren-analysis-routing-54/before')
m=load(T/'manifest.json');c=load(T/'loader-contract.json')
m.update(release=new,parentRelease=old);c.update(release=new,parentRelease=old)
policy={'schema':'liuren-analysis-route-v1','enabled':True,'questionRoutingRequired':True,'domainCount':17,
 'programSelectsClassGod':False,'quantityChangeEvidenceRequired':True,'reviewEvidenceRequired':True,
 'fixedReportTemplate':False,'maxRechecks':1,'realModelCallCount':0,'predictiveValidationCount':0,
 'audit':'output/liuren-analysis-routing-54/改造与验收说明.md'}
for data in [p,m,c]:data['analysisRouting']=policy
for rel in ['reading-route.json','references/shensha-policy.json','references/shensha-authority-evidence.json','references/confirmed-policy-register.json']:
 d=load(T/rel);d['release']=new;save(T/rel,d)
save(T/'analysis-routing-revision.json',policy)
for f in ['tools/liuren-analysis-route.mjs']:
 p['workflowImplementation'][f]=sha(R/f);c['sourceHashes'][f]=sha(R/f)
for cfg in ['opencode.json','.opencode/oh-my-opencode-slim.jsonc']:
 f=R/cfg;s=f.read_text('utf8').replace(old,new)
 data=json.loads(s)
 if cfg=='opencode.json':
  rules=data['agent']['liuren']['permission']['read']
  rules={k:v for k,v in rules.items() if not re.search(r'runtime[/\\]liuren[/\\]20[0-9A-Za-z_-]+[/\\]',k)}
  for leaf in ['methods/*','domains/*','references/*','details/*','procedures/*','entry.md']:
   rel='runtime/liuren/'+new+'/'+leaf
   for key in [(R/rel).as_posix(),str(R/rel).replace('/','\\'),rel,rel.replace('/','\\'),R.name+'/'+rel,R.name+'\\'+rel.replace('/','\\')]:rules[key]='allow'
  data['agent']['liuren']['permission']['read']=rules
 if cfg.endswith('oh-my-opencode-slim.jsonc'):data['agents']['liuren-adjudicator']['prompt']=(T/'references/adjudicator-prompt.md').read_text('utf8')
 save(f,data)
for f in ['README.md','AGENTS.md','目录总索引.md']:
 path=R/f;s=path.read_text('utf8').replace(old,new);path.write_text(s,'utf8')
p['authoringSource']='output/liuren-analysis-routing-54'
p['computeInterface']['transportEvidence']='output/liuren-analysis-routing-54/native-schema.json'
for data in [p,m,c]:
 if 'adjudication' in data and 'compatibleMethodRelease' in data['adjudication']:data['adjudication']['compatibleMethodRelease']=new
p['workflowImplementation']={f:sha(R/f) for f in p['workflowImplementation']}
p['files']={f:sha(R/'.opencode/skills'/f) for f in p['files']}
for f in p['bookRetrieval']['files']:p['bookRetrieval']['files'][f]=sha(R/f)
for item in p.get('localModuleOverrides',{}).values():item['sha256']=sha(R/item['file'])
c['sourceHashes']={f:sha(R/f) for f in c['sourceHashes']}
for key in ['computeInterface','bookRetrieval']:c[key]=p[key];m[key]=p[key]
save(T/'loader-contract.json',c)
m['files']['analysis-routing-revision.json']=sha(T/'analysis-routing-revision.json')
m['files']={f:sha(T/f) for f in m['files']}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest()
save(T/'manifest.json',m);p['methodVersion']=m['version'];save(R/'.opencode/liuren-active.json',p)
newfiles=['tools/liuren-analysis-route.mjs','tools/tests/liuren-analysis-route.test.mjs']
save(O/'after.json',{'release':new,'runtime':p['runtime'],'files':{f:sha(R/f) for f in b['files']},
 'new_file_hashes':{f:sha(R/f) for f in newfiles},'installed_skill_sha256':sha(Path.home()/'.codex/skills/daliuren-codex/SKILL.md'),
 'parent_unchanged':True,'predictive_validation_count':0,'real_model_call_count':0})
print('Sealed',new,m['version'])
