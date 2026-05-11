from crewai import Crew, LLM, Process
from src.agents import (
    data_collector,
    industry_analyst,
    financial_analyst,
    valuation_analyst,
    report_writer,
    senior_reviewer,
)
from src.tasks import (
    data_task,
    industry_task,
    financial_task,
    valuation_task,
    report_task,
    review_task,
)


def build_crew(ticker: str, model: str = "openai/gpt-4o") -> Crew:
    llm = LLM(model=model)

    collector  = data_collector(llm)
    ind_analyst = industry_analyst(llm)
    fin_analyst = financial_analyst(llm)
    val_analyst = valuation_analyst(llm)
    writer     = report_writer(llm)
    reviewer   = senior_reviewer(llm)

    t1 = data_task(collector, ticker)
    t2 = industry_task(ind_analyst, t1, ticker)
    t3 = financial_task(fin_analyst, t1, t2, ticker)
    t4 = valuation_task(val_analyst, t1, t2, t3, ticker)
    t5 = report_task(writer, [t1, t2, t3, t4], ticker)
    t6 = review_task(reviewer, t5, ticker)

    return Crew(
        agents=[collector, ind_analyst, fin_analyst, val_analyst, writer, reviewer],
        tasks=[t1, t2, t3, t4, t5, t6],
        process=Process.sequential,
        verbose=True,
    )
