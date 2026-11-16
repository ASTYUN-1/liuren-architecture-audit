# 文件式独立裁决、结构化提交与恢复

事件定位是裁决前提：每问domain必填，考试/疾病用actor_entity_id绑定考生/患者且branch为占日干。漏读分类占先补对应模块，不能跳过或换domain绕过。裁决者收到M_EVENT_POSITIONING及M_DOMAIN_*完整正文后，先对照原问核现实对象，再裁生克；不得把代问者设为日干后用六亲递推当事人。

主智能体核原问、可靠盘、取用候选、状态关系与必要原法，准备到可裁决，以focus_issues列中性争点，不夹带初判、排序或已知答案。裁决者对照完整盘查错漏，裁关键作用与各问结论；主智能体返回后核事实和覆盖并忠实交付，不重做全盘权衡。


12版执行规则：主智能体准备中性材料，独立裁决者裁关键作用，主智能体忠实交付。每问tasks必填，task_basis逐项注明user_requested及原问逐字request_quote，或necessary及具体理由；只给占时不等于问应期，不为完整性默认增加应期/取数。程序保留原问并提示明确亲属标签冲突，不替代专业取用。日干不能改成寄宫支来过校验。

先按当前路由读必查与触发专项；同版同上下文已读可复用。packet保存前核准备阶段必查回执，缺哪项只补哪项。report在交付前读。来源按行段/hash交程序装配，quote可省略；不要反复手抄引文。branch只放干支/纯支组合/戊（寄宫巳），注释放mapping_basis或mapping_review；verification只用method_interpretation/unverified。

packet返回task_prompt原样交新task，不提供task_id，不用background:true，不把上下文塞入task。裁决者逐页读完紧凑文件，使用liuren_adjudication_submit提交结构化结果，末消息仅返回工具回执。格式报错只在原子任务内修对应字段，保持裁决内容不变，最多三次提交；不得重新全盘权衡。含混对象不由程序猜改。程序保留原报告、字段错误、校验产物及hash。

主智能体收到结果后先task_result(task_id=子会话ID)领取并确认，领取同样经过六壬验收；不要用task取结果。失败用liuren_adjudication_result(action=read或repair)查看具体缺口/无歧义格式修复，不能再派整轮裁决。只有needs_input，或原报告中具体事实/引用错误（retry_context.error_path），并补入真实新材料，才可retry_context引用前task_id一次补核；仍失败明示未完成。同材料重复派发由程序拦截。

completed且验收通过，读report后调用liuren_adjudication_result(action=deliver,task_id=子会话ID)，取得绑定结果hash的完整report_markdown，直接交付技术正文；可调排版，不改结论/精度/条件、不添决定性理由。它保留取用、关键作用、反证、争点、应期取数记录与来源。工程通过不证明专业或预测正确。经验库、案例库仍不介入，原书、全部专业方法和正常年命/行年保留。


真实定位/效力/答案修正必须有具体证据；修格式不得将日干换成寄宫、将组合任意拆支。原始结果与修复记录分别保存，不用最新一份覆盖历史。已产出、已领取、已验收和已交付分别记录。状态存于output/liuren-flow-state，主子会话及文件hash绑定；重启后领取已保存结果仍核归属与hash。

input/output-v2、文件v1保持；新增task_basis、input_origin（程序生成）、retry_context。实体位置/状态和关系枚举由程序回填。应期/数量按原问声明后仍装入完整专法并要求special_methods；basis_ids只放方法来源，fact_ids放D_*、观察及事实。candidates和value均在record下。

详细字段见references/deterministic-tools.md与references/adjudicator-contract.md。未定维度保留条件和精度，不自动折中、降档，也不为反折中强断极端；不输出私下推理草稿。


13版结果交接：task及task_result向主智能体返回可见receipt-v1回执，task_id必须是该回执中的子会话ID；request_id、文件UUID和hash都不是task_id。不要从隐藏metadata找ID，不重复返回完整结构化报告。先按回执next_call调用task_result，再读report并调用liuren_adjudication_result(action="deliver",task_id=回执.task_id)。如旧任务的ID丢失，先liuren_adjudication_result(action="locate")；仅当前主会话恰有一份已保存裁决时自动定位，多份则返回候选并明确选择，不猜编号。格式失败只修字段，不重裁；需要核具体依据才action="read"获取完整结构化报告。子任务最终只回成功回执是正常交接，不是最终用户报告。
