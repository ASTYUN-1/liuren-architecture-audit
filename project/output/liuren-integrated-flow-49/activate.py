"""Bind the integrated method and deterministic inspection extension locally."""
from pathlib import Path
import hashlib,json,os
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
enc=lambda d:(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=load(O/'before.json');p=load(R/'.opencode/liuren-active.json')
OLD=before['release'];NEW='20261112-integrated-flow-49';T=R/'runtime/liuren'/NEW
assert p['release']==OLD and T.exists()
assert all(sha(R/f)==h for f,h in before['frozen'].items())
# Live implementation/test edits are expected; all other saved files must
# still have their pre-change bytes. Preserve unrelated pre-existing edits.
edited={'tools/liuren-palace-strength.mjs','tools/liuren-compute-schema.mjs','tools/liuren-core-handoff.mjs','tools/tests/liuren-core-handoff.test.mjs','tools/tests/liuren-codex.test.mjs'}
assert all(sha(R/f)==h for f,h in before['files'].items() if f not in edited)
pending={}
short=('49版综合执行：先明原问与占类，观察气势后定侧重，依专项首取/条件递补，沿同一对象核旺衰、有效作用与制救。'
 '课体不另开裁决轮次；毕法核心只交客观成格，意象按BF法号按需查，45版格名辅助边界保留。'
 'strength可选review:true定点核状态依据、已选对象关系事实与季土双表差异；不自动新增作用或裁成败。'
 '官讼新增litigation专项。沿39版五项review核职责、首取/递补及计算范围，不增加长表或重派。')
cfg=load(R/'opencode.json');models={k:(v.get('model'),v.get('variant')) for k,v in cfg['agent'].items()}
cfg=json.loads(json.dumps(cfg,ensure_ascii=False).replace('runtime/liuren/'+OLD,'runtime/liuren/'+NEW))
cfg['agent']['liuren']['prompt']=short+'\n'+cfg['agent']['liuren']['prompt'];pending['opencode.json']=enc(cfg)
slim=load(R/'.opencode/oh-my-opencode-slim.jsonc');old_child=(slim['agents']['liuren-adjudicator'].get('model'),slim['agents']['liuren-adjudicator'].get('variant'))
slim['agents']['liuren-adjudicator']['prompt']=short+'\n'+slim['agents']['liuren-adjudicator']['prompt']
pending['.opencode/oh-my-opencode-slim.jsonc']=enc(slim)
for f in ['README.md','目录总索引.md']:
 text=(R/f).read_text(encoding='utf-8').replace('指向 `'+OLD+'`','指向 `'+NEW+'`')
 text=text.replace('runtime/liuren/'+OLD+'/','runtime/liuren/'+NEW+'/')
 pending[f]=(text.rstrip()+'\n\n'+short+'仅本机新任务，旧任务沿原绑定；重启OpenCode加载。详见docs/综合研判与旺衰核查-49.md。\n').encode('utf-8')
pending['AGENTS.md']=((R/'AGENTS.md').read_text(encoding='utf-8').rstrip()+'\n\n'+short+' 本机活动版'+NEW+'；完整盘与按需参考保留，17分类（含litigation），不新增裁决者。系数、空亡与合局暂缓决定不变。重启OpenCode新会话加载，Codex新任务读取新绑定；历史任务沿原文件，网站未发布。\n').encode('utf-8')
for f in ['docs/本机六壬完整研判流程.md','docs/本机六壬高效执行.md']:
 text=(R/f).read_text(encoding='utf-8');head,rest=text.split('\n',1)
 pending[f]=(head+'\n\n当前49版执行：'+short+' 详细能力边界与调用例见[综合研判与旺衰核查](综合研判与旺衰核查-49.md)。旧版历史段落不得覆盖当前judgment-core。\n\n'+rest.lstrip('\n')).encode('utf-8')

current=lambda f:hashlib.sha256(pending[f]).hexdigest() if f in pending else sha(R/f)
contract={'id':'liuren-integrated-analysis-49','scope':'local-opencode-and-codex','bifaCoreMode':'conditions-only',
 'mainline':'question-domain-focus-role-state-effective-action-counterevidence','newDomain':'litigation',
 'strengthReview':True,'existingCoefficientsChanged':False,'groupNumericsAdded':False,'extraAdjudications':0,
 'sources':'references/analysis-workflow-evidence.json','classificationSources':'references/classification-evidence.json',
 'predictiveValidationCount':0,'realModelStabilityVerified':False}
p['integratedAnalysis']=contract
p['bifaApplication']['coreMode']='conditions-only; full matched imagery retained in bound reference'
p['computeInterface']['strengthReview']=True
p['bookRetrieval']['compatibleMethodRelease']=NEW
for f in p['bookRetrieval']['files']:p['bookRetrieval']['files'][f]=current(f)
for name in ['loader-contract.json','references/shensha-policy.json','references/shensha-authority-evidence.json','references/confirmed-policy-register.json','reading-route.json']:
 d=load(T/name);d['release']=NEW
 if name in ['loader-contract.json','references/confirmed-policy-register.json']:
  d['integratedAnalysis']=contract
 if name=='loader-contract.json':
  d.update(parentRelease=OLD,authoringSource=O.relative_to(R).as_posix(),bookRetrieval=p['bookRetrieval'])
  d['sourceHashes']={f:current(f) for f in d['sourceHashes']}
  for f in edited:
   if f.startswith('tools/') and '/tests/' not in f:d['sourceHashes'][f]=current(f)
 (T/name).write_bytes(enc(d))
m=load(T/'manifest.json');m.update(release=NEW,parentRelease=OLD,authoringSource=O.relative_to(R).as_posix(),
 integratedAnalysis=contract,bookRetrieval=p['bookRetrieval'],bifaApplication=p['bifaApplication'],computeInterface=p['computeInterface'])
m['files']={f:sha(T/f) for f in m['files']}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest()
(T/'manifest.json').write_bytes(enc(m))
p.update(release=NEW,runtime=T.relative_to(R).as_posix(),previousRelease=OLD,methodVersion=m['version'],
 backup=O.relative_to(R).as_posix()+'/before',authoringSource=O.relative_to(R).as_posix())
p['workflowImplementation']={f:current(f) for f in p['workflowImplementation']}
pending['.opencode/liuren-active.json']=enc(p)
assert models=={k:(v.get('model'),v.get('variant')) for k,v in cfg['agent'].items()}
assert old_child==(slim['agents']['liuren-adjudicator'].get('model'),slim['agents']['liuren-adjudicator'].get('variant'))
assert all(sha(R/f)==h for f,h in before['frozen'].items())
for f in sorted(pending,key=lambda f:f=='.opencode/liuren-active.json'):
 target=R/f;temp=target.with_name(target.name+'.integrated49.tmp');temp.write_bytes(pending[f]);os.replace(temp,target)
after={'release':NEW,'runtime':p['runtime'],'files':{f:sha(R/f) for f in before['files']},
 'parent_unchanged':True,'models_unchanged':True,'new_files':['tools/tests/liuren-strength-review.test.mjs','docs/综合研判与旺衰核查-49.md'],
 'predictive_validation_count':0}
(O/'after.json').write_bytes(enc(after));print('Activated',NEW,'; frozen parent retained')
