# 合成数据与完整交接样例

全部为工程合成材料，不涉及真实客户，不包含模型预测。`example-provenance.json` 记录实际生成状态；原排盘、标准化事实、AI视图与工具回执来自恢复55版的真实确定性调用。

| 文件 | 用途 |
|---|---|
| synthetic-chart-input.json | 可重新送给排盘工具的无人物输入 |
| original-engine-archive.json | 原页面JSON导出及适配附注，保留完整12宫/四课/三传 |
| normalized-chart-result.json | 标准化事实、校验、来源、采用神煞与基础状态 |
| ai-chart-view.json | AI实际接收的结构化盘面视图 |
| lookup-receipt.json | 五行/十二状态/六亲等查询输出 |
| strength-receipt.json | 已选合成对象的单宫旺衰计算输出；不能解释成预测概率 |
| field-dictionary.json | 1148个实际字段路径、类型和数组结构；专业用途见引擎接口说明 |
| synthetic-handoff/ | 测试构造的同run读取/计算/正文提交/五项review/一次recheck状态；没有真的原生子调用 |

合成报告由测试写入，不是AI专业裁决。native ID 使用fixture值，仅检验合同/状态机；不能把它当独立模型实际执行证据。原问/题意也明确为工程传输验收。需要重新生成时，先恢复55副本并运行说明中的传输测试，再运行 `node audit/generate_examples.mjs <恢复副本根>`。

样例里保存的绝对路径只是本次生成位置，重放时应重新排盘取得新的归档路径和hash，不能直接沿用不存在的旧路径。正文、审核和回执必须在同一个新run中产生。
