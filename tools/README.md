# 🔧 Tools

The **Tools** module provides utility scripts for LLMRouterBench system maintenance, result management, and debugging.

---

## 📑 Tool List

| # | Tool | Purpose |
|:---|:---|:---|
| 1 | `cache_writer` | Legacy cache backfill helper (deprecated for runtime path) |
| 2 | `visualize_embeddings` | Visualize question embeddings with dimensionality reduction |
| 3 | `test_embedding_model` | Sanity-check embedding model configuration |

---

## 1️⃣ cache_writer

`cache_writer` is now a legacy helper. Runtime caching no longer uses MySQL and the default runtime path is Redis-only.

### Important note

- Runtime benchmark collection already writes successful requests into Redis immediately.
- That is the supported path for resumable runs after interruption.
- This tool should not be treated as the primary cache path anymore.
- If you use it, align its config with Redis-shaped cache settings instead of MySQL.

### Recommended workflow

1. Configure Redis in `.env`.
2. Run collector or connectivity scripts normally.
3. Let successful requests populate Redis online.
4. Rerun after interruption to reuse cached requests.
