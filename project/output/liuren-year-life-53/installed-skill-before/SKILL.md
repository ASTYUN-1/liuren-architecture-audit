---
name: daliuren-codex
description: 用户说“使用大六壬进行测算”时启用。在Codex中使用活动专业规则和可信程序盘，准备中性材料后交GPT-6.1 Sol高思考子智能体独立裁决、核对并完整交付；用于占事及同卦续问，知识维护、课程写作和流程开发不自动启动占断。
---

# Codex大六壬占事

项目根`C:\Users\QLMa_\Documents\六壬八字测算`。当前专业规则只认`.opencode/liuren-active.json`，实际操作见项目`docs/本机六壬完整研判流程.md`；已装技能和历史说明不覆盖活动规则。工具调用及输入实例见[宿主操作](references/host.md)。

先`node tools/liuren-codex.mjs status`确认ready。准备读当前judgment-core、adjudication及本问domain，report交付前读；详细方法/原书按真实缺口，时间/数量/年命按问触发。依原问明确当事人、阶段与成功条件，用现有修正程序取得或复用完整可信盘与archive，固定起法直接用，不猜年命、不作出生推命。

按同版核心准备中性候选、必要观察、真实未知和精确来源handoff，不预写完整裁决。packet保存逐字原问、input_review来源身份与真实盘引用，程序生成全盘核心和绑定参考索引。普通占断不检索案例/经验库、旧任务或已知答案；原书及书内例证保留。

将packet返回spawn逐字交原生collaboration.spawn_agent，显式model=gpt-6.1-sol、reasoning_effort=high、fork_turns=none，并用bind登记原生agent_id。缺指定模型或原生工具明确未完成，不静默换模型，不用OpenCode task/DeepSeek接口，不把393216额度移植Codex。工作流开发不因本技能派裁决者。

裁决者只接本任务run，先role再read完整核心，依next_request逐页补齐，显示截断须重读。参考使用同run的module/material_id按需；候选可纠正，从完整盘查漏，依U01—U11和专项首取/条件递补裁关键作用、制救、最强反证及逐问结论。细则以绑定正文为准，不在此复制专业长文。

子把完整自由正文写run/report-draft.md，用submit连audit保存，末消息只回回执。数值问依绑定quantity/quantity-strength/quantity-correction取得真实最终quantity_adjustment回执，复制review进quantity_reviews；不拿基础数或单宫分代最终数。主等待并result领全报告，核事实/引用/覆盖/一致性，完成五项review后deliver，忠实交付，不自行改结论、数值、精度或条件。

有具体报告原句及绑定证据才action=recheck，在同一run由原生同一子智能体followup一次，保留report及report-recheck两版；不另建run、不重新派裁决。格式只修格式；长度中断且无已存正文可原智能体续写一次，仍无正文明确未完成，不用内部推理拼报告。余缺review如实登记并随deliver交付。历史任务沿绑定资料领取，不追改旧packet/盘。

历史C01—C11不是待确认清单；V41-01依用户决定保留现行。毕法/课体按核心作有界辅助，不新增独立裁决。共享文件回执只证明文本输出/保存，不证明读者身份、理解、术理正确或预测效果。
