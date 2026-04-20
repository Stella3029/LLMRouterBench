# 🔌 External Benchmark Integration

A lightweight API wrapper for integrating complex third-party benchmarks (SWE-bench, τ²-bench, etc.) that are too difficult to port into LLMRouterBench's standard evaluation system.

---

## ✨ Why external_bench?

Some benchmarks are **too complex to integrate** into the standard pipeline:
- **SWE-bench**: Multi-step agent workflows, code execution environments
- **τ²-bench**: Complex multi-turn interactions, specialized environments

**external_bench provides minimal-touch integration**:
- Use LLMRouterBench's unified API management (`DirectGenerator`)
- Benefit from Redis caching to reduce API costs and support resumable runs
- Keep your entire evaluation system unchanged

---

## 🚀 Quick Start

### Step 1: Add Imports

```python
from external_bench import setup, DirectGenerator, RecordResult, finish_benchmark, start_timer
setup()
```

### Step 2: Initialize Generator

```python
generator = DirectGenerator(
    model_name="anthropic/claude-3.5-sonnet",
    api_key=os.environ["ANTHROPIC_API_KEY"],
    base_url="https://api.anthropic.com/v1",
    cache_config=cache_config  # Optional Redis cache config
)
```

### Step 3: Replace API Calls

```python
def query_model(prompt):
    result = generator.generate(prompt)
    return result.output
```

### Step 4: Save Results

```python
accuracy = finish_benchmark(record_results, "gpt-4", "your_benchmark", "test")
```

---

## 📖 API Reference

### DirectGenerator

```python
DirectGenerator(
    model_name: str,
    api_key: str,
    base_url: str,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    cache_config: dict = None  # Redis cache config
)
```

---

## ✅ Integration Checklist

- [ ] Import `DirectGenerator`, `RecordResult`, `finish_benchmark`, `start_timer`
- [ ] Replace API calls with `generator.generate()`
- [ ] Add `RecordResult` collection after each evaluation
- [ ] Call `start_timer()` at benchmark start
- [ ] Call `finish_benchmark()` at benchmark end
- [ ] (Optional) Enable Redis caching

**Do NOT**:
- Refactor benchmark structure
- Change evaluation metrics or logic
- Modify workflow orchestration
