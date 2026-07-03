"""Gemini provider runner (google-generativeai SDK).

Owns Gemini's cross-cutting plumbing: API-key check, rate-limit / transient
retries, truncation recovery (finish_reason == MAX_TOKENS), and refusal retries.
"""

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

# Gemini 2.5 Flash supports up to 65,536 output tokens (thinking + visible share
# this budget). Used as the ceiling for the truncation-recovery retry.
GEMINI_TOKEN_CEILING = 65536


def _finish_reason(response) -> str:
    """First candidate's finish_reason as an upper-case name ('' if absent)."""
    try:
        reason = response.candidates[0].finish_reason
    except (AttributeError, IndexError, TypeError):
        return ""
    return getattr(reason, "name", str(reason)).upper() if reason is not None else ""


def _text(response) -> str:
    """Safely extract text (``response.text`` raises when a candidate is empty)."""
    try:
        return response.text or ""
    except Exception:
        try:
            parts = response.candidates[0].content.parts
            return "".join(getattr(p, "text", "") for p in parts)
        except Exception:
            return ""


def run_gemini(ticker: str, prompt: str, system_message: str, *,
               model: str, max_tokens: int, temperature: float = 0.7,
               max_retries: int = 5, refusal_retry: bool = True,
               recover_truncation: bool = True,
               token_ceiling: int = GEMINI_TOKEN_CEILING) -> str:
    """Call Gemini with an arbitrary system/user prompt and return the text."""
    try:
        import google.generativeai as genai
    except ImportError as exc:
        raise LLMError("google-generativeai not installed. Run: pip install google-generativeai") from exc

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise LLMError("GEMINI_API_KEY environment variable is not set")

    genai.configure(api_key=api_key)
    effective_max = min(max_tokens, token_ceiling)
    logger.info(f"Gemini call: model={model}, max_tokens={effective_max}")

    def _generate(contents: str, max_out: int, temp: float):
        gm = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_message,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_out, temperature=temp,
            ),
        )
        for attempt in range(1, max_retries + 1):
            try:
                return gm.generate_content(contents)
            except Exception as e:
                err = str(e)
                rate_limited = "RESOURCE_EXHAUSTED" in err or "quota" in err.lower() or "429" in err
                transient = any(s in err for s in ("UNAVAILABLE", "503", "INTERNAL", "500")) \
                    or "high demand" in err.lower()
                if (rate_limited or transient) and attempt < max_retries:
                    delay = RATE_LIMIT_BASE_DELAY * (2 ** (attempt - 1))
                    why = "Rate limit" if rate_limited else "Transient error"
                    logger.warning(f"{why} (attempt {attempt}/{max_retries}); retrying in {delay}s…")
                    time.sleep(delay)
                else:
                    raise LLMError(f"Gemini generate_content failed: {e}") from e

    response = _generate(prompt, effective_max, temperature)
    text = _text(response)
    logger.info(f"Response: chars={len(text)}, finish={_finish_reason(response)}")

    # Truncation recovery — retry once at the full ceiling.
    if recover_truncation and _finish_reason(response) == "MAX_TOKENS" and effective_max < token_ceiling:
        logger.warning(f"Truncated at {effective_max} tokens; retrying at {token_ceiling}…")
        response = _generate(prompt, token_ceiling, temperature)
        text = _text(response)
        if _finish_reason(response) == "MAX_TOKENS":
            logger.warning(f"Still truncated at {token_ceiling} tokens — report for {ticker} may be incomplete.")

    # Refusal recovery — escalate temperature + forceful prefix.
    if refusal_retry:
        for retry in range(1, MAX_REFUSAL_RETRIES + 1):
            if not is_refusal(text):
                break
            temp = min(0.7 + retry * 0.15, 1.0)
            logger.warning(f"Refusal (attempt {retry}/{MAX_REFUSAL_RETRIES}); retry temp={temp:.2f}…")
            time.sleep(3)
            response = _generate(refusal_override_prefix(ticker, retry) + prompt, effective_max, temp)
            text = _text(response)
        if is_refusal(text):
            logger.warning(f"All {MAX_REFUSAL_RETRIES} retries returned a refusal for {ticker}.")

    return text
