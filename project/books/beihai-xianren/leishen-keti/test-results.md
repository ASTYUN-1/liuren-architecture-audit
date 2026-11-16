# leishen-keti — 压力测试结果

> 阶段 4 产出。独立 sub-agent 盲测（盲测员未参与蒸馏、未看到预期答案）。

## 测试规模

- test-prompts.json: darwin 兼容格式，min_pass_rate=0.8
- 盲测方式: 独立 explorer sub-agent，只读 _skills-catalog.md（15 skill name+description）与剥离后的 _blind-input.json（仅 prompt，隐藏 type/expected/notes），做"该激活哪一个 skill"多选题式判断
- 判卷: 主流程对照 test-prompts.json 预期逐条核对

## 通过率

**8/9 (88.9%)**

## 失败分析

should-trigger-02 失败：prompt 为"我考驾照的证还没发下来，占下什么时候能拿到"——盲测正确判为 yingqi-panduan（应期问题，其 description 明示例"何时发证"），而测试预期为 leishen-keti。根因是 leishen-keti 的 description 把"何时到手"列入了 trigger，与 yingqi-panduan 真实重叠。

**已修复（修 skill，非修测试）**：从 leishen-keti description 移除"何时到手" trigger，并明确"纯'何时到手'时间问题转 yingqi-panduan——先定迟速再定日期，取类神定成败后再接应期"。此修复消除两个 skill 的跨 skill 抢调用风险。

修复后重测判定：本失败项属于"测试 prompt 本身同时命中两 skill trigger"的边界情形，description 已收敛，接受。

## 盲测细节

- should_trigger: 4 条中 3 条命中（买房→类神主线、怀孕→胎神、类神vs课体分叉）；1 条纯应期被正确路由至 yingqi-panduan
- should_not_trigger（诱饵）: 3 条全部忍住（天气→none，类神已取→kongwang-bianzhi，经济大势→keti-qishi）
- edge_case: 2 条符合预期边界（"能否进这家公司"→yingpin-gongzuo 求职专项，合理路由；病愈→取类神，若仅问痊愈程度可偏 jixiong-tiaozhi）

## 结论

接受（description 已修复，消除与 yingqi-panduan 的重叠）。
