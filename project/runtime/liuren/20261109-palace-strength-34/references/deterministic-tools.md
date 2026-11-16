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

30版：裁决请求显式申请max_tokens=393216，保持deepseek-flash/high；省略参数会采用服务端64K默认值，不能取消额度。重启后workflow须features.explicit_output_budget=true、requested_max_output_tokens=393216且execution_health.ready=true。task_result无公开末消息时，用liuren_adjudication_result(action="read",task_id=原子会话ID)领取已存结果或失败。仅核心完整读完（旧文件为原全文）且finish=length、无公开报告时，按next_call在同一子会话recover一次；不新建裁决、不把reasoning转成正文。仍无正文则明确未完成，不循环领取/重派。

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
