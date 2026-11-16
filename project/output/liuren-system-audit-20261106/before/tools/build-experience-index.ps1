<#
.SYNOPSIS
  经验日志索引生成器（非破坏性）。

.DESCRIPTION
  扫描 经验日志\*.md，读其 META 行 + 正文结构化字段，归一化后生成
  经验日志\_metadata_index.md，供 daliuren 步骤10「冲突裁决第1级」做锚定 grep。

  解决的问题：
    1. 经验日志此前无索引 → 只能全文 grep，慢且漏。
    2. 反馈值有 7 种变体（验 / ✅ / ❌ / **部分验** / 部分应验 / 不验 / 未验证）
       → 裸 grep "反馈=验" 会漏检 ✅ 这类已验证记录。本脚本归一为
         验 / 部分应验 / 未验 / 未载 四值，并保留「反馈原文」字段。
    3. 多数经验复盘文件的 META 缺 课体/发用/三传/日干 → 本脚本从正文回填。

  纪律：只读源文件，只写 _metadata_index.md；不修改任何源文件。

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\build-experience-index.ps1
#>
[CmdletBinding()]
param(
  [string]$DataRoot = "经验日志",
  [string]$OutFile  = "",
  [switch]$Quiet
)

$ErrorActionPreference = 'Stop'

# 定位项目根（脚本在 tools\ 下）
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projRoot  = Split-Path -Parent $scriptDir
if (-not (Test-Path -LiteralPath (Join-Path $projRoot $DataRoot))) {
  # 允许从项目根直接调用
  if (Test-Path -LiteralPath (Join-Path (Get-Location) $DataRoot)) { $projRoot = (Get-Location).Path }
  else { throw "找不到数据目录：$DataRoot（已尝试 $projRoot 与当前目录）" }
}
$dataPath = Join-Path $projRoot $DataRoot
if ([string]::IsNullOrWhiteSpace($OutFile)) { $OutFile = Join-Path $dataPath "_metadata_index.md" }

# ---------- 工具函数 ----------

$TIANJIANG = @('贵人','腾蛇','朱雀','六合','勾陈','青龙','天空','白虎','太常','玄武','太阴','天后')
$DIZHI     = @('子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥')
$WUXING    = @{ '甲'='木';'乙'='木';'丙'='火';'丁'='火';'戊'='土';'己'='土';'庚'='金';'辛'='金';'壬'='水';'癸'='水' }

# 课体词表：种子 + 从 案例项目库 的 case META 学习。
# 目的：防止正文回填时误匹配（如把说明文字"核心条件"当成课体）。
$script:KETI_VOCAB = New-Object System.Collections.Generic.HashSet[string]
@('元首','重审','知一','比用','涉害','遥克','蒿矢','弹射','昴星','掩目','虎视','别责','八专','伏吟','返吟','自任','自信',
  '贼克','退茹','进茹','连茹','间传','逆间传','三交','二烦','九丑','励德','不备','寡宿','孤辰','斩关','闭口','三奇','六仪',
  '润下','曲直','炎上','从革','稼穑','元胎','玄胎','时泰','龙战','无依','度厄','幼度厄','乱首','赘婿','见机','帷簿',
  '高盖','六阳','六阴','出户','进退','始入','铸印','乘轩','顾祖','回环','周遍','芜淫','蕪淫','魁星','游子','蓦越',
  '三阳','解离','迫逼','收魂') |
  ForEach-Object { [void]$script:KETI_VOCAB.Add($_) }
$script:KeTiOutOfVocab = New-Object System.Collections.Generic.HashSet[string]
$caseDir = Join-Path $projRoot '案例项目库'
if (Test-Path -LiteralPath $caseDir) {
  Get-ChildItem -LiteralPath $caseDir -Recurse -Filter 'case-*.md' -File | ForEach-Object {
    $m = [regex]::Match((Get-Content -LiteralPath $_.FullName -TotalCount 1 -Encoding UTF8), '课体\s*=\s*(?<v>[^|]*)')
    if ($m.Success) {
      $m.Groups['v'].Value -split '[，,、·\s]+' | Where-Object { $_ } | ForEach-Object { [void]$script:KETI_VOCAB.Add($_.Trim()) }
    }
  }
}

function Get-FirstMatchValue {
  param([string]$Text, [string]$Key)
  # 第一优先：行首（容忍 markdown 装饰 - ** | 空格）
  $pat1 = "(?m)^\s*[-*\s|]*\**\s*$Key\s*\**\s*[:：|]\s*\**\s*(?<v>.+?)\s*\**\s*(\||$)"
  $m = [regex]::Match($Text, $pat1)
  if ($m.Success) { return $m.Groups['v'].Value.Trim() }
  # 第二优先：行内任意位置（如 "**公历：** 2001-09-04 四柱：辛巳 丙申 …"）
  $pat2 = "\**\s*$Key\s*\**\s*[:：|]\s*\**\s*(?<v>[^\r\n|]+)"
  $m2 = [regex]::Match($Text, $pat2)
  if ($m2.Success) { return (($m2.Groups['v'].Value -replace '\*+', '') -replace '[\[\]【】]', '').Trim() }
  return ''
}

function Normalize-KeTi {
  param([string]$Raw)
  if ([string]::IsNullOrWhiteSpace($Raw)) { return '' }
  $s = $Raw -replace '[\[\]【】]', '' -replace '\*+', '' -replace '[（(].*?[)）]', ''
  $parts = @($s -split '[，,、·・→\-—/\s]+' | Where-Object { $_ } | ForEach-Object {
    $t = $_.Trim() -replace '^课体\s*=', ''
    if ($t -match '^(.+?)课$' -and $script:KETI_VOCAB.Contains($matches[1])) { $t = $matches[1] }   # 不备课 → 不备
    $t
  })
  if ($parts.Count -eq 0) { return '' }
  $kept    = @($parts | Where-Object { $script:KETI_VOCAB.Contains($_) })
  $outside = @($parts | Where-Object { -not $script:KETI_VOCAB.Contains($_) })
  foreach ($o in $outside) { [void]$script:KeTiOutOfVocab.Add($o) }
  return ($kept -join ',')
}

function Normalize-FaYong {
  param([string]$Raw)
  if ([string]::IsNullOrWhiteSpace($Raw)) { return '' }
  $s = $Raw -replace '\*+', ''
  $dz = ''
  foreach ($c in $s.ToCharArray()) { if ($DIZHI -contains [string]$c) { $dz = [string]$c; break } }
  $tj = ''
  foreach ($t in $TIANJIANG) { if ($s.Contains($t)) { $tj = $t; break } }
  if ($dz -and $tj) { return "$dz($tj)" }
  if ($dz) { return $dz }
  return ''
}

function Normalize-SanChuan {
  param([string]$Raw)
  if ([string]::IsNullOrWhiteSpace($Raw)) { return '' }
  $s = $Raw -replace '\*+', ''
  $found = New-Object System.Collections.ArrayList
  foreach ($c in $s.ToCharArray()) {
    if (($DIZHI -contains [string]$c) -and ($found -notcontains [string]$c)) { [void]$found.Add([string]$c) }
  }
  if ($found.Count -ge 3) { return ($found[0..2] -join '') }
  return ($found -join '')
}

function Normalize-Feedback {
  param([string]$Raw, [string]$TypeHint)
  $s = ($Raw -replace '\*+', '').Trim()
  if ([string]::IsNullOrWhiteSpace($s)) { return '未载' }
  # 顺序纪律：必须先判「部分」，再判「未验证」（否则"未验证"会被"未验"命中），最后才判「验」
  if ($s -match '部分') { return '部分应验' }
  if ($s -match '未验证' -or $s -match '未载') { return '未载' }
  if ($s -match '❌' -or $s -match '不验' -or $s -match '未验') { return '未验' }
  if ($s -match '✅' -or $s -match '验') { return '验' }
  # META 未写反馈：归 未载（不臆造）
  return '未载'
}

function Get-MetaLine {
  param([string]$Text)
  $m = [regex]::Match($Text, '(?m)^\s*<!--\s*META:(?<v>.*?)-->')
  if ($m.Success) { return $m.Groups['v'].Value.Trim() }
  return ''
}

function Get-Field {
  param([string]$Meta, [string]$Key)
  if ([string]::IsNullOrWhiteSpace($Meta)) { return '' }
  $m = [regex]::Match($Meta, "$Key\s*=\s*(?<v>[^|]*)")
  if ($m.Success) { return $m.Groups['v'].Value.Trim() }
  return ''
}

# ---------- 主流程 ----------

$files = Get-ChildItem -LiteralPath $dataPath -Filter *.md -File |
         Where-Object { $_.Name -notlike '_*' -and $_.Name -ne 'README.md' } |
         Sort-Object Name

$rows = New-Object System.Collections.ArrayList
$skipped = New-Object System.Collections.ArrayList

foreach ($f in $files) {
  $text = Get-Content -LiteralPath $f.FullName -Raw -Encoding UTF8
  $meta = Get-MetaLine $text

  if ([string]::IsNullOrWhiteSpace($meta)) {
    [void]$skipped.Add($f.Name + "  (无 META 行)")
    $meta = ''   # 仍尝试从正文回填
  }

  # --- 类型判定 ---
  $typeMeta = Get-Field $meta '类型'
  $topicMeta = Get-Field $meta '专题'
  $isDate   = $f.Name -match '^\d{4}-\d{2}-\d{2}'
  $isGuji   = $f.Name -match '^古籍-'
  $isTiqu   = $f.Name -match '^提取-'
  $isSuiming= $f.Name -match '^推命参考-'
  $isExtract= $f.Name -match '经验提取'
  $isReport = $f.Name -match '审查报告'

  if ($isGuji)      { $cat = '古籍蒸馏' }
  elseif ($isTiqu)  { $cat = '书籍提取' }
  elseif ($isSuiming){ $cat = '推命参考' }
  elseif ($isDate)  { $cat = '经验复盘' }
  elseif ($isExtract){ $cat = '案例库经验提取' }
  elseif ($isReport){ $cat = '审查报告' }
  else              { $cat = '其他' }

  # --- 字段：META 优先，正文回填 ---
  $zhanLei = Get-Field $meta '占类'
  if ([string]::IsNullOrWhiteSpace($zhanLei)) {
    if ($f.Name -match '-(疾病占|灾厄占|交易占|财运占|考试占|学业占|事业占|感情占|胎产占|失物占|出行占|行人占|家宅占|宅门占|官讼占|天时占|杂事占|来意占|射覆|推命占)-') {
      $zhanLei = $matches[1]
    }
  }

  $keTiRaw = Get-Field $meta '课体'
  if ([string]::IsNullOrWhiteSpace($keTiRaw)) { $keTiRaw = Get-FirstMatchValue $text '课体' }
  $keTi = Normalize-KeTi $keTiRaw

  $sanChuanRaw = Get-Field $meta '三传'
  if ([string]::IsNullOrWhiteSpace($sanChuanRaw)) { $sanChuanRaw = Get-FirstMatchValue $text '三传' }
  $sanChuan = Normalize-SanChuan $sanChuanRaw

  $faYongRaw = Get-Field $meta '发用'
  if ([string]::IsNullOrWhiteSpace($faYongRaw)) { $faYongRaw = Get-FirstMatchValue $text '发用' }
  $faYong = Normalize-FaYong $faYongRaw
  # 回填：正文无「发用：」标注时，取三传初传段（含其天将）
  if (-not $faYong -and $sanChuanRaw) {
    $seg = ($sanChuanRaw -split '[→\-—>]+')[0]
    $faYong = Normalize-FaYong $seg
  }

  $riGanRaw = Get-Field $meta '日干'
  if ([string]::IsNullOrWhiteSpace($riGanRaw)) {
    # 四柱顺序 = 年 月 日 时 → 日干取第 3 柱天干（历史 bug：曾误取年柱）
    $sizhu = Get-FirstMatchValue $text '四柱'
    if ($sizhu) {
      $p = @((($sizhu -replace '[，,]', ' ') -split '\s+') | Where-Object { $_ -match '^[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]' })
      if ($p.Count -ge 3) { $riGanRaw = $p[2].Substring(0,1) }
    }
  }
  $riGan = ($riGanRaw -replace '[^甲乙丙丁戊己庚辛壬癸]', '')
  if ($riGan.Length -gt 1) { $riGan = $riGan.Substring(0,1) }
  $riGanWx = ''
  if ($riGan -and $WUXING.ContainsKey($riGan)) { $riGanWx = $WUXING[$riGan] }

  $fbRaw = Get-Field $meta '反馈'
  if ([string]::IsNullOrWhiteSpace($fbRaw) -and $text -match '(?m)^##\s*反馈\s*\r?\n+>\s*(?<v>.+)$') { $fbRaw = $matches['v'] }
  $fbNorm = Normalize-Feedback $fbRaw $cat

  # --- 组装 ---
  $o = [ordered]@{
    文件   = $f.Name
    类别   = $cat
    占类   = $zhanLei
    课体   = $keTi
    发用   = $faYong
    三传   = $sanChuan
    日干   = $riGan
    日干五行 = $riGanWx
    反馈   = $fbNorm
    反馈原文 = $fbRaw
    主题   = $topicMeta
    来源   = (Get-Field $meta '来源')
    技法   = (Get-Field $meta '技法')
  }
  [void]$rows.Add([pscustomobject]$o)
}

# ---------- 输出 ----------

$ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$sb = New-Object System.Text.StringBuilder
[void]$sb.AppendLine('# 经验日志索引（自动生成 · 请勿手工编辑）')
[void]$sb.AppendLine('')
[void]$sb.AppendLine("> 生成时间：$ts")
[void]$sb.AppendLine('> 生成器：`tools\build-experience-index.ps1`')
[void]$sb.AppendLine('> 来源：`经验日志\*.md`（只读，不修改源文件）')
[void]$sb.AppendLine('> 用途：`daliuren` 步骤10「冲突裁决第1级」——检索 `反馈=验` 的同课体 / 同发用组合')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## 一、检索用法（锚定 META，勿裸搜正文）')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('```powershell')
[void]$sb.AppendLine('# 1) 已验证记录（必查，冲突裁决第1级）')
[void]$sb.AppendLine('Select-String -Path "经验日志\_metadata_index.md" -Pattern "^<!-- META:.*反馈=验"')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('# 2) 同课体（例：退茹）')
[void]$sb.AppendLine('Select-String -Path "经验日志\_metadata_index.md" -Pattern "^<!-- META:.*课体=[^|]*退茹"')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('# 3) 同发用组合（例：卯朱雀）')
[void]$sb.AppendLine('Select-String -Path "经验日志\_metadata_index.md" -Pattern "^<!-- META:.*发用=卯\(朱雀\)"')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('# 4) 组合（占类 + 课体 + 验）')
[void]$sb.AppendLine('Select-String -Path "经验日志\_metadata_index.md" -Pattern "^<!-- META:.*占类=交易占.*课体=[^|]*退茹.*反馈=验"')
[void]$sb.AppendLine('```')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('> ⚠️ 纪律：`README.md` / `_template.md` / `_*.md` 已从索引排除；')
[void]$sb.AppendLine('> 源文件正文可能含 META 格式示例，**不要**对源目录做裸 grep（会命中说明文字）。')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## 二、字段规范')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('| 字段 | 说明 |')
[void]$sb.AppendLine('|---|---|')
[void]$sb.AppendLine('| `类别` | 经验复盘 / 古籍蒸馏 / 书籍提取 / 推命参考 / 案例库经验提取 / 审查报告 / 其他 |')
[void]$sb.AppendLine('| `占类` | 六壬占类；无则留空 |')
[void]$sb.AppendLine('| `课体` | 已归一为逗号分隔；META 缺则从正文回填 |')
[void]$sb.AppendLine('| `发用` | `地支(天将)`；META 缺则从正文回填 |')
[void]$sb.AppendLine('| `三传` | 三地支连写；META 缺则从正文回填 |')
[void]$sb.AppendLine('| `日干` / `日干五行` | 天干 + 五行；META 缺则从正文四柱回填 |')
[void]$sb.AppendLine('| `反馈` | **归一值**：`验` / `部分应验` / `未验` / `未载`（可直接 grep） |')
[void]$sb.AppendLine('| `反馈原文` | 原始写法（如 `✅`、`**部分验**（…）`），供追溯 |')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('> 反馈归一对照：`✅`／`验` → `验`；含「部分」→ `部分应验`；`❌`／`不验` → `未验`；`未验证`／缺 → `未载`')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## 三、索引条目（锚定 META，每条一行）')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('<!-- INDEX-BEGIN -->')
foreach ($r in $rows) {
  $metaOut = "<!-- META: 文件=$($r.文件) | 类别=$($r.类别)"
  if ($r.占类)     { $metaOut += " | 占类=$($r.占类)" }
  if ($r.课体)     { $metaOut += " | 课体=$($r.课体)" }
  if ($r.发用)     { $metaOut += " | 发用=$($r.发用)" }
  if ($r.三传)     { $metaOut += " | 三传=$($r.三传)" }
  if ($r.日干)     { $metaOut += " | 日干=$($r.日干)" }
  if ($r.日干五行) { $metaOut += " | 日干五行=$($r.日干五行)" }
  $metaOut += " | 反馈=$($r.反馈)"
  if ($r.反馈原文 -and $r.反馈原文 -ne $r.反馈) { $metaOut += " | 反馈原文=$($r.反馈原文)" }
  $metaOut += " -->"
  [void]$sb.AppendLine($metaOut)
}
[void]$sb.AppendLine('<!-- INDEX-END -->')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## 四、明细表')
[void]$sb.AppendLine('')
[void]$sb.AppendLine('| # | 文件 | 类别 | 占类 | 课体 | 发用 | 三传 | 日干 | 反馈(归一) | 反馈(原文) |')
[void]$sb.AppendLine('|---|---|---|---|---|---|---|---|---|---|')
$i = 0
foreach ($r in $rows) {
  $i++
  [void]$sb.AppendLine("| $i | $($r.文件) | $($r.类别) | $($r.占类) | $($r.课体) | $($r.发用) | $($r.三传) | $($r.日干)$($r.日干五行) | $($r.反馈) | $($r.反馈原文) |")
}
[void]$sb.AppendLine('')
[void]$sb.AppendLine('## 五、统计')
[void]$sb.AppendLine('')
[void]$sb.AppendLine("- 条目总数：**$($rows.Count)**")
$rows | Group-Object 反馈 | Sort-Object Name | ForEach-Object { [void]$sb.AppendLine("- 反馈=$($_.Name)：$($_.Count) 条") }
[void]$sb.AppendLine('')
$rows | Group-Object 类别 | Sort-Object Name | ForEach-Object { [void]$sb.AppendLine("- 类别=$($_.Name)：$($_.Count) 条") }
if ($skipped.Count -gt 0) {
  [void]$sb.AppendLine('')
  [void]$sb.AppendLine('## 六、无 META 行（已排除或需补 META）')
  [void]$sb.AppendLine('')
  foreach ($s in $skipped) { [void]$sb.AppendLine("- $s") }
}

[void]$sb.AppendLine('')
[void]$sb.AppendLine('## 七、课体词表外命中（已过滤，留痕待裁决）')
[void]$sb.AppendLine('')
[void]$sb.AppendLine("> 词表规模：$($script:KETI_VOCAB.Count) 个课体名（种子 + 从 案例项目库 case META 学习）。")
[void]$sb.AppendLine('> 下列词在正文回填时被识别为疑似课体，但不在词表内，**已从索引剔除**，在此留痕以免静默丢失。')
[void]$sb.AppendLine('')
if ($script:KeTiOutOfVocab.Count -eq 0) {
  [void]$sb.AppendLine('（无）')
} else {
  foreach ($k in ($script:KeTiOutOfVocab | Sort-Object)) { [void]$sb.AppendLine("- $k") }
}

[System.IO.File]::WriteAllText($OutFile, $sb.ToString(), (New-Object System.Text.UTF8Encoding($false)))

if (-not $Quiet) {
  Write-Output "OK  -> $OutFile"
  Write-Output "条目数: $($rows.Count)"
  $rows | Group-Object 反馈 | Sort-Object Name | ForEach-Object { Write-Output ("  反馈={0}: {1}" -f $_.Name, $_.Count) }
  if ($skipped.Count -gt 0) { Write-Output ("无META: {0} 个（见索引第六节）" -f $skipped.Count) }
}
