import argparse
import json
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description='Quick readiness check for GPQA/MedQA/MMLUPro AvengersPro flow')
    parser.add_argument('--repo-root', default='.', help='Repository root')
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    checks = {
        'gpqa_data': root / 'data/GPQA/gpqa_diamond.json',
        'medqa_data': root / 'data/MedQA/test.json',
        'mmlupro_data': root / 'data/MMLUPro/test.json',
        'collector_config': root / 'config/data_collector_gpqa_medqa_mmlupro.yaml',
        'embedding_config': root / 'config/embedding_config_llm2.yaml',
        'avengers_simple_config': root / 'baselines/AvengersPro/config/simple_config_gpqa_medqa_mmlupro.json',
        'avengers_balance_config': root / 'baselines/AvengersPro/config/balance_config_gpqa_medqa_mmlupro.json',
        'model_groups': root / 'config/model_groups_gpqa_medqa_mmlupro.yaml',
    }

    result = {name: path.exists() for name, path in checks.items()}
    result['results_bench_exists'] = (root / 'results/bench').exists()
    result['avengers_data_exists'] = (root / 'baselines/AvengersPro/data/gpqa_medqa_mmlupro/seed42_split0.8').exists()
    result['outputs_avengerspro_exists'] = (root / 'outputs/avengerspro').exists()

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
