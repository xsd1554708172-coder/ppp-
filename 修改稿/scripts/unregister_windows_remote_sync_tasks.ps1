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

Write-Output ("Removed repeating task if present: {0}" -f $taskRepeat)
Write-Output ("Removed startup launcher if present: {0}" -f $startupFile)
