from crewai import Agent, Task


def data_task(agent: Agent, ticker: str) -> Task:
    return Task(
        description=(
            f"Use the stock_data_fetcher tool to retrieve all available financial data "
            f"for the ticker **{ticker.upper()}**. Return the full data summary."
        ),
        expected_output=(
            "A structured markdown summary including income statement, balance sheet, "
            "cash flow, valuation multiples, analyst estimates, and historical financials."
        ),
        agent=agent,
    )


def analysis_task(agent: Agent, data_task: Task, ticker: str) -> Task:
    return Task(
        description=(
            f"Using the financial data for {ticker.upper()}, perform a deep fundamental analysis:\n"
            "1. Business overview and competitive position\n"
            "2. Revenue & profitability trends\n"
            "3. Balance sheet strength and liquidity\n"
            "4. Cash flow quality and capital allocation\n"
            "5. Valuation (absolute and relative to peers)\n"
            "6. Key risks and growth catalysts\n"
            "7. Investment thesis summary"
        ),
        expected_output=(
            "A detailed analytical report in plain text with quantitative findings, "
            "trend analysis, and a concise investment thesis."
        ),
        agent=agent,
        context=[data_task],
    )


def report_task(agent: Agent, analysis_task: Task, ticker: str) -> Task:
    return Task(
        description=(
            f"Transform the fundamental analysis into a professional markdown investment "
            f"report for {ticker.upper()}. Write entirely in Traditional Chinese (繁體中文). "
            "Follow the required section structure below."
        ),
        expected_output=(
            "A complete markdown report in Traditional Chinese with these sections:\n"
            "# {ticker} 基本面分析\n"
            "## 公司概覽\n"
            "## 財務表現分析\n"
            "## 資產負債表分析\n"
            "## 現金流分析\n"
            "## 估值分析\n"
            "## 風險與成長催化劑\n"
            "## 投資結論"
        ),
        agent=agent,
        context=[analysis_task],
    )
