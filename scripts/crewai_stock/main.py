#!/usr/bin/env python3
"""
CrewAI multi-agent US stock fundamental analysis.
Outputs a Markdown report in Traditional Chinese.

Usage:
  python main.py AAPL
  python main.py TSLA --model openai/gpt-4o-mini --output-dir /path/to/out
"""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from src.crew import build_crew  # noqa: E402 (after load_dotenv)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="CrewAI Stock Fundamental Analysis")
    p.add_argument("ticker", help="Stock ticker symbol (e.g. AAPL)")
    p.add_argument("--model", default="openai/gpt-4o", help="LLM model (default: openai/gpt-4o)")
    p.add_argument("--output-dir", default=None, help="Output directory (default: ../../output/crewai_fundamental_analysis/<ticker>)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    ticker = args.ticker.upper()

    output_dir = (
        Path(args.output_dir)
        if args.output_dir
        else Path(__file__).parent.parent.parent / "output" / "crewai_fundamental_analysis" / ticker.lower()
    )

    print(f"\n=== CrewAI Stock Analysis: {ticker} | model: {args.model} ===\n")

    crew = build_crew(ticker, args.model)
    result = crew.kickoff()

    output_dir.mkdir(parents=True, exist_ok=True)
    today = date.today().isoformat()
    out_path = output_dir / f"fundamental_analysis_{today}_crewai.md"

    counter = 2
    while out_path.exists():
        out_path = output_dir / f"fundamental_analysis_{today}_crewai-{counter}.md"
        counter += 1

    frontmatter = (
        "---\n"
        f'title: "{ticker} 基本面分析 {today}"\n'
        f"date: {today}\n"
        f"ticker: {ticker}\n"
        "analysis_type: fundamental-analysis\n"
        "provider: crewai+openai\n"
        "language: zh-TW\n"
        f"model: {args.model}\n"
        "generated_by: CrewAI multi-agent (scripts/crewai_stock)\n"
        "---\n\n"
    )
    out_path.write_text(frontmatter + str(result), encoding="utf-8")
    print(f"\n✅ Report saved: {out_path}")


if __name__ == "__main__":
    main()
