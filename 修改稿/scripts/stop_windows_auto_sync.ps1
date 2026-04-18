param(
    [int]$IntervalMinutes = 5,
    [switch]$StopRunningProcesses
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$controlScript = Join-Path $scriptDir "set_windows_auto_sync.ps1"

if (-not (Test-Path -LiteralPath $controlScript)) {
    throw ("Control script not found: {0}" -f $controlScript)
}

$argList = @(
    "-ExecutionPolicy", "Bypass",
    "-File", $controlScript,
    "-Mode", "Disable",
    "-IntervalMinutes", $IntervalMinutes
)

if ($StopRunningProcesses) {
    $argList += "-StopRunningProcesses"
}

& powershell @argList
if ($LASTEXITCODE -ne 0) {
    throw "Failed to disable Windows auto-sync."
}

Write-Output "Windows auto-sync has been disabled. Startup shortcut is preserved."
