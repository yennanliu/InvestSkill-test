from crewai import Agent
from src.tools import StockDataTool


def data_collector(llm) -> Agent:
    return Agent(
        role="Stock Data Collector",
        goal="Retrieve comprehensive and accurate financial data for a given stock ticker",
        backstory=(
            "You are a financial data specialist who fetches precise market data. "
            "You always use the stock_data_fetcher tool to obtain the latest numbers."
        ),
        tools=[StockDataTool()],
        llm=llm,
        verbose=True,
    )


def equity_analyst(llm) -> Agent:
    return Agent(
        role="Senior Equity Analyst",
        goal="Perform deep fundamental analysis based on the collected financial data",
        backstory=(
            "You are a CFA-level equity analyst with 15 years of experience covering "
            "US technology and growth stocks. You identify financial strengths, risks, "
            "valuation drivers, and a clear investment thesis from raw data."
        ),
        llm=llm,
        verbose=True,
    )


def report_writer(llm) -> Agent:
    return Agent(
        role="Investment Report Writer",
        goal="Produce a structured, professional fundamental analysis report in Traditional Chinese",
        backstory=(
            "You are a bilingual equity research writer specialising in Traditional Chinese "
            "(繁體中文) investment reports. You transform complex analysis into clear, "
            "structured markdown that institutional and retail investors can act on."
        ),
        llm=llm,
        verbose=True,
    )
