# 核心交接与独立裁决

准备到可裁决即可：可靠盘、原问、候选取用、必要观察及真实未决处；不先写完整裁决，不为交接穷举矛盾。facts仅补现实事实和来源身份，不复述程序盘；observations避免重复程序状态。focus_issues保持中性，不限定裁决者查漏范围，无真实争点填[]。

主智能体读judgment-core及本问domain；详细通用方法、原书只按真实缺口查。method_modules列确需备查的ID，method_materials交精确来源handoff，quote可省略。程序保留完整引用及hash，单独保存完整存档；裁决入口仅传核心和索引。固定起法直接使用，原书摘要不能当作已核全文。

每问domain/tasks/task_basis依原问，user_requested附逐字request_quote，必要附属任务说明理由。只给占时不增加应期，迟速对比不自动加载完整定期法。课盘传liuren_chart原样archive，不手抄盘。branch仅干支或合法组合，理由放mapping_basis；verification仅method_interpretation/unverified。

1. packet保存后task_prompt原样给新task(subagent_type="liuren-adjudicator")；不传长JSON、旧task_id或background。
2. 裁决者reader默认读核心，首次page=1,page_count=4，按next_call读完核心。完整盘用于查漏，候选可纠正；有具体疑点时reader带material_id读原书，或module读详细方法，用原file_path/sha256。参考可分页，若采用某段为关键依据须理解完整所选段的条件；不遍历来源索引。只核核心传输，不要求所有参考读完。
3. 独立裁关键效力、制救、最强反证及逐问答案；submit完整Markdown正文或自由JSON，缺必要资料可needs_input。无固定专业字段。格式错误只修对应字段或同一正文，最多三次，不重新裁决。成功末消息只回回执。
4. 主智能体按回执task_id调用task_result，读report后result deliver取绑定hash的完整正文；只核事实/引用/覆盖/一致性，忠实交付，不重判。ID丢失先locate，不猜编号；格式故障repair。仅具体事实/引用错误或needs_input且补真实新材料，才按retry_context一次补核。

仅核心完整读取仍无正文且finish=length时，按next_call在原子会话recover一次；不重派，不用reasoning代正文。旧协议文件保持旧读取规则及领取能力。详细接口见references/deterministic-tools.md。
