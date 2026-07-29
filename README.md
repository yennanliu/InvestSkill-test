# InvestSkill-test

Scheduled US-equity research runs built on the [InvestSkill](https://github.com/yennanliu/InvestSkill)
framework library (v1.11.0, 27 analysis frameworks).

**Project site:** https://yennanliu.github.io/InvestSkill-test/

## Showcase — all 27 frameworks on one basket (繁體中文)

A worked example in Traditional Chinese covering the whole framework catalogue and all seven
[cookbook](https://yennj12.js.org/InvestSkill/cookbook-zh-tw.html) workflows, on a four-stock
basket that all gapped down 7.8–9.6% on the same day (2026-07-28):

| Page | Ticker | Angle |
|---|---|---|
| [展示櫃總覽](https://yennj12.js.org/InvestSkill-test/showcase/) | — | The hub: why they fell together, plus a 27-framework coverage map |
| [四檔對決](https://yennj12.js.org/InvestSkill-test/showcase/screener.html) | all four | `stock-screener` with all 22 sub-factors and their raw inputs shown |
| [MU](https://yennj12.js.org/InvestSkill-test/showcase/mu.html) | MRVL·**MU** | Flagship 15-module report: $820 prices peak margins sustained for ever at 15× |
| [SKHY](https://yennj12.js.org/InvestSkill-test/showcase/skhy.html) | **SKHY** | Data-integrity audit — the framework refuses to give a target (47/100 confidence) |
| [MRVL](https://yennj12.js.org/InvestSkill-test/showcase/mrvl.html) | **MRVL** | GAAP vs non-GAAP gap; three valuation methods disagree by an order of magnitude |
| [SNDL](https://yennj12.js.org/InvestSkill-test/showcase/sndl.html) | **SNDL** | Value-trap anatomy: 0.30× book, but book is melting 7.1%/yr |
| [工作流 A–G](https://yennj12.js.org/InvestSkill-test/showcase/workflows.html) | all four | Seven chained workflows — two correctly stop at the screening gate |
| [產業鏈地圖](https://yennj12.js.org/InvestSkill-test/showcase/supply-chain.html) | — | `industry-map`: HBM chain as 11 layers, 3 chokepoints, 4 second-order ideas |

Three data defects are left in deliberately (KRW filings against a USD ADR, 13 days of price
history, a `bookValue` field 27% below the filed balance sheet) so `result-validator` has
something real to catch. Every figure is derived from one shared snapshot and is recomputable.

## What this repo does

GitHub Actions clones the InvestSkill plugin, takes one `yfinance` snapshot per run, sends each
analysis framework to an LLM with that shared snapshot, and commits the resulting Markdown report
back to `output/`.

| | |
|---|---|
| Frameworks | 27, synced to InvestSkill's `prompts/` |
| Depth tiers | `--depth quick` (5) · `standard` (10) · `comprehensive` (15, default) |
| Default model | `gemini-3.6-flash` (also `--provider openai` / `claude`) |
| Report language | Traditional Chinese (繁體中文) by default, `--language` to change |
| Output | `output/<type>/<ticker>/<type>_<date>_<model>.md` |

## Usage

```bash
git clone https://github.com/yennanliu/InvestSkill.git InvestSkill   # frameworks + system context

python scripts/stock_eval_gemini.py AAPL
python scripts/dcf_valuation_gemini.py TSLA --model gemini-2.5-pro
python scripts/full_report_gemini.py NVDA --depth quick
python scripts/full_report_gemini.py MSFT --skills technical-analysis,bear-case
```

Set `GEMINI_API_KEY` (or `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`) in the environment, or as a
repository secret for the workflows in `.github/workflows/`.

## Layout

```
scripts/analysis/     config · prompts · data · llm · pipeline · publish
scripts/*_gemini.py   thin per-skill entrypoints
scripts/showcase/     zh-TW showcase generator + committed yfinance snapshot
scripts/validate_html.py  stdlib HTML/link/a11y checker for docs/
scripts/tests/        pytest suite (run: python -m pytest)
.github/workflows/    scheduled report jobs + CI
docs/                 project website (GitHub Pages)
output/               every generated report, committed
```

## Rebuilding the showcase

The showcase pages are generated, not hand-written. Every figure is recomputed from
`scripts/showcase/fixtures/snapshot.json` on each build, so a given snapshot always
produces byte-identical HTML — no network access and no API key needed.

```bash
python scripts/showcase/build.py            # regenerate docs/showcase/
python scripts/showcase/build.py --check    # verify committed HTML is current
python scripts/showcase/derive.py           # print the derived-metrics digest
python scripts/validate_html.py docs        # structure · links · a11y · artifacts
```

If you edit a generator module, run `build.py` and commit the regenerated HTML —
CI fails if the two disagree. Editing `docs/showcase/*.html` by hand will be
reverted by the next build, so don't.

## CI

| Workflow | Checks |
|---|---|
| [`tests.yml`](.github/workflows/tests.yml) | pytest on Python 3.11 + 3.13. All LLM SDKs and `yfinance` are faked, so no keys or network are needed. |
| [`site.yml`](.github/workflows/site.yml) | **build** — `docs/showcase` matches a fresh render, and two renders are byte-identical · **validate** — every page in `docs/` passes tag balance, head metadata, heading order, `img`/`svg` labelling, dead internal links and anchors, unrendered template artifacts, and flush borders on the CJK signal blocks · **lint** — `ruff` (pyflakes rules) plus a Python 3.11 grammar check |

Lint scope is deliberately narrow (see [`ruff.toml`](ruff.toml)): pyflakes catches real
defects — undefined names, unused imports, dead locals — while style rules stay off so CI
fails on bugs rather than on formatting opinions.

## Disclaimer

Not investment advice. Reports are LLM-generated output over free public data and can be wrong,
stale, or internally inconsistent. The archive deliberately keeps old reports that later proved
incorrect.
