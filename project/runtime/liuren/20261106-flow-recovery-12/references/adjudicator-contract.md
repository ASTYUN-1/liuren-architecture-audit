# 12版裁决交接契约

输入输出沿用v2，文件封装v1。原生工具schema与程序执行是同一套字段约定，详细接口见deterministic-tools.md。

输入：schema/request_id/questions/chart/facts/entities/observations/method_materials/focus_issues/unknowns。每问tasks必填；task_basis每项含task、origin（user_requested或necessary）、reason，user_requested另给原问逐字request_quote。input_origin与deterministic由程序生成，不手写。仅需有据重裁时给retry_context={previous_task_id,reason,error_path?}。不传初判、权重、排名或已知答案。

输出不再只靠一段自由JSON传输。裁决者调用liuren_adjudication_submit(result=output-v2对象)，通过原生schema及事实/引用/专法校验后取得receipt-v1；最终消息只回该回执。结构化输出保留scope_review/entity_checks/relation_checks/issue_resolutions/answers/source_conflicts/missing_inputs/special_methods/calculations。实体只给id/referent/branch/mapping_review/limits；位置和状态由程序生成，关系computed_relations同理。

special_methods每项公共字段question_id/kind/status/target/basis_ids/fact_ids?/calculation_ids/alternatives/limits/record。basis_ids是实际方法来源ID（E01-E22或M项），fact_ids是盘面/观察/事实ID。timing的候选在record.candidates:[{date,day,event}]；quantity的完成值在record.value。日期和数值须匹配程序计算，择法、轮次、倍率、单位仍由裁决者说明依据。没有相关任务则special_methods=[]，未定给具体limits，不编造完成记录。

提交报错按issues[].path改字段，不改裁决、不重新读全包，最多三次提交。原报告保留，只有无歧义的字段移位/引用分类/不含其他干支的注释可程序归一化。出现混合对象不猜拆、不截字冒充修复。任务结束后主智能体用task_result领取，六壬插件统一验收；结果工具read/repair只读已有产物或做上述格式归一化，不调用模型。

completed且验收通过，主智能体读report后用结果工具deliver取得与已采纳结果hash绑定的完整技术正文。只改排版，不添加决定性理由。needs_input按明确缺项补资料；具体事实/引用错误注明原记录字段路径；确有新材料才一次独立补核。格式失败、同样顾虑或不喜欢结果均不得重新派裁决。
