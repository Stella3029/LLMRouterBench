$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

Write-Host '=== MVP routing experiment: collector -> AvengersPro adaptor -> Simple -> Balance ==='
& (Join-Path $PSScriptRoot 'run_collect_gpqa_medqa_mmlupro.ps1')
& (Join-Path $PSScriptRoot 'list_results.ps1')
& (Join-Path $PSScriptRoot 'run_avengerspro_adaptor.ps1')
& (Join-Path $PSScriptRoot 'run_avengerspro_simple.ps1')
& (Join-Path $PSScriptRoot 'run_avengerspro_balance.ps1')
