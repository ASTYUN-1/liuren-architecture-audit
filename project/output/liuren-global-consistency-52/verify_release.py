"""Verify current closure, preserved rules and provenance; never call a model."""
from pathlib import Path
import hashlib,json,runpy
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=load(O/'before.json');a=load(O/'after.json');p=load(R/'.opencode/liuren-active.json')
assert p['release']==a['release']=='20261112-consistency-52'
assert all(sha(R/f)==h for f,h in b['frozen'].items()),'Parent changed'
assert all(sha(O/'before'/f)==h for f,h in b['files'].items()),'Backup changed'
assert all(sha(R/f)==h for f,h in a['files'].items()),'Live files changed after sealing'
assert all(sha(R/f)==h for f,h in a['new_file_hashes'].items())
loader=runpy.run_path(str(R/'tools/load-liuren-methods.py'));t,m=loader['active'](R)
assert p['methodVersion']==m['version']
assert all(sha(t/f)==h for f,h in m['files'].items())
assert m['version']==hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest()
for key in m['modules']:loader['content'](t,m,key)
for domain in m['domains']:
 steps=loader['plan_steps'](m,[domain]);keys=[s['id'] for s in steps]
 assert keys==['judgment-core',domain,'adjudication','report'],(domain,keys)
 assert [s['stage'] for s in steps]==sorted(s['stage'] for s in steps)
 selected=loader['plan_steps'](m,[domain],extras=['quantity-correction','quantity-strength','strength-quantity-evidence'])
 assert {s['id'] for s in selected}>={domain,'quantity-correction','quantity-strength','strength-quantity-evidence'}
 for conditional in m['conditional']:
  route=loader['plan_steps'](m,[domain],extras=[conditional])
  assert conditional in {s['id'] for s in route}
  assert len(route)==len({s['id'] for s in route})
assert all(sha(R/f)==h for f,h in p['workflowImplementation'].items())
assert all(sha(R/f)==h for f,h in load(t/'loader-contract.json')['sourceHashes'].items())
assert all(sha(R/'.opencode/skills'/f)==h for f,h in p['files'].items())
assert all(sha(R/f)==h for f,h in p['bookRetrieval']['files'].items())
for f in ['tools/liuren-strength-profile.json','tools/liuren-strength-rules.mjs','tools/liuren-local-strength-profile.json','tools/liuren-local-strength.mjs','tools/liuren-quantity-adjustment.mjs']:
 assert sha(R/f)==b['files'][f],f
for f,field in [('opencode.json','agent'),('.opencode/oh-my-opencode-slim.jsonc','agents')]:
 old,now=load(O/'before'/f),load(R/f)
 assert {k:(v.get('model'),v.get('variant')) for k,v in old[field].items()}=={k:(v.get('model'),v.get('variant')) for k,v in now[field].items()}
old=load(O/'before/.opencode/liuren-active.json')
assert p['adjudication'].get('maxOutputTokens')==old['adjudication'].get('maxOutputTokens')==393216
oldcore=(R/b['runtime']/'references/judgment-core.md').read_text('utf8')
newcore=(t/'references/judgment-core.md').read_text('utf8')
adopted=oldcore[oldcore.index('## 已确认判断口径 U01'):oldcore.index('## 单宫旺衰与取用后补算')].strip()
assert adopted in newcore,'Adopted U01-U11 changed'
entry=(R/'.opencode/skills/liuren/daliuren/SKILL.md').read_text('utf8')
assert entry==(t/'entry.md').read_text('utf8')
agents=(R/'AGENTS.md').read_text('utf8')
assert agents.count('# 本地大六壬工作区接手指引')==1
assert '51版现行规则（覆盖上方50版' not in agents and '42版本机基本毕法' not in agents
assert b['agent_prefix_detection']['original_project_only'] is True
prompt=(t/'references/adjudicator-prompt.md').read_text('utf8')
assert prompt==load(R/'.opencode/oh-my-opencode-slim.jsonc')['agents']['liuren-adjudicator']['prompt']
installed=Path.home()/'.codex/skills/daliuren-codex'
for f in ['SKILL.md','references/host.md']:
 assert (installed/f).read_bytes()==(R/'integrations/codex/daliuren-codex'/f).read_bytes(),f
records=load(t/'references/strength-quantity-evidence.json')['records']
for e in records:
 source=R/e['path'];assert sha(source)==e['sha256'],e['id']
 assert '\n'.join(source.read_text(encoding=e['encoding']).splitlines()[e['line_start']-1:e['line_end']])==e['quote'],e['id']
schema=load(O/'native-schema.json')
assert schema['networkRequestCaptured'] is False and schema['realModelCalled'] is False
for f,h in schema['implementationSha256'].items():assert sha(R/f)==h
assert p['flowControl']['maxAdjudications']==1
assert p['quantityCorrection']['calibrated'] is False
assert p['quantityCorrection']['defaultActualQuantityVoidFactor'] is None
result={'ok':True,'release':p['release'],'method_version':p['methodVersion'],
 'parent_files_unchanged':len(b['frozen']),'backup_files_verified':len(b['files']),
 'runtime_files_verified':len(m['files']),'modules_readable':len(m['modules']),
 'domains_planned':len(m['domains']),'all_conditional_routes_checked':len(m['conditional']),
 'source_spans_verified':len(records),'U01_U11_verbatim':True,'installed_skill_synced':True,
 'legacy_project_instructions_removed':True,'coefficients_models_budget_unchanged':True,
 'core_chars_before':len(oldcore),'core_chars_after':len(newcore),
 'native_schema_tools':len(schema['requests'][0]['tools']),
 'network_request_captured':False,'real_model_call_count':0,'predictive_validation_count':0}
(O/'final-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
print(json.dumps(result,ensure_ascii=False,indent=2))
