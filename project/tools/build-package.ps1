<#
.SYNOPSIS
  六壬八字体系包 —— 全量整合打包器（可复现）。

.DESCRIPTION
  把当前项目打成可分发的**全量整合包**，替代此前的三个分散包
  （六壬体系包-20260805 / 六壬体系包-增量-20260806 / 八字系列-核心包-20260806）。

  排除规则硬编码在 Test-Excluded 里，避免把手头垃圾打进包：

    默认排除
      - .opencode\node_modules\        opencode 运行时依赖（约 52 MB，非项目内容）
      - *.bak / *.orig / *.gbk.bak     编辑备份
      - 根目录 *.zip                   旧分包本体（已被本包取代）
      - .git\ / output\ / 临时文件
      - *.ps1 / *.md 之外的无主临时产物（见 -ExtraExclude）

    默认包含（与旧全量包 六壬体系包-20260805 收录范围对齐）
      .opencode\（不含 node_modules）、books\、案例项目库\、经验日志\、八字经验库\、
      书籍库\、排盘存档\、排盘工具魔改\（含 bazi-paipan\node_modules）、tools\、
      根级 opencode.json / README.md / 使用说明.txt / 更新说明.txt / *.bat / verify-system.ps1

  包内额外写入一份 `打包清单-<version>.txt`（清单+校验用），不落盘到项目。

.EXAMPLE
  powershell -ExecutionPolicy Bypass -File tools\build-package.ps1
  powershell -ExecutionPolicy Bypass -File tools\build-package.ps1 -Version 20260916-全量整合版
  powershell -ExecutionPolicy Bypass -File tools\build-package.ps1 -DryRun
#>
[CmdletBinding()]
param(
  [string]$Version   = (Get-Date -Format 'yyyy-MM-dd'),
  [string]$OutFile   = '',
  [string]$Name      = '六壬八字体系包',
  [switch]$DryRun,
  [string[]]$ExtraExclude = @(),
  [int]$ShowTop      = 12
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root      = Split-Path -Parent $scriptDir
if (-not (Test-Path -LiteralPath (Join-Path $root '.opencode'))) { throw "项目根定位失败：$root" }

# ---------------- 排除规则 ----------------
function Test-Excluded {
  param([string]$Rel)
  $r = $Rel -replace '\\', '/'
  if ($r -like '.opencode/node_modules*')  { return $true }   # 运行时依赖，最大的一块垃圾
  if ($r -match '\.(bak|orig)$')           { return $true }
  if ($r -match '\.gbk\.bak$')             { return $true }
  if ($r -match '^[^/]+\.zip$')            { return $true }   # 根目录旧分包
  if ($r -eq '.git' -or $r -like '.git/*') { return $true }
  if ($r -like 'output/*')                 { return $true }
  if ($r -like '**/Thumbs.db' -or $r -like '**/desktop.ini') { return $true }
  foreach ($pat in $ExtraExclude) { if ($r -like $pat) { return $true } }
  return $false
}

# ---------------- 收集 ----------------
$sep = [System.IO.Path]::DirectorySeparatorChar
$files = @()
$excludedCount = 0
Get-ChildItem -LiteralPath $root -Recurse -File -Force -ErrorAction SilentlyContinue | ForEach-Object {
  $rel = $_.FullName.Substring($root.Length + 1)
  if (Test-Excluded $rel) { $excludedCount++ } else { $files += $_ }
}
$files = @($files | Sort-Object FullName)

$totalMB = [math]::Round((($files | Measure-Object Length -Sum).Sum)/1MB, 2)

if ([string]::IsNullOrWhiteSpace($OutFile)) {
  $OutFile = Join-Path $root ("{0}-{1}.zip" -f $Name, $Version)
}
if (-not [System.IO.Path]::IsPathRooted($OutFile)) { $OutFile = Join-Path (Get-Location).Path $OutFile }

# ---------------- 顶层构成 ----------------
$top = @{}
foreach ($f in $files) {
  $r = $f.FullName.Substring($root.Length + 1) -replace '\\','/'
  $seg = ($r -split '/')[0]
  if ($r -notmatch '/') { $seg = '(根文件)' }
  if (-not $top.ContainsKey($seg)) { $top[$seg] = @{ n = 0; mb = 0.0 } }
  $top[$seg].n++
  $top[$seg].mb += $f.Length/1MB
}

# ---------------- 打包清单 ----------------
$ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
$mf = New-Object System.Text.StringBuilder
[void]$mf.AppendLine("$Name - 全量整合包  打包清单")
[void]$mf.AppendLine("版本: $Version")
[void]$mf.AppendLine("打包时间: $ts")
[void]$mf.AppendLine("文件数: $($files.Count)    未压缩合计: $totalMB MB")
[void]$mf.AppendLine("排除文件数: $excludedCount")
[void]$mf.AppendLine("")
[void]$mf.AppendLine("== 顶层构成 ==")
foreach ($k in ($top.Keys | Sort-Object)) {
  [void]$mf.AppendLine(("  {0,-24} {1,6} files  {2,8:N2} MB" -f $k, $top[$k].n, $top[$k].mb))
}
[void]$mf.AppendLine("")
[void]$mf.AppendLine("== 排除规则 ==")
[void]$mf.AppendLine("  .opencode\node_modules\ / *.bak / *.orig / *.gbk.bak / 根目录 *.zip / .git\ / output\")
[void]$mf.AppendLine("")
[void]$mf.AppendLine("== 安装 ==")
[void]$mf.AppendLine("  1. 解压到任意目录（建议路径不含空格）")
[void]$mf.AppendLine("  2. 装 Node.js（>=14）")
[void]$mf.AppendLine("  3. 双击 verify-system.bat 自检")
[void]$mf.AppendLine("")
[void]$mf.AppendLine("== 文件明细 ==")
foreach ($f in $files) {
  [void]$mf.AppendLine(("  {0,10:N0} B  {1}" -f $f.Length, ($f.FullName.Substring($root.Length + 1))))
}

if ($DryRun) {
  Write-Output "=== DRY RUN（未写盘）==="
  Write-Output ("目标: {0}" -f $OutFile)
  Write-Output ("打包文件数: {0}   未压缩: {1} MB   已排除: {2}" -f $files.Count, $totalMB, $excludedCount)
  Write-Output ""
  Write-Output "顶层构成:"
  foreach ($k in ($top.Keys | Sort-Object)) { Write-Output ("  {0,-24} {1,6} files  {2,8:N2} MB" -f $k, $top[$k].n, $top[$k].mb) }
  exit 0
}

# ---------------- 写盘 ----------------
if (Test-Path -LiteralPath $OutFile) { Remove-Item -LiteralPath $OutFile -Force }
$zip = [System.IO.Compression.ZipFile]::Open($OutFile, [System.IO.Compression.ZipArchiveMode]::Create)
try {
  $i = 0
  foreach ($f in $files) {
    $rel = ($f.FullName.Substring($root.Length + 1)).Replace('\', '/')
    $entry = $zip.CreateEntry($rel, [System.IO.Compression.CompressionLevel]::Optimal)
    $es = $entry.Open()
    $fs = [System.IO.File]::OpenRead($f.FullName)
    try { $fs.CopyTo($es) } finally { $fs.Dispose(); $es.Dispose() }
    $i++
    if ($i % 50 -eq 0) { Write-Progress -Activity '打包中' -Status "$i / $($files.Count)" -PercentComplete ([int](100*$i/$files.Count)) }
  }
  # 包内清单
  $mEntry = $zip.CreateEntry(("打包清单-{0}.txt" -f $Version), [System.IO.Compression.CompressionLevel]::Optimal)
  $sw = New-Object System.IO.StreamWriter($mEntry.Open(), (New-Object System.Text.UTF8Encoding($false)))
  try { $sw.Write($mf.ToString()) } finally { $sw.Dispose() }
} finally {
  $zip.Dispose()
  Write-Progress -Activity '打包中' -Completed
}

$zi = Get-Item -LiteralPath $OutFile
Write-Output "OK -> $($zi.FullName)"
Write-Output ("  条目 $($files.Count + 1)（含清单）   压缩后 {0:N2} MB   （原始 $totalMB MB）" -f ($zi.Length/1MB))
Write-Output ("  已排除 $excludedCount 个文件")
Write-Output ""
Write-Output "顶层构成（前 $ShowTop）:"
$top.Keys | Sort-Object { -$top[$_].mb } | Select-Object -First $ShowTop | ForEach-Object {
  Write-Output ("  {0,-24} {1,6} files  {2,8:N2} MB" -f $_, $top[$_].n, $top[$_].mb)
}
