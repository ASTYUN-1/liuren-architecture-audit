# yunchan-panduan — 压力测试结果

> 阶段 4 产出。盲测执行完成（独立盲测员，仅依据 SKILL.md frontmatter 的 description trigger 条件逐条判定）。

## 测试规模

- test-prompts.json: darwin 兼容格式，min_pass_rate=0.8
- 盲测方式: 独立 explorer sub-agent，只读 SKILL.md（frontmatter description + 语言信号）与 test-prompts.json 的 test_cases，按 description 的 trigger 条件对每条 prompt 独立判断"应激活/不应激活/边界"，再对照 type 统计命中。
- 判卷: 盲测判定 vs test_case.type——should_trigger 判"应激活"= 命中；should_not_trigger 判"不应激活"= 命中；edge_case 判可激活 = 命中（不激活也合理则注明）。

## 逐条判定

| test_case id | type | 盲测判定 | 命中与否 | 一句话理由 |
|---|---|---|---|---|
| should-trigger-01 | should_trigger | 应激活 | ✅ 命中 | "这胎""怀的是男孩还是女孩"直中 trigger 关键词"胎/生男生女/胎儿性别"，属 A2 触发场景 1 |
| should-trigger-02 | should_trigger | 应激活 | ✅ 命中 | "预产期/顺利生产/什么时候生"直中"预产期/顺产/产期"，属顺产难产+产期场景 |
| should-trigger-03 | should_trigger | 应激活 | ✅ 命中 | "怀孕/早产/足月"三词全中 trigger，属早产足月判断场景 |
| should-trigger-04 | should_trigger | 应激活 | ✅ 命中 | "能不能生个男孩"核心语义是生男生女/六甲（措辞"能不能"不改占类），可先断来意六甲再断性别 |
| should-not-trigger-01 | should_not_trigger | 不应激活 | ✅ 命中 | 纯历法/假日信息查询，零孕产信号，无触发词 |
| should-not-trigger-02 | should_not_trigger | 不应激活 | ✅ 命中 | description 明确排除"纯恋爱关系成否/婚期/第三者（用 lianai-panduan）"，未言孕产不得抢单 |
| should-not-trigger-03 | should_not_trigger | 不应激活 | ✅ 命中 | 纯财运主题与孕产零重叠，不应因"占"字误触发 |
| edge-01 | edge_case | 边界（可激活） | ✅ 命中 | "这辈子能不能有孩子/子女缘"为终身尺度，贴近 description 排除条款"纯终身运势与姻缘格局（用 zhongshen-nianyun）"；但含生育语义，激活后先澄清时间尺度转 zhongshen 亦合理（不激活也合理） |
| edge-02 | edge_case | 应激活（数据缺失降级） | ✅ 命中 | "肚子里这个宝宝男是女"明确命中"生男生女"trigger，应激活；但缺女方本命属相，金口诀法须降级为课体法+干上神法，如实声明勿补造 |

## 通过率

- 命中数: 9 / 总 case 数: 9 → **通过率 100%（9/9）**
- min_pass_rate = 0.8，**通过**。
- 诱饵容错：3 条 should_not_trigger（含 lianai-panduan 兄弟 skill 诱饵）全部判"不应激活"，零误触发。

## 失败分析

无失败 case。

## 盲测细节

- should_trigger: 4 条（生男生女 / 顺产难产+产期 / 早产足月 / 隔代问六甲）——全部命中，trigger 关键词覆盖充分。
- should_not_trigger（诱饵）: 3 条（端午放假→无关 / 感情成否婚期→lianai-panduan / 纯财运→cailu-panduan）——全部正确拒收，description 的"不适用于"排除条款起了关键作用。
- edge_case: 2 条（一生子女缘→zhongshen-nianyun 边界 / 缺女方本命→金口诀降级）——均按可激活判定命中；edge-01 激活后需先澄清时间尺度（终身格局转 zhongshen-nianyun），edge-02 需降级处理并遵守"勿补造数据"纪律。

## 结论

description 的 trigger 条件（正面关键词清单 + "不适用于"排除条款 + 与 lianai/zhongshen 的边界说明）在 9 条压力测试输入上判定准确率 100%，无漏触发、无误触发，≥80% 阈值通过。
