# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

The **sandbox** for the [InvestSkill](https://github.com/yennanliu/InvestSkill) skill library: a real
test environment where the skills maintained upstream are run end to end on live market data, by a real
LLM. It consumes InvestSkill and doesn't contain it. GitHub Actions clones InvestSkill, takes one
`yfinance` snapshot per run, sends each analysis framework to an LLM with that shared snapshot, and
commits the resulting Markdown to `output/`. A separate deterministic generator renders the zh-TW
showcase site under `docs/`.

Changes here usually do one of three jobs: exercise an upstream skill (`run_skill.py`,
`skill_sandbox.yml`), follow an upstream change (`upstream_sync.py`), or keep output manageable
(`cleanup_reports.py`). Fixes to the *skills themselves* belong upstream, not in this repo.

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
`full-report --depth` module sets from `prompts/full-report.md`. `ALIASES` lists upstream redirect
cards ("has been merged into `<target>`"). `dcf-valuation` and `fundamental-analysis` are aliases, so
the daily jobs named after them run a stub. The CLI warns when that happens.

### Staying in sync: `investskill.lock.json`

The lock records the upstream commit, version and SHA-256 of every `prompts/*.md` plus
`GEMINI.md`/`CLAUDE.md` as of the last reviewed sync. `scripts/upstream_sync.py` separates two kinds
of difference:

- **Upstream changes** (the commit or file hashes differ from the lock) can be adopted by rewriting
  the lock (`--write-lock`).
- **Drift** (`ANALYSIS_TYPES`, `DEPTH_TIERS` or `ALIASES` disagree with the clone, which the script
  parses directly) needs a code edit here.

`upstream_sync.yml` turns upstream changes into a PR on `bot/investskill-sync`, and drift into an
`upstream-drift` issue. `test_committed_lock_matches_config` requires the lock's skill set to equal
`ANALYSIS_TYPES`. When you bump the lock, update the config in the same change.

Report workflows still clone InvestSkill `main` at run time, not the locked commit. The lock is the
review baseline, not a runtime pin. Each report's frontmatter `skill_commit` records the revision
that actually ran.

## Commands

There is no requirements file. CI installs only `pytest pandas` for tests. Tests that touch
`data/sources.py` or `utils/formatting.py` use `importorskip("pandas")`, so without pandas about a
dozen tests are **skipped silently** instead of failing. Install it before you trust a green run.

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
python scripts/run_skill.py bear-case NVDA        # any upstream slug, no wrapper needed

# Upstream sync (needs the clone; no keys, no network)
python scripts/upstream_sync.py --check           # exit 1 on drift
python scripts/upstream_sync.py --write-lock      # adopt the clone as the new baseline

# Report retention (default: older than 30 days, under output/ + InvestSkill_output/)
python scripts/cleanup_reports.py --dry-run
```

Every entrypoint shares `--provider {gemini,openai,claude}`, `--model`, `--max-tokens`, `--output-dir`,
`--invest-skill-dir` (default `./InvestSkill`) and `--language` (default zh-TW). `full_report` adds
`--depth` (default `comprehensive`), `--skills` (overrides `--depth`) and `--sleep` (between modules).
`run_skill.py` takes the slug as its first positional, before the ticker.

`upstream_sync.py`, `cleanup_reports.py` and `run_skill.py` sit directly in `scripts/`. `pytest.ini` puts
`scripts/` on the path, so tests import them as top-level modules (`import upstream_sync`).

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
- Motion is layered on, never load-bearing. `shell.py` sets `html.js` from an inline head script and
  every animation selector is gated on it, so a no-JS (or `prefers-reduced-motion`, or print) reader
  gets the final state. Two consequences when editing: reveal targets are chosen by selector in the
  shell's JS rather than marked up in the pages, and anything that hides an element until an animation
  runs (`.rv`, `.ch-draw`'s dash offset, `.fl-node`) **must** be reset in both guard blocks at the
  bottom of the CSS — otherwise "animations off" means "content invisible".
- Flow diagrams (`viz.pipeline_chart` / `phase_chart` / `matrix_dots`) are plain SVG plus CSS classes
  (`fl-node`, `fl-dash`, `fl-cell`); no `<animate>` elements, so they stay static images when motion is
  off. Wrap them with `V.figure(..., extra_cls="dagfig")` to opt into the staggered entrance.
- Flat module layout: `build.py` puts its own directory on `sys.path`, so pages `import context`, not
  `from .context import`. `page_*.py` modules use `from context import *` deliberately — this is
  whitelisted in `ruff.toml` per-file-ignores and shouldn't spread elsewhere.
- Three data defects (KRW filings on a USD ADR, 13 days of price history, a `bookValue` 27% below the
  filed balance sheet) are left in the snapshot **on purpose** so `result-validator` has something real
  to catch. Don't "fix" them.
- `validate_html.py` is stdlib-only by design. Its `ARTIFACTS` list flags Python leakage (`None`,
  `nan`, `{placeholder}`, tracebacks) in rendered output; `ARTIFACT_ALLOW` holds the legitimate
  substrings that trip those regexes.

## Generated output: committed, 30-day retention

`output/` and `InvestSkill_output/` hold LLM-generated reports, committed by the workflows that
produce them. `cleanup_reports.yml` deletes reports older than 30 days every week, dating each one by
the date in its filename, else its frontmatter `date:` (never file mtime). Git history keeps
everything it deletes. Remove reports by age only: don't delete, rewrite or regenerate one to "fix" a
bad call. CodeRabbit review is filtered off these paths.

`docs/index.html` links to reports through a commit permalink
(`blob/<sha>/output/…`), because a `blob/main` link would 404 once retention removes the file. Keep
new report links in that form.

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
