"""
Integration tests: the full real wiring (config → prompts → data → llm →
pipeline → publish), with only the SDK + network boundary faked.

Unlike the unit tests, nothing inside the package is monkeypatched — the real
``call_llm`` runs against the fake Gemini/OpenAI SDK, and the real
``fetch_stock_data`` runs against the fake yfinance.
"""

import pytest

from analysis import cli
from analysis.config import TODAY

pytestmark = pytest.mark.integration


def test_single_report_end_to_end(monkeypatch, tmp_path, fake_invest_skill,
                                  fake_yfinance, fake_gemini):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    out_dir = tmp_path / "out"
    monkeypatch.setattr("sys.argv", [
        "dcf_valuation_gemini.py", "aapl",
        "--output-dir", str(out_dir), "--invest-skill-dir", str(fake_invest_skill),
    ])

    cli.run_single("dcf-valuation")

    report = out_dir / f"dcf_valuation_{TODAY}_gemini-3.6-flash.md"
    assert report.exists()
    text = report.read_text(encoding="utf-8")
    assert "analysis_type: dcf-valuation" in text
    assert "訊號框" in text  # the fake Gemini output flowed through
    # data + framework actually reached the model
    contents = fake_gemini.calls[0][0]
    assert "Apple Inc." in contents
    assert "dcf-valuation framework" in contents


def test_full_report_end_to_end(monkeypatch, tmp_path, fake_invest_skill,
                                fake_yfinance, fake_gemini):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    out_dir = tmp_path / "full"
    monkeypatch.setattr("sys.argv", [
        "full_report_gemini.py", "aapl",
        "--skills", "technical-analysis,fundamental-analysis,dcf-valuation",
        "--sleep", "0", "--output-dir", str(out_dir),
        "--invest-skill-dir", str(fake_invest_skill),
    ])

    cli.run_full()

    report = out_dir / f"full_report_{TODAY}_gemini-3.6-flash.md"
    assert report.exists()
    text = report.read_text(encoding="utf-8")
    assert "modules: 3" in text
    assert "綜合結論" in text
    assert "### 1." in text and "### 3." in text
    # 3 modules + 1 synthesis = 4 model calls
    assert len(fake_gemini.calls) == 4


def test_end_to_end_with_openai_provider(monkeypatch, tmp_path, fake_invest_skill,
                                         fake_yfinance, fake_openai):
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    out_dir = tmp_path / "oai"
    monkeypatch.setattr("sys.argv", [
        "stock_eval_gemini.py", "aapl", "--provider", "openai",
        "--output-dir", str(out_dir), "--invest-skill-dir", str(fake_invest_skill),
    ])

    cli.run_single("stock-eval")

    report = out_dir / f"stock_eval_{TODAY}_gpt-4o.md"
    assert report.exists()
    assert "provider: openai" in report.read_text(encoding="utf-8")
