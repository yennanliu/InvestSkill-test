# InvestSkill-test

Scheduled US-equity research runs built on the [InvestSkill](https://github.com/yennanliu/InvestSkill)
framework library (v1.11.0, 27 analysis frameworks).

**Project site:** https://yennanliu.github.io/InvestSkill-test/

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
scripts/tests/        pytest suite (run: python -m pytest scripts/tests)
.github/workflows/    scheduled + manual report jobs
docs/                 project website (GitHub Pages)
output/               every generated report, committed
```

## Disclaimer

Not investment advice. Reports are LLM-generated output over free public data and can be wrong,
stale, or internally inconsistent. The archive deliberately keeps old reports that later proved
incorrect.
