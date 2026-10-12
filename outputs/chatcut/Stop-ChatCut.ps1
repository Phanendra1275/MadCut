$ErrorActionPreference = 'Stop'
$taskRoot = (Resolve-Path -LiteralPath $PSScriptRoot).Path
$taskPidPath = Join-Path $taskRoot '.local/runtime-pids.json'
if (Test-Path -LiteralPath $taskPidPath) {
    $taskPids = Get-Content -LiteralPath $taskPidPath -Raw | ConvertFrom-Json
    foreach ($taskProcessId in @($taskPids.service, $taskPids.speech, $taskPids.correction, $taskPids.translation, $taskPids.language)) {
        if ($taskProcessId) {
            $taskProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $taskProcessId" -ErrorAction SilentlyContinue
            if ($taskProcess -and $taskProcess.CommandLine -and $taskProcess.CommandLine.Replace('/', '\').IndexOf($taskRoot.Replace('/', '\'), [StringComparison]::OrdinalIgnoreCase) -ge 0) { Stop-Process -Id $taskProcessId -ErrorAction SilentlyContinue }
        }
    }
}
Write-Host 'MadCut has stopped.'
