# batch_20261019 · 完整包交付说明

> 2026-10-19 ｜ 身份：初级资料，未统一分析，未正式入库 ｜ 盘图已全量转录

## 一、包结构

```
stage1_ready_v1/
  cases/                        243 个案例（七节模板，单一 text 原文块）
  image_ledger.json            263 张盘图台账（seq/file/sha256/time_norm）
  source_manifest.json          来源清单与哈希
  charts/v7/                    243 个盘面 JSON（217 可用 / 11 待核 / 15 冲突）
  analysis-ready/public/        217 个初判输入（无作答/反馈/评语）
  analysis-ready/private/       243 个私有包（作答/评语/反馈/原文定位）
  analysis_manifest.json        调度总清单（含 alias 映射、阻塞原因）
  review_queue.json             26 条待核清单
  ledger.json                   逐来源状态账本
  checkpoints/                  检查点
```

## 二、真实数字

| 项目 | 数量 |
|---|---|
| 采集来源 | 243 |
| 独立案例 | 243 |
| 有作答材料 | 222 |
| 有明确标注反馈 | 14 |
| 盘图转录 | 263 张（课盘 245 / 异体系与其他 18） |
| **可直接首次分析** | **217** |
| 待核 | 26 |

## 三、26 条待核明细

| 原因 | 数量 | 说明 |
|---|---|---|
| 四柱冲突 | 12 | 多数为**子时换日差异**（图按夜子时、程序按子初换日），如 0044、0100、0204、0240；另有少数疑似录入偏差（如 0012 年柱图作乙丑、程序乙巳） |
| 无起课时间 | 7 | 原图被裁切或缺时间行（如 0063、0210），不推测 |
| 月将冲突 | 3 | 换将规则差异（中气换将 vs 交节/日躔），如 0003、0028 |
| 时间写法不支持 | 3 | 中文数字年份、斜杠日期等，脚本未覆盖 |
| 时间约定待核 | 1 | 含农历/真太阳等约定 |

全部并列登记双方数值，未改图、未改原文、未用 `--accept-confirmed` 绕过复核。

## 四、公开/私有隔离

- 公开包：`case-<hash10>.json`，字段仅 `question` / `people_declared_in_question` / `facts` / `chart_assumptions` / `missing_inputs`
- 私有包：243 个，与案例一一对应；含逐份作答、徽章评级、评语正文、反馈原文、待核、哈希
- 独立校验 `validate_ready.py`：**0 错误**（来源归属、编号一致、原文逐字、作答完整性、图像哈希、盘面状态、公私配对、泄漏扫描）

## 五、使用方法

1. 调度器读 `analysis_manifest.json`，取 `ready_for_first_analysis=true` 的 217 条
2. 初判模型**只读**对应 `analysis-ready/public/case-xxxxxxxxxx.json`
3. 初判冻结后，再给 `analysis-ready/private/` 下同名文件
4. 总清单不要整份发给初判模型

## 六、遗留

- 26 条待核需人工复核（子时换日、换将规则、缺时间），不自动放行
- 隔离区：`raw/records_quarantine_20261019.jsonl`（56 条并发事故数据）、`pan_quarantine/`（31 张），未删除，不得直接复用
- 同 seq 多课盘（79、96、180）已按首张取时间并在待核事项注明，主图待核定
