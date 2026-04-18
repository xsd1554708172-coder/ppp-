param(
    [string]$Remote = "origin"
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent $repoRoot
$indexDir = Get-ChildItem -LiteralPath $repoRoot -Directory | Where-Object { $_.Name -like "00_*" } | Select-Object -First 1
if (-not $indexDir) {
    throw "Index directory not found."
}

$controlPath = Join-Path $indexDir.FullName "AUTO_SYNC_CONTROL.json"
$checkScript = Join-Path $PSScriptRoot "check_remote_signal_and_sync.ps1"

$enabled = $true
if (Test-Path -LiteralPath $controlPath) {
    try {
        $control = Get-Content -LiteralPath $controlPath -Raw | ConvertFrom-Json
        if ($control.enabled -ne $null) {
            $enabled = [bool]$control.enabled
        }
    } catch {
        $enabled = $true
    }
}

if (-not $enabled) {
    Write-Output "Auto-sync is disabled by local control file."
    exit 0
}

& powershell -ExecutionPolicy Bypass -File $checkScript -Remote $Remote
exit $LASTEXITCODE
