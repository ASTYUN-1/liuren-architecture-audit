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

沿用input/output-v2和文件协议v1，程序自动增加deterministic。它由packet工具生成，不手写。chart继续优先archive。每个questions成员新增tasks数组，按原问声明outcome/timing/quantity，可兼有；分清子问，不因未问数量而自动加数量任务。

entities的position省略或写"@program"，程序填写双方坐标；branch只填单个干支、纯支组合或辛（寄宫戌）这种明示格式。现实对象与候选取用写referent/mapping_basis，不能塞入branch或程序坐标。observations保留解释，但verification只能用method_interpretation/unverified；chart_checked归程序，手写会报错。

method_materials优先使用liuren_compute action=source返回的id/title/source_path/line_start/line_end/line_mode/sha256，quote可省略。当前runtime方法可只给路径及已知hash；书籍source需连续行段；universal对应三书检索splitlines行号，lf只适用于明确LF口径的记录，二者不能混。手写quote须逐行相符；程序补齐所选段落，不允许省略号拼接冒充原文。段落完整不等于已涵盖章节全部条件，语义仍核上下文。

tasks含timing会自动装入完整timing；含quantity装完整quantity与quantity-sources，IDs为M_AUTO_TIMING/M_AUTO_QUANTITY/M_AUTO_NUMBERS。主智能体不再抄全文或只抄数表交接。总材料最多40条（含自动项）、程序扩展后总输入20万字符（文件上限70万UTF-8字节），超出明确报错，不静默删减。已读同版正文仍复用，不要求为自动装配再调用一次method。

可选computation_requests保存准备阶段已有计算，格式[{"id":"C_dates","action":"calendar","calendar":{...}}]或[{"id":"C_number","action":"quantity","expression":{...}}]；工具重算后装入deterministic.calculations。原问事实、盘面事实、候选取象、推断与真实反馈仍分开；不传倾向或已知答案。

## 日期与算式

calendar明确start/end（公历日期）、timezone="Asia/Shanghai"、day_boundary="civil-midnight"或"zi-hour"，可给branches或完整pillars过滤；日内可给hour/minute。默认每日午时取样，offset_days=0为start，round_for_branch按过滤范围内同支编号。每次1至732天，超过报错，不截断。它调用固定hash的原引擎lunar.js，列全范围内竞争轮次，不选择应期，也不改原课旬空、天将与课传。起算点、含不含当日和阶段由模型明确，不能把巳日读成四天后。

quantity采用有界表达式，不执行代码。查数节点{"table":"branch","symbol":"丑"}，支持branch/stem/sheng/cheng；常数节点{"value":6}；运算节点{"op":"multiply","args":[...]}，另有add/subtract/divide。没有统一天将数表，不猜腾蛇数；用原法常数时须带来源。十进位、折半、量级与单位需有依据，程序只算提交的式子，不能把原数48自动变480元。小数用有理数计算，并返回exact_fraction。

## 裁决返回与取向义务

entity_checks仍给id/referent/branch/mapping_review/limits，position、five_qi、twelve_states、site_yin、shenjiang、fact_refs由程序回填，裁决者省略；如自行填写而不符会拒绝。relation_checks的computed_relations同理由程序生成。模型写的是validity、reason、effect_scope；被逐问结论用作决定性或反证的关系，另给application={object,mechanism,stage,goal_effect,alternative_resolution}，说明作用于谁、怎么起作用、过程/结果哪一层、怎样关联目标、为何不取最强另一解释。不要为每个无关节点填长表。

问及应期/数量时，完成裁决须向liuren_adjudication_submit提交special_methods，一项对应一个question_id+kind。共同字段：question_id、kind（timing/quantity）、status（completed/unresolved）、target、basis_ids（方法来源ID）、fact_ids（可选盘面/观察/事实ID）、calculation_ids、alternatives、limits、record。未定写具体缺口，不自动折中或降档。确需新资料而整体返回needs_input时，可暂不填尚未完成的专法记录，missing_inputs须给具体缺项。

timing.record包含event/stage/scale/start/count_rule/trigger/selected_method/round_comparison；completed须有candidates数组，每项date/day/event与所引用calendar计算相符。quantity.record包含object/position/number_table/operation/adjustments/magnitude/unit/precision；completed另给数值value，与引用quantity计算相符。只有干支候选、月份/年份/窗口而未完成公历转换时允许unresolved，保留已有判断及具体转换缺口，不把缺换算改为成败不明。

需要新算时，裁决者可用liuren_compute；最终calculations只交请求[{id:"C_...",action:"calendar",calendar:{...}}]或quantity+expression，程序重新计算，不交手写result。special_methods引用同ID。没有新增计算可填[]并引用输入已有计算。不得把主智能体、程序、子智能体各算一套作为三份独立证据。

主智能体核回传事实、问项/争点/专法覆盖和解释有没有越过依据，复用裁决及special_methods写完整技术报告，应期和数量各保留择法、条件、竞争候选/轮次或量级、算式与单位；不另发明决定性理由、不为谨慎折中改判。格式失败就地修复；具体事实/引用错误或必要新资料，按adjudication一次有据补核规则处理。





执行、回执和失败恢复统一见methods/adjudication.md。
