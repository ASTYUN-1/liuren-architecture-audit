# Codex大六壬工作流

本入口共用`.opencode/liuren-active.json`的专业资料、可信修正盘和原书。现行完整步骤只在[本机完整研判流程](本机六壬完整研判流程.md)维护；技能维护源为`integrations/codex/daliuren-codex/SKILL.md`，已装技能应与维护源同步。关键词“使用大六壬进行测算”启用占断；课程、知识维护、流程开发不自动派裁决。

主智能体使用当前模型，中性准备；原生裁决者显式gpt-6.1-sol/high/fork_turns=none，仅接本任务run。主只核事实、引用、覆盖、一致性并完整交付。缺模型/工具明确未完成，不静默回退。OpenCode的DeepSeek与393216额度不移植Codex。

检查`node tools/liuren-codex.mjs status`，请求写UTF-8 JSON并用`node tools/liuren-codex.mjs --request 请求文件.json`执行。packet保留原问/input_review及archive，bind登记原生子；role/read/compute/submit/result/recheck/review/deliver映射见技能[宿主说明](../integrations/codex/daliuren-codex/references/host.md)。裁决正文和回执在output/codex-liuren，同一run的report-recheck保留补核版本；不用新run作为当前补核办法。

核心全读，参考按需。取用职责、旺衰、制救、课体毕法及数量联动以同版judgment-core/专项为准；数字任务最终回执与quantity_reviews相符。普通占断不读两库/旧任务/已知答案，书内例证保留。历史任务沿其绑定规则，不追改；新任务读活动指针。

本桥接不提供操作系统级子进程权限隔离。共享文件读取回执不认证读者身份或语义理解；程序校验不证明术理及预测效果。工程验收不调用付费模型、不声称真实盲测；若要检验模型实际执行稳定性，须另外以无反馈新题验证。
