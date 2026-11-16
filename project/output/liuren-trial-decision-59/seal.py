from pathlib import Path
import json,hashlib,re
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
old='20261115-strength-meaning-58';new='20261115-trial-decision-59';T=R/'runtime/liuren'/new;B=R/'runtime/liuren'/old
b=load(O/'before.json');assert all(sha(R/f)==h for f,h in b['frozen'].items())
p=load(O/'before/.opencode/liuren-active.json');m=load(B/'manifest.json');c=load(B/'loader-contract.json')
domain_modules={};projection_audit=[]
legacy_headings=['## 判断流程','## 原有方法的独有检查','## 专项执行与收束','## 分维判断的来源整理与执行边界','## 执行','## I —']
for k in m['domains']:
 rel=m['modules'][k]['file'];src=B/rel;lines=src.read_text('utf8').splitlines(keepends=True)
 cut=next((i for i,line in enumerate(lines) if any(line.startswith(h) for h in legacy_headings)),len(lines))
 text=''.join(lines[:cut]).rstrip()+'\n'
 replacements={
 '沿共用主线核双方状态、有效通路、制救、时序和最强反证后再裁结果，不将辅助类单独另立结论。':'本试验只从本段采用分流与取用条件，倾向依class-selection-trial，不沿用完整占断流程。',
 '综合主线依judgment-core；':'本试验倾向依class-selection-trial；',
 '现行判断须按judgment-core及下文E段核角色、气态、有效作用、制救和最强反证；':'本试验判断只依class-selection-trial；'}
 changed=[]
 for a,z in replacements.items():
  if a in text:text=text.replace(a,z);changed.append({'before':a,'after':z})
 text+='\n## 本试验解释边界\n\n以上仅供分类、取用职责及适用条件；任何生克、鬼虎、制救或结果措辞都须依class-selection-trial先定本题作用性质，再按统一喜旺恶衰解释。不将旺鬼当成更强攻击，不以制不住旺鬼判凶；不以衰鬼数值小免除凶态。空墓、时序、实际通路保留，不能由低分直接判失用。原问未给的成功标准不补造。首取条件仍不足时只定点读classification-priority/原段，不用预训练通则补定。完整专项原件保留，未覆盖。\n'
 dest='references/trial-domains/'+k+'.md';file=T/dest;file.parent.mkdir(parents=True,exist_ok=True);file.write_text(text,'utf8')
 key='trial-domain-'+k;domain_modules[k]=key;m['modules'][key]={'file':dest,'required':False,'requires':[],'title':m['modules'][k].get('title',k)+'（短答取用摘录）','trigger':'当前短答工具适配器，完整占断仍读原专项'}
 m['files'][dest]=sha(file)
 projection_audit.append({'domain':k,'source_path':str(src.relative_to(R)),'source_sha256':sha(src),'source_lines':[1,cut],'output_path':str(file.relative_to(R)),'output_sha256':sha(file),'routing_replacements':changed,'omitted_from_line':cut+1 if cut<len(lines) else None,'note':'仅本试验读取；原专项不改。未摘录的完整取用条件可定点查classification-priority/原文，不证明原模块全部语义已审查。'})
save(O/'domain-projection-audit.json',projection_audit)
entry=(O/'entry.md').read_text('utf8');(R/'.opencode/skills/liuren/daliuren/SKILL.md').write_text(entry,'utf8');(T/'entry.md').write_text(entry,'utf8')
(T/'references/class-selection-trial.md').write_text((O/'class-selection-trial.md').read_text('utf8'),'utf8')
cfg=load(O/'before/opencode.json');cfg['agent']['liuren']['prompt']=entry.split('# 分类与取用试验',1)[1].strip()+'\n权限拒绝不绕过，工作流开发另行授权。'
cfg['agent']['liuren']['permission']['read']={k.replace(old,new):v for k,v in cfg['agent']['liuren']['permission']['read'].items()};save(R/'opencode.json',cfg)
f=R/'.opencode/plugins/liuren-adjudication.ts';text=f.read_text('utf8')
text=text.replace("'先取类，再复用盘内旺衰；关键跨宫生克需用liuren_compute(action=strength)补算已选对象和关系；主直接短答分类、主类/依据、旺衰制救、倾向与缺口'","'取类后先定本题作用性质，再按统一喜旺恶衰读状态；必要跨宫关系用strength补算并读取trial_judgment_basis；禁止旺鬼扣身再以身弱判凶，不以制不住旺鬼判失败；主短答倾向'")
text=text.replace("available_domains:EVENT_DOMAINS,domain_routing:DOMAIN_ROUTES,steps:['读class-selection-trial", "available_domains:EVENT_DOMAINS,domain_routing:DOMAIN_ROUTES,trial_decision_policy:TRIAL_DECISION_POLICY,steps:['读class-selection-trial")
f.write_text(text,'utf8')
for rel in ['README.md','目录总索引.md']:
 f=R/rel;text=(O/'before'/rel).read_text('utf8').replace('58版分类取用短答试验','59版分类取用短答试验').replace(old,new).replace('output/liuren-strength-meaning-58/试验与回切说明.md','output/liuren-trial-decision-59/定位与修改说明.md');f.write_text(text,'utf8')
p.update(release=new,previousRelease=old,runtime='runtime/liuren/'+new,backup='output/liuren-trial-decision-59/before',authoringSource='output/liuren-trial-decision-59')
p['classSelectionTrial'].update(id='class-selection-decision-59',rollbackRelease=old,domainModules=domain_modules,decisionBasis={'enabled':True,'id':'liuren-trial-decision-59','scope':'local-opencode-liuren-only','automatic_event_verdict':False,'numeric_algorithms_changed':False})
for d in [m,c]:d.update(release=new,parentRelease=old,classSelectionTrial=p['classSelectionTrial'])
for rel in ['reading-route.json','references/shensha-policy.json','references/shensha-authority-evidence.json','references/confirmed-policy-register.json']:
 d=load(B/rel);d['release']=new;save(T/rel,d)
for target in [p['workflowImplementation'],c['sourceHashes']]:
 target['tools/liuren-trial-decision.mjs']=sha(R/'tools/liuren-trial-decision.mjs')
 for key in target:target[key]=sha(R/key)
p['files']={k:sha(R/'.opencode/skills'/k) for k in p['files']}
p['bookRetrieval']['files']={k:sha(R/k) for k in p['bookRetrieval']['files']}
for d in [m,c]:d['bookRetrieval']=p['bookRetrieval']
save(T/'loader-contract.json',c);m['files']={k:sha(T/k) for k in m['files']};m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();save(T/'manifest.json',m)
p['methodVersion']=m['version'];save(R/'.opencode/liuren-active.json',p)
save(O/'after.json',{'release':new,'files':{k:sha(R/k) for k in list(b['files'])+b['new_files']},'frozen_58_unchanged':True,'original_domains_and_core_unchanged':all(sha(B/m['modules'][k]['file'])==sha(T/m['modules'][k]['file']) for k in m['domains']+['judgment-core'])})
print('Activated',new,'with',len(domain_modules),'scoped domain views')
