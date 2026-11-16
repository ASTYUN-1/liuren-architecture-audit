# 本地知识库调用链只读审计

102个完整案和本轮155张来源/规范卡已经接入当前本地检索；标准完整判断流程明确要求两路检索。是否命中某卡由查询决定，实际采用仍须模型核条件。本轮没有新库更新后真实模型完整研判的执行证据，也没有网站同步证据。

当前active为`20261027-quantity-02`，活动evidence模块哈希已通过loader核对。检索缓存命中后仍动态加载当前附加层，不受方法包旧日期或旧基础缓存锁死。

## 已核与缺口

- **F1 明确接入**：标准本地入口路由到现行evidence.md；方法包不包含新卡清单限制。经验/案例ensure_index即使命中旧基础缓存仍附加当前overlay，证据实时校验，新增卡不依赖重冻结方法包。
- **F2 字段部分转换与损失**：原卡conditions/exclusions/reasoning_steps/alternatives/evidence_refs在JSON经验entry逐数组一致。status转research_status，claim_origin与status进annotation_status，review_state由source_checked准入及固定verification表达；support/counterexample/source_case_refs等身份汇入case_refs和origin_keys，正反身份区分丢失；legacy_entry_ids和原relations结构不透传，relations转短相关项；规范branch_selector/完整族成员不透传，需按research_card_path读原卡。反证内容仍可见于summary/alternatives，不等于结构化counterexample_case_ids仍在。
- **F3 召回能力限制**：经验只对标题、method_tags、summary和首个证据quote做字面词匹配；不直接索引conditions/exclusions，不做规则前提求值或语义条件推理。真实条件独有短语“原已知状态必须明确”存在但0命中。案例加入原问/背景/主题、方法词和六维盘面结构分，仍非条件推理。条件的采用取舍由模型按evidence规程回读原段完成，当前没有真实模型端验收。
- **F4 有界传输与省略**：标准经验文本保条件/步骤/排除/alternatives全文，源quote前1200字；related摘要260字且至多6个。批处理包保被选规则条件/反证数组，源quote450字、related最多3、总包预算9000字会丢后排整候选；实probe原8候选剩3、丢5，067-RECONCILE未进包而067-TIMING仍在。案例compact仅2段方法各300字、问题650字及预算删项；均只能当定位，需回读全文。
- **F5 悬置与无效证据边界**：当前2张suspended（LR26-LEGACY-017、LR26-K2-006）仍可检索但均有“暂停采用，仅供审查”前缀；不是程序硬过滤。pending/坏hash/quote失配不准入，显式依赖与replacement的失效或悬置会传递阻断；非依赖相关卡不连坐。当前未改证据做破坏性故障注入，失效行为结论依据源码。
- **F6 同案排除probe通过**：排除BK26-MODERN-067后067来源卡及含其依赖身份的规范TARGET-STAGE入口均不返回；排除088后案例不返回。身份传播按已登记原案span和依赖，不以同一本书笼统归同案。未关联转载仍可能遗漏，不等于完全杜绝污染。
- **F7 仅旧批处理的确定缺口**：opencode-case-batch仍强制旧独立skill清单，run模式read白名单含skills/案例/经验/书籍/books/public-inputs，缺runtime及knowledge。当前模块和新卡路径在这些目录，可能无法回读完整资料；与标准本地opencode.json入口不同。本轮不启动或修复旧批处理。
- **F8 未验证的部署与实际研判**：本轮检索probe不等于模型实际读完条件/选择方法/正确迁移。网站adapter走冻结快照，未核在线资源清单，不能说网站已同步。

## 一个实际新卡字段例

`LR26-M102B-067-RECONCILE`被“复合 两天”实际查回。conditions/exclusions/reasoning_steps/alternatives/evidence_refs与原卡逐数组相同，独立验证增量0。原结构字段与转换后字段是否存在见JSON的`field_roundtrip`。

完整适用条件：

- 辛卯反吟卯酉，女戌男未；反馈明确两天后复合男主动

完整反证／其他解释：

- 复合方向有对应，未来再分无访
- 原报男主动复合反不能及不愿；女外情未证
- 问句保存不作原断；年命作用未决
- 反馈明复合，不能无证强改只是联系；未来婚姻/同居及离婚均未知
- 男主动与复合合；长期分闹暴力没有反馈，后泛劝不当个体事实

原`counterexample_case_ids`有本案精确来源身份；检索entry无此同名字段，身份混入case_refs，反证文字仍在上述alternatives。

## 四种事实分开

|层级|本次结论|
|---|---|
|CLI/底层实际检索|新经验卡、完整案例和同案排除probe通过|
|标准本地工作流明确调用|阶段2规程强制要求两路检索，但没有程序确保模型已执行|
|真实模型运行已使用|未验证；本轮仅源码与本地确定性检索|
|网站部署|未核也未部署，冻结快照不能靠本机更新自动获得新卡|

## 证据定位

- `.opencode/liuren-active.json:2` — "release"
- `.opencode/skills/liuren/daliuren/SKILL.md:28` — | 2 明占类
- `runtime/liuren/20261027-quantity-02/methods/evidence.md:3` — 每次完整判断必做
- `runtime/liuren/20261027-quantity-02/methods/evidence.md:10` — python -X utf8 tools/search-cases.py
- `runtime/liuren/20261027-quantity-02/methods/evidence.md:16` — 2. 读有限候选
- `tools/load-liuren-methods.py:22` — def active
- `tools/load-liuren-methods.py:79` — def content
- `tools/search-experience.py:23` — index = ensure_index
- `tools/search-cases.py:24` — index = ensure_index
- `tools/experience_retrieval.py:187` — return apply_experience(cached
- `tools/case_retrieval.py:402` — return apply_cases(cached
- `tools/liuren_research_overlay.py:81` — record_identities =
- `tools/liuren_research_overlay.py:107` — body = {k: card[k]
- `tools/liuren_research_overlay.py:120` — if card['status'] == 'suspended'
- `tools/liuren_research_overlay.py:129` — kind = '冲突待核'
- `tools/liuren_research_overlay.py:159` — label = {k: family[k]
- `tools/experience_retrieval.py:239` — body = normalize(e['summary']
- `tools/experience_retrieval.py:265` — related.append(dict
- `tools/experience_retrieval.py:295` — '原文片段（完整判断
- `tools/experience_retrieval.py:365` — research = {k: e[k]
- `tools/experience_retrieval.py:372` — e['source_excerpt'] = original[:450]
- `tools/experience_retrieval.py:380` — while len(result['results']) > 1
- `tools/case_retrieval.py:457` — qt, goal = tokens
- `tools/case_retrieval.py:322` — method_locations=supporting[:5]
- `tools/case_retrieval.py:545` — row['case'] = {k: r[k]
- `tools/liuren_knowledge_workbench.py:630` — 'eligible_for_search': not errors
- `tools/liuren_knowledge_workbench.py:644` — strict_deps =
- `tools/liuren_knowledge_workbench.py:570` — if ref.get('sha256') != digest
- `tools/opencode-case-batch.py:31` — SKILLS =
- `tools/opencode-case-batch.py:138` — allowed =
- `tools/opencode-case-batch.py:400` — case_packet = case_retrieval.evidence_packet
- `tools/website-retrieval.py:48` — ROOT / '_retrieval/experience-index.json'
- `docs/六壬知识整理-20261102/README.md:47` — OpenCode旧批处理

本轮只读审计；无付费模型、外部网络、全库重验、部署或代码/冻结包修改。探针读取现有缓存，若需重建即报错，未实际重建缓存。

647 eligible仅表示可检索及机械通过，不等于647条可采用；标准本地入口没有record_judgment程序门禁。2张悬置卡的暂停标签必须由模型遵守，retrieve未强制排除。

逐作者review及method-dimensions中的恢复完整性/理由缺口轴未由当前case构造或compact结构化带入候选；需要另读review侧表或源卡限制。
