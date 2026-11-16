# zhongshen-nianyun — 压力测试结果

> 阶段 4 产出。独立 sub-agent 盲测（盲测员未参与蒸馏、未看到预期答案）。

## 测试规模

- test-prompts.json: darwin 兼容格式，min_pass_rate=0.8
- 盲测方式: 独立 explorer sub-agent，只读 _skills-catalog.md（15 skill name+description）与剥离后的 _blind-input.json（仅 prompt，隐藏 type/expected/notes），做"该激活哪一个 skill"多选题式判断
- 判卷: 主流程对照 test-prompts.json 预期逐条核对

## 通过率

**9/9 (100%)**

## 失败分析

无。

## 盲测细节

- should_trigger: 4 条全部命中本 skill（终身运势、命理性格、35-45 大运、lifetime fortune）
- should_not_trigger（诱饵）: 3 条全部忍住（天气→none，单问明年→shiyun-zonghe，感情能否成→lianai-panduan）
- edge_case: 2 条符合预期（一生姻缘格局归终身课、当前恋爱成否归恋爱；跨年长期发展归终身课并提示逐年部分用 shiyun-zonghe）

## 结论

接受。
