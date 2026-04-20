from __future__ import annotations

from dataclasses import asdict, is_dataclass
from functools import wraps
from typing import Any, Callable, Dict, Optional

from loguru import logger

from .config import CacheConfig
from .key_generator import CacheKeyGenerator
from .redis_store import RedisCacheStore


class CacheDecorator:
    def __init__(self, config: CacheConfig):
        self.config = config
        self.key_generator = CacheKeyGenerator(config.key_generator)
        self.store = None
        self.stats = {"hits": 0, "misses": 0, "writes": 0}

        if not config.enabled:
            logger.info("Cache disabled: no cache backend will be initialized.")
            return

        backend = config.backend.lower()
        if backend != "redis":
            logger.warning(f"Cache disabled: unsupported backend '{backend}'. Redis is the only supported runtime backend.")
            self.config.enabled = False
            return

        store = RedisCacheStore(config.redis)
        if store.is_available():
            self.store = store
        else:
            self.config.enabled = False
            logger.warning("Cache disabled because Redis is unavailable.")

    def __call__(self, func: Callable[..., Any], generator_instance=None):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not self.config.enabled or self.store is None:
                return func(*args, **kwargs)

            key_payload = self._build_key_payload(func, generator_instance, args, kwargs)
            cache_key = self.key_generator.generate_key(**key_payload)

            cached = None
            if self.config.force_override_cache:
                logger.debug(f"cache skip read force_override_cache=true key={cache_key}")
            else:
                cached = self.store.get(cache_key)

            if cached is not None:
                self.stats["hits"] += 1
                logger.debug(f"cache hit key={cache_key}")
                result = self._restore_result(func, cached)
                if result is not None:
                    return result

            self.stats["misses"] += 1
            logger.debug(f"cache miss key={cache_key}")
            result = func(*args, **kwargs)
            serialized = self._serialize_result(result)
            if self._should_cache(serialized):
                if self.store.put(cache_key, serialized):
                    self.stats["writes"] += 1
                    logger.debug(f"cache write key={cache_key}")
            else:
                logger.debug(f"cache skip write key={cache_key}")
            return result

        return wrapper

    def _build_key_payload(self, func: Callable[..., Any], generator_instance, args, kwargs) -> Dict[str, Any]:
        payload: Dict[str, Any] = {}
        instance = generator_instance or getattr(func, "__self__", None)
        if instance is not None:
            payload.update({
                "model": getattr(instance, "config_name", getattr(instance, "model_name", None)),
                "temperature": getattr(instance, "temperature", None),
                "top_p": getattr(instance, "top_p", None),
                "reasoning_effort": getattr(instance, "reasoning_effort", None),
            })

        if args:
            first = args[0]
            if isinstance(first, str):
                payload.setdefault("messages", [{"role": "user", "content": first}])
                payload.setdefault("input", first)
            elif isinstance(first, list):
                payload.setdefault("messages", first)
                payload.setdefault("input", first)

        payload.update(kwargs)
        return payload

    def _serialize_result(self, result: Any) -> Dict[str, Any]:
        if is_dataclass(result):
            return asdict(result)
        if isinstance(result, dict):
            return result
        return {"value": result}

    def _restore_result(self, func: Callable[..., Any], cached: Dict[str, Any]) -> Optional[Any]:
        annotations = getattr(func, "__annotations__", {})
        return_type = annotations.get("return")
        if return_type is None:
            return cached
        try:
            if hasattr(return_type, "__dataclass_fields__"):
                return return_type(**cached)
        except Exception as exc:
            logger.warning(f"Failed to restore cached result, using miss path: {exc}")
            return None
        return cached

    def _should_cache(self, payload: Dict[str, Any]) -> bool:
        if not self.config.conditions.cache_successful_only:
            return True

        if "embeddings" in payload:
            return bool(payload.get("embeddings"))

        completion_tokens = payload.get("completion_tokens", 0) or 0
        if completion_tokens < self.config.conditions.min_completion_tokens:
            return False

        output = payload.get("output")
        if output in (None, ""):
            return False
        if isinstance(output, str):
            lowered = output.strip().lower()
            if lowered.startswith("generation failed:") or lowered.startswith("multimodal generation failed:") or lowered.startswith("processing failed:"):
                return False
        return True


def create_cache_decorator(cache_config: Optional[Dict[str, Any]] = None) -> CacheDecorator:
    config = CacheConfig.from_dict(cache_config or {})
    return CacheDecorator(config)
