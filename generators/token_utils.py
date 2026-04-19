"""Token counting utilities aligned with llm2.

Uses GPT-2 tokenizer as the default proxy for token count estimation,
and falls back to len(text)//4 when tokenizer loading is unavailable.
"""

from __future__ import annotations

from loguru import logger

_tokenizer = None
_tokenizer_loaded = False


def _get_tokenizer():
    global _tokenizer, _tokenizer_loaded
    if not _tokenizer_loaded:
        try:
            from transformers import AutoTokenizer

            _tokenizer = AutoTokenizer.from_pretrained("gpt2")
            logger.info("GPT-2 tokenizer loaded for token counting fallback")
        except Exception as exc:
            logger.warning(f"Failed to load GPT-2 tokenizer, using char//4 fallback: {exc}")
            _tokenizer = None
        _tokenizer_loaded = True
    return _tokenizer


def count_tokens(text: str) -> int:
    tokenizer = _get_tokenizer()
    if tokenizer is not None:
        return len(tokenizer.encode(text or ""))
    return max(1, len(text or "") // 4)
