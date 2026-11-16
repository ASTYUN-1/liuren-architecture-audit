from pathlib import Path
root=Path('.')
def edit(path, pairs):
 p=root/path;s=p.read_text(encoding='utf-8-sig')
 for old,new in pairs:
  if old not in s: raise RuntimeError('未找到替换目标: '+path+' '+old[:70])
  s=s.replace(old,new)
 p.write_text(s,encoding='utf-8',newline='\n')
edit('.opencode/skills/daliuren/SKILL.md',[
 ('仅当 `经验日志\\` 中存在同一课体（或同发用组合）且标记为 **"反馈：验"** 的记录时，直接采信该结论，其他信息源仅作背景说明。**未验证的记录降为第 3 级。**','通过条目级索引检索具体规则及反馈。先核对是否为独立原案，以及问题目标、类神位置与状态、旺衰空墓、年命和例外是否可迁移；历史称验与相似度本身不触发直接采信。条件不一致时，须结合书籍解释边界，不能压倒本课证据。未验证经验仅作候选解释。'),
 ('无已验证实战日志时执行','无条件充分吻合的实战依据时执行'),
 ('检索经验日志（"反馈：验"同课记录）','检索经验条目（含书籍方法、验证身份、适用条件与反例）'),
 ('经验日志"反馈：验"','经验条目条件核对'),
 ('2. **经验日志检索**：在 `经验日志\\_metadata_index.md`（归一化索引）中**锚定** `^<!-- META:` 检索同一课体（或同发用组合）且标记 **"反馈=验"** 的记录——命中即触发冲突裁决阶梯第 1 级。','2. **经验条目检索**：使用 `python -X utf8 tools/search-experience.py --query "课体 方法关键词" --category 对应占类 --limit 8`，读取命中条目的原文、验证身份、条件与关联反例。批处理无 shell 权限时读取调度器提供的本阶段 `*-experience-retrieval.json`，再读原文。参见 [经验检索规则](../liuren-cases/refs/experience-retrieval-v2.md)。旧经验 `_metadata_index.md` 只作兼容；经验相关性不套案例六维分，同源跨库引用不重复计证。'),
 ('等级 1（最高）：经验日志存在"反馈：验"同课记录 → 直接采信，其他信息源仅作背景说明。','等级 1（最高）：存在可定位的现实反馈，且具体规则的迁移条件、独立来源与反例已核对 → 优先参考其适用范围；不因同课或称验自动复制结论。'),
])
edit('.opencode/skills/liuren-cases/SKILL.md',[
 ('**主流程冲突裁决阶梯（第 1 级，最高）**：已验证的实战反馈优先于一切理论——当 `经验日志\\` 中存在同一课体（或同发用组合）且标记为"反馈：验"的记录时，直接采信该结论，其他信息源仅作背景说明。**这是案例库存在的根本理由：案例是断课的最高级信息源。**','**经验检索与迁移**：案例找相似情境，经验找具体方法、条件与例外。经验使用条目级新索引；历史称验不直接复制结论，案例与经验同源不计两份独立证据。执行 [经验检索规则](refs/experience-retrieval-v2.md)，批处理的禁止子智能体约束继续有效。'),
 ('**检索入口（不用裸 grep）**：`tools\\search-cases.ps1`（确定性检索 + 六维评分）。索引重建用 `tools\\build-experience-index.ps1`。详见 E3。','**检索入口**：`tools\\search-cases.ps1 -Scope case` 检索案例并做六维评分；`tools/search-experience.py` 检索细粒度经验。旧经验索引仅兼容，运行索引刷新用 `python -X utf8 tools/search-experience.py --refresh --status`。详见 E3。'),
 ('源文件的 `反馈=` 存在 7 种写法，**必须先归一再匹配**','案例源文件的 `反馈=` 存在 7 种写法，**必须先归一再匹配**'),
 ('已验证案例，结论可信度高','历史判验排序提示；仍须核对具体命中范围和迁移条件'),
])
p=root/'.opencode/skills/liuren-cases/SKILL.md';s=p.read_text(encoding='utf-8');a=s.index('#### E3 ·');b=s.index('#### E4 ·',a)
s=s[:a]+'''#### E3 · 案例与经验双入口（条目级经验索引）

**案例检索**保留数据根自检、META 索引优先、六维评分与原文类比：

```powershell
powershell -ExecutionPolicy Bypass -File tools/search-cases.ps1 -Scope case `
  -ZhanLei 财运占 -KeTi "元首,退茹" -FaYong "卯(朱雀)" -SanChuan 卯寅丑 -RiGan 癸 -LeiShen 财 -Top 8
```

- 检查 `案例项目库/` 与其 `_metadata_index.md`；缺失显式报告，不静默更换路径。
- 只把行首真实 META 当候选，排除模板、README 和讲解用的伪命中。
- 默认任一维命中后评分；严格匹配用 `-Strict`，占类别名仍自动互认。
- 案例索引零命中时，回退读取 `case-*.md` 的真实 META；无候选就如实声明，不硬套。
- META 缺失时读取案例正文；不能编造评分和搜索结果。

**经验检索**改为条目粒度，不再让一份多条规则的文件只占一行索引：

```powershell
python -X utf8 tools/search-experience.py --query "铸印 救神" --category 健康占 --limit 8
python -X utf8 tools/search-experience.py --query "空亡 填实" --all-terms --limit 8
```

- 已整理 808 个检索单元作为初始批注；这些不是 808 条独立验证规则。新原文自动分段进入“未整理待核”。
- 查询标题、方法标签、摘要与原文；支持占类别名和常见写法。默认任一词命中后按相关性排序，通用及待分类片段不会被占类硬过滤。
- 输出条目 ID、来源行号、原文摘要、验证身份、限制、同源组，以及关联的条件差异和冲突。命中后 read 原文及上下文；不能只看摘要。
- 同源复写合并显示，条件不同或仅相似的技巧不自动合并；案例与经验的同案引用不增加独立支持次数。
- 经验不套用下面 E4 的案例评分，不按“反馈=验”排除书籍、优秀作业或反例；相关性不是置信度。
- 历史“验”须核对实际反馈范围及当前问题、类神、空墓旺衰和年命，不能直接采信旧结论。
- 无命中时拆短关键词或取消占类，必要时补查原书；不能把一次检索无命中写成没有该经验。
- `search-cases.ps1 -Scope exp` 已转到新入口，`-Scope all` 分开输出案例分表和经验条目。
- 批量 DeepSeek 无 shell 权限时，由调度器生成本阶段 `*-experience-retrieval.json`；亲自 read 证据包及原文，仍禁止子智能体，不冒称自己调用了脚本。
- 原文每次按哈希检查；旧引用失效即移出旧批注并报告，新原文只标待整理。归档后由脚本刷新运行索引，冻结整理快照保持不变。

详细证据与归档去重规则见 [experience-retrieval-v2.md](refs/experience-retrieval-v2.md)。

''' + s[b:];p.write_text(s,encoding='utf-8',newline='\n')
edit('.opencode/skills/liuren-extract/SKILL.md',[
 ('课体+占类+发用三者一致即重复','同案+同义+同条件才判重复，课体+占类+发用只作召回线索'),
 ('写入前，在已有经验日志和案例库中 grep 搜索相同关键词组合。**课体 + 占类 + 发用 三者一致即视为重复，跳过。**','写入前，使用 `python -X utf8 tools/search-experience.py --query "规则关键词" --limit 8` 检索旧条目并读取原文，同时核对来源编号及关联案例。批处理无 shell 时读取调度器提供的本阶段经验检索包。**同案、同义、同条件才只挂接旧条目；相同课体、占类、发用不等于同一事件或同一规则。** 有新条件、反例或不同独立案例时分别登记；记录已有条目ID和真实出处，不重新包装相同经验，不增加独立验证次数。经验日志可保留本案复盘与引用记录，无新发现时明确写明。'),
])
p=root/'.opencode/skills/liuren-extract/SKILL.md';s=p.read_text(encoding='utf-8');s=s.replace('> **主流程 6.5B（古籍蒸馏经验）**：查询 `经验日志\\古籍-*.md` 和 `提取-*.md`（已蒸馏的古籍经验 + 从其他书籍提取的经验），用 grep 搜索 META 标签行，命中后读取该条目全文；META 匹配不到再降级搜索正文关键词。**本 skill 就是这些文件的产生者与维护者。**','> **主流程经验检索**：使用 `tools/search-experience.py` 的条目级索引查询案例经验、书籍方法和反例；命中后读原文及上下文。详见 [经验检索规则](../liuren-cases/refs/experience-retrieval-v2.md)。本 skill 维护原始经验，脚本维护检索层；技巧分类与置信度分开。')
s=s.replace('> 重新生成 `经验日志\\_metadata_index.md`——否则 `liuren-cases` 的检索器**读不到新条目**。','> 兼容重建旧 `经验日志\\_metadata_index.md`；另运行 `python -X utf8 tools/search-experience.py --refresh --status` 更新条目级运行索引。新内容自动标“未整理待核”，不伪装已完成语义核验。')
s=s.replace('保证主流程 6.5B 的 `grep "^<!-- META:.*占类=健康占.*课体=铸印"` 能一击命中','保留原文的占类和条件信息，供条目级索引及旧工具兼容读取；新主入口为 `tools/search-experience.py`')
p.write_text(s,encoding='utf-8',newline='\n')
print('已更新三份skill的检索、迁移与去重入口')
