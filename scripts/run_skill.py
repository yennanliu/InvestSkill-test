#!/usr/bin/env python3
"""
run_skill.py — run any InvestSkill framework by slug.

The sandbox entrypoint: the slug is the upstream ``prompts/<skill>.md`` filename,
so a skill added upstream can be exercised here before this repo knows about it
(an unknown slug falls back to a derived output prefix/label). The
``skill_sandbox.yml`` workflow wraps this script.

Usage:
  python scripts/run_skill.py bear-case NVDA
  python scripts/run_skill.py earnings-preview AAPL --provider claude
  python scripts/run_skill.py fact-check MSFT --invest-skill-dir ../InvestSkill

Environment: GEMINI_API_KEY (or OPENAI_API_KEY / ANTHROPIC_API_KEY per --provider)
"""

from analysis.cli import run_skill

if __name__ == "__main__":
    run_skill()
