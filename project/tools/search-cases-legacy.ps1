<#
.SYNOPSIS
  六壬双入口：案例六维评分 + 条目级经验检索。

.DESCRIPTION
  替代"LLM 随手 grep"，把 daliuren 步骤10 的检索机制固化为可复现脚本。

  检索机制（三层，纪律硬编码）：
    第0层  数据根自检 —— 找不到 案例项目库 / 经验日志 或索引缺失 → 直接报错并给出
                        初始化/迁移指引（**不再静默换路径**）。
    第1层  索引优先   —— 锚定 "<!-- META:" 只搜 _metadata_index.md（快、无噪音）。
    第2层  文件回退   —— 第1层 0 命中时，才锚定搜 case-*.md（排除 _*/README/_template）。
    * 所有匹配一律锚定 ^<!-- META:，从机制上杜绝把"讲 grep 的文档"当成案例命中。

  输出：案例六维评分与历史反馈提示；经验另列条目、验证身份和边界，不自动采信。

.PARAMETER ZhanLei
  新占所用占类。支持标准命名↔旧目录名互认（财运占=交易占、学业占=考试占…）。

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\search-cases.ps1 `
    -ZhanLei 财运占 -KeTi 元首,退茹 -FaYong "卯" -SanChuan 卯寅丑 -RiGan 癸
#>
[CmdletBinding()]
param(
  [string]$ZhanLei  = '',
  [string]$KeTi     = '',
  [string]$FaYong   = '',
  [string]$SanChuan = '',
  [string]$RiGan    = '',
  [string]$LeiShen  = '',
  [ValidateSet('','验','部分应验','未验','未载')] [string]$Feedback = '',
  [ValidateSet('case','exp','all')] [string]$Scope = 'all',
  [switch]$Strict,
  [int]$Top = 0,
  [string]$OutFile = ''
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

# 经验使用条目级索引，不再将整个经验文件套入案例六维评分。
function Invoke-ExperienceRetrieval {
  $entry = Join-Path $PSScriptRoot 'search-experience.py'
  $terms = (@($KeTi, $FaYong, $LeiShen) | Where-Object { $_ }) -join ' '
  $argsExp = @('-X', 'utf8', $entry)
  if ($terms) { $argsExp += @('--query', $terms) }
  if ($ZhanLei) { foreach ($z in ($ZhanLei -split '[，,\s]+' | Where-Object { $_ })) { $argsExp += @('--category', $z) } }
  if ($Top -gt 0) { $argsExp += @('--limit', [string]$Top) }
  if ($Strict) { $argsExp += '--all-terms' }
  # -Feedback 是旧案例状态筛选，不能当作新经验的验证筛选。
  if ($Feedback) { Write-Warning '经验不按历史反馈字段过滤；逐条返回验证身份，避免遗漏书籍、反例和优秀作业。' }
  $resultExp = & python @argsExp
  if ($LASTEXITCODE -ne 0) { throw '细粒度经验检索失败；未静默降级为旧文件索引。' }
  return ($resultExp -join [Environment]::NewLine)
}
if ($Scope -eq 'exp') {
  $resultExp = Invoke-ExperienceRetrieval
  if ($OutFile) {
    $targetExp = $OutFile
    if (-not [System.IO.Path]::IsPathRooted($targetExp)) { $targetExp = Join-Path (Get-Location).Path $targetExp }
    [System.IO.File]::WriteAllText($targetExp, $resultExp, (New-Object System.Text.UTF8Encoding($false)))
  }
  else { Write-Output $resultExp }
  exit 0
}

# ---------- 0. 数据根自检（不许静默换路径） ----------
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projRoot  = Split-Path -Parent $scriptDir
if (-not (Test-Path -LiteralPath (Join-Path $projRoot '案例项目库'))) { $projRoot = (Get-Location).Path }

$CASE_DIR = Join-Path $projRoot '案例项目库'
$EXP_DIR  = Join-Path $projRoot '经验日志'
$CASE_IDX = Join-Path $CASE_DIR '_metadata_index.md'
$EXP_IDX  = Join-Path $EXP_DIR  '_metadata_index.md'

$fatal = $false
if (-not (Test-Path -LiteralPath $CASE_DIR)) { Write-Error "数据根缺失：$CASE_DIR"; $fatal = $true }
if (-not (Test-Path -LiteralPath $EXP_DIR))  { Write-Error "数据根缺失：$EXP_DIR";  $fatal = $true }
if (-not (Test-Path -LiteralPath $CASE_IDX)) { Write-Error "案例索引缺失：$CASE_IDX"; $fatal = $true }
if ($fatal) {
  Write-Output ''
  Write-Output '【修复指引】本库数据根为：案例项目库\ + 经验日志\（见 opencode.json references）。'
  Write-Output '若曾使用旧口径“案例库\”，请勿静默改名——先与本项目负责人确认后迁移，或修正调用方的路径口径。'
  exit 2
}

# ---------- 1. 常量 ----------
$WUXING = @{ '甲'='木';'乙'='木';'丙'='火';'丁'='火';'戊'='土';'己'='土';'庚'='金';'辛'='金';'壬'='水';'癸'='水' }
$ZLMAP  = @{
  '学业占'=@('学业占','考试占'); '财运占'=@('财运占','交易占'); '感情占'=@('感情占','胎产占');
  '健康占'=@('健康占','疾病占','灾厄占'); '出行占'=@('出行占','行人占'); '事业占'=@('事业占','比赛占');
  '家宅占'=@('家宅占','宅门占'); '官讼占'=@('官讼占'); '失物占'=@('失物占'); '天时占'=@('天时占')
}
function Expand-ZhanLei {
  param([string]$z)
  if ([string]::IsNullOrWhiteSpace($z)) { return @() }
  $acc = New-Object System.Collections.ArrayList
  foreach ($one in ($z -split '[，,\s]+' | Where-Object { $_ })) {
    $hit = $false
    foreach ($k in $ZLMAP.Keys) {
      if ($ZLMAP[$k] -contains $one -or $k -eq $one) { foreach ($v in $ZLMAP[$k]) { if ($acc -notcontains $v) { [void]$acc.Add($v) } }; $hit = $true }
    }
    if (-not $hit) { if ($acc -notcontains $one) { [void]$acc.Add($one) } }
  }
  return @($acc)
}

function Get-Field { param([string]$Line,[string]$Key)
  $m = [regex]::Match($Line, "$Key\s*=\s*(?<v>[^|]*)")
  if ($m.Success) { return (($m.Groups['v'].Value -replace '-->\s*$', '').Trim()) }
  return ''
}
function Split-KeTi { param([string]$s)
  if ([string]::IsNullOrWhiteSpace($s)) { return @() }
  return @(($s -split '[，,、·\s]+') | Where-Object { $_ } | ForEach-Object { $_.Trim() })
}
function ZhuGanWx { param([string]$gan)
  $g = ($gan -replace '[^甲乙丙丁戊己庚辛壬癸]', '')
  if ($g.Length -ge 1 -and $WUXING.ContainsKey($g.Substring(0,1))) { return $WUXING[$g.Substring(0,1)] }
  return ''
}
# 条目名：经验日志用 文件=；案例项目库用 占类/编号
function Get-EntryName { param([string]$l)
  $f = Get-Field $l '文件'
  if ($f) { return $f }
  $no = Get-Field $l '编号'
  $zl = Get-Field $l '占类'
  if ($no) { if ($zl) { return "$zl/$no" } else { return $no } }
  return '(未命名)'
}

# ---------- 2. 组装检索条件 ----------
$zlSet   = Expand-ZhanLei $ZhanLei
$ktSet   = Split-KeTi $KeTi
$fxDizhi = if ($FaYong) { ($FaYong -replace '[^子丑寅卯辰巳午未申酉戌亥]', '') } else { '' }
$fxJiang = ''
if ($FaYong) { foreach ($t in @('贵人','腾蛇','朱雀','六合','勾陈','青龙','天空','白虎','太常','玄武','太阴','天后')) { if ($FaYong.Contains($t)) { $fxJiang = $t; break } } }
$scSet   = if ($SanChuan) { @(($SanChuan -replace '[^子丑寅卯辰巳午未申酉戌亥]', '').ToCharArray() | ForEach-Object { [string]$_ }) } else { @() }
$rgWx    = ZhuGanWx $RiGan

# ---------- 3. 三层检索 ----------
function Get-Hits {
  param([string]$Path, [string]$Kind)
  if (-not (Test-Path -LiteralPath $Path)) { return @() }
  # 纪律：一律锚定行首 META
  $lines = Select-String -LiteralPath $Path -Pattern '^<!-- META:' -Encoding UTF8 | ForEach-Object { $_.Line }
  $out = New-Object System.Collections.ArrayList
  foreach ($l in $lines) {
    if ($Scope -ne 'all') {
      $isCase = ($Kind -eq 'case')
      if ($Scope -eq 'case' -and -not $isCase) { continue }
      if ($Scope -eq 'exp'  -and $isCase)      { continue }
    }
    [void]$out.Add([pscustomobject]@{ Line = $l; Kind = $Kind })
  }
  return @($out)
}

$pool = New-Object System.Collections.ArrayList
$layer = ''
if ($Scope -in @('case','all') -and (Test-Path -LiteralPath $CASE_IDX)) {
  foreach ($h in (Get-Hits $CASE_IDX 'case')) { [void]$pool.Add($h) }
  $layer = '🥇 索引层（案例项目库\_metadata_index.md）'
}

# ---------- 4. 过滤（默认：任一维度命中即入池 → 评分排序；-Strict：全条件 AND） ----------
function Test-Cand {
  param($c)
  $l = $c.Line

  # 硬过滤：反馈（唯一强制项）
  if ($Feedback) { if ((Get-Field $l '反馈') -ne $Feedback) { return $false } }

  $hasAnyCrit = ($zlSet.Count -gt 0 -or $ktSet.Count -gt 0 -or $fxDizhi -or $scSet.Count -ge 3)
  if (-not $hasAnyCrit) { return $true }   # 只给日干/类神 → 全池参与评分

  $mZL = ($zlSet.Count -gt 0) -and ($zlSet -contains (Get-Field $l '占类'))
  $ck  = Split-KeTi (Get-Field $l '课体')
  $mKT = ($ktSet.Count -gt 0) -and (@($ktSet | Where-Object { $ck -contains $_ }).Count -gt 0)
  $mFY = $false
  if ($fxDizhi) { $cf = Get-Field $l '发用'; if ($cf -match $fxDizhi) { $mFY = $true } }
  $mSC = ($scSet.Count -ge 3) -and ((Get-Field $l '三传') -eq ($scSet -join ''))

  if ($Strict) {
    if ($zlSet.Count -gt 0 -and -not $mZL) { return $false }
    if ($ktSet.Count -gt 0 -and -not $mKT) { return $false }
    if ($fxDizhi -and -not $mFY)        { return $false }
    if ($scSet.Count -ge 3 -and -not $mSC) { return $false }
    return $true
  }
  # 默认：任一维度命中即入池（保证有排序候选可看，避免"全条件 AND → 0 命中"）
  return ($mZL -or $mKT -or $mFY -or $mSC)
}

$cands = @($pool | Where-Object { Test-Cand $_ })
$usedLayer = $layer

# 第2层：索引 0 命中 → 回退锚定搜 case 文件（排除 _* / README / _template）
if ($cands.Count -eq 0 -and $Scope -in @('case','all') -and (Test-Path -LiteralPath $CASE_DIR)) {
  $pool2 = New-Object System.Collections.ArrayList
  Get-ChildItem -LiteralPath $CASE_DIR -Recurse -Filter 'case-*.md' -File |
    Where-Object { $_.Name -notlike '_*' -and $_.Name -ne 'README.md' } | ForEach-Object {
      $l = (Get-Content -LiteralPath $_.FullName -TotalCount 1 -Encoding UTF8)
      if ($l -match '^<!-- META:') { [void]$pool2.Add([pscustomobject]@{ Line = $l; Kind = 'case' }) }
    }
  $cands = @($pool2 | Where-Object { Test-Cand $_ })
  $usedLayer = '🥈 回退层（锚定搜 case-*.md，索引 0 命中）'
}

# ---------- 5. 六维加权评分 ----------
function Get-Score {
  param($c)
  $l = $c.Line
  $s = [ordered]@{ 占类=0; 课体=0; 发用=0; 类神=0; 三传=0; 日干=0 }
  # 占类 25
  if ($zlSet.Count -gt 0 -and $zlSet -contains (Get-Field $l '占类')) { $s.占类 = 25 }
  # 课体 20 × Jaccard
  if ($ktSet.Count -gt 0) {
    $ck = Split-KeTi (Get-Field $l '课体')
    $inter = @($ktSet | Where-Object { $ck -contains $_ }).Count
    $union = @($ktSet + $ck | Select-Object -Unique).Count
    if ($union -gt 0) { $s.课体 = [math]::Round(20 * $inter / $union, 1) }
  }
  # 发用 15 / 8
  $cf = Get-Field $l '发用'
  if ($cf) {
    $cj = ''
    foreach ($t in @('贵人','腾蛇','朱雀','六合','勾陈','青龙','天空','白虎','太常','玄武','太阴','天后')) { if ($cf.Contains($t)) { $cj = $t; break } }
    if ($fxDizhi -and $cf -match $fxDizhi) {
      if ($fxJiang -and $cj -eq $fxJiang) { $s.发用 = 15 } else { $s.发用 = 8 }
    }
  }
  # 类神 15（仅对结构化字段 类神=/技法= 精确匹配，避免子串噪音；缺字段则 0，须人工补判）
  if ($LeiShen) {
    $hint = Get-Field $l '类神'
    if (-not $hint) { $hint = Get-Field $l '技法' }
    if ($hint -and $hint.Contains($LeiShen)) { $s.类神 = 15 }
  }
  # 三传 15 / 8（同序列=15；同为连茹/间传结构=8）
  $cs = Get-Field $l '三传'
  if ($scSet.Count -ge 3 -and $cs) {
    if ($cs -eq ($scSet -join '')) { $s.三传 = 15 }
    else {
      $ord = @('子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥')
      $isLianRu = { param($seq) if ($null -eq $seq) { return $false }; $t = @($seq.ToCharArray() | Where-Object { $ord -contains [string]$_ }); if ($t.Count -ne 3) { return $false }; $i1 = $ord.IndexOf($t[0]); $i2 = $ord.IndexOf($t[1]); $i3 = $ord.IndexOf($t[2]); return (($i2 -eq ($i1+1)%12 -and $i3 -eq ($i2+1)%12) -or ($i2 -eq ($i1+11)%12 -and $i3 -eq ($i2+11)%12)) }
      if ((& $isLianRu $cs) -and (& $isLianRu ($scSet -join ''))) { $s.三传 = 8 }
    }
  }
  # 日干五行 10
  $cw = Get-Field $l '日干五行'; if (-not $cw) { $cw = ZhuGanWx (Get-Field $l '日干') }
  if ($rgWx -and $cw -eq $rgWx) { $s.日干 = 10 }

  $raw = ($s.Values | Measure-Object -Sum).Sum
  $fb  = Get-Field $l '反馈'
  $coef = switch ($fb) { '验' { 1.1 } '部分应验' { 1.0 } '未验' { 0.8 } '未载' { 0.8 } default { 1.0 } }
  return [pscustomobject]@{ Dim = $s; Raw = $raw; Coef = $coef; Final = [math]::Round($raw * $coef, 1); Fb = $fb }
}

# ---------- 6. 输出（先缓冲，再统一写出，避免管道二次编码） ----------
$rows = foreach ($c in $cands) {
  $sc = Get-Score $c
  $l = $c.Line
  [pscustomobject]@{
    Kind = $c.Kind
    条目 = (Get-EntryName $l)
    占类 = (Get-Field $l '占类'); 课体 = (Get-Field $l '课体')
    发用 = (Get-Field $l '发用'); 三传 = (Get-Field $l '三传'); 日干 = (Get-Field $l '日干')
    反馈 = $sc.Fb; 原始 = $sc.Raw; 系数 = $sc.Coef; 最终 = $sc.Final
    分_占类=$sc.Dim.占类; 分_课体=$sc.Dim.课体; 分_发用=$sc.Dim.发用; 分_类神=$sc.Dim.类神; 分_三传=$sc.Dim.三传; 分_日干=$sc.Dim.日干
  }
}
$rows = @($rows | Sort-Object 最终 -Descending)
if ($Top -gt 0) { $rows = @($rows | Select-Object -First $Top) }

$script:OUT = New-Object System.Collections.ArrayList
function Add-Line { param([string]$x) [void]$script:OUT.Add($x) }

Add-Line '# 六壬案例/经验检索结果'
Add-Line ''
Add-Line ("- 数据根：``{0}``" -f $projRoot)
Add-Line ("- 检索层：{0}" -f $usedLayer)
Add-Line ("- 条件：占类=[{0}] 课体=[{1}] 发用=[{2}] 三传=[{3}] 日干={4}({5}) 反馈=[{6}] 类神=[{7}]" -f `
  ($zlSet -join ','), ($ktSet -join ','), $FaYong, ($scSet -join ''), $RiGan, $rgWx, $Feedback, $LeiShen)
Add-Line ("- 命中：**{0}** 条" -f $rows.Count)
Add-Line ''
if ($rows.Count -eq 0) {
  Add-Line '> 无候选。按纪律输出固定话术：“本课式在案例库中无高度匹配参照，本次以古籍理论/经验日志为主。”'
} else {
  Add-Line '## 六维加权评分表（满分100）'
  Add-Line ''
  Add-Line '> `类神15*` 由 `-LeiShen` 对结构化字段 `类神=` / `技法=` 精确匹配；缺字段则为 0，须人工判读后补加（故自动分上限 85）。'
  Add-Line ''
  Add-Line '| # | 条目 | 类别 | 占类25 | 课体20 | 发用15 | 类神15* | 三传15 | 日干10 | 原始 | 系数 | 最终 | 反馈 | ≥60 |'
  Add-Line '|---|---|---|---|---|---|---|---|---|---|---|---|---|---|'
  $i = 0
  foreach ($r in $rows) {
    $i++
    $pass = if ($r.最终 -ge 60) { '✅' } elseif ($r.最终 -ge 45) { '△(45线)' } else { '❌' }
    Add-Line ("| {0} | {1} | {2} | {3} | {4} | {5} | {6} | {7} | {8} | {9} | ×{10} | **{11}** | {12} | {13} |" -f `
      $i, $r.条目, $r.Kind, $r.'分_占类', $r.'分_课体', $r.'分_发用', $r.'分_类神', $r.'分_三传', $r.'分_日干', $r.原始, $r.系数, $r.最终, $r.反馈, $pass)
  }
  Add-Line ''

  Add-Line '## 历史称验案例提示（须核对迁移条件）'
  Add-Line ''
  $lvl1 = @($rows | Where-Object { $_.反馈 -eq '验' -and $_.最终 -ge 45 })
  if ($lvl1.Count -eq 0) {
    Add-Line '> 当前候选中没有历史称验且达到提示线的案例；结合本课、书籍和经验条目的具体条件判断，不据此推定库中不存在相关方法。'
  } else {
    foreach ($r in $lvl1) {
      Add-Line ("- **{0}**（最终 {1}｜占类={2}｜课体={3}｜发用={4}｜三传={5}）" -f $r.条目, $r.最终, $r.占类, $r.课体, $r.发用, $r.三传)
      Add-Line '  → 读取其断语与反馈，核对问题、类神、空墓旺衰及反例；评分和历史称验不构成直接采信条件。'
    }
  }
}
Add-Line ''
Add-Line '---'
Add-Line '> 纪律：本表由 `tools\search-cases.ps1` 生成，一律锚定 `^<!-- META:`；不含 README/_template/_* 文档噪音。'
Add-Line '> 相似度 ≠ 正确率（幸存者偏差）；同一课可多解，须结合本课显象（空亡/变质）复核。'

$text = ($script:OUT -join [Environment]::NewLine) + [Environment]::NewLine
if ($Scope -eq 'all') { $text += [Environment]::NewLine + (Invoke-ExperienceRetrieval) + [Environment]::NewLine }
if ($OutFile) {
  $full = $OutFile
  if (-not [System.IO.Path]::IsPathRooted($full)) { $full = Join-Path (Get-Location).Path $full }
  [System.IO.File]::WriteAllText($full, $text, (New-Object System.Text.UTF8Encoding($false)))
  Write-Output ("OK -> {0}  ({1} 条命中)" -f $full, $rows.Count)
} else {
  Write-Output $text
}
