param(
    [string]$Python = 'python',
    [ValidateRange(1024, 65535)][int]$Port = 8766
)
$ErrorActionPreference = 'Stop'
$siteDirectory = Join-Path $PSScriptRoot 'docs\handbook\dist'
Write-Host "ALIVE handbook: http://127.0.0.1:$Port"
Write-Host 'This serves documentation only, on this computer. Ctrl+C stops the server.'
Write-Host 'Alternatively, open docs\handbook\ALIVE_Handbook.html without a server.'
& $Python -m http.server $Port --bind 127.0.0.1 --directory $siteDirectory
if ($LASTEXITCODE -ne 0) { throw 'The handbook server could not start. Check Python and whether the port is already in use.' }
