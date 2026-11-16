"""Publish basic-law review as local 43; old runtime is immutable."""
from pathlib import Path
import json,hashlib,shutil,os
R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
OLD='20261111-basic-bifa-42';NEW='20261111-reviewed-bifa-43'
load=lambda p:json.loads(p.read_text('utf-8-sig'))
enc=lambda x:(json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pointer=load(R/'.opencode/liuren-active.json');assert pointer['release']==OLD
baseline=load(O/'before.json');assert all(sha(R/f)==h for f,h in baseline['frozen'].items())
runtime=R/'runtime/liuren'/NEW;assert not runtime.exists()
shutil.copytree(R/pointer['runtime'],runtime)
bundle=load(R/'tools/liuren-bifa-basic-rules.json');assert bundle['release']==NEW
shutil.copyfile(R/'tools/liuren-bifa-basic-rules.json',runtime/'references/bifa-basic-evidence.json')
short='43版本机毕法基本定义核查（20261111-reviewed-bifa-43）：100法逐法登记，134个基本条件分支和8项方法核查；非穷尽全部正变旁格。新盘按实际昼夜独立计算，matches只收明列条件全真，conditional_candidates保留缺项，method_checks为按问推理义务。第22依大全；书证按BF-B/D法号可查（含BF-B100）。详见docs/毕法百法基本适配-43.md。只限本机新任务，旧版冻结，网站未发布。'
core='''## 第43版：百法基本条件与方法交接（覆盖42版的25法范围说明）

本机正式完整盘及裁决核心的chart.bifa_conditions已逐法登记100法：134个已核基本条件分支、8项方法核查；不是所有正变旁格穷尽。

- matches：只有明列条件全真才能列入；附盘面坐标、实际昼夜、课传位置、空陷及书证索引。它确认基本结构关系，不能凭标题断成败。
- conditional_candidates：已有部分结构依据，但日照、本人年命或其他输入未足，保留null检查项；不得作为完整成格使用。
- method_checks：第9、93、94、96、97、98、99、100法的取舍、起课、空亡逐类、类神与问项、阶段核查，需AI依问履行；程序没有宣布这些推理已经完成。
- coverage.unavailable_context：输入不足且尚无足够盘面条件的规则，只登记缺项，不称候选成格。

第22依用户已定《大全》。贵人起法必须与本盘已采用表一致，实际天将只取本盘昼夜；另一贵人支仅在明文需昼夜两贵的规则中使用。第38分旬尾加首、天盘旬首乘玄、地盘旬首上乘玄及禄财旬尾；不能混成一个已完整闭口。第57不得把坐空鬼称实。第73初传临干时受克用日干，不把寄宫五行替代天干。第87坐墓与第88乘墓分开；干墓用日干五行。第75一字、二字、三字刑分支注明，不用笼统相刑替代。

阴干专项五行气（土随水）仅用于明列基本分支，不改U01—U11及通用天干十二长生。结构空陷不被抹掉，效力依本问类神、气态、制救与阶段核查；神将名性不是成败开关，包含或重叠条目不重复计票。不根据疾病、丧吊或芜淫格名宣告医学、死亡、外遇等现实事实。

原引擎标签仍不受信任；正变旁格尚未核实者暂停自动采用。BF-B/D法号查本任务绑定的连续全章书证（两法同章可共段），module=bifa-basic查看范围，bifa-basic-evidence查看总登记。决定性条目应核完整条件，不以标签代替原文。

第4四时返本表存在差异，暂不采用该旁格。第39太阳照武只报邻接候选，实际贵人昼夜不能替代日出日入。第56本人本命身份未绑定时只交候选。第100“已灾即可免后灾”与北海明确反驳冲突，暂停该概括自动判辞；保留具体结构与阶段核查，不改既定U口径。
'''
guide='# 毕法百法基本适配（43版）\n\n'+core+'\n\n| ID | 法 | 基本格/核查 | 明列条件 |\n|---|---:|---|---|\n'+''.join(f"|{r['id']}|{r['law_number']:02}|{r['name']}|{r['definition']}|\n" for r in bundle['rules'])
(runtime/'references/bifa-basic.md').write_text(guide,encoding='utf-8')
(R/'docs/毕法百法基本适配-43.md').write_text('# 本机毕法百法基本适配\n\n'+short+'\n\n'+core+'\n\n逐法来源与条件：[百法台账](../output/liuren-bifa-complete-20261111/百法逐法台账.md)。核查证据、备份与回滚脚本见同目录。工程通过不证明真实预测效果。\n',encoding='utf-8')
for rel in ['references/judgment-core.md','methods/adjudication.md','methods/structure.md','references/bifa.md']:
 p=runtime/rel;text=p.read_text('utf-8');head,rest=text.split('\n',1);p.write_text(head+'\n\n'+core+'\n'+rest,encoding='utf-8')
pending={}
for rel in ['README.md','目录总索引.md','AGENTS.md','docs/本机六壬高效执行.md','integrations/codex/daliuren-codex/SKILL.md','integrations/codex/daliuren-codex/references/host.md','.opencode/skills/liuren/daliuren/SKILL.md']:
 text=(R/rel).read_text('utf-8')
 if rel in ['README.md','目录总索引.md']:text=text.replace('指向 `'+OLD+'`','指向 `'+NEW+'`').replace('runtime/liuren/'+OLD+'/','runtime/liuren/'+NEW+'/')
 pending[rel]=(text+'\n\n'+short+'\n').encode('utf-8')
cfg=load(R/'opencode.json');oldmodels={k:(v.get('model'),v.get('variant')) for k,v in cfg['agent'].items()}
cfg=json.loads(json.dumps(cfg,ensure_ascii=False).replace('runtime/liuren/'+OLD,'runtime/liuren/'+NEW))
cfg['agent']['liuren']['prompt']=short+'\n'+cfg['agent']['liuren']['prompt'];assert oldmodels=={k:(v.get('model'),v.get('variant')) for k,v in cfg['agent'].items()};pending['opencode.json']=enc(cfg)
slim=load(R/'.opencode/oh-my-opencode-slim.jsonc');slim['agents']['liuren-adjudicator']['prompt']=short+'\n'+slim['agents']['liuren-adjudicator']['prompt'];pending['.opencode/oh-my-opencode-slim.jsonc']=enc(slim)
current_sha=lambda rel:hashlib.sha256(pending[rel]).hexdigest() if rel in pending else sha(R/rel)
contract=dict(id='reviewed-bifa-43',structures=134,methodChecks=8,representedLaws=100,sourceSpans=200,evidence='references/bifa-basic-evidence.json',actualModeOnly=True,nativeLabelsTrusted=False,all100LawsBasicReviewed=True,all100LawsComplete=False,scope='local-opencode-and-codex',predictiveValidationCount=0)
pointer.update(release=NEW,runtime=runtime.relative_to(R).as_posix(),previousRelease=OLD,backup='output/liuren-bifa-complete-20261111/before',authoringSource='output/liuren-bifa-complete-20261111',basicBifaIntegration=contract)
pointer['bookRetrieval']['compatibleMethodRelease']=NEW
pointer['files']={rel:current_sha('.opencode/skills/'+rel) for rel in pointer['files']}
for name in ['manifest.json','loader-contract.json']:
 d=load(runtime/name);d.update(release=NEW,parentRelease=OLD,basicBifaIntegration=contract,authoringSource='output/liuren-bifa-complete-20261111')
 if 'bookRetrieval' in d:d['bookRetrieval']['compatibleMethodRelease']=NEW
 if name=='loader-contract.json':d['sourceHashes']={rel:current_sha(rel) for rel in d['sourceHashes']}
 (runtime/name).write_bytes(enc(d))
for name in ['references/shensha-policy.json','references/shensha-authority-evidence.json','references/confirmed-policy-register.json','reading-route.json']:
 d=load(runtime/name);d['release']=NEW
 if name=='references/confirmed-policy-register.json':d['basicBifaIntegration']=contract
 (runtime/name).write_bytes(enc(d))
m=load(runtime/'manifest.json');m['files']={rel:sha(runtime/rel) for rel in m['files']};m['version']=hashlib.sha256(json.dumps(m['files'],sort_keys=True).encode()).hexdigest();(runtime/'manifest.json').write_bytes(enc(m))
pointer['methodVersion']=m['version'];pointer['workflowImplementation']={rel:current_sha(rel) for rel in pointer['workflowImplementation']}
pending['.opencode/liuren-active.json']=enc(pointer)
for rel in sorted(pending,key=lambda s:s=='.opencode/liuren-active.json'):
 target=R/rel;temp=target.with_name(target.name+'.bifa43.tmp');temp.write_bytes(pending[rel]);os.replace(temp,target)
assert all(sha(R/f)==h for f,h in baseline['frozen'].items())
(O/'after.json').write_bytes(enc(dict(release=NEW,runtime=pointer['runtime'],methodVersion=m['version'],old_runtime_unchanged=True,files={f:sha(R/f) for f in baseline['files']})))
print('Activated',NEW,'; frozen42 unchanged')
