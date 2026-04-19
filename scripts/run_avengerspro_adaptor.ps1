$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$outputDir = 'baselines/AvengersPro/data/gpqa_medqa_mmlupro'
$config = 'config/baseline_config_gpqa_medqa_mmlupro_cost.yaml'
$cacheMode = if ($env:REDIS_ENABLED -match '^(?i:true|1|yes|on)$') { 'redis' } else { 'disabled' }
Write-Host "[avengerspro-adaptor] cache mode: $cacheMode"
Write-Host "[avengerspro-adaptor] readiness check"
python scripts/check_avengerspro_ready.py --repo-root $RepoRoot

Write-Host "[avengerspro-adaptor] generating train/test JSONL from results/bench"
python -m baselines.adaptors.avengerspro_adaptor --config $config --seed 42 --split-ratio 0.8 --output-dir $outputDir
