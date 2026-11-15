#!/usr/bin/env python3
"""
run_showcase_live.py — thin wrapper.

Runs the current InvestSkill frameworks on one ticker picked at random from the
live-showcase universe (or the one given with ``--ticker``) and publishes the
result under ``docs/showcase/live/``. All logic lives in ``scripts/showcase_live``.

Usage:
  python scripts/run_showcase_live.py
  python scripts/run_showcase_live.py --ticker NVDA --depth quick
  python scripts/run_showcase_live.py --rebuild-index

Environment: GEMINI_API_KEY (or OPENAI_API_KEY / ANTHROPIC_API_KEY per --provider)
"""

from showcase_live.runner import main

if __name__ == "__main__":
    raise SystemExit(main())
