param([switch]$Apply,[switch]$Rollback)
$ErrorActionPreference='Stop'
$taskManifestPath=Join-Path $PSScriptRoot 'move-manifest.json'
$taskManifest=Get-Content -LiteralPath $taskManifestPath -Raw -Encoding utf8 | ConvertFrom-Json
$taskProject=[IO.Path]::GetFullPath($taskManifest.root).TrimEnd('\','/')
$taskPrefix=$taskProject+[IO.Path]::DirectorySeparatorChar
function SafePath([string]$rel) {
 $taskAbsolute=[IO.Path]::GetFullPath((Join-Path $taskProject $rel))
 if (-not $taskAbsolute.StartsWith($taskPrefix,[StringComparison]::OrdinalIgnoreCase)) {throw "Target outside project: $rel"}
 return $taskAbsolute
}
function CheckFiles($op,[string]$base) {
 foreach($taskFile in $op.files) {
  $taskFilePath=if($op.kind -eq 'file'){$base}else{Join-Path $base $taskFile.relative}
  $taskItem=Get-Item -LiteralPath $taskFilePath -Force
  if($taskItem.Attributes -band [IO.FileAttributes]::ReparsePoint){throw "Reparse point refused: $taskFilePath"}
  if($taskItem.Length -ne $taskFile.bytes -or (Get-FileHash -LiteralPath $taskFilePath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $taskFile.sha256){throw "Hash mismatch: $taskFilePath"}
 }
}
$taskOperations=@($taskManifest.operations)
if($Rollback){[array]::Reverse($taskOperations)}
# Complete preflight before any move.
foreach($taskOp in $taskOperations){
 $taskSrc=SafePath $(if($Rollback){$taskOp.destination}else{$taskOp.source})
 $taskDst=SafePath $(if($Rollback){$taskOp.source}else{$taskOp.destination})
 if(-not(Test-Path -LiteralPath $taskSrc)){throw "Source missing: $taskSrc"}
 if(Test-Path -LiteralPath $taskDst){throw "Refuse overwrite: $taskDst"}
 $taskSrcItem=Get-Item -LiteralPath $taskSrc -Force
 if($taskSrcItem.Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Refuse root reparse move'}
 CheckFiles $taskOp $taskSrc
}
if(-not $Apply){Write-Output 'Preflight PASS; no changes without -Apply';exit 0}
$taskCompleted=[Collections.Generic.List[object]]::new()
try{
 foreach($taskOp in $taskOperations){
  $taskSrc=SafePath $(if($Rollback){$taskOp.destination}else{$taskOp.source})
  $taskDst=SafePath $(if($Rollback){$taskOp.source}else{$taskOp.destination})
  New-Item -ItemType Directory -Path (Split-Path -Parent $taskDst) -Force | Out-Null
  Move-Item -LiteralPath $taskSrc -Destination $taskDst
  $taskCompleted.Add([pscustomobject]@{op=$taskOp;from=$taskSrc;to=$taskDst})
  CheckFiles $taskOp $taskDst
 }
}catch{
 for($taskI=$taskCompleted.Count-1;$taskI -ge 0;$taskI--){
  $taskDone=$taskCompleted[$taskI]
  if((Test-Path -LiteralPath $taskDone.to) -and -not(Test-Path -LiteralPath $taskDone.from)){
   Move-Item -LiteralPath $taskDone.to -Destination $taskDone.from
  }
 }
 throw
}
$taskResult=[pscustomobject]@{result='PASS';rollback=[bool]$Rollback;operations=$taskCompleted.Count;files=(@($taskManifest.operations | ForEach-Object {$_.files.Count} | Measure-Object -Sum).Sum);verified_sha256=$true;root=$taskProject;manifest_sha256=(Get-FileHash -LiteralPath $taskManifestPath -Algorithm SHA256).Hash.ToLowerInvariant()}
$taskResult | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $PSScriptRoot $(if($Rollback){'rollback-result.json'}else{'move-result.json'})) -Encoding utf8
$taskResult | ConvertTo-Json -Compress
