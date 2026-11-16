"""Read-only release acceptance; no divination or accuracy claim."""
from pathlib import Path
import json,hashlib,runpy
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=load(O/'before.json');a=load(O/'after.json');p=load(R/'.opencode/liuren-active.json');T=R/p['runtime'];m=load(T/'manifest.json')
assert p['release']==a['release']=='20261112-analysis-routing-54'
assert (R/p['analysisRouting']['audit']).is_file(),'Missing acceptance explanation'
assert all(sha(R/f)==h for f,h in b['frozen'].items()),'Frozen parent changed'
assert all(sha(O/'before'/f)==h for f,h in b['files'].items()),'Backup changed'
assert all(sha(R/f)==h for f,h in a['files'].items()),'Unsealed live file'
assert all(sha(R/f)==h for f,h in a['new_file_hashes'].items())
loader=runpy.run_path(str(R/'tools/load-liuren-methods.py'));runtime,manifest=loader['active'](R)
assert runtime==T
m=manifest
for key in m['modules']:loader['content'](T,m,key)
for d in m['domains']:assert [s['id'] for s in loader['plan_steps'](m,[d])]==['judgment-core',d,'adjudication','report']
assert all(sha(R/f)==h for f,h in p['workflowImplementation'].items())
assert all(sha(R/f)==h for f,h in load(T/'loader-contract.json')['sourceHashes'].items())
assert all(sha(R/'.opencode/skills'/f)==h for f,h in p['files'].items())
old=load(O/'before/.opencode/liuren-active.json')
for key in ['quantityCorrection','basicBifaIntegration','integratedAnalysis','numericAnswer','yearLifeInput']:
 assert p[key]==old[key],key
for f in ['tools/liuren-strength-profile.json','tools/liuren-strength-rules.mjs','tools/liuren-local-strength-profile.json','tools/liuren-local-strength.mjs']:
 assert sha(R/f)==b['files'][f],f
oldcore=(R/b['runtime']/'references/judgment-core.md').read_text('utf8');newcore=(T/'references/judgment-core.md').read_text('utf8')
assert oldcore[oldcore.index('## 已确认判断口径 U01'):]==newcore[newcore.index('## 已确认判断口径 U01'):]
assert (T/'entry.md').read_bytes()==(R/'.opencode/skills/liuren/daliuren/SKILL.md').read_bytes()
assert load(R/'.opencode/oh-my-opencode-slim.jsonc')['agents']['liuren-adjudicator']['prompt']==(T/'references/adjudicator-prompt.md').read_text('utf8')
assert (Path.home()/'.codex/skills/daliuren-codex/SKILL.md').read_bytes()==(R/'integrations/codex/daliuren-codex/SKILL.md').read_bytes()
assert (Path.home()/'.codex/skills/daliuren-codex/references/host.md').read_bytes()==(R/'integrations/codex/daliuren-codex/references/host.md').read_bytes()
assert sha(Path.home()/'.codex/skills/daliuren-codex/SKILL.md')==a['installed_skill_sha256']
for f,key in [('opencode.json','agent'),('.opencode/oh-my-opencode-slim.jsonc','agents')]:
 before,now=load(O/'before'/f),load(R/f)
 assert {k:(v.get('model'),v.get('variant')) for k,v in before[key].items()}=={k:(v.get('model'),v.get('variant')) for k,v in now[key].items()}
assert p['adjudication']['maxOutputTokens']==old['adjudication']['maxOutputTokens']==393216
assert p['experiment']['disableCaseExperience'] is True
schema=load(O/'native-schema.json');assert schema['realModelCalled'] is False
for f,h in schema['implementationSha256'].items():assert sha(R/f)==h
result={'ok':True,'release':p['release'],'method_version':m['version'],'frozen_parent_files':len(b['frozen']),
 'backup_files':len(b['files']),'runtime_files':len(m['files']),'readable_modules':len(m['modules']),'domains':len(m['domains']),
 'U01_U11_unchanged':True,'strength_parameters_unchanged':True,'models_budget_unchanged':True,
 'installed_skill_synced':True,'case_experience_retrieval_disabled':True,'real_model_calls':0,'predictive_validation_count':0}
(O/'final-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8');print(json.dumps(result,ensure_ascii=False,indent=2))
