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
        "Fetches live and historical financial data for a US stock ticker via yfinance. "
        "Returns income statement, balance sheet, cash flow, valuation multiples, and analyst estimates."
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


def _fetch(ticker: str) -> str:
    t = yf.Ticker(ticker.upper())
    info = t.info or {}

    def get(k):
        v = info.get(k)
        return str(v) if v is not None else "N/A"

    lines = [
        f"## Financial Data: {ticker.upper()}\n",
        f"**Company:** {get('longName')}",
        f"**Sector / Industry:** {get('sector')} / {get('industry')}",
        f"**Market Cap:** {_fmt(info.get('marketCap'), '$')}",
        f"**Price:** {_fmt(info.get('currentPrice'), '$')}",
        f"**52W Range:** {get('fiftyTwoWeekLow')} – {get('fiftyTwoWeekHigh')}",
        "",
        "### Income Statement (TTM)",
        f"- Revenue: {_fmt(info.get('totalRevenue'), '$')}",
        f"- Gross Profit: {_fmt(info.get('grossProfits'), '$')}",
        f"- EBITDA: {_fmt(info.get('ebitda'), '$')}",
        f"- Net Income: {_fmt(info.get('netIncomeToCommon'), '$')}",
        f"- EPS (TTM / FWD): {get('trailingEps')} / {get('forwardEps')}",
        f"- Gross Margin: {get('grossMargins')}  Operating: {get('operatingMargins')}  Net: {get('profitMargins')}",
        f"- Revenue Growth YoY: {get('revenueGrowth')}  Earnings Growth: {get('earningsGrowth')}",
        "",
        "### Balance Sheet",
        f"- Total Cash: {_fmt(info.get('totalCash'), '$')}  Total Debt: {_fmt(info.get('totalDebt'), '$')}",
        f"- D/E: {get('debtToEquity')}  Current Ratio: {get('currentRatio')}  Quick: {get('quickRatio')}",
        f"- Book Value/Share: {get('bookValue')}  P/B: {get('priceToBook')}",
        "",
        "### Cash Flow (TTM)",
        f"- Operating: {_fmt(info.get('operatingCashflow'), '$')}",
        f"- Free Cash Flow: {_fmt(info.get('freeCashflow'), '$')}",
        f"- CapEx: {_fmt(info.get('capitalExpenditures'), '$')}",
        "",
        "### Valuation Multiples",
        f"- P/E (TTM / FWD): {get('trailingPE')} / {get('forwardPE')}",
        f"- PEG: {get('pegRatio')}  P/S: {get('priceToSalesTrailing12Months')}",
        f"- EV/EBITDA: {get('enterpriseToEbitda')}  EV/Revenue: {get('enterpriseToRevenue')}",
        "",
        "### Analyst Estimates",
        f"- Target (mean): {get('targetMeanPrice')}  Range: {get('targetLowPrice')} – {get('targetHighPrice')}",
        f"- Recommendation: {get('recommendationKey')}  ({get('numberOfAnalystOpinions')} analysts)",
    ]

    try:
        fin = t.financials
        if fin is not None and not fin.empty:
            lines.append("\n### Historical Income Statement (4 yr)")
            header = "| Metric |" + "".join(f" {c.year} |" for c in fin.columns[:4])
            lines += [header, "|---|---|---|---|---|"]
            for row in ["Total Revenue", "Gross Profit", "Operating Income", "Net Income"]:
                if row in fin.index:
                    vals = "".join(f" {_fmt(fin.loc[row, c], '$')} |" for c in fin.columns[:4])
                    lines.append(f"| {row} |{vals}")
    except Exception:
        pass

    try:
        cf = t.cashflow
        if cf is not None and not cf.empty:
            lines.append("\n### Historical Cash Flow (4 yr)")
            header = "| Metric |" + "".join(f" {c.year} |" for c in cf.columns[:4])
            lines += [header, "|---|---|---|---|---|"]
            for row in ["Operating Cash Flow", "Capital Expenditure", "Free Cash Flow"]:
                if row in cf.index:
                    vals = "".join(f" {_fmt(cf.loc[row, c], '$')} |" for c in cf.columns[:4])
                    lines.append(f"| {row} |{vals}")
    except Exception:
        pass

    return "\n".join(lines)
