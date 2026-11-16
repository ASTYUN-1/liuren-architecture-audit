# movement 神煞身份校验修复候选

日期：2026-11-16。基线：独立架构审计仓库原始提交 `0807cda14705d6b092571a1242bdc647da42368b`。

## 已核实的问题

`project/tools/liuren-strength-engine.mjs` 原第 259 行允许显式 `rule.mode === 'movement'` 绕过默认的马星名称识别。只要该 ID 存在于传入的已采用神煞表，月破等非马神煞也能进入第 261 行的长生动象损耗计算。

新增测试仅使用 `examples/normalized-chart-result.json` 的合成盘，固定为戌月并调整天地盘为辰加申，同时同步四课、月将和三传坐标。按包内采用表重新解析后，`S15 月破` 确实位于辰，辰对所临申的状态为长生。

修复前，在这个合成条件下，显式指定月破为 movement 得到损耗 `0.24079440173424438`，没有报错。该数值来自本次合成输入，与外审所报 `0.30180915796588936` 的输入不完全相同，不能声称重复了后一个精确值。两者指向相同的身份校验缺口。

## 修改边界

- 自动识别与显式 movement 适配共用原来的名称模式 `(驿马|天马|丁马)$`。
- 显式 movement 对非马名称直接报错，校验发生在占题 goal.mode 判断之前。
- 保留既有“必须位于已采用表”的 ID 校验；未改变上游采用表的可信输入合同。
- 不改损耗公式、系数、旺衰状态、取表方法或正式专业规则。

当前包内采用表登记的马星为 `S03 日驿马`、`S04 天马`。驿马与丁马的正向测试采用明确的合成已采用项，只验证既有接口的名称兼容性；没有向正式采用表新增丁马或其他条目。

## 验证

新增 12 项测试：月破、太岁、日德在 movement/external 两种占题模式下均拒绝错误 movement 适配；日驿马、驿马、天马、丁马保持显式与自动路径一致；普通非马项不产生隐式马星损耗；不在已采用表的 ID 继续被拒绝。

修复前新增测试：6 项通过、6 项因“没有抛出异常”失败，并记录了实际损耗。修复后以下命令 64 项全部通过：

```powershell
cd project
node --test tools/tests/liuren-strength-movement.test.mjs tools/tests/liuren-strength.test.mjs tools/tests/liuren-shensha.test.mjs tools/tests/liuren-palace-strength.test.mjs tools/tests/liuren-strength-review.test.mjs
```

另尝试 `tools/tests/liuren-strength-quantity.test.mjs`，因包内没有 `.opencode/node_modules/@opencode-ai/plugin/dist/index.js` 而在模块加载时失败。该 SDK 缺口已在原包完整性报告中列明；本次没有安装依赖，也不将这套测试计为通过。

## 审计快照与发布状态

本修复只存在于独立修复分支。原始 ZIP、主分支快照、本机活动源码、活动指针、冻结 runtime、规则及原书均不改动。

包内 `SHA256SUMS.txt`、`FILE-MANIFEST.*` 和活动指针的源码绑定保留原始审计身份。因此本分支的引擎源码不再匹配原快照清单，这是有意保留的候选补丁差异；不能将本分支宣称为已经重新绑定、预检通过或部署的正式版本。正式采纳及重新发布另行审查。
