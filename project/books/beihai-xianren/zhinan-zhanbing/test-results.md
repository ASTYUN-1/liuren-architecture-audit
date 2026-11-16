# zhinan-zhanbing — 压力测试结果（阶段 4 盲测）

> 阶段 4 产出。盲测方式：独立盲测员仅依据 SKILL.md frontmatter 的 description（trigger 条件）逐条判定 test-prompts.json 的每条 prompt 是否应激活本 skill，再对照 test_case.type 核对命中。未修改 test-prompts.json 与 SKILL.md。

## 测试规模

- test-prompts.json: darwin 兼容格式，min_pass_rate=0.8
- 盲测判据：description 关键 trigger 词（兵/战/战争/边境/军事/贼/盗/失窃/被劫/逃亡/走失/寻人/失踪/破案/报案/占 等）+ "纯财运/纯人际不适用"排除边界 + "现代商战/纠纷需类比转换"明示可触发。

## 逐条盲测结果

| test_case id | type | 盲测判定 | 命中与否 | 一句话理由 |
|---|---|---|---|---|
| should-trigger-01 | should_trigger | 应激活 | 命中 | 含"边境/打仗/冲突"，直接命中 trigger"边境/战/战争"，兵占无疑。 |
| should-trigger-02 | should_trigger | 应激活 | 命中 | 含"进贼/丢/贼/抓到"，命中"贼/失窃/盗"，走玄武四步贼占。 |
| should-trigger-03 | should_trigger | 应激活 | 命中 | 含"走失/往哪去/什么时候找到"，命中"走失/寻人/失踪"，占逃亡寻人。 |
| should-trigger-04 | should_trigger | 应激活 | 命中 | 含"盗(商业机密)/商战/守不守得住"，description 明示商战须类比转换后触发。 |
| should-not-trigger-01 | should_not_trigger | 不应激活 | 命中 | "适合出门办事"泛问出行，无任何兵盗寻人 trigger 词。 |
| should-not-trigger-02 | should_not_trigger | 不应激活 | 命中 | "出差顺不顺/波折"为行止动象主题，"占"字未配兵盗类主题词，应归 youlu-lilun。 |
| should-not-trigger-03 | should_not_trigger | 不应激活 | 命中 | 纯财运/投资，description 明确"不适用于纯财运（转 cailu-panduan）"，不因含"占"误触发。 |
| edge-01 | edge_case | 可激活（边界） | 命中 | "是不是进过贼"含"贼"且问事态有无（贼占路径），但需与凶煞路径先辨判据；判可激活不越界。 |
| edge-02 | edge_case | 可激活（越占边界） | 命中 | 纯健康默认不属本 skill，但按"非占现类勿言之"例外，课盘见玄武发用/人宅受脱等强盗象时可越占断贼——判可激活（条件性）。 |

## 通过率

**命中 9 / 总 9 = 100%**（min_pass_rate=0.8，通过）。

## 失败分析

无失败 case。

## 盲测细节与边界备注

- should_trigger: 4 条全部命中，触发词覆盖充足（兵事/贼盗/走失/商战类推均有对应 description 表述）。
- should_not_trigger（诱饵）: 3 条全部正确拦截（无关出行 / youlu-lilun 动象 / cailu-panduan 纯财运），"占"字配主题词的约束有效，诱饵容错 0 达标。
- edge_case: 2 条均判"可激活"且注明边界条件——edge-01 依赖"事态有无 vs 吉凶担忧"的先后辨；edge-02 依赖课盘强盗象触发才越占，无强据则不激活（两种处理均符合 skill 边界纪律）。
- 主要风险点（非本次失败）：description 中 trigger 词"破案/报案"在测试集中未直接出现，现代司法语境（报警/立案）表述可能依赖"贼/盗"近义词间接命中，建议后续补测。

## 结论

**通过（100% ≥ 80%）**。description 的触发词覆盖与排除边界在 9 条盲测下表现良好：兵盗类正向命中、三类诱饵全部拦截、两条边界判定与 skill 自身边界纪律一致。
