param(
    [string]$Remote = "origin"
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent $repoRoot

Set-Location $repoRoot

git rev-parse --is-inside-work-tree | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "当前目录不是 Git 仓库：$repoRoot"
}

$status = git status --short
if ($status) {
    throw "工作区存在未提交改动；请先提交、暂存或清理后再同步远端。"
}

$remoteExists = git remote
if (-not $remoteExists) {
    Write-Output "No remote is configured."
    exit 0
}

$branch = git branch --show-current
git fetch $Remote
if ($LASTEXITCODE -ne 0) {
    throw "git fetch 失败"
}

git pull --rebase $Remote $branch
if ($LASTEXITCODE -ne 0) {
    throw "git pull --rebase 失败"
}

Write-Output "Synced from $Remote/$branch"
