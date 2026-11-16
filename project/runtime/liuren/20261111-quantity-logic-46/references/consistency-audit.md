# 第39版：原问、关键作用与计算回执核对

范围：本机OpenCode及共用Codex适配器。主智能体保留用户选择，OpenCode裁决者仍为DeepSeek Flash/high，Codex原生裁决仍为Sol/high。网站、服务器和已有任务沿原协议。

本版提高执行可核查性，不建立新的吉凶规则、不设分数成败阈值、不增加投票裁决者。程序不保证发现所有语义遗漏或提高预测准确率。

## 执行路线

1. 主智能体保存原问，填写`packet.input_review`，每问覆盖成功标准依据、阶段身份；每条补充现实事实区分用户明确、推断、未知。原问及消息hash进入绑定包。OpenCode原问来自宿主消息，Codex来自主智能体逐字提供，后者不冒充宿主认证。
2. 中性交接：候选、观察和开放争点可纠正，不能先设“偏成”或已通过某阶段。`neutrality_review`是模型核对记录，程序无法凭此证明中性。
3. 子智能体从完整盘查漏，报告正文自由表达，另给简短`audit`。只登记决定性作用与最强反证，不枚举全盘；关系有效性、取用与制救仍由模型判断。
4. 被正文引用的strength数值绑定真实回执。计算响应新增`calculation_receipt`；需要查完整回执时用`liuren_adjudication_audit(action="receipts")`。`action="check"`可在提交前核对正文与附件，无模型调用。
5. submit保存正文与附件。传输完成和一致性通过分别记录；即使附件缺失或发现错误也保留原报告，不掩盖失败。
6. 主智能体read后核对五项，发现具体错误附原句、绑定证据和补核请求，调用result recheck。只向原子会话补核一次，保留修订前后产物；新题派发与原报告恢复机制不变。
7. 主智能体用result review提交五项记录，然后deliver。未登记review不能正常交付；未解决问题自动附在报告前，标记`completed_with_gaps`。主智能体不能通过勾选“已检查”消除程序发现的数值/引用错误。

五项check ID：`input_fidelity`、`role_stage_consistency`、`calculation_scope`、`counterevidence`、`answer_constraints`。状态为`checked`或`unresolved`；每项附当前报告逐字引句与核对依据。这里只记录公开证据摘要，不要求私下推理过程。

## 输入附件

`input_review`示意（占位文字不能当真实资料）：

```json
{
  "questions": [{
    "question_id": "Q_1",
    "request_quote": "用户逐字子问",
    "success_basis": "本问成功标准的来源和拆解依据",
    "stage_origin": "unknown",
    "stage_basis": "用户没有提供已进行到哪一阶段"
  }],
  "facts": [],
  "neutrality_review": "未预设结果；阶段未知保留未知"
}
```

`user_explicit`阶段的stage_basis必须是原问逐字片段；`inferred`只能作为推断。facts每条登记`{fact_id,origin,source_quote?,basis}`，不能把程序按给定参数算出的结果当作用户确认输入。“97男”推算年命须标推断及历法约定，不能写成用户核实。

职业等候选存在原问“限二”等明确限制时，对应问题另填`max_candidates:2,limit_quote:"限二"`。程序核数量，候选是否每项又塞入很多行业由主智能体检查。

## 裁决附件

精确原生schema见`liuren_tool_help(topic="packet")`及submit工具；紧凑说明也随完整核心交给裁决者。`audit.schema="liuren-consistency-audit-v1"`，包含：

- `questions`：每问的原问引句、阶段身份、成功标准复核、报告答案引句、候选列表和最强反证处理。
- `relations`：仅关键作用；程序对象如`T:寅`、`S:丙`，列作用依据、作用到哪个结果条件、有效/受限/排除/未决及制救说明。role为support/obstruction/rescue/context，disposition为used/limited/excluded/unresolved。
- `calculations`：仅正文引用的strength回执，列receipt_sha256、scope(local/combined)、relation_ids、report_quote、score_claims。分数引用用真实回执result内JSON Pointer，例如`/actors/0/adjusted`。
- `omission_review`：简述完整盘查漏及限制，不把主交接当封闭范围。

basis_refs可用`program`、`core`、`domain:本问domain`、绑定材料/观察/事实ID和固定E01—E22；不接受其他任务的引用。补核finding还可引用`input`和本任务计算回执sha256。

`local`声明会把同问相关关键关系未进入计算情景的情况提示给主智能体；它仍只代表局部情景。`combined`必须覆盖模型已登记、与该情景对象相关、可数值处理且实际采用/受限的关键作用。刑冲等定性内容不强行量化；未登记关系仍可能漏掉，程序无法代替全盘语义查漏。

## 主智能体review与一次补核

review参数为`{report_sha256,checks:[{check,status,report_quote,basis},…]}`，须完整覆盖五项。hash由result read返回，修订后旧review失效。

recheck参数为`findings:[{check,report_quote,evidence_refs:["program"],evidence,request}]`；附具体证据缺口，不以“不喜欢结论”派发。OpenCode由插件调用原子会话，仍用既定裁决模型；Codex action=recheck返回原生`collaboration.followup_task`指令，只复用已bind的原智能体。不新建裁决任务。

补核失败、模型未提交修订或补核后仍有问题，保留缺口并交付带提示的原样报告，不循环补核，不由主智能体改判。

## Codex映射

保持原run：

- `action=audit,mode=receipts`：取本run真实回执。
- `action=audit,mode=check,result=正文,audit=附件`：检查。
- `action=submit,report_file=正文绝对路径,audit=附件`：保存。
- `action=result`：读取正文、附件、检查结果和报告hash。
- `action=recheck,findings=[…]`：登记唯一补核，按返回followup给原子智能体发送。
- `action=review,review={…}`：登记五项核对。
- `action=deliver`：取得最终正文及无法消除的缺口提示。

旧run不追溯强加新附件。共享文件系统与主智能体填报不构成读者身份认证；核对记录不等于语义正确性或预测效果证明。

## 验收原则

使用历史日志验证是否发现关系覆盖、阶段来源和输出限制等具体缺口。真实反馈不进入裁决提示，不把“必须预测失败”写成测试断言。新题准确度比较须固定中性交接包、资料、参数和成功标准，另行开展盲测。

## 数值/序位的现有五项核对

input_fidelity核原问是否被擅改为“若落选”等条件；calculation_scope核对象、数表、算式与修正是否真正完成，能否落到所求数值，不以只查目录算完成取数；answer_constraints核点值/区间及等级的形成依据。不因区间较宽就当有据，不以人数中位或研究指数直接定位。发现具体问题仍只走原有一次补核，不增加强制字段、裁决轮次或数法投票。
