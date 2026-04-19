$ErrorActionPreference = 'Stop'

$RepoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $RepoRoot

# RouterDC training is NOT part of the MVP path.
# Use this only in a GPU + DeepSpeed environment with torch.distributed / NCCL available.
# The adaptor must be run first to generate the JSON files.

$trainDir = 'baselines/RouterDC/data/gpqa_medqa_mmlupro/seed42_split0.8'
$saveDir = 'baselines/RouterDC/logs/gpqa_medqa_mmlupro'
$modelName = 'gte-Qwen2-7B-instruct'

Write-Host '[routerdc-train] prerequisite checks:'
Write-Host "  - generated data dir: $trainDir"
Write-Host "  - deepspeed config: baselines/RouterDC/ds_config.json"
Write-Host "  - model name/path: $modelName"
Write-Host ''
Write-Host 'Example command (edit model path/name if needed):'
Write-Host @"
deepspeed --num_gpus=1 baselines/RouterDC/train_router_mdeberta_7b.py `
  --model_name $modelName `
  --data_paths $trainDir/gpqa_train.json $trainDir/medqa_train.json $trainDir/mmlupro_train.json `
  --test_data_paths $trainDir/gpqa_test.json $trainDir/medqa_test.json $trainDir/mmlupro_test.json `
  --test_data_type probability probability probability `
  --save_path $saveDir `
  --deepspeed baselines/RouterDC/ds_config.json `
  --training_steps 300 `
  --eval_steps 50 `
  --batch_size 8 `
  --training_samples_per_dataset 1000 `
  --wandb_project routerdc_gpqa_medqa_mmlupro
"@
