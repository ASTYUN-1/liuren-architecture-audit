# 确定性事实、专法计算与交接：当前接口

交接报错按具体字段修正，保留facts、observations、focus_issues和unknowns；不通过删空材料、换request_id、换归档hash或反复probe来定位。request_id允许日期开头或UUID。当前runtime方法只需路径及已知hash即可装入完整正文；书籍范围错误会指出材料ID、路径和合法行界。输入容量按程序扩展后的完整盘、方法和计算共20万字符检查，文件上限70万UTF-8字节；超限明确报出实际值，不静默删减。

每问questions[].domain用于分类占资料路由。actor_entity_id不必填写；事件理解、当事对象及干支取用由模型完成。event_positioning仅记录分类和资料版本，不记录或验证角色绑定。程序装入完整定位及对应分类占，保留已读回执、坐标/阴神、日期、算式及来源校验，不承担人物身份推断。

程序负责定位、查表、关系枚举、日期和算式、连续引文及交接校验；模型负责取用、适用条件、作用效力和结果。不得把表中关系直接当成已发生作用或成败，计算通过不证明预测有效。经验库、案例库仍关闭。

## 读取与复用

liuren_chart已保留完整facts并增加program_facts，提供干支上阴、关键节点状态和关系；同盘先用返回结果，不再手算或重复读原JSON。engine_inventory.references指回同一chart.facts，原growth、seasonal_strength、nobleman、chart_types、userinfo/declared_life等不丢弃，也不重复塞全文。纠正神煞只采用shensha_resolution，不能因原标签仍保留就采用未登记项。旧userinfo年龄/年命未独立核验，禁止用它自动替代已核年命。

程序每个支节点同时给天盘该支的落宫/乘将、地盘同名宫的上神/乘将、直接阴神；不要把这三者混为同一位置。干阳干阴、支阳支阴来自四课/寄宫校对。D_B0至D_B11为支事实，D_S0至D_S9为干事实，可用于basis_ids。其他query关系ID只作导航，引用时回到参与的D_B/D_S与原法材料。

需要新增节点或具体计算时用liuren_compute。主智能体的chart/lookup/life传原archive={path,sha256}；裁决者不传archive，自动限定当前文件盘。action=chart可用symbols限定支/干；lookup需subject，可给reference/place/profile（four-seasons或quarter-earth）；calendar与quantity无需再次读取课盘。只用当前获准资料，source仅主智能体可用。

## 状态口径

五气同时提供four-seasons（四时分组）与quarter-earth（辰未戌丑土旺）条件表，并保留引擎原值；有分歧时根据实际原法说明采用口径，不能自动选更有利者、计为两票或合成分数。类神自身十二气按当前已采用的木亥、火寅、金巳、水土申五行顺行口径；引擎growth.day_stem另有阴干逆行，保留作异口径材料，不能自动替换。某字为墓、死、长生，不自动推出报废、死亡或存活。六亲默认对日干；lookup可明确其他reference，解释不得偷偷换参照。

life仅接受明确sex、age整数、age_basis="虚岁-已核"，可带用户已给birth_pillar。按references/nianming.md男一岁丙寅顺数、女一岁壬申逆数；程序不从本命猜出生年、年龄或年界。不接出生推命、大运、小限、飞限。

## 交接输入

沿用输入v2、灵活报告和文件协议v1，程序自动增加deterministic。它由packet工具生成，不手写。chart继续优先archive。每个questions成员新增tasks数组，按原问声明outcome/timing/quantity，可兼有；分清子问，不因未问数量而自动加数量任务。

entities的position省略或写"@program"，程序填写双方坐标；branch只填单个干支、纯支组合或辛（寄宫戌）这种明示格式。现实对象与候选取用写referent/mapping_basis，不能塞入branch或程序坐标。observations保留解释，但verification只能用method_interpretation/unverified；chart_checked归程序，手写会报错。

method_materials优先使用liuren_compute action=source返回的id/title/source_path/line_start/line_end/line_mode/sha256，quote可省略。当前runtime方法可只给路径及已知hash；书籍source需连续行段；universal对应三书检索splitlines行号，lf只适用于明确LF口径的记录，二者不能混。手写quote须逐行相符；程序补齐所选段落，不允许省略号拼接冒充原文。段落完整不等于已涵盖章节全部条件，语义仍核上下文。

tasks含timing会自动装入完整timing；含quantity装完整quantity与quantity-sources，IDs为M_AUTO_TIMING/M_AUTO_QUANTITY/M_AUTO_NUMBERS。主智能体不再抄全文或只抄数表交接。总材料最多40条（含自动项）、程序扩展后总输入20万字符（文件上限70万UTF-8字节），超出明确报错，不静默删减。已读同版正文仍复用，不要求为自动装配再调用一次method。

可选computation_requests保存准备阶段已有计算，格式[{"id":"C_dates","action":"calendar","calendar":{...}}]或[{"id":"C_number","action":"quantity","expression":{...}}]；工具重算后装入deterministic.calculations。原问事实、盘面事实、候选取象、推断与真实反馈仍分开；不传倾向或已知答案。

## 日期与算式

calendar明确start/end（公历日期）、timezone="Asia/Shanghai"、day_boundary="civil-midnight"或"zi-hour"，可给branches或完整pillars过滤；日内可给hour/minute。默认每日午时取样，offset_days=0为start，round_for_branch按过滤范围内同支编号。每次1至732天，超过报错，不截断。它调用固定hash的原引擎lunar.js，列全范围内竞争轮次，不选择应期，也不改原课旬空、天将与课传。起算点、含不含当日和阶段由模型明确，不能把巳日读成四天后。

quantity采用有界表达式，不执行代码。查数节点{"table":"branch","symbol":"丑"}，支持branch/stem/sheng/cheng；常数节点{"value":6}；运算节点{"op":"multiply","args":[...]}，另有add/subtract/divide。没有统一天将数表，不猜腾蛇数；用原法常数时须带来源。十进位、折半、量级与单位需有依据，程序只算提交的式子，不能把原数48自动变480元。小数用有理数计算，并返回exact_fraction。

## 裁决返回与取向义务

timing.record包含event/stage/scale/start/count_rule/trigger/selected_method/round_comparison；completed须有candidates数组，每项date/day/event与所引用calendar计算相符。quantity.record包含object/position/number_table/operation/adjustments/magnitude/unit/precision；completed另给数值value，与引用quantity计算相符。只有干支候选、月份/年份/窗口而未完成公历转换时允许unresolved，保留已有判断及具体转换缺口，不把缺换算改为成败不明。

主智能体核回传事实、问项/争点/专法覆盖和解释有没有越过依据，复用裁决报告写完整技术报告，应期和数量各保留择法、条件、竞争候选/轮次或量级、算式与单位；不另发明决定性理由、不为谨慎折中改判。仅传输失败才修复；具体事实/引用错误或必要新资料，按adjudication一次有据补核规则处理。

执行、回执和失败恢复统一见methods/adjudication.md。

## 工具参数速查：直接按接口交接

工具参数以当前会话展示的schema为准，禁止猜字段、路径、hash、行号或ID。发现当前schema与本文冲突，保留具体报错并停止该步，不能用空材料试探。以下用法不增加专业阶段或模型调用。

| 操作 | 调用与必填内容 | 返回后怎样复用 |
|---|---|---|
| 排盘 | liuren_chart，明确占时用datetime；仅用户/可靠原盘给齐四柱和月将才用manual-pillars | 先核ok与validation.ok；保存archive.path/sha256和program_facts。同盘复用；原图与自动盘冲突就说明具体差异，不手推或试改月将去匹配 |
| 方法/分类全文 | liuren_materials {"action":"method","module":"illness"}；module按本问替换 | 完整正文读后运用；元数据handoff可原样放入method_materials。操作说明没有handoff时不把它冒充专业证据 |
| 三书检索 | liuren_materials {"action":"book_search","query":"本问争点词","limit":4}；query与queries二选一 | 每个完整hit的handoff可原样交接；handoff=null或passage_complete=false先按continuation补原段，不把未读行当已读 |
| 确定性计算 | liuren_compute，action为lookup/calendar/quantity/life/source，配同名对象（quantity用expression） | 优先复用program_facts；calendar明确start/end/timezone/day_boundary。已返完整方法引用不再为转换路径调用source |
| 保存裁决材料 | liuren_adjudication_packet {packet:完整input-v2对象} | 成功返回task_prompt；packet不是JSON字符串，不能省掉外层packet |
| 派裁决 | task，subagent_type="liuren-adjudicator"，prompt原样填返回的task_prompt，description简述任务 | 不塞长上下文，不用background:true，不填旧task_id；裁决者read读完本次文件并submit |
| 领取与交付 | 主智能体task_result(task_id=回执的子会话ID)；随后liuren_adjudication_result(action="deliver",task_id=同ID) | ID丢失先action="locate"；具体问题用read/repair。成功回执不等于正文，格式错误不重派裁决 |

questions每个子问均必填id/text/subject/domain/stage/deadline/success_criteria/alternatives/tasks/task_basis。疾病四个子问分别写domain="illness"，不是只给总分类；考试用exam，其余用schema枚举。tasks仅用outcome/timing/quantity，逐项task_basis说明原问要求或必要性，不自动增加任务。domain用于资料路由，不做人物身份或日干角色锁定。

method_materials优先原样复制每次资料返回的handoff对象，同一id只保留一次。source_path支持工作区相对路径和该工作区内的合法绝对路径，程序统一为相对路径；无需模型转换斜杠或删盘符。仅接受当前runtime、书籍库/、books/及已登记应期资料，保留版本/hash/原文连续行段校验。当前runtime方法只需id/title/source_path和已知sha256，省略quote与行界装全文；书籍必须给准确line_start/line_end/line_mode，quote可省略。引用字段来自返回结果，不凭记忆重建。

修错以字段为单位：domain报错只补对应问项；source_path报错只修指出的材料引用。packet保存失败还没有派出裁决，保留其余分析材料修正后重提；task已经成功则领取结果，不再次派裁决。不要把路径错误当成缺书重新全库检索，不换request_id或archive.sha256绕过校验。


## 报告传输边界（本版）

裁决报告采用灵活表达：liuren_adjudication_submit({result: 报告正文字符串或自由JSON对象})。无需output-v2、固定分析字段或application五项表；程序不补写、不删改、不以缺字段拒收。依据、关键作用、反证、条件题、应期取数按实际问题说明，条件未满足可自然说明不答。需要补资料时可提交对象并标status="needs_input"、说明缺项。成功后末消息返回工具回执；主智能体用task_result领取，read查看原报告，读report后deliver领取原样报告与hash。只有非空、可保存、容量及任务归属/文件完整读取等传输检查；contractChecked仅兼容旧回执，validationScope="transport-only"、professionalContentChecked=false明确不作专业验收。不得为格式差异重派裁决。


21版工具自说明：liuren_tool_help(topic=packet/compute)返回当前实际schema；workflow带domains返回就绪缺项及next_calls。仅补缺读，不替代方法全文。记录id全局唯一，事实F_、争点I_分开；神煞观察kind可为shensha，不升级为程序事实。主智能体compute的chart/lookup/life均须原样带archive。packet/reader成功按next_call继续；剩余页为空后才提交自由正文，不设固定专业输出字段。
