$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$config = Join-Path $RepoRoot 'config/data_collector_gpqa_medqa_mmlupro.yaml'
Write-Host "[collector] readiness check"
python scripts/check_avengerspro_ready.py --repo-root $RepoRoot
Write-Host "[collector] showing config info: $config"
python -m data_collector.cli info $config

Write-Host "[collector] running benchmark collection"
python -m data_collector.cli run $config -y
