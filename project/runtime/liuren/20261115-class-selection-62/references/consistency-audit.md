# 判断依据、一致性附件与实质复核

本页服务于共用judgment-core主线，不另建裁决体系。程序核原问引句、声明、ID、来源和真实回执；模型核题意、取用、有效作用、制救及数量依据是否成立。正文自由表达，不提交私下推理，不以工程通过声称判断正确。

## 准备交接

input_review逐问保留request_quote、success_basis、stage_origin与stage_basis；来源为user_explicit的阶段须附原问连续引句。facts逐条登记用户明确、推断或未知，程序换算不冒充用户输入。数量限制有依据才登记max_candidates/limit_quote。

新路线任务每问带route：event、focus、primary_entity_ids、selection_basis、time_scope。它保存题意、分析侧重、首取/递补理由及结果形成/评定/通知/兑现分工；主候选须关联同一子问，关系题明确双方，整体题可无单类。程序不选择类神，独立裁决可以说明真实纠错依据后改正。

原问、可信全盘、同版方法和候选一起绑定。观察不预写成败，focus_issues只留本题真实缺口；同条件已定首取不重新开放为择旺争论。OpenCode原问由宿主读取，Codex逐字传入；不将共享文件系统和主填报视为读者身份认证。

## 裁决附件

submit的audit沿现有schema，字段用tool_help、consistency_guide为准，不从历史示例复制。questions逐问登记原问/阶段/成功标准复核、answer_quote及最强反证处理。relations只登记决定性支持、阻碍和制救，说明施受对象、依据、作用环节、采用范围、处置及公开原句；无效或局部有效均解释原因，不只登记正面作用。

basis_refs用program、core、domain:本问、绑定材料/观察/事实ID、route:问ID及已绑定E01—E22。补核还可用input和真实计算回执hash。引用存在不等于应用正确。

calculations登记真正引用的strength回执及数值原句。local保留局部覆盖提示；combined须覆盖已声明且切题有效的数值关系，不能把分开的局部支持称为综合链。未登记关系仍可能漏掉，定性刑冲不强行量化。

quantity_reviews复制最终quantity_adjustment的review，补question_id、final_receipt_sha256和report_quote。基数、算法、量级、已含气态/空减和后续步骤分别核；source保留适用原法的后续修正，experimental用真实without_void，序数按专法。缺步为unresolved并说明实际尝试，不为满足字段造数。免空减例外和进位按quantity-correction绑定evidence；原句与本题的适用性仍须核查。

## 主智能体五项复核

1. input_fidelity：原问实际事件、成功标准、事实身份是否完整保留。
2. role_stage_consistency：逐问对route核专项分支、主类职责及时间口径；首取是否在实判中生效，辅助类是否通过真实作用参与，而不是接管另一职责。
3. calculation_scope：实际数法和基数是否适用；是否漏走或重复修正，量级是否有独立依据；单宫和综合范围与回执相符。回执一致不能替代这些依据。
4. counterevidence：反证与支持是否按同一标准审查；施受双方、通路、救谁制谁、解除范围及时序是否足够支持取舍。
5. answer_constraints：逐问直接结论、数值/等级/精度、条件依赖及用户数量限制是否完成，有无后文无据撤回。

每项用当前report_sha256、report_quote、basis、evidence_refs定位，无法确认标unresolved。职责项覆盖各route:问ID。当前工具检查不能判定文字理由是否专业充分，主不能仅因audit.ok或算术相符就全部勾checked。

具体题意错配、违反已采用首取、制救未成立、无据量级或空减例外，均可用报告原句与绑定证据送原会话recheck一次。该次优先处理实质问题，不预先指定保留某一结论或数字；原裁决者可有据保留或修正。引句/标签错误只修相应字段，不重跑整盘、不另派，主不折中改判。补核后未解如实review并deliver，保留completed_with_gaps。

旧任务按原绑定政策领取，不追溯强加route、evidence或新附件。没有数值任务不增数量表格；本规则不增加裁决轮次、不恢复案例/经验检索。工程检查不证明语义遵守或预测准确。
