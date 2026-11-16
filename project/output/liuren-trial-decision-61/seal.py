from pathlib import Path
import json, hashlib, shutil
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
old='20261115-trial-decision-60';new='20261115-trial-decision-61';B=R/'runtime/liuren'/old;T=R/'runtime/liuren'/new
b=load(O/'before.json');assert all(sha(R/f)==h for f,h in b['frozen'].items())
p=load(O/'before/.opencode/liuren-active.json');m=load(B/'manifest.json');c=load(B/'loader-contract.json')
entry=(O/'entry.md').read_text('utf8');short=(O/'class-selection-trial.md').read_text('utf8')
(T/'entry.md').write_text(entry,'utf8');(R/'.opencode/skills/liuren/daliuren/SKILL.md').write_text(entry,'utf8')
(T/'references/class-selection-trial.md').write_text(short,'utf8')
cfg=load(O/'before/opencode.json');cfg['agent']['liuren']['prompt']=entry.split('# 分类与取用试验',1)[1].strip()+'\n权限拒绝不绕过，工作流开发另行授权。'
cfg['agent']['liuren']['permission']['read']={k.replace(old,new):v for k,v in cfg['agent']['liuren']['permission']['read'].items()};save(R/'opencode.json',cfg)
for rel in ['README.md','目录总索引.md']:
 s=(O/'before'/rel).read_text('utf8').replace('60版分类取用短答试验','61版分类取用短答试验').replace(old,new).replace('output/liuren-trial-decision-60/修正说明.md','output/liuren-trial-decision-61/修正说明.md')
 s=s.replace('取类后结合旺衰及制救','仅用五行月令旺衰并固定核初传')
 (R/rel).write_text(s,'utf8')
p.update(release=new,previousRelease=old,runtime='runtime/liuren/'+new,backup='output/liuren-trial-decision-61/before',authoringSource='output/liuren-trial-decision-61')
p['classSelectionTrial'].update(id='class-selection-decision-61',rollbackRelease=old,strengthPolicy='five-element month qi only (quarter-earth); initial transmission must be interpreted in event role')
p['classSelectionTrial']['decisionBasis'].update(id='liuren-trial-decision-61',single_season_profile='quarter-earth',initial_transmission_required=True,numeric_algorithms_changed=False)
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
save(O/'after.json',{'release':new,'files':{f:sha(R/f) for f in [*b['files'],*b['new_files']]},'frozen_60_unchanged':True})
print('Activated',new)
