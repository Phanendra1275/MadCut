$ErrorActionPreference = 'Stop'
$taskFontSource = Join-Path $PSScriptRoot 'public\fonts'
$taskFontDestination = Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Fonts'
New-Item -ItemType Directory -Force -Path $taskFontDestination | Out-Null
$taskFontRegistry = 'HKCU:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts'
if (-not (Test-Path -LiteralPath $taskFontRegistry)) { New-Item -Path $taskFontRegistry | Out-Null }
$taskFontBackupFolder = Join-Path $PSScriptRoot '.local\font-backups'
New-Item -ItemType Directory -Force -Path $taskFontBackupFolder | Out-Null
$taskFontBackup = Join-Path $taskFontBackupFolder ('user-fonts-'+(Get-Date -Format 'yyyyMMdd-HHmmssfff')+'.reg')
& reg.exe export 'HKCU\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Fonts' $taskFontBackup /y | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'Could not back up user font registrations.' }
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public static class MadCutFontInstall {
 [DllImport("gdi32.dll", CharSet=CharSet.Unicode)] public static extern int AddFontResourceEx(string path,uint flags,IntPtr reserved);
 [DllImport("user32.dll", CharSet=CharSet.Unicode)] public static extern IntPtr SendMessageTimeout(IntPtr hwnd,uint msg,IntPtr w,IntPtr l,uint flags,uint timeout,out IntPtr result);
}
"@
$taskFontFiles = @(
 @{File='Inter-Variable.ttf';Dest='MadCut-Inter-Variable.ttf';Name='Inter Variable (TrueType)'},
 @{File='Satisfy-Regular.ttf';Dest='Satisfy-Regular.ttf';Name='Satisfy Regular (TrueType)'}
)
foreach ($taskFontFile in $taskFontFiles) {
 $taskSourceFile = Join-Path $taskFontSource $taskFontFile.File
 $taskDestinationFile = Join-Path $taskFontDestination $taskFontFile.Dest
 if (Test-Path -LiteralPath $taskDestinationFile) {
  if ((Get-FileHash -LiteralPath $taskSourceFile).Hash -ne (Get-FileHash -LiteralPath $taskDestinationFile).Hash) { throw "An existing different font will not be overwritten: $taskDestinationFile" }
 } else { Copy-Item -LiteralPath $taskSourceFile -Destination $taskDestinationFile }
 New-ItemProperty -Path $taskFontRegistry -Name $taskFontFile.Name -Value $taskDestinationFile -PropertyType String -Force | Out-Null
 $taskFontAdded = [MadCutFontInstall]::AddFontResourceEx($taskDestinationFile,0,[IntPtr]::Zero)
 if ($taskFontAdded -lt 1) { throw "Windows could not load $taskDestinationFile" }
 Write-Host "Installed $($taskFontFile.Name) for this Windows user."
}
$taskFontBroadcast = [IntPtr]::Zero
[MadCutFontInstall]::SendMessageTimeout([IntPtr]0xffff,0x001D,[IntPtr]::Zero,[IntPtr]::Zero,2,2000,[ref]$taskFontBroadcast) | Out-Null
