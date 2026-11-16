"""Publish a new local runtime; preserve parent bytes and backup live files."""
from pathlib import Path
import hashlib,json,shutil,os,re
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
enc=lambda d:(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
b=load(O/'before.json');p=load(R/'.opencode/liuren-active.json')
OLD=b['release'];NEW='20261112-strength-quantity-51';T=R/'runtime/liuren'/NEW
assert p['release']==OLD and not T.exists(),'Refuse rerun or changed active pointer'
assert all(sha(R/f)==h for f,h in b['frozen'].items()),'Frozen parent changed'
changed={f for f,h in b['files'].items() if sha(R/f)!=h}
allowed={'tools/liuren-strength-engine.mjs','tools/liuren-palace-strength.mjs','tools/liuren-quantity-review.mjs',
 'tools/liuren-compute-schema.mjs','tools/liuren-deterministic-io.mjs','tools/liuren-adjudication-files.mjs',
 'tools/liuren-codex.mjs','tools/liuren-method-tools.mjs','.opencode/plugins/liuren-adjudication.ts',
 'tools/tests/liuren-quantity-review.test.mjs'}
assert changed<=allowed,changed-allowed
shutil.copytree(R/b['runtime'],T)
short=('51版旺衰取数：strength增加同范围真实无空重算quantity_basis，原系数不改。'
 '有明确适用原法优先source，已按气态选加乘不再叠实验倍率；否则说明理由以raw expression进入experimental，'
 '只按without_void用固定实验分段(≤2.5半、2.5至4连续到1、4至6本数、6至7.5到1.2、以上封1.2)，未校准。'
 '空半独立声明且不重复；源法无明文不强制再半，说明研究采用或例外。量级/单位/上限另定，超界不截断。'
 '新数值问最终用quantity_adjustment引用本任务基数/strength回执，复制review进quantity_reviews；序数日期编号不套倍率/空半。'
 '原问取类、有效作用、制救与最强反证主线不变；不增裁决轮次，不把强弱换成概率或自动成败。')
section='''## 51版：数量路径与旺衰因素分离

数值问先按本问分类、数量含义及阶段取主类，天将类定位所乘T:支；明确总额/实得/净额、成绩/过关、数量/序数。优先用有明确适用条件的原法source；基数已经因旺衰选加/乘/半，不再乘实验强弱系数。原法条件不足时，说明转用理由，以未含气态与空减的raw expression本数进入experimental，不得两路计算后择有利结果。

strength保留含空的实际状态，并输出相同对象/关系从头重算的without_void；选取跨宫有效关系后补算，single_palace不冒充综合，既有旺衰系数和合局暂缓不变。实验分段为E≤2.5乘0.5，2.5至4连续过渡至1，4至6乘1，6至7.5过渡至1.2，7.5以上维持1.2；只用without_void。此为项目未校准参数，5仅模型基准，非北海原文；强旺不自动进十百，0不自动判失败。

空亡单独登记：已含数量减损不再扣；实验路径在实际数量主类本身旬空且该阶段应减量时，可采用一次项目研究半数。source路径依原法；无明文不强制所有源法再半，须明确研究/估计补充或阶段例外。不因状态含空便声称数量已减，也不用含空指数再乘半。坐空/将空/身空不等同本数量类自身空。序数、日期、编号禁止实验倍率及空半。

量级和单位独立依据已知因，不以旺衰指数换满分百分比或奖金档次；财源/竞买者规模不等于个人所得。已知上下限照实登记，超界复核方法和量级，不删边界或截满分。新任务最终用quantity_adjustment消费本任务真实基数与strength回执（quantity三选一），保留本数同样兑现；复制返回review补question_id/final_receipt_sha256/report_quote进audit.quantity_reviews。具体字段查quantity-correction/consistency_guide。缺步先实际尝试后明示unresolved，不编数、不新增裁决轮次。

'''
for rel in ['references/judgment-core.md','methods/quantity.md']:
 f=T/rel;s=f.read_text(encoding='utf-8')
 s=re.sub(r'## 50版数量兑现：用户研究约定与实际执行\n.*?(?=\n(?:本页|#))','',s,flags=re.S,count=1) if rel.endswith('quantity.md') else s
 # The inserted v50 section is a fixed four-paragraph prefix. Remove it by
 # its last sentence rather than guessing the next heading in either file.
 if '## 50版数量兑现：用户研究约定与实际执行' in s:
  a=s.index('## 50版数量兑现：用户研究约定与实际执行');marker='详见quantity-correction及其原文证据。'
  z=s.index(marker,a)+len(marker);s=s[:a]+s[z:].lstrip('\n')
 s='\n'.join(line for line in s.splitlines() if not line.startswith('- **取数和旺衰分层**：'))
 head,rest=s.split('\n',1);f.write_text(head+'\n\n'+section+rest.lstrip('\n'),encoding='utf-8')
for rel in ['references/deterministic-tools.md','methods/adjudication.md','references/adjudicator-prompt.md']:
 f=T/rel;s=f.read_text(encoding='utf-8');s='\n'.join(l for l in s.splitlines() if not l.startswith('50版数量修正：'))
 f.write_text(s.rstrip()+'\n\n'+short+'完整字段查quantity-correction。\n',encoding='utf-8')
shutil.copyfile(O/'数量取用与修正规则.md',T/'references/quantity-correction.md')
shutil.copyfile(O/'旺衰与取数配合.md',T/'references/quantity-strength.md')
research=R/'output/beihai-quantity-method-review-20261112'
shutil.copyfile(research/'原文证据.json',T/'references/strength-quantity-evidence.json')
f=T/'domains/exam.md';s=f.read_text(encoding='utf-8').replace('50版：','51版：').replace('基数后按quantity-correction核气态及旬空减数，落实真实运算和quantity_reviews。','按quantity-correction分source/experimental路径、独立核量级与空减，最终quantity_adjustment回执进入quantity_reviews。已知满分登记上限，不按指数换得分比例。');f.write_text(s,encoding='utf-8')
contract={'id':'liuren-strength-quantity-51','scope':'local-opencode-and-codex','receiptReviewRequired':True,'couplingRequired':True,
 'stateVoidIsQuantityVoid':False,'defaultActualQuantityVoidFactor':None,'experimentalActualQuantityVoidFactor':0.5,
 'sourceVoidPolicy':'explicit-source-or-declared-research-exception','fixedStrengthThresholds':'experimental-path-only',
 'automaticIndexRatio':False,'experimentalProfile':'quantity-band-experiment-51','calibrated':False,
 'sources':'references/strength-quantity-evidence.json','predictiveValidationCount':0,'extraAdjudications':0}
pending={}
cfg=load(R/'opencode.json');cfg=json.loads(json.dumps(cfg,ensure_ascii=False).replace('runtime/liuren/'+OLD,'runtime/liuren/'+NEW))
cfg['agent']['liuren']['prompt']=short+'\n'+'\n'.join(l for l in cfg['agent']['liuren']['prompt'].splitlines() if not l.startswith('50版数量修正：'));pending['opencode.json']=enc(cfg)
slim=load(R/'.opencode/oh-my-opencode-slim.jsonc');prompt=slim['agents']['liuren-adjudicator']['prompt']
slim['agents']['liuren-adjudicator']['prompt']=short+'\n'+'\n'.join(l for l in prompt.splitlines() if not l.startswith('50版数量修正：'));pending['.opencode/oh-my-opencode-slim.jsonc']=enc(slim)
for name in ['README.md','目录总索引.md','AGENTS.md','docs/本机六壬高效执行.md','docs/本机六壬完整研判流程.md']:
 s=(R/name).read_text(encoding='utf-8');s=s.replace('指向 `'+OLD+'`','指向 `'+NEW+'`').replace('runtime/liuren/'+OLD+'/','runtime/liuren/'+NEW+'/')
 # Historical release prose stays for provenance, explicitly superseded below.
 s+='\n\n51版现行规则（覆盖上方50版数量修正的相反要求）：'+short+' 本机'+NEW+'；OpenCode重启后新会话，Codex新任务绑定，旧任务不追改；网站未发布。见docs/旺衰与取数联动-51.md。\n'
 pending[name]=s.encode('utf-8')
current=lambda f:hashlib.sha256(pending[f]).hexdigest() if f in pending else sha(R/f)
p['quantityCorrection']=contract;p['consistencyAudit']['quantityReviewRequired']=True;p['consistencyAudit']['quantityCouplingRequired']=True
p['bookRetrieval']['compatibleMethodRelease']=NEW
for f in p['bookRetrieval']['files']:p['bookRetrieval']['files'][f]=current(f)
p['computeInterface'].update(quantityAdjustment=True,strengthVoidFreeRecomputation=True,
 transportValidation='actual native schema serialization plus host root reconstruction; no fresh HTTP/provider capture; execution checked separately',
 transportEvidence='output/liuren-strength-quantity-51/native-schema.json')
for name in ['loader-contract.json','references/shensha-policy.json','references/shensha-authority-evidence.json','references/confirmed-policy-register.json','reading-route.json']:
 d=load(T/name);d['release']=NEW
 if name in ['loader-contract.json','references/confirmed-policy-register.json']:d['quantityCorrection']=contract
 if name=='loader-contract.json':
  d.update(parentRelease=OLD,authoringSource=O.relative_to(R).as_posix(),bookRetrieval=p['bookRetrieval'])
  d['sourceHashes']={f:current(f) for f in d['sourceHashes']};d['sourceHashes']['tools/liuren-quantity-adjustment.mjs']=current('tools/liuren-quantity-adjustment.mjs')
 (T/name).write_bytes(enc(d))
m=load(T/'manifest.json');m['modules']['strength-quantity-evidence']={'file':'references/strength-quantity-evidence.json','required':False,'requires':[],'trigger':'旺衰数法、空亡叠减、倍进和量级原文争点'}
m['files']['references/strength-quantity-evidence.json']=sha(T/'references/strength-quantity-evidence.json')
m.update(release=NEW,parentRelease=OLD,authoringSource=O.relative_to(R).as_posix(),quantityCorrection=contract,bookRetrieval=p['bookRetrieval'],consistencyAudit=p['consistencyAudit'],computeInterface=p['computeInterface'])
m['files']={f:sha(T/f) for f in m['files']};m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();(T/'manifest.json').write_bytes(enc(m))
p.update(release=NEW,runtime=T.relative_to(R).as_posix(),previousRelease=OLD,methodVersion=m['version'],backup=O.relative_to(R).as_posix()+'/before',authoringSource=O.relative_to(R).as_posix())
p['workflowImplementation']={f:current(f) for f in p['workflowImplementation']};p['workflowImplementation']['tools/liuren-quantity-adjustment.mjs']=current('tools/liuren-quantity-adjustment.mjs')
pending['.opencode/liuren-active.json']=enc(p)
assert all(sha(R/f)==h for f,h in b['frozen'].items())
for f in sorted(pending,key=lambda f:f=='.opencode/liuren-active.json'):
 dest=R/f;tmp=dest.with_name(dest.name+'.quantity51.tmp');tmp.write_bytes(pending[f]);os.replace(tmp,dest)
after={'release':NEW,'runtime':p['runtime'],'files':{f:sha(R/f) for f in b['files']},'new_files':['tools/liuren-quantity-adjustment.mjs','tools/tests/liuren-strength-quantity.test.mjs','docs/旺衰与取数联动-51.md'],
 'parent_unchanged':True,'predictive_validation_count':0}
(O/'after.json').write_bytes(enc(after));print('Activated',NEW)
