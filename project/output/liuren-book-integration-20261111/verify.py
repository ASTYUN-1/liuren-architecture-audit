"""Verify source identity, complete selection coverage, active reads and rollback guards."""
from pathlib import Path
import hashlib,json,subprocess,sys,importlib.util
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
d=load(ROOT/'.opencode/liuren-active.json');assert d['release']=='20261111-book-logic-41'
r=ROOT/d['runtime'];m=load(r/'manifest.json');checks=[]
def checked(name,condition):
 assert condition,name
 checks.append({'name':name,'passed':True})
checked('All versioned runtime hashes',all(sha(r/p)==h for p,h in m['files'].items()))
checked('Active implementation bindings',all(sha(ROOT/p)==h for p,h in d['workflowImplementation'].items()))
before=load(OUT/'before.json');after=load(OUT/'after.json')
checked('Frozen40 all files unchanged',all(sha(ROOT/p)==h for p,h in before['frozen'].items()))
checked('Rollback exact backups',all(sha(OUT/'before'/p)==h for p,h in before['files'].items()))
checked('Live rollback guards',all(sha(ROOT/p)==h for p,h in after['files'].items()))
e=load(r/'references/book-annotation-evidence.json')
checked('24 user selections mapped',sorted(x['selection'] for x in e['selections'])==list(range(1,25)))
for s in e['spans']:
 p=ROOT/s['path'];lines=p.read_text('utf-8-sig').splitlines()
 checked('Continuous quote '+s['id'],sha(p)==s['sha256'] and '\n'.join(lines[s['line_start']-1:s['line_end']])==s['quote'])
checked('Void entire section and continuation retained',any(s['line_start']==5467 and s['line_end']==5610 for s in e['spans']) and any(s['line_start']==5611 and s['line_end']==5693 for s in e['spans']))
checked('User deferred decision retained',e['user_decision']['quote']=='此处先保留现行，后续由我仔细研判。')
for name in ['book-logic','quantity-strength','void-class-applications','book-annotation-evidence']:
 checked('Runtime module '+name,name in m['modules'] and (r/m['modules'][name]['file']).is_file())
spec=importlib.util.spec_from_file_location('method_loader',ROOT/'tools/load-liuren-methods.py');mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
_,active=mod.active(ROOT)
for key in ['judgment-core','book-logic','quantity-strength','void-class-applications','book-annotation-evidence']:
 _,text,_=mod.content(r,active,key);checked('Readable complete module '+key,bool(text))
plan=mod.plan_steps(active,domains=['exam'],extras=['quantity'])
ids=[x['id'] for x in plan]
checked('Numeric route includes correction before adjudication',ids.index('quantity-strength')<ids.index('quantity')<ids.index('adjudication'))
checked('All 16 domains kept',len(active['domains'])==16)
checked('User term corrections live in core',all(x in (r/'references/judgment-core.md').read_text('utf-8') for x in ['strength计空不代表quantity','类神不入课传','神将吉凶名目只作倾向','神生其将且神自空']))
cfg=load(ROOT/'opencode.json');old=load(OUT/'before/opencode.json')
checked('Host model choices unchanged',{k:(v.get('model'),v.get('variant')) for k,v in cfg['agent'].items()}=={k:(v.get('model'),v.get('variant')) for k,v in old['agent'].items()})
slim=load(ROOT/'.opencode/oh-my-opencode-slim.jsonc');oldslim=load(OUT/'before/.opencode/oh-my-opencode-slim.jsonc')
for key in ['model','variant','maxTokens','maxOutputTokens','reasoningEffort']:
 checked('Adjudicator option preserved '+key,slim['agents']['liuren-adjudicator'].get(key)==oldslim['agents']['liuren-adjudicator'].get(key))
cards=load(ROOT/'knowledge/liuren-research/20261102/rules/book-annotation-20261111.json')
checked('12 research cards have exact source refs',len(cards)==12 and all(c['evidence_refs'] and c['independent_validation_count']==0 for c in cards))
for c in cards:
 for s in c['evidence_refs']:
  checked('Card quote '+c['id'],'\n'.join((ROOT/s['path']).read_text('utf-8-sig').splitlines()[s['line_start']-1:s['line_end']])==s['quote'] and sha(ROOT/s['path'])==s['sha256'])
result={'schema':'liuren-book41-verification-v1','release':d['release'],'methodVersion':d['methodVersion'],'checks':checks,
 'sourceSpans':len(e['spans']),'selectionCount':len(e['selections']),'independentPredictiveValidationCount':0,'modelCalls':0,'websiteChanged':False}
(OUT/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf-8')
print('Passed',len(checks),'source/binding/coverage/compatibility checks; independent predictive validation=0')
