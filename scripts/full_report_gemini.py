#!/usr/bin/env python3
"""
full_report_gemini.py — thin wrapper.

Runs the FULL InvestSkill analysis suite (all 15 full-demo modules) for one
ticker and synthesises a consolidated verdict — mirrors the public full-demo
(https://yennj12.js.org/InvestSkill/full-demo-rklb.html). All logic lives in the
layered ``analysis`` package (config · prompts · data · llm · pipeline ·
publish). Defaults to the Gemini provider but accepts ``--provider openai|claude``.

Usage:
  python scripts/full_report_gemini.py AAPL
  python scripts/full_report_gemini.py TSLA --model gemini-2.5-pro
  python scripts/full_report_gemini.py NVDA --skills technical-analysis,dcf-valuation

Environment: GEMINI_API_KEY (or OPENAI_API_KEY / ANTHROPIC_API_KEY per --provider)
"""

from analysis.cli import run_full

if __name__ == "__main__":
    run_full()
