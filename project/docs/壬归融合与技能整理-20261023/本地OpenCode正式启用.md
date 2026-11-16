# 本地 OpenCode 融合新版正式启用

> 历史启用记录：本页描述 `20261023-local-active-01`。当前本地版已于同日更新为 `20261023-modular-02`，见[重整与启用说明](../六壬技能结构重整-20261023/重整与启用说明.md)。下方规模、平铺路径及“八字字节不变”等陈述只代表当时状态。

2026-10-23：用户明确要求启用本地新版，并将旧版移出 Skill 配置文件夹。当前项目已完成切换。此前《本地实施交付》中“候选未启用”的状态是切换前记录，不再代表当前本地状态。

- 启用版本：`20261023-local-active-01`。
- 方法包版本：`da713e002642e279bbf04ae8cc4fbcf5d86f4234c8c87396c1e19f6a2d325648`，对应此前 enhanced 候选，术理正文未在本次启用中重写。
- 当时入口（现已备份）：[daliuren/SKILL.md](../../output/六壬技能结构重整-20261023/20261023-modular-02/backup/skills/daliuren/SKILL.md)。
- 启用指针：[liuren-active.json](../../.opencode/liuren-active.json)。
- 完整方法包：[runtime/liuren/20261023-local-active-01](../../runtime/liuren/20261023-local-active-01)。位于 Skill 发现目录之外，保留完整引用和来源；不是另一个自动注册的 Skill 树。

## 活动目录

`.opencode/skills` 中大六壬相关的正式 Skill 仅保留四个新版入口：

| 名称 | 功能 |
|---|---|
| `daliuren` | 统一排盘分流与单事融合研判；读取同一方法包的18个模块 |
| `liuren-cases` | 新版证据检索；明确要求案例维护时读取配置目录外的完整规程 |
| `liuren-extract` | 资料提取维护的新路由入口；完整原规程保留为外部参考 |
| `liuren-tuiming` | 出生推命的新路由入口；完整原规程保留为外部参考 |

旧方法名如 `sanbu-duanke`、`kaoshi-panduan`、`keti-qishi` 等21个子 Skill 已撤出活动目录，不再注册为独立 Skill；对应知识由新版总入口直接按模块加载。旧正文不留在这些活动路径中，也没有通过修改后缀留在活动目录。八字的三个 Skill 文件保持切换前字节不变。

提取和出生推命的专有方法未被单事方法替代；新版功能入口按任务读取配置目录外的完整原规程。不得据本次入口切换宣称这两个功能已重新完成术理设计。

## 完整备份与验证

旧稿完整备份位于：

`output/壬归融合实施-20261023/20261023-local-active-01/backup/skills/`

该目录包含切换前全部28个 Skill 的完整文件；逐文件哈希与原状态一致。被替换的25个六壬 Skill 的旧正文全部移出活动目录。切换过程中短暂使用的新版兼容入口，以及提取/推命旧目录的原文件，另保存在同次输出下 `retired-during-finalization/skills/`，不参与 Skill 发现。

Windows 曾拒绝整体目录重命名，首次切换原样恢复后，采用逐文件迁出；没有修改 ACL 或终止 OpenCode。用户随后关闭 OpenCode，最终旧子目录的空壳也已清理。操作没有递归删除旧稿。

验证结果：

- 完整方法包93个文件、18个模块、2744段迁移映射及模块链接校验通过；与冻结候选的方法版本一致。
- 四个最终入口的 YAML 和基本结构经官方 Skill 校验器检查。
- 本机 OpenCode `1.18.29` 的 `debug skill` 实际返回四个新版入口的位置和内容；每份内容均含启用版本，21个撤出名称均不再出现。
- 活动文件集合和哈希、完整备份哈希、入口引用、项目 `opencode.json` 未变均已核对。
- 没有调用付费模型；本次证明本地发现、入口加载和完整性，不证明预测准确率提升。没有应用本次科目三复盘提出的新术理修订。

最终收据：[opencode-discovery-receipt.json](../../output/壬归融合实施-20261023/20261023-local-active-01/opencode-discovery-receipt.json)。目录清单：[final-layout.json](../../output/壬归融合实施-20261023/20261023-local-active-01/final-layout.json)。

本次只更新当前项目的本地 OpenCode。网站、worker、服务器、数据库和生产知识包没有切换。

## 使用与后续核对

重新打开当前项目的 OpenCode，使用新会话。旧会话中已加载的旧规则或已知反馈仍是旧上下文；本次文件切换不清除历史消息。

复查命令（不调用模型）：

```powershell
python -X utf8 tools/activate-liuren-opencode.py verify
python -X utf8 tools/activate-liuren-opencode.py verify-opencode
```

`activate`、`finalize` 是本次事务的一次性操作，已启用时不得重复覆盖。若需回退，先按 `final-layout.json` 核对当前文件，另存新版，再仅恢复备份中对应的25个六壬目录和启用指针；不要覆盖八字或其他后续改动，不使用 `git reset`。原始备份必须保留。
