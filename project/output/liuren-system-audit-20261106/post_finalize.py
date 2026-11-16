"""Record post-install test maintenance and verify the installed bytes."""
from pathlib import Path
import json,hashlib,shutil
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
A=read(OUT/'activation-receipt.json');B=read(OUT/'before-manifest.json');p=read(ROOT/'.opencode/liuren-active.json')
assert p['release']==A['release']
changes=['tools/tests/test_liuren_class_mapping.py','tools/tests/liuren-compute-interface.test.mjs']
assert all(rel not in p['workflowImplementation'] for rel in changes)
if not (OUT/'activation-receipt-before-test-maintenance.json').exists():shutil.copyfile(OUT/'activation-receipt.json',OUT/'activation-receipt-before-test-maintenance.json')
for rel in changes:
 assert rel in B['live'] and sha(OUT/'before'/rel)==B['live'][rel]
 A['live'][rel]=sha(ROOT/rel)
A['postInstallTestMaintenance']={'files':{rel:sha(ROOT/rel) for rel in changes},'reason':'三宏阶段和有hash的历史规则来源；登记三条既有审定改写；原生source对比按声明的universal行模式规范化CRLF。仅测试变更，不改运行包或执行代码。'}
for rel,digest in A['live'].items():assert sha(ROOT/rel)==digest,rel
for rel,digest in A['runtimeFiles'].items():assert sha(ROOT/A['runtime']/rel)==digest,rel
for rel,digest in B['runtime'].items():assert sha(ROOT/B['parentRuntime']/rel)==digest,rel
doctor=read(OUT/'doctor-after.json')
assert doctor['errors']==['research mechanical validation has gaps']
assert doctor['checks']['runtime']['release']==p['release'] and doctor['checks']['program_chart']['ok']
assert doctor['checks']['research']['overlayFingerprint']=='aaf91ad9a2a838ddf2d7ce7ae2ea7eca17c760ce939c530e844b74003f5b85ac'
assert 'pass 143' in (OUT/'node-tests-after.log').read_text(encoding='utf-8-sig') and 'fail 0' in (OUT/'node-tests-after.log').read_text(encoding='utf-8-sig')
assert (OUT/'class-mapping-final.log').read_text(encoding='utf-8-sig').rstrip().endswith('OK')
post={'release':p['release'],'runtimeAndPreviousRuntimeVerified':True,'runtimeFiles':104,'nodePass':168,'pythonPass':40,'pythonSkipped':1,'doctorOnlyKnownResearchGap':True,'reportSha256':sha(OUT/'审查说明.md'),'evidence':{name:sha(OUT/name) for name in ['node-tests-after.log','class-mapping-final.log','single-method-after.log','doctor-after.json','host-chain.json','current-wire.json']}}
A['postInstallVerification']=post
(OUT/'activation-receipt.json').write_text(json.dumps(A,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(OUT/'post-install-verification.json').write_text(json.dumps(post,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in post.items() if k not in ['evidence','reportSha256']}))
