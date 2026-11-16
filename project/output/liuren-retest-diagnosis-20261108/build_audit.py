"""Read-only retest diagnosis. Preserve actual packet/report and original sources."""
from pathlib import Path
import hashlib,json

ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
RUN=ROOT/'output/codex-liuren/codex-cf2f4c1f-6cfd-4c67-a044-1443482e7dd6'
load=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def link(rel,line,label):return f'[{label}](<{(ROOT/rel).as_posix()}:{line}>)'

run=load(RUN/'run.json');receipt=load(RUN/'receipt.json')
assert sha(RUN/'report.md')==receipt['report_sha256']
packet=Path(run['packet_ref']['file_path']);assert sha(packet)==run['packet_ref']['sha256']
core=load(packet)['reading_core'];assert hashlib.sha256(core['content'].encode()).hexdigest()==core['sha256']
parsed=json.loads(core['content'])
evidence=[]
def add(id,rel,a,b,identity):
    p=ROOT/rel;lines=p.read_text('utf-8-sig').splitlines()
    row={'id':id,'path':rel,'encoding':'utf-8-sig','line_mode':'Python splitlines, one-based',
         'line_start':a,'line_end':b,'quote':'\n'.join(lines[a-1:b]),'sha256':sha(p),'identity':identity}
    evidence.append(row);return link(rel,a,id)
rp=(RUN/'report.md').relative_to(ROOT).as_posix()
refs={
'judgment':add('R01',rp,23,35,'实际子报告公开论证；不读取或推断隐藏推理'),
'classification':add('R02',rp,39,47,'实际行业与职级选项论证'),
'stem':add('B01','书籍库/北海闲人/北海闲人-神将释.txt',469,473,'北海原书本地转录，非本轮补造规则'),
'tiger':add('B02','书籍库/北海闲人/理法简易.txt',1417,1427,'原书按占类取类'),
'strength':add('B03','书籍库/北海闲人/北海闲人-神将释.txt',413,417,'旺休参与辨物，不能省略其条件或扩成所有旺金必金融'),
'shen':add('M01','runtime/liuren/20261108-clarified-33/references/shen-symbols.md',59,63,'裁决实际已读摘要'),
'jiang':add('M02','runtime/liuren/20261108-clarified-33/references/jiang-symbols.md',53,57,'裁决实际已读摘要'),
'recruitment':add('M03','runtime/liuren/20261108-clarified-33/domains/recruitment.md',46,51,'核心装入的专项方法'),
'void':add('M04','runtime/liuren/20261108-clarified-33/references/judgment-core.md',26,28,'核心强制装入U07—U09'),
'medical':add('M05','runtime/liuren/20261108-clarified-33/references/shensha-use.md',35,36,'已读医神摘要的适用身份'),
'focus':add('P01','output/codex-liuren-prep-20261108-interview/packet-request.json',123,151,'主智能体原始焦点输入')}
policy=load(ROOT/'runtime/liuren/20261108-clarified-33/references/shensha-policy.json')
def find(d):
    if isinstance(d,dict):
        if d.get('id') in ('S17','S18'):return [d]
        return sum((find(v) for v in d.values()),[])
    if isinstance(d,list):return sum((find(v) for v in d),[])
    return []
medical=find(policy);assert len(medical)==2
reads=[load(p) for p in (RUN/'reads').glob('*.json')]
modules=sorted({p.get('id') for p in reads if p.get('view')=='reference'})
proof={'scope':'read-only diagnosis; no active rule edits or new model calls',
       'release':run['release'],'methodVersion':run['method_version'],
       'requested_adjudicator':run['requested_adjudicator'],
       'native_binding':load(RUN/'native-agent.json'),
       'main_model_identity':'用户说明双6.1 Sol；本轮仅据本地任务证据核子任务请求与记录，未单独核主会话模型设置',
       'packet_sha256_verified':True,'report_sha256_verified':True,
       'core_has_U08':'**U08 ' in parsed['shared_method'],
       'core_mentions_stock': '股票' in core['content'],
       'reference_modules_read':modules,'medical_policy_entries':medical,
       'source_evidence':evidence,
       'reality_feedback':'用户告知已任职、A；本轮不新增独立现实验证',
       'causal_status':'文本缺漏及公开论证可定位；未通过受控模型实验分离各缺陷的因果贡献'}
(OUT/'evidence.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
body=f'''# 同案复测：共享方法与裁决偏向的只读诊断

本轮核查实际Sol子任务，不修改活动规则、不重新占断、不调用模型。现实反馈沿用户提供的“已任职、A”，不将其冒称新盲测。

## 已确认：确实使用了33版与Sol高思考子任务

run.json、packet及report回执SHA256相符，核心含完整U08。子任务请求与绑定记录为gpt-6.1-sol/high/fork_turns=none，release为{run['release']}，methodVersion为{run['method_version']}。因此本次错误不能简单解释成仍读取旧31版或未传新版空亡原则。用户报告主子双Sol；本轮没有独立复核主会话模型设置。

## 录用判断：空亡仍被用成了默认待克服的障碍

实际报告承认旺身、旺禄、月建、日德、旺虎临官和单位相生，随后写“足以克服空禄及承接不实的实现通路”未建立，从而不录用。见{refs['judgment']}。

问题不是报告遗漏“综合”二字，而是论证有不对称：吉象被限制为“有意向/有职位可谈”，空亡却转为“实际承接虚”的肯定判断；“相生不必成功”不能单独推出“相生仅是意向、最终不成”。保留程序旬空身份，也不等于空亡效应已经成立。这是公开论证中的推导缺口，不能据此反推本盘只要旺就必成。

核心已要求综合分析，但旧招聘专项仍突出“类现、旺相/进气、不空陷、不变质”的成事组合、解空分路与有生亦空。见{refs['recruitment']}及{refs['void']}。若把原文的条件组合读成所有录用必须跨过的不空门槛，就会形成默认判败。此处是需要审查的规则编排/解释偏向，不是已经测得的数值权重。

主智能体未指定失败或B，但I_1仍优先聚焦旬空禄与承接，见{refs['focus']}。这种焦点是否造成锚定尚须对照实验，不能仅凭同一错答断言。

## 行业判断：金融的明确原文在摘要中被弱化

《神将释》明确写申为钱星、金融行业、银行、商人商户，见{refs['stem']}；《理法简易》明确写“股票：以白虎为通类”，见{refs['tiger']}。这两条应进入金融候选的具体比较，不能先降为没有专业来源的泛联想。

实际已读申摘要压缩成道路、交接、金属财物和加工，金融只在边界提醒中一带而过，见{refs['shen']}。白虎摘要列疾病、道路、征讨等，未保留股票专项，见{refs['jiang']}。实际核心没有“股票”一词；报告实际读取的E03是空墓生合段，没有回查上述两段金融原书。

报告最后将A评价为申金财物、青龙的“较泛”联想，同时展开B的白虎、天医地医、酉太常医药组合，见{refs['classification']}。可以确证的是金融证据表述与原书具体程度不相称；不能据此声称补回两句就已证明金融中层或保证模型改选A。

旺衰不只参与成败，也参与辨物。《神将释》有金银/刀具依旺休区分的明确条件，见{refs['strength']}。当前摘要保留金属、器物等名词，未完整传达这一辨别条件。此原段有酉虎等具体对象，不可扩大成所有旺金皆金融、休囚皆医疗。

## 医神及多处空亡：还需检查证据依赖与适用范围

本次天医戌、地医辰不是两套独立计算：现行S18明文是所选天医的对冲，均由同一月序确定。报告可讨论二者各自位置，但不能仅凭两个医名便视为两条独立行业佐证。已有医神摘要强调病占医药、不能凭名字认定现实身份，见{refs['medical']}；本轮报告未给出把该组合升为招聘行业判据的更具体原法。属于适用依据缺口，不能据此宣布天地医在招聘中一概无用。

申禄空、戌坐申空、命上酉空则同属申酉旬空的一组派生条件。它们作用环节可以不同，不应直接合计为三次独立判败。报告已说命上空不另算一次独立验证，因此本轮只把依赖性列为审查点，不声称已证实其机械三次扣分。

## 对后续优化的具体含义

优先修复原书到摘要的关键条件与义项损失，再审查“空的身份→承接必虚”“有吉不必成→只能当意向”的推导，以及医药、金融两边使用依据的标准是否对称。主智能体的内容核对也应能识别关键依据缺漏，不只核格式、引用和前后一致。

成败、行业、职级分开记录。可设计保留同一盘事实与模型设置、只替换明确缺漏摘要或重写焦点的配对实验，检查错误链在哪里改变；这些是方法实验，不是新现实盲测。先有可迁移的原书依据，再用未用于修订的其他题检验，不能只把本题修到A就宣布工作流可靠。

本轮确认共享资料和公开论证存在具体缺口，尚未分离空亡、摘要损失、焦点和模型判断各自的因果贡献。两个模型或两个相同模型使用同一套材料，不构成独立方法验证。
'''
(OUT/'复测问题定位.md').write_text(body,encoding='utf-8')
print('Read-only diagnosis saved; active runtime, books, task packets and original report unchanged.')
