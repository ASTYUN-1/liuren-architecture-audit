# 本地大六壬工作区接手指引

先读README与目录总索引。当前资料版本只认`.opencode/liuren-active.json`；现行操作见[本机完整研判流程](docs/本机六壬完整研判流程.md)，不从旧版发布说明叠加要求。当前规则已合并，历史逐版入口原文保存在`output/liuren-global-consistency-52/before/`，冻结runtime不就地改写。

用户说“使用大六壬进行测算”时启用daliuren-codex；未发现则读取`integrations/codex/daliuren-codex/SKILL.md`和[Codex流程](docs/Codex大六壬工作流.md)。主智能体准备中性材料，原生子智能体显式gpt-6.1-sol/high/fork_turns=none独立裁决；主只核事实、引用、覆盖和一致性并完整交付。OpenCode用当前配置的DeepSeek/high及393216额度；不把此额度移植Codex。知识维护、课程写作和工作流开发不自动启动占断裁决。

普通研判：原问/当事人/阶段/成功标准→可信全盘→专项职责和首取/条件递补→察类及有效作用/制救→最强反证→按问应期/数量→独立裁决→五项review→必要原会话recheck一次→完整交付。准备读judgment-core、adjudication与本问domain，report交付前读；其余方法/原书按真实缺口查询，不恢复八项通读。理气贯穿，程序只核事实和计算，不选类神、不裁成败；已确认U01—U11直接执行，历史C编号不是待确认清单，V41-01保留现行待用户后续研判。详规以任务绑定runtime正文为准，不在此复制专业长文。

普通占断不检索案例/经验库、旧缓存或反馈；原书及书内例证保留。同卦复用可靠盘和同版已读材料，补新争点；正常年命/行年、长期占事与应期保留，出生推命及出生运限退出。毕法/课体不另开裁决轮次，格名不数票。旺衰数字需工具，单宫不冒充综合；数量任务按quantity、quantity-strength、quantity-correction，最终回执与audit一致。实验参数非古籍原文，工程通过不证明预测准确。

保留现有活动目录tools/tests/runtime/.opencode/案例项目库/经验日志/书籍库/books/knowledge/排盘工具魔改/排盘存档。八字active已迁出；冻结包内历史副本原样保留。外部资料优先用项目内已登记副本，见目录维护说明与路径路由映射。移动资产先列清单、核活动引用和前后SHA256、禁止覆盖并留回滚；不得为清根盲移docs/output或历史证据。不提交密钥、env、客户档案、测试私有及恢复材料；Git根可能在上级，操作只限授权范围。

## 知识维护与课程

书籍提取、旧案例复审和经验归并先读`docs/六壬知识整理-20261102/README.md`及`数据约定.md`，用`tools/liuren_knowledge_workbench.py`核覆盖/待办/引用。原书、卦师断语、旧AI解释、现实反馈、本轮归纳分别保留；入选作答可按子判断保留方法价值，不因一处错整篇作废。卡片检索同时读条件、反证与审查范围；程序切段/hash不等于语义精读，新增归纳保留来源、版本、条件、反证、缺口。新研究放`knowledge/liuren-research/20261102/`，不覆盖原始字节；网站部署另办。

课程工作先读`课程写作/AGENTS.md`、当前台账和专业底稿，保留用户修订，未经接受不标定稿。跨会话记忆仅在用户明确要求时新增简短重要事项，不存秘密。

## 本机运行与产品维护

OpenCode启动检查`python -X utf8 tools/liuren-preflight.py`，新进程首次tool_help(workflow)确认execution_health.ready；Codex检查`node tools/liuren-codex.mjs status`。同一新任务仅派一个裁决者；具体原句和绑定证据才原会话recheck一次。长度停止且完整读取、无报告时按next_call原会话recover一次，不另派、不将内部推理拼正文。保存成功后read→review→deliver，余缺显式交付；主不得折中改判。历史任务沿原绑定协议领取，不追改旧文件。当前仅本机，OpenCode重启新会话加载，Codex新任务读取指针；网站/服务器未发布。

本机默认完整技术报告，沿`docs/本机OpenCode完整输出规则.md`，不套网站隐藏来源或字数限制。参数以工具schema/next_call为准，prepare/read/check为可选工程审计，不是默认必跑全链。

web/mobile/ui-rebuild保留现路径。产品开发先读`docs/跨会话继续开发指南.md`，修改web另遵`web/AGENTS.md`。动态发布、服务与支付须核实，不把设计当已完成；复用配置且不输出凭据。不得缩减专业skill绕过截断；支付以真实资金和服务端证明，测试隔离，管理员连通单不生成报告。通常网站改动只重启web，先核实际任务再动worker；部署及服务器操作依本次授权。
