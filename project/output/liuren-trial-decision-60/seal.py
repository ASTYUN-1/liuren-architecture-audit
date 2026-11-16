from pathlib import Path
import json,hashlib,shutil
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
old='20261115-trial-decision-59';new='20261115-trial-decision-60';B=R/'runtime/liuren'/old;T=R/'runtime/liuren'/new
b=load(O/'before.json');assert all(sha(R/f)==h for f,h in b['frozen'].items())
p=load(O/'before/.opencode/liuren-active.json');m=load(B/'manifest.json');c=load(B/'loader-contract.json')
helper=R/'tools/liuren-trial-decision.mjs';s=(O/'helper.mjs').read_text('utf8').replace("id:'liuren-trial-decision-59'","id:'liuren-trial-decision-60'");helper.write_bytes(s.encode('utf8'))
test=R/'tools/tests/liuren-trial-decision.test.mjs';test.write_bytes((O/'test.mjs').read_text('utf8').replace("'liuren-trial-decision-59'","'liuren-trial-decision-60'").encode('utf8'))
test=R/'tools/tests/liuren-class-selection-trial.test.mjs';test.write_bytes((O/'before/tools/tests/liuren-class-selection-trial.test.mjs').read_text('utf8').replace("'liuren-trial-decision-59'","'liuren-trial-decision-60'").encode('utf8'))
entry=(B/'entry.md').read_text('utf8')+'\n已引用的官鬼即使未进入strength actors，也必须读取排盘trial_chart_basis的状态解释；不以“没有强压”“克不动”掩去衰鬼凶态。不切题者不引用，不虚构其旺衰。回答不扩展行动建议、金额大小、具体时间或已知结果。\n'
(T/'entry.md').write_text(entry,'utf8');(R/'.opencode/skills/liuren/daliuren/SKILL.md').write_text(entry,'utf8')
short=(B/'references/class-selection-trial.md').read_text('utf8').replace('短答试验 59','短答试验 60')+'\n补充：已引用的日鬼即使未进补算，也按排盘trial_chart_basis读其旺衰；不得把衰鬼或零称为“不旺不衰”“没有强压”。不切题者不纳入，不编其状态。输出不扩展行动建议、金额大小或具体应期。\n'
(T/'references/class-selection-trial.md').write_text(short,'utf8')
cfg=load(O/'before/opencode.json');cfg['agent']['liuren']['prompt']=entry.split('# 分类与取用试验',1)[1].strip()+'\n权限拒绝不绕过，工作流开发另行授权。'
cfg['agent']['liuren']['permission']['read']={k.replace(old,new):v for k,v in cfg['agent']['liuren']['permission']['read'].items()};save(R/'opencode.json',cfg)
for rel in ['README.md','目录总索引.md']:
 s=(O/'before'/rel).read_text('utf8').replace('59版分类取用短答试验','60版分类取用短答试验').replace(old,new).replace('output/liuren-trial-decision-59/定位与修改说明.md','output/liuren-trial-decision-60/修正说明.md');(R/rel).write_text(s,'utf8')
p.update(release=new,previousRelease=old,runtime='runtime/liuren/'+new,backup='output/liuren-trial-decision-60/before',authoringSource='output/liuren-trial-decision-60')
p['classSelectionTrial'].update(id='class-selection-decision-60',rollbackRelease=old)
p['classSelectionTrial']['decisionBasis'].update(id='liuren-trial-decision-60',unselected_day_ghost_chart_meaning=True)
for d in [m,c]:d.update(release=new,parentRelease=old,classSelectionTrial=p['classSelectionTrial'])
for rel in ['reading-route.json','references/shensha-policy.json','references/shensha-authority-evidence.json','references/confirmed-policy-register.json']:
 d=load(B/rel);d['release']=new;save(T/rel,d)
for target in [p['workflowImplementation'],c['sourceHashes']]:
 for f in target:target[f]=sha(R/f)
p['files']={f:sha(R/'.opencode/skills'/f) for f in p['files']}
p['bookRetrieval']['files']={f:sha(R/f) for f in p['bookRetrieval']['files']}
for d in [m,c]:d['bookRetrieval']=p['bookRetrieval']
save(T/'loader-contract.json',c);m['files']={f:sha(T/f) for f in m['files']};m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();save(T/'manifest.json',m)
p['methodVersion']=m['version'];save(R/'.opencode/liuren-active.json',p)
save(O/'after.json',{'release':new,'files':{f:sha(R/f) for f in b['files']},'frozen_59_unchanged':True})
shutil.copy2(R/'output/liuren-trial-decision-59/rollback.py',O/'rollback.py')
print('Activated',new)
