from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from loguru import logger


TRUTHY = {"1", "true", "yes", "on"}
FALSY = {"0", "false", "no", "off"}


def _resolve_env(value: Any) -> Any:
    if not isinstance(value, str):
        return value
    env_value = os.getenv(value)
    return env_value if env_value is not None else value


def _resolve_int(value: Any, default: int) -> int:
    resolved = _resolve_env(value)
    if resolved in (None, ""):
        return default
    return int(resolved)


def _resolve_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    resolved = _resolve_env(value)
    if isinstance(resolved, bool):
        return resolved

    normalized = str(resolved).strip().lower()
    if normalized in TRUTHY:
        return True
    if normalized in FALSY:
        return False
    return default


@dataclass
class MySQLConfig:
    host: str = "localhost"
    port: int = 3306
    user: str = "root"
    password: str = ""
    database: str = "llmrouterbench"
    table_name: str = "generator_output_cache"
    ttl_seconds: Optional[int] = None
    use_connection_pool: bool = False

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "MySQLConfig":
        data = data or {}
        ttl = _resolve_env(data.get("ttl_seconds"))
        return cls(
            host=str(_resolve_env(data.get("host", "localhost"))),
            port=_resolve_int(data.get("port", 3306), 3306),
            user=str(_resolve_env(data.get("user", "root"))),
            password=str(_resolve_env(data.get("password", ""))),
            database=str(_resolve_env(data.get("database", "llmrouterbench"))),
            table_name=str(_resolve_env(data.get("table_name", "generator_output_cache"))),
            ttl_seconds=int(ttl) if ttl not in (None, "", "null") else None,
            use_connection_pool=_resolve_bool(data.get("use_connection_pool"), False),
        )


@dataclass
class RedisConfig:
    host: str = "localhost"
    port: int = 6379
    password: str = ""
    db: int = 0
    ttl_seconds: Optional[int] = None
    key_prefix: str = "llmrouterbench:cache"
    username: Optional[str] = None
    ssl: bool = False

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "RedisConfig":
        data = data or {}
        ttl = _resolve_env(data.get("ttl_seconds"))
        username = _resolve_env(data.get("username"))
        return cls(
            host=str(_resolve_env(data.get("host", "localhost"))),
            port=_resolve_int(data.get("port", 6379), 6379),
            password=str(_resolve_env(data.get("password", ""))),
            db=_resolve_int(data.get("db", 0), 0),
            ttl_seconds=int(ttl) if ttl not in (None, "", "null") else None,
            key_prefix=str(_resolve_env(data.get("key_prefix", "llmrouterbench:cache"))),
            username=str(username) if username not in (None, "") else None,
            ssl=_resolve_bool(data.get("ssl"), False),
        )


@dataclass
class KeyGeneratorConfig:
    cached_parameters: List[str] = field(default_factory=lambda: ["model", "temperature", "top_p", "messages", "reasoning_effort"])
    hash_algorithm: str = "blake2b"
    hash_digest_size: int = 16

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "KeyGeneratorConfig":
        data = data or {}
        return cls(
            cached_parameters=list(data.get("cached_parameters", ["model", "temperature", "top_p", "messages", "reasoning_effort"])),
            hash_algorithm=str(data.get("hash_algorithm", "blake2b")),
            hash_digest_size=int(data.get("hash_digest_size", 16)),
        )


@dataclass
class CacheConditions:
    cache_successful_only: bool = True
    min_completion_tokens: int = 0
    cache_raw_response: bool = False
    refresh_if_missing_raw_response: bool = False

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "CacheConditions":
        data = data or {}
        return cls(
            cache_successful_only=_resolve_bool(data.get("cache_successful_only"), True),
            min_completion_tokens=int(data.get("min_completion_tokens", 0)),
            cache_raw_response=_resolve_bool(data.get("cache_raw_response"), False),
            refresh_if_missing_raw_response=_resolve_bool(data.get("refresh_if_missing_raw_response"), False),
        )


@dataclass
class CacheConfig:
    enabled: bool = True
    backend: str = "redis"
    force_override_cache: bool = False
    mysql: MySQLConfig = field(default_factory=MySQLConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    key_generator: KeyGeneratorConfig = field(default_factory=KeyGeneratorConfig)
    conditions: CacheConditions = field(default_factory=CacheConditions)
    log_level: str = "INFO"
    enable_stats: bool = True

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "CacheConfig":
        data = data or {}
        config = cls(
            enabled=_resolve_bool(data.get("enabled"), True),
            backend=str(_resolve_env(data.get("backend", "redis"))).lower(),
            force_override_cache=_resolve_bool(data.get("force_override_cache"), False),
            mysql=MySQLConfig.from_dict(data.get("mysql")),
            redis=RedisConfig.from_dict(data.get("redis")),
            key_generator=KeyGeneratorConfig.from_dict(data.get("key_generator")),
            conditions=CacheConditions.from_dict(data.get("conditions")),
            log_level=str(data.get("log_level", "INFO")),
            enable_stats=_resolve_bool(data.get("enable_stats"), True),
        )

        if config.backend != "redis":
            logger.warning(
                f"Cache backend '{config.backend}' is deprecated and unsupported at runtime; "
                "Redis is the only supported cache backend."
            )

        logger.info(f"Cache enabled: {config.enabled}")
        logger.info(f"Cache backend: {config.backend}")
        logger.info(f"Cache force_override_cache: {config.force_override_cache}")
        return config
