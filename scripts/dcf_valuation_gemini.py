#!/usr/bin/env python3
"""
dcf_valuation_gemini.py
========================
Replicates the InvestSkill Gemini CLI flow in a CI/CD-friendly script:
  1. Loads GEMINI.md as the system context  (mirrors: gemini auto-loads GEMINI.md)
  2. Loads prompts/dcf-valuation.md         (mirrors: @prompts/dcf-valuation.md)
  3. Fetches live + historical yfinance data (FCF, WACC inputs, revenue history)
  4. Calls the Gemini API and saves a Markdown report in Traditional Chinese

Usage
-----
  python scripts/dcf_valuation_gemini.py AAPL
  python scripts/dcf_valuation_gemini.py TSLA --model gemini-1.5-pro

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
PROMPT_FILE = "prompts/dcf-valuation.md"
SYSTEM_CONTEXT_FILE = "GEMINI.md"


# ---------------------------------------------------------------------------
# InvestSkill setup
# ---------------------------------------------------------------------------

def load_invest_skill(invest_skill_dir: Path) -> tuple[str, str]:
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
# Data fetching — DCF needs richer inputs
# ---------------------------------------------------------------------------

def _fmt(v: object, prefix: str = "") -> str:
    if v is None:
        return "N/A"
    if isinstance(v, int):
        return f"{prefix}{v:,}"
    if isinstance(v, float):
        return f"{prefix}{v:,.2f}"
    return str(v)


def fetch_stock_data(ticker: str) -> str:
    t = yf.Ticker(ticker)
    info = t.info or {}

    def get(key: str) -> str:
        v = info.get(key)
        return str(v) if v is not None else "N/A"

    total_debt = info.get("totalDebt", 0) or 0
    total_cash = info.get("totalCash", 0) or 0
    net_debt = total_debt - total_cash
    ocf = info.get("operatingCashflow", 0) or 0
    capex = info.get("capitalExpenditures", 0) or 0
    fcf = info.get("freeCashflow") or (ocf + capex)
    revenue = info.get("totalRevenue", 0) or 0
    fcf_margin = f"{fcf / revenue * 100:.2f}%" if revenue else "N/A"

    lines: list[str] = [f"## Live Financial Data for {ticker.upper()} (DCF Inputs)\n"]
    lines += [
        f"**Company:** {get('longName')}",
        f"**Sector / Industry:** {get('sector')} / {get('industry')}",
        f"**Market Cap:** {_fmt(info.get('marketCap'), '$')}",
        f"**Current Price:** {_fmt(info.get('currentPrice'), '$')}",
        f"**Shares Outstanding (diluted):** {_fmt(info.get('sharesOutstanding'))}",
        f"**52W Range:** {get('fiftyTwoWeekLow')} – {get('fiftyTwoWeekHigh')}",
        "",
        "### DCF Base Metrics (TTM)",
        f"- Revenue (TTM): {_fmt(revenue, '$')}",
        f"- Operating Cash Flow: {_fmt(ocf, '$')}",
        f"- Capital Expenditures: {_fmt(info.get('capitalExpenditures'), '$')}",
        f"- Free Cash Flow (TTM): {_fmt(fcf, '$')}",
        f"- FCF Margin: {fcf_margin}",
        f"- Stock-Based Compensation: {_fmt(info.get('sharesBasedCompensation'), '$')}",
        "",
        "### Balance Sheet (Net Debt Calculation)",
        f"- Total Cash: {_fmt(total_cash, '$')}",
        f"- Total Debt: {_fmt(total_debt, '$')}",
        f"- Net Debt: {_fmt(net_debt, '$')} {'(net cash)' if net_debt < 0 else ''}",
        f"- Debt/Equity: {get('debtToEquity')}",
        f"- Current Ratio: {get('currentRatio')}",
        "",
        "### WACC Inputs",
        f"- Beta (5Y monthly): {get('beta')}",
        f"- Interest Expense: {_fmt(info.get('interestExpense'), '$')}",
        f"- Effective Tax Rate: {get('effectiveTaxRate')}",
        f"- Enterprise Value: {_fmt(info.get('enterpriseValue'), '$')}",
        f"- EV/EBITDA: {get('enterpriseToEbitda')}",
        "",
        "### Growth & Profitability",
        f"- Revenue Growth (YoY): {get('revenueGrowth')}",
        f"- Earnings Growth (YoY): {get('earningsGrowth')}",
        f"- Gross Margin: {get('grossMargins')}",
        f"- Operating Margin: {get('operatingMargins')}",
        f"- Net Margin: {get('profitMargins')}",
        f"- ROE: {get('returnOnEquity')}",
        f"- ROA: {get('returnOnAssets')}",
        "",
        "### Analyst Estimates (Growth Cross-Check)",
        f"- Target Price (mean): {get('targetMeanPrice')}",
        f"- Target (low / high): {get('targetLowPrice')} / {get('targetHighPrice')}",
        f"- EPS (FWD): {get('forwardEps')}",
        f"- P/E (FWD): {get('forwardPE')}",
        f"- PEG Ratio: {get('pegRatio')}",
        "",
    ]

    # Historical cash flow (4 years) — key for FCF trend
    try:
        cf = t.cashflow
        if cf is not None and not cf.empty:
            lines.append("### Historical Cash Flow (last 4 fiscal years)")
            rows = ["Operating Cash Flow", "Capital Expenditure", "Free Cash Flow",
                    "Issuance Of Stock", "Repurchase Of Stock"]
            header = "| Metric |" + "".join(f" {c.year} |" for c in cf.columns[:4])
            sep = "|---|" + "---|" * min(4, len(cf.columns))
            lines += [header, sep]
            for row in rows:
                if row in cf.index:
                    vals = "".join(f" {_fmt(cf.loc[row, c], '$')} |" for c in cf.columns[:4])
                    lines.append(f"| {row} |{vals}")
            lines.append("")
    except Exception:
        pass

    # Historical revenue — key for growth assumptions
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
                    vals = "".join(f" {_fmt(fin.loc[row, c], '$')} |" for c in fin.columns[:4])
                    lines.append(f"| {row} |{vals}")
            lines.append("")
    except Exception:
        pass

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Report generation
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

    system_instruction = (
        system_context
        + "\n\n---\n\n"
        + "Write all analysis reports in Traditional Chinese (繁體中文)."
    )

    user_message = (
        analysis_prompt
        + "\n\n---\n\n"
        + f"Please build the full DCF model and valuation report for **{ticker.upper()}**. "
        + "Write the full report in Traditional Chinese (繁體中文).\n\n"
        + stock_data
    )

    print(f"Calling Gemini ({model_name}) for {ticker.upper()} DCF valuation...")
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
    safe_model = model_name.replace("/", "-")
    base = f"dcf_valuation_{today}_{safe_model}"

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
        "system_context: GEMINI.md\n"
        "provider: gemini\n"
        f"model: {model_name}\n"
        "language: zh-TW\n"
        f"generated_by: Gemini API (scripts/dcf_valuation_gemini.py)\n"
        "---\n\n"
    )
    path.write_text(frontmatter + content, encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="DCF valuation via InvestSkill + Gemini API")
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
    output_dir = Path(args.output_dir) if args.output_dir else Path("output/dcf_valuation") / ticker.lower()
    invest_skill_dir = Path(args.invest_skill_dir)

    system_context, analysis_prompt = load_invest_skill(invest_skill_dir)
    report = generate_report(ticker, system_context, analysis_prompt, args.model, args.max_tokens)
    path = save_report(ticker, report, output_dir, args.model)
    print(f"Report saved to: {path}")


if __name__ == "__main__":
    main()
