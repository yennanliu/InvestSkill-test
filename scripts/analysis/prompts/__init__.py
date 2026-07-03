"""
Prompt layer.

Unlike a vendored-template approach, this project's prompts live in the
*cloned InvestSkill repo* (``git clone yennanliu/InvestSkill``) — mirroring the
Gemini CLI flow where ``GEMINI.md`` is auto-loaded and analysis frameworks are
referenced as ``@prompts/<skill>.md``.

``PromptRepo`` wraps that cloned directory and exposes:
  * ``system_context(provider)`` — the provider's system markdown (GEMINI.md / CLAUDE.md)
  * ``framework(analysis_type)`` — the ``prompts/<slug>.md`` analysis framework
  * ``available(analysis_type)`` — whether that framework file exists

All reads are cached so a full-report run touches each file once.
"""

from __future__ import annotations

from pathlib import Path

from ..config import context_file
from ..exceptions import PromptError


class PromptRepo:
    """Loads system context + analysis frameworks from a cloned InvestSkill repo."""

    def __init__(self, invest_skill_dir: str | Path):
        self.root = Path(invest_skill_dir)
        self._cache: dict[str, str] = {}

    # ── system context (GEMINI.md / CLAUDE.md) ──────────────────────────────
    def system_context(self, provider: str) -> str:
        filename = context_file(provider)
        path = self.root / filename
        if not path.exists():
            # Fall back to GEMINI.md, the generic system context.
            fallback = self.root / "GEMINI.md"
            if not fallback.exists():
                raise PromptError(
                    f"System context not found: neither {path} nor {fallback} exist. "
                    "Is InvestSkill cloned?"
                )
            path = fallback
        return self._read(path)

    # ── analysis framework (prompts/<slug>.md) ──────────────────────────────
    def framework(self, analysis_type: str) -> str:
        path = self._framework_path(analysis_type)
        if not path.exists():
            raise PromptError(f"Prompt framework not found: {path}")
        return self._read(path)

    def available(self, analysis_type: str) -> bool:
        return self._framework_path(analysis_type).exists()

    def _framework_path(self, analysis_type: str) -> Path:
        return self.root / "prompts" / f"{analysis_type}.md"

    def _read(self, path: Path) -> str:
        key = str(path)
        if key not in self._cache:
            self._cache[key] = path.read_text(encoding="utf-8").strip()
        return self._cache[key]


__all__ = ["PromptRepo"]
