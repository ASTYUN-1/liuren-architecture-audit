"""Author the event-role revision in a candidate only; historical runtimes stay frozen."""
from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
R=OUT/'candidate-runtime'
NEW=json.loads((OUT/'before-manifest.json').read_text('utf-8'))['newRelease']
def read(rel): return (R/rel).read_text('utf-8')
def write(rel,text): (R/rel).write_text(text,encoding='utf-8')
def insert(rel,text):
    s=read(rel);a,b=s.split('\n',1);write(rel,a+'\n\n'+text+'\n'+b)
def replace(rel,old,new):
    s=read(rel);assert old in s,(rel,old);write(rel,s.replace(old,new,1))

policy='''## 本机执行：以事件为核心定位

本节为用户明确指定的本机占事规则。参考北海《六壬金针》LF584、586—589、2365—2368及《理法简易》LF377—381、1346：先识别所问之事及实际承担该事的对象，再依分类专法定干支和类神。不是“谁来问谁为日干”，也不是“所有占类日干永远为某个人”。

考试、考核、升学录取：日干代表实际考生；疾病、治疗、恢复：日干代表实际患者。换成父母、子女、姨舅、朋友或其他人代问，事件角色不随之改变。亲属称谓用于准确记录代问背景，不能以代问者为日干，再由父母/子孙/兄弟等递推来替换考生或患者。年命属于谁须单列，未知不借用代问者。

婚姻、攻守、胎产、人宅、交易等仍依该事件的专项对待轴确定角色，例如传统婚配干男支女、攻守干攻支守、占产干儿支母；提问者的身份不能挤占这些位置。没有人物的天气、作物等问题直接围绕对象取类，不强安一个代问人为中心。

《理法简易》LF1005—1007转引《说约》的嫡属六亲法，以及旧疾病亲属变法，保留原文和来源身份，属于可供知识研究的异法；本机普通单事流程不自动启用、不与事件定位并行投票，也不因哪条能得吉或吻合反馈而换法。只有用户明确要求比较该异法时，才单列参照分析，不能覆盖本流程主判断。这一执行选择不冒称古籍一致或经预测验证。

每个子问先在本轮已读的分类占中定位，再列“事件—当事对象—目标/问题—日干角色—日支角色—关键类神职责—年命归属”。这里的当事对象可以是人、物或组织；代问者若没有参与事件，不必占用一个课位。类神必须说明是人、成绩、学校、病证、财物、阻碍还是救应，不因六亲名称就当作现实亲属。

交接每问必填domain（16专项ID）；考试/疾病再填actor_entity_id，引用考生/患者实体，其branch填占日干，不能换成寄宫支或子孙/父母爻。程序只检查引用、坐标和已读专项，不替模型推断现实人物。裁决者仍须对照原问检查该实体是否真是当事人，而非给代问者改个标签。
'''
insert('methods/positioning.md',policy)
replace('methods/positioning.md','存在会改变结论的候选时，比较各自条件、关系和最强反证','存在会改变结论且不违背本节事件定位的候选时，比较各自条件、关系和最强反证')
replace('methods/positioning.md','特殊代占/年命须有来源，不按称谓机械替换。','代问不改变既定事件角色；特殊年命参照须有来源，不按称谓机械替换。')
replace('methods/class-mapping.md','日干不由谁提问机械决定，也不永久等于事件主体；四课不按人数分配，多象可共指一人。','先按positioning固定事件及当事对象；考试干为考生、疾病干为患者，不由谁提问或亲属关系改换。其他专法依事件的对待轴，不把“核心”误写成所有占类日干只能为人。四课不按人数分配，多象可共指一人。')
insert('methods/relations.md','''## 干支角色与四课坐标不可互换

先执行positioning的事件角色，再解释四课。第一课为日干上神，第二课为干上神的上神（干阴）；第三课为日支上神，第四课为支上神的上神（支阴），具体坐标以程序facts为准。干二课/支二课是两组关系层，不是求测人、父母、孩子、学校四个人的席位；不因代问人数重排，不把第一课下神改成代问者的本命。

日干的寄宫、干上神和日干本身分列。六亲仍以占日干计算；“子孙”可为作用义，不因代问者有晚辈便把子孙自动等同考生。日支取病证/学校/宅/相对方时须有本题专项依据，不能把同一论证中的支随意改成代问者或别的对象。改定位须撤销并重核受影响作用、制救和应期。
''')
insert('methods/shenjiang-use.md','事件定位先于神将象义：同一朱雀、父母、子孙等先核本问职责及作用对象。资格/成绩不是考生，病鬼不是患者，医生不是代问者；不能凭亲属称谓或孤立名象覆盖positioning及本问专项已定的干支角色。')
insert('methods/evidence.md','交接前核本问domain专项全文确已读取；只读class-mapping/positioning不能替代exam、illness等实际分类占。每问登记domain，考试/疾病登记actor_entity_id；核考生/患者确为事件当事人及日干，代问者不得经六亲递推顶替。程序随文件附完整定位规则与所选分类占，原问和候选供裁决者复核，已读同版内容复用。')
insert('methods/adjudication.md','事件定位是裁决前提：每问domain必填，考试/疾病用actor_entity_id绑定考生/患者且branch为占日干。漏读分类占先补对应模块，不能跳过或换domain绕过。裁决者收到M_EVENT_POSITIONING及M_DOMAIN_*完整正文后，先对照原问核现实对象，再裁生克；不得把代问者设为日干后用六亲递推当事人。')
insert('methods/report.md','开头用一句话交代“所问事件、实际当事对象、干支及关键类神职责”，不是报告代问者的个人吉凶。核裁决是否仍围绕同一考生/患者；病证、成绩、学校与当事人不互换。若定位错误，不忠实复制错误结论；按具体事实/定位错误补核规则处理，撤销其依赖关系，而非另做无依据的折中。')

domain_notes={
'exam':'本机事件定位：所问考生就是日干所代表的人，无论本人、父母、姨舅或朋友来问。成绩、学校、考官、资格和通知分别为该考试的对象/条件；不能先将代问者当日干再取子孙作考生。入学、转校以进入目标学校为标准，不以“答题顺利”或“有文书”替代录取。',
'illness':'本机事件定位：围绕谁患病、病势/治疗/恢复如何作判断，日干代表该患者，日支按本题病证/病事取法说明；虎鬼等病象、医药与救应另列。子孙代问长辈不把日干改成子孙后取父母为患者，父母代问孩子也不反向递推。病象得生和患者得生的利害不同。',
'finance':'本机事件定位：先定哪一笔钱、哪个经营/交易事件及实际收付双方，代问者不自动成为求财者。下文“我、本人、讨者”指事件中的相应角色；动静改位须来自事件阶段，不来自谁转述。钱、货、经营体与所得分开取类。',
'recruitment':'本机事件定位：问某人应聘/录用，围绕该应聘者、单位及岗位，不把代问亲属当本人；问单位招人则先明确招聘双方，不能照抄个人求职角色。考试过关与最终录用分子问，涉及考试的子问另登记exam并实读。',
'promotion-salary':'本机事件定位：围绕实际任职者、单位和职位/薪资变化；下文“人、本人”指该任职者，代问者不因开口就占日干。升职、调动、加薪的目标类神分别核，官鬼不自动等于某位提问者的长辈。',
'relationship':'本机事件定位：围绕所问伴侣双方及关系阶段，代问亲属不占婚配双方席位。采用传统异性婚配时依干男支女；女性本人来问也不据此改成干女支男。其他关系保留方法边界，不因“事件核心”就删除专项对待轴。',
'interpersonal':'本机事件定位：先定实际请求者、被请求者或合作双方，下文“我/彼”指事件双方，不是代问者/被代问者。动静、等待与回应依真实事件阶段，阴神不因现实多一人就自动分配给此人。',
'period-outlook':'本机事件定位：只有原问确为某人某时段的综合状况才用本模块，围绕被问对象而非代问者。年命和“我之所遇”归该对象；有明确单事目标时加载相应分类占，不用泛论替代考试、疾病等问题。',
'long-period':'本机事件定位：年限不改变事件对象。多年事业/财务仍围绕真正经历该事的人或组织，代问不切换成代问者的人生分析；各具体事件按相应分类占，正常年命归明确对象。',
'pregnancy':'本机事件定位：围绕是否受孕、孕期或分娩事件分清母体与胎儿。采用产时干儿支母是专项角色，丈夫、长辈代问不将日干自动改成自己；不把所有胎儿一律改成代问者子孙。',
'lost-person-object':'本机事件定位：先定所寻之人/物、失主、寻找者及是否已知被盗，代问身份不改变目标。所寻亲属不因六亲称谓替换本物专类/行人取用；玄武作走失者和作盗贼是不同事件职责。',
'classical-conflict':'本机事件定位：攻守用事件中的攻方/守方，干攻支守不随谁问而倒换；盗捕另分捕者、盗者、赃物。代问者不因与某方的亲属关系成为额外干支角色。',
'home':'本机事件定位：问哪处房屋、宅况、居住损益或迁居，先定实际住用者与该宅；干人支宅的人不是固定开口的代问者。宅的构件/损伤和人身结果分开，不能把宅的父母爻径认作现实父母。',
'travel':'本机事件定位：实际出行者/所候行人及目的地、归宿构成主线。家人代问不以家人作行者再用六亲替代出行者；行者、等待者、音信和到达分开，干陆支水等专法不与人物轴暗中混用。',
'weather':'本机事件定位：核心是所问地点、时段与晴雨风雪等现象，无须为传话者安一个人物主位。天气类神按本专项，房屋受灾或作物损失是另外的事件，分别加载home/agriculture。',
'agriculture':'本机事件定位：围绕实际农作、田圃、作物/畜禽、捕获或收成，干农人支田圃、干网支禽鱼等依具体专法。代问亲属不替代实际经营者；物类不是提问者的六亲人物。',
}
for name,note in domain_notes.items():insert('domains/'+name+'.md',note)
replace('domains/illness.md','北海概法干为病人支为病证；疾病分类又可用六合小儿等人物类。粹言另载子占父、妻占夫按六亲察类。它们的参照与适用层次应分别保留，不能把所有亲属代问强制归一套。','本机按事件定位采用北海干为病人、支为病证的主线；六合小儿等人物类只作本问有条件的辅助取类，不替换患者。粹言另载子占父、妻占夫按六亲察类，保留原法研究身份，本机普通单事不启用该身份切换，不与主线混用。')
replace('domains/illness.md','按 C16 注明患者与代问取法。','按 C16 固定患者为日干；代问关系只作背景，病证及医救另取。')
replace('domains/exam.md','按已读原书及本问为本人、考核、文书、资格或录取关系取用，说明为何采用某类神和位置。','按北海《六壬金针》LF2365以日干为考生，不论谁代问；依本题阶段另取考核、文书、资格和学校/录取类神，说明位置与职责。')
replace('domains/relationship.md','按题干当事人与代问视角取角色','按题干实际伴侣双方与所选专项取角色，代问者不占双方位置')
replace('domains/period-outlook.md','勾陈临干或作大运主题','勾陈临干或作阶段主题')

insert('references/adjudicator-prompt.md','''## 本机事件定位规则（先于作用裁决）

本机已由用户指定以事件为核心。先读packet.input_origin.source_text和每问domain，对照method_materials中的M_EVENT_POSITIONING、M_DOMAIN_*全文；不能只因主智能体列了角色便照单全收。考试日干为实际考生，疾病日干为实际患者；代问者是谁、与其何种亲属，不触发六亲递推来替换当事人。检查actor_entity_id对应的referent确是原问考生/病人，不能把代问者标成“考生”过检查。

先在scope_review.omission_check交代事件核心、实际对象、干支及关键类神职责，entity_checks.mapping_review说明相应取用；定位不成立先纠正或needs_input，禁止先裁错对象的吉凶。四课是干阳干阴/支阳支阴两组，不按代问者、孩子、学校人数分配。婚配、攻守、胎产等保留专项对待轴，不一律干人支事；天时等以现象为中心。

《说约》嫡属六亲法及旧亲属代占只保留来源研究身份，不覆盖本机已选的普通单事流程。程序附送的分类占是专业材料，不是主智能体初判；据完整盘独立核定位及作用，但不能把“独立”解释为重新启用被本机规则排除的代问者定位。定位变更须重核全部受影响生克、制救、应期及取数对象。
''')
insert('references/adjudicator-contract.md','14版每问domain必填；考试/疾病actor_entity_id必填并引用日干考生/患者实体。event_positioning为程序生成的角色与版本记录，不手填。文件自动附M_EVENT_POSITIONING及所选M_DOMAIN_*全文；输出scope_review与entity_checks先核实际对象，再裁作用。程序检查角色引用和日干符号，不替代语义核查。')
insert('references/deterministic-tools.md','14版事件角色：questions[].domain必填；exam/illness填写actor_entity_id指向实际考生/患者，其branch为占日干（不是寄宫支、子孙或父母）。完整定位规则和分类占由程序装入method_materials，event_positioning由程序生成。工具同时检查已读专项回执，缺项只补相关模块；程序没有自动选人、改盘或裁吉凶。')
insert('references/mapping-provenance.md','14版执行覆盖：历史positioning/疾病六亲代占上下文保留原字节；本机普通单事采用当前methods/positioning.md事件定位，考试/疾病不因亲属代问切换人物。以下历史引用、旧来源和异法不能作为绕过当前角色规则的执行入口。原书调查记录见output/liuren-delegated-positioning-20261106/代占取用定位核查.md；本次执行选择由用户明确指定，不冒称古法一致。')

write('references/event-positioning-policy.json',json.dumps({'schema':'liuren-event-positioning-v1','release':NEW,'authority':'explicit-user-instruction','scope':'local-opencode-event-divination','actorAsDayStem':['exam','illness'],'domains':list(domain_notes),'readDomainRequired':True,'attachFullDomainMethods':True,'kinshipDoesNotSelectActor':True,'sourceReferences':[{'path':'书籍库/北海闲人/六壬金针_修正版.md','lf':[584,586,587,588,589,2365,2366,2368]},{'path':'书籍库/北海闲人/理法简易.txt','lf':[377,381,1005,1007,1346]}],'sourceDisagreement':'嫡属六亲异法保留，不在本机普通单事自动执行','predictiveValidation':False},ensure_ascii=False,indent=2)+'\n')
print('Revised shared positioning, four lessons, handoff, 16 domains and adjudicator policy')
