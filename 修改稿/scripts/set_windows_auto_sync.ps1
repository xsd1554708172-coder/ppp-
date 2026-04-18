param(
    [ValidateSet("Enable", "Disable")]
    [string]$Mode,

    [int]$IntervalMinutes = 5,

    [switch]$StopRunningProcesses
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Split-Path -Parent $scriptDir
$repoRoot = Split-Path -Parent $repoRoot
$runner = Join-Path $scriptDir "run_hidden_sync_check.cmd"
$startupDir = [Environment]::GetFolderPath("Startup")
$startupFile = Join-Path $startupDir "Codex_PPP_RemoteSync_OnStartup.lnk"
$taskRepeat = "Codex_PPP_RemoteSync_Every{0}Min" -f $IntervalMinutes
$indexDir = Get-ChildItem -LiteralPath $repoRoot -Directory | Where-Object { $_.Name -like "00_*" } | Select-Object -First 1

if (-not $indexDir) {
    throw "Index directory not found."
}

$controlPath = Join-Path $indexDir.FullName "AUTO_SYNC_CONTROL.json"

if (-not (Test-Path -LiteralPath $runner)) {
    throw ("Runner not found: {0}" -f $runner)
}

function Ensure-StartupShortcut {
    $wsh = New-Object -ComObject WScript.Shell
    $shortcut = $wsh.CreateShortcut($startupFile)
    $shortcut.TargetPath = $runner
    $shortcut.WorkingDirectory = $scriptDir
    $shortcut.WindowStyle = 7
    $shortcut.Description = "Run Codex PPP remote sync check at Windows logon."
    $shortcut.Save()
}

function Write-ControlFile([bool]$EnabledValue) {
    $payload = [ordered]@{
        enabled = $EnabledValue
        interval_minutes = $IntervalMinutes
        updated_at = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ssK")
        updated_by = ("{0}@{1}" -f $env:USERNAME, $env:COMPUTERNAME)
        note = "Local control for Windows auto-sync. Startup shortcut is retained; disabled mode exits without syncing."
    }
    $payload | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $controlPath -Encoding UTF8
}

if ($Mode -eq "Enable") {
    $taskRun = ('"{0}"' -f $runner)
    schtasks /Create /TN $taskRepeat /SC MINUTE /MO $IntervalMinutes /TR $taskRun /RL LIMITED /F | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to create repeating sync task."
    }

    Ensure-StartupShortcut
    Write-ControlFile -EnabledValue ([bool]$true)
    Write-Output ("Windows auto-sync enabled. Task: {0}" -f $taskRepeat)
    Write-Output ("Startup shortcut preserved at: {0}" -f $startupFile)
    exit 0
}

schtasks /Query /TN $taskRepeat >$null 2>$null
if ($LASTEXITCODE -eq 0) {
    schtasks /Change /TN $taskRepeat /DISABLE | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to disable repeating sync task."
    }
}

Ensure-StartupShortcut
Write-ControlFile -EnabledValue ([bool]$false)

if ($StopRunningProcesses) {
    $patterns = @(
        "check_remote_signal_and_sync.ps1",
        "watch_remote_sync.ps1",
        "guarded_sync_check.ps1",
        "run_hidden_sync_check.cmd"
    )

    $candidates = Get-CimInstance Win32_Process | Where-Object {
        $cmd = $_.CommandLine
        if (-not $cmd) { return $false }
        foreach ($pattern in $patterns) {
            if ($cmd -like ("*{0}*" -f $pattern)) {
                return $true
            }
        }
        return $false
    }

    foreach ($proc in $candidates) {
        Stop-Process -Id $proc.ProcessId -Force -ErrorAction SilentlyContinue
    }
}

Write-Output ("Windows auto-sync disabled. Task disabled if present: {0}" -f $taskRepeat)
Write-Output ("Startup shortcut preserved at: {0}" -f $startupFile)
