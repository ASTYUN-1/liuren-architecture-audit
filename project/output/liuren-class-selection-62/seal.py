from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
old='20261115-trial-decision-61';new='20261115-class-selection-62'
B=R/'runtime/liuren'/old;T=R/'runtime/liuren'/new;b=load(O/'before.json')
assert all(sha(R/f)==h for f,h in b['frozen'].items())
p=load(O/'before/.opencode/liuren-active.json');m=load(B/'manifest.json');c=load(B/'loader-contract.json')
entry=(O/'entry.md').read_text('utf8');(R/'.opencode/skills/liuren/daliuren/SKILL.md').write_text(entry,'utf8')
cfg=load(O/'before/opencode.json')
cfg['agent']['liuren']['prompt']=entry.split('# 分类与取用试验',1)[1].strip()+'\n权限拒绝不绕过，工作流开发另行授权。'
cfg['agent']['liuren']['permission']['read']={k.replace(old,new):v for k,v in cfg['agent']['liuren']['permission']['read'].items()}
save(R/'opencode.json',cfg)
for rel in ['README.md','目录总索引.md']:
 s=(O/'before'/rel).read_text('utf8').replace('61版分类取用短答试验','62版分类取用短答试验').replace(old,new).replace('output/liuren-trial-decision-61/修正说明.md','output/liuren-class-selection-62/修正说明.md')
 s+='\n分类取用测试复盘按[两路核对规范](docs/分类取用测试核对规范.md)执行：先锁模型初答，再分别核对原案答者取法与原书教法及条件。当前只优化取用，不把原案答案交给待测会话。\n'
 (R/rel).write_text(s,'utf8')
p.update(release=new,previousRelease=old,runtime='runtime/liuren/'+new,backup='output/liuren-class-selection-62/before',authoringSource='output/liuren-class-selection-62')
p['classSelectionTrial'].update(id='class-selection-source-62',rollbackRelease=old,
 selectionPolicy={'id':'class-selection-source-62','preserve_original_question':True,'relation_requires_parties':True,'source_and_condition_required':True,'life_ground_upper_distinguished':True},
 reviewProtocol={'file':'docs/分类取用测试核对规范.md','sha256':sha(R/'docs/分类取用测试核对规范.md'),'scope':'post-answer evaluation only','axes':['原案答者实际取用及理由','原书教法及适用条件'],'reference_answers_supplied_to_test_model':False})
# Strength policy is unchanged: ID 61 identifies its semantics, not this release.
assert p['classSelectionTrial']['decisionBasis']['id']=='liuren-trial-decision-61'
for d in [m,c]:d.update(release=new,parentRelease=old,classSelectionTrial=p['classSelectionTrial'],authoringSource='output/liuren-class-selection-62')
for rel in ['reading-route.json','references/shensha-policy.json','references/shensha-authority-evidence.json','references/confirmed-policy-register.json']:
 d=load(B/rel);d['release']=new;save(T/rel,d)
for target in [p['workflowImplementation'],c['sourceHashes']]:
 for f in target:target[f]=sha(R/f)
p['files']={f:sha(R/'.opencode/skills'/f) for f in p['files']}
p['bookRetrieval']['files']={f:sha(R/f) for f in p['bookRetrieval']['files']}
for d in [m,c]:d['bookRetrieval']=p['bookRetrieval']
save(T/'loader-contract.json',c)
m['files']={f:sha(T/f) for f in m['files']}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();save(T/'manifest.json',m)
p['methodVersion']=m['version'];save(R/'.opencode/liuren-active.json',p)
save(O/'after.json',{'release':new,'files':{f:sha(R/f) for f in [*b['files'],*b['new_files']]},'frozen_61_unchanged':True})
print('Activated',new,'; model settings and strength semantics unchanged')
