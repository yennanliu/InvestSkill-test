"""Data sources layer: one comprehensive yfinance snapshot per ticker.

This is the only network-touching module for market data. It builds a single
Markdown block rich enough to feed *every* InvestSkill module (fundamentals,
DCF inputs, valuation, dividends, short interest, ownership, price action, and
historical statements), so a full-report run fetches once and shares the result.
"""

from __future__ import annotations

from ..exceptions import DataFetchError
from ..utils.formatting import fmt, hist_table
from ..utils.logging_utils import setup_logger

logger = setup_logger(__name__)


def fetch_stock_data(ticker: str) -> str:
    """Return a Markdown snapshot of live + historical data for ``ticker``."""
    try:
        import yfinance as yf
    except ImportError as exc:  # pragma: no cover - import guard
        raise DataFetchError("yfinance not installed. Run: pip install yfinance") from exc

    t = yf.Ticker(ticker)
    info = t.info or {}
    logger.info(f"Fetched yfinance snapshot for {ticker} ({len(info)} info keys)")

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
        f"**Market Cap:** {fmt(info.get('marketCap'), '$')}",
        f"**Current Price:** {fmt(info.get('currentPrice'), '$')}",
        f"**Shares Outstanding:** {fmt(info.get('sharesOutstanding'))}",
        f"**52W Range:** {get('fiftyTwoWeekLow')} – {get('fiftyTwoWeekHigh')}",
        f"**Beta (5Y monthly):** {get('beta')}",
        f"**Employees:** {get('fullTimeEmployees')}",
        "",
        "### Income Statement (TTM)",
        f"- Revenue: {fmt(revenue, '$')}",
        f"- Gross Profit: {fmt(info.get('grossProfits'), '$')}",
        f"- EBITDA: {fmt(info.get('ebitda'), '$')}",
        f"- Net Income: {fmt(info.get('netIncomeToCommon'), '$')}",
        f"- Gross Margin: {get('grossMargins')}",
        f"- Operating Margin: {get('operatingMargins')}",
        f"- Net Margin: {get('profitMargins')}",
        f"- EPS (TTM / FWD): {get('trailingEps')} / {get('forwardEps')}",
        f"- Revenue Growth (YoY): {get('revenueGrowth')}",
        f"- Earnings Growth (YoY): {get('earningsGrowth')}",
        "",
        "### Balance Sheet",
        f"- Total Cash: {fmt(total_cash, '$')}",
        f"- Total Debt: {fmt(total_debt, '$')}",
        f"- Net Debt: {fmt(net_debt, '$')} {'(net cash)' if net_debt < 0 else ''}",
        f"- Debt/Equity: {get('debtToEquity')}",
        f"- Current / Quick Ratio: {get('currentRatio')} / {get('quickRatio')}",
        f"- Book Value/Share: {get('bookValue')}",
        f"- Price/Book: {get('priceToBook')}",
        "",
        "### Cash Flow (TTM)  — DCF inputs",
        f"- Operating Cash Flow: {fmt(ocf, '$')}",
        f"- Capital Expenditures: {fmt(capex, '$')}",
        f"- Free Cash Flow: {fmt(fcf, '$')}",
        f"- FCF Margin: {fcf_margin}",
        "",
        "### Valuation & Returns",
        f"- P/E (TTM / FWD): {get('trailingPE')} / {get('forwardPE')}",
        f"- P/S: {get('priceToSalesTrailing12Months')}",
        f"- PEG Ratio: {get('pegRatio')}",
        f"- Enterprise Value: {fmt(info.get('enterpriseValue'), '$')}",
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
        f"- Shares Short: {fmt(info.get('sharesShort'))}",
        f"- Short % of Float: {get('shortPercentOfFloat')}",
        f"- Short Ratio (days to cover): {get('shortRatio')}",
        f"- Float Shares: {fmt(info.get('floatShares'))}",
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
            lines += [
                "### Price Action (last 6 months)",
                f"- Latest Close: {fmt(float(last), '$')}",
                f"- 20-day MA: {fmt(float(ma20), '$') if ma20 is not None else 'N/A'}",
                f"- 50-day MA: {fmt(float(ma50), '$') if ma50 is not None else 'N/A'}",
                f"- 6M High / Low: {fmt(float(closes.max()), '$')} / {fmt(float(closes.min()), '$')}",
                "",
                "Recent closes (last 10 trading days):",
                "| Date | Close | Volume |",
                "|---|---|---|",
            ]
            for idx, row in hist.tail(10).iterrows():
                d = idx.date().isoformat() if hasattr(idx, "date") else str(idx)
                lines.append(f"| {d} | {fmt(float(row['Close']), '$')} | {fmt(int(row['Volume']))} |")
            lines.append("")
    except Exception as exc:  # price history is best-effort
        logger.warning(f"price history unavailable for {ticker}: {exc}")

    # Historical statements — growth + FCF trend
    try:
        lines += hist_table(
            t.financials,
            "### Historical Income Statement (last 4 fiscal years)",
            ["Total Revenue", "Gross Profit", "Operating Income", "Net Income", "EBITDA"],
        )
    except Exception as exc:
        logger.warning(f"income statement unavailable for {ticker}: {exc}")

    try:
        lines += hist_table(
            t.cashflow,
            "### Historical Cash Flow (last 4 fiscal years)",
            ["Operating Cash Flow", "Capital Expenditure", "Free Cash Flow",
             "Issuance Of Stock", "Repurchase Of Stock", "Cash Dividends Paid"],
        )
    except Exception as exc:
        logger.warning(f"cash flow unavailable for {ticker}: {exc}")

    return "\n".join(lines)
