param(
    [string]$Remote = "origin"
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent $repoRoot

Set-Location $repoRoot

git rev-parse --is-inside-work-tree | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw ("Not a Git repository: {0}" -f $repoRoot)
}

$status = git status --short
if ($status) {
    throw "Working tree has uncommitted changes. Commit, stash, or clean it first."
}

$remoteExists = git remote
if (-not $remoteExists) {
    Write-Output "No remote is configured."
    exit 0
}

$branch = git branch --show-current
git fetch $Remote
if ($LASTEXITCODE -ne 0) {
    throw "git fetch failed"
}

git pull --rebase $Remote $branch
if ($LASTEXITCODE -ne 0) {
    throw "git pull --rebase failed"
}

Write-Output ("Synced from {0}/{1}" -f $Remote, $branch)

