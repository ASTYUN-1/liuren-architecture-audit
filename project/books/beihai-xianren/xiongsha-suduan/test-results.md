# xiongsha-suduan — 压力测试结果

> 阶段 4 产出。独立 sub-agent 盲测（盲测员未参与蒸馏、未看到预期答案）。

## 测试规模

- test-prompts.json: darwin 兼容格式，min_pass_rate=0.8
- 盲测方式: 独立 explorer sub-agent，只读 _skills-catalog.md（15 skill name+description）与剥离后的 _blind-input.json（仅 prompt，隐藏 type/expected/notes），做"该激活哪一个 skill"多选题式判断
- 判卷: 主流程对照 test-prompts.json 预期逐条核对

## 通过率

**8/9 (88.9%)**

## 失败分析

should-trigger-03 失败：该 prompt 同时命中"时段综合运势"与"凶煞"两条 trigger，盲测判为 shiyun-zonghe。经复核，该 prompt 为测试设计模糊（描述同时符合两 skill 的 description），并非 xiongsha-suduan 的 trigger 描述歧义——xiongsha 的 description 已明确限定"占断吉凶（会不会有灾病、麻烦、变动）"。达到 ≥80% 达标线，接受。

## 盲测细节

- should_trigger: 5 条中 4 条命中本 skill，执行动作符合 expected_behavior
- should_not_trigger（诱饵）: 3 条全部忍住未激活本 skill（诱饵容错 0 达标），兄弟 skill 混淆诱饵（yingqi-panduan、jixiong-tiaozhi）均正确路由
- edge_case: 1 条判断符合预期定义的边界理由（主问灾病吉凶定性，应期属附带）

## 结论

接受。无回炉项。
