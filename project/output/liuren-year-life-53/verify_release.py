"""Read-only local release acceptance, without cases, feedback or model calls."""
from pathlib import Path
import json,hashlib,runpy
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=load(O/'before.json');a=load(O/'after.json');p=load(R/'.opencode/liuren-active.json')
assert p['release']==a['release']=='20261112-year-life-53'
assert all(sha(R/f)==h for f,h in b['frozen'].items()),'Frozen 52 changed'
assert all(sha(O/'before'/f)==h for f,h in b['files'].items()),'Backup changed'
assert all(sha(R/f)==h for f,h in a['files'].items()),'Live files differ from sealed version'
assert all(sha(R/f)==h for f,h in a['new_file_hashes'].items())
loader=runpy.run_path(str(R/'tools/load-liuren-methods.py'));T,m=loader['active'](R)
assert all(sha(T/f)==h for f,h in m['files'].items())
for key in m['modules']:loader['content'](T,m,key)
for domain in m['domains']:
 assert [x['id'] for x in loader['plan_steps'](m,[domain])]==['judgment-core',domain,'adjudication','report']
 for extra in m['conditional']:assert extra in {x['id'] for x in loader['plan_steps'](m,[domain],extras=[extra])}
assert all(sha(R/f)==h for f,h in p['workflowImplementation'].items())
assert all(sha(R/f)==h for f,h in load(T/'loader-contract.json')['sourceHashes'].items())
assert all(sha(R/'.opencode/skills'/f)==h for f,h in p['files'].items())
assert all(sha(R/f)==h for f,h in p['bookRetrieval']['files'].items())
for v in p['localModuleOverrides'].values():assert sha(R/v['file'])==v['sha256']
old=load(O/'before/.opencode/liuren-active.json')
for key in ['quantityCorrection','basicBifaIntegration','integratedAnalysis','numericAnswer','bookAnnotationIntegration']:
 assert p[key]==old[key],key
for f in ['tools/liuren-strength-profile.json','tools/liuren-strength-rules.mjs','tools/liuren-local-strength-profile.json','tools/liuren-local-strength.mjs','tools/liuren-quantity-adjustment.mjs']:
 assert sha(R/f)==b['files'][f],f
oldcore=(R/b['runtime']/'references/judgment-core.md').read_text('utf8');newcore=(T/'references/judgment-core.md').read_text('utf8')
adopted=oldcore[oldcore.index('## 已确认判断口径 U01'):].split('\n## ',1)[0].strip()
assert adopted in newcore,'U01—U11 changed'
assert (R/'.opencode/skills/liuren/daliuren/SKILL.md').read_bytes()==(T/'entry.md').read_bytes()
assert load(R/'.opencode/oh-my-opencode-slim.jsonc')['agents']['liuren-adjudicator']['prompt']==(T/'references/adjudicator-prompt.md').read_text('utf8')
for rel in ['SKILL.md','references/host.md']:
 assert (Path.home()/'.codex/skills/daliuren-codex'/rel).read_bytes()==(R/'integrations/codex/daliuren-codex'/rel).read_bytes()
assert sha(Path.home()/'.codex/skills/daliuren-codex/SKILL.md')==a['installed_skill_sha256']
for f,key in [('opencode.json','agent'),('.opencode/oh-my-opencode-slim.jsonc','agents')]:
 before,now=load(O/'before'/f),load(R/f)
 assert {k:(v.get('model'),v.get('variant')) for k,v in before[key].items()}=={k:(v.get('model'),v.get('variant')) for k,v in now[key].items()}
assert p['adjudication']['maxOutputTokens']==old['adjudication']['maxOutputTokens']==393216
schema=load(O/'native-schema.json')
assert schema['realModelCalled'] is False and schema['networkRequestCaptured'] is False
assert len(schema['requests'][0]['tools'])==8
for f,h in schema['implementationSha256'].items():assert sha(R/f)==h
assert p['yearLifeInput']['birthdayRequired'] is False
result={'ok':True,'release':p['release'],'method_version':m['version'],'parent_files_unchanged':len(b['frozen']),'backup_files_verified':len(b['files']),'runtime_files_verified':len(m['files']),'modules_readable':len(m['modules']),'domains_planned':len(m['domains']),'conditional_routes_checked':len(m['conditional']),'U01_U11_unchanged':True,'strength_quantity_parameters_unchanged':True,'models_budget_unchanged':True,'installed_skill_synced':True,'native_schema_tools':8,'real_model_call_count':0,'predictive_validation_count':0}
(O/'final-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(result,ensure_ascii=False,indent=2))
