---
name: daliuren
description: 用于本机大六壬问事、代问、分类占断和同卦追问；可靠程序盘、14项必查、16专项、中性文件交接独立裁决及完整技术报告。
---
# 大六壬主入口
版本 `20261106-handoff-chain-20`。本版保留无案例库、经验库设置，明确主智能体准备、子智能体裁决、主智能体采信交付的边界；完整逐条回源审查和独立预测效果验证仍未完成。

以理气贯穿全局，以本问定侧重；类象可在原法占类、位置、真假空陷、气态和制救条件成立时参与取类、切题组合及结果，不能凭孤立名象翻判，也不一律压为事后描写。阶段1只形成待核初势，不冻结成败。

用可靠程序盘推动判断，先保留原问、成功标准、期限、已核背景与未知。原问事实、常识假设、盘推、原案反馈及运筹分开。使用liuren_chart；同卦盘有效则复用，不由模型重排，不补造年命。

本版事件定位：主智能体理解原问时，自然分清发生什么事、实际涉及谁或什么、双方职责和目标，再依该占类的专法确定干支与关键类神。代问者不自动成为事件当事人；考试围绕实际考生，疾病围绕实际患者，婚配、攻守、胎产等保留专项对待轴。将必要取用理由融入正常分析，不另设角色表、人物身份核验阶段或模型调用。裁决者在正常研判中沿用事件语境，遇到具体取用错误才纠正并重核受影响作用，不为确认主体另派一轮。程序不以考试/疾病类别强绑日干，不做亲属称谓推断或输出角色锁定；仅保留资料分类读取、文件版本和确定性盘面/计算校验。

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

主智能体依问整理已核材料，以focus_issues引用观察ID列关键中性争点，不夹带初判、倾向或已知答案，不凑正反。裁决者对照完整盘复核取用、查漏补充必要取用，再裁关键作用；每条依据展开一次。主智能体返回后核事实、引用、问项与争点覆盖及报告一致性，复用裁决理由和结论，不重新权衡折中。格式错误不重裁；具体事实/引用错误或新材料按当前协议一次补核，细节见adjudication。

交付完整专业正文，直接回答子问，列主要依据、最强反证、采用理由、来源和实际缺口，不强制判断JSON。同卦追问只补受影响争点与依赖，保留旧报告修订轨迹。prepare/read/check仅可选工程审计。

案例查询/反馈维护、资料提取分别分流liuren-cases、liuren-extract；Skill发现不等于写权限已具备。写入维护须使用有任务授权的Build模式。本轮仅大六壬占事，年命/行年及正常应期按输入另核；long-period仅长期占事，不自动转出生运限。

工具交接及失败恢复按自动加载的《本机六壬高效执行》当前协议；字段查当前references/deterministic-tools.md。协议采用输入v2、灵活报告、文件v1。收到成功回执后领取并交付，不将回执当最终报告，也不重复派裁决。

工具参数不靠猜：每个questions成员必填domain/tasks/task_basis；method及完整book_search返回的handoff原样加入method_materials，同一id仅一次。工具接受工作区内合法绝对路径并规范化；不能擅改hash或行号。保存成功才传task_prompt给task，成功裁决只领取与交付。完整字段和错误恢复见自动加载的《本机六壬高效执行》“工具参数速查”。


## 报告传输边界（本版）

裁决报告采用灵活表达：liuren_adjudication_submit({result: 报告正文字符串或自由JSON对象})。无需output-v2、固定分析字段或application五项表；程序不补写、不删改、不以缺字段拒收。依据、关键作用、反证、条件题、应期取数按实际问题说明，条件未满足可自然说明不答。需要补资料时可提交对象并标status="needs_input"、说明缺项。成功后末消息返回工具回执；主智能体用task_result领取，read查看原报告，读report后deliver领取原样报告与hash。只有非空、可保存、容量及任务归属/文件完整读取等传输检查；contractChecked仅兼容旧回执，validationScope="transport-only"、professionalContentChecked=false明确不作专业验收。不得为格式差异重派裁决。
