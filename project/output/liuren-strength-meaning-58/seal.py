from pathlib import Path
import hashlib,json
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
old='20261114-class-strength-trial-57';new='20261115-strength-meaning-58';T=R/'runtime/liuren'/new
p=load(O/'before/.opencode/liuren-active.json');b=load(O/'before.json')
assert all(sha(R/f)==h for f,h in b['frozen'].items()),'Frozen 57 changed'
policy='''旺衰与可用性分开判断。本题相关的日干、关键类神、官鬼和凶神统一喜旺恶衰：越旺越有利，越衰越不利；官鬼凶神旺默认不以侵害为主，衰败凶态显。不得把鬼旺解释为侵害大、鬼弱或零解释为无害；不得把身分下降、鬼分高低直接当作考试失败或制救成败。能否实际作用另核职责、位置、通路、受制与时序，不设低分失用开关。泄耗先核去向，泄干生本题主类可体现付出，不默认失败。相关关系可补算，实际作用性质先于分数解释。'''
bands='''统一旺衰层级（不是可用程度、成功概率或分数）：E=0为本模型计算下限；0<E<1极衰；1≤E<2.5衰弱；2.5≤E<5偏弱至中等；5≤E<7.5较旺；7.5≤E≤10强旺。null是缺计算。4至6不增不减是旧数量修正分段，不用于此处；旧harm_tendency/favorable_tendency小数不参与本轮吉凶裁决。'''
entry=(O/'before/.opencode/skills/liuren/daliuren/SKILL.md').read_text('utf8')
entry=entry.replace('详细规范见class-selection-trial。','详细规范见class-selection-trial。\n\n'+policy+'\n'+bands)
(R/'.opencode/skills/liuren/daliuren/SKILL.md').write_text(entry,'utf8');(T/'entry.md').write_text(entry,'utf8')
f=T/'references/class-selection-trial.md';s=(R/'runtime/liuren'/old/'references/class-selection-trial.md').read_text('utf8').replace('分类取用短答试验 57','分类取用短答试验 58')
s=s.replace('考试特别区分','## 本轮已确认旺衰口径（控制本轮综合取舍）\n\n'+policy+'\n\n'+bands+'\n\n出答前在同一轮检查：是否把鬼旺当作伤害大、鬼弱当作无害；是否把低分当作不能作用；是否把有助于主类的泄耗当成失败。存在任一项就依本段修正取舍，不另开裁决或复核流程，不需输出检查清单。\n\n考试特别区分')
f.write_text(s,'utf8')
f=T/'references/judgment-core.md';s=(R/'runtime/liuren'/old/'references/judgment-core.md').read_text('utf8');start=s.index('- **U02 喜旺恶衰。**');end=s.index('\n- **U03',start)
s=s[:start]+'- **U02 喜旺恶衰。**采用北海喜旺恶衰趋势，以下数值执行解释由用户本轮确认，不冒称古籍原有数值阈值。'+policy+bands+'旺鬼贪荣有时段条件，不据当前有利保证长期无患；当前结果和后患分开。刑虎等组合仍核其具体条件，不因有组合便否认本段的统一倾向。'+s[end:]
s=s.replace('2.5不是失用开关；','2.5不是失用开关；标签是旺衰层级，非可用程度；')
f.write_text(s,'utf8')
cfg=load(R/'opencode.json');a=cfg['agent']['liuren'];a['prompt']=entry.split('# 分类与取用试验',1)[1].strip()+'\n权限拒绝即表示该工具不在当前试验范围，不以其他代理、Build、外部MCP或脚本绕过；工作流开发由用户另行提出。'
a['permission']['read']={k.replace(old,new):v for k,v in a['permission']['read'].items()};save(R/'opencode.json',cfg)
for rel in ['README.md','目录总索引.md','docs/本机六壬完整研判流程.md','docs/本机OpenCode完整输出规则.md','docs/本机六壬高效执行.md']:
 f=R/rel;s=(O/'before'/rel).read_text('utf8').replace(old,new).replace('57版分类取用短答试验','58版分类取用短答试验').replace('liuren-class-strength-trial-57/试验与回切说明.md','liuren-strength-meaning-58/试验与回切说明.md');f.write_text(s,'utf8')
p.update(release=new,previousRelease=old,runtime='runtime/liuren/'+new,backup='output/liuren-strength-meaning-58/before',authoringSource='output/liuren-strength-meaning-58')
p['classSelectionTrial'].update(id='class-selection-strength-meaning-58',rollbackRelease=old)
meaning={'id':'liuren-strength-meaning-58','unified_wang_good_shuai_bad':True,'score_is_usability':False,'low_score_means_harmless':False,'high_ghost_score_means_more_harm':False,'numerical_algorithms_changed':False,'professional_interpretation_changed':True,'source':'user-confirmed','audit':'output/liuren-strength-meaning-58/试验与回切说明.md'}
p['strengthInterpretation']=meaning
m=load(T/'manifest.json');c=load(T/'loader-contract.json')
for d in [m,c]:d.update(release=new,parentRelease=old,classSelectionTrial=p['classSelectionTrial'],strengthInterpretation=meaning)
for rel in ['reading-route.json','references/shensha-policy.json','references/shensha-authority-evidence.json','references/confirmed-policy-register.json']:
 d=load(T/rel);d['release']=new
 if rel.endswith('confirmed-policy-register.json'):d['strengthInterpretation']=meaning
 save(T/rel,d)
p['workflowImplementation']['tools/liuren-strength-interpretation.mjs']=sha(R/'tools/liuren-strength-interpretation.mjs')
c['sourceHashes']['tools/liuren-strength-interpretation.mjs']=sha(R/'tools/liuren-strength-interpretation.mjs')
p['workflowImplementation']={f:sha(R/f) for f in p['workflowImplementation']};p['files']={f:sha(R/'.opencode/skills'/f) for f in p['files']}
p['bookRetrieval']['files']={f:sha(R/f) for f in p['bookRetrieval']['files']}
c['sourceHashes']={f:sha(R/f) for f in c['sourceHashes']}
for d in [m,c]:d['bookRetrieval']=p['bookRetrieval']
save(T/'loader-contract.json',c);m['files']={f:sha(T/f) for f in m['files']};m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();save(T/'manifest.json',m)
p['methodVersion']=m['version'];save(R/'.opencode/liuren-active.json',p)
save(O/'after.json',{'release':new,'files':{f:sha(R/f) for f in list(b['files'])+b['new_files']},'frozen_57_unchanged':True})
(O/'试验与回切说明.md').write_text('''# 58版旺衰解释与五例复测

用户确认：相关吉神、官鬼及凶神均喜旺恶衰；旺衰不是可用程度，低分或零不证明官鬼无害，高分不证明侵害更大。

保留原0、1、2.5、5、7.5、10边界、数值算法及系数，修改旺衰标签，并把统一性质说明同时送入主提示、短规则、U02、排盘及所选关系补算回执。4至6数量修正分段及旧危害倾向小数不用于本轮裁吉凶。工具负增量不是现实损害量。完整专业口径改变，工程通过不等于预测改善。

保持本机OpenCode短答、无裁决、无分数名次应期；新进程新会话加载。网站未发布，五例不入库，不传答案。冻结57保留。

回切：python -X utf8 output/liuren-strength-meaning-58/rollback.py；仅在当前文件仍符合after.json时还原57，删除本版新增的两个工具/测试文件。58冻结包和试验记录保留。
''','utf8')
print('Activated',new)
