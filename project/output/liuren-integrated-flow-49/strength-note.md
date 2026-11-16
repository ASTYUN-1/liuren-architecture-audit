
## 49版旺衰工具的按需核查

strength原参数增加可选review:true；默认不输出扩展核查，不改变已有系数、单宫值、补算值、空亡口径或合局暂缓决定。仍先依问取用并说明依据，再提交actors；需要数值增减时给完整links快照。

review返回state_basis（各已选对象五气、十二气参照、旬空/坐空、通达及直接关系）、relation_candidates（仅已声明对象两两关系事实，含刑冲合害；未提交关系不自动算作用）、season_comparison（同一actors/links分别核季土双表，不选择高分表、不平均）。这些是定点查漏工具，不是全盘穷举义务；不应每次自动附review:true。

coverage始终说明提交和实际计算的关系数、未更新其他宫位、未验证专业取用/通路适用性、不能判成败。state_basis.pending_action_conditions是内部作用适配提示；神煞未提供、专项未适配等不得理解为没有作用，也不要求把所有提示变成新待办。

例：在原strength对象中加"review":true即可；其他mode/season_profile/season_basis/actors/links不变。可用single_palace查关键节点的基础与事实，再按原法确认必要关系补算；已有材料足够时直接selected_relations，无须固定多跑一轮。evaluation中的strength也支持review，保持原旬空/研究新旬政策各自身份。

未补入：全盘自动取用、自动通路裁定、成败概率、所有刑冲神煞数值化、三合半合三会数值、自动合化、已校准系数或所有未来兑现机制。定性未量化不等于不参与原法判断。
