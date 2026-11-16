# Codex 大六壬工作流

2026-11-08。本入口与 OpenCode 共用 `.opencode/liuren-active.json` 指向的专业资料、现有修正排盘和原书；不另造专业规则，不改 OpenCode 的 DeepSeek 配置或冻结包。

## 使用

在 Codex 中打开本项目，新建或重新打开会话后输入：

> 使用大六壬进行测算。……原问、占时和已知背景……

主智能体使用当前所选模型；裁决者显式 `gpt-6.1-sol`、`high`，使用新上下文 `fork_turns=none`，只接收中性材料与绑定指针。主智能体核事实、来源、覆盖和一致性，忠实交付完整裁决正文。缺工具或不支持指定模型时明确未完成，不静默回退。

技能安装在 `C:\Users\QLMa_\.codex\skills\daliuren-codex\`；维护源位于 `integrations/codex/daliuren-codex/`。自然语言调用关键词为“使用大六壬进行测算”，技能自动选择开启，无需输入内部技能名；`$daliuren-codex` 仍可显式调用。旧会话的技能目录快照不一定刷新，首次建议新开会话。若未发现技能，可明确要求读取维护源的 SKILL.md 执行。

## 工具与记录

- `node tools/liuren-codex.mjs status`：核活动文件hash，返回资料版本和指定子模型。
- `tools/liuren-resolved-chart.mjs`：原有可信修正盘。
- `tools/liuren-codex.mjs --request 请求文件.json`：方法/原书、packet、绑定读取、compute、submit和result适配。详见技能的references/host.md。
- `output/codex-liuren/codex-UUID/`：本次任务指令快照、派发参数、原生子任务标识、读取回执、完整报告和哈希；原有packet生成器另存核心及完整引用档案。
- 只读工程验收说明见 `output/liuren-codex-activation-20261108/`。验收任务明确标为transport-test，不预测现实事件。

原生子智能体由Codex会话工具启动，不使用OpenCode task，不调用独立付费模型API，不新配API密钥。具体账户额度沿用Codex当前账户环境；不据此声称免费或无限额度。DeepSeek专用393216额度不移植到Codex，实际限制由当前宿主模型决定。

## 范围

普通研判沿用31版核心必读、原书按需、完整盘查漏、无案例/经验检索及完整自由报告。详细理气方法保留，并未因宿主迁移修正其尚未解决的条件冲突。已知答案案例不作为新模型盲测。

桥接不替代OpenCode插件的会话权限隔离。共享文件系统的阅读回执只说明文本已输出，不认证读者身份，不证明语义理解；模型与思考档以实际原生spawn参数和运行证据为准。程序仅核传输，不自动审定专业内容。

## 安装与撤回

`integrations/codex/install-skill.ps1 -ValidateOnly` 只检查待安装文件；去掉参数安装三个明确文件，有同名不同内容则停止，禁止覆盖。安装需要用户技能目录的写权限，不改Codex全局模型或配置。

撤回时停用此技能入口；可将本次新建的用户技能文件夹改名移出skills发现目录，先核目标与文件hash。无需回滚OpenCode或专业运行包，既有报告保留。

官方文档页面在本轮网络访问中返回403，未据未打开的页面宣称产品细节。当前原生协作工具已明确列出gpt-6.1-sol及high，并按该可调用接口实现；日后宿主变化时重新验证。
