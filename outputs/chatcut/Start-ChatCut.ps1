param([switch]$NoBrowser)
$ErrorActionPreference = 'Stop'
$taskRoot = $PSScriptRoot
$taskConfigPath = Join-Path $taskRoot '.local/config.json'
if (-not (Test-Path -LiteralPath $taskConfigPath)) { throw 'Run local/setup.py first to install the free local models.' }
$taskConfig = Get-Content -LiteralPath $taskConfigPath -Raw | ConvertFrom-Json
$taskRunning = $false
try { $taskHealth = Invoke-RestMethod -Uri 'http://127.0.0.1:5173/api/health' -TimeoutSec 2; $taskRunning = $taskHealth.local -eq $true } catch {}
if (-not $taskRunning) {
    $taskPython = $taskConfig.python_executable
    if (-not (Test-Path -LiteralPath $taskPython)) { $taskPython = (Get-Command python).Source }
    $taskArgs = @('"' + (Join-Path $taskRoot 'local/service.py') + '"')
    Start-Process -FilePath $taskPython -ArgumentList $taskArgs -WorkingDirectory $taskRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $taskRoot '.local/logs/service-output.log') -RedirectStandardError (Join-Path $taskRoot '.local/logs/service-error.log') | Out-Null
    $taskLoaded = $false
    for ($taskTry = 0; $taskTry -lt 30; $taskTry++) {
        Start-Sleep -Seconds 1
        try { $taskHealth = Invoke-RestMethod -Uri 'http://127.0.0.1:5173/api/health' -TimeoutSec 2; if ($taskHealth.local) { $taskLoaded = $true; break } } catch {}
    }
    if (-not $taskLoaded) { throw 'MadCut could not start. See .local/logs/service-error.log.' }
}
if (-not $NoBrowser) { Start-Process 'http://127.0.0.1:5173/' }
Write-Host 'MadCut is running. Models load locally; no API account or payments are required.'
