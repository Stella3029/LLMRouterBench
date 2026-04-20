import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from data_collector.config_loader import ConfigLoader
from generators.factory import create_generator


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Smoke test model connectivity using the same config/generator path as benchmark runs."
    )
    parser.add_argument(
        "--config",
        default="config/data_collector_gpqa_medqa_mmlupro.yaml",
        help="Collector config file to load models from.",
    )
    parser.add_argument(
        "--models",
        nargs="*",
        help="Optional subset of model names to test. Defaults to all models in config.",
    )
    parser.add_argument(
        "--prompt",
        default="Reply with exactly: OK",
        help="Prompt used for the connectivity test.",
    )
    parser.add_argument(
        "--output-json",
        help="Optional path to save the full results as JSON.",
    )
    parser.add_argument(
        "--disable-cache",
        action="store_true",
        help="Ignore cache config and hit the model service directly.",
    )
    return parser.parse_args()


def summarize_output(text: str, limit: int = 120) -> str:
    compact = " ".join((text or "").strip().split())
    if len(compact) <= limit:
        return compact
    return compact[: limit - 3] + "..."


def run_single_test(model_config: Dict[str, Any], cache_config: Optional[Dict[str, Any]], prompt: str) -> Dict[str, Any]:
    generator = create_generator(model_config=model_config, cache_config=cache_config)

    started_at = time.time()
    result = generator.generate(prompt)
    elapsed = time.time() - started_at

    output_text = result.output or ""
    success = not output_text.startswith("Generation failed:")

    return {
        "name": model_config["name"],
        "api_model_name": model_config["api_model_name"],
        "base_url": model_config["base_url"],
        "success": success,
        "elapsed_seconds": round(elapsed, 3),
        "prompt_tokens": result.prompt_tokens,
        "completion_tokens": result.completion_tokens,
        "cost": result.cost,
        "output_preview": summarize_output(output_text),
        "error": "" if success else output_text,
    }


def print_results(results: List[Dict[str, Any]]) -> None:
    print(
        f"{'MODEL':<22} {'STATUS':<8} {'SECONDS':<8} {'P_TOK':<8} "
        f"{'C_TOK':<8} {'COST':<10} PREVIEW"
    )
    print("-" * 110)
    for item in results:
        status = "OK" if item["success"] else "FAIL"
        print(
            f"{item['name']:<22} {status:<8} {item['elapsed_seconds']:<8} "
            f"{item['prompt_tokens']:<8} {item['completion_tokens']:<8} "
            f"{item['cost']:<10.6f} {item['output_preview']}"
        )


def main() -> int:
    args = parse_args()

    config_loader = ConfigLoader(args.config)
    benchmark_config = config_loader.load()

    selected_names = set(args.models or [])
    selected_models = []
    for model in benchmark_config.models:
        if selected_names and model.name not in selected_names:
            continue
        selected_models.append(model)

    if not selected_models:
        print("No models selected. Check --models names or config file.", file=sys.stderr)
        return 1

    cache_config = None if args.disable_cache else benchmark_config.cache_config
    if args.disable_cache:
        print("[connectivity] Cache enabled: False")
        print("[connectivity] Cache backend: disabled")
    else:
        print("[connectivity] Cache enabled: True")
        print("[connectivity] Cache backend: redis")
        print("[connectivity] Redis connection status will be reported by runtime cache logs")

    results: List[Dict[str, Any]] = []
    for model in selected_models:
        model_dict = model.__dict__.copy()
        try:
            result = run_single_test(
                model_config=model_dict,
                cache_config=cache_config,
                prompt=args.prompt,
            )
        except Exception as exc:
            result = {
                "name": model.name,
                "api_model_name": model.api_model_name,
                "base_url": model.base_url,
                "success": False,
                "elapsed_seconds": 0.0,
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "cost": 0.0,
                "output_preview": f"Unhandled exception: {exc}",
                "error": str(exc),
            }
        results.append(result)

    print_results(results)

    summary = {
        "config": str(Path(args.config).resolve()),
        "tested_models": len(results),
        "successful_models": sum(1 for item in results if item["success"]),
        "failed_models": sum(1 for item in results if not item["success"]),
        "results": results,
    }

    if args.output_json:
        output_path = Path(args.output_json)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"\nSaved JSON report to: {output_path}")

    return 0 if summary["failed_models"] == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
