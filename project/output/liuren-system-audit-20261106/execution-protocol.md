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
