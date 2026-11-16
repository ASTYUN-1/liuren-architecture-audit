"""Strengthen the existing numerical-answer obligation without choosing numbers."""
from pathlib import Path
import hashlib
import json
import os
import shutil

R=Path(__file__).resolve().parents[2]
O=Path(__file__).resolve().parent
OLD='20261111-quantity-logic-46'
NEW='20261111-numeric-answer-47'
load=lambda p:json.loads(p.read_text('utf-8-sig'))
enc=lambda d:(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=load(R/'.opencode/liuren-active.json')
assert p['release']==OLD
assert not (O/'before.json').exists()
files=['.opencode/liuren-active.json','opencode.json','.opencode/oh-my-opencode-slim.jsonc',
 '.opencode/skills/liuren/daliuren/SKILL.md','integrations/codex/daliuren-codex/SKILL.md',
 'integrations/codex/daliuren-codex/references/host.md','README.md','目录总索引.md','AGENTS.md']
before={'release':OLD,'runtime':p['runtime'],'files':{f:sha(R/f) for f in files},
 'frozen':{f.relative_to(R).as_posix():sha(f) for f in (R/p['runtime']).rglob('*') if f.is_file()}}
for f in files:
 dst=O/'before'/f;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(R/f,dst)
(O/'before.json').write_bytes(enc(before))
runtime=R/'runtime/liuren'/NEW
assert not runtime.exists()
shutil.copytree(R/p['runtime'],runtime)
short=('用户明确想要数字（含“大概多少、给个数、最可能第几”等上下文意图）时，'
 '先实际尝试取数并给最有依据的具体估计值及口径，可附范围；不以定性词、宽区间或方法限制代替。'
 '数值估计不要求保证精确或唯一通法，允许说明依据的近似推估，区分程序计算与模型估计。'
 '只有查法及必要计算后仍无可辩护数值，才说明具体缺步和已完成的尝试；不随机凑数。')
detail='''## 用户有数字意图时先完成数值回答（47版）

识别原问及上下文的数值意图，不要求用户说“取数”或使用固定关键词。“大概多少”“你给个数”“最可能排第几”等均应沿原任务接数量方法；结合上下文核清所指对象，不把用户只问有无、成败或前后倾向自动扩大成精确数字任务。task_basis保留原句及上下文理由，接口词句识别不替代语义判断。

先选对象和适用方法，查看所需原法，执行必要计算与有据修正，再在逐问结论给一个最有依据的具体数值及单位/名次/等级口径，例如“主估约N分”“主选第N名”。范围用于补充误差与条件；用户只要区间或候选时按其要求。不能默认只给区间、只说偏多偏少或仅列出方法而不尝试得数。

“具体数值”可以是近似估计，不要求已有唯一算法、统计校准或保证个位命中。允许结合有源数法、已核作用及题设约束作可解释的近似推估，说明其中哪一步是推估以及为何选这个数；不能将其冒充程序精确算出或古法明定。区间已有依据且中心值有代表性时可以选主估值，但不能无据取中点或平均候选。完整有源算式可直接形成点值，不把“还没有精确通法”当作停止理由。

确实查不到适用方法，或关键取位/运算/量级映射未明到无法形成可辩护估计时，具体说清查了什么、算到哪一步、还缺什么，给现有方法支持的程度；不虚构一个数填满答案。缺口应针对该数值，不扩大为“这种事不能取数”。已有可解释估计时，以“约/主估”标明一次，不再用后文将答案全部撤回。无需重复查同版已读资料，也不增加裁决轮次。

主智能体沿现有answer_constraints核“用户要数却只给定性或范围”，沿calculation_scope核尝试和估计依据。若报告有具体缺口，附原句及绑定规则走原有一次补核；主智能体不自行补数字或改裁决。程序继续只做计算和传输，不以数字是否出现自动验收专业正确。
'''
for rel in ['methods/quantity.md','references/direct-answer.md']:
 f=runtime/rel;f.write_text(f.read_text('utf-8').rstrip()+'\n\n'+detail,encoding='utf-8')
for rel in ['references/judgment-core.md','methods/adjudication.md','methods/report.md',
 'references/consistency-audit.md','references/quantity-rank.md']:
 f=runtime/rel;f.write_text(f.read_text('utf-8').rstrip()+'\n\n## 数字意图与主估值（47版）\n\n'+short+'\n详见quantity及direct-answer；沿现有一次补核，不由主智能体代填数值。\n',encoding='utf-8')
pending={}
for rel in files:
 if rel in ['opencode.json','.opencode/oh-my-opencode-slim.jsonc','.opencode/liuren-active.json']:continue
 s=(R/rel).read_text('utf-8').replace('runtime/liuren/'+OLD+'/', 'runtime/liuren/'+NEW+'/').replace('指向 `'+OLD+'`','指向 `'+NEW+'`')
 pending[rel]=(s.rstrip()+'\n\n47版数字作答：'+short+'\n').encode('utf-8')
cfg=load(R/'opencode.json')
models={k:(v.get('model'),v.get('variant')) for k,v in cfg['agent'].items()}
cfg=json.loads(json.dumps(cfg,ensure_ascii=False).replace('runtime/liuren/'+OLD,'runtime/liuren/'+NEW))
cfg['agent']['liuren']['prompt']=short+'\n'+cfg['agent']['liuren']['prompt']
assert models=={k:(v.get('model'),v.get('variant')) for k,v in cfg['agent'].items()}
pending['opencode.json']=enc(cfg)
slim=load(R/'.opencode/oh-my-opencode-slim.jsonc')
slim['agents']['liuren-adjudicator']['prompt']=short+'\n'+slim['agents']['liuren-adjudicator']['prompt']
pending['.opencode/oh-my-opencode-slim.jsonc']=enc(slim)
current_sha=lambda f:hashlib.sha256(pending[f]).hexdigest() if f in pending else sha(R/f)
contract={'id':'numeric-answer-47','concreteEstimatePreferred':True,'semanticNumericIntent':True,
 'attemptBeforeAbstention':True,'modelEstimateDistinctFromComputation':True,
 'fabricatedNumberAllowed':False,'extraAdjudications':0,'predictiveValidationCount':0}
p.update(release=NEW,runtime=runtime.relative_to(R).as_posix(),previousRelease=OLD,
 backup=O.relative_to(R).as_posix()+'/before',authoringSource=O.relative_to(R).as_posix(),numericAnswer=contract)
p['bookRetrieval']['compatibleMethodRelease']=NEW
for name in ['loader-contract.json','references/shensha-policy.json','references/shensha-authority-evidence.json',
 'references/confirmed-policy-register.json','reading-route.json']:
 d=load(runtime/name);d['release']=NEW
 if name=='loader-contract.json':
  d.update(parentRelease=OLD,authoringSource=p['authoringSource'],numericAnswer=contract)
  d['sourceHashes']={f:current_sha(f) for f in d['sourceHashes']}
 (runtime/name).write_bytes(enc(d))
m=load(runtime/'manifest.json');m.update(release=NEW,parentRelease=OLD,authoringSource=p['authoringSource'],numericAnswer=contract)
if 'bookRetrieval' in m:m['bookRetrieval']['compatibleMethodRelease']=NEW
m['modules']['quantity']['trigger']='用户原问及上下文明确要数，包括估数、名次、等级与变化量；不要求固定关键词'
m['files']={f:sha(runtime/f) for f in m['files']}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest()
(runtime/'manifest.json').write_bytes(enc(m))
p['methodVersion']=m['version'];p['workflowImplementation']={f:current_sha(f) for f in p['workflowImplementation']}
p['files']={f:current_sha('.opencode/skills/'+f) for f in p['files']}
pending['.opencode/liuren-active.json']=enc(p)
assert all(sha(R/f)==h for f,h in before['frozen'].items())
for rel in sorted(pending,key=lambda f:f=='.opencode/liuren-active.json'):
 target=R/rel;tmp=target.with_name(target.name+'.numeric47.tmp');tmp.write_bytes(pending[rel]);os.replace(tmp,target)
(O/'after.json').write_bytes(enc({'release':NEW,'runtime':p['runtime'],
 'files':{f:sha(R/f) for f in files},'frozen46_unchanged':True,'models_unchanged':True}))
print('Activated',NEW,'; frozen46 unchanged; no model calls')
