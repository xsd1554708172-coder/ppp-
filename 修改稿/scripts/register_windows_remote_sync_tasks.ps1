param(
    [int]$IntervalMinutes = 5
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$runner = Join-Path $scriptDir "run_hidden_sync_check.cmd"
$startupDir = [Environment]::GetFolderPath("Startup")
$startupFile = Join-Path $startupDir "Codex_PPP_RemoteSync_OnStartup.lnk"

if (-not (Test-Path -LiteralPath $runner)) {
    throw ("Runner not found: {0}" -f $runner)
}

$taskRepeat = "Codex_PPP_RemoteSync_Every{0}Min" -f $IntervalMinutes
$taskRun = ('"{0}"' -f $runner)

schtasks /Create /TN $taskRepeat /SC MINUTE /MO $IntervalMinutes /TR $taskRun /RL LIMITED /F | Out-Null
if ($LASTEXITCODE -ne 0) {
    throw "Failed to create repeating sync task."
}

$wsh = New-Object -ComObject WScript.Shell
$shortcut = $wsh.CreateShortcut($startupFile)
$shortcut.TargetPath = $runner
$shortcut.WorkingDirectory = $scriptDir
$shortcut.WindowStyle = 7
$shortcut.Description = "Run Codex PPP remote sync check at Windows logon."
$shortcut.Save()

Write-Output ("Registered repeating task: {0}" -f $taskRepeat)
Write-Output ("Installed startup launcher: {0}" -f $startupFile)
