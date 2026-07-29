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

## The showcase (`scripts/showcase/` → `docs/showcase/`)

A zh-TW worked example that runs InvestSkill's whole framework catalogue over one four-stock basket.
`docs/showcase/*.html` is **generated** — ~900 KB of HTML from ~5,500 lines of Python and one 450 KB
snapshot fixture. Nothing is hand-written and nothing is fetched at build time.

### Editorial premise

MU, SKHY, MRVL and SNDL all gapped down 7.8–9.6% on 2026-07-28 — three memory/AI semis plus one
deliberately unrelated Canadian cannabis retailer, which makes the synchronicity a liquidity event
rather than a fundamental one. That is the hook every page hangs off. Each ticker carries a distinct
demonstration role, so changing the basket would break the narrative, not just the numbers:

| Ticker | Role in the showcase |
|---|---|
| MU | Flagship 15-module report — $820 prices peak margins as permanent at 15× |
| SKHY | Data-integrity audit — KRW filings on a USD ADR, 13 days of history; the framework *refuses* to give a target (47/100 confidence) |
| MRVL | GAAP vs non-GAAP gap; three valuation methods disagree by an order of magnitude |
| SNDL | Value-trap anatomy — 0.30× book, but book is melting 7.1%/yr |

### Pages

`build.py` renders exactly eight files; `TICKERS` in `build.py` drives the four per-ticker pages.

| File | Module | Content |
|---|---|---|
| `index.html` | `page_hub.py` | Hub: the shared gap-down, benchmark context, 27-framework coverage map |
| `screener.html` | `page_screener.py` | `stock-screener` head-to-head — 5 weighted dimensions, every sub-factor and its raw input shown |
| `mu/skhy/mrvl/sndl.html` | `page_stock.py` | The 15-module `full-report`, one section per module (M1–M15), then synthesis, bear-case red team, scorecard, valuation summary, entry/exit ladder, catalyst calendar, monitoring, `result-validator` audit, signal box |
| `workflows.html` | `page_workflows.py` | Cookbook workflows A–G run for real; C and D correctly stop at the screening gate |
| `supply-chain.html` | `page_chain.py` | `industry-map` — HBM chain as 11 layers, 3 chokepoints, 4 second-order ideas |

### Build pipeline

```
fixtures/snapshot.json ──► derive.py ──► context.py ──► page_*.py ──► shell.page() ──► HTML
   (raw yfinance dump)     (DERIVED)    (facts + fmt)   (+ viz, prose)   (chrome)
```

| Module | Role |
|---|---|
| `fixtures/snapshot.json` | Raw yfinance dump: per ticker `info`, `hist_1y`/`hist_5y`, annual + quarterly `financials`/`balance_sheet`/`cashflow`, `inst_holders`, `insider_tx`, `recos`, `calendar`, option chains; plus `_bench` (`^GSPC`, `^SOX`, `SMH`, `^IXIC`) |
| `derive.py` | Every computed metric: Piotroski F-Score, ROIC vs WACC, DCF (`DCF_ASSUMPTIONS`), relative performance, IV/max-pain, the 5-dimension screener score, and the 5-phase `composite`. Exposes `DERIVED[ticker]`. Runnable standalone as a digest. |
| `context.py` | The star-imported namespace: `RAW`, `C` (=`DERIVED`), `T`, `ASOF`, `NAMES`, `ROLE`, plus page-level facts (`GAP`, `DD`, `EARN`, `CYC`, `INS`, `INST`, `BS`, `RECO`) and every formatter (`money`, `pc`, `pcf`, `num`, `cls`, `arrow`, `st`, `sig_block`, `prov`, `interp`) |
| `viz.py` | Hand-rolled SVG chart primitives — `line_chart`, `hbar_chart`, `radar_chart`, `football_field`, `scatter_chart`, `insider_timeline`, `column_chart`, `gauge`, `heat_table`, `simple_table`, wrapped by `figure()`. No JS charting library; charts are inline SVG so pages are self-contained. |
| `prose.py` | The editorial layer — `P[ticker]` with ~23 keyed narrative slots (`tagline`, `spine`, `thesis`, `bull`, `bear`, one per module, `valid`, `vflags`, `sig`). Prose *interprets* numbers; it must not restate figures the generator could compute. |
| `shell.py` | `CSS` + `JS` + `page(title, desc, body, active)` — doctype, head metadata, OG tags, inline-SVG favicon, nav, skip link, footer, disclaimer. Also `nav()`, `toc()`, `NAV_ITEMS`. |

### Determinism is the contract

CI enforces two properties: committed HTML equals a fresh render, and two consecutive renders are
byte-identical. Both jobs run on 3.11 and 3.13.

- **Hand-editing `docs/showcase/*.html` is pointless** — the next build reverts it. Edit the generator,
  run `build.py`, commit the regenerated HTML. `build.py --check` prints a unified diff naming the
  stale page, and flags `MISSING` / `ORPHAN` files.
- Anything non-deterministic breaks the gate: `date.today()`, `random`, dict iteration over unsorted
  input, set ordering, unstable float formatting. `ASOF = "2026-07-29"` in `context.py` is a hardcoded
  string for exactly this reason — never make it dynamic.
- **No derived-values fixture on disk.** Every number is recomputed from the snapshot each build, so a
  page can't quietly drift from the data it cites. Don't cache `DERIVED` to a file.
- Flat module layout: `build.py` puts its own directory on `sys.path`, so pages do `import context`, not
  `from .context import`. `page_*.py` use `from context import *` deliberately — whitelisted in
  `ruff.toml` per-file-ignores, and it shouldn't spread beyond those files.

### Conventions the validator enforces

`validate_html.py` is stdlib-only and checks what has actually broken here before. When adding markup:

- **Exactly one `<h1>` per page**, and heading levels never skip going down.
- Every `<img>` needs `alt`; every `<svg>` needs `aria-hidden="true"` or `role="img"` (or an
  `aria-hidden` wrapper within ~160 chars). The chart helpers in `viz.py` already do this.
- Every data `<table>` needs `<th>` cells.
- Internal links and `#anchors` must resolve — including cross-page fragments. Same-site navigation
  must be **relative**; `site.yml` greps for absolute `https://…/InvestSkill-test/` hrefs and fails.
- No Python leakage in rendered output: `None`, `nan`, `{placeholder}`, `lambda`, `[tk]`, tracebacks.
  `ARTIFACT_ALLOW` holds the legitimate substrings that trip those regexes; extend it rather than
  loosening a pattern.
- **ASCII signal-box borders must be flush.** `sig_block()` pads by *East Asian display width*, not
  `len()` — CJK glyphs occupy two monospace cells. Any new box-drawing output must use `_dw`/`_pad`
  from `context.py`, or the check fails.

Nothing checks *semantic* drift. Headline counts ("27 個框架", "22 個子因子") are hardcoded prose
strings, not derived from the data, so they can and do fall out of step with the tables beneath them —
`page_screener.py` currently hardcodes 22 in eight places while `derive.py` computes 21. Prefer
deriving a count over restating it.

### Deliberate defects — do not "fix"

Three data problems are left in the snapshot on purpose so `result-validator` has something real to
catch: SKHY's KRW-denominated filings against a USD ADR price (`KRW = 1380.0` is a stated assumption,
not a silent patch), SKHY's 13 days of price history, and a `bookValue` field 27% below the filed
balance sheet.

Insufficient data is meant to **propagate as `None`, not as a fabricated number**. SKHY has no momentum
sub-factors at all, so its 動能 dimension is `None` and drops out of the weighted total — that visible
hole is the point of the page. Preserve that behaviour when touching `derive.py`.

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
