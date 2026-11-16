# 八字排盘操作 SOP

## 排盘铁律

> **禁止 LLM 自行推算四柱八字。必须使用 `paipan` npm 包输出。**
> `paipan` 的输出视为权威正确，LLM 不得质疑或纠正。

## 🗂️ 排盘归档铁律（必读）

> **`--out` 输出文件必须写入 `排盘存档/八字/` 子目录**，命名 `八字-YYYYMMDD-HHmmss-备注.json`。
> **禁止写入项目根目录**（防散落、防同名覆盖）。归档规范见 `排盘存档/README.md`。

```bash
# ✅ 正确示例（写入存档库）
node 排盘工具魔改/bazi-paipan/paipan.js \
  --year 1990 --month 6 --day 15 --hour 14 --minute 30 \
  --gender male --city cn-shanghai --pretty --out 排盘存档/八字/八字-20260801-140000-示例.json

# ❌ 错误示例（禁止散落根目录）
--out 排盘结果.json
```

---

## 方式一：CLI 命令行（推荐）

### 公历排盘

```bash
node 排盘工具魔改/bazi-paipan/paipan.js \
  --year 1990 --month 6 --day 15 --hour 14 --minute 30 \
  --gender male --city cn-shanghai --pretty
```

### 农历排盘

```bash
node 排盘工具魔改/bazi-paipan/paipan.js \
  --calendar lunar --year 1990 --month 5 --day 23 --hour 14 \
  --gender male --city cn-beijing --pretty
```

### 参数说明

| 参数 | 必填 | 说明 | 示例 |
|------|:--:|------|------|
| `--calendar` | 否 | 历法：solar(公历)/lunar(农历)，默认 solar | `--calendar lunar` |
| `--year` | ✅ | 年 | `--year 1990` |
| `--month` | ✅ | 月 | `--month 6` |
| `--day` | ✅ | 日 | `--day 15` |
| `--hour` | ✅ | 时（0-23） | `--hour 14` |
| `--minute` | 否 | 分，默认 0 | `--minute 30` |
| `--gender` | ✅ | 性别：male/female | `--gender male` |
| `--city` | 否 | 城市代码，默认 cn-beijing | `--city cn-shanghai` |
| `--leap` | 否 | 农历闰月标记（仅农历模式） | `--leap` |
| `--pretty` | 否 | 格式化 JSON 输出 | `--pretty` |
| `--out` | 否 | 结果直写 UTF-8 文件（**Windows 推荐**，规避控制台中文乱码） | `--out 排盘结果.json` |
| `--liuyue` | 否 | 流年下附带流月数组。⚠️ **默认不加**，输出会膨胀到 ~18000 行。仅在需要流月分析时使用 | `--liuyue` |
| `--liuyue-year` | 否 | 仅输出指定年份的流月（自动启用 liuyue 但只保留目标年数据）。**推荐**替代 `--liuyue` | `--liuyue-year 2026` |
| `--liuri` | 否 | 计算指定日期的流日（干支/十神/旬空），格式 YYYY-MM-DD | `--liuri 2026-08-07` |
| `--lishi` | 否 | 计算指定日期的流时（12时辰），格式 YYYY-MM-DD | `--lishi 2026-08-07` |

### 城市代码参考

> ⚠️ **城市字段强制规则（排盘 400 最常见原因）：**
> 1. **`city` 必须是 `cn-xxx` 城市代码**（下表），**禁止传中文城市名**（如 `city: "北京"`、`city: "上海"`）——`paipan` 包对未知 city 直接抛错，HTTP API 返回 **400**
> 2. 用户只给了中文城市名 → 先查下表映射为代码；**下表未收录的城市 → 不传 city**（默认 cn-beijing），或传最近城市代码
> 3. 紫微（ziwei-paipan）的请求体与八字不同：紫微不传 city、gender 用 `'男'/'女'`——**合参流程中禁止把紫微的参数格式直接抄给八字接口**（八字 gender 用 `'male'/'female'`，city 必须代码）

| 代码 | 城市 |
|------|------|
| `cn-beijing` | 北京 |
| `cn-shanghai` | 上海 |
| `cn-guangzhou` | 广州 |
| `cn-shenzhen` | 深圳 |
| `cn-hangzhou` | 杭州 |
| `cn-chengdu` | 成都 |
| `cn-wuhan` | 武汉 |
| `cn-nanjing` | 南京 |

> 完整城市列表见 `paipan` 包文档。

---

### HTTP 400 错误排障（PowerShell 调用必读）

> **现象**：PowerShell 的 `Invoke-RestMethod` 遇到 400 时抛异常，**默认不显示响应体**——所以只看到 `(400) 请求错误` 而不知道具体原因。

**排障方法（读取响应体中的 error 字段）：**
```powershell
try {
  Invoke-RestMethod -Uri "http://localhost:3457/paipan" -Method Post `
    -ContentType "application/json" -Body $body -TimeoutSec 10
} catch {
  # ⚠️ PowerShell 5.1 实测：$_.ErrorDetails 常为 null，取不到 body——须直接读响应流
  $resp = $_.Exception.Response
  if ($resp) {
    $sr = New-Object System.IO.StreamReader($resp.GetResponseStream(), [System.Text.Encoding]::UTF8)
    $sr.ReadToEnd()   # ← 这才是服务端返回的 error 详情（如 "Unknown city id" + 中文提示）
    $sr.Close()
  } else {
    $_.Exception.Message
  }
}
```
或直接用 Node 调用（能直接看到 body）：
```powershell
node -e "fetch('http://localhost:3457/paipan',{method:'POST',headers:{'Content-Type':'application/json'},body:'...'}).then(r=>r.text()).then(t=>console.log(t))"
```

**400 常见原因速查：**
| 原因 | 提示 |
|------|------|
| `city` 传中文/未知代码 | 改用 `cn-xxx` 代码，或省略 |
| `hour` 越界（非 0-23） | 校正为 0-23 |
| body 不是合法 JSON | 用 `ConvertTo-Json` 序列化后再发 |
| body 含中文（非 ASCII） | ⚠️ PowerShell 5.1 的 `Invoke-RestMethod` 会把非 ASCII 字符编成 `?` 送达，服务端收到的是乱码（如 `北京` → `??`）。**请求体只放 ASCII**：`city` 用 `cn-xxx`、`gender` 用 `male`/`female`；确需发送中文请改用上方 Node 方式 |

---

### 排盘结果读取策略（重要）

> ⚠️ **禁止全量 read 排盘 JSON 进入上下文。** 排盘输出可达数千至数万行，全量读取浪费大量 token。

**正确读取方式：**

1. **常规排盘**（不加 `--liuyue`）：输出约 300-500 行，可用 `read` 读取前半部分（约前 500 行）获取四柱、日主、空亡、神煞、大运表头等核心数据
2. **大运/流年数据**：不要逐行读取 `liunian` 数组，改用 `grep` 精准提取：
   ```bash
   # 提取所有大运表头（干支+起止年龄）
   grep -E '"index": [0-9]+,|"startYear"|"endYear"|"startAge"|"endAge"|"gan":|"zhi":|"ganzhi":|"shishen":' 排盘结果.json | head -80
   ```
3. **特定年份流年**：用 grep 定位后再读取周边行：
   ```bash
   # 先找目标年份的行号
   grep -n '"year": 2026' 排盘结果.json
   # 再读取该行附近 30 行
   ```

---

### 流月按需提取

流月数据（梁湘润流月法则所需）仅在以下场景需要：
- 用户明确问"这个月/下个月运势"
- 第 9 步需要判断月运伏吟/双冲/双合时

**推荐用法：**

```bash
# 方式一：--liuyue-year（仅保留指定年份流月，输出最小）
node 排盘工具魔改/bazi-paipan/paipan.js \
  --year 2000 --month 3 --day 9 --hour 8 --gender female \
  --liuyue-year 2026 --pretty --out 排盘结果.json

# 方式二：--liuyue 全量输出后用 Node 提取目标年份
node -e "
  const d=require('./排盘结果.json');
  for (const p of d.dayun.pillars) {
    for (const ln of p.liunian) {
      if (ln.year===2026) console.log(JSON.stringify({year:ln.year,ganzhi:ln.ganzhi,liuYue:ln.liuYue},null,2));
    }
  }
"
```

---

### Windows 中文乱码规避（重要）

**现象：** Windows PowerShell 中直接运行 CLI，中文（如日主"辛"、纳音"路旁土"）可能显示为乱码。
**原因：** Node 输出 UTF-8，PowerShell 5.1 按系统编码（GBK）解码后再输出 → 显示层乱码；数据本身无损（用 read/grep 工具读文件内容正确）。

**规避方法（任选其一）：**

1. **推荐**：加 `--out 文件.json`，结果由脚本直写 UTF-8 文件，再 Read 读取：
   ```bash
   node 排盘工具魔改/bazi-paipan/paipan.js \
     --year 1990 --month 6 --day 15 --hour 14 --minute 30 \
     --gender male --city cn-shanghai --pretty --out 排盘结果.json
   ```
2. 用 cmd 重定向（保留原始 UTF-8 字节，不经过 PowerShell 编码转换）：
   ```bash
   cmd /c "node 排盘工具魔改\bazi-paipan\paipan.js --year 1990 --month 6 --day 15 --hour 14 --minute 30 --gender male --city cn-shanghai > 排盘结果.json 2>&1"
   ```
   ⚠️ 不要用 PowerShell 的 `>` 重定向——会把内容转成 UTF-16 编码。

---

## 方式二：HTTP API 服务

### 启动服务

```bash
node 排盘工具魔改/bazi-paipan/serve.js [port]
# 默认端口: 3457
```

### 调用排盘

```bash
curl -X POST http://localhost:3457/paipan \
  -H "Content-Type: application/json" \
  -d '{"calendar":"solar","year":1990,"month":6,"day":15,"hour":14,"minute":30,"gender":"male","city":"cn-shanghai"}'
```

### 健康检查

```bash
curl http://localhost:3457/health
# → {"status":"ok","service":"bazi-paipan"}
```

---

## JSON 输出关键字段说明

### 顶层结构

| 字段 | 类型 | 说明 |
|------|------|------|
| `input` | object | 输入参数（含自动补全的 `longitude` 经度、`timeZone` 时区） |
| `trueSolar` | object | 真太阳时校正结果（`longitudeOffset` 经度差、`eot` 均时差、`totalShift` 总位移） |
| `solarDate` | object | 公历日期 |
| `lunarDate` | object | 农历日期（`year`/`month`/`day`/`leap` + `label` 中文标签） |
| `lunarLabel` | string | 农历中文标签字符串（与 `lunarDate.label` 同值，便于直接取用） |
| `dayMaster` | string | 日主天干（如 "辛"） |
| `pillars` | object | 四柱（year/month/day/hour） |
| `xunkong` | string[] | 旬空地支行 |
| `monthCommand` | object | 月令司令（含节令、司令天干、阶段） |
| `transparentStems` | array | 透干列表 |
| `rooting` | array | 通根情况 |
| `sanyuan` | object | 三元（胎元/命宫/身宫） |
| `gongwei` | object | 宫位六亲（palaces/family/ganzhiKin） |
| `relations` | array | 刑冲合害关系列表 |
| `shensha` | array | 神煞列表 |
| `dayun` | object | 大运（起运/小运/大运柱/流年） |
| `liuri` | object | 流日（`--liuri` 时出现）：干支/十神/旬空 |
| `lishi` | array | 流时（`--lishi` 时出现）：12 时辰干支/时段/十神 |

### pillars 每柱结构

| 字段 | 说明 |
|------|------|
| `gan` | 天干 |
| `zhi` | 地支 |
| `ganzhi` | 干支组合（如 "庚午"） |
| `ganWuxing` | 天干五行 |
| `zhiWuxing` | 地支五行 |
| `ganYinYang` | 天干阴阳 |
| `nayin` | 纳音（name/wuxing） |
| `hiddenStems` | 藏干列表（gan/wuxing/shishen） |
| `shishen` | 十神（相对于日主） |
| `changsheng` | 十二长生状态 |
| `selfChangsheng` | 自坐长生 |
| `xunkong` | 是否旬空 |

### dayun 结构

| 字段 | 说明 |
|------|------|
| `forward` | 顺行/逆行 |
| `startAge` | 起运年龄（years/months/days） |
| `startSolar` | 起运公历日期 |
| `preStart` | 起运前年限 |
| `xiaoYun` | 小运（逐年） |
| `pillars` | 大运柱数组，每柱含 `liunian` 流年数组 |
| `pillars[].liunian[].liuYue` | 流月数组（`--liuyue` 时出现）：12 月/年，含 ganzhi、term（节令名）、startSolar（节令起止时刻）、shishen |

---

## 验证步骤

排盘完成后，验证以下关键字段：

1. ✅ `pillars.year.ganzhi` — 年柱干支（如 "庚午"）
2. ✅ `pillars.day.ganzhi` — 日柱干支（如 "辛亥"）
3. ✅ `dayMaster` — 日主天干（与日柱天干一致）
4. ✅ `dayun.pillars` 非空 — 大运数据存在
5. ✅ `lunarDate.label` — 农历日期标签可读

**验证通过 → 进入分析步骤（SKILL.md 步骤2）**

---

## 排盘引擎准确性验证记录

> 验证日期：2026-07-31
> 验证引擎：paipan v1.8.0（基于 lunar-typescript v1.8.6）

### 验证一：问真八字交叉对比

与问真八字的 OpenFate 生产校准测试集进行精确比对：

| 验证项 | 结果 |
|--------|:--:|
| 四柱（年/月/日/时） | ✅ 完全一致 |
| 日主 | ✅ 完全一致 |
| 空亡 | ✅ 完全一致 |
| 纳音 | ✅ 完全一致 |
| 藏干 + 十神 | ✅ 完全一致 |
| 起运年龄 | ✅ 误差在数天内 |
| 大运顺逆 | ✅ 正确 |
| 农历转换 | ✅ 完全一致 |
| 真太阳时 | ✅ 一致（精度差 <30秒） |

**唯一差异**：节气边界时刻的真太阳时策略。paipan 始终应用真太阳时校正，问真八字部分场景禁用。传统命理应以真太阳时为准。

### 验证二：独立数学验证

使用公认的八字推算公式（五虎遁、日干支公式、五鼠遁、旬空公式）进行独立计算：

| 测试日期 | 四柱 | 日主 | 空亡 | 结果 |
|----------|------|------|------|:--:|
| 1990-06-15 14:30 男 上海 | 庚午 壬午 辛亥 乙未 | 辛 | 寅卯 | ✅ |
| 2000-01-01 08:00 女 北京 | 己卯 丙子 戊午 丙辰 | 戊 | 子丑 | ✅ |
| 1985-09-25 22:00 男 成都 | 乙丑 乙酉 丁卯 辛亥 | 丁 | 戌亥 | ✅ |
| 1972-03-08 06:30 女 广州 | 壬子 癸卯 戊戌 乙卯 | 戊 | 辰巳 | ✅ |

**关键验证点：**
- 2000-01-01 在立春前 → 年柱应为己卯（非庚辰）→ 正确 ✅
- 1985年乙丑男命 → 大运应为逆排 → 正确 ✅
- 1972年壬子女命 → 大运应为逆排 → 正确 ✅
- 四城市真太阳时偏移均在合理范围，未跨越时辰边界 ✅

### 结论

**paipan v1.8.0 的八字排盘核心计算在所有测试用例上均正确，通过问真八字+独立数学双重验证，可作为权威排盘引擎使用。**
