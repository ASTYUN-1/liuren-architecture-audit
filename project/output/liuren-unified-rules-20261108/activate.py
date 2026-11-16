"""Register/refresh local32 and atomically switch its active pointer last."""
from pathlib import Path
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
OLD='20261107-slim-31'; NEW='20261108-unified-32'; R=ROOT/'runtime/liuren'/NEW
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text('utf-8-sig'))
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
p=load(ROOT/'.opencode/liuren-active.json');assert p['release'] in [OLD,NEW]
first=p['release']==OLD
before=load(OUT/'before.json')
assert all(sha(ROOT/'runtime/liuren'/OLD/rel)==h for rel,h in before['frozen31'].items())
assert all(sha(ROOT/rel)==h for rel,h in before['sourceBooks'].items())
if first:
 note='''

32版已确认口径更新（20261108-unified-32，覆盖旧指令中相反的专业摘要）：活动judgment-core完整载入U01—U11，主智能体准备和独立裁决者共同执行。喜旺恶衰、直接临生合与外来扶助、日干天干十二长生/支将五行十二气、制救、天时地利、空亡综合效应、四建分工及时间变化统一。已定规则不再作两派争点；真实未定边界见pending-conflicts的C01—C07。主智能体返回核对包含U口径一致性；具体错误附原句、U编号及绑定证据，依宿主一次补核协议处理，不自行折中改判。工具契约仍liuren-tools-31，模型与额度不变。仅本机；OpenCode重启后新会话加载，新Codex任务读取新指针；历史任务沿原绑定版本。记录见output/liuren-unified-rules-20261108/更新与验收说明.md。
'''
 for rel in ['AGENTS.md','README.md','docs/本机六壬高效执行.md','docs/本机六壬完整研判流程.md','docs/本机六壬稳定运行指南.md','docs/Codex大六壬工作流.md']:
  f=ROOT/rel;s=f.read_text('utf-8').replace('具体事实/引用错误','具体事实/引用/已确认U口径错误')
  if rel=='README.md':s=s.replace('指向 `'+OLD+'`','指向 `'+NEW+'`')
  if rel=='docs/Codex大六壬工作流.md':s=s.replace('详细理气方法保留，并未因宿主迁移修正其尚未解决的条件冲突','详细理气方法保留，已确认U口径随共用核心执行；具体尚未确认的边界见C01—C07')
  if rel=='docs/本机六壬高效执行.md':s=s.replace('当前本机31版','当前本机32版')
  if rel=='docs/本机六壬完整研判流程.md':s=s.replace('当前31版','当前32版')
  f.write_text(s+note,encoding='utf-8')
 f=ROOT/'目录总索引.md';f.write_text(f.read_text('utf-8').replace('runtime/liuren/'+OLD+'/','runtime/liuren/'+NEW+'/'),encoding='utf-8')
for name in ['loader-contract.json','manifest.json']:
 d=load(R/name);d['release']=NEW;d['parentRelease']=OLD;d['authoringSource']=OUT.relative_to(ROOT).as_posix()
 d['confirmedJudgmentPolicy']={'id':'liuren-unified-policy-32','rules':'U01-U11','mandatoryCore':True,'pendingRegistry':'pending-conflicts','sourceConsensus':False,'predictiveValidationCount':0}
 if 'computeInterface' in d:d['computeInterface']['release']=NEW
 if 'bookRetrieval' in d:d['bookRetrieval']['compatibleMethodRelease']=NEW
 if name=='loader-contract.json':d['sourceHashes']={rel:sha(ROOT/rel) for rel in d['sourceHashes']}
 dump(R/name,d)
q=load(R/'references/shensha-policy.json');q['release']=NEW;dump(R/'references/shensha-policy.json',q)
route=load(R/'reading-route.json');route['release']=NEW
route.setdefault('labels',{}).update({'confirmed-policy':'已确认判断规则','pending-conflicts':'具体待确认边界','confirmed-policy-evidence':'本轮已核连续书据'})
dump(R/'reading-route.json',route)
m=load(R/'manifest.json');m['files']={rel:sha(R/rel) for rel in m['files']};m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();dump(R/'manifest.json',m)
p.update(release=NEW,runtime=R.relative_to(ROOT).as_posix(),previousRelease=OLD,backup=(OUT/'before').relative_to(ROOT).as_posix(),authoringSource=OUT.relative_to(ROOT).as_posix(),methodVersion=m['version'])
p['confirmedJudgmentPolicy']=m['confirmedJudgmentPolicy']
if 'bookRetrieval' in p:p['bookRetrieval']['compatibleMethodRelease']=NEW
if 'computeInterface' in p:p['computeInterface']['release']=NEW
p['files']={rel:sha(ROOT/'.opencode/skills'/rel) for rel in p['files']}
p['workflowImplementation']={rel:sha(ROOT/rel) for rel in p['workflowImplementation']}
p['bookRetrieval']['files']={rel:sha(ROOT/rel) for rel in p['bookRetrieval']['files']}
tmp=ROOT/'.opencode/liuren-active.unified32.tmp';dump(tmp,p);os.replace(tmp,ROOT/'.opencode/liuren-active.json')
dump(OUT/'activation.json',{'release':NEW,'previousRelease':OLD,'scope':'local OpenCode and Codex shared methods','before':before['files'],'after':{rel:sha(ROOT/rel) for rel in before['files']},'frozen31Intact':True,'sourceBooksIntact':True,'paidModelCalls':0,'predictiveValidationCount':0})
print('Local32 registered; frozen31/source books intact; host models unchanged.')
