from crewai import Crew, LLM, Process
from src.agents import data_collector, equity_analyst, report_writer
from src.tasks import data_task, analysis_task, report_task


def build_crew(ticker: str, model: str = "openai/gpt-4o") -> Crew:
    llm = LLM(model=model)

    collector = data_collector(llm)
    analyst = equity_analyst(llm)
    writer = report_writer(llm)

    t1 = data_task(collector, ticker)
    t2 = analysis_task(analyst, t1, ticker)
    t3 = report_task(writer, t2, ticker)

    return Crew(
        agents=[collector, analyst, writer],
        tasks=[t1, t2, t3],
        process=Process.sequential,
        verbose=True,
    )
