"""Read-only integrity, source-span and actual material-loader verification."""
from pathlib import Path
import hashlib,json,runpy

R=Path(__file__).resolve().parents[2]
O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=load(O/'before.json')
pointer=load(R/'.opencode/liuren-active.json')
assert pointer['release']=='20261112-integrated-flow-49'
for f,h in before['frozen'].items():
    assert sha(R/f)==h,('parent changed',f)
for f,h in before['files'].items():
    assert sha(O/'before'/f)==h,('backup changed',f)
loader=runpy.run_path(str(R/'tools/load-liuren-methods.py'))
runtime,manifest=loader['active'](R)
for f,h in manifest['files'].items():
    assert sha(runtime/f)==h,('runtime changed',f)
for module,item in manifest['modules'].items():
    assert isinstance(item['requires'],list),module
    loader['content'](runtime,manifest,module)
extras=['analysis-workflow','analysis-workflow-evidence','classification-priority','classification-evidence']
for domain in manifest['domains']:
    plan=loader['plan_steps'](manifest,[domain],extras=extras)
    ids={step['id'] for step in plan}
    assert {domain,*extras,'judgment-core','adjudication','report'}<=ids,(domain,ids)
assert len(manifest['domains'])==17
source_count=0
for rel in ['references/classification-evidence.json','references/analysis-workflow-evidence.json']:
    for e in load(runtime/rel)['evidence']:
        p=R/e['path']
        assert sha(p)==e.get('source_sha256',e.get('sha256')),e['id']
        text=p.read_text(encoding=e.get('source_encoding',e.get('encoding')))
        quote='\n'.join(text.splitlines()[e['line_start']-1:e['line_end']])
        assert quote==e['quote'].replace('\r\n','\n'),('quote mismatch',e['id'])
        source_count+=1
for rel in ['opencode.json','.opencode/oh-my-opencode-slim.jsonc']:
    old,new=load(O/'before'/rel),load(R/rel)
    field='agent' if rel=='opencode.json' else 'agents'
    assert {k:(v.get('model'),v.get('variant')) for k,v in old[field].items()}=={
        k:(v.get('model'),v.get('variant')) for k,v in new[field].items()}
assert pointer['bookRetrieval']['books']==['RG','LF','TY','QA','KN','TR','KE']
print(json.dumps({'ok':True,'release':pointer['release'],
    'parent_files_unchanged':len(before['frozen']),'backup_files_verified':len(before['files']),
    'runtime_files_verified':len(manifest['files']),'modules_readable':len(manifest['modules']),
    'domains_planned':len(manifest['domains']),'source_spans_verified':source_count,
    'book_ids':pointer['bookRetrieval']['books'],'models_unchanged':True,
    'validation_scope':'engineering_integrity_and_exact_source_spans',
    'real_model_stability_verified':False,'predictive_validation_count':0},ensure_ascii=False,indent=2))
