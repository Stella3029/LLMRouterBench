$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

$outputDir = 'baselines/RouterDC/data/gpqa_medqa_mmlupro'
$config = 'config/baseline_config_gpqa_medqa_mmlupro.yaml'
$embedding = 'config/embedding_config_llm2.yaml'

Write-Host "[routerdc-adaptor] generating RouterDC JSON datasets"
python -m baselines.adaptors.routerdc_adaptor --config $config --seed 42 --split-ratio 0.8 --n-clusters 16 --embedding-config $embedding --output-dir $outputDir
