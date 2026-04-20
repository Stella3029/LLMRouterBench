from __future__ import annotations

import json
from typing import Any, Dict, Optional

from loguru import logger

from .config import RedisConfig


class RedisCacheStore:
    def __init__(self, config: RedisConfig):
        self.config = config
        self.client = None
        try:
            import redis

            self.client = redis.Redis(
                host=config.host,
                port=config.port,
                password=config.password or None,
                db=config.db,
                username=config.username,
                ssl=config.ssl,
                decode_responses=True,
            )
            self.client.ping()
            logger.info(f"Redis cache connected: {config.host}:{config.port}/{config.db} prefix={config.key_prefix}")
        except Exception as exc:
            logger.warning(f"Redis unavailable, cache disabled: {exc}")
            self.client = None

    def _full_key(self, key: str) -> str:
        return f"{self.config.key_prefix}:{key}"

    def is_available(self) -> bool:
        return self.client is not None

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        if self.client is None:
            return None
        try:
            value = self.client.get(self._full_key(key))
            return json.loads(value) if value else None
        except Exception as exc:
            logger.warning(f"Redis get failed for key {key[:16]}...: {exc}")
            return None

    def put(self, key: str, value: Dict[str, Any]) -> bool:
        if self.client is None:
            return False
        try:
            payload = json.dumps(value, ensure_ascii=False)
            full_key = self._full_key(key)
            if self.config.ttl_seconds:
                self.client.setex(full_key, self.config.ttl_seconds, payload)
            else:
                self.client.set(full_key, payload)
            return True
        except Exception as exc:
            logger.warning(f"Redis put failed for key {key[:16]}...: {exc}")
            return False

    def stats(self) -> Dict[str, Any]:
        if self.client is None:
            return {"available": False}
        try:
            info = self.client.info("stats")
            return {
                "available": True,
                "key_prefix": self.config.key_prefix,
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
            }
        except Exception as exc:
            logger.warning(f"Redis stats failed: {exc}")
            return {"available": True, "error": str(exc)}
