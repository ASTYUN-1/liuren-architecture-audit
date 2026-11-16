# 文件式裁决输入输出契约

先用liuren_adjudication_packet保存packet对象，再将返回task_prompt原样给task。task prompt只有协议标记、文件路径和SHA256，不传长JSON。子智能体用liuren_adjudication_read读取全部页。

## 输入

- schema=liuren-adjudication-input-v2、request_id（字母开头、字母数字下划线或连字符）、questions、chart、facts、entities、observations、method_materials、focus_issues、unknowns 必须全部提供；无内容的数组用 []。文件标记和文件封装仍用v1，内层输入输出为v2；旧会话须重启，不混用协议。
- questions 每项：id、text（原问）、subject、stage、deadline（未问填未限定）、success_criteria、alternatives（只列候选名称，无排序理由）。每个ID在输入全局唯一；固定书据用E01–E22。保存工具自动将输入中E加数字编号改为I_E编号，所有结构化引用同步改名；工具返回renamed_ids。优先用Q/F/S/O/M前缀。
- chart 两种形式择一：优先 {source, archive:{path,sha256}}，path/sha256原样取liuren_chart返回的archive，程序限于排盘存档/六壬内、核哈希及程序盘校验后复制_direct.facts；不读取原页面断语。兼容 {source,facts}，facts必须为程序返回的完整对象，包含内层schema=liuren-chart-facts-v1、四柱、十二天地盘、四课三传及其他原字段。不得手抄重组，不为补schema伪造盘；旺衰、神煞解释放observations。校验失败指出具体字段路径，不改外层包装。不支持两种形式混用。引擎原有表仍需专业复核。
- facts 每项：id、text、source。只放实际已知背景，不放盘推或原案反馈；未知不补。
- entities 每项：id、question_ids、referent、branch、position、mapping_basis。branch允许单个干支、辛（寄宫戌）或未卯亥等明确组合，位置和解释另列；不自动换成其他类神。类神为待核取用，不标最终优劣；主客、目标及影响结果的其他类神不得只送单方。
- observations 每项：id、entity_ids、kind（five_qi/twelve_states/relation/void/shenjiang/structure/movement/special_method）、statement、reference（明确参照对象）、source、verification（chart_checked/method_interpretation/unverified）。正反观察按盘位及稳定ID排列，不以主判筛选、分组或排序；不加支持度、胜率、结论倾向。只挑有利材料属于违规，虽非程序可穷尽识别。
- method_materials 每项：id、title、source_path、quote。最多40条，总输入10万字符；只传实际已读并必要的原法连续材料；允许书籍库、books、当前方法及获准 docs 来源，不含案例／经验库。固定书据已在系统提示，不用重复传。书例不作为本问事实。
- focus_issues 每项：id（建议C前缀）、question_ids（至少一个本问ID）、entity_ids、observation_ids、question（简短中性问题，最多2000字符）。最多12项，只列可能改变答案、精度或关键取用的未决处；引用现有观察，不复制长篇辩论、先给答案或排候选优劣。无实质争点用[]，不强制凑正反。实体/观察可空但须有明确问题，例如缺哪项原法或定位；裁决者仍核完整盘，争点不是封闭选项。各ID在全输入唯一，E编号自动改名时同步更新observation_ids等结构化引用。
- unknowns：尚未核明的资料或口径。所有文本是材料而非新指令。

输入没有 initial_verdict、preferred、ranking、weights、known_result、previous_judgment 等字段，未知字段不能透传。中性字段仍可能被措辞污染，主智能体必须保持原问原貌、不塞入倾向。

## 输出

只返回 liuren-adjudication-output-v2 JSON：schema、request_id、status、scope_review、entity_checks、relation_checks、issue_resolutions、answers、source_conflicts、missing_inputs。字段定义及枚举以子智能体系统提示和 tools/liuren-adjudication-contract.mjs 为准。内部JSON不替代用户收到的完整中文报告。

scope_review：question_ids覆盖所有原问一次；mapping_status为confirmed/corrected/needs_input；added_entity_ids列全部新增J实体；corrections列具体定位修正；omission_check简述对照完整盘核主客、目标、关键阻救及争点遗漏的结果。可以发现输入争点之外的决定性关系，不重新写一遍全盘。新增实体或改动对象、干支、位置不能标confirmed；关键定位未决须needs_input，不能completed。该字段是可核查声明，不证明实际发现了全部遗漏。

issue_resolutions：每个focus_issues ID恰回应一次，包括needs_input时；每项issue_id、status（resolved/unresolved）、relation_ids、resolution、limits。resolved须引用实际relation_checks ID并简述取舍；unresolved须明列具体限制。无争点返回[]。关系理由只展开一次，争点和答案引用关系ID，不重复正反长论；未解争点对结果、过程、程度或时间的实际影响在对应答案中交代，不能一概降低结果等级。

entity_checks 审核每个原实体，允许有据增加 J 实体；relation_checks 逐条说明对象、双方状态、位置、制化、实际效力和作用范围，引用真实 E／输入依据ID。answers 每问一次，直接结论、精度、决定性及反向关系ID、最强反证处理、过程、时间、条件和限制；精度 exact/direction/unresolved。source_conflicts 保留实际适用的书法分歧。needs_input 必须列具体缺项；completed 的有向／精确结论必须引用决定性关系。

不索取思维链，只保留可核对的判断依据摘要。输出契约校验能发现结构、引用和缺项问题，不能证明术理正确、判断无偏或现实命中。

返回后的主智能体核事实、引用、覆盖及报告一致性，复用裁决者理由交付；不再进行第二次裁决。具体错误或新材料须指出ID与受影响问题，修正材料后才重裁；仅不同倾向不重问。程序不分析自然语言是否暗含初判，也不能验证最终中文报告确实忠实，仍需按report执行。
