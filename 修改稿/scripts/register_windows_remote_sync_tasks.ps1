param(
    [int]$IntervalMinutes = 5
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$controlScript = Join-Path $scriptDir "set_windows_auto_sync.ps1"

if (-not (Test-Path -LiteralPath $controlScript)) {
    throw ("Control script not found: {0}" -f $controlScript)
}

& powershell -ExecutionPolicy Bypass -File $controlScript -Mode Enable -IntervalMinutes $IntervalMinutes
exit $LASTEXITCODE
