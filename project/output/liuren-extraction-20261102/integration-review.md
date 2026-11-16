# 本地检索附加层独立只读验收

验收日期：2026-11-02。范围：`tools/liuren_research_overlay.py`、`tools/experience_retrieval.py`、`tools/case_retrieval.py`、`tools/liuren_knowledge_workbench.py` 的 `validated_records`、索引接入、文本输出、批处理包及已知同案排除。没有修改上述主文件；故障注入均使用 `unittest.mock.patch` 在进程内完成，没有改写审查、规则或原始资料。

**结论：已复验通过本轮指定范围，未留阻断问题。**最初复现的两处信息遗漏已反馈主会，主会修订后再次验证均通过。此结论针对工程接入与信息保留，不代表全库语义审查完成或预测效果提升。

## 已发现并复验关闭

1. **经验文本输出漏掉审查的可取内容。**初版 `experience_retrieval.render` 输出审查 `finding`，未输出 `review_notices.reference_value`。以 `LA26-LEGACY-001` / `H0001` 实跑，两条可取内容均未见于文本。修订后两条均出现，案例文本及批处理包亦保留 `reference_value` 和 `action_scope`。这避免只呈现纠错而遗漏卦师有用的组合读法。
2. **审查JSON整体无法解析时，旧摘要失去定点提示，经验批处理包又丢掉具体错误。**复现：仅在内存中 patch `liuren_knowledge_workbench.read_bytes`，使 `knowledge/liuren-research/20261102/audits/legacy-review.json` 返回非法JSON。初版H0001恢复裸强摘要，经验packet删除了 `research_issues` 列表。修订后H0001摘要带“审查层加载缺口，先核原文”，保留旧方法素材但明确附加审查不完整；经验与案例packet均有 `research_issue_count=1` 及故障文件/错误诊断。诊断不携全局审查目标或证据正文。故障并未被当成旧规则自动重新获准。

## 当前实跑结果

- `validated_records`：49记录，49可检索，`mechanical_valid=true`，0 issues，6个规则族，`complete=false`，独立验证数0。候选和原载方法均保持检索参照，不因未独立验证而禁用。
- 两次 `experience_retrieval.ensure_index` 均989项，唯一ID989，无正常入口重复叠加；两次案例索引均256来源。附加层从基础缓存临时应用，没有把审查追加写回基础数据。
- 班主任检索批处理实收 `LR26-K2-009`、`K2-010`，其 `conditions`、`exclusions`、`reasoning_steps`、`alternatives`、`reference_value` 与原卡逐字段相等。原文片段有长度限制，但明确标截断并保留卡路径与来源位置，未用截断原文代替完整条件。
- `B0289`现有 `LA26-BOOK-001`定点审查；`action_scope`明确只暂停从此案抽出的“飞廉作白虎必有去无回”充分条件，不删原案，不否定原作者其他风险判断。新卡K2-006及其他暂停卡仍作为审查材料检出，带暂停身份。
- 4个既有开发题0002、0026、0037、0200：分别以本题 `source_id` 调经验/案例packet，两个包均不含对应原始题ID；基础检索逐条检查也未见对应题来源残留。读取的是这4题既有public输入，没有打开新题答案；它们仍是方法开发暴露样本，不能称盲测。
- 跨来源依赖故障注入：内存中给K2-008增设对K2-011的 `依赖`，排除0037时K2-008一起被排除，证明依赖来源可以继承。把K2-011改pending，K2-008被标 `关联记录失效`；只给0037原文件字节追加换行的内存模拟产生 `source_hash_changed`，K2-011和依赖者均阻断。未依赖的关联不因对方状态而被当作同一方法合并。
- 单份有效审查的quote故障注入：LA26-LEGACY-001不再作为有效审查应用，H0001保留“关联审查待核或证据失效”及“审查缺口”提示，未静默恢复。原书案的 `source_case_ids` / `source_case_refs` 身份也参与排除；整案注册不靠精选引用碰巧覆盖身份。
- 覆盖报告代码明确将资产索引、引用核对、语义审查和效果验证分列，整源精读/全窗完成未被自动计成已完成；201份作答的参照价值与现有14份反馈标签分开，未误称只有14份可用或全201份已经精读。
- 追加的6个规则族逐族复验：丑未、权重、初空失物、子问、摘要语义等5个比较/分支族，在经验检索中各成员仍保持独立组（分别8/8、11/11、6/6、15/15、6/6），没有按相似方法折叠成同一事件。唯一`同源归并`族将H0111/H0115合并显示，而LR26-LEGACY-016仍为独立审读卡。与基础案例缓存逐条比较，只有已核同源的胎产case-001/case-005改变`source_group`；分别排除任一档路径，都同时排除两档及对应旧经验。规则族标签在CLI和packet保留。
- 实跑`python -m unittest discover -s tools/tests -p test_liuren_research_overlay.py -v`，11项全部通过。另用全新Python进程按文件路径`importlib`导入两个检索模块，不手动修改`sys.path`，均可直接调用`ensure_index`（989/256），入口兼容修复通过。

## 范围限制

反馈防泄露核查覆盖了4个已暴露题的显式身份、当前登记的同案路径及内存构造的跨卡依赖。未建立来源联系的转引、未知同源和既有历史污染，仍不能由本次测试保证排除。没有打开预留题私有答案来扩大测试，也没有重做预测试验。报告中的“通过”不认可所有原作者/旧AI推论均正确；原文可取内容、子判断、冲突与事实验证状态仍按各卡分别使用。

验收末轮代码SHA256：

- `liuren_research_overlay.py`：`95e8fff74beb725e99fc00eaaaf87ac5cfb2f4eba5d6e3b3d78b4f0e18d2ccc3`
- `experience_retrieval.py`：`970e1021029e7ae6590ecaca5f9652bd32e3f8e630bf75cb436bcd6ebb56f5c9`
- `case_retrieval.py`：`8bd95081c784acf438118b822fef392131ced9952e075cea3c591a96ba5436f6`
- `liuren_knowledge_workbench.py`：`48bc8d420c9e255a5f07e9fc8b62aa7401804338f94c1b17d2acbefe985217fc`
