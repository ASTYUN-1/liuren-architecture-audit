"""Snapshot 56, restore selected-strength access, and seal a new local release."""
from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2]; O=Path(__file__).resolve().parent
old='20261114-class-selection-trial-56'; new='20261114-class-strength-trial-57'
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
def replace(p,a,b):
 s=p.read_text('utf8'); assert a in s,(p,a);p.write_text(s.replace(a,b),'utf8')
p=load(R/'.opencode/liuren-active.json');assert p['release']==old
T=R/'runtime/liuren'/new; c=load(R/p['runtime']/'loader-contract.json')
files=set(p['workflowImplementation'])|set(c['sourceHashes'])
files.update('.opencode/skills/'+f for f in p['files'])
files.update(['.opencode/liuren-active.json','README.md','目录总索引.md','docs/本机六壬完整研判流程.md','docs/本机OpenCode完整输出规则.md','docs/本机六壬高效执行.md','tools/tests/liuren-class-selection-trial.test.mjs'])
assert not (O/'before.json').exists() and not T.exists()
for f in files:
 d=O/'before'/f;d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(R/f,d)
b={'release':old,'files':{f:sha(R/f) for f in sorted(files)},'frozen':{f.relative_to(R).as_posix():sha(f) for f in (R/p['runtime']).rglob('*') if f.is_file()}}
save(O/'before.json',b);shutil.copytree(R/p['runtime'],T)
plugin=R/'.opencode/plugins/liuren-adjudication.ts'
replace(plugin,"!['chart','lookup','life','source'].includes(args.action)","!['chart','lookup','life','source','strength'].includes(args.action)")
replace(plugin,'不运行取数、应期或扩展数值分析。','允许取类后的旺衰补算；不运行取数、应期或其他扩展数值分析。')
replace(plugin,'主智能体直接短答：分类、主类及坐标/首取依据、简要倾向、必要缺口','先取类，再复用盘内旺衰；关键跨宫生克需用liuren_compute(action=strength)补算已选对象和关系；主直接短答分类、主类/依据、旺衰制救、倾向与缺口')
entry=R/'.opencode/skills/liuren/daliuren/SKILL.md'
replace(entry,'必要坐标/年命查核可用compute的lookup/life/source/chart，不扩展数值分析。','必要坐标/年命查核可用compute的lookup/life/source/chart。先取类再查类神旺衰：盘内单宫旺衰直接复用，关键跨宫生克用compute的strength按已选对象及有依据的关系补算；不得只列空墓或神煞就定倾向。旺衰数值不直接折成吉凶、概率或分数。')
(T/'entry.md').write_bytes(entry.read_bytes())
module=T/'references/class-selection-trial.md'
replace(module,'分类取用短答试验 56','分类取用短答试验 57')
replace(module,'4. 按关键类神的气态、空墓、直接作用及必要制救给“偏吉／偏凶／暂难定”倾向，附一两条切题理由及最关键保留条件。旺不直接等于成功、空不直接等于失败，局部救应不自动解除全部阻碍。不展开全盘或用数值指数定吉凶。', '''4. 取类之后，必须结合主类及关键作用方的旺衰、空墓、有效生克与必要制救给“偏吉／偏凶／暂难定”。先读盘内月令、十二气、空墓及单宫旺衰；月令旺衰不等于综合状态，单宫指数也不含取用后的跨宫作用。主类必须贯穿倾向依据，不能只凭辅助类空弱或神煞名目定成败。
5. 对决定倾向的跨宫生扶、泄耗、克制，用liuren_compute(action="strength",archive=原盘archive,strength={mode:"selected_relations",season_profile,season_basis,actors,links,review:true})补算。actors只填已取用主类、必要作用/制救方（id为T:支、J:天将或S:日干，含role与basis）；links只填已依原法确认适用的关系（source、target、basis）。只需单宫可复用原盘；不做全盘两两计算，不为工具凑作用。刑冲合化及神煞依适用条件解释，不自动塞入生克计分。参数不明查tool_help(topic="compute")。
6. 核双方是否有力、作用通路及解除范围；有救应候选就查能否真正解除本题关键阻碍。季月四季/季土双表须同一依据一致使用；有分歧且无已定依据时保留分歧，不按结果换表。附一两条切题理由及最关键保留条件。旺不直接等于成功、空不直接等于失败，旺鬼不直接等于攻击更强，局部救应不自动解除全部阻碍。指数是研究计算参考，不是吉凶阈值、成功概率或考试分数，不手填/编造指数。''')
replace(module,'职责与首取依据”；两三句倾向、关键依据和缺口','职责与首取依据”；两三句主类旺衰及有效作用/制救、倾向和缺口')
cfg=load(R/'opencode.json');agent=cfg['agent']['liuren']
agent['prompt']=entry.read_text('utf8').split('# 分类与取用试验',1)[1].strip()+'\n权限拒绝即表示该工具不在当前试验范围，不以其他代理、Build、外部MCP或脚本绕过；工作流开发由用户另行提出。'
agent['permission']['read']={k.replace(old,new):v for k,v in agent['permission']['read'].items()};save(R/'opencode.json',cfg)
for rel in ['README.md','目录总索引.md','docs/本机六壬完整研判流程.md','docs/本机OpenCode完整输出规则.md','docs/本机六壬高效执行.md']:
 f=R/rel;s=f.read_text('utf8').replace(old,new).replace('56版分类取用短答试验','57版分类取用短答试验').replace('liuren-class-selection-trial-56/试验与回切说明.md','liuren-class-strength-trial-57/试验与回切说明.md')
 s=s.replace('简单倾向，不触发','简单倾向（取类后结合旺衰及制救），不触发').replace('主类/位置/首取依据、简单吉凶倾向','主类/位置/首取依据、结合旺衰制救的简单吉凶倾向');f.write_text(s,'utf8')
test=R/'tools/tests/liuren-class-selection-trial.test.mjs'
replace(test,"['quantity','strength','calendar','evaluation','methods','imagery']","['quantity','calendar','evaluation','methods','imagery']")
p.update(release=new,previousRelease=old,runtime='runtime/liuren/'+new,backup='output/liuren-class-strength-trial-57/before',authoringSource='output/liuren-class-strength-trial-57')
p['classSelectionTrial'].update(id='class-selection-strength-and-tendency-57',strengthEnabled=True,strengthPolicy='select classes first; reuse single palace; compute justified selected relations',rollbackRelease=old)
m=load(T/'manifest.json');c=load(T/'loader-contract.json')
for d in [m,c]:d.update(release=new,parentRelease=old,classSelectionTrial=p['classSelectionTrial'])
for rel in ['reading-route.json','references/shensha-policy.json','references/shensha-authority-evidence.json','references/confirmed-policy-register.json']:
 d=load(T/rel);d['release']=new;save(T/rel,d)
def seal():
 assert all(sha(R/f)==h for f,h in b['frozen'].items()),'Frozen 56 changed'
 p['workflowImplementation']={f:sha(R/f) for f in p['workflowImplementation']}
 p['files']={f:sha(R/'.opencode/skills'/f) for f in p['files']}
 p['bookRetrieval']['files']={f:sha(R/f) for f in p['bookRetrieval']['files']}
 c['sourceHashes']={f:sha(R/f) for f in c['sourceHashes']}
 for d in [m,c]:d['bookRetrieval']=p['bookRetrieval']
 save(T/'loader-contract.json',c);m['files']={f:sha(T/f) for f in m['files']}
 m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();save(T/'manifest.json',m)
 p['methodVersion']=m['version'];save(R/'.opencode/liuren-active.json',p)
 save(O/'after.json',{'release':new,'files':{f:sha(R/f) for f in b['files']},'frozen_56_unchanged':True,'external_model_calls':0})
seal()
rollback=(R/'output/liuren-class-selection-trial-56/rollback.py').read_text('utf8').replace('55','56').replace('at 56','at 57').replace('after 56','after 57').replace('Frozen 56 retained','Frozen 57 retained')
(O/'rollback.py').write_text(rollback,'utf8')
(O/'试验与回切说明.md').write_text('''# 57版分类取用与旺衰短答试验

本机OpenCode新进程、新会话生效。先分类取类，再复用盘内单宫旺衰；关键跨宫生克使用strength计算已选对象和关系，结合有效制救给简要倾向。通常200—400字，不触发裁决，不做分数、名次、应期。

恢复strength访问并补充使用要求，未修改旺衰算法、系数和专项取类规则。指数不直接决定吉凶。56冻结资料保留；Codex完整协议保留。工具连通验证不等于模型遵守或预测准确。

回切：python -X utf8 output/liuren-class-strength-trial-57/rollback.py。脚本仅在活动文件仍符合本版after.json时还原56；回切后重启OpenCode。
''','utf8')
print('Activated',new)
