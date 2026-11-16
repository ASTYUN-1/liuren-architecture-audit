# 本地大六壬工作区接手指引

## Codex 专用研判入口

用户说“使用大六壬进行测算”时，在Codex中启用 `daliuren-codex` 技能，无需输入内部技能名；未自动发现时先读 `integrations/codex/daliuren-codex/SKILL.md` 与 [Codex工作流](docs/Codex大六壬工作流.md)。共用当前活动专业资料与程序盘，主智能体准备中性材料，以原生子智能体显式 `gpt-6.1-sol`、`reasoning_effort=high`、`fork_turns=none` 独立裁决。主智能体只核事实/引用/覆盖/一致性并完整交付。OpenCode task/reader/submit/result在Codex中由 `tools/liuren-codex.mjs` 适配；不调用不存在的OpenCode原生工具，不把DeepSeek额度设置套到Codex。此入口不改变下面仍适用于OpenCode的宿主配置；工作流开发、课程写作和知识维护不自动派占断裁决。

默认任务是本机大六壬研判、知识维护或课程工作。先读 [README](README.md) 与 [目录总索引](目录总索引.md)，再按任务进入专项。保留现有目录名称，不因整理而推断专业规则、网站部署或八字迁出已完成。

- 活动核心目录保留原路径：`tools/`、`tests/`、`runtime/`、`.opencode/`、`案例项目库/`、`经验日志/`、`书籍库/`、`books/`、`knowledge/`、`排盘工具魔改/`、`排盘存档/`。
- 当前六壬入口由 `.opencode/liuren-active.json` 指定；八字 active 指针已迁出。旧 `runtime/liuren` 冻结包及历史备份可能仍含八字副本，作为兼容、追溯和回滚资料原样保留，不进入新 active 计划；不得为目录外观改写冻结内容。
- 完整本地研判先读[本机完整研判流程](docs/本机六壬完整研判流程.md)，按当前daliuren及8项共用方法执行一条主线，16专项和时间/数量/年命按问触发。理气贯穿，依占类及事件取用；可信程序盘、神煞位置和固定采用口径直接使用。类象依位置、真假、气态和制救条件参与综合判断，处理最强反证，不凭孤立名象定成败。当前研判不检索案例库、经验库或旧缓存；原书和专业条件保留，知识维护另走专项。同卦复用可靠盘及同版已读资料，只补新争点。当前入口为daliuren/liuren-cases/liuren-extract；仅占事，正常年命/行年、应期与长期占事保留，出生推命及出生运限退出。prepare/read/check仅可选审计；doctor和工程测试不证明专业或预测效果。
- 新增归纳须保留来源、版本、条件、反证和缺口。程序切段、hash 校验、运行成功不能替代语义精读或真实效果验收。
- 课程写作先读 [课程写作/AGENTS.md](课程写作/AGENTS.md)、当前台账和专业底稿，保留用户修订；未经接受的草稿不标成定稿。
- 外部必要资料已按闭包复制，来源见 [目录维护说明](docs/目录维护说明-20261102.md)。优先使用已记录的项目内副本；不复制凭据、系统运行时或缓存。历史旧路径由 [路由映射](docs/路径路由映射.json) 解释，不覆盖来源字节。
- 移动资产须先列明确清单、核对活动引用、禁止覆盖，并保留前后 SHA256 和回滚方法。`docs/`、`output/` 的历史证据与冻结包不得为清根而盲移。
- 不提交密钥、env、客户档案、测试私有目录或恢复材料。Git 根可能是上级 Documents，操作限于任务授权范围。
- 跨会话记忆只记重要、可复用、已确认事项；仅在用户明确要求时新增记忆说明，不保存密码或令牌。

## 大六壬知识维护

处理书籍/题库方法提取、旧案例复审和经验归并时，先读 [知识整理入口](docs/六壬知识整理-20261102/README.md) 和 [数据约定](docs/六壬知识整理-20261102/数据约定.md)，用 `tools/liuren_knowledge_workbench.py` 检查覆盖、待办及引用有效性，再接续已登记的阅读范围。原书、卦师断语、旧AI解释、现实反馈与本轮归纳分别保留；入选作答即使反馈身份不明仍有方法参照价值，按子判断保留可取内容，不能因一处错误整篇作废。

本地 `search-experience.py` 与 `search-cases.py` 已接入附加规则/审查，使用时同时阅读条件、反证、审查作用范围及保留价值。规则卡的原文校验不等于预测效果验证；程序切段不等于语义精读。新卡与审查放 `knowledge/liuren-research/20261102/`，原始来源不得被事后修正覆盖，冻结运行包不就地改写；网站部署另按任务办理。

## 本机 OpenCode 的最终输出

在本目录直接使用本机 OpenCode 研判时，遵循 [本机完整输出规则](docs/本机OpenCode完整输出规则.md)。本机默认完整技术报告，暂不启用 `wenheng-public-output`，不套用客户公开报告对案例、来源、路径、评分及方法依据的信息隐藏要求；保留实际依据、反证、条件与缺口的可核对说明。此设置仅针对本机会话，网站受限任务继续使用其原有交付规范。

## 保留开发区：问衡网站、APK 与运营

`web/`、`mobile/`、`ui-rebuild/` 按用户决定保留现路径。处理网站开发、部署、支付、AI 工作流或运营问题时，先读 [跨会话继续开发指南](docs/跨会话继续开发指南.md)，再按任务读取其中最新专项记录；修改 `web/` 还须遵循 [web/AGENTS.md](web/AGENTS.md)。

- 动态服务状态、发布版本、外部支付通道须重新核实；旧文档包含已被覆盖的历史状态，不把设计方案当完成证据。
- 用户偏好低成本落地、遇卡点继续推进独立任务；复用既有配置与资产，不重复索取可安全复用的配置，不输出凭据。
- 不缩减或覆盖原 skill 以绕过输出截断；保留 AI 规则准确性、资料版本和轨迹缺口等技术债，工程交付通过不等于术理验收通过。
- 支付成功必须由真实资金及服务端核对证明，不伪造生产订单或权益。测试使用隔离数据库；¥0.10 管理员连通性单不发报告或追问。
- 既有部署记录为旧电脑负责业务、数据库和 AI，香港 VPS 负责公网入口；操作前核实当前实际拓扑，保留其他网站和中转服务。通常网站变更只重启 web，先核实任务再动 worker。

## 本机现行裁决分工

主智能体准备中性材料，独立裁决者查漏并裁关键作用和结果；返回后主智能体核事实、引用、问项覆盖和一致性，忠实交付，不重新折中权衡。具体错误或真实新材料按现行协议一次补核，格式差异不重裁。可信程序事实及固定神煞取法直接复用，程序不裁吉凶。完整工具接续见[高效执行](docs/本机六壬高效执行.md)，专业条件以活动runtime正文为准，不叠加旧版历史补丁。

本次20261107-slim-29仅本机OpenCode生效；网站、APK及服务器未发布。

28版：裁决请求不再传max_tokens/maxOutputTokens，取消项目65536覆盖及宿主继承额度；服务端仍有模型/上下文上限，high保留。task_result无公开末消息时，用liuren_adjudication_result(action="read",task_id=原子会话ID)领取已存结果或失败。仅完整读完且finish=length、无公开报告时，按next_call用recover在同一子会话续写提交一次；不新建裁决、不把reasoning转成正文。仍无正文则明确未完成，不循环领取/重派。重启本机OpenCode后，workflow的features.provider_default_output_budget与bounded_same_session_recovery均须为true。

本机29版执行与排障以[稳定运行指南](docs/本机六壬稳定运行指南.md)为准。启动可用tools/liuren-preflight.py；workflow须execution_health.ready=true，旧进程不新派发。插件固定2.2.18；未初始化的AOCI仅在本项目暂停，其他MCP保留。


30版额度修正：本机裁决显式请求max_tokens=393216，模型deepseek/deepseek-flash与high保留。此前省略客户端额度会回落DeepSeek high默认64K，不能再以provider_default_output_budget=true作为当前要求。workflow须execution_health.ready=true、features.explicit_output_budget=true且requested_max_output_tokens=393216。只扩大生成额度，不改变专业方法或交接链；重启OpenCode加载。


31版当前执行规则（覆盖上方历版关于8项/14项通读和裁决全部材料必读的要求）：主智能体准备读judgment-core、adjudication及本问domain，report在交付前读。原positioning/liqi/structure/void/shensha-use/movement及全部专业方法全文保留，按真实条件缺口、反证冲突或摘要不足定点查。原书只交必要handoff备查，不复述整盘、不为交接先写完整裁决。程序保存紧凑核心与hash绑定完整存档；reader默认完整核心，参考用material_id（含固定E01—E22）或module按需查。只强制核心完整传输；参考不是待办清单，必要段落查明条件再用于决定性判断。候选取用可纠正，完整盘用于独立查漏。无两库、原书来源身份、完整自由报告及最强反证保留。工具契约liuren-tools-31，workflow须execution_health.ready=true及features.core_handoff/on_demand_sources=true。模型deepseek-flash/high、max_tokens393216不变；只在本机，重启加载，旧任务按原文件协议领取。


32版历史记录（现行33版已修订待确认登记；20261108-unified-32，覆盖旧指令中相反的专业摘要）：活动judgment-core完整载入U01—U11，主智能体准备和独立裁决者共同执行。喜旺恶衰、直接临生合与外来扶助、日干天干十二长生/支将五行十二气、制救、天时地利、空亡综合效应、四建分工及时间变化统一。已定规则不再作两派争点；真实未定边界见pending-conflicts的C01—C11。主智能体返回核对包含U口径一致性；具体错误附原句、U编号及绑定证据，依宿主一次补核协议处理，不自行折中改判。工具契约仍liuren-tools-31，模型与额度不变。仅本机；OpenCode重启后新会话加载，新Codex任务读取新指针；历史任务沿原绑定版本。记录见output/liuren-unified-rules-20261108/更新与验收说明.md。


33版解释与矛盾登记修订（20261108-clarified-33，覆盖32版相反的“待确认”措辞）：贪生停用指类神对日主的作用受限，财、父母、鬼分别释义；通类/分类分层，胎爻专项依北海（干支胎同重、土胎子午两处），应期视用/视末按原文明示阶段。主、子智能体共同按U11筛选真正同条件互斥；明确条文自行解释执行，不要求用户再确认。C01—C11已逐项关闭或重新分类，不再作为待确认清单；来源措辞、程序取法和文字校勘另记。工具契约、宿主模型与额度不变，仅本机；OpenCode重启新会话加载，Codex新任务读取活动指针，历史任务沿原绑定版本。记录见output/liuren-clarified-rules-20261108/矛盾复核与原文入口.md。


34版单宫旺衰接入（20261109-palace-strength-34）：34版单宫旺衰：默认分数仅为单宫直接关系的旺衰，5/2.5均非失用阈值，弱仍可作用。明确取用和跨宫作用依据后，必须调用liuren_compute(action=strength)补算，不自行加减、不重复扣空、不全盘五行联算。先读共用judgment-core，接口见deterministic-tools；三合/半合/三会数值继续暂缓。 仅本机，新OpenCode进程/新Codex任务使用新绑定；历史包和原盘不改。详细计算及回滚见output/liuren-palace-integration-20261109/接入说明.md。


35版本机工具升级（20261109-deterministic-tools-35）：35版确定性工具层：工具只查盘、查表、计算和枚举时间，AI依原法取用、选法与裁决。取数/取象先methods查方法，按quantity_method/imagery调用；evaluation接日历与旺衰，不裁应期。空亡系数沿用34版，三合等数值暂缓。主、子共读judgment-core；详见deterministic-tools。 使用说明见docs/确定性工具使用说明-35.md；回滚见output/liuren-tool-upgrade-20261109/rollback.py。


36版关神接入（20261109-guanshen-36）：36版新增季关神S33：春丑夏辰秋未冬戌；采用规则共39条，原38条及22停用名不变。关墓阻隔、冲解及掌管仓库吉用按原段取用，寡宿同表不重复计证。仅本机，新任务绑定；原盘与旧冻结包不改。 原文复核与回滚见output/liuren-guanshen-20261109/。


37版本机双Sol试用（20261109-sol-37）：OpenCode主智能体、独立裁决者及活动辅助智能体统一conpera/gpt-6.1-sol、high。取消DeepSeek专用393216输出额度，由当前提供方和宿主决定；workflow应显示explicit_output_budget=false、requested_max_output_tokens=null。专业规则沿用36版，历史包不改；重启OpenCode并新建会话加载。配置与回滚见output/opencode-sol-20261109/。


38版本机OpenCode裁决模型对照（20261109-deepseek-child-38）：仅独立裁决者切换为deepseek/deepseek-flash（本机显示DeepSeek V4.1 Flash）、high，恢复该裁决者既有393216生成上限。主智能体保留用户所选模型，不要求与裁决者相同。专业方法沿用37版；Codex原生裁决仍为Sol/high，网页内测与正式服务不变。重启OpenCode后新建任务加载；历史任务不重派。配置、验收及回滚见output/opencode-deepseek-child-20261109/。


39版一致性核对：新任务保留原问与input_review来源身份；子报告附简短audit，登记关键作用、最强反证与真实计算覆盖。局部补算不能冒充综合结果。主智能体read核对后用review登记事实身份、职责阶段、计算范围、反证、逐问约束五项；有具体原句和绑定证据才用原子会话recheck一次，保留前后报告，未解决缺口显式交付，不另派或自行改判。程序不选类神、不裁成败、不设分数阈值，正文仍自由表达。专业方法与模型选择沿用38版；网站未发布。接口见docs/本机六壬一致性核对-39.md。
