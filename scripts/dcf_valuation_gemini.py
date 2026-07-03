#!/usr/bin/env python3
"""
dcf_valuation_gemini.py — thin wrapper.

DCF intrinsic-value report via the layered ``analysis`` package. All logic lives
in scripts/analysis/ (config · prompts · data · llm · pipeline · publish); this
entrypoint just selects the analysis type. Defaults to the Gemini provider but
accepts ``--provider openai|claude``.

Usage:
  python scripts/dcf_valuation_gemini.py AAPL
  python scripts/dcf_valuation_gemini.py TSLA --model gemini-2.5-pro --max-tokens 20000

Environment: GEMINI_API_KEY (or OPENAI_API_KEY / ANTHROPIC_API_KEY per --provider)
"""

from analysis.cli import run_single

if __name__ == "__main__":
    run_single("dcf-valuation")
