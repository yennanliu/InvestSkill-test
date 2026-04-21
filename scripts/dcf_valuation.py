#!/usr/bin/env python3
"""
dcf_valuation.py
================
1. Reads the prompt from InvestSkill/prompts/dcf-valuation.md
2. Fetches live + historical financial data via yfinance (FCF, WACC inputs, etc.)
3. Calls the OpenAI API and saves the report as Markdown (Traditional Chinese)

Usage
-----
  python scripts/dcf_valuation.py AAPL
  python scripts/dcf_valuation.py TSLA --model gpt-4o-mini --max-tokens 8000
  python scripts/dcf_valuation.py AAPL --prompt-file /path/to/dcf-valuation.md

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

DEFAULT_PROMPT_FILE = Path("InvestSkill/prompts/dcf-valuation.md")


# ---------------------------------------------------------------------------
# Data fetching — DCF needs richer data than the other analyses
# ---------------------------------------------------------------------------

def _fmt(v: object, prefix: str = "", suffix: str = "") -> str:
    if v is None:
        return "N/A"
    if isinstance(v, float):
        return f"{prefix}{v:,.2f}{suffix}"
    if isinstance(v, int):
        return f"{prefix}{v:,}{suffix}"
    return str(v)


def fetch_stock_data(ticker: str) -> str:
    t = yf.Ticker(ticker)
    info = t.info or {}

    def get(key: str) -> str:
        v = info.get(key)
        return str(v) if v is not None else "N/A"

    lines: list[str] = [f"## Live Financial Data for {ticker.upper()} (DCF Inputs)\n"]

    # --- Company overview ---
    lines += [
        f"**Company:** {get('longName')}",
        f"**Sector / Industry:** {get('sector')} / {get('industry')}",
        f"**Market Cap:** {_fmt(info.get('marketCap'), '$')}",
        f"**Current Price:** {_fmt(info.get('currentPrice'), '$')}",
        f"**Shares Outstanding (diluted):** {_fmt(info.get('sharesOutstanding'))}",
        f"**Float Shares:** {_fmt(info.get('floatShares'))}",
        f"**52W Range:** {get('fiftyTwoWeekLow')} – {get('fiftyTwoWeekHigh')}",
        "",
    ]

    # --- DCF base metrics ---
    total_debt = info.get("totalDebt", 0) or 0
    total_cash = info.get("totalCash", 0) or 0
    net_debt = total_debt - total_cash
    ocf = info.get("operatingCashflow", 0) or 0
    capex = info.get("capitalExpenditures", 0) or 0
    fcf = info.get("freeCashflow") or (ocf + capex)  # capex is usually negative in yfinance
    revenue = info.get("totalRevenue", 0) or 0
    fcf_margin = (fcf / revenue * 100) if revenue else None

    lines += [
        "### DCF Base Metrics (TTM)",
        f"- Revenue (TTM): {_fmt(revenue, '$')}",
        f"- Operating Cash Flow: {_fmt(ocf, '$')}",
        f"- Capital Expenditures: {_fmt(info.get('capitalExpenditures'), '$')}",
        f"- Free Cash Flow (TTM): {_fmt(fcf, '$')}",
        f"- FCF Margin: {_fmt(fcf_margin, suffix='%') if fcf_margin is not None else 'N/A'}",
        f"- Stock-Based Compensation: {_fmt(info.get('sharesBasedCompensation'), '$')}",
        "",
        "### Balance Sheet (for Net Debt)",
        f"- Total Cash & Equivalents: {_fmt(total_cash, '$')}",
        f"- Total Debt: {_fmt(total_debt, '$')}",
        f"- Net Debt (Debt − Cash): {_fmt(net_debt, '$')} {'(net cash position)' if net_debt < 0 else ''}",
        f"- Debt/Equity: {get('debtToEquity')}",
        "",
    ]

    # --- WACC inputs ---
    lines += [
        "### WACC Inputs",
        f"- Beta (5Y monthly): {get('beta')}",
        f"- Interest Expense: {_fmt(info.get('interestExpense'), '$')}",
        f"- Effective Tax Rate: {get('effectiveTaxRate')}",
        f"- Enterprise Value: {_fmt(info.get('enterpriseValue'), '$')}",
        f"- EV/EBITDA: {get('enterpriseToEbitda')}",
        f"- EV/Revenue: {get('enterpriseToRevenue')}",
        "",
    ]

    # --- Growth anchors ---
    lines += [
        "### Growth & Profitability",
        f"- Revenue Growth (YoY): {get('revenueGrowth')}",
        f"- Earnings Growth (YoY): {get('earningsGrowth')}",
        f"- Gross Margin: {get('grossMargins')}",
        f"- Operating Margin: {get('operatingMargins')}",
        f"- Net Margin: {get('profitMargins')}",
        f"- ROE: {get('returnOnEquity')}",
        f"- ROA: {get('returnOnAssets')}",
        "",
    ]

    # --- Analyst estimates (cross-check for growth) ---
    lines += [
        "### Analyst Estimates",
        f"- Target Price (mean): {get('targetMeanPrice')}",
        f"- Target Price (low / high): {get('targetLowPrice')} / {get('targetHighPrice')}",
        f"- Recommendation: {get('recommendationKey')}",
        f"- EPS (FWD): {get('forwardEps')}",
        f"- P/E (FWD): {get('forwardPE')}",
        f"- PEG Ratio: {get('pegRatio')}",
        "",
    ]

    # --- Historical free cash flow (4 years) ---
    try:
        cf = t.cashflow
        if cf is not None and not cf.empty:
            lines.append("### Historical Cash Flow Statement (last 4 fiscal years)")
            rows = [
                "Operating Cash Flow",
                "Capital Expenditure",
                "Free Cash Flow",
                "Issuance Of Stock",
                "Repurchase Of Stock",
            ]
            header = "| Metric |" + "".join(f" {c.year} |" for c in cf.columns[:4])
            sep = "|---|" + "---|" * min(4, len(cf.columns))
            lines += [header, sep]
            for row in rows:
                if row in cf.index:
                    vals = "".join(
                        f" {_fmt(cf.loc[row, c], '$')} |" for c in cf.columns[:4]
                    )
                    lines.append(f"| {row} |{vals}")
            lines.append("")
    except Exception:
        pass

    # --- Historical revenue & earnings ---
    try:
        fin = t.financials
        if fin is not None and not fin.empty:
            lines.append("### Historical Income Statement (last 4 fiscal years)")
            rows = ["Total Revenue", "Gross Profit", "Operating Income", "Net Income", "EBITDA"]
            header = "| Metric |" + "".join(f" {c.year} |" for c in fin.columns[:4])
            sep = "|---|" + "---|" * min(4, len(fin.columns))
            lines += [header, sep]
            for row in rows:
                if row in fin.index:
                    vals = "".join(
                        f" {_fmt(fin.loc[row, c], '$')} |" for c in fin.columns[:4]
                    )
                    lines.append(f"| {row} |{vals}")
            lines.append("")
    except Exception:
        pass

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def load_prompt(prompt_file: Path) -> str:
    if not prompt_file.exists():
        print(f"ERROR: Prompt file not found: {prompt_file}", file=sys.stderr)
        sys.exit(1)
    content = prompt_file.read_text(encoding="utf-8").strip()
    print(f"✅ Loaded prompt from: {prompt_file} ({len(content)} chars)")
    return content


def generate_report(ticker: str, prompt: str, model: str, max_tokens: int) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    stock_data = fetch_stock_data(ticker)

    user_message = (
        prompt
        + "\n\n---\n\n"
        + f"Please build the full DCF model and valuation report for **{ticker.upper()}**. "
        + "Write the full report in Traditional Chinese (繁體中文).\n\n"
        + stock_data
    )

    print(f"Calling OpenAI ({model}) for {ticker.upper()} DCF valuation...")
    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional equity research analyst specialising in DCF modelling. "
                    "Build rigorous, structured DCF valuation reports in Markdown with full "
                    "10-year projections, WACC breakdown, sensitivity tables, and three-scenario "
                    "probability-weighted intrinsic value. "
                    "Write the entire report in Traditional Chinese (繁體中文)."
                ),
            },
            {"role": "user", "content": user_message},
        ],
    )
    return response.choices[0].message.content


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def save_report(ticker: str, content: str, output_dir: Path, model: str = "openai") -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    base = f"dcf_valuation_{today}_{model}"

    path = output_dir / f"{base}.md"
    counter = 2
    while path.exists():
        path = output_dir / f"{base}-{counter}.md"
        counter += 1

    frontmatter = (
        "---\n"
        f'title: "{ticker.upper()} DCF Valuation {today}"\n'
        f"date: {today}\n"
        f"ticker: {ticker.upper()}\n"
        "analysis_type: dcf-valuation\n"
        "skill_source: https://github.com/yennanliu/InvestSkill\n"
        "prompt_file: prompts/dcf-valuation.md\n"
        "provider: openai\n"
        f"model: {model}\n"
        "language: zh-TW\n"
        f"generated_by: OpenAI API (scripts/dcf_valuation.py)\n"
        "---\n\n"
    )
    path.write_text(frontmatter + content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate DCF valuation report via InvestSkill + OpenAI")
    p.add_argument("ticker", help="Stock ticker symbol (e.g. AAPL)")
    p.add_argument("--model", default="gpt-4o", help="OpenAI model ID (default: gpt-4o)")
    p.add_argument("--max-tokens", type=int, default=16000, help="Max output tokens (default: 16000)")
    p.add_argument("--output-dir", default=None, help="Output directory")
    p.add_argument("--prompt-file", default=None, help=f"Path to InvestSkill prompt file (default: {DEFAULT_PROMPT_FILE})")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    ticker = args.ticker.upper()
    output_dir = Path(args.output_dir) if args.output_dir else Path("output/dcf_valuation") / ticker.lower()
    prompt_file = Path(args.prompt_file) if args.prompt_file else DEFAULT_PROMPT_FILE

    prompt = load_prompt(prompt_file)
    report = generate_report(ticker, prompt, args.model, args.max_tokens)
    path = save_report(ticker, report, output_dir, model=args.model)
    print(f"Report saved to: {path}")


if __name__ == "__main__":
    main()
