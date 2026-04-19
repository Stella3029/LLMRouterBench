$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

Write-Host "[collector] listing generated benchmark results"
python -m data_collector.cli list --output-dir results --order dataset
