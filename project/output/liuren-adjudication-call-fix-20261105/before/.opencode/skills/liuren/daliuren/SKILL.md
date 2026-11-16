---
name: daliuren
description: 本机大六壬单事与分类研判；课势定侧重、察类循气、制化裁决；保留14项必查与按问16专项。
---
# 大六壬主入口
版本 `20261105-subagent-adjudication-04`。本版保留无案例库、经验库设置，并将裁决交给独立子智能体；完整逐条回源审查和独立预测效果验证仍未完成。

以理气贯穿全局，以本问定侧重；类象可在原法占类、位置、真假空陷、气态和制救条件成立时参与取类、切题组合及结果，不能凭孤立名象翻判，也不一律压为事后描写。阶段1只形成待核初势，不冻结成败。

用可靠程序盘推动判断，先保留原问、成功标准、期限、已核背景与未知。原问事实、常识假设、盘推、原案反馈及运筹分开。使用liuren_chart；同卦盘有效则复用，不由模型重排，不补造年命。

## 实际专业主线
按当前争点用liuren_materials action=method逐模块读取全文，读后运用；同版同上下文真实已读内容复用，不先加载全计划。依赖ID表示需掌握的规则，不证明已采用。实际截断按精确路径和位置补读，不缩规则。

| 宏阶段 | 工作 | 必查模块 |
|---|---|---|
| 1 | 初看课势，依问定侧重 | class-mapping, positioning, relations, liqi, structure |
| 2 | 察类辨用，循气取象 | void, bashajiubao, engine-shensha-output, shensha-focus, shensha-use, movement |
| 3 | 资料核证，子智能体裁决，完整交付 | evidence, adjudication, report |

取类时若需神将同用/互换或神将义，shenjiang-use、shen-symbols、jiang-symbols可在阶段1定位前读取；后续复用。关系和理气基础规则可按依赖先掌握，这不表示先冻结取用或结果。涉及年命才在有明确输入时核nianming。阶段3先按任务核timing/quantity/quantity-sources，再用evidence核盘面与原法材料，按adjudication契约以全新task调用liuren-adjudicator独立裁决，最后report交付。主智能体不再形成暂定或最终主判；子智能体模型DeepSeek V4.1 Flash、高思考。缺项补齐后重新独立裁决，不由主智能体代裁。等级不一律归取数。

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

对照规则：本次研判不调用案例库、经验库，不执行retrieve、cases/experience扫描，也不回读两库原档、历史快照或旧检索缓存；不从其他入口绕取相同库资料。evidence仍必读，用于本盘依据、原书条件与最强反证的自核。原书查证、当前方法及其内置书例、研究附加规则身份核对均保留；不是清除既有知识的空白模型实验。有效新条件仍须回核主线。报告明确“本次按对照设计未检索案例/经验库”，不能称检索失败或全库无匹配。

主智能体依问整理取用、气态、关系及原法条件，不夹带初判、倾向或已知答案；正反材料按盘位／稳定ID排列。同一输入只裁决一次；新增事实或发现错误才补材料重裁。子智能体返回后保持其结论和精度，不自行折中、降档或改判。

交付完整专业正文，直接回答子问，列主要依据、最强反证、采用理由、来源和实际缺口，不强制判断JSON。同卦追问只补受影响争点与依赖，保留旧报告修订轨迹。prepare/read/check仅可选工程审计。

案例查询/反馈维护、资料提取分别分流liuren-cases、liuren-extract；Skill发现不等于写权限已具备。写入维护须使用有任务授权的Build模式。本轮仅大六壬占事，年命/行年及正常应期按输入另核；long-period仅长期占事，不自动转出生运限。
