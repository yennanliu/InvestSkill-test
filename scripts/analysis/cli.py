"""
Shared CLI for the thin ``scripts/*_gemini.py`` wrappers.

Each wrapper calls ``run_single(analysis_type)`` or ``run_full()``; all argument
parsing, default resolution, generation, and saving live here so the wrappers
stay a couple of lines.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import (
    DEFAULT_DEPTH,
    DEFAULT_INVEST_SKILL_DIR,
    DEFAULT_LANGUAGE,
    DEFAULT_PROVIDER,
    SUPPORTED_DEPTHS,
    SUPPORTED_PROVIDERS,
    analysis_meta,
    provider_default,
)
from .exceptions import AnalysisError
from .pipeline import generate_analysis, generate_full_report
from .publish import save_full_report, save_report


def _base_parser(description: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=description)
    p.add_argument("ticker", help="Stock ticker symbol (e.g. AAPL)")
    p.add_argument("--provider", default=DEFAULT_PROVIDER, choices=SUPPORTED_PROVIDERS,
                   help=f"LLM provider (default: {DEFAULT_PROVIDER})")
    p.add_argument("--model", default=None,
                   help="Model ID (default: the provider's configured default)")
    p.add_argument("--max-tokens", type=int, default=None,
                   help="Max output tokens (default: the provider's configured default)")
    p.add_argument("--output-dir", default=None, help="Output directory for the report")
    p.add_argument("--invest-skill-dir", default=str(DEFAULT_INVEST_SKILL_DIR),
                   help=f"Path to the cloned InvestSkill repo (default: {DEFAULT_INVEST_SKILL_DIR})")
    p.add_argument("--language", default=DEFAULT_LANGUAGE, help="Report language (default: zh-TW)")
    return p


def _resolve(args) -> tuple[str, int]:
    """Fill model/max-tokens from provider defaults when not supplied."""
    model = args.model or provider_default(args.provider, "default_model")
    max_tokens = args.max_tokens or provider_default(args.provider, "default_tokens")
    return model, max_tokens


def _default_output_dir(analysis_type: str, ticker: str) -> Path:
    return Path("output") / analysis_meta(analysis_type)["prefix"] / ticker.lower()


def run_single(analysis_type: str) -> None:
    """Entrypoint for a single-module wrapper script."""
    meta = analysis_meta(analysis_type)
    args = _base_parser(f"{meta['label']} via InvestSkill ({analysis_type})").parse_args()
    ticker = args.ticker.upper()
    model, max_tokens = _resolve(args)
    output_dir = Path(args.output_dir) if args.output_dir else _default_output_dir(analysis_type, ticker)

    try:
        content = generate_analysis(
            ticker, analysis_type,
            provider=args.provider, model=model, max_tokens=max_tokens,
            invest_skill_dir=args.invest_skill_dir, language=args.language,
        )
        path = save_report(analysis_type, ticker, content, output_dir, args.provider, model)
    except AnalysisError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"✅ Report saved to: {path}")


def run_full() -> None:
    """Entrypoint for the full-report wrapper script."""
    parser = _base_parser("Run the full InvestSkill analysis suite (full-report depth tiers)")
    parser.add_argument("--depth", default=DEFAULT_DEPTH, choices=SUPPORTED_DEPTHS,
                        help=f"Module set to run: quick (5) / standard (10) / "
                             f"comprehensive (15) (default: {DEFAULT_DEPTH})")
    parser.add_argument("--skills", default=None,
                        help="Comma-separated skill slugs to run (overrides --depth)")
    parser.add_argument("--sleep", type=float, default=1.0,
                        help="Seconds between module calls to ease rate limits (default: 1.0)")
    args = parser.parse_args()

    ticker = args.ticker.upper()
    model, max_tokens = _resolve(args)
    output_dir = Path(args.output_dir) if args.output_dir else _default_output_dir("full-report", ticker)
    skills = [s.strip() for s in args.skills.split(",") if s.strip()] if args.skills else None

    try:
        result = generate_full_report(
            ticker,
            provider=args.provider, model=model, max_tokens=max_tokens,
            invest_skill_dir=args.invest_skill_dir, skills=skills, depth=args.depth,
            language=args.language, sleep=args.sleep,
        )
        if not result["sections"]:
            print("ERROR: no modules produced output.", file=sys.stderr)
            sys.exit(1)
        path = save_full_report(ticker, result["sections"], result["synthesis"],
                                output_dir, args.provider, model)
    except AnalysisError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
    print(f"✅ Full report ({len(result['sections'])} modules) saved to: {path}")
