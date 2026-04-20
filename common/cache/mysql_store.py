from __future__ import annotations

from typing import Any, Dict, Optional

from loguru import logger

from .config import MySQLConfig


class MySQLCacheStore:
    def __init__(self, config: MySQLConfig):
        self.config = config
        logger.warning(
            "Deprecated MySQL cache backend requested. Runtime cache is Redis-only, and MySQL is unreachable in the default path."
        )

    def is_available(self) -> bool:
        return False

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        return None

    def put(self, key: str, value: Dict[str, Any]) -> bool:
        return False
