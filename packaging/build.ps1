$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

py -3.13 -m venv .build-venv
& .\.build-venv\Scripts\python.exe -m pip install --upgrade pip
& .\.build-venv\Scripts\python.exe -m pip install -r requirements-build.txt

if (Test-Path dist) { Remove-Item dist -Recurse -Force }
if (Test-Path build) { Remove-Item build -Recurse -Force }
& .\.build-venv\Scripts\pyinstaller.exe --clean packaging\VirtualTaylorFrame.spec

$portable = "dist\VirtualTaylorFrame-Portable"
if (Test-Path $portable) { Remove-Item $portable -Recurse -Force }
Copy-Item "dist\VirtualTaylorFrame" $portable -Recurse
Compress-Archive -Path "$portable\*" -DestinationPath "dist\VirtualTaylorFrame-Portable.zip" -Force

$iscc = Get-Command iscc -ErrorAction SilentlyContinue
if ($iscc) { & $iscc.Source packaging\VirtualTaylorFrame.iss }
else { Write-Warning "Inno Setup (iscc.exe) not found; installer was not built." }
