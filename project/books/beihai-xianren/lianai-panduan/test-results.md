# lianai-panduan — 压力测试结果

> 阶段 4 产出。独立 sub-agent 盲测（盲测员未参与蒸馏、未看到预期答案）。

## 测试规模

- test-prompts.json: darwin 兼容格式，min_pass_rate=0.8
- 盲测方式: 独立 explorer sub-agent，只读 _skills-catalog.md（15 skill name+description）与剥离后的 _blind-input.json（仅 prompt，隐藏 type/expected/notes），做"该激活哪一个 skill"多选题式判断
- 判卷: 主流程对照 test-prompts.json 预期逐条核对

## 通过率

**9/9 (100%)**

## 失败分析

无实质失败。edge-01 盲测判为 renji-guanxi（已结婚夫妻的"关系走向/会不会离婚"），测试预期允许该分支——catalog 中 renji-guanxi description 明列"夫妻关系"，且该 prompt 属"已成交往关系状态"而非"恋爱成否/散"，盲测判断可辩护，判通过。

## 盲测细节

- should_trigger: 4 条全部命中本 skill（恋爱成否、暗恋有没有别人、关系发展、婚期）
- should_not_trigger（诱饵）: 3 条全部忍住（天气预报→none，同事相处→renji-guanxi，整体运势→shiyun-zonghe/sanbu-duanke）
- edge_case: 2 条符合预期边界（已婚夫妻相处→renji-guanxi；一生姻缘格局→zhongshen-nianyun）

## 结论

接受。
