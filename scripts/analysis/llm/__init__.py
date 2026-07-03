"""
LLM provider layer.

Each provider module owns one ``run_<provider>`` runner that takes an arbitrary
``(system_message, prompt)`` and handles the provider's plumbing (API-key check,
rate-limit / transient retries, refusal recovery, and — for Gemini — truncation
recovery). ``call_llm`` dispatches by provider name so the gen layer stays
provider-agnostic.
"""

from __future__ import annotations

from ..config import provider_default
from ..exceptions import LLMError
from .claude import run_claude
from .gemini import run_gemini
from .openai import run_openai

_RUNNERS = {
    "gemini": run_gemini,
    "openai": run_openai,
    "claude": run_claude,
}


def call_llm(provider: str, ticker: str, prompt: str, system_message: str, *,
             model: str | None = None, max_tokens: int | None = None,
             temperature: float = 0.7) -> str:
    """Dispatch a completion to the named provider.

    ``model`` / ``max_tokens`` fall back to the provider defaults when omitted.
    """
    runner = _RUNNERS.get(provider)
    if runner is None:
        raise LLMError(
            f"Unknown provider {provider!r}. Supported: {', '.join(_RUNNERS)}"
        )
    model = model or provider_default(provider, "default_model")
    max_tokens = max_tokens or provider_default(provider, "default_tokens")
    return runner(ticker, prompt, system_message,
                  model=model, max_tokens=max_tokens, temperature=temperature)


__all__ = ["call_llm", "run_gemini", "run_openai", "run_claude"]
