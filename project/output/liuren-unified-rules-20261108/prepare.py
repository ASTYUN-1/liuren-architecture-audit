"""Prepare local32 without editing frozen31 or activating an incomplete release."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
OLD='20261107-slim-31'; NEW='20261108-unified-32'; R=ROOT/'runtime/liuren'/NEW
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text('utf-8-sig'))
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def write(p,s):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s,encoding='utf-8')
def replace(p,a,b):
 s=p.read_text('utf-8-sig');assert a in s,(str(p),a[:90]);write(p,s.replace(a,b))
assert load(ROOT/'.opencode/liuren-active.json')['release']==OLD
assert not R.exists(), 'Do not overwrite a prepared release'
rels=['.opencode/liuren-active.json','.opencode/oh-my-opencode-slim.jsonc','opencode.json',
 '.opencode/skills/liuren/daliuren/SKILL.md','integrations/codex/daliuren-codex/SKILL.md',
 'integrations/codex/daliuren-codex/references/host.md','tools/liuren-deterministic.mjs',
 'tools/liuren-deterministic-io.mjs','tools/liuren-core-handoff.mjs','tools/liuren-flow-control.mjs',
 '.opencode/plugins/liuren-adjudication.ts','tools/tests/liuren-deterministic.test.mjs',
 'tools/tests/liuren-core-handoff.test.mjs','README.md','目录总索引.md','AGENTS.md',
 'docs/本机六壬高效执行.md','docs/本机六壬完整研判流程.md','docs/本机六壬稳定运行指南.md',
 'docs/Codex大六壬工作流.md']
for rel in rels:
 dst=OUT/'before'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,dst)
global_skill=Path('C:/Users/QLMa_/.codex/skills/daliuren-codex')
for rel in ['SKILL.md','references/host.md']:
 dst=OUT/'before/global-skill'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(global_skill/rel,dst)
frozen={f.relative_to(ROOT/'runtime/liuren'/OLD).as_posix():sha(f) for f in (ROOT/'runtime/liuren'/OLD).rglob('*') if f.is_file()}
evidence=load(ROOT/'output/liuren-four-guides-audit-20261108/连续原文与来源.json')
source_hashes={rel:sha(ROOT/rel) for rel in evidence['source_scope']}
dump(OUT/'before.json',{'files':{rel:sha(ROOT/rel) for rel in rels},'frozen31':frozen,'sourceBooks':source_hashes,'globalSkill':{rel:sha(global_skill/rel) for rel in ['SKILL.md','references/host.md']}})
shutil.copytree(ROOT/'runtime/liuren'/OLD,R)

policy='''## 已确认判断口径 U01—U11（主智能体与裁决者共同执行）

身份：这是用户本轮确认采用的本地体系及工作约定，不声称诸书完全一致或预测效果已经验证。原书保留原字；下列口径控制本版本的执行。旧摘录中的相反说法只作来源，不是可以逐盘任选的另一条指令。尚未定清的具体边界只登记在pending-conflicts，不能把已确认内容重新列为二说。

- **U01 原文与执行。**“凡、必、百无一成”等强语保留原貌，执行时解释其对象、条件、机制及范围，不做无条件成败开关；也不能借“夸张”随意否定切题的反证。区分原书、讲解、本轮归纳、用户体系选择和现实反馈。
- **U02 喜旺恶衰。**采用北海“壬学喜旺恶衰，无论喜忌”的核心趋势；吉神旺吉力足，衰则吉力减；凶神旺时可表现为威权、秩序或贪荣，衰败时凶态可加重。官鬼旺偏权威权势、衰偏凶恶侵扰是趋势形容，不是固定人物职业，也不是所有具体组合自动吉凶。禁止把“鬼旺”直接当作“攻击伤害更大”，禁止把凶将死墓绝直接当作无害。有效作用能力、表现性质、受者承受及制救分开，再看本问结果。旺鬼贪荣有当令时限，后来衰败可能转患；当前结果与后患分别论。刑虎等交叉见C03。
- **U03 直接临生合与外来生扶。**鬼煞直接临于生合之处，贪生合停害；须指明上下直接作用的位置。别处生扶不等同于在所在之处贪恋，可增强其已有作用。两者不是同一条件的矛盾。不能把日干或吉神得生一概判作失用；贪生停用能否扩大到财类等非官鬼，尚见C02，不能自行扩大或抹掉原文。
- **U04 十二气跟随所看对象。**日干状态采用天干十二长生：阳顺阴逆，甲亥乙午丙寅丁酉戊寅己酉庚巳辛子壬申癸卯起长生。支神、天将等按自身五行采用木亥火寅金巳水土申顺行。明确“谁在何处”：丁见未为冠带；白虎（金）乘申为临官，申（金）坐午为沐浴；天将对乘支、支对地盘、天将对地盘分列。不采用天一群笔记“十二长生永远以日干为准”，也不以五行顺行表覆盖阴干。日干寄宫不是日干五行替身。
- **U05 生克刑合并见。**生克、刑合可能并行，不因有两种关系便列两套结论。依相应连续原文的双方旺衰、乘将、上下位置及时间确定主作用；如庚辛与巳兼长生和火克、寅巳兼生刑、未亥兼克合，须保留各自条件。半合、刑、合化的存在与效力分开；不凭“大势”循环证明大势，也不自行合化。
- **U06 制救。**同时看受者、施者：身、鬼和救神各自的气态、位置、通路、神将及吉煞条件。鬼衰而凶态显、旺子孙能实际制之，可减害；救神气弱，不能因有子孙或吉名保证救成。德等可增强化煞吉力，仍核落点、受制及作用；既不一德包治，也不忽略有效德解。只缓解局部就只判局部；关键阻碍确被解除，可改变结果。发用之鬼末传可制、末传之鬼发用不能制等时序条件按对应专法保留，不作全盘无时序相抵。
- **U07 天时、地利与综合旺衰。**月令主管天时及五气，坐处主管地利；月令得气是重要源条件，不把它与坐处看成可任意互换的二说。失令得地不自动大成，得令失地亦须看受限处；一个“衰”字不抹去天时，一个“旺”字不保证实现。狭义月令旺相休囚死和广义综合旺衰分名记录；广义旺衰描述对象的总体状态，空亡亦为其条件之一。生处、坐处、制处和承接条件共同分析，未确立数值能量单位、固定加权或胜负阈值，禁止伪造方程。季土细分见C05。
- **U08 空亡事实与效应。**程序旬空身份保留；综合月令、生处、坐处、制处、空的是谁、所求环节及制救判其实际影响。不得“空必败”“旺必不空”“有生便兑现”或“月必压空”；也不把岁月有权等同于旬空字段取消。“日可搏月”的讨论兼指能力强弱、权柄与持续性，不能缩成仅时间长短。用户举出的两个极端是方向示意，不是已定阈值。此处已统一分析方法；具体何种中间组合足以落实尚见C04，不能又把整个空亡问题泛称未决。
- **U09 四建分工与效力。**采用《壬归》及北海：岁月重权柄及重大影响，日辰定相关人事，正时为先锋显端倪、近速；月令定五气不以月建入传为前提。力量由所论对象的气地、实际关系和承接决定，权柄大、发动快、作用久是不同维度。入课传是重要作用位置，非固定倍数；闲地仍可能由岁月上神等切题关系起作用，不能直接忽略。长短问题调整观察时段，不倒置总排序。不采用“年最小、时最大”，也不建立“年必胜月必胜日必胜时”；发用重要不等于压倒一切。时支、时干、时上神各署身份。“月克日、时生日”不能无据推出先凶后吉，失令也不能一律虚不受补。
- **U10 时间推进。**旺衰、空亡和有效制救须随所判时段更新；推应期检查出旬、逢值、冲填、季节变化改变了哪项条件，原占盘不擅自更换。出旬只解除该旬的空条件，不自动保证成功；旺鬼当时无患不推成永久无患。未发生的转折保留为待验条件。期限内完成、最终完成与后患分别答。
- **U11 两级裁决与矛盾处理。**主智能体准备中性材料，候选可纠正，focus_issues只列真实未知条件或C编号，不把U01—U10重新当成两派供选择；必要观察说明适用U编号及最强反证，不先写完整判词。裁决者从完整盘独立查漏，依本版U规则裁作用与结果，不能从旧书句任选反向口径。相反材料先比较对象、位置、时段、气态、占类及范围；可并行者分层，已选体系者按U执行，仍未定的同条件冲突登记具体来源和决定性缺口，不凭口味选边。报告在决定性处简述采用规则及为何最强反证不足；不强制填表或复述全部规则。主智能体核事实、引用、覆盖、内部及U口径一致性，不能另行折中改判；具体违规须逐字定位报告、指出U编号并附绑定规则/来源证据，依宿主一次补核协议处理，Codex复用原子智能体。单纯不同意结论或格式差异不重裁。已知原案反馈不混入新的盲断材料。
'''
pending='''# 尚待统一的具体边界

本表仅记录尚未确认的适用边界，不重新开放U01—U11；非全书穷尽审查。没有新增确认前，不得将候选解释写成已定规则。决定性问题不能裁清时，指出具体条件及影响的答案精度，不为每个案件机械输出双分支。

| ID | 具体问题与出处 | 当前处理及待确认点 |
|---|---|---|
| C01 | 财通类/专类及不入课传：finance 的LR26-TXY-D01；《理法简易》LF697—698、1355—1358、1719—1724、1740—1744，《壬归》LF355—359 | 财爻主线组织已保留；俱现时专类优先与财爻优先的同条件边界尚未明确。不能按作者名次裁决。待明确何问取专类、何问取财爻，以及类不入仍能得财的具体条件。 |
| C02 | 贪生停用是否限官鬼：《理法简易》正式splitlines 815—819有“类神临生临合…不能为我所用”；《毕法赋全解》1261—1273有财贪荣、身弱不可取而身旺可争取 | U03已解决直接临生合与别处生扶的区别；仅对官鬼适用仍是用户倾向，未确认为通则。待核财贪荣究竟是财停用还是取者能力不足，出行恋生是否另属行动关系。 |
| C03 | 旺鬼贪荣与刑虎组合：《毕法》1237—1245；E20指南注解旺神相刑、E15壬归出行鬼禁日、E07北海相应解说；SG10玉连环秋旺金鬼而木身火救皆弱 | U02趋势已定，非“旺鬼一律无害”。待明确刑虎、身衰、救衰交叉时的具体制胜条件，不能把专例当作恢复“鬼越旺越凶”的通则。 |
| C04 | 空的具体效应：《理法简易》LF2744—2802及特训班LF78—81；SG13—SG15；void-method-conditions | U08及U10已定。未定的是旺、生、受制、空在非极端组合中何时只迟、何时不能落实；玄蛇空反凶与凶空无力、脱空仍耗的对象边界亦须补足。不能量化造阈值。 |
| C05 | 月令五气的季土细分：程序同时输出four-seasons与quarter-earth；deterministic-tools现保留两表 | U07月令主管天时已定；辰未戌丑按整季余气、整月土旺或分节用事尚无本轮统一采用证据。两表作为敏感性资料保留；不得逐盘挑选有利表。若两表改变决定性作用，应披露具体差异待确认。 |
| C06 | 半合、刑和四纲引化：《理法简易》821—849；liqi-sources TY-05/TY-08；methods/relations | U05关系并行已定。北海二字成刑/半合与笔记四纲引化不是同一构成；不能把半合当化局，也不能以上四纲当免刑。合化、单见自刑、刑的方向与有效性尚需各自明确采用范围。 |
| C07 | 类不现、神将互换的搜索范围：shenjiang-use；北海分类不现路径与笔记四课/八门不同 | 本家对应和真实坐标不互代已定。是否扩到八门来补出原本不现的专类，尚需按占类确认；不得以互换自动取消不现条件。 |

行号说明：LF为历史规则卡原行号；明确写“正式splitlines”的为Python splitlines一基行号，二者不可混报。原书未改，引用时沿所选连续摘录的行号模式核对。
'''
write(R/'references/confirmed-judgment-policy.md','# 已确认的本地判断规则\n\n'+policy)
write(R/'references/pending-conflicts.md',pending)
ev=dict(evidence);ev['professional_rules_modified']=True;ev['scope']='已核连续原文快照；采用/排除状态见U规则，不以书证等同效果验证'
for e in ev['evidence']:
 src=ROOT/e['path'];assert sha(src)==e['sha256'];rows=src.read_text(e.get('encoding','utf-8-sig')).splitlines();assert '\n'.join(rows[e['line_start']-1:e['line_end']])==e['quote'],e['id']
write(R/'references/confirmed-policy-evidence.md','# 已核连续书据 SG01—SG18\n\n原书连续选段及身份如下；SG07总力量排序不采用，SG08为比喻而非案例。采用边界见U规则。\n\n'+'\n\n'.join('## '+e['id']+' '+e['topic']+'\n\n来源：'+e['path']+'；'+str(e['line_start'])+'—'+str(e['line_end'])+'；'+e.get('encoding','utf-8-sig')+'；splitlines；SHA256 '+e['sha256']+'\n\n'+e['quote'] for e in ev['evidence']))
dump(R/'references/confirmed-policy-evidence.json',ev)
core=R/'references/judgment-core.md';s=core.read_text('utf-8')
s=s.replace('程序并列的季节口径不混票、不为结果换法','季土细分仅依C05保留敏感性，不混票、不为结果换法')
s=s.replace('生可能扶身也可能助病鬼','生的直接临处与别处扶助按U03区分，可能扶身也可能扶既有病鬼作用')
s=s.replace('生扶解空、旺不为空、填实与实现的原法张力尚存，遇关键实现相反查void及void-method-conditions，不能把得到生扶一概写成得到结果','采用U08综合判断空的效应；具体中间组合及特殊空义见C04，需要时查void及void-method-conditions，不能把得到生扶一概写成得到结果')
write(core,s+'\n'+policy)

# Replace obsolete active instructions rather than merely attaching a later disclaimer.
replace(R/'methods/liqi.md','旺者若为所忧之病、官鬼，得旺可能加重风险；','采用U02喜旺恶衰，官鬼得旺不可直接当作害力加大，须辨贪荣时限、具体凶态及受者/救者状态；')
replace(R/'methods/liqi.md','十二气有参照对象：《笔记》的十二长生总论以日干为准；《壬归》类神临地法考察类神自身与坐处。论天将自身气数又是另一层。','十二气按U04跟随所看对象：日干用天干阳顺阴逆；支神与天将用五行顺行。天一群笔记的日干总参照不采用；《壬归》类神临地法保留对象与坐处。')
replace(R/'methods/liqi.md','没有充分依据不预设任何一层永久优先。','月令主管天时、坐处主管地利，按U07分工综合，不建立无条件胜负表。')
replace(R/'methods/liqi.md','病鬼旺与救神旺所利不同；旺相不自动有利','采用U02喜旺恶衰趋势；官鬼旺不可直接视作更凶，救神旺仍需能救达；旺相不自动保证所求实现')
for rel in ['methods/liqi.md','methods/void.md','methods/timing.md','methods/structure.md','methods/shenjiang-use.md','methods/report.md','references/void-method-conditions.md','references/adjudication-method-conditions.md','references/expert-adjudication.md','references/liqi-sources.md']:
 p=R/rel;s=p.read_text('utf-8');lines=s.split('\n',1);write(p,lines[0]+'\n\n执行采用judgment-core的U01—U11；本页引文是来源材料，不恢复已停用的相反指令。尚待确认的具体边界只见pending-conflicts的C01—C07，不能笼统重开全部理气争论。\n'+lines[1])
replace(R/'methods/void.md','沿本问所选方法完整分析。下列真异说若使关键实现相反，又无原文明示的区别，保留具体结果分支；不临场拣吉凶断语拼接。','按U08及U10分析空的事实、综合效应及时间变化。下列摘录保留原法身份，不允许任择“空必败”或“旺必不空”；决定性中间条件未定时定位C04，说明缺的是何种实现条件。')
replace(R/'methods/void.md','原局事实、力量作用、事件实现、应期分开，这是防混用的组织安排，不能冒充原书分歧已统一。','原局事实、综合状态、实现与应期按U08/U10分开。此分析口径已确定，原书并未因此字面一致；具体适用阈值仍属C04。')
replace(R/'methods/void.md','空亡的净影响直接写入同一作用主线，沿用已核节点。上述为断法的真实分歧，不能因为盘式可信便认定已经消除','空亡的净影响按U08直接写入同一作用主线，沿用已核节点。C04只保留未定的具体效应边界，不把U08已定原则再交裁决者任选')
replace(R/'references/liqi-sources.md','《笔记》日干十二长生与《壬归》类神自身临地十二气并列保留，未证明可互相替代。','按U04执行：日干天干十二长生、支将自身五行十二气分列；《笔记》永远以日干为准的总参照只作历史来源，不采用。')
book=(R/'references/adjudicator-book-basis.md').read_text('utf-8')
book=book.replace('本次类神十二气按此口径，不用出生推命的阴阳干逆运','本次仅支神/天将自身十二气按此五行顺行口径；日干依U04采用天干阳顺阴逆')
book=book.replace('不把引擎日干逆运表自动当成已核原法','日干按U04采用天干阳顺阴逆，不把五行顺行表套到阴干')
book=book.replace('因为得旺者可能反而加强对类将的伤害','须辨此处得旺的对象、内战实际方向与类将受损，不能改成所有旺鬼必增害')
book=book.replace('生鬼增患与贪生不施克也不能静默合并','直接临生合与外来扶助按U03区分；非官鬼停用范围只保留C02')
book=book.replace('鬼煞贪生合也可能不来害我。这是特定作用解释，不能据此断一切受生都失去克力','鬼煞直接临生合停害按U03执行；外来生扶另论。类神停用能否扩及财类尚见C02，不把一切得生解释为失用')
book=book.replace('## 必须保留的分歧与限制','## 原文身份、采用及边界')
book+='\nU01—U11是本版执行口径；E18的日干总参照与E16的年小时大总排序不采用。E07/E15/E20/E21的组合边界仅属C03。连续书据另可按module查confirmed-policy-evidence；pending-conflicts不是每案待办表。\n'
write(R/'references/adjudicator-book-basis.md',book)
role=(R/'references/adjudicator-prompt.md').read_text('utf-8').split('# 固定书据：')[0]
role=role.replace('引擎 growth.day_stem 可能采用另一口径，不能直接当所选原法已核结论','日干采用U04天干阳顺阴逆，支神天将采用五行顺行；程序同时提供天将对乘支与对地盘的不同参照')
role=role.replace('原法冲突未解，列出分支与缺口','U02趋势照常执行；C03具体组合仍缺条件时才指出边界')
role=role.replace('财生鬼可加害，救者被制可失救，贪生合也可能不能为我所用。原文边界不明时列未决，不能自造通解','直接临生合停害与外来生扶按U03区分，后者可扶既有作用；救者被制可失救。非官鬼停用范围仅列C02，不把所有生合重新列为未决')
role+='\n## 本版矛盾裁决职责\n\n严格采用核心U01—U11；这些是本地已确认规则，主智能体未主动提起也须遵守。主智能体候选不约束你从完整盘补漏。相反摘录须先辨对象、上下直接关系、时段、气态、占类和原文范围；不可重新选择已排除的学说，也不可用一句喜旺恶衰遮去真实反证。未知边界限C01—C07，只有实际影响结果时才查相应连续原文并说明未定条件，不为了看似果断造阈值。决定性处简述适用U编号、实际条件和最强反证处理。具体口径违规按一次补核协议纠正，主智能体不得自行改判。\n\n'+book
write(R/'references/adjudicator-prompt.md',role)
cfg=load(ROOT/'.opencode/oh-my-opencode-slim.jsonc');cfg['agents']['liuren-adjudicator']['prompt']=role;dump(ROOT/'.opencode/oh-my-opencode-slim.jsonc',cfg)
op=load(ROOT/'opencode.json');op['agent']['liuren']['prompt']+='\n采用活动judgment-core的U01—U11。准备时将已确认口径与真实未知分开，已定规则不重新作两派争点，focus_issues只留真实条件缺口/C编号；子智能体按同版规则独立裁。返回核事实、引用、覆盖及U口径一致性；具体违规定位原文、U编号及绑定证据，依一次补核协议处理，不自行折中或以不同意结果重派。'
# Only update literal release paths in live host configuration.
dump(ROOT/'opencode.json',json.loads(json.dumps(op,ensure_ascii=False).replace(OLD,NEW)))
ad=R/'methods/adjudication.md';s=ad.read_text('utf-8');s=s.replace('仅具体事实/引用错误或needs_input且补真实新材料','仅具体事实/引用/已确认U口径错误或needs_input且补真实新材料');write(ad,s+'\n'+'''## 已确认规则与冲突交接

主智能体先采用核心U01—U11，真实未决仅限具体条件及C编号；不把已定规则列作可任选的正反派，不将观察写成完整裁决。必要观察带适用U编号及真实反证。裁决者对照同版核心，从完整盘补漏；旧书异句不自动成为相反执行指令。

主智能体返回核对包括U口径一致性。具体违规逐字指出报告、U编号及规则原段；绑定该规则或原书为真实补核材料，按retry_context最多一次补核。error_path自由正文用$，JSON用真实字段；不得伪造现实事实作重派理由，不同意结论不算违规。Codex沿用原子智能体补核；OpenCode沿原领取及retry协议，保留前后版本。工程仅验证证据/传输，不自动裁专业正确。
''')
shared='''\n已确认判断口径以活动judgment-core的U01—U11为准。主智能体准备时不将已定规则重列为两说，真实缺口才列C编号及所缺条件；子智能体依同版规则独立查漏裁决，不能从旧摘录任选反向口径。返回核对包含U口径一致性；发现具体违规，逐字定位报告及U编号，附绑定规则证据，沿宿主一次补核协议处理，不由主智能体自行折中改判。\n'''
for rel in ['.opencode/skills/liuren/daliuren/SKILL.md','integrations/codex/daliuren-codex/SKILL.md','integrations/codex/daliuren-codex/references/host.md']:
 p=ROOT/rel;s=p.read_text('utf-8');s=s.replace('仅具体事实/引用错误或真实新增必要材料','仅具体事实/引用/已确认口径错误或真实新增必要材料');s=s.replace('当前方法的空亡生扶等缺口仍保留；更换模型不等于专业问题已解决','已确定U口径已进入共用核心；具体待确认边界见pending-conflicts的C01—C07，更换模型不等于这些边界或预测效果已经验证');write(p,s+shared)

# Deterministic facts: stem cycles vs element cycles; two distinct general coordinates.
p=ROOT/'tools/liuren-deterministic.mjs'
replace(p,"const START={木:'亥',火:'寅',土:'申',金:'巳',水:'申'};","const START={木:'亥',火:'寅',土:'申',金:'巳',水:'申'};\nconst STEM_START=Object.fromEntries(GAN.map((g,i)=>[g,[...'亥午寅酉寅酉巳子申卯'][i]]));\nexport const growthProfile=subject=>GAN.includes(subject)?'stem-yang-forward-yin-reverse':'element-forward-water-earth';")
replace(p,"return STATES[mod(ZHI.indexOf(place)-ZHI.indexOf(START[element(subject)]))];","const stemIndex=GAN.indexOf(subject);const start=stemIndex>=0?STEM_START[subject]:START[element(subject)];const direction=stemIndex>=0&&stemIndex%2===1?-1:1;return STATES[mod(direction*(ZHI.indexOf(place)-ZHI.indexOf(start)))];")
replace(p,"general_growth:{reference:r.tianjiang,ground:growth(r.tianjiang,r.di),profile:","general_growth:{reference:r.tianjiang,branch:growth(r.tianjiang,b),ground:growth(r.tianjiang,r.di),profile:")
replace(p,"growth:{profile:'element-forward-water-earth',reference:stem,home:growth(stem,home),day_branch:growth(stem,c.day_branch)}","growth:{profile:growthProfile(stem),reference:stem,home:growth(stem,home),upper:growth(stem,upper),day_branch:growth(stem,c.day_branch)}")
replace(p,'engine day-stem table retained separately; may use yin-stem reverse convention','engine day-stem table retained; U04 adopts stem yang-forward/yin-reverse')
replace(p,"growth:'element-forward; 木亥火寅金巳水土申; not yin-stem reverse'","growth:'U04: stems yang-forward/yin-reverse; branches/generals element-forward 木亥火寅金巳水土申; each object/place explicit'")
p=ROOT/'tools/liuren-deterministic-io.mjs'
replace(p,'calculate,growth,kin','calculate,growth,growthProfile,kin')
replace(p,'place,growth:growth(subject,place),subject_to_place','place,growth:growth(subject,place),growth_profile:growthProfile(subject),subject_to_place')
p=ROOT/'tools/liuren-core-handoff.mjs'
replace(p,'general_growth:n.general_growth.ground','general_growth:[n.general_growth.branch??null,n.general_growth.ground]')
replace(p,'growth:[n.growth.home,n.growth.day_branch]','growth:[n.growth.home,n.growth.upper??null,n.growth.day_branch]')
replace(p,'general_growth=将自身临地','general_growth=[将自身对所乘天盘支,将自身对地盘]；支将十二气=五行顺行；旧绑定包缺层显示null不推造')
replace(p,'growth=[本干寄宫,本干日支]；十二气统一沿用element-forward-water-earth，日干引擎异表仍保存在chart.growth','growth=[本干寄宫,本干寄宫上神,本干日支]；各干采用stem-yang-forward-yin-reverse；原引擎表仍保存在chart.growth')
replace(p,"'以下是主智能体候选材料，不是程序事实或既定结论；可纠正并从完整盘补漏。'","'以下是主智能体候选材料，不是程序事实或既定结论；可纠正并从完整盘补漏。已确认U01—U11须执行；focus_issues不重新开放既定口径，真实缺口见C编号。'")
pol=load(R/'references/deterministic-policy.json');pol['release']=NEW;pol['growth'].update(profile='object-dependent-U04',stemProfile='stem-yang-forward-yin-reverse',stemStart=dict(zip('甲乙丙丁戊己庚辛壬癸','亥午寅酉寅酉巳子申卯')),branchGeneralProfile='element-forward-water-earth',notEquivalent='stem and element cycles serve different objects; never interchange');dump(R/'references/deterministic-policy.json',pol)
replace(R/'references/deterministic-tools.md','类神自身十二气按当前已采用的木亥、火寅、金巳、水土申五行顺行口径；引擎growth.day_stem另有阴干逆行，保留作异口径材料，不能自动替换','按U04分对象：日干采用天干阳顺阴逆（丁见未冠带）；支神/天将采用木亥火寅金巳水土申五行顺行。天将对乘支与对地盘分别提供，不能只保留后一层；lookup返回growth_profile')

# Existing one-recheck guard remains evidence-bound and capped. Only its explanation changes.
for rel in ['tools/liuren-flow-control.mjs','.opencode/plugins/liuren-adjudication.ts']:
 p=ROOT/rel;s=p.read_text('utf-8').replace('具体事实/引用错误','具体事实/引用/已确认U口径错误');write(p,s)

# Register readable policy/evidence/remaining boundaries; full policy is already in mandatory core.
m=load(R/'manifest.json')
for id,file in [('confirmed-policy','references/confirmed-judgment-policy.md'),('pending-conflicts','references/pending-conflicts.md'),('confirmed-policy-evidence','references/confirmed-policy-evidence.md')]:
 m['modules'][id]={'file':file,'required':False,'requires':[],'trigger':'已确认U规则的出处或具体C边界需要定点查证时；不是每案附加清单'}
for file in ['references/confirmed-judgment-policy.md','references/pending-conflicts.md','references/confirmed-policy-evidence.md','references/confirmed-policy-evidence.json']:m['files'][file]=sha(R/file)
dump(R/'manifest.json',m)
write(OUT/'待确认矛盾清单.md',pending.replace('行号说明：','快速入口：活动运行包中的各模块及原书路径可直接核对，以下不代表全书所有矛盾均已查清。\n\n行号说明：'))
write(OUT/'已确认判断规则.md','# 已确认判断规则\n\n'+policy)
print('Prepared new32, backed up live files, left active pointer on31 until validation setup.')
