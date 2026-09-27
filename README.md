# InvestSkill-test

The sandbox for [InvestSkill](https://github.com/yennanliu/InvestSkill): a real test environment where
the skills maintained there are run end to end on live market data, by a real LLM, on a schedule. Tracks
InvestSkill v1.12.0 (34 files in `prompts/`), pinned in [`investskill.lock.json`](investskill.lock.json).

**Project site:** https://yennanliu.github.io/InvestSkill-test/

## Showcase — all 27 frameworks on one basket (繁體中文, as of v1.11.0)

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
back to `output/`. Three loops keep it useful as a sandbox:

- **Test any skill at any revision.** [`skill_sandbox.yml`](.github/workflows/skill_sandbox.yml) runs
  one skill against an InvestSkill branch, tag, SHA or open PR (`pull/<n>/head`), so a skill change can
  be tried on real data before it merges upstream. Every report's frontmatter records the upstream
  commit that produced it (`skill_commit`).
- **Follow upstream automatically.** [`upstream_sync.yml`](.github/workflows/upstream_sync.yml) checks
  InvestSkill daily. New upstream commits become a PR that bumps the lock and lists what changed.
  Anything this repo's code must follow (a new or removed skill, a `full-report` depth-tier change, a
  new alias stub) becomes an `upstream-drift` issue.
- **Keep only recent output.** [`cleanup_reports.yml`](.github/workflows/cleanup_reports.yml) deletes
  reports older than 30 days every week, or on demand. Git history keeps them.

| | |
|---|---|
| Frameworks | 34 files in InvestSkill's `prompts/`, all runnable via `run_skill.py` |
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
python scripts/run_skill.py earnings-preview NVDA          # any prompts/<skill>.md, by slug
```

`dcf-valuation`, `fundamental-analysis` and `research-bundle` are now alias stubs upstream: redirect
cards merged into `stock-valuation`, `stock-eval` and `full-report`. They still run, but the CLI warns,
because a report from a stub doesn't exercise the real framework.

Set `GEMINI_API_KEY` (or `OPENAI_API_KEY` / `ANTHROPIC_API_KEY`) in the environment, or as a
repository secret for the workflows in `.github/workflows/`.

## Keeping up with InvestSkill

```bash
git clone https://github.com/yennanliu/InvestSkill.git InvestSkill
python scripts/upstream_sync.py                 # what changed since the lock, and what drifted
python scripts/upstream_sync.py --check         # exit 1 if this repo's config has drifted
python scripts/upstream_sync.py --write-lock    # adopt the clone's revision as the new baseline
```

`upstream_sync.yml` runs the same script daily and on `workflow_dispatch`. To get a run as soon as
InvestSkill changes, add this step to a workflow there, using a token that can dispatch to this repo:

```bash
gh api repos/yennanliu/InvestSkill-test/dispatches -f event_type=investskill-updated
```

For the bot to open PRs, enable **Settings → Actions → General → Allow GitHub Actions to create and
approve pull requests**. PRs opened with the default token don't trigger `tests.yml`. To run CI on
them, add a fine-grained PAT (contents, pull requests and issues: read/write) as the `SYNC_TOKEN`
secret. `test_committed_lock_matches_config` fails any lock bump that adds or drops a skill without
the matching `ANALYSIS_TYPES` row.

## Report retention

```bash
python scripts/cleanup_reports.py --dry-run     # list reports older than 30 days
python scripts/cleanup_reports.py --days 60     # delete reports older than 60 days
```

A report's age is the generation date in its filename, or failing that its frontmatter `date:`.
File mtime is never used, and a report with no readable date is kept. `cleanup_reports.yml` runs
every Sunday, and can also be started by hand with `days` / `dry_run` inputs. It commits the
deletions to main.

## Layout

```
scripts/analysis/     config · prompts · data · llm · pipeline · publish
scripts/*_gemini.py   thin per-skill entrypoints
scripts/run_skill.py  any skill by slug (the sandbox entrypoint)
scripts/upstream_sync.py   InvestSkill change + drift detector (investskill.lock.json)
scripts/cleanup_reports.py report retention
scripts/showcase/     zh-TW showcase generator + committed yfinance snapshot
scripts/validate_html.py  stdlib HTML/link/a11y checker for docs/
scripts/tests/        pytest suite (run: python -m pytest)
.github/workflows/    scheduled report jobs + CI
docs/                 project website (GitHub Pages)
output/               generated reports from the last 30 days, committed
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
| [`upstream_sync.yml`](.github/workflows/upstream_sync.yml) | Daily: InvestSkill vs. the lock and `analysis.config`. Changes → lock-bump PR; drift → `upstream-drift` issue |
| [`skill_sandbox.yml`](.github/workflows/skill_sandbox.yml) | Manual: one skill × one ticker × one InvestSkill revision; report uploaded as an artifact, and committed only if asked |
| [`cleanup_reports.yml`](.github/workflows/cleanup_reports.yml) | Weekly + manual: delete reports older than the retention window (default 30 days) |
| [`site.yml`](.github/workflows/site.yml) | **build** — `docs/showcase` matches a fresh render, and two renders are byte-identical · **validate** — every page in `docs/` passes tag balance, head metadata, heading order, `img`/`svg` labelling, dead internal links and anchors, unrendered template artifacts, and flush borders on the CJK signal blocks · **lint** — `ruff` (pyflakes rules) plus a Python 3.11 grammar check |

Lint scope is deliberately narrow (see [`ruff.toml`](ruff.toml)): pyflakes catches real
defects — undefined names, unused imports, dead locals — while style rules stay off so CI
fails on bugs rather than on formatting opinions.

## Disclaimer

Not investment advice. Reports are LLM-generated output over free public data and can be wrong,
stale, or internally inconsistent. Reports that later proved incorrect are not singled out for removal:
every report is deleted by age alone, and stays in git history afterwards.
