"""Claude provider runner (anthropic SDK)."""

from __future__ import annotations

import os
import time

from ..exceptions import LLMError
from ..utils.logging_utils import setup_logger
from .base import (
    MAX_REFUSAL_RETRIES,
    RATE_LIMIT_BASE_DELAY,
    is_refusal,
    refusal_override_prefix,
)

logger = setup_logger(__name__)


def run_claude(ticker: str, prompt: str, system_message: str | None = None, *,
               model: str, max_tokens: int, temperature: float | None = None,
               max_retries: int = 5, refusal_retry: bool = True) -> str:
    """Call Claude with an arbitrary system/user prompt and return the text."""
    try:
        import anthropic
    except ImportError as exc:
        raise LLMError("anthropic not installed. Run: pip install anthropic") from exc

    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise LLMError("ANTHROPIC_API_KEY environment variable is not set")

    client = anthropic.Anthropic(api_key=api_key)
    logger.info(f"Claude call: model={model}, max_tokens={max_tokens}")

    def _create(content: str, temp: float | None):
        kwargs = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": content}],
        }
        if system_message:
            kwargs["system"] = system_message
        if temp is not None:
            kwargs["temperature"] = temp
        for attempt in range(1, max_retries + 1):
            try:
                return client.messages.create(**kwargs)
            except anthropic.RateLimitError:
                if attempt == max_retries:
                    raise LLMError("Claude rate limit exhausted")
                delay = RATE_LIMIT_BASE_DELAY * (2 ** (attempt - 1))
                logger.warning(f"Rate limit (attempt {attempt}/{max_retries}); retrying in {delay}s…")
                time.sleep(delay)

    response = _create(prompt, temperature)
    text = "\n\n".join(b.text for b in response.content if hasattr(b, "text"))
    logger.info(f"Response: chars={len(text)}")

    if refusal_retry:
        for retry in range(1, MAX_REFUSAL_RETRIES + 1):
            if not is_refusal(text):
                break
            temp = min(0.7 + retry * 0.15, 1.0)
            logger.warning(f"Refusal (attempt {retry}/{MAX_REFUSAL_RETRIES}); retry temp={temp:.2f}…")
            time.sleep(3)
            response = _create(refusal_override_prefix(ticker, retry) + prompt, temp)
            text = "\n\n".join(b.text for b in response.content if hasattr(b, "text"))
        if is_refusal(text):
            logger.warning(f"All {MAX_REFUSAL_RETRIES} retries returned a refusal for {ticker}.")

    return text
