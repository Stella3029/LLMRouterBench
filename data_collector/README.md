# 🔌 Collector

The **Collector** module provides unified API access to LLMs with caching, retries, and cost tracking for benchmark data collection.

---

## 🚀 Quick Start

```bash
python -m data_collector.cli info config/data_collector_example.yaml
python -m data_collector.cli run config/data_collector_example.yaml
python -m data_collector.cli list
```

---

## ⚙️ Configuration

See `config/data_collector_example.yaml` for the fully annotated configuration reference.

### Structure

```yaml
models:
  - name: gpt-4o-mini
    api_model_name: openai/gpt-4o-mini
    base_url: https://openrouter.ai/api/v1
    api_key: OPENROUTER_API_KEY
    temperature: 0.2
    timeout: 600

datasets:
  - dataset_id: mmlu_pro
    splits: ["test"]

run:
  output_dir: ./results
  concurrency: 32
  demo_mode: false

cache:
  enabled: true
  backend: redis
  redis:
    host: REDIS_HOST
    port: REDIS_PORT
    db: REDIS_DB
    key_prefix: REDIS_KEY_PREFIX
```

### Key Options

| Section | Field | Description |
|:---|:---|:---|
| **models** | `generator_type` | `direct` (text), `multimodal` (vision), `embedding` |
| **run** | `demo_mode` | Test with limited samples |
| **run** | `concurrency` | Parallel API calls |
| **cache** | `enabled` | Redis caching for cost reduction, resumable runs, and evaluator iteration |

---

## 🔧 Redis Caching

Runtime cache is now **Redis-first and Redis-only**.

### Why Cache?

1. **Dataset Subset Reuse**: later full runs can reuse subset calls.
2. **Resumable Runs**: reruns after failures or Ctrl+C can hit Redis for completed requests.
3. **Evaluator Iteration**: with `cache_raw_response: true`, evaluator logic can be iterated without re-calling APIs.

### Configuration Reference

```yaml
cache:
  enabled: true
  backend: redis
  force_override_cache: false
  redis:
    host: REDIS_HOST
    port: REDIS_PORT
    password: REDIS_PASSWORD
    db: REDIS_DB
    key_prefix: REDIS_KEY_PREFIX
    ssl: REDIS_SSL
    ttl_seconds: null
  key_generator:
    cached_parameters: ["model", "temperature", "top_p", "messages", "reasoning_effort"]
  conditions:
    cache_successful_only: true
    min_completion_tokens: 0
    cache_raw_response: false
    refresh_if_missing_raw_response: false
```

### Runtime behavior

- Startup logs show `Cache enabled`, `Cache backend`, and either Redis connected or disabled.
- Requests follow `get -> call -> put`.
- `cache hit`, `cache miss`, `cache write`, and `force_override_cache` are observable in logs.
- If Redis is unavailable, runtime logs `Redis unavailable, cache disabled` and continues uncached.
- Failed outputs are not written into cache.
