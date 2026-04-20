#!/usr/bin/env python3
"""
Deprecated cache writer for LLMRouterBench.

Runtime caching is Redis-first and Redis-only. Successful requests are written to
Redis immediately by the generator cache decorator, so interrupted runs can be
resumed without a separate backfill pass.

This legacy tool is kept only to avoid broken entrypoints, but it no longer
attempts MySQL and intentionally exits with a clear message.
"""

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Deprecated legacy cache writer. Runtime cache is now Redis-only."
    )
    parser.add_argument("config_path", help="Path to the cache writer configuration file")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--models", type=str)
    parser.add_argument("--exclude-models", type=str)
    parser.parse_args()

    print(
        "cache_writer is deprecated: runtime cache is Redis-only and successful requests are written immediately during normal runs. "
        "Use collector/connectivity entrypoints with Redis configured in .env instead.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
