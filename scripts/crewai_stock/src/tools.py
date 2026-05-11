from __future__ import annotations
from typing import Any, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import yfinance as yf


class _Input(BaseModel):
    ticker: str = Field(description="US stock ticker symbol, e.g. AAPL")


class StockDataTool(BaseTool):
    name: str = "stock_data_fetcher"
    description: str = (
        "Fetches comprehensive live and historical financial data for a US stock ticker via yfinance. "
        "Returns income statement, balance sheet, cash flow, valuation multiples, quarterly trends, "
        "analyst estimates, earnings surprises, institutional holders, and recent news headlines."
    )
    args_schema: Type[BaseModel] = _Input

    def _run(self, ticker: str) -> Any:
        return _fetch(ticker)


# ---------------------------------------------------------------------------

def _fmt(v, prefix="", suffix="") -> str:
    if v is None:
        return "N/A"
    if isinstance(v, float):
        return f"{prefix}{v:,.2f}{suffix}"
    if isinstance(v, int):
        return f"{prefix}{v:,}{suffix}"
    return str(v)


def _pct(v) -> str:
    if v is None:
        return "N/A"
    try:
        return f"{float(v)*100:.1f}%"
    except (TypeError, ValueError):
        return str(v)


def _table(df, rows, max_cols=4) -> list[str]:
    cols = df.columns[:max_cols]
    labels = [str(c.date()) if hasattr(c, "date") else str(c) for c in cols]
    header = "| Metric |" + "".join(f" {l} |" for l in labels)
    sep = "|---|" + "---|" * len(cols)
    lines = [header, sep]
    for row in rows:
        if row in df.index:
            vals = "".join(f" {_fmt(df.loc[row, c], '$')} |" for c in cols)
            lines.append(f"| {row} |{vals}")
    return lines


def _fetch(ticker: str) -> str:
    t = yf.Ticker(ticker.upper())
    info = t.info or {}

    def get(k):
        v = info.get(k)
        return str(v) if v is not None else "N/A"

    # ── Overview ─────────────────────────────────────────────────────────────
    lines = [
        f"# Stock Data: {ticker.upper()}\n",
        f"**Company:** {get('longName')}",
        f"**Sector / Industry:** {get('sector')} / {get('industry')}",
        f"**Exchange:** {get('exchange')}  **Currency:** {get('currency')}",
        f"**Country:** {get('country')}  **Employees:** {get('fullTimeEmployees')}",
        f"**Market Cap:** {_fmt(info.get('marketCap'), '$')}",
        f"**Enterprise Value:** {_fmt(info.get('enterpriseValue'), '$')}",
        f"**Price:** {_fmt(info.get('currentPrice'), '$')}",
        f"**52W Range:** {get('fiftyTwoWeekLow')} – {get('fiftyTwoWeekHigh')}",
        f"**50D / 200D MA:** {get('fiftyDayAverage')} / {get('twoHundredDayAverage')}",
        f"**Beta:** {get('beta')}",
        "",
        f"**Business Summary:** {get('longBusinessSummary')}",
        "",
    ]

    # ── Income Statement (TTM) ────────────────────────────────────────────────
    lines += [
        "## Income Statement (TTM)",
        f"- Revenue: {_fmt(info.get('totalRevenue'), '$')}",
        f"- Gross Profit: {_fmt(info.get('grossProfits'), '$')}",
        f"- EBITDA: {_fmt(info.get('ebitda'), '$')}",
        f"- Net Income: {_fmt(info.get('netIncomeToCommon'), '$')}",
        f"- EPS (TTM): {get('trailingEps')}  EPS (FWD): {get('forwardEps')}",
        f"- Gross Margin: {_pct(info.get('grossMargins'))}",
        f"- Operating Margin: {_pct(info.get('operatingMargins'))}",
        f"- Net Margin: {_pct(info.get('profitMargins'))}",
        f"- Revenue Growth YoY: {_pct(info.get('revenueGrowth'))}",
        f"- Earnings Growth YoY: {_pct(info.get('earningsGrowth'))}",
        f"- R&D Expenses: {_fmt(info.get('researchDevelopment'), '$')}",
        "",
    ]

    # ── Balance Sheet ─────────────────────────────────────────────────────────
    lines += [
        "## Balance Sheet",
        f"- Total Cash & Equivalents: {_fmt(info.get('totalCash'), '$')}",
        f"- Total Debt: {_fmt(info.get('totalDebt'), '$')}",
        f"- Net Cash (Debt): {_fmt((info.get('totalCash') or 0) - (info.get('totalDebt') or 0), '$')}",
        f"- Debt / Equity: {get('debtToEquity')}",
        f"- Current Ratio: {get('currentRatio')}  Quick Ratio: {get('quickRatio')}",
        f"- Book Value / Share: {get('bookValue')}  P/B: {get('priceToBook')}",
        f"- Return on Equity (ROE): {_pct(info.get('returnOnEquity'))}",
        f"- Return on Assets (ROA): {_pct(info.get('returnOnAssets'))}",
        "",
    ]

    # ── Cash Flow (TTM) ───────────────────────────────────────────────────────
    lines += [
        "## Cash Flow (TTM)",
        f"- Operating Cash Flow: {_fmt(info.get('operatingCashflow'), '$')}",
        f"- Capital Expenditures: {_fmt(info.get('capitalExpenditures'), '$')}",
        f"- Free Cash Flow: {_fmt(info.get('freeCashflow'), '$')}",
        "",
    ]

    # ── Valuation ─────────────────────────────────────────────────────────────
    lines += [
        "## Valuation Multiples",
        f"- P/E (TTM): {get('trailingPE')}  P/E (FWD): {get('forwardPE')}",
        f"- PEG Ratio: {get('pegRatio')}",
        f"- Price / Sales (TTM): {get('priceToSalesTrailing12Months')}",
        f"- Price / Book: {get('priceToBook')}",
        f"- EV / EBITDA: {get('enterpriseToEbitda')}",
        f"- EV / Revenue: {get('enterpriseToRevenue')}",
        "",
    ]

    # ── Dividends & Buybacks ──────────────────────────────────────────────────
    lines += [
        "## Dividends & Capital Return",
        f"- Dividend Rate: {get('dividendRate')}  Yield: {_pct(info.get('dividendYield'))}",
        f"- Payout Ratio: {_pct(info.get('payoutRatio'))}",
        f"- 5Y Avg Dividend Yield: {_pct(info.get('fiveYearAvgDividendYield'))}",
        f"- Share Buyback (implied by shares change): see historical balance sheet",
        f"- Shares Outstanding: {_fmt(info.get('sharesOutstanding'))}",
        f"- Float: {_fmt(info.get('floatShares'))}",
        f"- Short Ratio: {get('shortRatio')}  Short % Float: {_pct(info.get('shortPercentOfFloat'))}",
        "",
    ]

    # ── Analyst Estimates ─────────────────────────────────────────────────────
    lines += [
        "## Analyst Estimates & Recommendations",
        f"- Consensus: {get('recommendationKey')} ({get('numberOfAnalystOpinions')} analysts)",
        f"- Mean Target: {get('targetMeanPrice')}  Median: {get('targetMedianPrice')}",
        f"- Low Target: {get('targetLowPrice')}  High Target: {get('targetHighPrice')}",
        "",
    ]

    # ── Historical Annual Financials (4 yr) ───────────────────────────────────
    try:
        fin = t.financials
        if fin is not None and not fin.empty:
            lines.append("## Historical Annual Income Statement (4 yr)")
            lines += _table(fin, ["Total Revenue", "Gross Profit", "Operating Income", "Net Income"])
            lines.append("")
    except Exception:
        pass

    try:
        bs = t.balance_sheet
        if bs is not None and not bs.empty:
            lines.append("## Historical Annual Balance Sheet (4 yr)")
            lines += _table(bs, ["Total Assets", "Total Liabilities Net Minority Interest",
                                  "Stockholders Equity", "Total Debt", "Cash And Cash Equivalents"])
            lines.append("")
    except Exception:
        pass

    try:
        cf = t.cashflow
        if cf is not None and not cf.empty:
            lines.append("## Historical Annual Cash Flow (4 yr)")
            lines += _table(cf, ["Operating Cash Flow", "Capital Expenditure", "Free Cash Flow"])
            lines.append("")
    except Exception:
        pass

    # ── Quarterly Financials (last 4 Q) ───────────────────────────────────────
    try:
        qfin = t.quarterly_financials
        if qfin is not None and not qfin.empty:
            lines.append("## Quarterly Income Statement (last 4 Q)")
            lines += _table(qfin, ["Total Revenue", "Gross Profit", "Operating Income", "Net Income"])
            lines.append("")
    except Exception:
        pass

    try:
        qcf = t.quarterly_cashflow
        if qcf is not None and not qcf.empty:
            lines.append("## Quarterly Cash Flow (last 4 Q)")
            lines += _table(qcf, ["Operating Cash Flow", "Capital Expenditure", "Free Cash Flow"])
            lines.append("")
    except Exception:
        pass

    # ── Earnings Surprises ────────────────────────────────────────────────────
    try:
        earnings = t.earnings_dates
        if earnings is not None and not earnings.empty:
            lines.append("## Recent Earnings Surprises (last 4 Q)")
            lines.append("| Quarter | EPS Estimate | EPS Actual | Surprise % |")
            lines.append("|---|---|---|---|")
            for dt, row in earnings.head(4).iterrows():
                est = _fmt(row.get("EPS Estimate"))
                act = _fmt(row.get("Reported EPS"))
                sur = _fmt(row.get("Surprise(%)"), suffix="%")
                lines.append(f"| {str(dt)[:10]} | {est} | {act} | {sur} |")
            lines.append("")
    except Exception:
        pass

    # ── Institutional Holders ─────────────────────────────────────────────────
    try:
        inst = t.institutional_holders
        if inst is not None and not inst.empty:
            lines.append("## Top Institutional Holders")
            lines.append("| Holder | Shares | % Out | Value |")
            lines.append("|---|---|---|---|")
            for _, row in inst.head(6).iterrows():
                lines.append(
                    f"| {row.get('Holder', 'N/A')} "
                    f"| {_fmt(row.get('Shares'))} "
                    f"| {_fmt(row.get('% Out'), suffix='%')} "
                    f"| {_fmt(row.get('Value'), '$')} |"
                )
            lines.append("")
    except Exception:
        pass

    # ── Recent News ───────────────────────────────────────────────────────────
    try:
        news = t.news
        if news:
            lines.append("## Recent News Headlines (last 6)")
            for item in news[:6]:
                title = item.get("title", "")
                pub = item.get("publisher", "")
                lines.append(f"- [{title}] ({pub})")
            lines.append("")
    except Exception:
        pass

    return "\n".join(lines)
