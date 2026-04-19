$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

Write-Host '=== Full routing experiment: MVP + RouterDC data preparation ==='
& (Join-Path $PSScriptRoot 'run_mvp_routing_experiment.ps1')
& (Join-Path $PSScriptRoot 'run_routerdc_adaptor.ps1')
Write-Host ''
Write-Host 'RouterDC training is not auto-executed in this full script.'
Write-Host 'Use scripts/run_routerdc_train_template.ps1 after preparing a GPU + DeepSpeed environment.'
