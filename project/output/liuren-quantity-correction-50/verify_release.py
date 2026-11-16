"""Read-only verification of active sources, parent freeze and source quotes."""
from pathlib import Path
import hashlib,json,runpy
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=load(O/'before.json');p=load(R/'.opencode/liuren-active.json');assert p['release']=='20261112-quantity-correction-50'
assert all(sha(R/f)==h for f,h in b['frozen'].items())
assert all(sha(O/'before'/f)==h for f,h in b['files'].items())
loader=runpy.run_path(str(R/'tools/load-liuren-methods.py'));t,m=loader['active'](R)
assert all(sha(t/f)==h for f,h in m['files'].items())
for module in m['modules']:loader['content'](t,m,module)
for domain in m['domains']:
 ids={v['id'] for v in loader['plan_steps'](m,[domain],extras=['quantity-correction','quantity-correction-evidence'])}
 assert {domain,'quantity-correction','quantity-correction-evidence'}<=ids
evidence=[]
for f in ['references/classification-evidence.json','references/analysis-workflow-evidence.json','references/quantity-correction-evidence.json']:
 for e in load(t/f)['evidence']:
  source=R/e['path'];assert sha(source)==e.get('source_sha256',e.get('sha256')),e['id']
  lines=source.read_text(encoding=e.get('source_encoding',e.get('encoding'))).splitlines()
  assert '\n'.join(lines[e['line_start']-1:e['line_end']])==e['quote'].replace('\r\n','\n'),e['id']
  evidence.append(e['id'])
assert p['quantityCorrection']['receiptReviewRequired'] is True
for f,field in [('opencode.json','agent'),('.opencode/oh-my-opencode-slim.jsonc','agents')]:
 a,z=load(O/'before'/f),load(R/f)
 assert {k:(v.get('model'),v.get('variant')) for k,v in a[field].items()}=={k:(v.get('model'),v.get('variant')) for k,v in z[field].items()}
old=load(O/'before/.opencode/liuren-active.json')
assert old['adjudication'].get('maxOutputTokens')==p['adjudication'].get('maxOutputTokens')
for f,h in old['workflowImplementation'].items():
 if f in ['tools/liuren-strength-profile.json','tools/liuren-palace-strength.mjs','tools/liuren-strength-engine.mjs','tools/liuren-strength-rules.mjs','tools/liuren-local-strength.mjs']:
  assert sha(R/f)==h,f
status=load(O/'codex-status.json');assert status['ready'] and not status['mismatches']
print(json.dumps({'ok':True,'release':p['release'],'parent_files_unchanged':len(b['frozen']),
 'backup_files_verified':len(b['files']),'runtime_content_files_verified':len(m['files']),
 'modules_readable':len(m['modules']),'domains_planned':len(m['domains']),
 'source_spans_verified':len(evidence),'models_and_budget_unchanged':True,'strength_algorithm_unchanged':True,
 'new_numerical_tasks_require_receipt_review':True,'real_model_validation':False,'predictive_validation_count':0},ensure_ascii=False,indent=2))
