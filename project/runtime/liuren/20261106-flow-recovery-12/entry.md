---
name: daliuren
description: 本机大六壬单事与分类研判；课势定侧重、察类循气、制化裁决；保留14项必查与按问16专项。
---
# 大六壬主入口
版本 `20261106-flow-recovery-12`。本版保留无案例库、经验库设置，明确主智能体准备、子智能体裁决、主智能体采信交付的边界；完整逐条回源审查和独立预测效果验证仍未完成。

以理气贯穿全局，以本问定侧重；类象可在原法占类、位置、真假空陷、气态和制救条件成立时参与取类、切题组合及结果，不能凭孤立名象翻判，也不一律压为事后描写。阶段1只形成待核初势，不冻结成败。

用可靠程序盘推动判断，先保留原问、成功标准、期限、已核背景与未知。原问事实、常识假设、盘推、原案反馈及运筹分开。使用liuren_chart；同卦盘有效则复用，不由模型重排，不补造年命。

## 实际专业主线
按当前争点用liuren_materials action=method逐模块读取全文，读后运用；同版同上下文真实已读内容复用，不先加载全计划。依赖ID表示需掌握的规则，不证明已采用。实际截断按精确路径和位置补读，不缩规则。

| 宏阶段 | 工作 | 必查模块 |
|---|---|---|
| 1 | 初看课势，依问定侧重 | class-mapping, positioning, relations, liqi, structure |
| 2 | 察类辨用，循气取象 | void, bashajiubao, engine-shensha-output, shensha-focus, shensha-use, movement |
| 3 | 资料核证，子智能体裁决，完整交付 | evidence, adjudication, report |

取类时若需神将同用/互换或神将义，shenjiang-use、shen-symbols、jiang-symbols可在阶段1定位前读取；后续复用。关系和理气基础规则可按依赖先掌握，这不表示先冻结取用或结果。涉及年命才在有明确输入时核nianming。阶段3先按任务核timing/quantity/quantity-sources，再用evidence核盘面与原法材料，按adjudication契约以全新task调用liuren-adjudicator独立裁决，最后report交付。主智能体准备到可裁决：核取用候选、状态、关系和原法条件，不预先完成全部矛盾取舍；子智能体模型DeepSeek V4.1 Flash、高思考。格式问题在原任务修复；真实缺材料或具体事实/引用错误按一次有据补核规则处理，不由主智能体代裁。等级不一律归取数。

| 条件模块 | 触发条件 | 最早读取位置（已读复用） |
|---|---|---|
| daliuren-paipan | 需要起课或核对程序盘 | 阶段1，class-mapping前 |
| nianming | 涉及本命或行年规则的计算、核验或采用 | 阶段1，class-mapping前 |
| rule-semantics | 否定范围、摘要条件或规则强度存疑 | 阶段1，positioning前 |
| liqi-sources | 所采用方法存在来源或口径分歧 | 阶段1，positioning前，先于可能提前加载的liqi |
| risk | 四大凶象承担主判或最强反证 | 阶段2，movement前 |
| shensha-tradition | 采用季煞或传统神煞层级说明 | 阶段2，bashajiubao前 |
| quantity | 原问要求金额、分数、数量、重量、距离等数值，或已选应期专法需要数理时长 | 阶段3，evidence前 |
| quantity-sources | 需要核对取数数表、原法条件或精确数值案例；已取得对应原书可复用 | 阶段3，evidence前 |
| timing | 有时间任务 | 阶段3，evidence前 |
| shenjiang-use | 采用神将同用、互换，或需要核对具体神将类义的适用范围 | 阶段1，positioning前 |
| shen-symbols | 需查十二天神的基础义、复合取义或与本家天将的差别 | 阶段1，positioning前 |
| jiang-symbols | 需查十二天将的职能、占类取义或与本家支神的差别 | 阶段1，positioning前 |
| mapping-provenance | 需核合并对应、旧 I/B 上下文、原卡或未决条件 | 阶段1，positioning前 |

16专项按本问选择：finance、recruitment、promotion-salary、relationship、interpersonal、period-outlook、long-period、pregnancy、exam、illness、lost-person-object、classical-conflict、home、travel、weather、agriculture。专项缺条件时标缺口，不套邻类。纯排盘只读daliuren-paipan。十一原环节是reading-route.json的legacyCoverage覆盖映射，不是11次强制固定跳转；八煞九宝和32项等14项必要任务均保留。

对照规则：本次研判不调用案例库、经验库，不执行retrieve、cases/experience扫描，也不回读两库原档、历史快照或旧检索缓存；不从其他入口绕取相同库资料。evidence仍必读，用于本盘依据、原书条件与最强反证材料的核证，不预先裁完全部矛盾。原书查证、当前方法及其内置书例、研究附加规则身份核对均保留；不是清除既有知识的空白模型实验。有效新条件仍须回核主线。报告明确“本次按对照设计未检索案例/经验库”，不能称检索失败或全库无匹配。

主智能体依问整理已核材料，以focus_issues引用观察ID列关键中性争点，不夹带初判、倾向或已知答案，不凑正反。裁决者对照完整盘复核取用、查漏补J实体，再裁关键作用；每条依据展开一次。主智能体返回后核事实、引用、问项与争点覆盖及报告一致性，复用裁决理由和结论，不重新权衡折中。格式错误不重裁；具体事实/引用错误或新材料按12版一次补核，细节见adjudication。

交付完整专业正文，直接回答子问，列主要依据、最强反证、采用理由、来源和实际缺口，不强制判断JSON。同卦追问只补受影响争点与依赖，保留旧报告修订轨迹。prepare/read/check仅可选工程审计。

案例查询/反馈维护、资料提取分别分流liuren-cases、liuren-extract；Skill发现不等于写权限已具备。写入维护须使用有任务授权的Build模式。本轮仅大六壬占事，年命/行年及正常应期按输入另核；long-period仅长期占事，不自动转出生运限。

本版交接采用input/output-v2（focus_issues、scope_review、issue_resolutions），文件协议仍为v1。裁决委派先用liuren_adjudication_packet保存中性packet对象，再把返回task_prompt原样给task；不要手写JSON字符串或把长上下文塞进task。裁决者通过专用工具读完当前文件才可交付。细节见adjudication。

课盘交接优先用chart={source,archive:{path,sha256}}：路径和哈希原样取liuren_chart返回的archive，由程序读完整facts。无归档时才原样复制facts（含liuren-chart-facts-v1的内层schema），不重组字段；盘推放observations，未知不补。method_materials最多40条，总输入10万字符，不静默删材料。报错按完整字段路径修正，不改外层包装、不用空盘试探。


09版程序事实与专法交接：先复用liuren_chart的program_facts；必要时liuren_compute按关键节点查。packet每问声明tasks，位置省略或@program，解释不用chart_checked；来源按行段/hash自动装配。应期取数全文随tasks自动进入裁决文件，返回检查special_methods。完整接口见references/deterministic-tools.md；程序不裁吉凶，原专业方法、无两库与主子分工保留。



12版执行规则：主智能体准备中性材料，独立裁决者裁关键作用，主智能体忠实交付。每问tasks必填，task_basis逐项注明user_requested及原问逐字request_quote，或necessary及具体理由；只给占时不等于问应期，不为完整性默认增加应期/取数。程序保留原问并提示明确亲属标签冲突，不替代专业取用。日干不能改成寄宫支来过校验。

先按当前路由读必查与触发专项；同版同上下文已读可复用。packet保存前核准备阶段必查回执，缺哪项只补哪项。report在交付前读。来源按行段/hash交程序装配，quote可省略；不要反复手抄引文。branch只放干支/纯支组合/戊（寄宫巳），注释放mapping_basis或mapping_review；verification只用method_interpretation/unverified。

packet返回task_prompt原样交新task，不提供task_id，不用background:true，不把上下文塞入task。裁决者逐页读完紧凑文件，使用liuren_adjudication_submit提交结构化结果，末消息仅返回工具回执。格式报错只在原子任务内修对应字段，保持裁决内容不变，最多三次提交；不得重新全盘权衡。含混对象不由程序猜改。程序保留原报告、字段错误、校验产物及hash。

主智能体收到结果后先task_result(task_id=子会话ID)领取并确认，领取同样经过六壬验收；不要用task取结果。失败用liuren_adjudication_result(action=read或repair)查看具体缺口/无歧义格式修复，不能再派整轮裁决。只有needs_input，或原报告中具体事实/引用错误（retry_context.error_path），并补入真实新材料，才可retry_context引用前task_id一次补核；仍失败明示未完成。同材料重复派发由程序拦截。

completed且验收通过，读report后调用liuren_adjudication_result(action=deliver,task_id=子会话ID)，取得绑定结果hash的完整report_markdown，直接交付技术正文；可调排版，不改结论/精度/条件、不添决定性理由。它保留取用、关键作用、反证、争点、应期取数记录与来源。工程通过不证明专业或预测正确。经验库、案例库仍不介入，原书、全部专业方法和正常年命/行年保留。
