#!/usr/bin/env python3
"""
stock_eval.py
=============
Fetch live financial data via yfinance, load the stock-eval prompt from
InvestSkill, and call the OpenAI API to generate a comprehensive stock
evaluation report saved as Markdown.

Usage
-----
  python scripts/stock_eval.py AAPL
  python scripts/stock_eval.py TSLA --model gpt-4o-mini --max-tokens 8000

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

# ---------------------------------------------------------------------------
# Prompt template (mirrors InvestSkill prompts/stock-eval.md)
# ---------------------------------------------------------------------------
STOCK_EVAL_PROMPT = """# US Stock Evaluation

You are an expert equity analyst. Perform a comprehensive stock evaluation combining fundamental analysis, valuation modeling, quality scoring, and risk assessment.

## Analysis Components

### 1. Company Overview
- Business model, competitive advantages, moat assessment
- Market position, addressable market, industry trends
- Revenue mix by segment and geography
- Competitive dynamics and disruption risk

### 2. Financial Health
- Revenue/earnings growth (3Y and 5Y CAGR)
- Gross, operating, and net margin trends
- Balance sheet: cash, debt, net debt, book value
- Cash flow: OCF, FCF, FCF yield
- Liquidity ratios: current ratio, quick ratio

### 3. Valuation Metrics
| Metric | Current | 1Y Ago | 5Y Avg | Sector Avg |
|--------|---------|--------|--------|------------|
| P/E (TTM) | | | | |
| P/E (FWD) | | | | |
| EV/EBITDA | | | | |
| EV/FCF | | | | |
| Price/Sales | | | | |
| PEG Ratio | | | | |

### 4. Quality Scoring

**Piotroski F-Score (0–9):** Assess 9 binary criteria across profitability, leverage/liquidity, and operating efficiency. Score 8–9 = strong; 0–2 = weak.

**ROIC vs. WACC:**
- ROIC > WACC = value creation
- ROIC < WACC = value destruction
- Spread: ROIC − WACC = ___ bps

### 5. DCF Framework
- TTM FCF and FCF margin
- Base-case 5-year growth rate
- WACC estimate
- Quick intrinsic value range (Bear/Base/Bull)
- Margin of safety vs. current price

### 6. Risk Matrix
| Risk Category | Level (H/M/L) | Key Concern |
|--------------|---------------|-------------|
| Valuation Risk | | |
| Business/Competitive | | |
| Financial/Leverage | | |
| Regulatory/Legal | | |
| Macro/Sector | | |

## Output

**Investment Thesis** (2–3 sentences): Bull case summary.

**Bear Case** (2–3 sentences): Key risks that could invalidate the thesis.

**Key Metrics Dashboard:**
```
Revenue Growth (YoY):  ___%     FCF Yield:     ___%
Gross Margin:          ___%     P/E (FWD):     ___x
Operating Margin:      ___%     EV/EBITDA:     ___x
ROIC:                  ___%     WACC:          ___%
Piotroski F-Score:     ___/9    DCF IV Range:  $___–$___
```

---

## Signal Output

```
╔══════════════════════════════════════════════╗
║              INVESTMENT SIGNAL               ║
╠══════════════════════════════════════════════╣
║ Signal:      BULLISH / NEUTRAL / BEARISH     ║
║ Confidence:  HIGH / MEDIUM / LOW             ║
║ Horizon:     SHORT / MEDIUM / LONG-TERM      ║
╚══════════════════════════════════════════════╝
```

---

Now analyze the following stock using the live data provided below.
"""


# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

def fetch_stock_data(ticker: str) -> str:
    """Return a text summary of key financial data for the ticker."""
    t = yf.Ticker(ticker)

    info = t.info or {}
    lines: list[str] = [f"## Live Data for {ticker.upper()}\n"]

    def get(key: str, default: str = "N/A") -> str:
        v = info.get(key)
        return str(v) if v is not None else default

    lines.append(f"**Company:** {get('longName')}")
    lines.append(f"**Sector / Industry:** {get('sector')} / {get('industry')}")
    lines.append(f"**Market Cap:** ${info.get('marketCap', 0):,}" if info.get('marketCap') else "**Market Cap:** N/A")
    lines.append(f"**Current Price:** ${get('currentPrice')}")
    lines.append(f"**52W Range:** {get('fiftyTwoWeekLow')} – {get('fiftyTwoWeekHigh')}")
    lines.append("")

    lines.append("### Valuation")
    lines.append(f"- P/E (TTM): {get('trailingPE')}")
    lines.append(f"- P/E (FWD): {get('forwardPE')}")
    lines.append(f"- PEG Ratio: {get('pegRatio')}")
    lines.append(f"- Price/Sales: {get('priceToSalesTrailing12Months')}")
    lines.append(f"- Price/Book: {get('priceToBook')}")
    lines.append(f"- EV/EBITDA: {get('enterpriseToEbitda')}")
    lines.append(f"- EV/Revenue: {get('enterpriseToRevenue')}")
    lines.append("")

    lines.append("### Profitability")
    lines.append(f"- Revenue (TTM): ${info.get('totalRevenue', 0):,}" if info.get('totalRevenue') else "- Revenue (TTM): N/A")
    lines.append(f"- Gross Margin: {get('grossMargins')}")
    lines.append(f"- Operating Margin: {get('operatingMargins')}")
    lines.append(f"- Net Margin: {get('profitMargins')}")
    lines.append(f"- ROE: {get('returnOnEquity')}")
    lines.append(f"- ROA: {get('returnOnAssets')}")
    lines.append("")

    lines.append("### Cash Flow")
    lines.append(f"- Operating Cash Flow: ${info.get('operatingCashflow', 0):,}" if info.get('operatingCashflow') else "- Operating Cash Flow: N/A")
    lines.append(f"- Free Cash Flow: ${info.get('freeCashflow', 0):,}" if info.get('freeCashflow') else "- Free Cash Flow: N/A")
    lines.append("")

    lines.append("### Balance Sheet")
    lines.append(f"- Total Cash: ${info.get('totalCash', 0):,}" if info.get('totalCash') else "- Total Cash: N/A")
    lines.append(f"- Total Debt: ${info.get('totalDebt', 0):,}" if info.get('totalDebt') else "- Total Debt: N/A")
    lines.append(f"- Debt/Equity: {get('debtToEquity')}")
    lines.append(f"- Current Ratio: {get('currentRatio')}")
    lines.append(f"- Quick Ratio: {get('quickRatio')}")
    lines.append("")

    lines.append("### Growth")
    lines.append(f"- Revenue Growth (YoY): {get('revenueGrowth')}")
    lines.append(f"- Earnings Growth (YoY): {get('earningsGrowth')}")
    lines.append(f"- EPS (TTM): {get('trailingEps')}")
    lines.append(f"- EPS (FWD): {get('forwardEps')}")
    lines.append("")

    lines.append("### Analyst Estimates")
    lines.append(f"- Target Price (mean): {get('targetMeanPrice')}")
    lines.append(f"- Target Price (low/high): {get('targetLowPrice')} / {get('targetHighPrice')}")
    lines.append(f"- Recommendation: {get('recommendationKey')}")
    lines.append(f"- # Analyst Opinions: {get('numberOfAnalystOpinions')}")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(ticker: str, model: str, max_tokens: int) -> str:
    """Call OpenAI and return the analysis text."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERROR: OPENAI_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    stock_data = fetch_stock_data(ticker)
    user_message = STOCK_EVAL_PROMPT + "\n\n" + stock_data

    print(f"Calling OpenAI ({model}) for {ticker.upper()} stock evaluation...")
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
        f'title: "{ticker.upper()} Stock Evaluation {today}"\n'
        f"date: {today}\n"
        f"ticker: {ticker.upper()}\n"
        "analysis_type: stock-eval\n"
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
    p = argparse.ArgumentParser(description="Generate stock evaluation report via OpenAI")
    p.add_argument("ticker", help="Stock ticker symbol (e.g. AAPL)")
    p.add_argument("--model", default="gpt-4o", help="OpenAI model ID (default: gpt-4o)")
    p.add_argument("--max-tokens", type=int, default=16000, help="Max output tokens (default: 16000)")
    p.add_argument("--output-dir", default=None, help="Output directory (default: output/stock_eval/<ticker>)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    ticker = args.ticker.upper()
    output_dir = Path(args.output_dir) if args.output_dir else Path("output/stock_eval") / ticker.lower()

    report = generate_report(ticker, args.model, args.max_tokens)
    path = save_report(ticker, report, output_dir)
    print(f"Report saved to: {path}")


if __name__ == "__main__":
    main()
