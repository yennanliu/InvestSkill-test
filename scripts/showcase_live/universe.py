"""The tickers the live showcase rotates through, and how one is picked."""
from __future__ import annotations

import random

# Order is not significant. Funds are detected at run time (yfinance quoteType),
# not listed here, so a ticker that changes structure needs no edit.
UNIVERSE: tuple[str, ...] = (
    # semis, memory, thematic funds
    "SPCX", "MU", "SKHY", "WDC", "SNDK", "MRVL", "SOXQ", "SOXX", "WQTM", "VTI",
    "QQQ", "ROBO", "UBER",
    # large caps, growth, defence and space
    "TSLA", "PL", "GRAB", "TSM", "GOOG", "AMZN", "MSFT", "SOFI", "PLTR", "RKLB",
    "ONDS", "AVAV", "KTOS", "META", "AMD", "NVDA", "NU", "VST", "ORCL",
)

# Modules run for a fund. ``full-report`` is a single-stock orchestrator and its
# own framework says to stop and use ``etf-analysis`` for an ETF.
ETF_SKILLS: tuple[str, ...] = (
    "etf-analysis", "technical-analysis", "sector-analysis", "economics-analysis",
)


def pick(recent: list[str], *, universe: tuple[str, ...] = UNIVERSE,
         rng: random.Random | None = None) -> str:
    """Pick a random ticker, avoiding the most recently run half of the universe.

    ``recent`` is newest first. Pure random choice would repeat tickers while
    others wait weeks; excluding the latest ``len(universe) // 2`` distinct
    tickers keeps the choice random but spreads the runs.
    """
    rng = rng or random.SystemRandom()
    cooling: list[str] = []
    for ticker in recent:
        ticker = ticker.upper()
        if ticker in universe and ticker not in cooling:
            cooling.append(ticker)
        if len(cooling) >= len(universe) // 2:
            break
    candidates = [t for t in universe if t not in cooling] or list(universe)
    return rng.choice(candidates)
