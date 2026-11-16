param([switch]$ValidateOnly)
$ErrorActionPreference = 'Stop'
$sourceSkill = Join-Path $PSScriptRoot 'daliuren-codex'
$skillsRoot = Join-Path $env:USERPROFILE '.codex\skills'
$targetSkill = Join-Path $skillsRoot 'daliuren-codex'
$resolvedRoot = [IO.Path]::GetFullPath($skillsRoot)
$resolvedTarget = [IO.Path]::GetFullPath($targetSkill)
if ([IO.Path]::GetDirectoryName($resolvedTarget) -ne $resolvedRoot) { throw 'Target escapes Codex skills directory.' }
if (-not (Test-Path -LiteralPath $skillsRoot -PathType Container)) { throw 'Existing Codex skills directory not found.' }
if ((Get-Item -LiteralPath $skillsRoot).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Linked skills root is not supported.' }
if ((Test-Path -LiteralPath $targetSkill) -and ((Get-Item -LiteralPath $targetSkill).Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Linked target is not supported.' }
$skillFiles = @('SKILL.md', 'references\host.md', 'agents\openai.yaml')
foreach ($relativeFile in $skillFiles) {
    $sourceFile = Join-Path $sourceSkill $relativeFile
    $targetFile = Join-Path $targetSkill $relativeFile
    if (-not (Test-Path -LiteralPath $sourceFile -PathType Leaf)) { throw "Missing source: $relativeFile" }
    if (Test-Path -LiteralPath $targetFile) {
        if ((Get-Item -LiteralPath $targetFile).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "Linked target file: $relativeFile" }
        if ((Get-FileHash -LiteralPath $sourceFile -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath $targetFile -Algorithm SHA256).Hash) { throw "Existing different skill file; no overwrite: $relativeFile" }
    }
}
if (-not $ValidateOnly) {
    foreach ($relativeFile in $skillFiles) {
        $sourceFile = Join-Path $sourceSkill $relativeFile
        $targetFile = Join-Path $targetSkill $relativeFile
        if (-not (Test-Path -LiteralPath $targetFile)) {
            $targetDirectory = [IO.Path]::GetDirectoryName($targetFile)
            New-Item -ItemType Directory -Path $targetDirectory -Force | Out-Null
            Copy-Item -LiteralPath $sourceFile -Destination $targetFile
        }
        if ((Get-FileHash -LiteralPath $sourceFile -Algorithm SHA256).Hash -ne (Get-FileHash -LiteralPath $targetFile -Algorithm SHA256).Hash) { throw "Installation hash mismatch: $relativeFile" }
    }
}
[pscustomobject]@{ validated = $true; installed = (-not $ValidateOnly); target = $targetSkill; files = $skillFiles } | ConvertTo-Json
