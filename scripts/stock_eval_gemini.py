#!/usr/bin/env python3
"""
stock_eval_gemini.py
====================
Replicates the InvestSkill Gemini CLI flow in a CI/CD-friendly script:
  1. Clones InvestSkill (done by the workflow before this script runs)
  2. Loads GEMINI.md as the system context  (mirrors: gemini auto-loads GEMINI.md)
  3. Loads prompts/stock-valuation.md       (mirrors: @prompts/stock-valuation.md)
  4. Fetches live yfinance data
  5. Calls the Gemini API and saves a Markdown report in Traditional Chinese

Usage
-----
  python scripts/stock_eval_gemini.py AAPL
  python scripts/stock_eval_gemini.py TSLA --model gemini-2.0-flash --max-tokens 8192
  python scripts/stock_eval_gemini.py AAPL --invest-skill-dir /path/to/InvestSkill

Environment
-----------
  GEMINI_API_KEY  (required)
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date
from pathlib import Path

try:
    import yfinance as yf
except ImportError:
    print("ERROR: yfinance not installed. Run: pip install yfinance", file=sys.stderr)
    sys.exit(1)

try:
    import google.generativeai as genai
except ImportError:
    print("ERROR: google-generativeai not installed. Run: pip install google-generativeai", file=sys.stderr)
    sys.exit(1)

DEFAULT_INVEST_SKILL_DIR = Path("InvestSkill")
PROMPT_FILE = "prompts/stock-valuation.md"
SYSTEM_CONTEXT_FILE = "GEMINI.md"


# ---------------------------------------------------------------------------
# InvestSkill setup — mirrors Gemini CLI auto-loading GEMINI.md
# ---------------------------------------------------------------------------

def load_invest_skill(invest_skill_dir: Path) -> tuple[str, str]:
    """
    Returns (system_context, analysis_prompt).
    - system_context = contents of GEMINI.md  (auto-loaded by gemini CLI)
    - analysis_prompt = contents of prompts/stock-valuation.md  (@prompts/... reference)
    """
    gemini_md = invest_skill_dir / SYSTEM_CONTEXT_FILE
    prompt_md = invest_skill_dir / PROMPT_FILE

    if not gemini_md.exists():
        print(f"ERROR: {gemini_md} not found. Is InvestSkill cloned?", file=sys.stderr)
        sys.exit(1)
    if not prompt_md.exists():
        print(f"ERROR: {prompt_md} not found.", file=sys.stderr)
        sys.exit(1)

    system_context = gemini_md.read_text(encoding="utf-8").strip()
    analysis_prompt = prompt_md.read_text(encoding="utf-8").strip()

    print(f"✅ Loaded system context: {gemini_md} ({len(system_context)} chars)")
    print(f"✅ Loaded analysis prompt: {prompt_md} ({len(analysis_prompt)} chars)")
    return system_context, analysis_prompt


# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

def _fmt(v: object, prefix: str = "") -> str:
    if v is None:
        return "N/A"
    if isinstance(v, (int, float)):
        return f"{prefix}{v:,}" if isinstance(v, int) else f"{prefix}{v:,.2f}"
    return str(v)


def fetch_stock_data(ticker: str) -> str:
    t = yf.Ticker(ticker)
    info = t.info or {}

    def get(key: str) -> str:
        v = info.get(key)
        return str(v) if v is not None else "N/A"

    lines: list[str] = [f"## Live Financial Data for {ticker.upper()}\n"]
    lines += [
        f"**Company:** {get('longName')}",
        f"**Sector / Industry:** {get('sector')} / {get('industry')}",
        f"**Market Cap:** {_fmt(info.get('marketCap'), '$')}",
        f"**Current Price:** {_fmt(info.get('currentPrice'), '$')}",
        f"**52W Range:** {get('fiftyTwoWeekLow')} – {get('fiftyTwoWeekHigh')}",
        "",
        "### Valuation",
        f"- P/E (TTM): {get('trailingPE')}",
        f"- P/E (FWD): {get('forwardPE')}",
        f"- PEG Ratio: {get('pegRatio')}",
        f"- Price/Sales: {get('priceToSalesTrailing12Months')}",
        f"- Price/Book: {get('priceToBook')}",
        f"- EV/EBITDA: {get('enterpriseToEbitda')}",
        f"- EV/Revenue: {get('enterpriseToRevenue')}",
        "",
        "### Profitability",
        f"- Revenue (TTM): {_fmt(info.get('totalRevenue'), '$')}",
        f"- Gross Margin: {get('grossMargins')}",
        f"- Operating Margin: {get('operatingMargins')}",
        f"- Net Margin: {get('profitMargins')}",
        f"- ROE: {get('returnOnEquity')}",
        f"- ROA: {get('returnOnAssets')}",
        "",
        "### Cash Flow & Balance Sheet",
        f"- Operating Cash Flow: {_fmt(info.get('operatingCashflow'), '$')}",
        f"- Free Cash Flow: {_fmt(info.get('freeCashflow'), '$')}",
        f"- Total Cash: {_fmt(info.get('totalCash'), '$')}",
        f"- Total Debt: {_fmt(info.get('totalDebt'), '$')}",
        f"- Debt/Equity: {get('debtToEquity')}",
        f"- Current Ratio: {get('currentRatio')}",
        "",
        "### Growth & Analyst Estimates",
        f"- Revenue Growth (YoY): {get('revenueGrowth')}",
        f"- Earnings Growth (YoY): {get('earningsGrowth')}",
        f"- EPS (TTM): {get('trailingEps')}",
        f"- EPS (FWD): {get('forwardEps')}",
        f"- Target Price (mean): {get('targetMeanPrice')}",
        f"- Target (low / high): {get('targetLowPrice')} / {get('targetHighPrice')}",
        f"- Recommendation: {get('recommendationKey')}",
        "",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Report generation — mirrors: @prompts/stock-valuation.md <ticker>
# ---------------------------------------------------------------------------

def generate_report(
    ticker: str,
    system_context: str,
    analysis_prompt: str,
    model_name: str,
    max_tokens: int,
) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    genai.configure(api_key=api_key)

    stock_data = fetch_stock_data(ticker)

    # System instruction = GEMINI.md context  (what gemini CLI auto-loads)
    system_instruction = (
        system_context
        + "\n\n---\n\n"
        + "Write all analysis reports in Traditional Chinese (繁體中文)."
    )

    # User message = @prompts/stock-valuation.md <ticker> + live data
    user_message = (
        analysis_prompt
        + "\n\n---\n\n"
        + f"Please perform the above stock valuation analysis for **{ticker.upper()}**. "
        + "Write the full report in Traditional Chinese (繁體中文).\n\n"
        + stock_data
    )

    print(f"Calling Gemini ({model_name}) for {ticker.upper()} stock valuation...")
    model = genai.GenerativeModel(
        model_name=model_name,
        system_instruction=system_instruction,
        generation_config=genai.GenerationConfig(max_output_tokens=max_tokens),
    )
    response = model.generate_content(user_message)
    return response.text


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def save_report(ticker: str, content: str, output_dir: Path, model_name: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    # Sanitise model name for filename (e.g. gemini-2.0-flash → gemini-2.0-flash)
    safe_model = model_name.replace("/", "-")
    base = f"stock_eval_{today}_{safe_model}"

    path = output_dir / f"{base}.md"
    counter = 2
    while path.exists():
        path = output_dir / f"{base}-{counter}.md"
        counter += 1

    frontmatter = (
        "---\n"
        f'title: "{ticker.upper()} Stock Valuation {today}"\n'
        f"date: {today}\n"
        f"ticker: {ticker.upper()}\n"
        "analysis_type: stock-valuation\n"
        "skill_source: https://github.com/yennanliu/InvestSkill\n"
        "prompt_file: prompts/stock-valuation.md\n"
        "system_context: GEMINI.md\n"
        "provider: gemini\n"
        f"model: {model_name}\n"
        "language: zh-TW\n"
        f"generated_by: Gemini API (scripts/stock_eval_gemini.py)\n"
        "---\n\n"
    )
    path.write_text(frontmatter + content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Stock valuation via InvestSkill + Gemini API")
    p.add_argument("ticker", help="Stock ticker symbol (e.g. AAPL)")
    p.add_argument("--model", default="gemini-2.0-flash", help="Gemini model ID (default: gemini-2.0-flash)")
    p.add_argument("--max-tokens", type=int, default=8192, help="Max output tokens (default: 8192)")
    p.add_argument("--output-dir", default=None)
    p.add_argument("--invest-skill-dir", default=str(DEFAULT_INVEST_SKILL_DIR),
                   help=f"Path to cloned InvestSkill repo (default: {DEFAULT_INVEST_SKILL_DIR})")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    ticker = args.ticker.upper()
    output_dir = Path(args.output_dir) if args.output_dir else Path("output/stock_eval") / ticker.lower()
    invest_skill_dir = Path(args.invest_skill_dir)

    system_context, analysis_prompt = load_invest_skill(invest_skill_dir)
    report = generate_report(ticker, system_context, analysis_prompt, args.model, args.max_tokens)
    path = save_report(ticker, report, output_dir, args.model)
    print(f"Report saved to: {path}")


if __name__ == "__main__":
    main()
