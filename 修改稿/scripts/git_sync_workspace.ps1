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

git add -A

$status = git status --short
if (-not $status) {
    Write-Output "No changes to commit."
    exit 0
}

git commit -m $CommitMessage
if ($LASTEXITCODE -ne 0) {
    throw "git commit 失败"
}

$remote = git remote
if (-not $remote) {
    Write-Output "Commit created, but no remote is configured."
    exit 0
}

$branch = git branch --show-current
git push origin $branch
if ($LASTEXITCODE -ne 0) {
    throw "git push 失败"
}

Write-Output "Pushed to origin/$branch"
