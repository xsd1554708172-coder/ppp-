param(
    [string]$Remote = "origin",
    [switch]$Quiet
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent $repoRoot

Set-Location $repoRoot

git rev-parse --is-inside-work-tree | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw ("Not a Git repository: {0}" -f $repoRoot)
}

$indexDir = Get-ChildItem -LiteralPath $repoRoot -Directory | Where-Object { $_.Name -like "00_*" } | Select-Object -First 1
if (-not $indexDir) {
    throw "Index directory not found."
}

$statePath = Join-Path $indexDir.FullName "LOCAL_SYNC_STATE.json"
$signalRepoPath = ($indexDir.Name + "/REMOTE_SYNC_SIGNAL.json")
$signalLocalPath = Join-Path $indexDir.FullName "REMOTE_SYNC_SIGNAL.json"

$remoteExists = git remote
if (-not $remoteExists) {
    if (-not $Quiet) {
        Write-Output "No remote is configured."
    }
    exit 0
}

$branch = git branch --show-current
git fetch $Remote
if ($LASTEXITCODE -ne 0) {
    throw "git fetch failed"
}

$localCommit = (git rev-parse HEAD).Trim()
$remoteCommit = (git rev-parse ("{0}/{1}" -f $Remote, $branch)).Trim()
$workingTreeDirty = [bool](git status --short)

$remoteSignal = $null
$remoteSignalRaw = git show ("{0}/{1}:{2}" -f $Remote, $branch, $signalRepoPath) 2>$null
if ($LASTEXITCODE -eq 0 -and $remoteSignalRaw) {
    try {
        $remoteSignal = $remoteSignalRaw | ConvertFrom-Json
    } catch {
        $remoteSignal = $null
    }
}

$state = $null
if (Test-Path -LiteralPath $statePath) {
    try {
        $state = Get-Content -LiteralPath $statePath -Raw | ConvertFrom-Json
    } catch {
        $state = $null
    }
}

$lastSeenSequence = $null
if ($state -and $state.last_seen_signal_sequence -ne $null) {
    $lastSeenSequence = [int]$state.last_seen_signal_sequence
}

$remoteSequence = $null
if ($remoteSignal -and $remoteSignal.signal_sequence -ne $null) {
    $remoteSequence = [int]$remoteSignal.signal_sequence
}

$needsSync = $localCommit -ne $remoteCommit
$signalChanged = $false
if ($remoteSequence -ne $null -and $lastSeenSequence -ne $null) {
    $signalChanged = $remoteSequence -gt $lastSeenSequence
}

if ($needsSync) {
    if ($workingTreeDirty) {
        $blockedState = [ordered]@{
            checked_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
            status = "blocked_dirty_worktree"
            local_head = $localCommit
            remote_head = $remoteCommit
            last_seen_signal_sequence = $lastSeenSequence
            pending_signal_sequence = $remoteSequence
        }
        $blockedState | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $statePath -Encoding UTF8
        throw "Remote update detected, but local working tree is dirty. Sync skipped."
    }

    & powershell -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "sync_from_github.ps1") -Remote $Remote
    if ($LASTEXITCODE -ne 0) {
        throw "sync_from_github.ps1 failed"
    }

    $newLocalCommit = (git rev-parse HEAD).Trim()
    $localSignal = $null
    if (Test-Path -LiteralPath $signalLocalPath) {
        try {
            $localSignal = Get-Content -LiteralPath $signalLocalPath -Raw | ConvertFrom-Json
        } catch {
            $localSignal = $null
        }
    }

    $syncedState = [ordered]@{
        checked_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
        status = "synced"
        local_head = $newLocalCommit
        remote_head = $remoteCommit
        last_seen_signal_sequence = $(if ($localSignal) { $localSignal.signal_sequence } else { $remoteSequence })
        remote_signal_changed = $signalChanged
    }
    $syncedState | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $statePath -Encoding UTF8

    if (-not $Quiet) {
        Write-Output "Remote update synced to local workspace."
    }
    exit 0
}

$currentState = [ordered]@{
    checked_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
    status = "already_current"
    local_head = $localCommit
    remote_head = $remoteCommit
    last_seen_signal_sequence = $(if ($remoteSequence -ne $null) { $remoteSequence } else { $lastSeenSequence })
    remote_signal_changed = $signalChanged
}
$currentState | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $statePath -Encoding UTF8

if (-not $Quiet) {
    Write-Output "Local workspace is already current."
}

