<#
.SYNOPSIS
案例问题级检索 + 经验条目检索。-LegacyCase 可比较原六维入口。
.EXAMPLE
.\tools\search-cases.ps1 -Query '换工作能否满意' -ZhanLei 事业占 -Scope case -Top 6
#>
[CmdletBinding()]
param(
  [string]$Query = '',
  [string]$ZhanLei = '',
  [string]$KeTi = '',
  [string]$FaYong = '',
  [string]$SanChuan = '',
  [string]$RiGan = '',
  [string]$LeiShen = '',
  [ValidateSet('','验','部分应验','未验','未载')] [string]$Feedback = '',
  [ValidateSet('case','exp','all')] [string]$Scope = 'all',
  [switch]$Strict,
  [int]$Top = 8,
  [string[]]$ExcludeSource = @(),
  [switch]$LegacyCase,
  [string]$OutFile = ''
)
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}
$chunks = [System.Collections.Generic.List[string]]::new()
if ($Scope -in @('case','all')) {
  if ($LegacyCase) {
    $legacyParams = @{Scope='case'; ZhanLei=$ZhanLei; KeTi=$KeTi; FaYong=$FaYong; SanChuan=$SanChuan; RiGan=$RiGan; LeiShen=$LeiShen; Feedback=$Feedback; Top=$Top; Strict=$Strict}
    $legacyText = & (Join-Path $PSScriptRoot 'search-cases-legacy.ps1') @legacyParams
    $chunks.Add(($legacyText -join [Environment]::NewLine))
  } else {
    $caseArgs = @('-X','utf8',(Join-Path $PSScriptRoot 'search-cases.py'))
    if ($Query) { $caseArgs += @('--query',$Query) }
    foreach ($pair in @(@('--category',$ZhanLei),@('--keti',$KeTi),@('--fayong',$FaYong),@('--sanchuan',$SanChuan),@('--rigan',$RiGan),@('--leishen',$LeiShen),@('--feedback',$Feedback))) {
      if ($pair[1]) { $caseArgs += $pair }
    }
    if ($Top -gt 0) { $caseArgs += @('--limit',[string]$Top) }
    if ($Strict) { $caseArgs += '--strict' }
    foreach ($source in $ExcludeSource) { $caseArgs += @('--exclude-source',$source) }
    $caseText = & python @caseArgs
    if ($LASTEXITCODE -ne 0) { throw '案例问题级检索失败，未静默降级为旧索引。' }
    $chunks.Add(($caseText -join [Environment]::NewLine))
  }
}
if ($Scope -in @('exp','all')) {
  $terms = (@($Query,$KeTi,$FaYong,$LeiShen) | Where-Object { $_ }) -join ' '
  $expArgs = @('-X','utf8',(Join-Path $PSScriptRoot 'search-experience.py'))
  if ($terms) { $expArgs += @('--query',$terms) }
  if ($ZhanLei) { foreach ($cat in ($ZhanLei -split '[，,\s]+' | Where-Object { $_ })) { $expArgs += @('--category',$cat) } }
  if ($Top -gt 0) { $expArgs += @('--limit',[string]$Top) }
  if ($Strict) { $expArgs += '--all-terms' }
  foreach ($source in $ExcludeSource) { $expArgs += @('--exclude-source',$source) }
  if ($Feedback) { Write-Warning '经验不按案例反馈字段过滤，逐条核对验证身份。' }
  $expText = & python @expArgs
  if ($LASTEXITCODE -ne 0) { throw '经验条目检索失败。' }
  $chunks.Add(($expText -join [Environment]::NewLine))
}
$resultText = $chunks -join ([Environment]::NewLine + [Environment]::NewLine)
if ($OutFile) {
  $targetFile = $OutFile
  if (-not [System.IO.Path]::IsPathRooted($targetFile)) { $targetFile = Join-Path (Get-Location).Path $targetFile }
  [System.IO.File]::WriteAllText($targetFile,$resultText,[System.Text.UTF8Encoding]::new($false))
} else { Write-Output $resultText }
