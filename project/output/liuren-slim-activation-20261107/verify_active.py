from pathlib import Path
import hashlib
import importlib.util
import json
import re
import subprocess

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
def load(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('active_slim_loader',ROOT/'tools/load-liuren-methods.py')
loader=importlib.util.module_from_spec(spec);spec.loader.exec_module(loader)
runtime,m=loader.active(ROOT)
checks=[]
def check(name,ok,detail=None):
    assert ok,(name,detail)
    checks.append(dict(check=name,passed=True,detail=detail))
check('活动指针及方法身份一致',m['release']=='20261107-slim-26')
check('全运行包hash一致',all(sha(runtime/rel)==h for rel,h in m['files'].items()),len(m['files']))
protected=load(OUT/'protected-sha256.json')
check('冻结25包、工具程序及引擎字节未改',all(sha(ROOT/rel)==h for rel,h in protected.items()),len(protected))
for key in m['modules']:loader.content(runtime,m,key)
check('全部登记模块可读',True,len(m['modules']))
check('8项必读且旧6项退出主线',loader.plan(m)==m['required'] and len(m['required'])==8 and not set(m['moduleAliases']).intersection(m['required']))
for domain in m['domains']:
    selected=loader.plan(m,[domain]);assert set(selected)==set(m['required'])|{domain};assert selected.count(domain)==1
check('16专项按本问唯一进入',len(m['domains'])==16)
for key in m['conditional']:assert key in loader.plan(m,extras=[key])
check('全部按需分支可达',True,len(m['conditional']))
base=ROOT/'runtime/liuren/20261106-performance-25'
a=load(base/'references/shensha-policy.json');b=load(runtime/'references/shensha-policy.json')
a.pop('release');b.pop('release');check('神煞取法只改发布身份',a==b)
count=0
for old in (base/'domains').glob('*.md'):
    new=(runtime/'domains'/old.name).read_text('utf-8')
    for paragraph in re.split(r'\n\s*\n',old.read_text('utf-8-sig')):
        if paragraph.startswith(('共同规则只按 class-mapping 执行一次。','原专项上下文与历史来源身份见 mapping-provenance。')):continue
        assert paragraph.strip() in new,(old.name,paragraph[:50]);count+=1
check('16专项独有段落完整保留',True,count)
before=load(OUT/'before/.opencode/oh-my-opencode-slim.jsonc')['agents']['liuren-adjudicator']
after=load(ROOT/'.opencode/oh-my-opencode-slim.jsonc')['agents']['liuren-adjudicator']
basis=before['prompt'][before['prompt'].index('## 裁决依据'):before['prompt'].index('日干和组合的参照、成员由模型依原法核明')]
check('裁决依据与E01至E22全文保留',basis in after['prompt'])
check('裁决模型high及权限未变',all(before[k]==after[k] for k in ['model','variant','options','permission']))
pages=0
for key in m['required']+['exam','illness','finance','timing','quantity','quantity-sources']:
    _,body,_=loader.content(runtime,m,key);actual=[]
    for n in range(1,len(loader.page_text(body))+1):
        output=subprocess.run(['python','-X','utf8',str(ROOT/'tools/load-liuren-methods.py'),'read',key,'--page',str(n)],cwd=ROOT,capture_output=True,check=True).stdout
        _,text=loader.parse_page_output(output);actual.append(text);pages+=1
    assert ''.join(actual)==body
check('活动CLI实际逐页读取回执完整',True,pages)
pointer=load(ROOT/'.opencode/liuren-active.json')
for field in ['workflowImplementation']:
    assert all(sha(ROOT/rel)==h for rel,h in pointer[field].items())
assert all(sha(ROOT/rel)==h for rel,h in pointer['bookRetrieval']['files'].items())
contract=load(runtime/'loader-contract.json')
assert all(sha(ROOT/rel)==h for rel,h in contract['sourceHashes'].items())
check('入口与周边实现hash一致',True)
config=load(ROOT/'opencode.json');previous_config=load(OUT/'before/opencode.json')
expected=json.loads(json.dumps(previous_config,ensure_ascii=False).replace('20261106-performance-25','20261107-slim-26'))
for key in ['prompt','description']:expected['agent']['liuren'][key]=config['agent']['liuren'][key]
check('主配置仅改活动路径和主提示词',expected==config)
check('仅本机生效且两库仍禁用',pointer['localOnlyActivation'] and not pointer['websiteChanged'] and pointer['experiment']['disableCaseExperience'])
checks_output={'checks':checks,'modelCalls':0,'predictiveValidationCount':0,'nativeModelRun':False,'scope':'local-opencode-only'}
(OUT/'verification.json').write_text(json.dumps(checks_output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':len(checks),'pageReads':pages,'domainParagraphs':count},ensure_ascii=False))
