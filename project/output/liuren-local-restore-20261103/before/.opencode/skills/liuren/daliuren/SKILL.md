---
name: daliuren
description: 大六壬排盘、起课、断课、解课及单事研判统一入口。以北海三步法为主干，融合壬归的定位、位次、理气与制救；按步骤读取方法模块。出生推命、案例维护和资料提取另行分流。
---

# 大六壬单事研判

版本：`20261102-integrated-01`。所有相对链接以本文件所在目录为准；命令在项目根目录执行。

## 本机统一执行主路线


本模块负责执行资料与验收的程序约束；其余原论、判法和专门步骤全文保留。模型仍须逐条研判，检查通过不证明术理正确或预测准确。

1. 在项目根目录使用唯一主入口：`python -X utf8 tools/liuren-workflow.py prepare --input INPUT.json --out RUN`。INPUT包含chart（现有程序引擎参数）、questions（逐问id/question/target/stage/success_criterion/requires）、domains与按条件选出的modules；requires包含conclusion，涉及应期/数量分别加入timing/quantity。source_id及exclude_sources须填已知原案身份。prepare由现有固定引擎生成facts并校验；不接纳模型重排或未经核对的facts。输入无需反馈，也不应放保留答案。
2. 读取RUN/context.json、evidence-packet.json；会话固定facts哈希、源身份、模块计划和全部候选编号。全部候选与省略编号在coverage.json，context带其稳定hash和数量；不把含全文快照的session.json反复送入模型。默认排除暂停记录。候选排序只表示召回，条件/排除/状态/分支选择不被摘要取代；证据正文以ID、hash、定位、正反角色保全后按需分页读取，未读范围保持局限。
3. 按原十一环节读取所有计划模块的所有页：`python -X utf8 tools/liuren-workflow.py read --run RUN --id module:ID --page N`。计划不是已读凭证，读凭证也不是理解证明。命中候选用同一入口`read --run RUN --id ID --part record --page N`读取完整结构；source/evidence:N/source_case:N分别读取原条目与逐个证据。正文保原字节身份、每页有覆盖标记，不整本回传多案书。采用项在evidence_parts列实际完整读取的证据段。会话外、同案、保留答案不得以按ID绕过排除。`--review`仅可审查身份隔离后仍可见的暂停项，不生成可采用凭证。
4. 对每张卡逐条保留conditions/exclusions原文及index，标role：source_context原案背景、source_outcome原载结果、applicability可迁移成立条件、exclusion排除条件、unknown角色待判。不得把原案反馈变成本问先验；前两类只能source_only，并明确used_as_current_fact=false、迁移边界，不能填当前fact_refs。角色未知只能reference/defer/reject。source_method是来源身份，不代表通用预测规则；采用须另有已辨明的可迁移条件、当前子问与程序fact原值、迁移理由。
5. 判断记录包含session_id/session_sha256/facts_sha256/stage、questions和coverage。逐问按requires分别记录conclusion/timing/quantity的status(supported/conditional/unknown)、statement；未知列missing，条件结论列unresolved。应期列window/trigger/basis，数量列range/unit/basis。chart_evidence及条件引用用facts中的path/value精确原值，不从历史反馈补本问事实。
6. rules每项记录id、decision(adopt/conditional/reference/defer/reject)、conditions/exclusions逐条角色与状态、transfer_rationale、fact_refs；unknown记录missing。排除条件met或前提unmet/unknown不得adopt。来源方法没有已判明适用前提时只reference。application另列本问rationale/fact_refs；strongest_counterexample记录status、assessment/source_refs或未决缺口；完整source_refs与会话源清单相同。同源案例与经验不重复计独立证据。
7. `python -X utf8 tools/liuren-workflow.py check --run RUN --record JUDGMENT.json`检查绑定、原文、源与依赖新鲜度、完整已读模块、逐问覆盖、事实原值和条件状态。coverage.candidate_manifest_sha256确认完整候选覆盖清单，unreviewed_limitations明确未读/未评估范围；也兼容显式candidate_ids全列表。检查失败先修记录或保留unknown，不写“已验”；独立验证增量始终0。通过只表示程序覆盖的结构与证据约束，不证明文字之间的因果关系、术理适用性或现实结果。

旧search/load脚本只作兼容定位与分页；旧批量付费执行不再作为新任务入口。案例维护、资料提取、推命保留原专门规程，普通单事不绕到维护流程重复读取。


## 分流与读取约束

- 仅排盘：读[本机排盘操作](<refs/daliuren-paipan.md>)，优先调用 `liuren_chart` 一次完成起课、核验和完整JSON归档；工具未发现时用 `node tools/liuren-direct.mjs`，不先操作浏览器。已有同输入、同设置的可靠 facts 时复用，不由模型重排。
- 本机排盘操作版本为 `20261030-direct-01`，优先于方法包旧手册中的“强制浏览器/唯一依赖3456/默认不落盘”；分页读取器对 `daliuren-paipan` 返回带哈希的本机操作模块，专业研判方法与其他模块不变。只排盘不继续加载断课模块；活时报数等未适配模式按操作模块分流，不冒充正时。
- 出生推命、案例维护、资料提取：分别调用 `liuren-tuiming`、`liuren-cases`、`liuren-extract`。普通断课的检索直接按下列证据模块执行，不绕维护入口重复加载。
- 完整单事判断按下表依次执行。表中“必读”须实际读取全文并完成检查，不能以入口简述代替。共享规则只在对应方法文件维护，不必重复读旧稿。同版本同会话完整读过可复用；截断、换版本或上下文丢失后补读。
- 方法文件的I节原论、B节历史教训及参考表强语均保留条件参照身份，按E节操作与本问定位、理气、反证裁决使用；不能把单例或吉凶名称当无条件结案。旧方法名只标来源，直接读取对应文件，无需调用同名旧 Skill。
- 先判定占类及下表条件；用 `python -X utf8 tools/load-liuren-methods.py plan --domain illness` 取得分环节清单，涉及年命加 `--nianming`，有应期任务加 `--timing`，有数值任务加 `--condition quantity`（不能仅因命中财运/考试占类就自动选入），其余命中条件加 `--condition 模块ID`（可重复）。清单会列出未选中的条件，须核对并补选；新争点出现时重新规划补读。也可直接完整 Read 下表对应文件；两种路径使用相同的必读和条件集合。
- 分页用 `read 模块ID --page N`。输出固定 UTF-8、LF；`pageSha256` 对 BEGIN 行后至 END 分隔换行前的原始正文 UTF-8 字节计算，保留正文原有末尾换行，不含标记和额外分隔换行。保留版本、页码、哈希和结束标记；直接 Read 不伪造页凭证。缺页或截断须补齐；哈希只验证内容传输，不证明模型理解或执行。

## 三步主干与十一环节

“明占类 → 定侧重 → 看显象”保持一条流程。逐步输出可核对小结；不输出私下思维草稿。多个子问共用盘和已核节点，分别裁决。

<!-- READING_STAGES_BEGIN -->
| 环节 | 实际动作与可见产物 | 读取要求 |
|---|---|---|
| 1 数据准备 | 区分题干事实、程序盘、解释断语；列盘源、关键缺项 | 命中条件必读[本机排盘操作](<refs/daliuren-paipan.md>)、[年命](<../../../../runtime/liuren/20261102-integrated-01/references/nianming.md>)（条件与参数见下表）。复用可靠程序盘，不由模型重排。 |
| 2 明占类 | 保留原问，列对象、事件阶段、期限、成功标准；检索方法与反例 | 必读[定位与选线](<../../../../runtime/liuren/20261102-integrated-01/methods/positioning.md>)、[证据检索](<../../../../runtime/liuren/20261102-integrated-01/methods/evidence.md>)。命中条件必读[规则语义](<../../../../runtime/liuren/20261102-integrated-01/references/rule-semantics.md>)（条件与参数见下表）。并读取命中占类。并读取命中的占类；原问与检索要求按本环节落实。 |
| 3 定侧重 | 固定日干/日支/类神/人物；写明主线如何直接回答本问 | 必读[课位与关系](<../../../../runtime/liuren/20261102-integrated-01/methods/relations.md>)。不得只给角色贴标签。 |
| 4 看显象 | 对主判和最强反证比较双方状态、关系与实际作用 | 必读[理气与救制](<../../../../runtime/liuren/20261102-integrated-01/methods/liqi.md>)、[空亡与变质](<../../../../runtime/liuren/20261102-integrated-01/methods/void.md>)。命中条件必读[来源卡](<../../../../runtime/liuren/20261102-integrated-01/references/liqi-sources.md>)、[风险细则](<../../../../runtime/liuren/20261102-integrated-01/details/risk.md>)（条件与参数见下表）。 |
| 5 综合核查 | 八煞九宝及32项逐项检查，区分已核、待核、采用与无关 | 必读[八煞九宝](<../../../../runtime/liuren/20261102-integrated-01/references/bashajiubao.md>)、[引擎神煞字段](<../../../../runtime/liuren/20261102-integrated-01/references/engine-shensha-output.md>)、[32项](<../../../../runtime/liuren/20261102-integrated-01/references/shensha-focus.md>)、[神煞取用](<../../../../runtime/liuren/20261102-integrated-01/references/shensha-use.md>)。命中条件必读[神煞方法](<../../../../runtime/liuren/20261102-integrated-01/details/shensha-tradition.md>)（条件与参数见下表）。 |
| 6 动态深化 | 关键通路、直接阴神、已核年命；写出作用与停止深化理由 | 必读[动态与阴神](<../../../../runtime/liuren/20261102-integrated-01/methods/movement.md>)。有具体争点才扩层。 |
| 7 结构反证 | 九宗门、毕法结构、位次相互核对，不能由课名结案 | 必读[课体结构](<../../../../runtime/liuren/20261102-integrated-01/methods/structure.md>)。构成不明时读所链接表格。 |
| 8 制救裁决 | 比较最强反证、救制范围；分开结果、过程、程度 | 必读[调制与裁决](<../../../../runtime/liuren/20261102-integrated-01/methods/adjudication.md>)。 |
| 9 应期与取数 | 在既定对象与结果分支中分别完成数值和时间任务 | 命中条件必读[数量与精度](<../../../../runtime/liuren/20261102-integrated-01/methods/quantity.md>)、[数法来源与条件](<../../../../runtime/liuren/20261102-integrated-01/references/quantity-sources.md>)、[应期](<../../../../runtime/liuren/20261102-integrated-01/methods/timing.md>)（条件与参数见下表）。按题目选择专项；无相应任务注明不适用，不改变主干次序。 |
| 10 收尾核证 | 复用前置检索，核来源、迁移条件与未解决分歧；有新争点再查 | 依证据检索规程复用前置检索，有新争点再查。 |
| 11 交付复核 | 列依据、反证取舍、结论依赖、边界及实际读取缺口 | 必读[报告与交付检查](<../../../../runtime/liuren/20261102-integrated-01/methods/report.md>)。缺必读项先补读。 |
<!-- READING_STAGES_END -->

## 占类与条件路由

按具体子问读取，不把所有占类全跑一遍。复合题可选多个：

| ID | 目标 | 文件 |
|---|---|---|
| finance | 工资、经营、利润、债款、金额 | [财运](<../../../../runtime/liuren/20261102-integrated-01/domains/finance.md>) |
| recruitment | 求职、面试、录用、入职 | [应聘](<../../../../runtime/liuren/20261102-integrated-01/domains/recruitment.md>) |
| promotion-salary | 在职职责、晋升、加薪、平调外派 | [任职](<../../../../runtime/liuren/20261102-integrated-01/domains/promotion-salary.md>) |
| relationship | 联系、恋爱、订婚、结婚 | [感情](<../../../../runtime/liuren/20261102-integrated-01/domains/relationship.md>) |
| interpersonal | 相处、态度、合作损益 | [人际](<../../../../runtime/liuren/20261102-integrated-01/domains/interpersonal.md>) |
| period-outlook | 阶段综合运势 | [阶段运势](<../../../../runtime/liuren/20261102-integrated-01/domains/period-outlook.md>) |
| long-period | 问事课看终身、多年、年运 | [长期](<../../../../runtime/liuren/20261102-integrated-01/domains/long-period.md>) |
| pregnancy | 怀孕、胎产、分娩 | [胎产](<../../../../runtime/liuren/20261102-integrated-01/domains/pregnancy.md>) |
| exam | 学校、驾校、职业考试，成绩录取答辩毕业 | [考试](<../../../../runtime/liuren/20261102-integrated-01/domains/exam.md>) |
| illness | 病势、治疗、手术、恢复 | [疾病](<../../../../runtime/liuren/20261102-integrated-01/domains/illness.md>) |
| lost-person-object | 失物、走失、寻人、被盗 | [失物寻人](<../../../../runtime/liuren/20261102-integrated-01/domains/lost-person-object.md>) |
| classical-conflict | 古典兵占、攻守、盗逃 | [兵占](<../../../../runtime/liuren/20261102-integrated-01/domains/classical-conflict.md>) |

家宅、天时、出行、司法行政等未有成熟专项：仍执行全部基础模块，按[定位与选线](<../../../../runtime/liuren/20261102-integrated-01/methods/positioning.md>)查有据的原书小段；不得套邻近专项。下表条件在判断中出现时立即补读，不为缩短读取略去适用例外。

<!-- READING_CONDITIONS_BEGIN -->
| 模块 ID | 触发条件 | 环节 | plan 参数 |
|---|---|---|---|
| `daliuren-paipan` | 需要起课或核对程序盘 | 1 | `--condition daliuren-paipan` |
| `nianming` | 涉及本命或行年规则的计算、核验或采用 | 1 | `--nianming` |
| `rule-semantics` | 否定范围、摘要条件或规则强度存疑 | 2 | `--condition rule-semantics` |
| `liqi-sources` | 所采用方法存在来源或口径分歧 | 4 | `--condition liqi-sources` |
| `risk` | 四大凶象承担主判或最强反证 | 4 | `--condition risk` |
| `shensha-tradition` | 采用季煞或传统神煞层级说明 | 5 | `--condition shensha-tradition` |
| `quantity` | 原问要求金额、分数、数量、重量、距离等数值，或已选应期专法需要数理时长 | 9 | `--condition quantity` |
| `quantity-sources` | 需要核对取数数表、原法条件或精确数值案例；已取得对应原书可复用 | 9 | `--condition quantity-sources` |
| `timing` | 有时间任务 | 9 | `--timing` |
<!-- READING_CONDITIONS_END -->

本机通过统一 CLI 的 prepare/read/check 执行子问登记、来源读取和程序检查；网站工具不在本机调用。交付保留实际检查回执，不把结构检查写成术理验证。纯技术检查、教材例与自审不证明预测准确率。
