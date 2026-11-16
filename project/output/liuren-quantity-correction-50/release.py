"""Build and activate a fresh local release; never overwrite the frozen parent."""
from pathlib import Path
import hashlib,json,shutil,os
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
enc=lambda d:(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=load(O/'before.json');p=load(R/'.opencode/liuren-active.json')
OLD=b['release'];NEW='20261112-quantity-correction-50';T=R/'runtime/liuren'/NEW
assert p['release']==OLD and not T.exists(),'Do not rerun against an existing candidate or changed pointer'
assert all(sha(R/f)==h for f,h in b['frozen'].items())
edited={'tools/liuren-consistency-audit.mjs','tools/liuren-adjudication-files.mjs','tools/liuren-method-tools.mjs'}
assert all(sha(R/f)==h for f,h in b['files'].items() if f not in edited)
shutil.copytree(R/b['runtime'],T)
shutil.copyfile(O/'数量修正规则.md',T/'references/quantity-correction.md')
shutil.copyfile(O/'原文证据.json',T/'references/quantity-correction-evidence.json')
short=('50版数量修正：先基数、后核综合旺衰与数量兑现，实际用expression算最终数；'
 '按用户研究约定允许说明依据的比例估计，4—7/2—3仅示意，不设硬阈值或默认指数/5。'
 '分数等实量的数量主类本身旬空且同层未扣时默认减半；已含或专项/阶段例外须说明，序数日期不机械折半。'
 '数值问audit.quantity_reviews绑定本任务基数、strength及最终数回执，核步骤与旬空处理，不能只写未执行；不新增裁决轮次。')
section='''## 50版数量兑现：用户研究约定与实际执行

原书数随旺衰增减的方向与本机指数的比例估计分开。基数是中间结果；查本法已含的旺相加乘/休囚分支后，核综合旺衰、旬空及实际实现份额。允许有依据并标明身份的比例估计，不能因为无唯一古法系数便跳过；不把指数/5作为自动通法。用户所举5附近、4—7直取及2—3折半是研究示意，不编成硬阈值或失用线。

分数、实得钱物等数量主类在所判阶段本身旬空，基数尚未含该数量减损时默认实际减半；状态层strength已计空不能替代。数量比例已含同一次空减则不再乘半；独立气弱与空半叠加须说明独立依据。其他空位、序数/日期/编号不机械套用；源法或可靠阶段解除有例外须具体说明。56乘半是28，不能见已知反馈22再倒选系数。

数值问沿同轮判断给audit.quantity_reviews，每问一项，绑定真实基数、strength和最终quantity回执，登记修正步骤及其原法/用户研究/模型估计身份、旬空处理及正文引句；详形状见consistency_guide。保留基数也说明为何可用；无可辩护估计则登记unresolved和具体缺步，不编数或把基础数冒充最终量。主智能体沿原calculation_scope核算术、职责和比例理由；程序仅核回执与声明，不验证专业准确率。详见quantity-correction及其原文证据。

'''
for rel in ['references/judgment-core.md','methods/quantity.md']:
 f=T/rel;s=f.read_text(encoding='utf-8');head,rest=s.split('\n',1)
 s=head+'\n\n'+section+rest.lstrip('\n')
 s=s.replace('禁止指数/5等自创换算','不得将指数/5默认作通法；按50版允许有据且标明身份的研究比例估计')
 f.write_text(s,encoding='utf-8')
f=T/'references/quantity-strength.md';s=f.read_text(encoding='utf-8')
s=s.replace('不得创造strength_index/5、2.9/10等自动换算','不得把strength_index/5、2.9/10等设为自动换算通法；50版依用户约定允许说明参照及依据的个案比例估计')
head,rest=s.split('\n',1);f.write_text(head+'\n\n'+section+rest.lstrip('\n'),encoding='utf-8')
for rel in ['references/deterministic-tools.md','methods/adjudication.md','references/adjudicator-prompt.md']:
 f=T/rel;f.write_text(f.read_text(encoding='utf-8').rstrip()+'\n\n'+short+'完整条件查quantity-correction；字段形状见consistency_guide。\n',encoding='utf-8')
f=T/'domains/exam.md';s=f.read_text(encoding='utf-8').replace('资格重河魁/戌印','职称资格取得重河魁/戌印')
s+='\n50版：问具体分数不能自动沿用前问过关类神。《理法》考后幕贵分数与《毕法》日常成绩朱雀各有适用分支，须说明本问类型/阶段及首取理由，不按算得高低择类。专业证书考试不因有证书二字便改取印绶。基数后按quantity-correction核气态及旬空减数，落实真实运算和quantity_reviews。\n'
f.write_text(s,encoding='utf-8')
f=T/'references/classification-priority.md';s=f.read_text(encoding='utf-8').replace('资格证书重河魁/戌印','职称评定及其资格证书重河魁/戌印')
f.write_text(s,encoding='utf-8')
m=load(T/'manifest.json')
for key,file in [('quantity-correction','references/quantity-correction.md'),('quantity-correction-evidence','references/quantity-correction-evidence.json')]:
 m['modules'][key]={'file':file,'required':False,'requires':[],'trigger':'数值问核基数、旺衰与实际修正；原文按争点读取'}
 m['files'][file]=sha(T/file)
contract={'id':'liuren-quantity-correction-50','scope':'local-opencode-and-codex','receiptReviewRequired':True,
 'stateVoidIsQuantityVoid':False,'defaultActualQuantityVoidFactor':0.5,'fixedStrengthThresholds':False,
 'automaticIndexRatio':False,'proportionalEstimates':'declared-user-research-or-model-estimate',
 'sources':'references/quantity-correction-evidence.json','predictiveValidationCount':0,'extraAdjudications':0}
pending={}
cfg=load(R/'opencode.json');cfg=json.loads(json.dumps(cfg,ensure_ascii=False).replace('runtime/liuren/'+OLD,'runtime/liuren/'+NEW))
cfg['agent']['liuren']['prompt']=short+'\n'+cfg['agent']['liuren']['prompt'];pending['opencode.json']=enc(cfg)
slim=load(R/'.opencode/oh-my-opencode-slim.jsonc');slim['agents']['liuren-adjudicator']['prompt']=short+'\n'+slim['agents']['liuren-adjudicator']['prompt'];pending['.opencode/oh-my-opencode-slim.jsonc']=enc(slim)
for f in ['README.md','目录总索引.md','AGENTS.md','docs/本机六壬高效执行.md','docs/本机六壬完整研判流程.md']:
 s=(R/f).read_text(encoding='utf-8')
 if f in ['README.md','目录总索引.md']:s=s.replace('runtime/liuren/'+OLD+'/','runtime/liuren/'+NEW+'/').replace('指向 `'+OLD+'`','指向 `'+NEW+'`')
 pending[f]=(s.rstrip()+'\n\n'+short+' 本机活动版'+NEW+'；OpenCode重启新会话加载，Codex新任务绑定，旧任务不改。见docs/数量修正与原文核查-50.md；网站未发布。\n').encode('utf-8')
current=lambda f:hashlib.sha256(pending[f]).hexdigest() if f in pending else sha(R/f)
p['quantityCorrection']=contract;p['consistencyAudit']['quantityReviewRequired']=True
p['bookRetrieval']['compatibleMethodRelease']=NEW
for f in p['bookRetrieval']['files']:p['bookRetrieval']['files'][f]=current(f)
for name in ['loader-contract.json','references/shensha-policy.json','references/shensha-authority-evidence.json','references/confirmed-policy-register.json','reading-route.json']:
 d=load(T/name);d['release']=NEW
 if name in ['loader-contract.json','references/confirmed-policy-register.json']:d['quantityCorrection']=contract
 if name=='loader-contract.json':
  d.update(parentRelease=OLD,authoringSource=O.relative_to(R).as_posix(),bookRetrieval=p['bookRetrieval'])
  d['sourceHashes']={f:current(f) for f in d['sourceHashes']}
  for f in edited|{'tools/liuren-quantity-review.mjs'}:d['sourceHashes'][f]=current(f)
 (T/name).write_bytes(enc(d))
m.update(release=NEW,parentRelease=OLD,authoringSource=O.relative_to(R).as_posix(),quantityCorrection=contract,bookRetrieval=p['bookRetrieval'],consistencyAudit=p['consistencyAudit'])
m['files']={f:sha(T/f) for f in m['files']};m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();(T/'manifest.json').write_bytes(enc(m))
p.update(release=NEW,runtime=T.relative_to(R).as_posix(),previousRelease=OLD,methodVersion=m['version'],backup=O.relative_to(R).as_posix()+'/before',authoringSource=O.relative_to(R).as_posix())
p['workflowImplementation']={f:current(f) for f in p['workflowImplementation']};p['workflowImplementation']['tools/liuren-quantity-review.mjs']=current('tools/liuren-quantity-review.mjs')
pending['.opencode/liuren-active.json']=enc(p)
assert all(sha(R/f)==h for f,h in b['frozen'].items())
for f in sorted(pending,key=lambda f:f=='.opencode/liuren-active.json'):
 dest=R/f;tmp=dest.with_name(dest.name+'.quantity50.tmp');tmp.write_bytes(pending[f]);os.replace(tmp,dest)
after={'release':NEW,'runtime':p['runtime'],'files':{f:sha(R/f) for f in b['files']},'new_files':['tools/liuren-quantity-review.mjs','tools/tests/liuren-quantity-review.test.mjs','docs/数量修正与原文核查-50.md'],'parent_unchanged':True,'predictive_validation_count':0}
(O/'after.json').write_bytes(enc(after));print('Activated',NEW)
