# 文件式独立裁决、提交与恢复

主智能体准备到可裁决，裁决者对完整盘查漏、裁关键作用；主智能体核事实与覆盖并忠实交付，不重新权衡。对事件自然理解并依分类专法取用，必要依据记录在实体与观察；程序仅路由分类与计算，不绑定人物。

## 当前工具交接与恢复

每问声明domain、tasks和逐项task_basis：原问明确要求用user_requested及逐字request_quote，必要附属任务用necessary并说明理由。只给占时不等于问应期，不为完整性自加应期、金额。程序保存原问；事件理解及取用由模型依分类专法完成，不做亲属称谓推断或日干角色锁定。

先复用liuren_chart.program_facts。必要时liuren_compute定点查坐标、阴神、状态、日期或算式；程序给关系，不替模型裁效力。chart优先原样引用排盘返回的archive.path/sha256；无归档才复制完整facts含内层schema。实体branch只放干支、纯支组合或戊（寄宫巳），说明放mapping_basis；position省略或@program。观察verification只用method_interpretation/unverified。

method_materials的当前runtime方法可只给ID、标题、路径及已知hash，由程序核manifest装全文；书籍用准确行段、line_mode与hash，quote可省略。应期/取数全文随tasks自动进入裁决文件，不再抄全文。材料总数最多40条（含自动项）、扩展后输入20万字符、文件70万UTF-8字节；超限指出实际值，不静默删减。准备阶段缺哪个必查/专项只补哪个，report在交付前读。

1. liuren_adjudication_packet保存中性材料。focus_issues引用已有观察列实质争点，不传倾向/排序，不凑正反；无争点填[]。报错按具体字段改，不删空材料、换ID或归档hash做探针。
2. 返回task_prompt原样交task(subagent_type="liuren-adjudicator")；不填task_id，不用background:true，不塞长上下文。裁决者逐页读完当前绑定文件，正常研判取用、查漏与关键效力，不另跑身份核验。模型deepseek/deepseek-flash、高思考，由oh-my-opencode-slim注册。
3. 裁决者liuren_adjudication_submit提交output-v2；程序字段省略。应期候选在record.candidates，数值在record.value；special_methods.basis_ids仅方法来源ID，fact_ids放盘面/观察。格式报错在当前子任务只修所指字段，合计最多三次提交；不重判。成功后末消息只回receipt-v1，这是交接回执。
4. 主智能体按可见回执的子会话task_id调用task_result领取/确认。request_id、文件UUID、hash都不是task_id；不用task取结果。ID丢失用liuren_adjudication_result(action="locate")，多份时明确选择。需核具体问题才action="read"读完整结果；失败可action="repair"做无歧义格式恢复，不重新派整轮。
5. completed且验收通过，读report后liuren_adjudication_result(action="deliver",task_id=该子会话ID)，取得绑定结果hash的完整report_markdown。主智能体核事实、引用、问项/争点覆盖及正文一致性，复用裁决理由，可调排版，不添决定性理由、不折中改判。needs_input/invalid_output不交付为已完成。

只有needs_input或原报告的具体事实/引用错误，且有真实新增材料，才用retry_context引用前task_id一次补核；具体错误给error_path。主观不同意、显示格式问题、回执简短均不是重裁理由。仍失败保留具体缺口，不由主智能体代裁。已验收结果不会被宿主收尾错误覆盖；重启后仍核归属和hash。

input/output-v2及文件v1并用，各有职责，不是版本冲突。全部专业方法、原书查证、最强反证、正常年命/行年保留；案例库、经验库及其旧缓存不介入。工程检查不证明专业理解或预测效果。详细字段见当前references/deterministic-tools.md。

真实定位/作用/答案修正须有具体证据，不能用格式修复换取用。专法与全部专业义务保留，未定维度保留条件和精度；不自动降档，也不为反折中强断极端。不输出私下推理草稿。原始、修复、验收、领取和交付记录分存output/liuren-flow-state。

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
