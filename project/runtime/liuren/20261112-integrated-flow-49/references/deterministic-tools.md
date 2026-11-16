# 程序事实与计算接口

参数以当前工具schema和liuren_tool_help为准。程序负责坐标、查表、计算及来源/传输校验；模型负责对象取用、方法条件与效力。交接和失败恢复只按methods/adjudication.md，不增加专业阶段。

## 读取与复用

liuren_chart已保留完整facts并增加program_facts，提供干支上阴、关键节点状态和关系；同盘先用返回结果，不再手算或重复读原JSON。engine_inventory.references指回同一chart.facts，原growth、seasonal_strength、nobleman、chart_types、userinfo/declared_life等不丢弃，也不重复塞全文。纠正神煞只采用shensha_resolution，不能因原标签仍保留就采用未登记项。旧userinfo年龄/年命未独立核验，禁止用它自动替代已核年命。

程序每个支节点同时给天盘该支的落宫/乘将、地盘同名宫的上神/乘将、直接阴神；不要把这三者混为同一位置。干阳干阴、支阳支阴来自四课/寄宫校对。D_B0至D_B11为支事实，D_S0至D_S9为干事实，可用于basis_ids。其他query关系ID只作导航，引用时回到参与的D_B/D_S与原法材料。

需要新增节点或具体计算时用liuren_compute。主智能体的chart/lookup/life可原样传liuren_chart.archive（含可选raw_sha256），或只传archive={path,sha256}；可选raw_sha256与已验证文件内的原始哈希核对；裁决者不传archive，自动限定当前文件盘。action=chart可用symbols限定支/干；lookup需subject，可给reference/place/profile（four-seasons或quarter-earth）；calendar与quantity无需再次读取课盘。只用当前获准资料，source仅主智能体可用。

## 状态口径

五气同时提供four-seasons（四时分组）与quarter-earth（辰未戌丑土旺）条件表，并保留引擎原值；有分歧时根据实际原法说明采用口径，不能自动选更有利者、计为两票或合成分数。按U04分对象：日干采用天干阳顺阴逆（丁见未冠带）；支神/天将采用木亥火寅金巳水土申五行顺行。天将对乘支与对地盘分别提供，不能只保留后一层；lookup返回growth_profile。某字为墓、死、长生，不自动推出报废、死亡或存活。六亲默认对日干；lookup可明确其他reference，解释不得偷偷换参照。

life仅接受明确sex、age整数、age_basis="虚岁-已核"，可带用户已给birth_pillar。按references/nianming.md男一岁丙寅顺数、女一岁壬申逆数；程序不从本命猜出生年、年龄或年界。不接出生推命、大运、小限、飞限。

## 交接输入

沿用输入v2、灵活报告和文件协议v1，程序自动增加deterministic。它由packet工具生成，不手写。chart继续优先archive。每个questions成员新增tasks数组，按原问声明outcome/timing/quantity，可兼有；分清子问，不因未问数量而自动加数量任务。

entities的position省略或写"@program"，程序填写双方坐标；branch只填单个干支、纯支组合或辛（寄宫戌）这种明示格式。现实对象与候选取用写referent/mapping_basis，不能塞入branch或程序坐标。observations保留解释，但verification只能用method_interpretation/unverified；chart_checked归程序，手写会报错。

method_materials优先使用liuren_compute action=source返回的id/title/source_path/line_start/line_end/line_mode/sha256，quote可省略。当前runtime方法可只给路径及已知hash；书籍source需连续行段；universal对应三书检索splitlines行号，lf只适用于明确LF口径的记录，二者不能混。手写quote须逐行相符；程序补齐所选段落，不允许省略号拼接冒充原文。段落完整不等于已涵盖章节全部条件，语义仍核上下文。

tasks含timing会在完整存档装入timing；含quantity装quantity与quantity-sources，核心只列参考索引，裁决者按任务需要查读，IDs为M_AUTO_TIMING/M_AUTO_QUANTITY/M_AUTO_NUMBERS。主智能体不再抄全文或只抄数表交接。总材料最多40条（含自动项）、程序扩展后总输入20万字符（文件上限70万UTF-8字节），超出明确报错，不静默删减。已读同版正文仍复用，不要求为自动装配再调用一次method。

可选computation_requests保存准备阶段已有计算，格式[{"id":"C_dates","action":"calendar","calendar":{...}}]或[{"id":"C_number","action":"quantity","expression":{...}}]；工具重算后装入deterministic.calculations。原问事实、盘面事实、候选取象、推断与真实反馈仍分开；不传倾向或已知答案。

## 日期与算式

calendar明确start/end（公历日期）、timezone="Asia/Shanghai"、day_boundary="civil-midnight"或"zi-hour"，可给branches或完整pillars过滤；日内可给hour/minute。默认每日午时取样，offset_days=0为start，round_for_branch按过滤范围内同支编号。每次1至732天，超过报错，不截断。它调用固定hash的原引擎lunar.js，列全范围内竞争轮次，不选择应期，也不改原课旬空、天将与课传。起算点、含不含当日和阶段由模型明确，不能把巳日读成四天后。

quantity采用有界表达式，不执行代码。查数节点{"table":"branch","symbol":"丑"}，支持branch/stem/sheng/cheng；常数节点{"value":6}；运算节点{"op":"multiply","args":[...]}，另有add/subtract/divide。没有统一天将数表，不猜腾蛇数；用原法常数时须带来源。十进位、折半、量级与单位需有依据，程序只算提交的式子，不能把原数48自动变480元。小数用有理数计算，并返回exact_fraction。

裁决输出为完整正文或自由JSON，时间与数值的专业记录按report说明，不强制record/application等字段。工具保留计算回执，主智能体核范围/时区/日界一致后复用。当前工具契约为liuren-tools-31；候选方法版本不是宿主工具重载证据。

38版OpenCode模型对照：裁决者deepseek/deepseek-flash/high，申请393216生成上限；主智能体保留用户所选模型。workflow须features.explicit_output_budget=true、requested_max_output_tokens=393216且execution_health.ready=true。Codex原生裁决仍用Sol/high，不套用DeepSeek额度。task_result无公开末消息时，用liuren_adjudication_result(action="read",task_id=原子会话ID)领取已存结果或失败。仅核心完整读完（旧文件为原全文）且finish=length、无公开报告时，按next_call在同一子会话recover一次；不新建裁决、不把reasoning转成正文。仍无正文则明确未完成，不循环领取/重派。

29版启动：workflow.execution_health.ready核对进程实际加载的插件/流程hash。false时只读取已有报告，不新派发。locate可恢复唯一已绑定子会话，running不记空报告；已结束的恢复会在read时核对并收束。完整操作见docs/本机六壬稳定运行指南.md。

31版：核心含完整程序盘、紧凑状态表、共用判断规范、本问专项及必要候选；原书/详细方法另存hash绑定档案。reader默认核心，核心读完即可submit。决定性条件不清、反证冲突或摘要不足时，用同一file_path/sha256加material_id（含E01—E22）或module查连续原文。参考不要求逐项读，参考页不计核心读取回执。完整存档与旧文件兼容保留。


## 单宫旺衰与取用后补算（34版，主、子共同执行）

默认`strength_index`只表示该对象的单宫旺衰：计月令、对象自身十二气、旬空/坐空以及本宫天地、自己的直接阴神、同宫神将的直接生扶泄耗克制。它不是全局旺衰、取用后的最终作用、成败概率，也不是吉凶分。天将对地盘只有十二气参照，不新增将地生克边；不凭同在课传就互相加减。原局空亡字段保留，已计的空亡不再扣一次。

固定分档：E=0表示本计算没有有效力量（缺失/null不能记0）；0<E<1极弱，通常难独立显著作用；1≤E<2.5弱但仍有作用；2.5≤E<5偏弱至中等可作用；5≤E<7.5较强；7.5≤E≤10强。5是基准，2.5是弱力参考，均非可用/不可用开关。极弱也不删除节点，仍看结构、触发、应期与具体任务；不能以低分直接断事情不成。不得把这些研究分档冒充已验证的自然能量单位或准确率。

实际取用后，其他宫位可能生扶、泄耗或克制类神。先依原法明确双方类神身份、实际影响通路和依据，再调用`liuren_compute(action="strength", strength=...)`补算；不能因五行相生克便自动全盘联算，不能自行估算、手加分或另乘空亡倍率。工具推导生克类型及固定系数，返回单宫分、补算分、差额与分档；主、子均直接采信程序数值，不复核排盘算术。工具不能验证取用理由的专业真伪：模型仍须解释取用、能否兑现及最强反证。取用纠正时，用完整的新关系清单重算，不在上次补算结果上层叠加。原有直接关系工具自动跳过，未提交关系不扩散。

补算沿用原盘月令条件表，季月有双表时说明原法依据并沿同表比较，不按得分高低择表；需敏感性比较则两表各算且分别解释，不平均、不计两票。时间改变另按U10查应期，当前补算不自动更新时柱或旬空。三合/半合/三会数值继续暂缓。

单宫E与对某对象的实际作用分层：官鬼、财、父母的直接贪生合及制救仍依U03/U06；自身旺不保证能为我用，弱也不等于不能用。补算已适配的直接贪生/合绊降低对外传递，尚未量化的刑冲、神煞、事件条件仍由原法分析，不拿研究分数覆盖。完整定向作用A若为null代表适配不足，不是没有作用。

仅在需要给出取用后的数值增减时强制调用补算，不把所有盘面关系变成新待办。主智能体准备保持中性，裁决者可改候选类神并调用同工具；主智能体核对分数含义、关系依据和口径一致性，不重新折中改判。详细参数及调用例见`deterministic-tools`，工程接口不限制自由裁决报告。

### 工具参数与计算含义

`mode=single_palace`仅查询，给actors并省略links。`mode=selected_relations`必须给非空links；actors每项为`id/role/basis`，links每项为`source/target/basis`。T表示天盘支、J表示天将、S仅本日日干；不接受地盘D作为跨宫施受者。source是施生、施克或比和方，程序自行定类型，反向输入、重复关系、未取用对象或自定系数均拒绝。主智能体在OpenCode须带完整`archive`，裁决者自动用绑定盘而不填archive。

示例仅演示已经完成取用后的“金生子水”，不主张本案应取酉为施助者：

```json
{
  "action": "strength",
  "strength": {
    "mode": "selected_relations",
    "season_profile": "quarter-earth",
    "season_basis": "本问按所用原法采用季土条件表",
    "actors": [
      {
        "id": "T:酉",
        "role": "假设施助方",
        "basis": "示例：经原法取用并确认施助身份"
      },
      {
        "id": "T:子",
        "role": "假设目标类神",
        "basis": "示例指定，非本课实际裁决"
      }
    ],
    "links": [
      {
        "source": "T:酉",
        "target": "T:子",
        "basis": "示例：确认此施助方对目标存在生扶通路"
      }
    ]
  }
}
```

Codex子智能体使用`node tools/liuren-codex.mjs --request 请求文件`，请求为`{"action":"compute","run":"本任务run绝对路径","request":上述对象}`。主智能体未建run时也可调用，省略run而在request中附可信盘的完整archive；沿用归档hash，不重新排盘。两宿主共用算法，调用结果留回执；旧绑定核心未含本版单宫算法的任务不混用新补算。

补算固定本宫已算平衡，令L_i=B_i+单宫净作用，H为通达系数，V为空亡保留率，则 E'_i=V_i×clip[0,10](H_i×(L_i+Σ新增受力−Σ新增施力耗费))。不是把已经扣空的E再乘一遍V。未取用宫位保持原单宫观察，不自动连锁传播；同次多个明确关系共同迭代，从0/5/10多初值验算收敛。每次请求是完整关系快照，不读取前次结果叠加。

新增通路系数固定0.75，同施者通路合计超过2时按比例归一。沿用研究参数：生入0.20×g×源分×τ，源泄0.10×g×源分×τ；克入−0.20×g×源分×τ/(1+受者分/5)，施克耗为克量绝对值×0.20；比和0.06×g×min(源分,源基础种子)。τ沿源节点已适配的直接贪生合限制取1−goal_loss，生与克均考虑；未适配的专项不冒充已量化。此处系数为工程研究约定，并非原书已有精确比例。

读返回的actors.single_palace、adjusted、delta、level及applied_relations；already_local_or_blocked说明本次未重复叠加的直接关系或初末时序限制。普通交付不贴全部审计迭代账；有疑问再查回执。任何分数都不能直接换算是否录用、职位或行业。


# 35版确定性工具使用说明

工具负责固定查表和计算，AI负责取用、适用条件、选法和裁决。默认盘不增加这些专项的完整输出；按问调用。

OpenCode主智能体调用liuren_compute；盘面计算附原样archive，裁决子智能体自动绑定原盘。Codex使用 `node tools/liuren-codex.mjs --request 请求文件`，外层为 `{"action":"compute","request":下列对象}`；裁决者另带本任务run。两宿主共用内核。

## 方法查询

```json
{"action":"methods","methods":{"kind":"quantity"}}
```

kind可换imagery；可给id查询单项。目录返回适用范围、必填字段、来源和方法精度，不自动推荐最有利的算法。

## 具名取数

```json
{
  "action":"quantity",
  "quantity_method":{
    "id":"CY501-use-ground",
    "target":"T:戌",
    "season_profile":"quarter-earth",
    "basis":"示例结构；实际须确认本盘初传和采用口径"
  }
}
```

主智能体另加archive；target必须是本盘实际对象，不照抄示例支。

| id | 已实现步骤 | 必填参数 |
| --- | --- | --- |
| CY501-use-ground | 《粹言》501实际初传与地盘五气分支；旺列10/100倍候选，相相乘加倍，休相加，囚死相加折半 | target、season_profile、basis |
| WY244-month | 《五要》244实际初传：月建倍、月破半，其余不加减；不加入地盘天将 | target、number_table、basis |
| WY67-shenjiang-base | 《五要》67选定天盘类神乘本段天将数，不强制入传；仅基础数 | target、basis |
| WY242-generated-base | 《五要》242指定传神：旺相取五行成数，其余取生数；仅基础步 | target、season_profile、basis |

number_table只供WY244-month，取branch/sheng/cheng，按原法选表。季月沿已说明口径，不按结果高低换表。上述旺衰读取月令五气，不用综合指数改写原文条件。

返回stage、value或candidates、unit及unresolved。base-only不是最终数量；旺气原文量级候选不擅选其中一个。unit可给已明确的单位，但工具不能凭单位猜十倍百倍。未执行的后续步骤明确保留，不能以基础值冒充完整断数。

旧expression查表算式保持兼容，但不能与quantity_method同次混用，也不自动叠到另一个数法结果上。

## 历法推演

原有start/end、timezone=Asia/Shanghai及day_boundary参数保持。day_boundary取civil-midnight（00:00）或zi-hour（23:00）；日柱和时干共用所选口径。

```json
{"action":"calendar","calendar":{"start":"2026-11-01","end":"2026-11-30","timezone":"Asia/Shanghai","day_boundary":"civil-midnight","mode":"boundaries","boundary_types":["节气","节月","旬界"]}}
```

boundary_types还可给日界。模式boundaries不同时接采样或行筛选参数。节月以引擎节气准确时刻切换，不以公历月初替代。

```json
{"action":"calendar","calendar":{"start":"2026-11-06","end":"2026-11-20","timezone":"Asia/Shanghai","day_boundary":"civil-midnight","match":{"target":"子","relation":"冲","axis":"day"},"origin":"2026-11-06T14:43"}}
```

relation可取值、冲、六合；axis可取day/hour。branch/pillars原筛选仍可用。origin可给原占日期或本地时刻，不带时刻时取午时；in_origin_xun标记是否处于原来那一次十日旬，六十日后旬名重复不会重新认作原旬。origin_state=inside/outside可筛选。

sample_minutes枚举全天分钟步长，不与hour/minute同用。默认仍每日午时取样。区间最多732天，样本最多10000，越界明确报错而不截断。返回全范围匹配，不选择“真正应期”。值、冲、合的关系事实不等同填实、冲开或事情完成。

## 时间情景与旺衰

```json
{
  "action":"evaluation",
  "evaluation":{
    "calendar":{"start":"2026-11-06","end":"2026-11-10","timezone":"Asia/Shanghai","day_boundary":"civil-midnight"},
    "strength":{
      "mode":"single_palace",
      "season_profile":"quarter-earth",
      "season_basis":"示例固定采用季土表；实际依原法",
      "actors":[{"id":"T:寅","role":"示例目标","basis":"实际需完成取用"}]
    },
    "void_policy":"original"
  }
}
```

主智能体附archive。strength亦支持现有selected_relations及完整links，由历法时间直接驱动计算。最多128个匹配时刻；对象位置、原日干及原课传不变，只更新声明范围内条件，未加入未来日时自动生克。

- original（默认）：保留原空亡计算条件，按评价节月更新五气。不是宣称出旬后仍应永远论空，只是隔离尚未确定的空亡机制。
- evaluation-xun-research：沿既有研究接口以评价日柱的新旬空替换空条件；仅供明确提出的比较试算，不等同已经确定的出旬、填实或冲实判法。

两种政策均沿用34版空亡系数。返回的evaluation_void是评价日历事实，original_void是原盘事实；以void_policy说明本次实际采用哪组条件。不得根据结果高低切换政策或平均两种分数。

## 条件取象

```json
{"action":"imagery","imagery":{"id":"DF449-growth","target":"T:寅","reference":"ground","basis":"示例：确认本段专项适用并看所临地盘"}}
```

主智能体附archive。首批target仅支持天盘支，其他对象不冒充已经实现。

| id | 参数与范围 |
| --- | --- |
| MG104-material | 实际初传；season_profile、basis；匹配《鬼撮脚》103—104明确的月令五气材质候选 |
| DF449-growth | reference=ground/yin及basis；匹配《东方朔》449的具名十二气阶段/外观，不读月令倍率 |
| DF75-void | basis；本支旬空并入传时返回空虚/孔窍候选，坐空单独列，不自动等同 |

matches为空只表示此方法没有匹配，不表示无物或无作用。物态候选不直接推广为求职、财运等事情成败；不同射覆专法的起法与使用位置仍由AI核上下文。

## 交付与版本

程序结果直接采信，不让模型重复手算。取用、方法适用性与最终解释仍由裁决者完成，主智能体按现行分工核对交付。工具结果不强制专业报告采用固定格式。

34版直接关系、空亡参数和弱力分档保持；三合、半合、三会数值暂缓。新方法只在35版新绑定任务使用；历史任务沿原版，若发现旧任务需要新工具应另建明确的新任务绑定，不混用旧回执。


## 第39版执行核对

39版一致性核对：新任务保留原问与input_review来源身份；子报告附简短audit，登记关键作用、最强反证与真实计算覆盖。局部补算不能冒充综合结果。主智能体read核对后用review登记事实身份、职责阶段、计算范围、反证、逐问约束五项；有具体原句和绑定证据才用原子会话recheck一次，保留前后报告，未解决缺口显式交付，不另派或自行改判。程序不选类神、不裁成败、不设分数阈值，正文仍自由表达。专业方法与模型选择沿用38版；网站未发布。接口见docs/本机六壬一致性核对-39.md。


40版直接作答：子智能体开始裁决前采用direct-answer规则，先综合依据再选主判。是非给是/否或倾向，数值给有依据的最佳估计值和单位，位置结合方向与分野给主选地区，原因给主因；不以中间类象、候选堆积、反复免责声明代替答案，不把未问的高精度设成拒答门槛。不随机选边、不编数值或过度定位，敏感隐私不凭盘面臆断。提交前自查，主智能体在39版answer_constraints复核直接作答及前后未撤回，calculation_scope核估计依据。主准备保持中性，不能替子智能体选结果；保留一次原子会话补核与未决项。仅本机OpenCode及共用Codex，新任务加载；网站未发布。详见docs/本机六壬直接作答-40.md。


41版：methods(quantity)现有5个分支，新增LF3329-class-ground；目标可为有据选定关键类神，不强制初传/入传。旺仅基础数、相相乘、休相加、囚死相加折半。具名取数回执新增calculation_scope，明确未读取综合指数/未作空亡数量修正。额外有据数值修正另次调用quantity expression，见quantity-strength。

## 49版旺衰工具的按需核查

strength原参数增加可选review:true；默认不输出扩展核查，不改变已有系数、单宫值、补算值、空亡口径或合局暂缓决定。仍先依问取用并说明依据，再提交actors；需要数值增减时给完整links快照。

review返回state_basis（各已选对象五气、十二气参照、旬空/坐空、通达及直接关系）、relation_candidates（仅已声明对象两两关系事实，含刑冲合害；未提交关系不自动算作用）、season_comparison（同一actors/links分别核季土双表，不选择高分表、不平均）。这些是定点查漏工具，不是全盘穷举义务；不应每次自动附review:true。

coverage始终说明提交和实际计算的关系数、未更新其他宫位、未验证专业取用/通路适用性、不能判成败。state_basis.pending_action_conditions是内部作用适配提示；神煞未提供、专项未适配等不得理解为没有作用，也不要求把所有提示变成新待办。

例：在原strength对象中加"review":true即可；其他mode/season_profile/season_basis/actors/links不变。可用single_palace查关键节点的基础与事实，再按原法确认必要关系补算；已有材料足够时直接selected_relations，无须固定多跑一轮。evaluation中的strength也支持review，保持原旬空/研究新旬政策各自身份。

未补入：全盘自动取用、自动通路裁定、成败概率、所有刑冲神煞数值化、三合半合三会数值、自动合化、已校准系数或所有未来兑现机制。定性未量化不等于不参与原法判断。
