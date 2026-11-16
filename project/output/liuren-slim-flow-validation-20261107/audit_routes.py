"""Exhaust active routes and every CLI method page; never query cases/experience."""
from pathlib import Path
import hashlib,importlib.util,json,re,subprocess,sys
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
spec=importlib.util.spec_from_file_location('route_audit_loader',ROOT/'tools/load-liuren-methods.py')
loader=importlib.util.module_from_spec(spec);spec.loader.exec_module(loader)
runtime,m=loader.active(ROOT)
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def check(name,ok,detail=None):
 assert ok,(name,detail)
 checks.append({'check':name,'passed':True,'detail':detail})
check('活动指针/manifest/全包字节身份一致',all(sha(runtime/rel)==h for rel,h in m['files'].items()),len(m['files']))
required=['positioning','liqi','structure','void','shensha-use','movement','adjudication','report']
check('主线8项唯一且旧6项不再重复',loader.plan(m)==required and not set(m['moduleAliases']).intersection(required))
routes=0
for domain in m['domains']:
 for timing in [False,True]:
  for quantity in [False,True]:
   selected=loader.plan(m,[domain],timing=timing,extras=['quantity','quantity-sources'] if quantity else [])
   assert selected[-1]=='report' and len(selected)==len(set(selected))
   assert set(required+[domain]).issubset(selected)
   assert ('timing' in selected)==timing
   assert ('quantity' in selected)==quantity
   routes+=1
 for condition in m['conditional']:
  steps=loader.plan_steps(m,[domain],extras=[condition]);keys=[r['id'] for r in steps]
  assert condition in keys and keys[-1]=='report' and len(keys)==len(set(keys))
  assert [r['stage'] for r in steps]==sorted(r['stage'] for r in steps)
  routes+=1
check('16占类×结果/应期/数量及13触发分支均连通',True,routes)
pages=0
for key in m['modules']:
 _,text,digest=loader.content(runtime,m,key)
 actual=[]
 for page in range(1,len(loader.page_text(text))+1):
  proc=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'tools/load-liuren-methods.py'),'read',key,'--page',str(page)],cwd=ROOT,capture_output=True,check=True,timeout=20)
  meta,body=loader.parse_page_output(proc.stdout);assert meta['fileSha256']==digest
  actual.append(body);pages+=1
 assert ''.join(actual)==text,key
check('全部登记模块经真实CLI逐页重建，含兼容别名',True,{'modules':len(m['modules']),'pageCalls':pages})
sys.path.insert(0,str(ROOT/'tools'))
from liuren_material_scope import MaterialScope
scope=MaterialScope(ROOT)
for rel in ['procedures/common.md','procedures/liuren-cases.md','procedures/liuren-extract.md']:
 check('维护入口文件可读取：'+rel,scope.permitted(runtime/rel))
for rel in ['案例项目库','经验日志','runtime/liuren/20261107-slim-26']:
 check('普通研判禁用边界保留：'+rel,not scope.permitted(ROOT/rel/'test.json'))
p=load(ROOT/'.opencode/liuren-active.json')
check('活动实现/三书/入口哈希登记一致',all(sha(ROOT/rel)==h for rel,h in p['workflowImplementation'].items()) and all(sha(ROOT/rel)==h for rel,h in p['bookRetrieval']['files'].items()) and all(sha(ROOT/'.opencode/skills'/rel)==h for rel,h in p['files'].items()))
contract=load(runtime/'loader-contract.json')
check('loader全部实现源hash一致',all(sha(ROOT/rel)==h for rel,h in contract['sourceHashes'].items()))
policy=load(runtime/'references/shensha-policy.json');previous=load(ROOT/'runtime/liuren/20261107-slim-26/references/shensha-policy.json')
policy.pop('release');previous.pop('release')
check('神煞固定取法及专业正文未改',policy==previous and all((runtime/rel).read_bytes()==(ROOT/'runtime/liuren/20261107-slim-26'/rel).read_bytes() for rel in m['files'] if rel.startswith(('methods/','domains/','details/','procedures/'))))
result={'release':p['release'],'checks':checks,'externalModelCalls':0,'predictiveValidationCount':0,'websiteChanged':False}
(OUT/'routes-audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'passed':len(checks),'routes':routes,'pageCalls':pages},ensure_ascii=False))
