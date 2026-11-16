# 独立子智能体裁决接口

本模块仅负责把裁决阶段交给 oh-my-opencode-slim 注册的 liuren-adjudicator，不再要求主智能体形成暂定或最终主判。主智能体完成前两阶段、所需应期／数量等专法和 evidence 资料复核后，按 [输入输出契约](../references/adjudicator-contract.md)整理中性材料，调用一次前台 task。

调用：task(subagent_type="liuren-adjudicator", description="大六壬独立裁决", prompt=JSON.stringify(输入对象))。不提供 task_id、不传 background:true。已安装 slim 2.2.18 使用原生 task，没有 background_task 接口；自定义 agent 由项目 .opencode/oh-my-opencode-slim.jsonc 注册。模型固定 opencode-go/deepseek-v4.1-flash，variant=high，reasoningEffort=high；不回退其他模型。

输入只含原问与成功标准、完整可靠课盘事实、已知背景、待核类神和未排序观察、实际已读原法材料及未知。不得夹带主判、倾向、候选排名、分数、真实答案或旧裁决。候选列表按原问顺序，无原顺序按稳定ID；不是按支持度排序。解释性观察标 method_interpretation 或 unverified，不能伪装盘面事实。术理书据已固定在子智能体系统提示中，不需为此次委派再全量搜书。当前仍禁案例／经验两库。

返回 completed 且通过契约检查后，主智能体按 report 完整交付，保留子智能体结论、决定性作用与最强反证的处理及精度。主智能体检查事实／引用／契约，不自行再裁决或折中。若有事实错误、原法遗漏或新输入，补齐中性材料后新建裁决会话；不得以“复核”为名自己改判。needs_input 仅补所列必要缺项；同一输入不重复调用。插件缺失、模型失败或 invalid_output 时明确裁决未完成，不回退主智能体代裁；同一任务最多一次有具体修正的重试，仍失败就报告缺口。

详细专业依据及有条件分歧见子智能体固定书据；本模块不再并行保留旧主智能体裁决流程。历史正文仍冻结于旧 runtime，可回退查阅。独立裁决不等于结论正确，尚无预测效果验证。
