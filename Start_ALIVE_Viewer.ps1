param([string]$Python = 'python')

# Creates an isolated environment for the viewer; no RL packages or GPU needed.
$ErrorActionPreference = 'Stop'
$projectRoot = $PSScriptRoot
$environmentPython = Join-Path $projectRoot '.venv-viewer\Scripts\python.exe'
Set-Location -LiteralPath $projectRoot
if (-not (Test-Path -LiteralPath $environmentPython)) {
    Write-Host 'Creating the ALIVE viewer environment (Python 3.11+ required)...'
    & $Python -m venv (Join-Path $projectRoot '.venv-viewer')
    if ($LASTEXITCODE -ne 0) { throw 'Python environment creation failed. Install Python 3.11+ or supply -Python with its executable path.' }
}
& $environmentPython -c 'import pygame, alive.viewer'
if ($LASTEXITCODE -ne 0) {
    Write-Host 'Installing the local viewer and its graphics dependency...'
    & $environmentPython -m pip install -e '.[viewer]'
    if ($LASTEXITCODE -ne 0) { throw 'Viewer installation failed. Check your internet connection and Python version.' }
}
& $environmentPython -m alive.viewer
if ($LASTEXITCODE -ne 0) { throw 'The viewer exited with an error. See the output above.' }
