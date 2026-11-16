"""One-shot local consolidation. Parent runtime and original source bytes stay frozen."""
from pathlib import Path
import hashlib, json, shutil, os, re

R = Path(__file__).resolve().parents[2]
O = Path(__file__).resolve().parent
load = lambda p: json.loads(p.read_text(encoding='utf-8-sig'))
enc = lambda v: (json.dumps(v, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
b = load(O/'before.json')
p = load(R/'.opencode/liuren-active.json')
OLD = b['release']
NEW = '20261112-consistency-52'
T = R/'runtime/liuren'/NEW
assert p['release'] == OLD and not T.exists(), 'Refuse rerun or changed pointer'
assert all(sha(R/f) == h for f, h in b['frozen'].items()), 'Parent changed'
shutil.copytree(R/b['runtime'], T)

def put(f, s):
    dest = R/f
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(s.rstrip()+'\n', encoding='utf-8')

def runtime(f, s):
    put((T.relative_to(R)/f).as_posix(), s)

oldcore = (T/'references/judgment-core.md').read_text('utf-8')
# Preserve the adopted rules verbatim; the surrounding append-only release
# commentary is replaced by a single present-tense execution specification.
u = oldcore[oldcore.index('## 已确认判断口径 U01'):oldcore.index('## 单宫旺衰与取用后补算')].strip()
core = '''# 本机占事共用判断规范

本页是当前执行主线及采用口径，主智能体与裁决者共同遵守。原文、讲解、项目归纳、用户选择和现实反馈分别标明；不声称诸书一致或预测效果已经验证。当前入口只读本页与本问专项，详细方法/原书按真实缺口查询，不把来源目录当必读清单。旧版说明只供追溯，不能反向覆盖本任务绑定规则。

## 一条分析主线

1. **原问与目标**：明确实际当事人、对象、阶段、期限、成功标准和条件子问；代问者不自动成为当事人。现实事实、用户推测、模型推断与未知分开。按本问domain取法，给占时不等于问应期，迟速比较不自动触发全部时间/取数方法。
2. **明占类、定侧重、取类**：观察真实课传的动静、进退、明暗、缓急、持续作为切口，不能凭课名先冻结成败。通类看大方向，专类按具体职责；同职责有首取与有条件递补时按专项执行，无排序不虚构总序。类神空弱不能任意换类；明确允许空或不现递补的专项依完整条件执行。纠正须说明原问误解、职责错配、漏法、可靠坐标或新事实，不能按候选更旺/更合意选。细节查classification-priority。
3. **可靠位置与全面察类**：复用可信程序全盘、固定神煞、历法；分清日干/寄宫、干上/干阴、天盘支/坐处、同名地盘上神、天将/乘支和直接阴神。天空不是旬空。关键主类及最强反证察月令五气、地利十二气、空墓、阴神、神将内外战、生扶泄耗、刑冲合害与制救；不按人数分四课。
4. **有效作用**：分别核自身有力、对外能作用、对本问有益、最终兑现。说明施受对象、双方状态、通路、时序及影响环节；与者能给、取者能取，不把相生关系当已兑现。直接阴神先一层，新增层只解决具体疑点，重复即止。类神不入课传通常不直接断败，仍按专项到全盘及已核年命寻类。财临门等原法入课传条件保留，不无说明跨类迁移。
5. **综合与反证**：支持和反证用同一标准；判断制救解除哪个障碍、到何阶段，局部缓解不扩成成功，关键阻碍有效解除可改判。不能把所有不利改成波折，也不因谨慎自动降档；成行/到达/办成、录用/报到、承诺/到账及期限内/最终完成分开。共同趋势没有区别依据时不能区分相邻选项。
6. **按问细断并交付**：有时间、数量、年命任务才补相应方法；数字意图包括约数、名次、等第及进退差值。裁决者从完整盘独立查漏并给逐问主结论，主智能体只核事实、引用、覆盖与一致性。现有audit、五项review和原会话一次recheck完成闭环，不另开课体/毕法裁决轮次。

## 气势、神将、课体与毕法的职责

发用联月令、坐处、乘将及切题神煞察发动、快慢、规模、虚实和持续，单宫指数不是整课气势。虎急蛇缠是表现趋势，速度不是吉凶。发用作用于四课须核真实通路、施受和时序，采用数值补算时交工具。

神将吉凶名目只作倾向，神克将减权减力而非一概归零。类聚按共同实际作用，不按同名多票，不把书中“加倍”变成无据数值倍率。阳显阴藏可指表面/内部条件，人的阴神不一律作心理或秘密。动可以是调动、转岗、晋升等状态变化，核关墓空、合绊、恋生及有效冲解；启动不等于到达或受益。

课体/大象帮助定侧重并描述结构；毕法在本地采用为描述性辅助，格名和意象不单独决定结果或加权。还原底层实际作用，涉及本问的取类、空亡、阶段等方法照常履行；无关条目可不用，不逐条解释、不数重叠格名多票。核心bifa_conditions只列客观条目与成格，程序确认结构不等于取义完成；完整导出的意象及百法录按需用BF-01至BF-100、BF-B35/BF-D35查询，不反向补成未成立子格。第22成格依《大全》。整体耗损/动象不直接实体化成分手、失窃、成功或具体日期。详细边界查bifa-basic、analysis-workflow。

神煞只用程序resolved项并核对象、落点、状态和制救；未采用或缺参者不作依据。归属在天盘支，地盘为坐处。同位多名不重复计证。季关神S33春丑夏辰秋未冬戌；阻隔、关墓、冲解及仓库吉用按原段，不能见关就断不动；S23寡宿同表但义项不同。具体查shensha-use/meanings。

## 旺衰计算的边界

默认strength_index是单宫直接关系研究指数：含月令、自身十二气、旬空/坐空、天地、本身直接阴神及同宫神将生克。天将对地盘只列十二气，不新增将地生克边；不是全局力量、吉凶分、成败概率或最终作用。0与null不同，5只是基准，2.5不是失用开关，弱仍可作用；完整作用A为null是适配不足，不是作用不存在。

先由原法明确取用、对象和有效通路；需要表达跨宫数值增减时调用strength补算，不手加分、不自动全盘联算、不在上次结果层叠。已含本宫关系自动跳过；未提交关系不扩散。取用改正后以完整新清单重算。刑冲、神煞等未量化条件仍定性分析，三合/半合/三会数值暂缓。review:true仅在需查漏时查状态、已选对象的关系事实及季土差异，候选关系不自动成为有效作用。

季土双表须说明所用依据，同表前后比较，不按结果择表、平均或计两票。时间推进依U10；evaluation默认保留原空亡、更新节月五气；evaluation-xun-research为新旬替换研究情景，不是已定出旬/冲实算法。日历值冲合事实不等于事件已填实，不能自动选最高分日期作应期。参数与分档细节查deterministic-tools。

## 数量与旺衰的结合

先按本次数量含义、对象和阶段重新取类：通过、分数、排名、通知、资格不同；天将类定位所乘T:支，不沿用前问通过类。先methods查具名法，原法明确适用则走source；已因旺衰选加/乘/半，视为已使用气态，不再套实验倍率。原法不足时说明转用理由，以未含气态及空减的raw expression本数走experimental，不两路算后择有利。

strength同时返回同对象、同关系、同季表从头重算的without_void；实验倍率只读该视图，不从含空指数倒除。实验分段：E≤2.5乘0.5；2.5至4连续至1；4至6本数；6至7.5连续至1.2；7.5以上维持1.2。这是未校准项目参数，非北海原文、非成败阈值。状态计空不等于数量已减，但已因同一空亡减量不能再扣；原法无明文不强制所有source再半，须明示原法/项目研究/模型估计及阶段依据。仅数量主类本身旬空可用该项研究半数，身空、坐空、载体空不自动代替；不得含空指数减后再空半。

量级、单位、上下限独立说明，不把强弱指数换满分百分比、排名或彩票奖金档次；财源规模不是个人所得。无上限不等于不能估计，但缺少十百千量级依据时说明具体缺步，不能靠旺衰任意移小数点。超出现实边界须复核方法/量级，不截满分。序数、日期、编号不套实验倍率和空半。

新数值问最终quantity_adjustment消费本任务真实基数/strength回执，保留本数也须兑现；复制返回review补question_id、final_receipt_sha256、report_quote进入audit.quantity_reviews。查quantity、quantity-strength、quantity-correction及动态consistency_guide；序数按需查quantity-rank。具名目录不是数法全集，expression可实现有据原法，不能用未调整base-only冒充最终数。先实际尝试并给最有依据的具体估计值和单位，可附范围；仍无可辩护数值才说明已试步骤及缺口，不用定性词或宽区间代答，不随机凑数。

## 作答与核对

逐问先给主结论，再给决定性依据和最强反证的取舍。是非给是/否或倾向；所在地给有依据的主选地区及可支持精度；原因给主因；条件子问尊重原题依赖。不同子问分别完成，不以缺少用户未问的高精度拒答，不在后文无据撤回主判。推测身份标一次，不伪造概率、精确住址或第三方敏感隐私；细则见direct-answer。

正文自由表达，已有audit是来源/作用/范围附件，不是固定判词模板。五项review为input_fidelity、role_stage_consistency、calculation_scope、counterevidence、answer_constraints；核首取/递补依据、真实计算范围及逐问覆盖，局部不冒充综合。具体错误须报告原句及绑定证据，原会话recheck一次；不另派、不由主智能体折中改判，排版不重裁，余缺显式交付。程序核事实/算术/回执，不选类神、不裁成败；“不设阈值”指不以分数裁吉凶，不否定上述实验数量分段。

普通占断不读案例/经验库、旧缓存或已知反馈；原书及书内例证保留。正常年命/行年可用且资料需已核，不作出生推命。命偏固有、年偏当前但当前可超一年，不建立年永远胜命。V41-01出旬书证冲突按用户决定保留U08/U10待其后续研判，不反复询问；特殊空义关键而摘要不足查void-class-applications。详细采用条件不清、摘要不足或反证冲突时定点读连续原段，已定规则不从旧摘录反向执行。
'''
runtime('references/judgment-core.md', core+'\n\n'+u)

adjudication = '''# 核心交接与独立裁决

准备必读judgment-core、adjudication和本问domain，report交付前读。专业取用、理气及数量采用口径以同任务核心为准；详细方法和原书只按决定性条件缺口、反证冲突或摘要不足查。

主智能体保存原问及input_review来源身份，候选取用说明职责与依据，不先完成裁决。facts只补现实事实及来源身份，observations只留程序盘未表达而切题的观察，focus_issues无真实问题则[]。已定U规则和历史C编号不重新列成待确认争点。原书用精确handoff、method_modules只列必要备查，不复述整章或把来源清单变必读。

packet生成完整可信盘、紧凑核心及hash绑定全档。OpenCode原样task_prompt派一次task；Codex按桥接spawn显式Sol/high/fork_turns=none并bind。裁决者读完整核心，可纠正候选、从全盘查漏，按material_id/module查同任务绑定参考；新材料须保留来源与适用条件。始终沿原文件hash或run，不自行改路径换版。

裁决者给完整自由正文与现有audit，登记关键作用、最强反证及实际计算；数字任务按quantity-correction取得最终回执及quantity_reviews。程序检查传输/算术/声明一致性，不确认类神选对或预测准确。缺必要条件可具体说明needs_input/unresolved，不造数过检。

主智能体领取并完整读报告，读report后完成input_fidelity、role_stage_consistency、calculation_scope、counterevidence、answer_constraints五项review。有具体报告原句、绑定规则/原问/真实回执证据时，使用result(action=recheck)或Codex action=recheck，在同一裁决者、同一任务/run补核一次并保留前后报告。当前新任务不用retry_context另建裁决，不能因不同意结论重派；主智能体不重新折中、不替填数值。无具体证据或补核后仍未解则review如实标缺口并deliver。

格式/保存错误只修字段或保存同一正文，不从头分析。OpenCode完整读核后finish=length且无公开正文，按工具next_call在原会话recover一次；它是传输续写，不是第二轮裁决。仍无正文明确未完成，不以内部推理拼接。历史任务沿其原绑定协议领取；不追改旧packet和原盘。

主智能体核本问主类职责、真正竞争候选及首取/递补条件，计算核所选对象/关系的真实覆盖。程序查漏候选不等于已采用有效作用。报告结论、精度、条件和决定性理由忠实交付，只调展示格式；具体schema以工具帮助及绑定consistency_guide为准。
'''
runtime('methods/adjudication.md', adjudication)

oldreport = (T/'methods/report.md').read_text('utf-8')
reportbody = oldreport[oldreport.index('正文自然连贯'):oldreport.index('## 第39版执行核对')].strip()
runtime('methods/report.md', '''# 完整技术报告与交付核对

逐问先给直接结论，再说明决定性依据、最强反证及取舍；题型与精度边界依judgment-core，完整细则按需查direct-answer。数字须真实尝试取数并给有依据的具体估计值与单位；无法完成时说明已做步骤和具体缺口，不用定性或宽区间替代。

主智能体交付前只核事实、引用、问项覆盖和内部/采用口径一致性，保留裁决者的取用、关键关系、反证处理、结论、精度与条件。按adjudication完成现有五项review；具体错误以原句和绑定证据在原会话补核一次，不另派、不自行改判。needs_input或未完成如实说明，不代替裁决。

'''+reportbody+'''

数值记录须区分本数、含空状态指数、without_void、source/experimental路径、真实修正、量级、单位和最终回执。状态计空不冒充数量已减，同因素不重复扣；数量最终review与实际回执一致，未解决项保留。局部计算不得称全局核算，工具验证不证明术理正确或准确率提升。
''')

prompt = '''# 大六壬独立裁决者

只依据本任务原问、完整可信盘、绑定judgment-core与本问domain，独立裁关键作用和逐问结果。主智能体提供候选，不能限制你从完整盘纠正取用和查漏。严格采用核心U01—U11；历史C01—C11不是待确认清单，真实同条件互斥按U11处理，V41-01按用户决定保留现行。

先liuren_adjudication_read(page=1,page_count=4)，依next_call读完全部核心；Codex按role映射每次一页。显示截断须补齐。参考不是必读清单；决定性条件不清、摘要不足或新反证影响结论时，以相同file_path/sha256或run，用module/material_id查绑定连续方法/原文。BF-35查百法录，BF-B35/BF-D35查原章；E01—E22按需，不读案例/经验库、其他任务或已知答案。

核心规定取用职责与首取/条件递补、五气十二气、空亡、有效作用、制救、最强反证及数量联动。按真实通路使用compute，不手算数值或日期，不自动全盘五行联算。仅按问补时间/数量/年命。数值任务须最终quantity_adjustment并复制工具review进quantity_reviews；具体字段依绑定consistency_guide与工具schema，不把基础数当最终数。

逐问给直接答案、决定性依据及最强反证取舍；完整自由Markdown正文或JSON对象与audit一起submit。可先audit取receipts/check；缺项具体说明，不编数通过。成功末消息只回回执。格式错只修字段或同一正文，不重判。收到LIUREN_CONSISTENCY_RECHECK_V1时只补具体证据缺口并再次submit，可有依据地保留原判；同一任务一次补核，不另派、不从头重裁。未知阶段不能写作用户事实。
'''
oldprompt = (T/'references/adjudicator-prompt.md').read_text('utf-8')
guide = oldprompt[oldprompt.index('# 固定书据：'):oldprompt.index('## 单宫旺衰与取用后补算')].strip()
runtime('references/adjudicator-evidence-guide.md', guide)
runtime('references/adjudicator-prompt.md', prompt)

# Source interpretation remains available. Remove only superseded operational
# advice and exact duplicated policy blocks, not quotations or source bytes.
f = T/'domains/recruitment.md'
s = f.read_text('utf-8').replace('与《理法简易》有生亦空冲突且影响实现者明列分支，不作万能补救。', '来源措辞差别留在C04，执行依U08/U10综合判断，不因旧摘录相反重开已定口径；决定性真实缺口具体披露，不作万能补救。')
runtime('domains/recruitment.md', s)
f = T/'domains/period-outlook.md'
s = f.read_text('utf-8').replace('- ce11（凶课体）：只按类神断而漏课体凶格（天网难逃、解离婚姻先好后坏、芜淫私情、干支乘墓为"止"）；吉课体（轩盖课）遇空亡变质转凶（乘轩落马→丢官罢职）。且同一课体吉凶随占类而变（解离问婚姻凶、问牢狱反可逃脱）。', '- ce11（旧课体评议）：原整理列天网、解离、芜淫、乘墓及轩盖空陷等强断作为查漏提示；现行执行须还原所涉对象、气态、制救与阶段。同课随占类异义，不能由格名直接断私情、罢职或翻转成败，也不忽略底层切题关系。')
runtime('domains/period-outlook.md', s)
f = T/'methods/quantity.md';s = f.read_text('utf-8')
a = s.index('## 51版：');z = s.index('## 数字的含义先于算式')
s = s[:a]+'''当前数量联动规则见judgment-core与quantity-correction：source已使用气态不再叠实验倍率；experimental用真实without_void与固定研究分段；空减、量级、单位分别核。最终以同任务quantity_adjustment兑现及quantity_reviews记录，不以base-only代替。以下六环是方法展开，不另开裁决流程。

'''+s[z:]
s = s.replace('数量判断复用第3—8环节结论，在第9环节与应期分别完成。', '数量判断复用已核取用和有效作用，在独立裁决前按问完成，与应期分别论证。')
runtime('methods/quantity.md', s)
# The basic registry has 134 structural branches plus 8 method checks; retain
# those precise counts instead of the early 42-version 32-pattern snapshot.
for f in ['methods/structure.md','references/bifa.md','references/bifa-basic.md']:
    s = (T/f).read_text('utf-8')
    a = s.find('## 毕法赋：描述性辅助与百法录')
    if a >= 0:
        tail = s.find('\n## ', a+4)
        if tail < 0:
            # bifa.md contains more original material following the fixed block.
            marker = '不新增长表、硬性采用数量或重派裁决。'
            tail = s.index(marker, a)+len(marker)
        s = s[:a]+'毕法采用边界统一见judgment-core；成格只确认结构，先核切题性并还原实际作用，格名不独立裁成败。百法录及原章按BF编号按需查，不逐条解释、不重复计证。\n\n'+s[tail:].lstrip()
    runtime(f, s)

route = load(T/'reading-route.json')
route['release'] = NEW
for item in route['conditional'].values():
    stage = next(s for s in route['stages'] if s['id'] == item['stage'])
    if item.get('beforeRequired') not in stage['required']:
        item.pop('beforeRequired', None)
runtime('reading-route.json', json.dumps(route, ensure_ascii=False, indent=2))

# Keep externally supplied personal/server sections byte-for-byte.
prefix = (R/'AGENTS.md').read_bytes().split(b'--- project-doc ---')[0]
project = '''--- project-doc ---

# 本地大六壬工作区接手指引

先读README与目录总索引。当前资料版本只认`.opencode/liuren-active.json`；现行操作见[本机完整研判流程](docs/本机六壬完整研判流程.md)，不从旧版发布说明叠加要求。当前规则已合并，历史逐版入口原文保存在`output/liuren-global-consistency-52/before/`，冻结runtime不就地改写。

用户说“使用大六壬进行测算”时启用daliuren-codex；未发现则读取`integrations/codex/daliuren-codex/SKILL.md`和[Codex流程](docs/Codex大六壬工作流.md)。主智能体准备中性材料，原生子智能体显式gpt-6.1-sol/high/fork_turns=none独立裁决；主只核事实、引用、覆盖和一致性并完整交付。OpenCode用当前配置的DeepSeek/high及393216额度；不把此额度移植Codex。知识维护、课程写作和工作流开发不自动启动占断裁决。

普通研判：原问/当事人/阶段/成功标准→可信全盘→专项职责和首取/条件递补→察类及有效作用/制救→最强反证→按问应期/数量→独立裁决→五项review→必要原会话recheck一次→完整交付。准备读judgment-core、adjudication与本问domain，report交付前读；其余方法/原书按真实缺口查询，不恢复八项通读。理气贯穿，程序只核事实和计算，不选类神、不裁成败；已确认U01—U11直接执行，历史C编号不是待确认清单，V41-01保留现行待用户后续研判。详规以任务绑定runtime正文为准，不在此复制专业长文。

普通占断不检索案例/经验库、旧缓存或反馈；原书及书内例证保留。同卦复用可靠盘和同版已读材料，补新争点；正常年命/行年、长期占事与应期保留，出生推命及出生运限退出。毕法/课体不另开裁决轮次，格名不数票。旺衰数字需工具，单宫不冒充综合；数量任务按quantity、quantity-strength、quantity-correction，最终回执与audit一致。实验参数非古籍原文，工程通过不证明预测准确。

保留现有活动目录tools/tests/runtime/.opencode/案例项目库/经验日志/书籍库/books/knowledge/排盘工具魔改/排盘存档。八字active已迁出；冻结包内历史副本原样保留。外部资料优先用项目内已登记副本，见目录维护说明与路径路由映射。移动资产先列清单、核活动引用和前后SHA256、禁止覆盖并留回滚；不得为清根盲移docs/output或历史证据。不提交密钥、env、客户档案、测试私有及恢复材料；Git根可能在上级，操作只限授权范围。

## 知识维护与课程

书籍提取、旧案例复审和经验归并先读`docs/六壬知识整理-20261102/README.md`及`数据约定.md`，用`tools/liuren_knowledge_workbench.py`核覆盖/待办/引用。原书、卦师断语、旧AI解释、现实反馈、本轮归纳分别保留；入选作答可按子判断保留方法价值，不因一处错整篇作废。卡片检索同时读条件、反证与审查范围；程序切段/hash不等于语义精读，新增归纳保留来源、版本、条件、反证、缺口。新研究放`knowledge/liuren-research/20261102/`，不覆盖原始字节；网站部署另办。

课程工作先读`课程写作/AGENTS.md`、当前台账和专业底稿，保留用户修订，未经接受不标定稿。跨会话记忆仅在用户明确要求时新增简短重要事项，不存秘密。

## 本机运行与产品维护

OpenCode启动检查`python -X utf8 tools/liuren-preflight.py`，新进程首次tool_help(workflow)确认execution_health.ready；Codex检查`node tools/liuren-codex.mjs status`。同一新任务仅派一个裁决者；具体原句和绑定证据才原会话recheck一次。长度停止且完整读取、无报告时按next_call原会话recover一次，不另派、不将内部推理拼正文。保存成功后read→review→deliver，余缺显式交付；主不得折中改判。历史任务沿原绑定协议领取，不追改旧文件。当前仅本机，OpenCode重启新会话加载，Codex新任务读取指针；网站/服务器未发布。

本机默认完整技术报告，沿`docs/本机OpenCode完整输出规则.md`，不套网站隐藏来源或字数限制。参数以工具schema/next_call为准，prepare/read/check为可选工程审计，不是默认必跑全链。

web/mobile/ui-rebuild保留现路径。产品开发先读`docs/跨会话继续开发指南.md`，修改web另遵`web/AGENTS.md`。动态发布、服务与支付须核实，不把设计当已完成；复用配置且不输出凭据。不得缩减专业skill绕过截断；支付以真实资金和服务端证明，测试隔离，管理员连通单不生成报告。通常网站改动只重启web，先核实际任务再动worker；部署及服务器操作依本次授权。
'''
(R/'AGENTS.md').write_bytes(prefix+project.encode('utf-8'))
assert hashlib.sha256(prefix).hexdigest() == b['agent_prefix_sha256']

flow = '''# 本机六壬完整研判流程

本页是现行操作入口，版本从`.opencode/liuren-active.json`读取。历史发布说明和冻结包用于追溯，不叠加执行；本次整理记录见[全局核查](../output/liuren-global-consistency-52/核查与验收说明.md)。专业细则以同任务绑定judgment-core及专项为准。

1. **检查与定题**：OpenCode启动跑`python -X utf8 tools/liuren-preflight.py`，首次`liuren_tool_help(topic=workflow,domains=[本问])`确认execution_health.ready；Codex先`node tools/liuren-codex.mjs status`。原问保留，明确当事人、子问、阶段、期限、成功条件及真实/推断/未知身份。
2. **读取与排盘**：准备读judgment-core、adjudication、本问domain；用程序取得完整可信盘及archive，同输入可靠盘复用。详细positioning/liqi/void/structure/shensha-use/movement及原书只按实际条件缺口或反证冲突查；年命、应期和数量按问触发。占类ID与数目以manifest为准。
3. **同一主线准备**：明占类、观察气势定侧重、按职责首取/有条件递补，沿主类真实坐标察气地空墓及有效作用/制救，保留最强反证。候选可纠正，不因空弱或算得高低换类；不预写完整裁决。facts不复述整盘，原书用精确handoff，focus_issues只留本问真缺口。
4. **按需计算**：工具只核盘/查表/计算；已选跨宫关系要表达数值增减时strength补算，不自动全盘联算，单宫不冒充综合。数量依quantity及quantity-strength/quantity-correction，分source与experimental、空减和量级，最终quantity_adjustment消费真实回执；序数不机械折半。应期用calendar/evaluation核候选，不按最高分自动择期。
5. **独立裁决**：packet生成完整盘核心及hash绑定参考；只派一次裁决，主候选不限制全盘查漏。OpenCode当前DeepSeek Flash/high，显式393216额度；Codex原生Sol/high/fork_turns=none，不套DeepSeek额度。子读全核心，参考按需，以自由完整正文+audit提交。
6. **核对交付**：领取并完整读报告，交付前读report。五项review核事实身份、职责阶段、计算范围、反证、逐问约束。有具体原句及绑定证据才原会话recheck一次，不新派、不由主折中；格式问题只修格式。按next_call deliver并完整交付，余缺保留。长度停止且无报告的传输recover依原会话工具条件一次，仍无正文明确未完成。

普通占断不检索案例/经验库或已知反馈；原书和书内例证保留。毕法、课体、神煞融入本问作用主线，不分系统轮流裁判或数票。U01—U11直接执行，V41-01保留现行；实验旺衰/取数参数未经预测校准。工程检查不证明模型遵守或预测准确。

同卦续问复用同版已核盘/资料，只补新争点；数值追问重新核所求职责。历史任务按原绑定领取，新资料不得反向改写旧报告。当前变更仅本机，OpenCode重启新会话、Codex新任务加载；网站未发布。
'''
put('docs/本机六壬完整研判流程.md', flow)
put('docs/本机六壬高效执行.md', '''# 本机六壬高效执行

现行完整步骤只在[本机完整研判流程](本机六壬完整研判流程.md)维护；本页仅列减少重复工作的约定。版本及工具能力以活动指针和实时tool_help为准，不加载历史逐版补丁。

- 同输入复用可信盘、同版已读方法和已核节点；固定起法直接用程序。主准备读核心/裁决/本问专项，report交付前读，其他参考只解决具体疑点。
- 中性交接保留原问、实际角色与阶段、候选依据、必要观察及真缺口，不复述全盘/整书、不先做完整裁决。程序核心带全盘，裁决者可纠正和查漏。
- 取用和有效通路先于数值。只补算有专业依据的关系，不全盘两两联算；review:true按需，事实候选不自动作用。原回执和计算范围可复用，不同阶段/对象不能冒用。
- 数量遵循quantity/quantity-strength/quantity-correction：同因素不重复用，量级与单位独立；有数字意图实际尝试并给有据估计，确实缺步才说明。未问数量/应期不自动扩任务。
- 按next_call完成packet→一次独立裁决→read→五项review→deliver。具体原句和绑定证据才原会话recheck一次；传输recover另有条件，不是重裁额度。缺口保留，不以新任务循环。

OpenCode当前DeepSeek/high及393216；Codex原生Sol/high不继承该额度。启动检查、技能与宿主映射见完整流程和[Codex流程](Codex大六壬工作流.md)。旧任务沿绑定资料领取；原书与冻结包原样保留。参数请查工具schema，不为少读而漏决定性条件。
''')

readme = (R/'README.md').read_text('utf-8')
# Retain the workspace map and optional audit commands; replace release appends.
readme = readme.split('\n本机OpenCode裁决者当前为')[0]
# Most release append lists start earlier; preserve only stable introductory use.
cut = readme.find('\n32版')
if cut >= 0: readme = readme[:cut]
readme = readme.replace(OLD, NEW)
put('README.md', readme+'''\n
## 当前规则与维护

现行操作统一见[完整研判流程](docs/本机六壬完整研判流程.md)。专业规范在活动runtime的judgment-core、各专项及按需参考中；不从本页或历史发布日志叠加版本规则。OpenCode裁决DeepSeek/high及393216；Codex原生Sol/high。新任务一名独立裁决者，原会话最多一次证据补核，五项review后完整交付。当前数量采用source/experimental分路及真实回执联动，参数未经预测校准。

本次[全局核查记录](output/liuren-global-consistency-52/核查与验收说明.md)保留问题清单、精简前原文、验证和回滚。普通研判不检索案例/经验库；知识维护另走专项。当前只改本机，新OpenCode进程/新Codex任务加载，网站未发布。
''')
index = (R/'目录总索引.md').read_text('utf-8').split('\n35版本机工具升级')[0].replace(OLD, NEW)
put('目录总索引.md', index+'''\n
现行判断流程见[本机完整研判流程](docs/本机六壬完整研判流程.md)；专业规则只按活动指针绑定，不叠加历史版说明。本次核查与历史入口快照见[全局核查记录](output/liuren-global-consistency-52/核查与验收说明.md)。案例/经验资料仅知识维护按需，普通占断不检索两库。
''')

entry = '''---
name: daliuren
description: 使用可信程序课盘完成大六壬占事研判，依活动规则准备中性材料、独立裁决并核对交付；知识维护和课程开发另走专项。
---

# 大六壬占事

当前版本只认`.opencode/liuren-active.json`。先tool_help(workflow)确认execution_health.ready；准备读judgment-core、adjudication及本问domain，report交付前读。详细通用方法、原书和应期/数量/年命按真实缺口或任务触发，不通读旧八项，不从历史版日志叠加规则。

主线：原问/实际当事人/阶段/成功条件→可信全盘→专项职责与首取/条件递补→气地空墓及有效作用/制救→最强反证→按问细断→独立裁决→五项review→完整交付。专业细则以任务绑定judgment-core的U01—U11及本问domain为准；类神空弱不任意改取，毕法/课体不另开裁决轮次，不凭名象数票。数值按quantity/quantity-strength/quantity-correction真实兑现，单宫分不冒充综合。

主准备中性候选，facts不复述全盘，observations只留必要观察，focus_issues只列本问真缺口。原书精确handoff备查。packet返回task_prompt原样派一次task；裁决者读完整核心，从全盘独立查漏，参考按material_id/module按需，不能把索引作必读清单。

领取完整正文后主只核事实/引用/覆盖/一致性并完成review；有具体原句及绑定证据才原会话recheck一次，不重派、不自行折中。传输续写按next_call的recover条件一次，仍无正文明确未完成。deliver后忠实交付结论、精度、条件与缺口。参数查tool_help和动态schema，工具契约liuren-tools-31不随发布号机械变更。

普通占断不查案例/经验库、旧缓存或已知反馈；原书/书内例证保留。年命行年正常采用，出生推命退出。同卦复用可靠盘及同版已读内容，补新争点。完整操作见docs/本机六壬完整研判流程.md；工程回执不证明理解或预测准确。
'''
put('.opencode/skills/liuren/daliuren/SKILL.md', entry)
runtime('entry.md', entry)

codex = '''---
name: daliuren-codex
description: 用户说“使用大六壬进行测算”时启用。在Codex中使用活动专业规则和可信程序盘，准备中性材料后交GPT-6.1 Sol高思考子智能体独立裁决、核对并完整交付；用于占事及同卦续问，知识维护、课程写作和流程开发不自动启动占断。
---

# Codex大六壬占事

项目根`C:\\Users\\QLMa_\\Documents\\六壬八字测算`。当前专业规则只认`.opencode/liuren-active.json`，实际操作见项目`docs/本机六壬完整研判流程.md`；已装技能和历史说明不覆盖活动规则。工具调用及输入实例见[宿主操作](references/host.md)。

先`node tools/liuren-codex.mjs status`确认ready。准备读当前judgment-core、adjudication及本问domain，report交付前读；详细方法/原书按真实缺口，时间/数量/年命按问触发。依原问明确当事人、阶段与成功条件，用现有修正程序取得或复用完整可信盘与archive，固定起法直接用，不猜年命、不作出生推命。

按同版核心准备中性候选、必要观察、真实未知和精确来源handoff，不预写完整裁决。packet保存逐字原问、input_review来源身份与真实盘引用，程序生成全盘核心和绑定参考索引。普通占断不检索案例/经验库、旧任务或已知答案；原书及书内例证保留。

将packet返回spawn逐字交原生collaboration.spawn_agent，显式model=gpt-6.1-sol、reasoning_effort=high、fork_turns=none，并用bind登记原生agent_id。缺指定模型或原生工具明确未完成，不静默换模型，不用OpenCode task/DeepSeek接口，不把393216额度移植Codex。工作流开发不因本技能派裁决者。

裁决者只接本任务run，先role再read完整核心，依next_request逐页补齐，显示截断须重读。参考使用同run的module/material_id按需；候选可纠正，从完整盘查漏，依U01—U11和专项首取/条件递补裁关键作用、制救、最强反证及逐问结论。细则以绑定正文为准，不在此复制专业长文。

子把完整自由正文写run/report-draft.md，用submit连audit保存，末消息只回回执。数值问依绑定quantity/quantity-strength/quantity-correction取得真实最终quantity_adjustment回执，复制review进quantity_reviews；不拿基础数或单宫分代最终数。主等待并result领全报告，核事实/引用/覆盖/一致性，完成五项review后deliver，忠实交付，不自行改结论、数值、精度或条件。

有具体报告原句及绑定证据才action=recheck，在同一run由原生同一子智能体followup一次，保留report及report-recheck两版；不另建run、不重新派裁决。格式只修格式；长度中断且无已存正文可原智能体续写一次，仍无正文明确未完成，不用内部推理拼报告。余缺review如实登记并随deliver交付。历史任务沿绑定资料领取，不追改旧packet/盘。

历史C01—C11不是待确认清单；V41-01依用户决定保留现行。毕法/课体按核心作有界辅助，不新增独立裁决。共享文件回执只证明文本输出/保存，不证明读者身份、理解、术理正确或预测效果。
'''
put('integrations/codex/daliuren-codex/SKILL.md', codex)
put('docs/Codex大六壬工作流.md', '''# Codex大六壬工作流

本入口共用`.opencode/liuren-active.json`的专业资料、可信修正盘和原书。现行完整步骤只在[本机完整研判流程](本机六壬完整研判流程.md)维护；技能维护源为`integrations/codex/daliuren-codex/SKILL.md`，已装技能应与维护源同步。关键词“使用大六壬进行测算”启用占断；课程、知识维护、流程开发不自动派裁决。

主智能体使用当前模型，中性准备；原生裁决者显式gpt-6.1-sol/high/fork_turns=none，仅接本任务run。主只核事实、引用、覆盖、一致性并完整交付。缺模型/工具明确未完成，不静默回退。OpenCode的DeepSeek与393216额度不移植Codex。

检查`node tools/liuren-codex.mjs status`，请求写UTF-8 JSON并用`node tools/liuren-codex.mjs --request 请求文件.json`执行。packet保留原问/input_review及archive，bind登记原生子；role/read/compute/submit/result/recheck/review/deliver映射见技能[宿主说明](../integrations/codex/daliuren-codex/references/host.md)。裁决正文和回执在output/codex-liuren，同一run的report-recheck保留补核版本；不用新run作为当前补核办法。

核心全读，参考按需。取用职责、旺衰、制救、课体毕法及数量联动以同版judgment-core/专项为准；数字任务最终回执与quantity_reviews相符。普通占断不读两库/旧任务/已知答案，书内例证保留。历史任务沿其绑定规则，不追改；新任务读活动指针。

本桥接不提供操作系统级子进程权限隔离。共享文件读取回执不认证读者身份或语义理解；程序校验不证明术理及预测效果。工程验收不调用付费模型、不声称真实盲测；若要检验模型实际执行稳定性，须另外以无反馈新题验证。
''')
# Keep host schema examples but remove the stale instruction to open a new run.
host = (R/'integrations/codex/daliuren-codex/references/host.md').read_text('utf-8')
host = host.split('\n已确认判断口径以活动judgment-core')[0]
host = host.replace('"unknowns": []', '''"unknowns": [],
    "input_review": {
      "questions": [{"question_id":"Q_1","request_quote":"<原问逐字子问>","success_basis":"<成功标准的来源>","stage_origin":"user_explicit","stage_basis":"<阶段来源；推断用inferred，未知用unknown>"}],
      "facts": [],
      "neutrality_review":"<核对事实、推断与未知，未夹带主智能体判词>"
    }''')
host += '''\n## 核对、补核与数量

领取报告后在同一run用action=review登记五项核对，再action=deliver。具体原句和绑定证据支持错误时action=recheck，返回原智能体的followup；原run另存report-recheck，不得另建run或重派。实际请求形状以返回next_request及动态schema为准。

questions中有quantity任务时，先methods查法，再以quantity_method或expression求本数，strength取得真实状态及without_void；最终quantity_adjustment引用同run基数/strength回执。复制review补question_id/final_receipt_sha256/report_quote进audit.quantity_reviews；source/experimental互斥，同因素不重复调整，量级/单位另述。字段查绑定quantity-correction与consistency_guide，不在此复制全schema。初始示例的tasks仅outcome；问数字/时间时按原问登记相应tasks/task_basis，facts增加一项也须input_review.facts对应来源身份。
'''
put('integrations/codex/daliuren-codex/references/host.md', host)

mainprompt = '''本机大六壬占事只按活动指针和当前daliuren入口。先tool_help(workflow)确认execution_health.ready，准备读judgment-core、adjudication与本问domain，report交付前读；参考/原书按真实缺口，应期数量年命按问，不叠历史版补丁。主线依核心：原问/实际对象/阶段/成功标准→可信全盘→职责与首取/条件递补→有效作用/制救→最强反证→按问细断→独立裁决→五项review→完整交付。主只准备中性候选和精确handoff，不预裁结果；固定程序事实直接用，普通占断不查两库、旧缓存或已知反馈。packet原样task_prompt派一次；读全返回正文，有具体原句和绑定证据才同一裁决者recheck一次，不另派或自行折中。传输recover按next_call条件一次，仍无正文明确未完成。具体数量source/experimental、空减与量级以及毕法边界依同版核心，不在提示中复制旧规则。工具schema/next_call为接口依据。工作流开发排障切Build，不自动派占断。'''
cfg = load(R/'opencode.json')
cfg = json.loads(json.dumps(cfg, ensure_ascii=False).replace('runtime/liuren/'+OLD, 'runtime/liuren/'+NEW))
cfg['agent']['liuren']['prompt'] = mainprompt
(R/'opencode.json').write_bytes(enc(cfg))
slim = load(R/'.opencode/oh-my-opencode-slim.jsonc')
slim['agents']['liuren-adjudicator']['prompt'] = prompt
(R/'.opencode/oh-my-opencode-slim.jsonc').write_bytes(enc(slim))

p['slimming'].pop('retainedUnresolved', None)
p['slimming']['historyRegistry'] = 'references/pending-conflicts.md'
p['flowControl']['legacyMaxAdjudications'] = p['flowControl'].pop('maxAdjudications', 2)
p['flowControl']['maxAdjudications'] = 1
p['adjudication']['workflowBoundaries']['changedEvidenceOnlyRetry'] = False
p['adjudication']['workflowBoundaries']['sameChildEvidenceRecheck'] = True
p['consistencyConsolidation'] = {'id':'liuren-global-consistency-52','scope':'local-opencode-and-codex',
 'adoptedRulesChanged':False,'strengthCoefficientsChanged':False,'quantityBandsChanged':False,
 'historicalRuntimeChanged':False,'predictiveValidationCount':0,'realModelCallCount':0,
 'audit':'output/liuren-global-consistency-52/核查与验收说明.md'}
p['bookRetrieval']['compatibleMethodRelease'] = NEW
p['files'] = {f:sha(R/'.opencode/skills'/f) for f in p['files']}
for f in p['bookRetrieval']['files']: p['bookRetrieval']['files'][f] = sha(R/f)
# Record the actual implementation/entry closure used by readiness checks.
for f in ['opencode.json','integrations/codex/daliuren-codex/SKILL.md',
          'integrations/codex/daliuren-codex/references/host.md']:
    p['workflowImplementation'][f] = sha(R/f)
p['workflowImplementation'] = {f:sha(R/f) for f in p['workflowImplementation']}
for name in ['loader-contract.json','references/shensha-policy.json','references/shensha-authority-evidence.json',
             'references/confirmed-policy-register.json']:
    d = load(T/name);d['release'] = NEW
    if name == 'loader-contract.json':
        d.update(parentRelease=OLD,authoringSource=O.relative_to(R).as_posix(),bookRetrieval=p['bookRetrieval'])
        d['flowControl'] = p['flowControl']
        d['slimming'] = p['slimming']
        d['adjudication'] = p['adjudication']
        d['sourceHashes'] = {f:sha(R/f) for f in d['sourceHashes']}
    (T/name).write_bytes(enc(d))
m = load(T/'manifest.json')
m['modules']['adjudicator-evidence-guide'] = {'file':'references/adjudicator-evidence-guide.md',
    'required':False,'requires':[],'trigger':'E01—E22条件摘要不足时按需查，不强制全读'}
# Two retrieval guides are for a retired workflow; keep the file bytes for
# provenance, but stop advertising them as available judgment modules.
for key in ['case-retrieval-v2','experience-retrieval-v2']:
    m['modules'].pop(key, None)
m.update(release=NEW,parentRelease=OLD,authoringSource=O.relative_to(R).as_posix(),
    bookRetrieval=p['bookRetrieval'],slimming=p['slimming'],flowControl=p['flowControl'],
    adjudication=p['adjudication'],consistencyConsolidation=p['consistencyConsolidation'])
m['files']['references/adjudicator-evidence-guide.md'] = sha(T/'references/adjudicator-evidence-guide.md')
m['files'] = {f:sha(T/f) for f in m['files']}
m['version'] = hashlib.sha256(json.dumps(m['files'], sort_keys=True).encode()).hexdigest()
(T/'manifest.json').write_bytes(enc(m))
p.update(release=NEW,runtime=T.relative_to(R).as_posix(),methodVersion=m['version'],previousRelease=OLD,
    backup=O.relative_to(R).as_posix()+'/before',authoringSource=O.relative_to(R).as_posix())
assert all(sha(R/f) == h for f,h in b['frozen'].items())
temp = R/'.opencode/liuren-active.json.consistency52.tmp'
temp.write_bytes(enc(p));os.replace(temp,R/'.opencode/liuren-active.json')
after = {'release':NEW,'runtime':p['runtime'],'files':{f:sha(R/f) for f in b['files']},
    'new_files':['tools/tests/liuren-workflow-consistency.test.mjs'],
    'parent_unchanged':True,'predictive_validation_count':0}
(O/'after.json').write_bytes(enc(after))
print('Activated', NEW, 'Core chars', len(oldcore), '->', len((T/'references/judgment-core.md').read_text('utf8')))
