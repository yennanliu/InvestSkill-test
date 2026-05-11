from crewai import Agent, Task


def data_task(agent: Agent, ticker: str) -> Task:
    return Task(
        description=(
            f"Use the stock_data_fetcher tool to retrieve all available financial data for **{ticker.upper()}**. "
            "Return the complete raw output exactly as produced by the tool — do not summarise or truncate."
        ),
        expected_output=(
            "Full structured financial dataset including: company overview, TTM income statement, "
            "balance sheet, cash flow, valuation multiples, dividend info, analyst estimates, "
            "annual historical financials (4 yr), quarterly financials (4 Q), earnings surprises, "
            "institutional holders, and recent news headlines."
        ),
        agent=agent,
    )


def industry_task(agent: Agent, data_task: Task, ticker: str) -> Task:
    return Task(
        description=(
            f"Using the financial data for **{ticker.upper()}**, produce a comprehensive industry and "
            "competitive intelligence report covering ALL of the following:\n\n"
            "1. **Industry Definition & TAM**: Define the addressable market, size it ($ figures), "
            "   and characterise its growth trajectory (secular growth, cyclical, mature, disrupted).\n"
            "2. **Porter's Five Forces**: Score each force (Low / Medium / High) with a 2-3 sentence "
            "   justification backed by evidence from the financial data (e.g. gross margins as proxy "
            "   for pricing power, capex intensity as barrier-to-entry signal).\n"
            "3. **Competitive Moat Analysis**: Identify which moat types the company possesses "
            "   (brand, switching costs, network effects, cost advantage, intangible assets / patents) "
            "   and provide specific evidence for each claimed moat.\n"
            "4. **Competitive Landscape**: Name the top 3-5 direct competitors and describe how "
            "   this company's margins, growth, and returns compare.\n"
            "5. **Market Share & Positioning**: Is the company a market leader, challenger, or niche player? "
            "   What is its pricing power trajectory?\n"
            "6. **Sector Tailwinds & Headwinds**: Identify 3 macro/structural tailwinds and 3 headwinds "
            "   specific to this industry.\n"
            "7. **Regulatory & Geopolitical Risks**: Note any meaningful regulatory exposure "
            "   (antitrust, data privacy, tariffs, export controls, etc.)."
        ),
        expected_output=(
            "A structured competitive intelligence report (~600 words) with quantitative evidence "
            "throughout. Sections: Industry Overview, Porter's Five Forces (table), Moat Assessment, "
            "Competitive Landscape, Tailwinds & Headwinds, Regulatory Risks."
        ),
        agent=agent,
        context=[data_task],
    )


def financial_task(agent: Agent, data_task: Task, industry_task: Task, ticker: str) -> Task:
    return Task(
        description=(
            f"Perform a rigorous quantitative financial analysis of **{ticker.upper()}** "
            "using the raw financial data and the industry context. Cover ALL of the following:\n\n"
            "1. **Revenue Analysis**: Break down revenue growth — compute exact YoY % for each of "
            "   the last 4 annual periods and last 4 quarters. Identify acceleration or deceleration. "
            "   Comment on revenue quality (recurring vs one-time, organic vs acquired).\n"
            "2. **Profitability Deep-Dive**: Compute gross / operating / net margin for each period. "
            "   Quantify operating leverage (margin expansion per point of revenue growth). "
            "   Compute EBITDA margin. Assess R&D spend as % of revenue.\n"
            "3. **DuPont Analysis**: Decompose ROE = Net Margin × Asset Turnover × Equity Multiplier. "
            "   Show all three components with actual numbers and explain what is driving ROE.\n"
            "4. **Balance Sheet Quality**: Assess liquidity (current & quick ratios), "
            "   solvency (D/E, net debt/EBITDA), capital structure efficiency. "
            "   Flag goodwill / intangibles as % of assets if elevated.\n"
            "5. **Cash Flow Quality**: Compute FCF conversion rate (FCF / Net Income). "
            "   Compare operating cash flow vs net income for accrual signal. "
            "   Assess CapEx intensity (CapEx / Revenue) and maintenance vs growth CapEx.\n"
            "6. **Capital Allocation Scorecard**: Evaluate buybacks (share count trend), "
            "   dividends (payout ratio sustainability), M&A (if evident), and ROIC trend.\n"
            "7. **Earnings Quality Flags**: Identify any concerning trends — "
            "   large accruals, revenue recognition issues, rising DSO, inventory build, "
            "   or aggressive capitalization of costs.\n"
            "8. **Quarterly Trend Check**: From the quarterly data, identify any sequential "
            "   improvement or deterioration in revenue, margins, or FCF in the most recent quarters."
        ),
        expected_output=(
            "A rigorous financial analysis report (~800 words) with explicit numbers, "
            "YoY/QoQ percentage changes, and ratio calculations throughout. "
            "Sections: Revenue Analysis, Profitability, DuPont ROE Decomposition, "
            "Balance Sheet Quality, Cash Flow Quality, Capital Allocation, "
            "Earnings Quality, Quarterly Trend."
        ),
        agent=agent,
        context=[data_task, industry_task],
    )


def valuation_task(agent: Agent, data_task: Task, industry_task: Task, financial_task: Task, ticker: str) -> Task:
    return Task(
        description=(
            f"Perform a comprehensive multi-method valuation of **{ticker.upper()}** "
            "and produce three scenarios with explicit 12-month price targets. "
            "Cover ALL of the following:\n\n"
            "1. **Current Valuation Snapshot**: Present the key multiples (P/E TTM & FWD, "
            "   EV/EBITDA, P/S, P/FCF, PEG) and compare them to: "
            "   (a) the company's own 3-year historical range, "
            "   (b) direct competitors.\n"
            "2. **Implied Growth Analysis**: Using current P/E or EV/EBITDA, "
            "   back-solve: what revenue/earnings growth rate is the market pricing in? "
            "   Is that expectation achievable given the historical track record?\n"
            "3. **DCF Framework (qualitative)**: Describe the key FCF growth drivers for years 1-5 "
            "   and the terminal growth assumption. Estimate a reasonable WACC range given beta and "
            "   capital structure. State whether the stock appears under/fairly/overvalued on a DCF basis.\n"
            "4. **Scenario Analysis** — produce all three with explicit assumptions and price targets:\n"
            "   - 🐻 **Bear Case** (probability %): What goes wrong? "
            "     (e.g. margin compression, revenue miss, multiple de-rating). "
            "     State revenue/EPS assumption and resulting target multiple → 12M price target.\n"
            "   - 📊 **Base Case** (probability %): Consensus expectations largely met. "
            "     State revenue/EPS assumption and target multiple → 12M price target.\n"
            "   - 🚀 **Bull Case** (probability %): Upside surprise. "
            "     State revenue/EPS assumption and multiple expansion → 12M price target.\n"
            "   - **Probability-weighted target price** = sum of (price × probability).\n"
            "5. **Key Catalysts & De-risking Events**: List 3-5 upcoming events "
            "   (earnings dates, product launches, regulatory decisions) that could move the stock.\n"
            "6. **Overall Verdict**: BUY / HOLD / SELL with conviction level (High / Medium / Low) "
            "   and the single most important reason."
        ),
        expected_output=(
            "A structured valuation report (~600 words) with explicit numbers throughout. "
            "Sections: Valuation Snapshot (table), Implied Growth, DCF Framework, "
            "Scenario Analysis (3 scenarios with price targets & probabilities), "
            "Catalysts, Verdict."
        ),
        agent=agent,
        context=[data_task, industry_task, financial_task],
    )


def report_task(agent: Agent, prev_tasks: list, ticker: str) -> Task:
    return Task(
        description=(
            f"Synthesise all upstream analysis into a comprehensive equity research report "
            f"for **{ticker.upper()}**. "
            "Write ENTIRELY in Traditional Chinese (繁體中文). Minimum 2,500 words. "
            "Use markdown formatting with clear section headers.\n\n"
            "Required sections (in order):\n"
            f"# {ticker.upper()} 深度基本面分析報告\n"
            "## 公司概覽\n"
            "## 行業分析與競爭格局\n"
            "## 財務表現深度分析\n"
            "## 資產負債表與資本結構\n"
            "## 現金流與資本配置\n"
            "## 估值分析\n"
            "## 情境分析（空頭／基準／多頭）\n"
            "## 主要風險因素\n"
            "## 成長催化劑\n"
            "## 投資結論\n\n"
            "Rules:\n"
            "- Every section must contain specific numbers, not vague statements.\n"
            "- Include at least one markdown table in the financial or valuation section.\n"
            "- The investment conclusion must state a clear BUY/HOLD/SELL in Chinese "
            "  (買入 / 持有 / 賣出) with the probability-weighted 12-month price target.\n"
            "- Do NOT include a top-level executive summary — the reviewer will add that."
        ),
        expected_output=(
            "A complete markdown equity research report in Traditional Chinese, "
            "at least 2,500 words, with all 10 required sections, specific data throughout, "
            "and a clear investment conclusion with price target."
        ),
        agent=agent,
        context=prev_tasks,
    )


def review_task(agent: Agent, report_task: Task, ticker: str) -> Task:
    return Task(
        description=(
            f"You are the Chief Research Officer reviewing the draft report for **{ticker.upper()}**. "
            "Your job is to elevate it to institutional publication standard. Do ALL of the following:\n\n"
            "1. **Add an Executive Summary (執行摘要)** at the very top of the report containing:\n"
            "   - A 📊 Key Metrics Summary table (Ticker, Price, Market Cap, P/E TTM, P/E FWD, "
            "     EV/EBITDA, Gross Margin, Net Margin, FCF Yield, ROE, Analyst Target, Our Target).\n"
            "   - A 3-5 sentence investment thesis paragraph.\n"
            "   - Clear verdict line: e.g. ✅ 買入 | 目標價：$XXX | 信心水準：高\n"
            "2. **Review each section** for completeness and accuracy:\n"
            "   - Confirm all quoted numbers match the raw financial data.\n"
            "   - Replace any vague language ('relatively strong', 'somewhat elevated') "
            "     with specific quantified statements.\n"
            "   - Ensure the bear/base/bull scenarios each have explicit probability weights "
            "     that sum to 100%, and explicit 12-month price targets.\n"
            "3. **Strengthen Risk Section**: Each risk must have a quantified impact "
            "   (e.g. 'a 100bps margin compression would reduce EPS by approximately X%').\n"
            "4. **Polish language**: Ensure Traditional Chinese is precise, professional, "
            "   and free of mixed simplified/traditional characters.\n"
            "5. **Return the COMPLETE final report** — not a list of edits, but the full polished "
            "   markdown document ready for publication, starting with 執行摘要."
        ),
        expected_output=(
            "The complete, publication-ready equity research report in Traditional Chinese "
            "with: (1) an 執行摘要 section with key metrics table and clear verdict at the top, "
            "(2) all original sections enhanced with specific data, "
            "(3) quantified risks, (4) probability-weighted scenario analysis, "
            "(5) a definitive BUY/HOLD/SELL conclusion with 12-month price target."
        ),
        agent=agent,
        context=[report_task],
    )
