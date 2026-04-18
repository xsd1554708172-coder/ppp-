param(
    [int]$IntervalSeconds = 300,
    [string]$Remote = "origin"
)

$repoRoot = Split-Path -Parent $PSScriptRoot
$repoRoot = Split-Path -Parent $repoRoot
$checkScript = Join-Path $PSScriptRoot "check_remote_signal_and_sync.ps1"

$indexDir = Get-ChildItem -LiteralPath $repoRoot -Directory | Where-Object { $_.Name -like "00_*" } | Select-Object -First 1
if (-not $indexDir) {
    throw "Index directory not found."
}

$logPath = Join-Path $indexDir.FullName "REMOTE_SYNC_POLL.log"

while ($true) {
    $timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
    try {
        $result = & powershell -ExecutionPolicy Bypass -File $checkScript -Remote $Remote
        $line = ("[{0}] {1}" -f $timestamp, ($result -join " "))
    } catch {
        $line = ("[{0}] ERROR: {1}" -f $timestamp, $_.Exception.Message)
    }

    Add-Content -LiteralPath $logPath -Value $line -Encoding UTF8
    Start-Sleep -Seconds $IntervalSeconds
}

