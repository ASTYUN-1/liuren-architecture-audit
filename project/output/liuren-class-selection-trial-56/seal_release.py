from pathlib import Path
import hashlib,json,shutil
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
old='20261114-tool-reliability-55';new='20261114-class-selection-trial-56';T=R/'runtime/liuren'/new
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf8')
b=load(O/'before.json')
assert all(sha(R/f)==h for f,h in b['frozen'].items()),'Frozen 55 changed'
trial='''# 分类取用短答试验 56（仅本机 OpenCode）

本轮只练分类、取用及简单倾向。主智能体直接回答，不创建packet、不调用task、不派裁决者，不做review/recheck/deliver，不写完整报告。此范围优先于保留资料中的完整占断、取数和应期指令。Codex与历史已绑定任务仍按原协议。

1. 先依原问的实际所求、当事人和阶段选专项分支；不是按考试名称等关键词取类。读本页与该专项即可，不通读judgment-core/adjudication/report，也不跑methods完整计划。
2. 用完整可信程序盘；已有同盘直接复用，缺盘用liuren_chart（未给占时用now）。程序坐标、贵人和神煞采信程序，不手排。用户给年命可直接采用，不要求生日；仅新增年命用life。
3. 给出主类神、对应职责、天盘支/坐处/乘将及一条首取依据。兼看类只写真正影响本题的一项；同职责递补须满足专项条件，不能因主类空弱或辅助更旺就换主类。位置不清只lookup；取用条件不清才查classification-priority或连续原文。
4. 按关键类神的气态、空墓、直接作用及必要制救给“偏吉／偏凶／暂难定”倾向，附一两条切题理由及最关键保留条件。旺不直接等于成功、空不直接等于失败，局部救应不自动解除全部阻碍。不展开全盘或用数值指数定吉凶。

考试特别区分某科专业过关、日常成绩、升学录取、最终资格拿证及通知。首取依exam及classification-priority原有适用条件，不预设所有考试都取幕贵，也不因考试名称含职称而改取证书；考生定位按专项，不把代问者自动当日干。

输出通常200—400字：一句分类/阶段；小表“主类或必要兼看｜位置｜职责与首取依据”；两三句倾向、关键依据和缺口。依据写模块/条目即可，不堆来源。确有取用歧义才列竞争候选及条件，不强造唯一正确答案；缺决定性信息最多补问一个关键问题，已有信息先答。

即使原问含分数、名次或日期，也只答对应的分类取用和倾向，末尾一句“本试验暂不判断具体分数、名次和应期”。不计算、不估数字、不扩展建议，不拿过线倾向冒充已知过线事实。普通试验不查案例/经验库、旧会话或已知反馈。

取用理由供用户核验；程序只核坐标，不能证明取用正确或预测准确。反馈用于指出具体错配，未经用户确认不自动改规则或升级正式版。
'''
(T/'references/class-selection-trial.md').write_text(trial,'utf8')
entry='''---
name: daliuren
description: 本机分类取用短答试验：主智能体直接识别专项、关键类神及简单倾向，不触发裁决流程。
---

# 分类与取用试验

活动版本只认.opencode/liuren-active.json。本机OpenCode当前为class-selection-trial；先tool_help(workflow)确认execution_health.ready，再用liuren_materials(action=method,modules=["class-selection-trial",本问domain])读短规则及专项。只查真正的取用缺口。

主直接短答：分类/阶段→主类及可靠坐标、首取依据→关键状态支持的偏吉/偏凶/暂难定及关键缺口。通常200—400字，小表加两三句即可。详细规范见class-selection-trial。

不创建packet，不调用task或任何裁决、复核、报告交付工具；不读judgment-core/adjudication/report，不跑完整方法计划，不做分数/名次/应期。专项保留的取数及完整报告步骤在本试验不执行。需要盘时liuren_chart，已有同盘复用；缺占时用now。必要坐标/年命查核可用compute的lookup/life/source/chart，不扩展数值分析。

不检索案例/经验库或已知答案；不把程序通过说成取用正确。Codex和旧绑定任务仍走原协议；正式完整版本保留在55版，试验反馈后另行修订。
'''
(R/'.opencode/skills/liuren/daliuren/SKILL.md').write_text(entry,'utf8');(T/'entry.md').write_text(entry,'utf8')
p=load(R/'.opencode/liuren-active.json');p.update(release=new,previousRelease=old,runtime='runtime/liuren/'+new,backup='output/liuren-class-selection-trial-56/before',authoringSource='output/liuren-class-selection-trial-56',defaultMode='class-selection-trial')
policy={'id':'class-selection-and-tendency-56','enabled':True,'scope':'local-opencode-new-tasks','directAnswer':True,'adjudicationEnabled':False,'quantityEnabled':False,'timingEnabled':False,'targetLength':'200-400 Chinese characters','module':'class-selection-trial','rollbackRelease':old,'predictiveValidationCount':0,'realModelCallCount':0}
p['classSelectionTrial']=policy
cfg=load(R/'opencode.json');agent=cfg['agent']['liuren']
agent['description']='分类取用短答试验：主直接回答，不派裁决，不做分数应期。'
agent['prompt']=entry.split('# 分类与取用试验',1)[1].strip()+'\n权限拒绝即表示该工具不在当前试验范围，不以其他代理、Build、外部MCP或脚本绕过；工作流开发由用户另行提出。'
permissions=agent['permission']
for tool in ['liuren_adjudication_packet','liuren_adjudication_result','liuren_adjudication_read','liuren_adjudication_submit','liuren_adjudication_audit','task_result']:permissions[tool]='deny'
permissions['task']={'*':'deny','liuren-adjudicator':'deny'}
permissions['read']={k.replace(old,new):v for k,v in permissions['read'].items()}
save(R/'opencode.json',cfg)
for rel in ['README.md','目录总索引.md']:
 f=R/rel;s=f.read_text('utf8').replace(old,new)
 note='\n当前本机OpenCode默认为56版分类取用短答试验：主智能体直接回答分类、取用及简单倾向，不触发裁决流程，不做分数/名次/应期。通常200—400字。详见[试验与回切说明](output/liuren-class-selection-trial-56/试验与回切说明.md)；下文完整流程保留供Codex和历史任务使用。\n'
 if note.strip() not in s:s=s.replace('\n', '\n'+note,1)
 if rel=='README.md':s=s.replace('55版修复本地工具参数、引用身份与错误定位','底层沿用55版工具参数、引用身份与错误定位修复')
 f.write_text(s,'utf8')
for rel in ['docs/本机六壬完整研判流程.md','docs/本机OpenCode完整输出规则.md','docs/本机六壬高效执行.md']:
 f=R/rel;s=f.read_text('utf8');notice='\n当前OpenCode新会话按56版分类取用短答试验执行：读class-selection-trial及本问专项→可信程序盘→主直接短答分类、主类/位置/首取依据、简单吉凶倾向。通常200—400字，不触发packet/task/裁决/review/recheck/deliver，不做分数、名次或应期。下列完整步骤仅供Codex及历史绑定任务；不得对本试验叠加。详见[试验与回切说明](../output/liuren-class-selection-trial-56/试验与回切说明.md)。\n'
 if notice.strip() not in s:s=s.replace('\n','\n'+notice,1)
 f.write_text(s,'utf8')
m=load(T/'manifest.json');c=load(T/'loader-contract.json')
m.update(release=new,parentRelease=old);c.update(release=new,parentRelease=old)
m['modules']['class-selection-trial']={'file':'references/class-selection-trial.md','required':False,'requires':[],'trigger':'本机OpenCode分类取用短答试验'}
m['files']['references/class-selection-trial.md']=sha(T/'references/class-selection-trial.md')
for rel in ['reading-route.json','references/shensha-policy.json','references/shensha-authority-evidence.json','references/confirmed-policy-register.json']:
 d=load(T/rel);d['release']=new;save(T/rel,d)
for d in [m,c]:d['classSelectionTrial']=policy
for key in ['workflowImplementation'] :p[key]={f:sha(R/f) for f in p[key]}
p['files']={f:sha(R/'.opencode/skills'/f) for f in p['files']}
for f in p.get('bookRetrieval',{}).get('files',{}):p['bookRetrieval']['files'][f]=sha(R/f)
c['sourceHashes']={f:sha(R/f) for f in c['sourceHashes']}
for key in ['bookRetrieval']:c[key]=p[key];m[key]=p[key]
save(T/'loader-contract.json',c)
m['files']={f:sha(T/f) for f in m['files']}
m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();save(T/'manifest.json',m)
p['methodVersion']=m['version'];save(R/'.opencode/liuren-active.json',p)
save(O/'after.json',{'release':new,'files':{f:sha(R/f) for f in b['files']},'frozen_55_unchanged':True,'real_model_calls':0})
print('Activated',new)
