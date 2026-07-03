"""OpenAI provider runner (openai SDK)."""

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

# Per-model output-token caps for chat completions.
OPENAI_MAX_TOKENS = {
    "gpt-4o": 16384,
    "gpt-4o-mini": 16384,
    "gpt-4-turbo": 4096,
    "gpt-4": 8192,
}


def run_openai(ticker: str, prompt: str, system_message: str, *,
               model: str, max_tokens: int, temperature: float = 0.7,
               max_retries: int = 5, refusal_retry: bool = True,
               cap_tokens: bool = True) -> str:
    """Call OpenAI chat completions with an arbitrary system/user prompt."""
    try:
        import openai
    except ImportError as exc:
        raise LLMError("openai not installed. Run: pip install openai") from exc

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise LLMError("OPENAI_API_KEY environment variable is not set")

    effective_max = max_tokens
    if cap_tokens:
        effective_max = min(max_tokens, OPENAI_MAX_TOKENS.get(model, 16384))
        if effective_max != max_tokens:
            logger.info(f"Capping max_tokens {max_tokens} → {effective_max} for {model}")

    client = openai.OpenAI(api_key=api_key)
    logger.info(f"OpenAI call: model={model}, max_tokens={effective_max}")

    def _create(content: str, temp: float):
        for attempt in range(1, max_retries + 1):
            try:
                return client.chat.completions.create(
                    model=model,
                    max_tokens=effective_max,
                    temperature=temp,
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": content},
                    ],
                )
            except openai.RateLimitError:
                if attempt == max_retries:
                    raise LLMError("OpenAI rate limit exhausted")
                delay = RATE_LIMIT_BASE_DELAY * (2 ** (attempt - 1))
                logger.warning(f"Rate limit (attempt {attempt}/{max_retries}); retrying in {delay}s…")
                time.sleep(delay)

    response = _create(prompt, temperature)
    text = response.choices[0].message.content or ""
    logger.info(f"Response: chars={len(text)}")

    if refusal_retry:
        for retry in range(1, MAX_REFUSAL_RETRIES + 1):
            if not is_refusal(text):
                break
            temp = min(0.7 + retry * 0.15, 1.2)
            logger.warning(f"Refusal (attempt {retry}/{MAX_REFUSAL_RETRIES}); retry temp={temp:.2f}…")
            time.sleep(3)
            response = _create(refusal_override_prefix(ticker, retry) + prompt, temp)
            text = response.choices[0].message.content or ""
        if is_refusal(text):
            logger.warning(f"All {MAX_REFUSAL_RETRIES} retries returned a refusal for {ticker}.")

    return text
