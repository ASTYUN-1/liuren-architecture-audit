"""Check the exact candidate bytes and run local integration tests; no model calls."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
LIVE=OUT/'candidate-live';RUN=OUT/'candidate-runtime'
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def text(p):return p.read_text('utf-8-sig')
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
checks=[]
def check(name,value):
 if not value:raise ValueError(name)
 checks.append({'name':name,'status':'passed'})
before=read(OUT/'before-manifest.json');candidate=read(OUT/'candidate-manifest.json')
parent=ROOT/before['parentRuntime'];pointer=read(LIVE/'.opencode/liuren-active.json');manifest=read(RUN/'manifest.json')
check('frozen 08 bytes retained',all(sha(parent/r)==h for r,h in before['runtime'].items()))
check('candidate live bytes exact',all(sha(LIVE/r)==h for r,h in candidate['live'].items()))
check('runtime file inventory exact',set(manifest['files'])=={p.relative_to(RUN).as_posix() for p in RUN.rglob('*') if p.is_file() and p.name!='manifest.json'})
check('runtime bytes exact',manifest['files']==candidate['runtime'] and all(sha(RUN/r)==h for r,h in manifest['files'].items()))
version=hashlib.sha256(json.dumps(manifest['files'],sort_keys=True).encode()).hexdigest()
check('method version and releases agree',version==manifest['version']==pointer['methodVersion']==candidate['methodVersion'] and manifest['release']==pointer['release']==candidate['release']==before['newRelease'])
check('shensha identity agrees',read(RUN/'references/shensha-policy.json')['release']==pointer['release'])
def effective(r):return LIVE/r if (LIVE/r).is_file() else ROOT/r
check('workflow implementation hashes',all(sha(effective(r))==h for r,h in pointer['workflowImplementation'].items()))
loader=read(RUN/'loader-contract.json')
check('loader hashes',loader['release']==pointer['release'] and all(sha(effective(r))==h for r,h in loader['sourceHashes'].items()))
route=read(RUN/'reading-route.json');old_route=read(parent/'reading-route.json')
check('14 required reads, 16 topics and 11 original stages retained',route==json.loads(json.dumps(old_route,ensure_ascii=False).replace(before['parentRelease'],before['newRelease'])) and sum(len(s['required']) for s in route['stages'])==14 and len(route['domains'])==16 and len(route['legacyCoverage'])==11)
appended=['methods/'+n+'.md' for n in ['adjudication','relations','liqi','timing','quantity','report','evidence']]
check('professional method bodies retained as prefix',all(text(RUN/r).startswith(text(parent/r)) for r in appended))
changed=set(appended+['entry.md','reading-route.json','loader-contract.json','manifest.json','references/shensha-policy.json','references/adjudicator-contract.md','references/adjudicator-prompt.md'])
check('all other parent runtime files retained byte for byte',all(sha(RUN/r)==h for r,h in before['runtime'].items() if r not in changed))
for r in ['references/adjudicator-book-basis.md','references/adjudicator-book-evidence.json','references/adjudication-method-conditions.md']:
 check('fixed book material unchanged: '+r,sha(RUN/r)==sha(parent/r))
evidence=read(RUN/'references/adjudicator-book-evidence.json')['evidence']
check('E01 to E22 retained',set(e['id'] for e in evidence)=={'E'+str(i).zfill(2) for i in range(1,23)})
check('case and experience experiment retained',read(RUN/'experiment.json')['disableCaseExperience'] is True and pointer['experiment']==read(OUT/'before/.opencode/liuren-active.json')['experiment'])
retrieval=pointer['bookRetrieval']
check('three book search intact',retrieval['books']==['RG','LF','TY'] and retrieval['compatibleMethodRelease']==pointer['release'] and all(sha(effective(r))==h for r,h in retrieval['files'].items()))
cfg=read(LIVE/'opencode.json');old_cfg=read(OUT/'before/opencode.json')
slim=read(LIVE/'.opencode/oh-my-opencode-slim.jsonc');old_slim=read(OUT/'before/.opencode/oh-my-opencode-slim.jsonc')
agent=slim['agents']['liuren-adjudicator'];old_agent=old_slim['agents']['liuren-adjudicator']
check('DeepSeek model and high reasoning retained',agent['model']==old_agent['model']=='deepseek/deepseek-flash' and agent['variant']==old_agent['variant']=='high' and agent['options']['reasoningEffort']=='high' and pointer['adjudication']['plugin']=='oh-my-opencode-slim')
check('main and child compute permissions',cfg['agent']['liuren']['permission']['liuren_compute']=='allow' and agent['permission']['liuren_compute']=='allow')
reduced=json.loads(json.dumps(slim));reduced['agents']['liuren-adjudicator']['prompt']=old_agent['prompt'];reduced['agents']['liuren-adjudicator']['permission'].pop('liuren_compute')
check('other slim settings preserved',reduced==old_slim)
reduced=json.loads(json.dumps(cfg).replace(before['newRelease'],before['parentRelease']));reduced['agent']['liuren']['prompt']=old_cfg['agent']['liuren']['prompt'];reduced['agent']['liuren']['permission'].pop('liuren_compute')
check('other main settings preserved',reduced==old_cfg)
prompt=text(RUN/'references/adjudicator-prompt.md')
check('runtime and actual child prompt agree',agent['prompt']==prompt)
example=json.loads(prompt.split('```json\n',1)[1].split('\n```',1)[0])
check('output example leaves program fields to code',all(not any(k in e for k in ['position','five_qi','twelve_states','site_yin','shenjiang']) for e in example['entity_checks']) and 'application' in example['relation_checks'][0] and 'special_methods' in example and 'calculations' in example)
fixed_heading='## 必须保留的分歧与限制'
fixed_tail=fixed_heading+text(parent/'references/adjudicator-prompt.md').split(fixed_heading,1)[1]
check('fixed prompt source conditions retained',prompt[prompt.index(fixed_heading):].startswith(fixed_tail))
for name in ['daliuren','liuren-cases','liuren-extract']:
 rel='.opencode/skills/liuren/'+name+'/SKILL.md';body=text(LIVE/rel)
 check('skill header and hash '+name,body.startswith('---\n') and '\nname: '+name+'\n' in body and '\ndescription:' in body and pointer['files']['liuren/'+name+'/SKILL.md']==sha(LIVE/rel))
check('skill entry equals runtime entry',sha(LIVE/'.opencode/skills/liuren/daliuren/SKILL.md')==sha(RUN/'entry.md'))
plugin=text(LIVE/'.opencode/plugins/liuren-adjudication.ts')
check('child source read blocked in code',"if(context.agent!== 'liuren')throw new Error('LIUREN_COMPUTE_SOURCE_PRIMARY_ONLY')" in plugin)
check('file protocol and factual return checks retained',all(s in plugin for s in ['LIUREN_ADJUDICATION_FILE_V1','FILE_NOT_FULLY_READ','finalizeFoundation','validateOutput']))
check('new feature enabled without new model calls',pointer['deterministicFoundation']['enabled'] is True and pointer['deterministicFoundation']['modelCallsAdded']==0)

env=os.environ.copy();env['LIUREN_TEST_CODE_ROOT']=str(LIVE)
node=Path(shutil.which('node'))
if os.name=='nt':node=node.with_suffix('.exe')
check('candidate import dependency unchanged',sha(ROOT/'tools/liuren-shensha.mjs')==read(OUT/'before/.opencode/liuren-active.json')['workflowImplementation']['tools/liuren-shensha.mjs'])
args=[str(node),'--import',(OUT/'candidate-import.mjs').as_uri(),'--test','tools/tests/liuren-deterministic.test.mjs','tools/tests/liuren-adjudication-contract.test.mjs','tools/tests/liuren-adjudication-plugin.test.mjs','tools/tests/liuren-chart-health.test.mjs','tools/tests/liuren-shensha.test.mjs']
started=time.monotonic();proc=subprocess.run(args,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding='utf-8',errors='replace',timeout=90)
(OUT/'candidate-tests.log').write_text(proc.stdout,encoding='utf-8')
check('candidate integration tests',proc.returncode==0)
result={'status':'passed','release':pointer['release'],'candidateManifestSha256':sha(OUT/'candidate-manifest.json'),'checks':checks,'testLog':'candidate-tests.log','testLogSha256':sha(OUT/'candidate-tests.log'),'testSeconds':round(time.monotonic()-started,3),'externalModelCalled':False,'predictiveValidationCount':0}
dump(OUT/'candidate-checks.json',result)
print(json.dumps({'status':'passed','staticChecks':len(checks)-1,'tests':next((s.strip() for s in proc.stdout.splitlines() if 'tests ' in s and ('ℹ' in s or s.startswith('# tests'))),'see log'),'release':pointer['release']},ensure_ascii=False))
