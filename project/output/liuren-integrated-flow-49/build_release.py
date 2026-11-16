"""Build a fresh method release; never edit its frozen parent."""
from pathlib import Path
import hashlib, json, shutil
R=Path(__file__).resolve().parents[2]; O=Path(__file__).resolve().parent
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
enc=lambda d:(json.dumps(d,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
before=load(O/'before.json'); OLD=before['release']; NEW='20261112-integrated-flow-49'
assert all(sha(R/f)==h for f,h in before['frozen'].items())
T=R/'runtime/liuren'/NEW
assert not T.exists(), 'Existing candidate must be inspected, not overwritten'
shutil.copytree(R/before['runtime'],T)

flow='''## 49版综合主线：明占类、定侧重、察作用

本轮依北海《特训班讲义》“明占类，定侧重，看显象”及《理法简易》“课体看大象，类象定吉凶，理气为准则”整理执行。理气贯穿全程，不新增六十四课或毕法独立裁决轮次；原U01—U11、45版毕法采用边界及数值作答规则保留。

1. **明占类与目标**：分清实际当事人、所求、阶段、期限及成功标准；成否、出现、发展、属性分别定位。先读本问domain。通类、专类与不同类神按职责分工；同职责有明示首取/条件递补时依专项执行。没有适用排序不虚构总序，原法明确并看则兼看。
2. **观察气势、确定侧重**：从真实组合观察动静、进退、明暗、缓急与持续，选择切题类神、双方关系或整体发展为切口；说明它回答哪个子问。整体观察是线索，不凭课名先冻结成败；总体趋势问题可重整体结构，但不能用无条件“大势”掩去具体目标、专项反证或已定U口径。北海部分氛围用法边界未明，不作为自动翻判规则。
3. **取类并全面察类**：固定主类职责与坐标，核天时五气、地利十二气、直接阴神及神将、空墓、生扶泄耗、刑冲合害与制救。神煞既可取类也可说明状态，按切题环节进入，不再单独统计吉凶。类神空弱不自动改换；专项明确允许依空、不现等递补时按完整条件执行。纠正取用需指出原问误解、职责错配、漏读专法、可靠坐标或新事实等依据，不能只因另一候选更旺、更合意而改选。
4. **核有效作用与工具覆盖**：自身有力、对外能作用、对本问有益、实际兑现分开判断。先明确双方及通路，再用strength查单宫或补算；涉及数值增减必须用工具，不自行加减。需要查漏时加review:true，核状态依据、已选对象间关系事实、季土双表差异；未提交关系不自动生效，未声明对象不宣称已覆盖，未数字化条件仍按原法判断。数值不能替模型取用或判成败。
5. **收束与反证**：沿同一目标比较支持、关键阻碍和最强反证，辨其改变结果还是过程、程度或时间。课体与毕法还原为实际关系，同一事实换名不增加证据；上位结构与子格不重复计证。原问需要才展开应期/数量。沿现有audit和五项review核取用职责、首取/递补依据、计算真实范围及反证，不新增审计长表或额外裁决轮次。

核心bifa_conditions仅交“条目、成格”客观条件；完整导出与绑定参考保留“意象”，用BF-法号按需查。成立不等于切题；不要求逐条解释。毕法中的取类、空亡、阶段等分析方法按既有主线履行，不能因格名辅助而忽略底层实际作用。详源与适用边界按需查analysis-workflow、classification-priority和本问domain。

'''
p=T/'references/judgment-core.md'; text=p.read_text(encoding='utf-8')
text=text.replace('沿用“条目、成格、意象”三字段','完整导出保留“条目、成格、意象”；49版裁决核心仅列条目与成格，意象按需查')
head,rest=text.split('\n',1);p.write_text(head+'\n\n'+flow+rest.lstrip('\n'),encoding='utf-8')

priority='''# 分类取用：职责、首取与条件递补

身份：本轮依据已回源连续原文整理的执行补充，不声明各书无分歧或预测已验证。先固定目标；同职责依适用专法选择，不同职责各答其环节。不因空弱任意换类，也不禁止原文明示的条件递补。没有已核映射时标功能推定及范围。

## 婚姻爱情
传统男女婚配成否以干男支女及双方上神关系为重要主线；龙后侧重各自处境，不能替代婚配成否。媒合、财礼、配偶状态和偕老分职责。其他关系按已核适用边界定位，不套未核性别映射。来源：北海《理法简易》3981—4011及CF-E08对应连续范围及本轮CF-E07—E10。

## 学业考试
考生、成绩、评分、学校、证书、通知分开。日常成绩朱雀为主类，父母依《金针》该分支兼看；不扩成所有考试的唯一类。升学依《金针》河魁为第一类象，禄/长生承担学校目标；三者不自由互换，目标学校接纳关系仍核。研究生考试兼保留《理法》幕贵、魁星的考核分支，不当作河魁已被废止。专业过关重幕贵，资格证书重河魁/戌印、太常为绶；公务员朱雀有公吏职责，不等于通知职责。条件交叉不明时定点查原段，不能临时择最吉者。来源：《金针》2352—2371、《毕法全解》455—469、《理法》1409—1437；CF-E11—E13。

## 职位晋升与任所
所求明确职位或在任处境，以有据的职位类为第一；缺少现代职位映射时说明功能推定，不把古代政治职位表直接映射公司职级。德禄、贵人、催官、印绶等按作用兼看。任所方向子问沿《毕法》有禄看禄、无禄看父母、俱不入课传看日支的条件路径；此序不推广全部事业问。评职称、晋岗、加薪及实际到账分开。来源：《金针》1927—1945、《毕法全解》608—620及CF-E14—E17。

## 工作、经营与求财
一般应聘以禄为第一类，其他工作类按职责参看；指定单位录用还核干人支单位与该职位接纳条件，不由一般有工作直接推特定单位录用。禄之薪水、父母之来源、长生之生计/经营不随意互换。经营能维持与利润实得分别核；实际款项以财爻为主线，财源专类、与者、取者、财阴及通达兼看。来源：CF-E02—E06、E11、E16—E18及本问现行domain。

## 失物、走失与行人
物品、宠物先定本物专类；原因未明不先认盗窃。走失人问当前处境，行年、本命、玄武俱入课传时先行年，不把玄武永久列首。一般行人在外或来归依《金针》年命第一、马第二、六亲参看；取第一时不把第二第三再当同一行人，无第一才按本条递补。年命未知不同于已知年命不现；未知时按有据替代路径，不能补造。找贼、捕获与追回物品另分职责。来源：《理法》1155—1173、《金针》相关行人章、《毕法全解》4800—4814；CF-E01、E19—E23。

## 官讼是非
普通争执先读interpersonal；已涉诉讼读litigation。依《金针》诉讼本体勾陈为第一；勾不现朱现则朱主，两者俱现仍勾主，朱雀的文书职责保留。民事原被告与公诉被告的干支定位分开，不以谁提问固定角色。胜诉、判款、执行到账分答；财、文书、田产标的兼其专类，律师、证据与条文分别核制救效力。来源：《金针》官讼章CF-E24—E26、《毕法全解》1317—1327、3388—3399。原章强断、刑罚与“德不救”等不一并激活，继续采用U06与当前结构边界。

## 其他常见分类
疾病区分患者、病象与救治；白虎/鬼的递补按具体原法，不固定只取一者。胎产分是否怀孕、胎儿、分娩与母体；家宅分人宅、买卖、文书；出行分能动、成行、到达、办成；天气、农事、时运与长期占按各domain的对象和阶段执行。通用排序不覆盖这些专项。现代细分缺口保留，不凭总表臆造专法。

本轮CF编号是classification-evidence中的证据编号，与裁决固定E01—E22不同。原文与归纳分开；需要决定性采用且条件不足时按证据路径续读原章。
'''
(T/'references/classification-priority.md').write_text(priority,encoding='utf-8')

source=load(R/'output/分类占取用全面核查-20261112/原文证据.json')
for row in source['evidence']:
 f=R/row['path']; assert sha(f)==row['source_sha256']
 assert '\n'.join(f.read_text(encoding=row['source_encoding']).splitlines()[row['line_start']-1:row['line_end']])==row['quote']
 row['id']='CF-'+row['id']
(T/'references/classification-evidence.json').write_bytes(enc(source))
analysis=(R/'output/分类占取用全面核查-20261112/北海综合断课流程-原文核查.md').read_text(encoding='utf-8')
analysis=analysis.replace('现行活动专业规则未修改。','本页原文核查作为49版方法来源；已采用执行补充以judgment-core为准。').replace('当前仅提交研究结论，未修改活动方法。','本轮已将有界执行补充接入49版；原书强断及未定氛围边界不自动激活。')
analysis=analysis.replace('`北海综合断课流程-原文证据.json`','analysis-workflow-evidence')
(T/'references/analysis-workflow.md').write_text(analysis,encoding='utf-8')
shutil.copyfile(R/'output/分类占取用全面核查-20261112/北海综合断课流程-原文证据.json',T/'references/analysis-workflow-evidence.json')

domain_notes={
 'relationship':'婚配成否先核本题双方关系；个人发展、媒合、财礼与偕老分职责。传统干男支女不因提问者性别倒置；龙后状态不直接替代婚配。',
 'exam':'日常成绩以朱雀并依《金针》兼父母；升学以河魁为第一类象，禄/长生为学校目标，另核指定学校接纳关系。研究生的幕贵/魁星考核职责保留，证书、学校、评分和通知不自由互换。专业过关重幕贵，资格重河魁/戌印，太常之绶不等于证已到手。交叉条件不足查classification-priority及原段，不挑最旺者。',
 'promotion-salary':'明确职位或在任处境首取有据职位类；现代映射未核时明示推定。催官、德禄、贵人与动象按职责兼看，不能仅见动便断升。任所方向才用禄→父母→日支的原法条件递补，不泛化所有工作问。职称、晋岗、加薪和到账分别答。',
 'recruitment':'一般应聘以禄为第一类；父母之来源、长生之生计和具体职员类分职责，不在几者中择最吉者。问指定单位还核人/单位关系及该岗位接纳条件，一般有工作不保证目标单位录用。',
 'finance':'实际钱款以财爻为主线，经营/生计以其专类；与者能给、取者能取、财阴、款项归我通路分别核。通类吉不能替代文书、财源或具体交易条件，忙碌、承诺及批准不等于利润或到账。',
 'lost-person-object':'普通遗失及宠物先寻本物专类，不先套盗贼；人员走失年命、玄武俱现时按《理法》先行年。一般行人在外或来归依《金针》年命第一、马第二、六亲参看，无第一才依本条递补，不将第二第三重作同一人。年命未知与已知不现分开；方位、安危、捕获和物品追回分职责。'
}
for domain,note in domain_notes.items():
 p=T/f'domains/{domain}.md';text=p.read_text(encoding='utf-8');head,rest=text.split('\n',1)
 p.write_text(head+'\n\n## 49版首取与职责\n\n'+note+' 综合主线依judgment-core；条件和连续来源按需查classification-priority / classification-evidence，本节补充优先于旧摘要的宽泛候选并列，不替代未重审专项条件。\n\n'+rest.lstrip('\n'),encoding='utf-8')

litigation='''# 官讼是非：诉讼职责与条件递补

已知进入诉讼、司法程序或明确问能否引发诉讼时使用；普通口角、人际不睦先用interpersonal，不能因见勾鬼便认定已发生诉讼。

1. 原问确认民事、刑事公诉还是其他程序，以及原告、被告、实际被公诉人和阶段。民事沿《金针》干原告支被告；国家公诉沿其干为被公诉人的分支。行政、报警、调查等不能无据等同已经公诉；现代未核程序保留映射缺口，不能把提问者固定作干。
2. 诉讼本体沿《金针》勾陈第一；勾不现而朱现以朱为主，两者俱现仍勾主。朱雀文书、官鬼的官方/压力职责另核；不能将勾朱鬼无条件并列任选，也不因主取勾就删除其他相关作用。
3. 胜负、处罚程度、和解、文书形成及执行兑现分问。经济讼兼财、文书讼兼朱、田产讼兼对应田产类；胜诉不保证钱物到手。律师子孙与证据/理由/文卷父母按《金针》来源职责核制鬼或承接转生，不以吉名保证救成。
4. 看主类与双方上神的天时、临地、阴神、空墓、实际制救和最强反证。德等救应仍依U06核对象、通路及解除范围；不激活原章所有课名强断、古代刑罚对应或无条件“德不救”。刑罚、疾病和死亡不能由格名直接给出事实结论。

本模块补齐已核职责和首取，不宣称覆盖现代全部立案、上诉、行政执法、量刑与强制执行专法。来源见classification-evidence的CF-E24—E26、E28—E31；方法条件不足时回连续原段。取数、应期沿已有模块，旺衰工具只计算已选关系，不自动判输赢。
'''
(T/'domains/litigation.md').write_text(litigation,encoding='utf-8')

p=T/'references/keti-quanbiao.md';text=p.read_text(encoding='utf-8')
text=text.replace('> 本表支撑 `daliuren` 主 skill **步骤 7 课体细读第一层（九宗门大势）**，并补全特殊课体定义。','> 本表用于按需核课体构成及来源取义，不增加裁决轮次。先依本问定侧重；起传方法、组合结构、子格与本问效力分别看。')
text=text.replace('> 课体细读三层：**第一层九宗门大势**（本表）→ 第二层毕法课传结构定关键（[bifa.md](<bifa.md>)）→ 第三层位次定力度。','> 课体与毕法共享底层关系；名目成立不等于切题、有效或决定结果。九宗门不天然压过其他结构，包含与重叠不重复计证。')
text=text.replace('- 步骤 7 第一层先按下表九宗门定整课"基调"（吉 / 凶 / 滞 / 反复）；命中特殊课体时按第二部分核对定义与要点。','- 先观察实际气势与动静进退，按原问决定侧重；不能仅凭九宗门或课名冻结整课吉凶。表中吉凶词是来源倾向，须核组成类象、宜忌和有效作用。')
text=text.replace('- 三合局、稼穑、游子、铸印、轩盖等格局类课体在**来意占**（步骤 2）中可直接锁定占类（如铸印→官事、轩盖→出行/官迁、稼穑→田土）。','- 三合局、稼穑、游子、铸印、轩盖等可提供来意候选；不能单凭课名锁定现实占类或覆盖用户明示问题。')
text=text.replace('- 本表只定大势与课体名，不替代第二层毕法关键结构（[bifa.md](<bifa.md>)）与第三层位次力度。','- 课体定义核实后回同一主线察类；毕法格名沿45版作辅助，真实底层作用仍依理气参与结果，不另加吉凶权重。')
p.write_text(text,encoding='utf-8')
for rel in ['methods/adjudication.md','methods/structure.md','references/bifa.md','references/bifa-basic.md']:
 p=T/rel;text=p.read_text(encoding='utf-8').replace('沿用“条目、成格、意象”三字段','完整导出保留“条目、成格、意象”；49版裁决核心仅列条目与成格，意象按需查')
 p.write_text(text,encoding='utf-8')

tools_note='''
## 49版旺衰工具的按需核查

strength原参数增加可选review:true；默认不输出扩展核查，不改变已有系数、单宫值、补算值、空亡口径或合局暂缓决定。仍先依问取用并说明依据，再提交actors；需要数值增减时给完整links快照。

review返回state_basis（各已选对象五气、十二气参照、旬空/坐空、通达及直接关系）、relation_candidates（仅已声明对象两两关系事实，含刑冲合害；未提交关系不自动算作用）、season_comparison（同一actors/links分别核季土双表，不选择高分表、不平均）。这些是定点查漏工具，不是全盘穷举义务；不应每次自动附review:true。

coverage始终说明提交和实际计算的关系数、未更新其他宫位、未验证专业取用/通路适用性、不能判成败。state_basis.pending_action_conditions是内部作用适配提示；神煞未提供、专项未适配等不得理解为没有作用，也不要求把所有提示变成新待办。

例：在原strength对象中加"review":true即可；其他mode/season_profile/season_basis/actors/links不变。可用single_palace查关键节点的基础与事实，再按原法确认必要关系补算；已有材料足够时直接selected_relations，无须固定多跑一轮。evaluation中的strength也支持review，保持原旬空/研究新旬政策各自身份。

未补入：全盘自动取用、自动通路裁定、成败概率、所有刑冲神煞数值化、三合半合三会数值、自动合化、已校准系数或所有未来兑现机制。定性未量化不等于不参与原法判断。
'''
p=T/'references/deterministic-tools.md';p.write_text(p.read_text(encoding='utf-8')+tools_note,encoding='utf-8')
p=T/'references/adjudicator-prompt.md';text=p.read_text(encoding='utf-8');p.write_text('49版：明占类→定侧重→察实际作用，依共用核心与本问专项首取/递补。毕法核心仅列成格条件，意象按BF法号按需查；不逐条解释、不另开课体流程。旺衰review:true仅需查漏时调用，未声明关系不自动补入。沿原自由报告及一次补核协议。\n\n'+text,encoding='utf-8')
p=T/'methods/adjudication.md';p.write_text(p.read_text(encoding='utf-8')+'\n49版沿现有role_stage_consistency核本问主类职责、实际竞争候选与首取/递补依据；calculation_scope核已选对象和关系覆盖，不将review事实候选当已采用作用。无须新增固定附件字段。\n',encoding='utf-8')

m=load(T/'manifest.json')
for key,file,title in [('analysis-workflow','references/analysis-workflow.md','北海综合流程与原文边界'),('analysis-workflow-evidence','references/analysis-workflow-evidence.json','综合流程连续原文'),('classification-priority','references/classification-priority.md','分类取用职责与条件递补'),('classification-evidence','references/classification-evidence.json','CF分类连续书证'),('litigation','domains/litigation.md','官讼是非取用')]:
 m['modules'][key]={'file':file,'required':False,'requires':[],'title':title,'trigger':'本问或具体条件需要时读取'}
 m['files'][file]=sha(T/file)
if 'litigation' not in m['domains']:m['domains'].append('litigation')
for item in m['modules'].values():item.setdefault('requires',[])
(T/'manifest.json').write_bytes(enc(m))
route=load(T/'reading-route.json');route['domains'].append('litigation');route['labels']['litigation']='官讼是非'
(T/'reading-route.json').write_bytes(enc(route))
(O/'flow-section.md').write_text(flow,encoding='utf-8');(O/'strength-note.md').write_text(tools_note,encoding='utf-8')
assert all(sha(R/f)==h for f,h in before['frozen'].items())
print(json.dumps({'candidate':NEW,'domains':len(m['domains']),'parent_unchanged':True},ensure_ascii=False))
