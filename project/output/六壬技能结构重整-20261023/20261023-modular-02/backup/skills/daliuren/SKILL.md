---
name: daliuren
description: 大六壬排盘、起课、断课、解课、占卜、四课三传与单事研判的统一入口；使用北海三步法与壬归融合增强版。出生推命、案例归档及资料提取分流到对应维护入口。
---

# 本地 OpenCode 六壬融合版：daliuren

已启用版本：`20261023-local-active-01`；方法包：`da713e002642e279bbf04ae8cc4fbcf5d86f4234c8c87396c1e19f6a2d325648`（enhanced）。

单事研判先完整读取[判断核心](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/core.md>)、[证据纪律](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/evidence.md>)及[神煞基础](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/mechanisms/shensha.md>)，固定原问、对象、阶段和成功标准；再按问项读取对应占类及触发的机制。按同一版本复用已完整读过的内容。

本地执行：已有可靠程序 facts 时直接使用；需要起课或仅排盘时，先完整读取[本地排盘操作手册](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/sources/snapshots/.opencode/skills/daliuren/refs/daliuren-paipan.md>)，使用既有 localhost:3456 服务，不自行重排天地盘、四课或三传。纯排盘到此完成。

出生推命转 `liuren-tuiming`；案例查询和归档转 `liuren-cases`；书籍与经验提取转 `liuren-extract`。八字沿用原入口。案例、经验及工具路径以项目根目录为基准。

本地 OpenCode 没有网站的 `register_questions`、`record_judgment` 工具；以核心要求的逐问论证摘要记录对象、盘面关系、状态、反证取舍、结论依赖及未定项，不臆造工具调用，也不声称已通过网站程序校验。历史正文中的旧方法名使用下列新版模块别名，旧 localhost/文件操作仅用于本地环境，不另行启动旧版八套判断流程。

单事研判只加载本总入口。旧子 Skill 名称仅为模块别名，直接读取对应模块文件，不再调用同名 Skill。

以下模块均属于同一融合流程；完整原文、原例和旧稿位于运行包的 sources 中，仅供按争点查证。运行规则依核心的适配口径执行。

[core](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/core.md>)：本问涉及daliuren/sanbu-duanke/leishen-keti
[evidence](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/evidence.md>)：本问涉及liuren-cases
[state-and-rescue](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/mechanisms/state-and-rescue.md>)：本问涉及kongwang-bianzhi/jixiong-tiaozhi
[movement-and-yinshen](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/mechanisms/movement-and-yinshen.md>)：本问涉及keti-qishi/youlu-lilun
[shensha](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/mechanisms/shensha.md>)：本问涉及shensha-panduan/xiongsha-suduan
[timing](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/mechanisms/timing.md>)：本问涉及yingqi-panduan
[finance](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/domains/finance.md>)：本问涉及cailu-panduan
[recruitment](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/domains/recruitment.md>)：本问涉及yingpin-gongzuo
[promotion-salary](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/domains/promotion-salary.md>)：本问涉及shengzhi-jiaxin
[relationship](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/domains/relationship.md>)：本问涉及lianai-panduan
[interpersonal](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/domains/interpersonal.md>)：本问涉及renji-guanxi
[period-outlook](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/domains/period-outlook.md>)：本问涉及shiyun-zonghe
[long-period](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/domains/long-period.md>)：本问涉及zhongshen-nianyun
[pregnancy](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/domains/pregnancy.md>)：本问涉及yunchan-panduan
[exam](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/domains/exam.md>)：本问涉及kaoshi-panduan
[illness](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/domains/illness.md>)：本问涉及jibing-panduan
[lost-person-object](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/domains/lost-person-object.md>)：本问涉及shiwu-xunren
[classical-conflict](<../../../runtime/liuren/20261023-local-active-01/.opencode/skills/daliuren/refs/runtime/domains/classical-conflict.md>)：本问涉及zhinan-zhanbing
