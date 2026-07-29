# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A *consumer* of the [InvestSkill](https://github.com/yennanliu/InvestSkill) framework library, not the
library itself. GitHub Actions clones InvestSkill, takes one `yfinance` snapshot per run, sends each
analysis framework to an LLM with that shared snapshot, and commits the resulting Markdown to `output/`.
A separate deterministic generator renders the zh-TW showcase site under `docs/`.

Reports are Traditional Chinese (繁體中文) by default — prompts, section headings, and the
"投資訊號框" signal box are all zh-TW string literals in `scripts/analysis/pipeline.py`.

## The external dependency

`scripts/analysis/prompts/` does **not** contain prompts. Every framework and system-context file is
read at runtime from a cloned sibling repo:

```bash
git clone https://github.com/yennanliu/InvestSkill.git InvestSkill
```

`PromptRepo` (in `scripts/analysis/prompts/__init__.py`) reads `InvestSkill/prompts/<slug>.md` for the
framework and `InvestSkill/GEMINI.md` / `CLAUDE.md` for the provider system context (falling back to
`GEMINI.md`). Without that clone, every generation path raises `PromptError`. The test suite fakes the
clone via the `fake_invest_skill` fixture, so tests need neither the clone nor network access.

`ANALYSIS_TYPES` in `scripts/analysis/config/__init__.py` maps a slug to its output prefix/label; the
slug **is** the upstream filename. Adding a framework upstream means adding a row there (an unknown slug
falls back to a derived prefix/label rather than erroring). `DEPTH_TIERS` mirrors upstream's
`full-report --depth` module sets — keep it in sync with `prompts/full-report.md`.

## Commands

```bash
# Tests (no keys, no network — SDKs and yfinance are stubbed in conftest.py)
python -m pytest
python -m pytest scripts/tests/unit/test_pipeline.py::test_name   # single test
python -m pytest -m integration                                    # end-to-end CLI→pipeline→publish
python -m pytest -m "not integration"

# Lint (CI pins ruff 0.16.0; pyflakes + E9 only, style rules deliberately off)
ruff check --no-cache scripts/

# Showcase site — regenerate, verify, inspect the numbers
python scripts/showcase/build.py            # write docs/showcase/
python scripts/showcase/build.py --check    # fail if committed HTML is stale
python scripts/showcase/derive.py           # print the derived-metrics digest
python scripts/validate_html.py docs        # structure · links · a11y · template artifacts

# Report generation (needs the InvestSkill clone + GEMINI_API_KEY)
python scripts/stock_eval_gemini.py AAPL
python scripts/full_report_gemini.py NVDA --depth quick
python scripts/full_report_gemini.py MSFT --skills technical-analysis,bear-case
```

## Architecture: `scripts/analysis/`

Layered; each layer has one job and the layer above never reaches past it.

| Layer | Module | Responsibility |
|---|---|---|
| config | `config/` | slug→metadata table, depth tiers, per-provider default model/tokens |
| prompt | `prompts/` | `PromptRepo` — reads + caches the cloned InvestSkill markdown |
| data | `data/sources.py` | the only market-data network call; one Markdown snapshot rich enough for *every* module |
| provider | `llm/` | `call_llm` dispatches to `run_gemini` / `run_openai` / `run_claude` |
| gen | `pipeline.py` | assembles prompt + snapshot → LLM → report text |
| output | `publish.py` | YAML frontmatter + collision-safe write to `output/<prefix>/<ticker>/` |
| cli | `cli.py` | all argparse; the `scripts/*_gemini.py` files are 2-line wrappers |

Two design decisions worth knowing before editing:

- **One fetch, one PromptRepo per run.** `generate_full_report` fetches yfinance once and injects the
  same `stock_data` string into all 5/10/15 modules, so every section of a report cites identical
  numbers. Don't add a per-module fetch.
- **A failing module never aborts the run.** `generate_full_report` catches per-module exceptions and
  writes `_模組生成失敗：…_` into that section; the synthesis pass is likewise guarded.

Provider runners own their own retry semantics. Shared across all of them (`llm/base.py`): refusal
detection (short response + a phrase from `REFUSAL_PATTERNS`) plus an escalating override prefix, retried
up to `MAX_REFUSAL_RETRIES`. Gemini additionally recovers from `finish_reason == MAX_TOKENS` by retrying
against `GEMINI_TOKEN_CEILING`.

`publish.py` runs `sanitize_mermaid` over every report — LLMs reliably hallucinate two invalid
`xychart-beta` forms (swapped axes, object-literal series) that break rendering. See
`utils/mermaid.py` for what is repaired and what is left alone.

## The showcase generator (`scripts/showcase/`)

`docs/showcase/*.html` is **generated**. Every figure is recomputed from
`scripts/showcase/fixtures/snapshot.json` on each build — no network, no API key, no derived-values
fixture on disk. CI enforces two properties: committed HTML equals a fresh render, and two renders are
byte-identical.

- Hand-editing `docs/showcase/*.html` is pointless — the next build reverts it. Edit the generator, run
  `build.py`, commit the regenerated HTML.
- Anything non-deterministic (`date.today()`, dict iteration over unsorted input, unstable float
  formatting) breaks the byte-identical gate. `ASOF` in `context.py` is a hardcoded date for this reason.
- Flat module layout: `build.py` puts its own directory on `sys.path`, so pages `import context`, not
  `from .context import`. `page_*.py` modules use `from context import *` deliberately — this is
  whitelisted in `ruff.toml` per-file-ignores and shouldn't spread elsewhere.
- Three data defects (KRW filings on a USD ADR, 13 days of price history, a `bookValue` 27% below the
  filed balance sheet) are left in the snapshot **on purpose** so `result-validator` has something real
  to catch. Don't "fix" them.
- `validate_html.py` is stdlib-only by design. Its `ARTIFACTS` list flags Python leakage (`None`,
  `nan`, `{placeholder}`, tracebacks) in rendered output; `ARTIFACT_ALLOW` holds the legitimate
  substrings that trip those regexes.

## Generated output is committed

`output/` and `InvestSkill_output/` hold LLM-generated reports and are committed deliberately, including
ones that later proved wrong. Treat them as an archive: don't clean, rewrite, or regenerate them to
"fix" a bad call. CodeRabbit review is filtered off these paths.

## Legacy vs current entrypoints

- `scripts/*_gemini.py` — current. Thin wrappers over `analysis.cli`, multi-provider.
- `scripts/stock_eval.py`, `dcf_valuation.py`, `fundamental_analysis.py` — earlier standalone
  OpenAI-only scripts that duplicate fetch/prompt/save inline. Still wired to their own workflows; new
  work belongs in the `analysis` package, not here.
- `scripts/crewai_stock/` — separate CrewAI multi-agent experiment with its own `pyproject.toml`.
- `financial-services-dev/` — sample output from Anthropic's `financial-services` plugin; documentation
  only, no code.

## CI

`tests.yml` runs pytest on Python 3.11 and 3.13. `site.yml` runs three independent jobs — showcase build
reproducibility (3.11 + 3.13), `validate_html.py` over `docs/`, and ruff plus an AST check that every
script parses under the 3.11 grammar. Python 3.11 is the floor; avoid newer syntax. The report-generating
workflows are `workflow_dispatch` + scheduled cron and require `GEMINI_API_KEY` / `OPENAI_API_KEY` /
`ANTHROPIC_API_KEY` as repository secrets.

Same-site navigation in `docs/` must use relative links — `site.yml` greps for absolute
`https://…/InvestSkill-test/` hrefs and fails.
