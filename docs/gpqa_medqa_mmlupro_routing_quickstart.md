# GPQA / MedQA / MMLUPro Routing Experiment Quickstart

This repo now contains a minimal runnable path for:
- benchmark collection on `gpqa`, `medqa`, `mmlupro`
- baseline conversion for AvengersPro and RouterDC
- running `AvengersPro Simple`
- running `AvengersPro Balance`
- preparing RouterDC data and a training command template

## Configs added
- `config/data_collector_gpqa_medqa_mmlupro.yaml`
- `config/baseline_config_gpqa_medqa_mmlupro.yaml`
- `config/baseline_config_gpqa_medqa_mmlupro_cost.yaml`
- `config/embedding_config_llm2.yaml`
- `baselines/AvengersPro/config/simple_config_gpqa_medqa_mmlupro.json`
- `baselines/AvengersPro/config/balance_config_gpqa_medqa_mmlupro.json`
- `baselines/RouterDC/ds_config.json`

## Scripts added
- `scripts/run_collect_gpqa_medqa_mmlupro.ps1`
- `scripts/list_results.ps1`
- `scripts/run_avengerspro_adaptor.ps1`
- `scripts/run_avengerspro_simple.ps1`
- `scripts/run_avengerspro_balance.ps1`
- `scripts/run_routerdc_adaptor.ps1`
- `scripts/run_routerdc_train_template.ps1`

## MVP sequence
1. Fill environment variables from `.env.example`.
2. Ensure Redis connection settings are present in `.env`.
3. Run collector.
4. Generate AvengersPro train/test JSONL.
5. Run AvengersPro Simple.
6. Run AvengersPro Balance.

## Full sequence
1. MVP sequence
2. Generate RouterDC dataset JSON files
3. Run RouterDC in a GPU + DeepSpeed environment using the template script

## Cache note
- Runtime cache is Redis-first and Redis-only.
- Main configs now default to Redis cache enabled.
- You do not need wrapper flags or `--cache-mode redis` for normal runs.
- If Redis is unavailable, runtime logs `Redis unavailable, cache disabled` and continues uncached.
- Successful requests are written to Redis immediately, so reruns after Ctrl+C can reuse completed samples.
