$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$outputDir = 'outputs/avengerspro'
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
$config = 'baselines/AvengersPro/config/simple_config_gpqa_medqa_mmlupro.json'
$resultFile = Join-Path $outputDir 'results_avengerspro_simple_gpqa_medqa_mmlupro.json'
$summaryFile = Join-Path $outputDir 'summary_avengerspro_simple_gpqa_medqa_mmlupro.json'
$cacheMode = if ($env:REDIS_ENABLED -match '^(?i:true|1|yes|on)$') { 'redis' } else { 'disabled' }

Write-Host "[avengerspro-simple] cache mode: $cacheMode"
Write-Host "[avengerspro-simple] readiness check"
python scripts/check_avengerspro_ready.py --repo-root $RepoRoot

Write-Host "[avengerspro-simple] running simple cluster router"
python -m baselines.AvengersPro.simple_cluster_router --config $config --output $resultFile

Write-Host "[avengerspro-simple] summarizing results"
python scripts/summarize_avengerspro_results.py --results $resultFile --output-json $summaryFile
