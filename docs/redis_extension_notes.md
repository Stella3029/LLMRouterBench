# Redis extension notes for LLMRouterBench

当前仓库已经统一为 Redis-first、Redis-only 的运行时缓存设计。

当前行为：
- `common/cache/` 提供正式 Redis 运行时缓存实现。
- 生成器侧缓存入口在 `generators/generator.py` 中通过 `common.cache.decorator.create_cache_decorator` 接入。
- 默认运行路径只支持 Redis，不再默认尝试 MySQL。
- 如果 Redis 不可用，程序会明确记录 `Redis unavailable, cache disabled`，然后继续以 no-cache 模式运行。
- 成功请求会在返回后立即写入 Redis，因此中断后重跑可以复用已成功缓存的请求。

统一配置约定：
- `REDIS_HOST`
- `REDIS_PORT`
- `REDIS_PASSWORD`
- `REDIS_DB`
- `REDIS_KEY_PREFIX`
- `REDIS_SSL`

推荐用法：
1. 在 `.env` 中填入 Redis 连接配置。
2. 直接运行 collector / connectivity / avengers 相关脚本，无需额外 wrapper、无需 `--cache-mode redis`。
3. 启动日志会显示：
   - `Cache enabled: True`
   - `Cache backend: redis`
   - `Redis cache connected: host:port/db prefix=...`
   - 或 `Redis unavailable, cache disabled: ...`
4. 请求期间可在 debug 日志中看到 `cache hit` / `cache miss` / `cache write`。

说明：
- 仓库中的 MySQL 缓存文件仅保留为 deprecated legacy stub，不参与默认运行路径。
- 如需显式禁用缓存，只应通过明确的 disable 入口，而不是依赖默认回退到 SQL。
