# Redis extension notes for LLMRouterBench

当前仓库并不原生支持 Redis。

已确认的事实：
- 现有配置文件中的缓存结构都是 `mysql:` 风格，例如：
  - `config/data_collector_small_model_config.yaml`
  - `config/data_collector_proprietary_model_config.yaml`
  - `config/embedding_config.yaml`
  - `.env.example`
- 生成器侧缓存入口在 `generators/generator.py` 中通过 `common.cache.decorator.create_cache_decorator` 接入。
- 但当前 checkout 中并没有找到 `common/cache/` 目录，因此完整缓存后端并未随仓库一起提供。

因此，本次为 GPQA / MedQA / MMLUPro + AvengersPro / RouterDC 实验准备的配置默认采用：
- `cache.enabled: false`
- 不依赖 MySQL
- 也不伪造 Redis 支持

如果后续要扩展 Redis，最小改造方案是：
1. 在 `common/cache/` 下补一个 Redis store 实现，例如 `redis_store.py`。
2. 在 `common.cache.decorator` / cache config parser 中增加 `redis:` 分支。
3. 让 `create_cache_decorator(...)` 能根据配置识别：
   - `cache.redis.host`
   - `cache.redis.port`
   - `cache.redis.password`
   - `cache.redis.db`
   - `cache.redis.key_prefix`
4. 对齐 `llm2/src/cache.py` 中的 key 生成与序列化思路。

建议：
- 先用当前无缓存方案跑通 collector + AvengersPro。
- 等实验链条稳定后，再单独补 Redis，不要把它塞进首轮可运行路径里。
