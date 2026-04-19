param(
    [string]$CommitMessage = "chore: sync PPP manuscript workspace"
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent $repoRoot
$refreshScript = Join-Path $PSScriptRoot "refresh_revision_indexes.py"
$indexDir = Get-ChildItem -LiteralPath $repoRoot -Directory | Where-Object { $_.Name -like "00_*" } | Select-Object -First 1
if (-not $indexDir) {
    throw "Index directory not found."
}
$signalPath = Join-Path $indexDir.FullName "REMOTE_SYNC_SIGNAL.json"

Set-Location $repoRoot

git rev-parse --is-inside-work-tree | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "褰撳墠鐩綍涓嶆槸 Git 浠撳簱锛?repoRoot"
}

if (Test-Path -LiteralPath $refreshScript) {
    & python $refreshScript | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "refresh_revision_indexes.py 执行失败"
    }
}

$remote = git remote
$branch = git branch --show-current
git add -A

$status = git status --short
if ($status) {
    $sequence = 1
    if (Test-Path -LiteralPath $signalPath) {
        try {
            $existingSignal = Get-Content -LiteralPath $signalPath -Raw | ConvertFrom-Json
            if ($existingSignal.signal_sequence) {
                $sequence = [int]$existingSignal.signal_sequence + 1
            }
        } catch {
            $sequence = 1
        }
    }

    $signalPayload = [ordered]@{
        project        = "ppp-paper-workspace"
        signal_version = 1
        signal_sequence = $sequence
        last_pushed_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
        updated_by     = ("{0}@{1}" -f $env:USERNAME, $env:COMPUTERNAME)
        branch         = $branch
        purpose        = "Tracked sync signal for remote-to-local workspace updates."
        note           = "Refreshed automatically by git_sync_workspace.ps1 before push."
    }

    $signalPayload | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $signalPath -Encoding UTF8
    git add -A

    git commit -m $CommitMessage
    if ($LASTEXITCODE -ne 0) {
        throw "git commit 澶辫触"
    }
}

if (-not $remote) {
    if ($status) {
        Write-Output "Commit created, but no remote is configured."
    } else {
        Write-Output "No changes to commit and no remote is configured."
    }
    exit 0
}

git fetch origin
if ($LASTEXITCODE -ne 0) {
    throw "git fetch 澶辫触"
}

git pull --rebase origin $branch
if ($LASTEXITCODE -ne 0) {
    throw "git pull --rebase 澶辫触"
}

git push origin $branch
if ($LASTEXITCODE -ne 0) {
    throw "git push 澶辫触"
}

if ($status) {
    Write-Output "Committed and pushed to origin/$branch"
} else {
    Write-Output "No local changes; synced from and confirmed against origin/$branch"
}

