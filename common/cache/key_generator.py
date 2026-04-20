from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

from .config import KeyGeneratorConfig


class CacheKeyGenerator:
    def __init__(self, config: KeyGeneratorConfig):
        self.config = config

    def generate_key(self, **kwargs: Any) -> str:
        payload: Dict[str, Any] = {}
        for name in self.config.cached_parameters:
            if name in kwargs:
                payload[name] = kwargs[name]
        serialized = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
        algorithm = self.config.hash_algorithm.lower()
        if algorithm == "blake2b":
            return hashlib.blake2b(serialized.encode("utf-8"), digest_size=self.config.hash_digest_size).hexdigest()
        if algorithm == "sha256":
            return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        if algorithm == "sha1":
            return hashlib.sha1(serialized.encode("utf-8")).hexdigest()
        if algorithm == "md5":
            return hashlib.md5(serialized.encode("utf-8")).hexdigest()
        raise ValueError(f"Unsupported hash algorithm: {self.config.hash_algorithm}")
