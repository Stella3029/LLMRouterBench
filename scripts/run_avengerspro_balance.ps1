$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$outputDir = 'outputs/avengerspro'
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null
$config = 'baselines/AvengersPro/config/balance_config_gpqa_medqa_mmlupro.json'
$resultFile = Join-Path $outputDir 'results_avengerspro_balance_gpqa_medqa_mmlupro.json'
$summaryFile = Join-Path $outputDir 'summary_avengerspro_balance_gpqa_medqa_mmlupro.json'

Write-Host "[avengerspro-balance] readiness check"
python scripts/check_avengerspro_ready.py --repo-root $RepoRoot

Write-Host "[avengerspro-balance] running balance cluster router"
python -m baselines.AvengersPro.balance_cluster_router --config $config --output $resultFile

Write-Host "[avengerspro-balance] summarizing results"
python scripts/summarize_avengerspro_results.py --results $resultFile --output-json $summaryFile
