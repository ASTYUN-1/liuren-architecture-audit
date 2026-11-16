# Read-only local Liuren verification. Does not start chart or website services.
$ErrorActionPreference = 'Stop'
$taskRoot = $PSScriptRoot
$taskPython = Get-Command python -ErrorAction Stop
Push-Location -LiteralPath $taskRoot
try {
    & $taskPython.Source -X utf8 (Join-Path $taskRoot 'tools\liuren-workflow.py') doctor
    $taskExit = $LASTEXITCODE
} finally {
    Pop-Location
}
exit $taskExit
