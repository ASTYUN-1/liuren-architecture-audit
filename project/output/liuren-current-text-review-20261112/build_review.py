"""Make a review-only snapshot of current rules and checked book passages."""
from pathlib import Path
import hashlib,json,shutil

R=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda raw:hashlib.sha256(raw).hexdigest()
p=load(R/'.opencode/liuren-active.json');T=R/p['runtime'];m=load(T/'manifest.json')
assert p['release']==m['release'] and p['methodVersion']==m['version']
assert not (O/'审查目录.md').exists(),'Review already exists; do not overwrite review annotations'
rows=[];bykey={}
def copy(key,title,source,group,description,filename=None):
 raw=source.read_bytes()
 relative=source.relative_to(R).as_posix()
 if source.is_relative_to(T):assert sha(raw)==m['files'][source.relative_to(T).as_posix()],key
 target=O/group/(filename or key+'.md');target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists():assert target.read_bytes()==raw,'Existing review text differs; do not overwrite: '+str(target)
 else:target.write_bytes(raw)
 row={'key':key,'title':title,'source':relative,'snapshot':target.relative_to(O).as_posix(),
  'sha256':sha(raw),'bytes':len(raw),'lines':len(raw.decode('utf8').splitlines()),'description':description}
 rows.append(row);bykey[key]=row;return row
def module(key,title,description,group='现行共用原文'):
 return copy(key,title,T/m['modules'][key]['file'],group,description)
copy('daliuren-skill','总入口 SKILL',R/'.opencode/skills/liuren/daliuren/SKILL.md','现行共用原文','规定实际读取什么、怎样交接与交付')
copy('codex-skill','Codex宿主 SKILL',R/'integrations/codex/daliuren-codex/SKILL.md','执行与工具原文','Codex专用执行职责，不是另一套专业取用法')
specs=[
 ('judgment-core','共用判断规范','所有子问共同采用的主线、U01—U11及旺衰取数边界'),
 ('positioning','原问、对象与取用','当事人与代问者、干支职责、九系统、通类与专类、类不现'),
 ('classification-priority','分类职责、首取与条件递补','婚恋、考试、职位、工作求财、寻物行人和官讼等主次条件'),
 ('shenjiang-use','神将同用与互换','天神/天将对应、替代路径与不可迁移的坐标和力量'),
 ('shen-symbols','十二天神象义','基础物类、形质功能及复合取义'),
 ('jiang-symbols','十二天将象义','人物事职能，不能把名目直接当结果'),
 ('liqi','关键对象的有效作用','气态、位置、施受、制救和实际兑现'),
 ('void','空亡','空的对象、状态与具体环节，不凭空名结案'),
 ('movement','动静、流向与行止','状态变化、流动方向、关墓空与冲解'),
 ('structure','课传结构','结构与本问对象的联系，不能只凭课名'),
 ('analysis-workflow','北海综合流程的原文与归纳','原书总论与本机采用边界分别保留'),
 ('confirmed-policy','采用口径 U01—U11 全文','本地采用规则，不冒充各书共识'),
 ('book-logic','类神状态及作用的书证执行补充','不现、阴阳、气势、施受及阶段的细节'),
 ('bifa','毕法使用边界','毕法描述辅助定位'),
 ('bifa-basic','毕法基本条件及适配边界','成格事实与按问取义分开'),
 ('shensha-use','神煞取用','直接取类、修饰与制救的具体条件'),
 ('quantity','数量取法','数量对象、数法、单位与实际估计'),
 ('quantity-strength','旺衰对取数的作用','气态选法与后续修正的分工'),
 ('quantity-correction','旺衰与数量兑现','source/experimental、空减、量级及真实回执'),
 ('timing','应期','时段、起点、尺度与兑现条件'),
]
for key,title,description in specs:module(key,title,description)
for key,title,description in [
 ('adjudication','中性交接与独立裁决','准备、独立裁决、一次同会话补核'),
 ('report','完整报告与核对','结论、反证、依据及缺口怎样交付'),
 ('consistency-audit','五项一致性核对','事实身份、职责阶段、计算范围、反证与逐问约束')]:
 module(key,title,description,'执行与工具原文')
copy('deterministic-tools','程序工具接口与计算边界',T/'references/deterministic-tools.md','执行与工具原文',
 '正文文件存在且在manifest.files；当前未登记同名module ID，不能直接用该ID查询')

domain_labels={'relationship':'婚姻爱情','exam':'学业考试','promotion-salary':'职位晋升与薪酬',
 'recruitment':'应聘与工作录用','finance':'经营求财','lost-person-object':'失物寻物与走失',
 'litigation':'官讼诉讼','interpersonal':'人际是非','illness':'疾病求医','pregnancy':'胎产生育',
 'home':'家宅地产','travel':'出行行人','weather':'天时天气','agriculture':'农渔畜养',
 'period-outlook':'阶段时运','long-period':'长期占事','classical-conflict':'兵盗等古典专题补充'}
assert set(domain_labels)==set(m['domains'])
for key,title in domain_labels.items():module(key,title,'该分类当前完整正文，保留全部条件及来源标识','分类占原文')

evidence_receipts=[];evidence_links={};cache={}
for key,title in [('classification-evidence','分类取用的48段原书依据'),('analysis-workflow-evidence','综合流程的14段原书依据')]:
 source=T/m['modules'][key]['file'];raw=source.read_bytes()
 assert sha(raw)==m['files'][source.relative_to(T).as_posix()]
 target=O/'书证'/source.name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
 data=json.loads(raw);parts=['# '+title,'','以下为当前证据表登记的连续范围，逐段按原始编码回读原书并核对hash、行号和完整文本。原书原有强语及书例照录；被引用不表示所有断语都已采为本机规则。行号为解码后的splitlines，一基、闭区间。','']
 for e in data['evidence']:
  file=R/e['path'];encoding=e.get('encoding',e.get('source_encoding','utf-8-sig'))
  digest=e.get('sha256',e.get('source_sha256'))
  if e['path'] not in cache:cache[e['path']]=file.read_bytes()
  original=cache[e['path']];assert sha(original)==digest,e['id']
  start,end=e['line_start'],e['line_end']
  quote='\n'.join(original.decode(encoding).splitlines()[start-1:end]);assert quote==e['quote'],e['id']
  heading_line=sum(len(x.splitlines())+1 for x in parts)+1
  parts.extend(['## '+e['id'],'',f"来源：[{file.name}]({file.as_posix()}:{start})；第{start}—{end}行；编码`{encoding}`。",'',f'原文件 SHA256：`{digest}`','', '````text',quote,'````',''])
  evidence_receipts.append({'id':e['id'],'source':e['path'],'sha256':digest,'encoding':encoding,
   'line_start':start,'line_end':end,'quote_matches_source':True})
 out=O/'书证'/(key+'-原书原文.md');out.write_text('\n'.join(parts),encoding='utf8')
 evidence_links[key]=out.relative_to(O).as_posix()
# Already-rendered U-rule evidence is copied intact, rather than reparsed as JSON.
module('confirmed-policy-evidence','U口径的SG连续书证','SG来源原文与采用边界；不是待执行的新规则','书证')

def link(row,snapshot=True):
 return f"[{row['title']}]({row['snapshot'] if snapshot else (R/row['source']).as_posix()})"
def table(keys):
 out=['| 原文 | 审查重点 | 当前实际文件 |','|---|---|---|']
 for key in keys:
  r=bykey[key];out.append(f"| {link(r)} | {r['description']} | [活动原文件]({(R/r['source']).as_posix()}) |")
 return '\n'.join(out)
def excerpt(key,match):
 s=(R/bykey[key]['source']).read_text('utf8');line=next((n,x) for n,x in enumerate(s.splitlines(),1) if match in x)
 n,text=line;return f"> {text}\n\n出处：[{bykey[key]['title']}，第{n}行]({(R/bykey[key]['source']).as_posix()}:{n})。"

index=f'''# 当前判断依据与关键原文审查目录

快照日期：2026-11-12（北京时间）。绑定活动版：`{p['release']}`；方法hash：`{p['methodVersion']}`。

这是供你人工审查的资料包，**没有改动活动规则、提示、原书或两库开关**。目录内“现行共用原文”“分类占原文”“执行与工具原文”均为对应活动文件的逐字节副本，没有将正文改写成另一份摘要。修改意见应另记，不能把这份审查快照误当新的活动入口。

## 先分清三种“原文”

1. **实际执行文本**：skill、judgment-core与各domain等，是模型当前收到的规则。它们包含项目归纳和用户采用口径，不全是古籍引文。
2. **原书原文**：书证目录中的连续选段，保留编码、hash、原文件及行号；用来审查项目规则是否忠实、条件是否遗漏。
3. **本目录导读**：以下分层和审查问题是便于阅读的导航，不新增专业规则，也不冒充北海原文。

## 当前文件怎样分层

目前没有17份各自独立的分类SKILL.md：共用`daliuren`总入口，专业执行采用`judgment-core`加本问`domains/…md`；详细方法按需查询。Codex另有宿主skill处理工具与裁决分工，并非另一套专业断法。

“通类”也没有独立名为通类的skill，目前主要写在`positioning`和共用核心U11中，具体通用象义还分布在`shenjiang-use`、`shen-symbols`、`jiang-symbols`及理气等模块。这一点本身可以作为本轮结构审查对象。

建议先审下面七份，再进入具体分类。这是人工审查阅读顺序，不是给普通占断新增七项必读。

{table(['daliuren-skill','judgment-core','positioning','classification-priority','shenjiang-use','liqi','analysis-workflow'])}

## 第一层：谁代表谁，以及通类和专类的关系

需要审查：实际当事人与代问者怎样定位？日干、日支在不同占类是否有明确职责？通类和专类是在回答同一件事，还是分别回答不同环节？什么条件才允许更换或递补主类？

以下直接摘录当前执行文本：

{excerpt('positioning','按“现实对象')}

{excerpt('positioning','通类定大方向')}

{excerpt('judgment-core','2. **明占类')}

## 第二层：分类占的完整正文

先看`classification-priority`中的职责和主次总表，再读相应domain全文。总表不是对全文全部条件的替代；同属“考试”仍须区分考生、成绩、学校、资格、证书和通知。

{table(list(domain_labels))}

分类书据：[48段原书连续原文]({evidence_links['classification-evidence']})，以及同目录未经改写的`classification-evidence.json`。CF-E编号对应证据，不是程序打分或吉凶权重。

## 第三层：支神、天将与取象

需要审查：象义如何定位到具体对象？天将与本家支同用、互换分别属于什么方法？互换会不会偷换实际坐标、旺衰和作用？

{table(['shenjiang-use','shen-symbols','jiang-symbols'])}

{excerpt('shenjiang-use','本机围绕本问')}

## 第四层：状态、有效作用、方位和流向

这里分开两种“定位”：`positioning`解决人事角色和职责；`movement`及失物、出行专项处理具体动向、流向和相关空间线索。不能把前者直接理解为地理方位。

需要审查：谁生谁、谁克谁，关系是否能实际作用？自身有力是否等于能为我所用？气地、空亡、阴神、神将和制救有没有重复或漏掉？

{table(['liqi','void','movement','book-logic','confirmed-policy'])}

U口径书据：[SG连续书证]({bykey['confirmed-policy-evidence']['snapshot']})。其中未采用部分须按原文自身说明辨别，不能把书证全段自动当执行规则。

## 第五层：课体、毕法和神煞怎样参与

{table(['structure','analysis-workflow','bifa','bifa-basic','shensha-use'])}

综合流程书据：[14段北海原书连续原文]({evidence_links['analysis-workflow-evidence']})。

尤其可以对照北海“明占类，定侧重，看显象”“先观课体大象”等原文，与本机采用的毕法辅助边界。原书观点、本地选择及工程约束应分别审查，不能混称为北海唯一流程。

## 第六层：旺衰、取数和应期的执行依据

{table(['quantity','quantity-strength','quantity-correction','timing'])}

研究分段及系数是项目约定，不能当作北海原文或已校准的自然单位。要审查其适用层次，再看最终数量是否真的消费了对应计算回执；原书选加乘已使用的气态，不能无说明再算一轮。

## 第七层：裁决者实际执行和主智能体核对什么

{table(['codex-skill','adjudication','report','consistency-audit','deterministic-tools'])}

这部分用于审查“规则是否真正进入工作流程”，不代替专业取用判断。程序能核哈希、坐标、算术和所声明覆盖，不能证明主类选对或通路解释正确。

本次整理发现一个可单列的入口问题：`references/deterministic-tools.md`文件存在、已列入manifest.files，但`manifest.modules`没有同名`deterministic-tools`登记；部分正文却写“查deterministic-tools”。因此该字串目前不能直接当作reader的module ID。本资料包保留该文件原文供审查，未借整理过程修改活动规则或接口。

## 审查记录方式与校验

可按“文件/段落—原句—你的疑点—拟改方向—对应原书依据”标注；先保留原句，再区分来源摘录、项目归纳和采用决定。本次未预填你的意见，也没有把尚待讨论的问题改成规则。

共收录{len(rows)}份现行文件，17分类完整正文；另回源核对62段分类与综合流程书证。每份现行文件的原路径、快照路径、SHA256及行数见[原文清单](原文清单.json)。现行正文副本均与源字节一致；62段书证的编码、文件hash、行号及全文相符。复制与核验不等于已经完成本轮语义审定或预测验证。

本次未检索经验库、案例库或旧检索缓存，未修改活动版，未调用预测模型。
'''
(O/'审查目录.md').write_text(index,encoding='utf8')
receipt={'release':p['release'],'methodVersion':p['methodVersion'],'review_only':True,
 'files':rows,'verified_book_passages':evidence_receipts,'active_files_modified':False,
 'case_experience_retrieval':False,'predictive_validation_count':0}
(O/'原文清单.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
assert (R/'.opencode/liuren-active.json').read_bytes()==json.dumps(p,ensure_ascii=False,indent=2).encode()+b'\n','Pointer changed'
for r in rows:assert sha((O/r['snapshot']).read_bytes())==r['sha256']==sha((R/r['source']).read_bytes())
print(json.dumps({'review':str(O/'审查目录.md'),'release':p['release'],'copied_files':len(rows),
 'domains':len(domain_labels),'source_spans_verified':len(evidence_receipts),'active_unchanged':True},ensure_ascii=False,indent=2))
