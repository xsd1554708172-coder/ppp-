param(
    [int]$IntervalMinutes = 5
)

$taskRepeat = "Codex_PPP_RemoteSync_Every{0}Min" -f $IntervalMinutes
$startupDir = [Environment]::GetFolderPath("Startup")
$startupFile = Join-Path $startupDir "Codex_PPP_RemoteSync_OnStartup.lnk"

foreach ($taskName in @($taskRepeat)) {
    schtasks /Delete /TN $taskName /F 2>$null | Out-Null
}

if (Test-Path -LiteralPath $startupFile) {
    Remove-Item -LiteralPath $startupFile -Force
}

Remove-Item -LiteralPath (Join-Path ((Get-ChildItem -LiteralPath (Split-Path -Parent (Split-Path -Parent $PSScriptRoot)) -Directory | Where-Object { $_.Name -like "00_*" } | Select-Object -First 1).FullName) "AUTO_SYNC_CONTROL.json") -Force -ErrorAction SilentlyContinue

Write-Output ("Removed repeating task if present: {0}" -f $taskRepeat)
Write-Output ("Removed startup launcher if present: {0}" -f $startupFile)
Write-Output "This is a full uninstall. For everyday enable/disable, use set_windows_auto_sync.ps1 instead."
