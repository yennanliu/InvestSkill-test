#!/usr/bin/env python3
"""
full_report_gemini.py
=====================
Runs the FULL InvestSkill analysis suite for a single ticker in one go — mirrors
the public full-demo (https://yennj12.js.org/InvestSkill/full-demo-rklb.html),
which executes all 15 analysis modules and synthesises a consolidated verdict.

Flow (mirrors the InvestSkill Gemini CLI):
  1. Loads GEMINI.md as the system context   (mirrors: gemini auto-loads GEMINI.md)
  2. Fetches a rich yfinance snapshot ONCE    (shared across every module)
  3. For each skill, loads prompts/<skill>.md  (mirrors: @prompts/<skill>.md)
     and calls the Gemini API to produce that module's section
  4. Runs a final synthesis pass over all module signals
  5. Saves ONE combined Markdown report

Usage
-----
  python scripts/full_report_gemini.py AAPL
  python scripts/full_report_gemini.py TSLA --model gemini-2.5-pro
  python scripts/full_report_gemini.py NVDA --skills technical-analysis,dcf-valuation

Environment
-----------
  GEMINI_API_KEY  (required)
"""

from __future__ import annotations

import argparse
import os
import sys
import time
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
SYSTEM_CONTEXT_FILE = "GEMINI.md"
DEFAULT_MODEL = "gemini-2.5-flash"

# The 15 modules run by the public full-demo, in analytical order.
# Each entry is (skill-slug, human title). The slug maps to prompts/<slug>.md.
FULL_DEMO_SKILLS: list[tuple[str, str]] = [
    ("technical-analysis",     "Technical Analysis"),
    ("fundamental-analysis",   "Fundamental Analysis"),
    ("stock-eval",             "Stock Evaluation"),
    ("economics-analysis",     "Macroeconomic Analysis"),
    ("sector-analysis",        "Industry / Sector Analysis"),
    ("insider-trading",        "Insider Trading Analysis"),
    ("institutional-ownership","Institutional Holdings"),
    ("short-interest",         "Short Interest Analysis"),
    ("earnings-call-analysis", "Earnings Call Analysis"),
    ("chart-master",           "Chart Visualization"),
    ("dcf-valuation",          "DCF Valuation"),
    ("stock-valuation",        "Equity Valuation"),
    ("options-analysis",       "Options Analysis"),
    ("dividend-analysis",      "Dividends & Capital Returns"),
    ("competitor-analysis",    "Competitive Analysis"),
]


# ---------------------------------------------------------------------------
# InvestSkill setup
# ---------------------------------------------------------------------------

def load_system_context(invest_skill_dir: Path) -> str:
    gemini_md = invest_skill_dir / SYSTEM_CONTEXT_FILE
    if not gemini_md.exists():
        print(f"ERROR: {gemini_md} not found. Is InvestSkill cloned?", file=sys.stderr)
        sys.exit(1)
    system_context = gemini_md.read_text(encoding="utf-8").strip()
    print(f"✅ Loaded system context: {gemini_md} ({len(system_context)} chars)")
    return system_context


def load_prompt(invest_skill_dir: Path, slug: str) -> str | None:
    prompt_md = invest_skill_dir / "prompts" / f"{slug}.md"
    if not prompt_md.exists():
        print(f"⚠️  Skipping '{slug}': {prompt_md} not found.", file=sys.stderr)
        return None
    return prompt_md.read_text(encoding="utf-8").strip()


# ---------------------------------------------------------------------------
# Data fetching — one comprehensive snapshot shared by every module
# ---------------------------------------------------------------------------

def _fmt(v: object, prefix: str = "") -> str:
    if v is None:
        return "N/A"
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, int):
        return f"{prefix}{v:,}"
    if isinstance(v, float):
        return f"{prefix}{v:,.2f}"
    return str(v)


def _hist_table(df: object, heading: str, rows: list[str]) -> list[str]:
    """Render up to 4 fiscal years of the given rows as a Markdown table."""
    if df is None or df.empty:
        return []
    cols = df.columns[:4]
    out = [
        heading,
        "| Metric |" + "".join(f" {c.year} |" for c in cols),
        "|---|" + "---|" * len(cols),
    ]
    for row in rows:
        if row in df.index:
            vals = "".join(f" {_fmt(df.loc[row, c], '$')} |" for c in cols)
            out.append(f"| {row} |{vals}")
    out.append("")
    return out


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

    lines: list[str] = [f"## Live Financial Data for {ticker.upper()}\n"]
    lines += [
        f"**Company:** {get('longName')}",
        f"**Sector / Industry:** {get('sector')} / {get('industry')}",
        f"**Market Cap:** {_fmt(info.get('marketCap'), '$')}",
        f"**Current Price:** {_fmt(info.get('currentPrice'), '$')}",
        f"**Shares Outstanding:** {_fmt(info.get('sharesOutstanding'))}",
        f"**52W Range:** {get('fiftyTwoWeekLow')} – {get('fiftyTwoWeekHigh')}",
        f"**Beta (5Y monthly):** {get('beta')}",
        f"**Employees:** {get('fullTimeEmployees')}",
        "",
        "### Income Statement (TTM)",
        f"- Revenue: {_fmt(revenue, '$')}",
        f"- Gross Profit: {_fmt(info.get('grossProfits'), '$')}",
        f"- EBITDA: {_fmt(info.get('ebitda'), '$')}",
        f"- Net Income: {_fmt(info.get('netIncomeToCommon'), '$')}",
        f"- Gross Margin: {get('grossMargins')}",
        f"- Operating Margin: {get('operatingMargins')}",
        f"- Net Margin: {get('profitMargins')}",
        f"- EPS (TTM / FWD): {get('trailingEps')} / {get('forwardEps')}",
        f"- Revenue Growth (YoY): {get('revenueGrowth')}",
        f"- Earnings Growth (YoY): {get('earningsGrowth')}",
        "",
        "### Balance Sheet",
        f"- Total Cash: {_fmt(total_cash, '$')}",
        f"- Total Debt: {_fmt(total_debt, '$')}",
        f"- Net Debt: {_fmt(net_debt, '$')} {'(net cash)' if net_debt < 0 else ''}",
        f"- Debt/Equity: {get('debtToEquity')}",
        f"- Current / Quick Ratio: {get('currentRatio')} / {get('quickRatio')}",
        f"- Book Value/Share: {get('bookValue')}",
        f"- Price/Book: {get('priceToBook')}",
        "",
        "### Cash Flow (TTM)  — DCF inputs",
        f"- Operating Cash Flow: {_fmt(ocf, '$')}",
        f"- Capital Expenditures: {_fmt(capex, '$')}",
        f"- Free Cash Flow: {_fmt(fcf, '$')}",
        f"- FCF Margin: {fcf_margin}",
        "",
        "### Valuation & Returns",
        f"- P/E (TTM / FWD): {get('trailingPE')} / {get('forwardPE')}",
        f"- P/S: {get('priceToSalesTrailing12Months')}",
        f"- PEG Ratio: {get('pegRatio')}",
        f"- Enterprise Value: {_fmt(info.get('enterpriseValue'), '$')}",
        f"- EV/EBITDA: {get('enterpriseToEbitda')}",
        f"- EV/Revenue: {get('enterpriseToRevenue')}",
        f"- ROE / ROA: {get('returnOnEquity')} / {get('returnOnAssets')}",
        f"- Effective Tax Rate: {get('effectiveTaxRate')}",
        "",
        "### Dividends & Capital Returns",
        f"- Dividend Rate / Yield: {get('dividendRate')} / {get('dividendYield')}",
        f"- Payout Ratio: {get('payoutRatio')}",
        f"- 5Y Avg Dividend Yield: {get('fiveYearAvgDividendYield')}",
        "",
        "### Short Interest & Ownership",
        f"- Shares Short: {_fmt(info.get('sharesShort'))}",
        f"- Short % of Float: {get('shortPercentOfFloat')}",
        f"- Short Ratio (days to cover): {get('shortRatio')}",
        f"- Float Shares: {_fmt(info.get('floatShares'))}",
        f"- % Held by Insiders: {get('heldPercentInsiders')}",
        f"- % Held by Institutions: {get('heldPercentInstitutions')}",
        "",
        "### Analyst Estimates",
        f"- Target Price (mean): {get('targetMeanPrice')}",
        f"- Target (low / high): {get('targetLowPrice')} / {get('targetHighPrice')}",
        f"- Recommendation: {get('recommendationKey')}",
        f"- # Analyst Opinions: {get('numberOfAnalystOpinions')}",
        "",
    ]

    # Recent price history — feeds technical analysis & charts
    try:
        hist = t.history(period="6mo")
        if hist is not None and not hist.empty:
            closes = hist["Close"].dropna()
            ma20 = closes.rolling(20).mean().iloc[-1] if len(closes) >= 20 else None
            ma50 = closes.rolling(50).mean().iloc[-1] if len(closes) >= 50 else None
            last = closes.iloc[-1]
            hi = closes.max()
            lo = closes.min()
            lines += [
                "### Price Action (last 6 months)",
                f"- Latest Close: {_fmt(float(last), '$')}",
                f"- 20-day MA: {_fmt(float(ma20), '$') if ma20 is not None else 'N/A'}",
                f"- 50-day MA: {_fmt(float(ma50), '$') if ma50 is not None else 'N/A'}",
                f"- 6M High / Low: {_fmt(float(hi), '$')} / {_fmt(float(lo), '$')}",
                "",
                "Recent closes (last 10 trading days):",
                "| Date | Close | Volume |",
                "|---|---|---|",
            ]
            for idx, row in hist.tail(10).iterrows():
                d = idx.date().isoformat() if hasattr(idx, "date") else str(idx)
                lines.append(f"| {d} | {_fmt(float(row['Close']), '$')} | {_fmt(int(row['Volume']))} |")
            lines.append("")
    except Exception:
        pass

    # Historical income statement — growth assumptions
    try:
        lines += _hist_table(
            t.financials,
            "### Historical Income Statement (last 4 fiscal years)",
            ["Total Revenue", "Gross Profit", "Operating Income", "Net Income", "EBITDA"],
        )
    except Exception:
        pass

    # Historical cash flow — FCF trend for DCF & capital returns
    try:
        lines += _hist_table(
            t.cashflow,
            "### Historical Cash Flow (last 4 fiscal years)",
            ["Operating Cash Flow", "Capital Expenditure", "Free Cash Flow",
             "Issuance Of Stock", "Repurchase Of Stock", "Cash Dividends Paid"],
        )
    except Exception:
        pass

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Gemini calls
# ---------------------------------------------------------------------------

def _system_instruction(system_context: str) -> str:
    return (
        system_context
        + "\n\n---\n\n"
        + "Write all analysis reports in Traditional Chinese (繁體中文)."
    )


def run_module(
    model: "genai.GenerativeModel",
    analysis_prompt: str,
    ticker: str,
    stock_data: str,
) -> str:
    user_message = (
        analysis_prompt
        + "\n\n---\n\n"
        + f"Apply the framework above to **{ticker.upper()}** and write this module's "
        + "section of a full research report in Traditional Chinese (繁體中文). "
        + "Use the shared data below; do not repeat the raw data table — analyse it. "
        + "End with an InvestSkill 'investment signal box' containing: "
        + "評分 (1–10), 訊號方向 (看多/中性/看空), 信心水準, and 建議動作 (買進/持有/避開).\n\n"
        + stock_data
    )
    response = model.generate_content(user_message)
    return response.text


def run_synthesis(
    model: "genai.GenerativeModel",
    ticker: str,
    module_signals: str,
    module_count: int,
) -> str:
    prompt = (
        f"You have completed a full {module_count}-module InvestSkill analysis of **{ticker.upper()}**. "
        "Below are each module's signal boxes. Synthesise them into a consolidated conclusion "
        "in Traditional Chinese (繁體中文):\n"
        "1. 綜合評分 (weighted 1–10) 與整體訊號 (看多/中性/看空)\n"
        "2. 信心水準 與理由\n"
        "3. 各模組共識與分歧點\n"
        "4. 最終投資建議 (買進/持有/避開) 與關鍵風險\n\n"
        + module_signals
    )
    response = model.generate_content(prompt)
    return response.text


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def save_report(ticker: str, sections: list[tuple[str, str]], synthesis: str,
                output_dir: Path, model_name: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    safe_model = model_name.replace("/", "-")
    base = f"full_report_{today}_{safe_model}"

    path = output_dir / f"{base}.md"
    counter = 2
    while path.exists():
        path = output_dir / f"{base}-{counter}.md"
        counter += 1

    frontmatter = (
        "---\n"
        f'title: "{ticker.upper()} Full InvestSkill Report {today}"\n'
        f"date: {today}\n"
        f"ticker: {ticker.upper()}\n"
        "analysis_type: full-report\n"
        f"modules: {len(sections)}\n"
        "skill_source: https://github.com/yennanliu/InvestSkill\n"
        "demo_reference: https://yennj12.js.org/InvestSkill/full-demo-rklb.html\n"
        "system_context: GEMINI.md\n"
        "provider: gemini\n"
        f"model: {model_name}\n"
        "language: zh-TW\n"
        "generated_by: Gemini API (scripts/full_report_gemini.py)\n"
        "---\n\n"
    )

    body: list[str] = [
        f"# {ticker.upper()} 全模組投資分析報告 ({today})",
        "",
        f"> 由 InvestSkill 全套 {len(sections)} 個分析模組生成，模型：`{model_name}`。",
        "",
        "## 🎯 綜合結論 (Consolidated Verdict)",
        "",
        synthesis,
        "",
        "---",
        "",
        "## 📑 各模組分析 (Module Sections)",
        "",
    ]
    for i, (title, content) in enumerate(sections, 1):
        body += [f"### {i}. {title}", "", content, "", "---", ""]

    path.write_text(frontmatter + "\n".join(body), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Run the full InvestSkill analysis suite via Gemini API")
    p.add_argument("ticker", help="Stock ticker symbol (e.g. AAPL)")
    p.add_argument("--model", default=DEFAULT_MODEL,
                   help=f"Gemini model ID (default: {DEFAULT_MODEL})")
    p.add_argument("--max-tokens", type=int, default=20000,
                   help="Max output tokens per module (default: 20000)")
    p.add_argument("--output-dir", default=None)
    p.add_argument("--invest-skill-dir", default=str(DEFAULT_INVEST_SKILL_DIR),
                   help=f"Path to cloned InvestSkill repo (default: {DEFAULT_INVEST_SKILL_DIR})")
    p.add_argument("--skills", default=None,
                   help="Comma-separated skill slugs to run (default: all 15 full-demo modules)")
    p.add_argument("--sleep", type=float, default=1.0,
                   help="Seconds to sleep between module calls to ease rate limits (default: 1.0)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    ticker = args.ticker.upper()
    output_dir = Path(args.output_dir) if args.output_dir else Path("output/full_report") / ticker.lower()
    invest_skill_dir = Path(args.invest_skill_dir)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("ERROR: GEMINI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    genai.configure(api_key=api_key)

    # Resolve which skills to run.
    if args.skills:
        wanted = [s.strip() for s in args.skills.split(",") if s.strip()]
        title_map = dict(FULL_DEMO_SKILLS)
        skills = [(s, title_map.get(s, s.replace("-", " ").title())) for s in wanted]
    else:
        skills = FULL_DEMO_SKILLS

    system_context = load_system_context(invest_skill_dir)
    print(f"Fetching yfinance snapshot for {ticker}...")
    stock_data = fetch_stock_data(ticker)

    model = genai.GenerativeModel(
        model_name=args.model,
        system_instruction=_system_instruction(system_context),
        generation_config=genai.GenerationConfig(max_output_tokens=args.max_tokens),
    )

    sections: list[tuple[str, str]] = []
    print(f"\nRunning {len(skills)} InvestSkill modules for {ticker} on {args.model}...\n")
    for i, (slug, title) in enumerate(skills, 1):
        prompt = load_prompt(invest_skill_dir, slug)
        if prompt is None:
            continue
        print(f"  [{i}/{len(skills)}] {title} ({slug})...")
        try:
            content = run_module(model, prompt, ticker, stock_data)
            sections.append((title, content))
        except Exception as exc:  # keep the run alive if one module fails
            print(f"      ⚠️  {slug} failed: {exc}", file=sys.stderr)
            sections.append((title, f"_模組生成失敗：{exc}_"))
        if args.sleep and i < len(skills):
            time.sleep(args.sleep)

    if not sections:
        print("ERROR: no modules produced output.", file=sys.stderr)
        sys.exit(1)

    # Consolidated verdict over every module's signal box.
    print("\nSynthesising consolidated verdict...")
    module_signals = "\n\n".join(f"## {title}\n{content}" for title, content in sections)
    try:
        synthesis = run_synthesis(model, ticker, module_signals, len(sections))
    except Exception as exc:
        print(f"⚠️  synthesis failed: {exc}", file=sys.stderr)
        synthesis = f"_綜合結論生成失敗：{exc}_"

    path = save_report(ticker, sections, synthesis, output_dir, args.model)
    print(f"\n✅ Full report ({len(sections)} modules) saved to: {path}")


if __name__ == "__main__":
    main()
