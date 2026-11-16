"""Seal the unpublished year-life adapter and retain frozen-parent fingerprints."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
b=load(O/'before.json');p=load(R/'.opencode/liuren-active.json');assert p['release']=='20261112-year-life-53'
assert all(sha(R/f)==h for f,h in b['frozen'].items()),'Frozen parent changed'
T=R/p['runtime'];m=load(T/'manifest.json');c=load(T/'loader-contract.json')
for rel in ['reading-route.json','references/shensha-policy.json','references/shensha-authority-evidence.json','references/confirmed-policy-register.json']:
 data=load(T/rel);data['release']=p['release']
 if rel=='reading-route.json':
  data['conditional']['nianming']['trigger']=m['conditional']['nianming']
  data['conditional']['deterministic-tools']={'stage':data['conditional']['nianming']['stage'],'trigger':m['conditional']['deterministic-tools']}
 save(T/rel,data)
policy={'id':'liuren-year-life-v1','scope':'local-opencode-and-codex','userStatedAdopted':True,'birthdayRequired':False,'branchOnlySupported':True,'sexMissingCandidates':True,'chartYearSource':'chart.pillars[0]','legacyUserinfoAuthoritative':False,'sameChartLifeReceipt':True,'twoDigitManualPivot':50,'predictiveValidationCount':0,'realModelCallCount':0,'audit':'output/liuren-year-life-53/改造与验收说明.md'}
p['yearLifeInput']=policy;m['yearLifeInput']=policy;c['yearLifeInput']=policy
for f in ['tools/liuren-year-life.mjs','tools/liuren-direct/chart.mjs']:p['workflowImplementation'][f]=sha(R/f);c['sourceHashes'][f]=sha(R/f)
p['workflowImplementation']={f:sha(R/f) for f in p['workflowImplementation']}
p['files']={f:sha(R/'.opencode/skills'/f) for f in p['files']}
for f in p['bookRetrieval']['files']:p['bookRetrieval']['files'][f]=sha(R/f)
for item in p.get('localModuleOverrides',{}).values():item['sha256']=sha(R/item['file'])
p['computeInterface']['transportEvidence']='output/liuren-year-life-53/native-schema.json'
p['computeInterface']['transportValidation']='actual native schema serialization and root reconstruction; no HTTP request captured and no model called'
c.update(release=p['release'],parentRelease=b['release']);c['sourceHashes']={f:sha(R/f) for f in c['sourceHashes']}
for k in ['computeInterface','bookRetrieval']:c[k]=p[k];m[k]=p[k]
for data in [p,m,c]:
 if 'adjudication' in data and 'compatibleMethodRelease' in data['adjudication']:data['adjudication']['compatibleMethodRelease']=p['release']
save(T/'loader-contract.json',c)
m['files']={f:sha(T/f) for f in m['files']}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest()
save(T/'manifest.json',m);p['methodVersion']=m['version'];save(R/'.opencode/liuren-active.json',p)
new=['tools/liuren-year-life.mjs','tools/tests/liuren-year-life.test.mjs']
save(O/'after.json',{'release':p['release'],'runtime':p['runtime'],'files':{f:sha(R/f) for f in b['files']},'new_file_hashes':{f:sha(R/f) for f in new if (R/f).exists()},'installed_skill_sha256':sha(Path.home()/'.codex/skills/daliuren-codex/SKILL.md'),'parent_unchanged':True,'predictive_validation_count':0,'real_model_call_count':0})
print('Sealed',p['release'],m['version'])
