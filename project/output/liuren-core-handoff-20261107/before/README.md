# 本地大六壬工作区

这里用于本机排盘、专业研判、知识整理和课程写作。为兼容既有工具，文件夹仍叫“六壬八字测算”。现有网站与手机产品源码保留在原路径，产品开发从独立入口接续。

| 要做的事 | 入口 |
| --- | --- |
| 先了解目录与资料位置 | [目录总索引](目录总索引.md) |
| 本机完整技术报告与输出边界 | [本机 OpenCode 完整输出规则](docs/本机OpenCode完整输出规则.md) |
| 继续六壬知识整理、案例复审 | [知识整理入口](docs/六壬知识整理-20261102/README.md)、[数据约定](docs/六壬知识整理-20261102/数据约定.md) |
| 查看专业规则、反证与已登记资料 | [knowledge](knowledge/)、[经验日志](经验日志/)、[案例项目库](案例项目库/) |
| 排盘与已存课盘 | [排盘工具魔改](排盘工具魔改/)、[排盘存档](排盘存档/README.md) |
| 课程写作 | [课程写作规则](课程写作/AGENTS.md)；先读该目录当前台账与专业底稿 |
| 公众号文章与配图 | [运营资料/公众号](运营资料/公众号/README.md) |
| 网站、APK、部署与运营维护 | [跨会话继续开发指南](docs/跨会话继续开发指南.md)，修改 web 时另读 [web/AGENTS.md](web/AGENTS.md) |
| 找迁移前的文件 | [路径路由映射](docs/路径路由映射.json)、[归档说明](归档/README.md) |

## 本机使用

在本目录打开 OpenCode。技能和活动配置位于 `.opencode/` 与 `opencode.json`；工作流与资料版本以当前配置和本轮运行记录为准。默认交付完整技术报告，保留来源、条件、反证与缺口。

本轮六壬活动指针为 [.opencode/liuren-active.json](.opencode/liuren-active.json)，指向 `20261107-slim-30`；八字 active 指针已迁出。旧 `runtime/liuren/` 冻结版本和历史备份可能仍有八字副本，按兼容、追溯和回滚用途原样保留，不进入新的活动读取计划。

本机默认从`daliuren`按[完整研判流程](docs/本机六壬完整研判流程.md)执行原问与可信盘→依问取用→综合作用和最强反证→独立裁决→核对交付。共用资料8项，16占类专项及应期、数量、年命按问触发；直接使用可信程序盘与固定神煞结果，同卦复用已核材料。三个入口为daliuren、liuren-cases、liuren-extract，普通研判与知识维护分开。精简不代表预测准确率等价已经验证。

当前无两库对照只关闭本次案例库、经验库调用；方法模块、原书和原有书内例证保留。普通研判不执行search-cases、search-experience或retrieve，也不回读旧检索缓存。原基线保留，可按本轮发布记录回切比较。

`tools/liuren-workflow.py` 保留为可选工程审计工具：

```powershell
python -X utf8 tools/liuren-workflow.py doctor
python -X utf8 tools/liuren-workflow.py prepare --input INPUT.json --out RUN
python -X utf8 tools/liuren-workflow.py read --run RUN --id ID --page 1
python -X utf8 tools/liuren-workflow.py check --run RUN --record JUDGMENT.json
```

`INPUT.json`、`RUN`、`ID`、`JUDGMENT.json` 是可选审计中的占位符。历史输入结构见 [20261102 工作流说明](output/liuren-consolidation-20261102/workflow/使用说明.md)，其中“唯一主路线、必须重新 prepare”的要求不再适用于本机默认研判。程序页码仅表示内容被输出，check 不证明专业判断正确，也不约束最终判断原文。

`doctor` 只读检查本机六壬运行包、知识数据和必要依赖；也可双击 `verify-system.bat` 或运行 `verify-system.ps1` 调用同一入口。旧验证脚本的原件在 [融合前备份](归档/配置与旧说明/融合前-20261102/)，不再按旧混合包启动八字服务。

需要图形排盘时，运行 `node 排盘工具魔改/serve.js`（或双击 `start-server.bat`），再打开 http://localhost:3456 。服务只应按本次需要启动；端口占用时先检查已有进程。排盘字段和运行通过不代表术理或预测效果已经验收。

## 资料与历史

`书籍库/`、`books/`、`案例项目库/`、`经验日志/`、`knowledge/` 保持原路径；新复制的依赖有逐文件来源与 SHA256 清单，见 [目录维护说明](docs/目录维护说明-20261102.md)。原书、原始断语、旧 AI 解释、现实反馈与本轮归纳分开保留。历史材料中的旧路径按路由表解释，不改写原文来制造一致。

`docs/` 与 `output/` 中引用密集的来源、发布记录和验收证据继续保留，分别见 [docs 分类索引](docs/目录分类索引.md) 和 [output 分类索引](output/目录分类索引.md)。原安装包和旧说明已进入 `归档/`。八字专项的打包、解压验证和迁出状态只认其最终验收记录，不再用本页旧版的八字启动命令作为活动入口。

本次目录整理不发布网站、不运行付费模型、不验证真实占断效果。旧 README 与 AGENTS 的逐字节备份位于 [接续入口备份](归档/配置与旧说明/接续入口-20261102/)。

本机独立裁决仍由deepseek/deepseek-flash、high承担。现行操作只见[高效执行](docs/本机六壬高效执行.md)，本轮[生效与回滚说明](output/liuren-slim-activation-20261107/生效说明.md)。本次只切本机入口，网站和服务器未发布。

27版修复归档引用在排盘与计算/裁决工具之间的字段兼容，详见[流程复验报告](output/liuren-slim-flow-validation-20261107/流程复验报告.md)。仍仅本机生效。

本机28版取消项目裁决输出额度，增加原子会话正文恢复；说明见[本次修复](output/liuren-stalled-child-repair-20261107/修复说明.md)。网站未发布。

本机29版执行与排障以[稳定运行指南](docs/本机六壬稳定运行指南.md)为准。启动可用tools/liuren-preflight.py；workflow须execution_health.ready=true，旧进程不新派发。插件固定2.2.18；未初始化的AOCI仅在本项目暂停，其他MCP保留。

本机30版显式申请裁决生成额度393,216 tokens，保持deepseek-flash/high，修正省略参数回落服务端64K默认值的问题。重启后新请求生效；实际长裁决仍待验证。说明见[额度修改说明](output/liuren-token-limit-audit-20261107/修改说明.md)。
