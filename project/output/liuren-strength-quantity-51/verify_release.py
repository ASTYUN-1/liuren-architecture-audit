"""Read-only release, source quote and baseline verification."""
from pathlib import Path
import hashlib,json,runpy
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=load(O/'before.json');p=load(R/'.opencode/liuren-active.json')
assert p['release']=='20261112-strength-quantity-51'
assert all(sha(R/f)==h for f,h in b['frozen'].items()),'Parent changed'
assert all(sha(O/'before'/f)==h for f,h in b['files'].items()),'Backup changed'
loader=runpy.run_path(str(R/'tools/load-liuren-methods.py'));t,m=loader['active'](R)
assert all(sha(t/f)==h for f,h in m['files'].items())
for module in m['modules']:loader['content'](t,m,module)
for domain in m['domains']:
 ids={s['id'] for s in loader['plan_steps'](m,[domain],extras=['quantity-correction','quantity-strength','strength-quantity-evidence'])}
 assert {domain,'quantity-correction','quantity-strength','strength-quantity-evidence'}<=ids
assert all(sha(R/f)==h for f,h in p['workflowImplementation'].items())
assert all(sha(R/f)==h for f,h in load(t/'loader-contract.json')['sourceHashes'].items())
for f in ['tools/liuren-strength-profile.json','tools/liuren-strength-rules.mjs','tools/liuren-local-strength-profile.json','tools/liuren-local-strength.mjs']:
 assert sha(R/f)==b['files'][f],f
for f,field in [('opencode.json','agent'),('.opencode/oh-my-opencode-slim.jsonc','agents')]:
 old,now=load(O/'before'/f),load(R/f)
 assert {k:(v.get('model'),v.get('variant')) for k,v in old[field].items()}=={k:(v.get('model'),v.get('variant')) for k,v in now[field].items()}
old=load(O/'before/.opencode/liuren-active.json')
assert old['adjudication'].get('maxOutputTokens')==p['adjudication'].get('maxOutputTokens')
records=load(t/'references/strength-quantity-evidence.json')['records']
for e in records:
 f=R/e['path'];assert sha(f)==e['sha256'],e['id']
 assert '\n'.join(f.read_text(encoding=e['encoding']).splitlines()[e['line_start']-1:e['line_end']])==e['quote'],e['id']
assert p['quantityCorrection']['couplingRequired'] and p['quantityCorrection']['calibrated'] is False
assert p['quantityCorrection']['defaultActualQuantityVoidFactor'] is None
for rel in ['references/judgment-core.md','methods/quantity.md','references/quantity-strength.md','references/quantity-correction.md']:
 text=(t/rel).read_text(encoding='utf-8')
 assert '## 50版数量兑现：用户研究约定与实际执行' not in text
 assert '默认实际减半' not in text
schema=load(O/'native-schema.json')
assert schema['networkRequestCaptured'] is False and schema['realModelCalled'] is False
for f,h in schema['implementationSha256'].items():assert sha(R/f)==h
result={'ok':True,'release':p['release'],'parent_files_unchanged':len(b['frozen']),
 'backup_files_verified':len(b['files']),'runtime_files_verified':len(m['files']),'modules_readable':len(m['modules']),
 'domains_planned':len(m['domains']),'new_source_spans_verified':len(records),
 'original_strength_coefficients_unchanged':True,'models_and_budget_unchanged':True,
 'source_void_default_narrowed':True,'new_tasks_require_final_quantity_receipt':True,
 'native_schema_check':'actual serialization and host reconstruction; no fresh HTTP capture',
 'real_model_validation':False,'predictive_validation_count':0}
(O/'final-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
