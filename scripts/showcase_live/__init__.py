"""Live showcase: one LLM-generated report per run, on a ticker picked from a fixed universe.

The curated showcase under ``scripts/showcase/`` is frozen: one snapshot, a
deterministic build, every figure recomputed. This package is the other half —
it runs the *current* InvestSkill frameworks on a rotating ticker and publishes
the result under ``docs/showcase/live/``, so the site always carries a recent
run made with the latest upstream skills.

  universe.py  the ticker list and the picker
  mdhtml.py    a small, dependency-free Markdown → HTML converter
  site.py      signal parsing, the per-ticker page, the index, runs.json
  runner.py    the CLI (``scripts/run_showcase_live.py``)
"""
