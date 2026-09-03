$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$python = Get-Command py -ErrorAction SilentlyContinue
if (-not $python) { throw "Python Launcher (py.exe) is required to build Virtual Taylor Frame." }
& $python.Source -3.13 -m venv .build-venv
& .\.build-venv\Scripts\python.exe -m pip install --upgrade pip
& .\.build-venv\Scripts\python.exe -m pip install -r requirements-build.txt

if (Test-Path dist) { Remove-Item dist -Recurse -Force }
if (Test-Path build) { Remove-Item build -Recurse -Force }
& .\.build-venv\Scripts\pyinstaller.exe --clean packaging\VirtualTaylorFrame.spec

$portable = "dist\VirtualTaylorFrame-Portable"
if (Test-Path $portable) { Remove-Item $portable -Recurse -Force }
Copy-Item "dist\VirtualTaylorFrame" $portable -Recurse
Compress-Archive -Path "$portable\*" -DestinationPath "dist\VirtualTaylorFrame-Portable.zip" -Force

Write-Host "Portable artifact: dist\VirtualTaylorFrame-Portable.zip"
Write-Host "Run packaging\VirtualTaylorFrame.iss with Inno Setup to create the installer."
