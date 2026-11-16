# renji-guanxi — 压力测试结果

> 阶段 4 产出。独立 sub-agent 盲测（盲测员未参与蒸馏、未看到预期答案）。

## 测试规模

- test-prompts.json: darwin 兼容格式，min_pass_rate=0.8
- 盲测方式: 独立 explorer sub-agent，只读 _skills-catalog.md（15 skill name+description）与剥离后的 _blind-input.json（仅 prompt，隐藏 type/expected/notes），做"该激活哪一个 skill"多选题式判断
- 判卷: 主流程对照 test-prompts.json 预期逐条核对

## 通过率

**9/9 (100%)**

## 失败分析

无实质失败。not-03 盲测判为 shiyun-zonghe（测试预期为 sanbu-duanke），但该 prompt 为泛问整体运势（"工作感情财运都想看看"），测试自身注释即允许"泛占则转 shiyun-zonghe 综合时运断法"，盲测判断合理，判通过。

## 盲测细节

- should_trigger: 4 条全部命中本 skill（同事关系、整体人缘、夫妻相处、help or harm）
- should_not_trigger（诱饵）: 3 条全部忍住未激活本 skill（天气预报→none，恋爱成否→lianai-panduan，泛问运势→shiyun-zonghe/sanbu-duanke）
- edge_case: 2 条符合预期边界（对象分手→lianai-panduan；领导提拔→shengzhi-jiaxin）

## 结论

接受。
