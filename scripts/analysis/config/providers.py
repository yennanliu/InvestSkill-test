"""Per-provider configuration: default model + output-token budget.

Editing a default here changes it for every script and workflow that does not
pass an explicit ``--model`` / ``--max-tokens``.
"""

from __future__ import annotations

# Which cloned-InvestSkill markdown file acts as the system context per provider.
# Falls back to GEMINI.md when the provider-specific file is absent.
PROVIDER_CONTEXT_FILE = {
    "gemini": "GEMINI.md",
    "claude": "CLAUDE.md",
    "openai": "GEMINI.md",
}

PROVIDER_DEFAULTS = {
    "gemini": {
        "default_model": "gemini-2.5-flash",
        "default_tokens": 20000,
    },
    "openai": {
        "default_model": "gpt-4o",
        "default_tokens": 16000,
    },
    "claude": {
        "default_model": "claude-sonnet-4-6",
        "default_tokens": 8000,
    },
}

SUPPORTED_PROVIDERS = tuple(PROVIDER_DEFAULTS)


def provider_default(provider: str, key: str):
    """Return a provider default (``default_model`` / ``default_tokens``)."""
    try:
        return PROVIDER_DEFAULTS[provider][key]
    except KeyError as exc:
        raise KeyError(
            f"Unknown provider {provider!r} or key {key!r}. "
            f"Supported providers: {', '.join(SUPPORTED_PROVIDERS)}"
        ) from exc


def context_file(provider: str) -> str:
    """Return the system-context markdown filename for a provider."""
    return PROVIDER_CONTEXT_FILE.get(provider, "GEMINI.md")
