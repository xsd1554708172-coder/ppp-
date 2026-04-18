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
$syncScript = Join-Path $scriptDir "git_sync_workspace.ps1"

if (-not (Test-Path -LiteralPath $archiveScript)) {
    throw "Archive script not found: $archiveScript"
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

& powershell -ExecutionPolicy Bypass -File $syncScript -CommitMessage $CommitMessage
if ($LASTEXITCODE -ne 0) {
    throw "Git sync step failed."
}
