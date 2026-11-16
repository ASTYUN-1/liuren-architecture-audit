"""Verify installed bytes, actual material routing and recorded test outcomes."""
from pathlib import Path
import hashlib,importlib,json,sys
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
def read(p):return json.loads(p.read_text('utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
receipt=read(OUT/'activation-receipt.json');before=read(OUT/'before-manifest.json')
pointer=read(ROOT/'.opencode/liuren-active.json');runtime=ROOT/pointer['runtime'];manifest=read(runtime/'manifest.json')
assert pointer['release']==receipt['release']==manifest['release']
assert all(sha(ROOT/r)==h for r,h in receipt['files'].items())
assert all(sha(runtime/r)==h for r,h in receipt['runtimeFiles'].items())
assert all(sha(ROOT/before['parentRuntime']/r)==h for r,h in before['runtime'].items())
assert all(sha(ROOT/r)==h for r,h in pointer['workflowImplementation'].items())
assert all(sha(ROOT/r)==h for r,h in read(runtime/'loader-contract.json')['sourceHashes'].items())
assert all(sha(ROOT/r)==h for r,h in pointer['bookRetrieval']['files'].items())
sys.path.insert(0,str(ROOT/'tools'))
scope=importlib.import_module('liuren_material_scope').MaterialScope(ROOT)
guide=runtime/'references/deterministic-tools.md'
assert scope.permitted(guide)
source=scope.read(str(guide),start=1,count=160)
assert '确定性事实' in str(source)
plan=read(OUT/'installed-method-plan.json');module_ids={m['id'] for m in plan['modules']}
assert plan['release']==pointer['release'] and {'timing','quantity','quantity-sources','exam','adjudication'}<=module_ids
testlog=(OUT/'installed-tests.log').read_text('utf-8-sig')
assert ('pass 107' in testlog or '# pass 107' in testlog) and ('fail 0' in testlog or '# fail 0' in testlog)
doctor=read(OUT/'installed-doctor.json')
assert doctor['checks']['runtime']['release']==pointer['release']
assert doctor['checks']['shensha_policy']['release']==pointer['release']
assert doctor['checks']['program_chart']['ok'] is True
assert doctor['errors']==['research mechanical validation has gaps']
wire=read(OUT/'installed-wire.json')
assert wire['exitCode']==0 and wire['realModelCalled'] is False and wire['requests']
assert all(not r['referenceErrors'] for r in wire['requests'])
assert {t['name'] for r in wire['requests'] for t in r['tools']}=={'liuren_adjudication_packet','liuren_adjudication_read','liuren_compute'}
assert all(sha(ROOT/r)==h for r,h in wire['implementationSha256'].items())
old_doctor=read(ROOT/'output/liuren-compute-interface-20261106/installed-doctor.json')
assert doctor['checks']['research_issues']==old_doctor['checks']['research_issues']
result={'status':'passed-with-existing-research-gap','release':pointer['release'],'methodVersion':pointer['methodVersion'],
 'installedFiles':len(receipt['files']),'runtimeFiles':len(manifest['files']),'frozenParentUnchanged':True,
 'implementationLoaderBookHashesValid':True,'materialToolCanReadNewGuide':True,'timingQuantityPlanValid':True,
 'installedTests':{'passed':107,'failed':0,'log':'installed-tests.log'},
 'doctor':{'ok':doctor['ok'],'runtimeAndChartPassed':True,'errors':doctor['errors'],'researchIssueCount':len(doctor['checks']['research_issues'])},
 'externalModelCalled':False,'predictiveValidationCount':0,'liveModelLatencyMeasured':False,
 'actualOpenCodeTransport':{'exitCode':0,'relatedTools':3,'missingReferences':0,'destination':'127.0.0.1 mock API'},
 'evidence':{p.name:sha(p) for p in [OUT/'activation-receipt.json',OUT/'installed-tests.log',OUT/'installed-doctor.json',OUT/'installed-method-plan.json',OUT/'installed-wire.json']}}
(OUT/'installed-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['status','release','installedTests','doctor','materialToolCanReadNewGuide']},ensure_ascii=False))
