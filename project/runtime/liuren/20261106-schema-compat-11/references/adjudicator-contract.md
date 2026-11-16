# 09版文件交接契约

输入输出沿用v2、文件封装沿用v1。09版条件字段、计算记录和程序回填见[唯一详细接口](deterministic-tools.md)。

输入保留schema/request_id/questions/chart/facts/entities/observations/method_materials/focus_issues/unknowns；每问新增tasks，可选computation_requests。deterministic由工具生成。

输出保留schema/request_id/status/scope_review/entity_checks/relation_checks/issue_resolutions/answers/source_conflicts/missing_inputs，另给special_methods/calculations；实体程序字段及computed_relations省略由程序填，不手抄。

模型仍DeepSeek V4.1 Flash、high，slim注册独立新task，完整读完当前文件；没有倾向、排序或已知答案。同材料不重裁，具体错误/新材料才按主方法一次补核重试。返回必须通过事实与结构校验，未定保持具体精度和条件，不自动降档。程序校验不证明术理或预测效果。
