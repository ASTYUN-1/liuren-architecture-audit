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

普通研判沿用31版核心必读、原书按需、完整盘查漏、无案例/经验检索及完整自由报告。详细理气方法保留，已确认U口径随共用核心执行；历史C01—C11按33版关闭或重新分类。已知答案案例不作为新模型盲测。

桥接不替代OpenCode插件的会话权限隔离。共享文件系统的阅读回执只说明文本已输出，不认证读者身份，不证明语义理解；模型与思考档以实际原生spawn参数和运行证据为准。程序仅核传输，不自动审定专业内容。

## 安装与撤回

`integrations/codex/install-skill.ps1 -ValidateOnly` 只检查待安装文件；去掉参数安装三个明确文件，有同名不同内容则停止，禁止覆盖。安装需要用户技能目录的写权限，不改Codex全局模型或配置。

撤回时停用此技能入口；可将本次新建的用户技能文件夹改名移出skills发现目录，先核目标与文件hash。无需回滚OpenCode或专业运行包，既有报告保留。

官方文档页面在本轮网络访问中返回403，未据未打开的页面宣称产品细节。当前原生协作工具已明确列出gpt-6.1-sol及high，并按该可调用接口实现；日后宿主变化时重新验证。


32版历史记录（现行33版已修订待确认登记；20261108-unified-32，覆盖旧指令中相反的专业摘要）：活动judgment-core完整载入U01—U11，主智能体准备和独立裁决者共同执行。喜旺恶衰、直接临生合与外来扶助、日干天干十二长生/支将五行十二气、制救、天时地利、空亡综合效应、四建分工及时间变化统一。已定规则不再作两派争点；真实未定边界见pending-conflicts的C01—C11。主智能体返回核对包含U口径一致性；具体错误附原句、U编号及绑定证据，依宿主一次补核协议处理，不自行折中改判。工具契约仍liuren-tools-31，模型与额度不变。仅本机；OpenCode重启后新会话加载，新Codex任务读取新指针；历史任务沿原绑定版本。记录见output/liuren-unified-rules-20261108/更新与验收说明.md。


33版解释与矛盾登记修订（20261108-clarified-33，覆盖32版相反的“待确认”措辞）：贪生停用指类神对日主的作用受限，财、父母、鬼分别释义；通类/分类分层，胎爻专项依北海（干支胎同重、土胎子午两处），应期视用/视末按原文明示阶段。主、子智能体共同按U11筛选真正同条件互斥；明确条文自行解释执行，不要求用户再确认。C01—C11已逐项关闭或重新分类，不再作为待确认清单；来源措辞、程序取法和文字校勘另记。工具契约、宿主模型与额度不变，仅本机；OpenCode重启新会话加载，Codex新任务读取活动指针，历史任务沿原绑定版本。记录见output/liuren-clarified-rules-20261108/矛盾复核与原文入口.md。


34版单宫旺衰接入（20261109-palace-strength-34）：34版单宫旺衰：默认分数仅为单宫直接关系的旺衰，5/2.5均非失用阈值，弱仍可作用。明确取用和跨宫作用依据后，必须调用liuren_compute(action=strength)补算，不自行加减、不重复扣空、不全盘五行联算。先读共用judgment-core，接口见deterministic-tools；三合/半合/三会数值继续暂缓。 仅本机，新OpenCode进程/新Codex任务使用新绑定；历史包和原盘不改。详细计算及回滚见output/liuren-palace-integration-20261109/接入说明.md。


35版本机工具升级（20261109-deterministic-tools-35）：35版确定性工具层：工具只查盘、查表、计算和枚举时间，AI依原法取用、选法与裁决。取数/取象先methods查方法，按quantity_method/imagery调用；evaluation接日历与旺衰，不裁应期。空亡系数沿用34版，三合等数值暂缓。主、子共读judgment-core；详见deterministic-tools。 使用说明见docs/确定性工具使用说明-35.md；回滚见output/liuren-tool-upgrade-20261109/rollback.py。
