#!/usr/bin/env python3
"""
stock_eval.py
=============
1. Reads the prompt from InvestSkill/prompts/stock-valuation.md
   (the repo must be cloned first, or pass --prompt-file to override).
2. Fetches live financial data via yfinance.
3. Calls the OpenAI API and saves the report as Markdown.

Usage
-----
  python scripts/stock_eval.py AAPL
  python scripts/stock_eval.py TSLA --model gpt-4o-mini --max-tokens 8000
  python scripts/stock_eval.py AAPL --prompt-file /path/to/stock-valuation.md

Environment
-----------
  OPENAI_API_KEY  (required)
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
    from openai import OpenAI
except ImportError:
    print("ERROR: openai not installed. Run: pip install openai", file=sys.stderr)
    sys.exit(1)

# Default location where the workflow clones InvestSkill
DEFAULT_PROMPT_FILE = Path("InvestSkill/prompts/stock-valuation.md")


# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

def fetch_stock_data(ticker: str) -> str:
    """Return a text summary of key financial data for the ticker."""
    t = yf.Ticker(ticker)
    info = t.info or {}

    def get(key: str, default: str = "N/A") -> str:
        v = info.get(key)
        return str(v) if v is not None else default

    def fmt_large(key: str) -> str:
        v = info.get(key)
        return f"${v:,}" if v else "N/A"

    lines: list[str] = [
        f"## Live Financial Data for {ticker.upper()}\n",
        f"**Company:** {get('longName')}",
        f"**Sector / Industry:** {get('sector')} / {get('industry')}",
        f"**Market Cap:** {fmt_large('marketCap')}",
        f"**Current Price:** ${get('currentPrice')}",
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
        f"- Revenue (TTM): {fmt_large('totalRevenue')}",
        f"- Gross Margin: {get('grossMargins')}",
        f"- Operating Margin: {get('operatingMargins')}",
        f"- Net Margin: {get('profitMargins')}",
        f"- ROE: {get('returnOnEquity')}",
        f"- ROA: {get('returnOnAssets')}",
        "",
        "### Cash Flow",
        f"- Operating Cash Flow: {fmt_large('operatingCashflow')}",
        f"- Free Cash Flow: {fmt_large('freeCashflow')}",
        "",
        "### Balance Sheet",
        f"- Total Cash: {fmt_large('totalCash')}",
        f"- Total Debt: {fmt_large('totalDebt')}",
        f"- Debt/Equity: {get('debtToEquity')}",
        f"- Current Ratio: {get('currentRatio')}",
        f"- Quick Ratio: {get('quickRatio')}",
        "",
        "### Growth & EPS",
        f"- Revenue Growth (YoY): {get('revenueGrowth')}",
        f"- Earnings Growth (YoY): {get('earningsGrowth')}",
        f"- EPS (TTM): {get('trailingEps')}",
        f"- EPS (FWD): {get('forwardEps')}",
        "",
        "### Analyst Estimates",
        f"- Target Price (mean): {get('targetMeanPrice')}",
        f"- Target Price (low / high): {get('targetLowPrice')} / {get('targetHighPrice')}",
        f"- Recommendation: {get('recommendationKey')}",
        f"- # Analyst Opinions: {get('numberOfAnalystOpinions')}",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def load_prompt(prompt_file: Path) -> str:
    """Read the InvestSkill prompt file."""
    if not prompt_file.exists():
        print(
            f"ERROR: Prompt file not found: {prompt_file}\n"
            "Make sure InvestSkill is cloned (the workflow does this automatically).",
            file=sys.stderr,
        )
        sys.exit(1)
    content = prompt_file.read_text(encoding="utf-8").strip()
    print(f"✅ Loaded prompt from: {prompt_file} ({len(content)} chars)")
    return content


def generate_report(ticker: str, prompt: str, model: str, max_tokens: int) -> str:
    """Call OpenAI and return the analysis text."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    stock_data = fetch_stock_data(ticker)

    # Mirror the "Universal Access" pattern from InvestSkill README:
    # paste the prompt, then add the stock question/data below it.
    user_message = (
        prompt
        + "\n\n---\n\n"
        + f"Please perform the above stock valuation analysis for **{ticker.upper()}**.\n\n"
        + stock_data
    )

    print(f"Calling OpenAI ({model}) for {ticker.upper()} stock valuation...")
    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional equity research analyst. "
                    "Produce detailed, structured investment reports in Markdown. "
                    "Be data-driven, objective, and thorough."
                ),
            },
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def save_report(ticker: str, content: str, output_dir: Path) -> Path:
    """Save report with YAML frontmatter and same-day deduplication."""
    output_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    base = f"stock_eval_{today}"

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
        "provider: openai\n"
        f"generated_by: OpenAI API (scripts/stock_eval.py)\n"
        "---\n\n"
    )
    path.write_text(frontmatter + content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate stock valuation report via InvestSkill + OpenAI")
    p.add_argument("ticker", help="Stock ticker symbol (e.g. AAPL)")
    p.add_argument("--model", default="gpt-4o", help="OpenAI model ID (default: gpt-4o)")
    p.add_argument("--max-tokens", type=int, default=16000, help="Max output tokens (default: 16000)")
    p.add_argument(
        "--output-dir",
        default=None,
        help="Output directory (default: output/stock_eval/<ticker>)",
    )
    p.add_argument(
        "--prompt-file",
        default=None,
        help=f"Path to InvestSkill prompt file (default: {DEFAULT_PROMPT_FILE})",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    ticker = args.ticker.upper()
    output_dir = (
        Path(args.output_dir) if args.output_dir else Path("output/stock_eval") / ticker.lower()
    )
    prompt_file = Path(args.prompt_file) if args.prompt_file else DEFAULT_PROMPT_FILE

    prompt = load_prompt(prompt_file)
    report = generate_report(ticker, prompt, args.model, args.max_tokens)
    path = save_report(ticker, report, output_dir)
    print(f"Report saved to: {path}")


if __name__ == "__main__":
    main()
