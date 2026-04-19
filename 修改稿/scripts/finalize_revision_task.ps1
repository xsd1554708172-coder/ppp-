param(
    [Parameter(Mandatory = $true)]
    [string]$SourcePath,

    [Parameter(Mandatory = $true)]
    [string]$Token,

    [string]$Timestamp = "",

    [string]$CommitMessage = ""
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$revisionRoot = Split-Path -Parent $scriptDir
$repoRoot = Split-Path -Parent $revisionRoot

if (-not $CommitMessage) {
    $CommitMessage = "chore: archive and sync $Token revision"
}

$archiveScript = Join-Path $scriptDir "archive_revision_output.py"
$indexScript = Join-Path $scriptDir "refresh_revision_indexes.py"
$logScript = Join-Path $scriptDir "write_revision_operation_log.py"
$syncScript = Join-Path $scriptDir "git_sync_workspace.ps1"

if (-not (Test-Path -LiteralPath $archiveScript)) {
    throw "Archive script not found: $archiveScript"
}

if (-not (Test-Path -LiteralPath $indexScript)) {
    throw "Index refresh script not found: $indexScript"
}

if (-not (Test-Path -LiteralPath $logScript)) {
    throw "Operation log script not found: $logScript"
}

if (-not (Test-Path -LiteralPath $syncScript)) {
    throw "Git sync script not found: $syncScript"
}

$archiveArgs = @($archiveScript, "--source", $SourcePath, "--token", $Token)
if ($Timestamp) {
    $archiveArgs += @("--timestamp", $Timestamp)
}

$archiveTarget = & python @archiveArgs
if ($LASTEXITCODE -ne 0) {
    throw "Archive step failed."
}

Write-Output "Archived revision to: $archiveTarget"

& python $indexScript
if ($LASTEXITCODE -ne 0) {
    throw "Index refresh step failed."
}

$series = ""
if ($Token.ToLower().StartsWith("v1")) {
    $series = "v1"
} elseif ($Token.ToLower().StartsWith("v2")) {
    $series = "v2"
} else {
    $series = "workspace"
}

$logArgs = @(
    $logScript,
    "--action", "finalize_revision_task",
    "--series", $series,
    "--token", $Token,
    "--source", $SourcePath,
    "--archive", $archiveTarget,
    "--note", "Archived revised manuscript and refreshed 修改稿 indexes.",
    "--commit-message", $CommitMessage
)

$logPath = & python @logArgs
if ($LASTEXITCODE -ne 0) {
    throw "Operation log step failed."
}

Write-Output "Operation log written to: $logPath"

& powershell -ExecutionPolicy Bypass -File $syncScript -CommitMessage $CommitMessage
if ($LASTEXITCODE -ne 0) {
    throw "Git sync step failed."
}
