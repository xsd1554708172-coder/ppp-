param(
    [string]$CommitMessage = "chore: sync PPP manuscript workspace"
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent $repoRoot

Set-Location $repoRoot

git rev-parse --is-inside-work-tree | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "当前目录不是 Git 仓库：$repoRoot"
}

$remote = git remote
$branch = git branch --show-current
git add -A

$status = git status --short
if ($status) {
    git commit -m $CommitMessage
    if ($LASTEXITCODE -ne 0) {
        throw "git commit 失败"
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
    throw "git fetch 失败"
}

git pull --rebase origin $branch
if ($LASTEXITCODE -ne 0) {
    throw "git pull --rebase 失败"
}

git push origin $branch
if ($LASTEXITCODE -ne 0) {
    throw "git push 失败"
}

if ($status) {
    Write-Output "Committed and pushed to origin/$branch"
} else {
    Write-Output "No local changes; synced from and confirmed against origin/$branch"
}
