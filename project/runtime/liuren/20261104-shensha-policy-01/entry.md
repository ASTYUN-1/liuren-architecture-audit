---
name: daliuren
description: 大六壬排盘、起课、断课与单事研判；按北海三步法与十一环节读取方法，分类取用并核显象、理气与制救。出生推命与知识维护另行分流。
---

# 大六壬单事研判
版本 `20261104-shensha-policy-01`。明占类→定侧重→看显象，按十一环节执行并给可核对小结，不输出私下思维草稿。在项目根执行命令；本机交付完整技术判断，保留来源、条件、反证和缺口。网站公开报告隐藏、改写及发布门禁不适用。prepare/read/check 仅可选审计，不强制 JSON。

仅排盘先读[本机操作](<../../../docs/本机六壬直接排盘.md>)，优先 liuren_chart，一次起课、核验并归档完整 JSON；工具缺失用 node tools/liuren-resolved-chart.mjs。复用同输入设置的可靠 facts，不由模型重排；活时报数按操作分流。出生推命、案例维护、资料提取分别走 liuren-tuiming、liuren-cases、liuren-extract。

## 方法读取
完整单事先按子问选占类和条件。在六壬受限模式用 liuren_materials(action="methods", domains=[...], conditions=[...], timing=..., nianming=..., batch=N) 获取当前路由和全文批次；按返回清单读完适用模块全部页。CLI 等价：python -X utf8 tools/load-liuren-methods.py plan --domain illness，再 read 模块ID --page N；条件用 --condition，可重复。工具未读正文不得登记为已读。
同版本、本会话已完整读过且仍在上下文的内容可复用；换版、缺页、截断或内容丢失才补读。页码、哈希和运行通过只证明传输/结构，不证明理解、术理或预测。分页核 UTF-8/LF、BEGIN/END 和页哈希；直接 Read 不伪造凭证。

## 十一环节
<!-- READING_STAGES_BEGIN -->
| 环节 | 执行动作 | 必读模块 ID |
|---|---|---|
| 1 数据准备 | 区分题干事实、程序盘、解释断语；列盘源、关键缺项 | 按下表条件 |
| 2 明占类 | 保留原问，分清对象、阶段、目标；从十二分类进入九系统取用，检索方法与反例 | class-mapping, positioning, evidence |
| 3 定侧重 | 说明现实对象、候选类神、取用依据及实际位置；有歧义保留条件分支 | relations |
| 4 看显象 | 同时核主类神与其他相关课传显象，比较状态、关系、实际作用和最强反证 | liqi, void |
| 5 综合核查 | 八煞九宝及32项逐项检查，区分已核、待核、采用与无关 | bashajiubao, engine-shensha-output, shensha-focus, shensha-use |
| 6 动态深化 | 关键通路、直接阴神、已核年命；写出作用与停止深化理由 | movement |
| 7 结构反证 | 九宗门、毕法结构、位次相互核对，不能由课名结案 | structure |
| 8 制救裁决 | 比较最强反证、救制范围；分开结果、过程、程度 | adjudication |
| 9 应期与取数 | 在既定对象与结果分支中分别完成数值和时间任务 | 按下表条件 |
| 10 收尾核证 | 复用前置检索，核来源、迁移条件与未解决分歧；有新争点再查 | 按下表条件 |
| 11 交付复核 | 列依据、反证取舍、结论依赖、边界及实际读取缺口 | report |
<!-- READING_STAGES_END -->

环节2另读选中专项，环节3将定位落实到盘中作用。多个子问共用盘、已核节点与来源，分别裁决；理气、空亡、八煞九宝与32项、阴神、课体、制救保持原检查深度。I/B 原载断语与旧案例为条件参照，不能凭吉凶名称结案；采用细法缺上下文时读 mapping-provenance 指向的原段。

## 分类路由（按目标，复合题可多选）
| 类别 | ID |
|---|---|
| 婚恋伴侣 / 人际交往 | relationship / interpersonal |
| 事业任职：求职 / 在职 | recruitment / promotion-salary |
| 财务经营 / 学业考核 | finance / exam |
| 疾病求医 / 胎产生育 | illness / pregnancy |
| 家宅地产 / 出行行人 | home / travel |
| 失物盗逃 / 天时环境 / 农渔畜养 | lost-person-object / weather / agriculture |
| 阶段运势 / 长期 / 古典兵占 | period-outlook / long-period / classical-conflict |
各类按子问、阶段细分。未齐的司法行政、梦怪等查有据原书子段，不套邻类；类别存在不表示专法完整。

<!-- READING_CONDITIONS_BEGIN -->
| 条件模块 | 触发时必读 | 环节 |
|---|---|---|
| daliuren-paipan | 需要起课或核对程序盘 | 1 |
| nianming | 涉及本命或行年规则的计算、核验或采用 | 1 |
| rule-semantics | 否定范围、摘要条件或规则强度存疑 | 2 |
| liqi-sources | 所采用方法存在来源或口径分歧 | 4 |
| risk | 四大凶象承担主判或最强反证 | 4 |
| shensha-tradition | 采用季煞或传统神煞层级说明 | 5 |
| quantity | 原问要求金额、分数、数量、重量、距离等数值，或已选应期专法需要数理时长 | 9 |
| quantity-sources | 需要核对取数数表、原法条件或精确数值案例；已取得对应原书可复用 | 9 |
| timing | 有时间任务 | 9 |
| shenjiang-use | 采用神将同用、互换，或需要核对具体神将类义的适用范围 | 3 |
| shen-symbols | 需查十二天神的基础义、复合取义或与本家天将的差别 | 3 |
| jiang-symbols | 需查十二天将的职能、占类取义或与本家支神的差别 | 3 |
| mapping-provenance | 需核合并对应、旧 I/B 上下文、原卡或未决条件 | 2 |
<!-- READING_CONDITIONS_END -->

条件采用即补读；nianming 对应 --nianming，timing 对应 --timing，其余 --condition ID。神将辞义未触发不全读；有新争点时补选。

## 证据与交付
定侧重前分别检索案例、经验，按“事件＋目标”再按“位置/结构＋争点”补检；用 liuren_materials(action="retrieve", case_query=..., experience_query=..., category=...)。摘要用于定位，实际阅读相关原档与邻近条件、原断、反馈，说明迁移与未采用理由，不凑采用条数。普通断课直接检索，不绕维护入口；材料范围按该工具 scope。
直接交付完整盘面、定位依据、主线、支持与最强反证、制救取舍、逐问结论、来源及未核项，不经客户版删改。同卦追问保留前情，只补新增争点；新事实推翻前提时说明修正并重核依赖。解释与原案事实、原载反馈、本案事实分开，不移植结论。
具体本机执行与完整输出边界见 docs/本机六壬完整研判流程.md、docs/本机OpenCode完整输出规则.md；它们是执行说明，不重复加载专业方法。

神煞取用先读程序 shensha_resolution：新盘自动带出；旧盘用 liuren_materials(action="shensha", path="原归档路径")。未采用项不得转作背景风险；原标签仅比对。完整口径见现有 shensha-focus / shensha-use，不新增必读层。

当前排盘神煞计算与导出已修正：facts及archive为采用值，legacy_archive保留旧引擎结果。神煞只归属天盘tian，di仅是所临地盘；不得把午加丑之午煞记到丑。
