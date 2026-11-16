# 本机统一会话契约

本模块负责执行资料与验收的程序约束；其余原论、判法和专门步骤全文保留。模型仍须逐条研判，检查通过不证明术理正确或预测准确。

1. 在项目根目录使用唯一主入口：`python -X utf8 tools/liuren-workflow.py prepare --input INPUT.json --out RUN`。INPUT包含chart（现有程序引擎参数）、questions（逐问id/question/target/stage/success_criterion/requires）、domains与按条件选出的modules；requires包含conclusion，涉及应期/数量分别加入timing/quantity。source_id及exclude_sources须填已知原案身份。prepare由现有固定引擎生成facts并校验；不接纳模型重排或未经核对的facts。输入无需反馈，也不应放保留答案。
2. 读取RUN/context.json、evidence-packet.json；会话固定facts哈希、源身份、模块计划和全部候选编号。全部候选与省略编号在coverage.json，context带其稳定hash和数量；不把含全文快照的session.json反复送入模型。默认排除暂停记录。候选排序只表示召回，条件/排除/状态/分支选择不被摘要取代；证据正文以ID、hash、定位、正反角色保全后按需分页读取，未读范围保持局限。
3. 按原十一环节读取所有计划模块的所有页：`python -X utf8 tools/liuren-workflow.py read --run RUN --id module:ID --page N`。计划不是已读凭证，读凭证也不是理解证明。命中候选用同一入口`read --run RUN --id ID --part record --page N`读取完整结构；source/evidence:N/source_case:N分别读取原条目与逐个证据。正文保原字节身份、每页有覆盖标记，不整本回传多案书。采用项在evidence_parts列实际完整读取的证据段。会话外、同案、保留答案不得以按ID绕过排除。`--review`仅可审查身份隔离后仍可见的暂停项，不生成可采用凭证。
4. 对每张卡逐条保留conditions/exclusions原文及index，标role：source_context原案背景、source_outcome原载结果、applicability可迁移成立条件、exclusion排除条件、unknown角色待判。不得把原案反馈变成本问先验；前两类只能source_only，并明确used_as_current_fact=false、迁移边界，不能填当前fact_refs。角色未知只能reference/defer/reject。source_method是来源身份，不代表通用预测规则；采用须另有已辨明的可迁移条件、当前子问与程序fact原值、迁移理由。
5. 判断记录包含session_id/session_sha256/facts_sha256/stage、questions和coverage。逐问按requires分别记录conclusion/timing/quantity的status(supported/conditional/unknown)、statement；未知列missing，条件结论列unresolved。应期列window/trigger/basis，数量列range/unit/basis。chart_evidence及条件引用用facts中的path/value精确原值，不从历史反馈补本问事实。
6. rules每项记录id、decision(adopt/conditional/reference/defer/reject)、conditions/exclusions逐条角色与状态、transfer_rationale、fact_refs；unknown记录missing。排除条件met或前提unmet/unknown不得adopt。来源方法没有已判明适用前提时只reference。application另列本问rationale/fact_refs；strongest_counterexample记录status、assessment/source_refs或未决缺口；完整source_refs与会话源清单相同。同源案例与经验不重复计独立证据。
7. `python -X utf8 tools/liuren-workflow.py check --run RUN --record JUDGMENT.json`检查绑定、原文、源与依赖新鲜度、完整已读模块、逐问覆盖、事实原值和条件状态。coverage.candidate_manifest_sha256确认完整候选覆盖清单，unreviewed_limitations明确未读/未评估范围；也兼容显式candidate_ids全列表。检查失败先修记录或保留unknown，不写“已验”；独立验证增量始终0。通过只表示程序覆盖的结构与证据约束，不证明文字之间的因果关系、术理适用性或现实结果。

旧search/load脚本只作兼容定位与分页；旧批量付费执行不再作为新任务入口。案例维护、资料提取、推命保留原专门规程，普通单事不绕到维护流程重复读取。
