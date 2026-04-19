import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

import yaml


def load_json(path: Path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_model_groups(path: Path):
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    return set(data.get('small_models', [])), set(data.get('large_models', []))


def pct(n, d):
    return (100.0 * n / d) if d else 0.0


def main():
    parser = argparse.ArgumentParser(description='Summarize AvengersPro routing results')
    parser.add_argument('--results', required=True, help='Path to AvengersPro results JSON')
    parser.add_argument('--model-groups', default='config/model_groups_gpqa_medqa_mmlupro.yaml', help='Path to model group YAML')
    parser.add_argument('--output-json', default=None, help='Optional path to save summary JSON')
    args = parser.parse_args()

    results_path = Path(args.results)
    payload = load_json(results_path)
    result = payload.get('results', {})
    config = payload.get('config', {})

    small_models, large_models = load_model_groups(Path(args.model_groups))

    total_queries = result.get('total_queries', 0)
    correct_routes = result.get('correct_routes', 0)
    accuracy = result.get('accuracy', 0.0)
    model_selection_stats = result.get('model_selection_stats', {}) or {}
    dataset_performance = result.get('dataset_performance', {}) or {}
    cost_analysis = result.get('cost_analysis', {}) or {}

    total_model_selections = sum(model_selection_stats.values())
    small_selection_count = sum(count for model, count in model_selection_stats.items() if model in small_models)
    large_selection_count = sum(count for model, count in model_selection_stats.items() if model in large_models)

    per_model_accuracy = {}
    dataset_model_accuracy = result.get('dataset_model_accuracy', {}) or {}
    if dataset_model_accuracy:
        merged = defaultdict(list)
        for _, per_dataset in dataset_model_accuracy.items():
            for model, scores in per_dataset.items():
                merged[model].extend(scores)
        for model, scores in merged.items():
            per_model_accuracy[model] = sum(scores) / len(scores) if scores else 0.0

    # Fallback when detailed routing accuracy traces are not serialized into the result file.
    # In that case, we still expose selection counts and aggregate router accuracy.
    per_model_summary = []
    all_models = sorted(model_selection_stats.keys())
    for model in all_models:
        per_model_summary.append({
            'model': model,
            'selection_count': model_selection_stats.get(model, 0),
            'selection_ratio_percent': round(pct(model_selection_stats.get(model, 0), total_model_selections), 2),
            'group': 'small' if model in small_models else ('large' if model in large_models else 'unknown'),
            'avg_accuracy_when_selected': round(per_model_accuracy.get(model, 0.0), 4)
        })

    summary = {
        'results_file': str(results_path),
        'router_accuracy_percent': round(accuracy, 4),
        'correct_routes': correct_routes,
        'total_queries': total_queries,
        'total_model_selections': total_model_selections,
        'small_model_selection_count': small_selection_count,
        'large_model_selection_count': large_selection_count,
        'small_model_selection_ratio_percent': round(pct(small_selection_count, total_model_selections), 2),
        'large_model_selection_ratio_percent': round(pct(large_selection_count, total_model_selections), 2),
        'dataset_performance': dataset_performance,
        'cost_analysis': cost_analysis,
        'per_model_summary': per_model_summary,
        'config_snapshot': {
            'n_clusters': config.get('n_clusters'),
            'max_router': config.get('max_router'),
            'performance_weight': config.get('performance_weight'),
            'cost_sensitivity': config.get('cost_sensitivity')
        }
    }

    print('=== AvengersPro Routing Summary ===')
    print(f"Results file: {results_path}")
    print(f"Router accuracy: {accuracy:.4f}")
    print(f"Correct routes / total queries: {correct_routes}/{total_queries}")
    print(f"Total model selections: {total_model_selections}")
    print(f"Small-model selections: {small_selection_count} ({summary['small_model_selection_ratio_percent']:.2f}%)")
    print(f"Large-model selections: {large_selection_count} ({summary['large_model_selection_ratio_percent']:.2f}%)")

    if cost_analysis:
        print('--- Cost ---')
        print(f"Total cost: ${cost_analysis.get('total_cost', 0.0):.6f}")
        print(f"Avg cost/query: ${cost_analysis.get('avg_cost_per_query', 0.0):.6f}")
        print(f"Cost per correct prediction: ${cost_analysis.get('cost_per_correct_prediction', 0.0):.6f}")
        print(f"Cost efficiency: {cost_analysis.get('cost_efficiency', 0.0):.6f}")

    if per_model_summary:
        print('--- Model usage ---')
        for item in per_model_summary:
            print(
                f"{item['model']}: count={item['selection_count']}, "
                f"ratio={item['selection_ratio_percent']:.2f}%, "
                f"group={item['group']}, "
                f"avg_accuracy_when_selected={item['avg_accuracy_when_selected']:.4f}"
            )

    if args.output_json:
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        print(f"Summary JSON saved to: {output_path}")


if __name__ == '__main__':
    main()
