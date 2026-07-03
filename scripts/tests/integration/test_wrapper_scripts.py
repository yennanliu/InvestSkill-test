"""
Integration tests that execute the real ``scripts/*_gemini.py`` wrapper files
via runpy (as ``__main__``), with the SDK + network boundary faked.

This proves the shipped entrypoints — the exact files CI invokes — wire through
every layer and write a report.
"""

import runpy
from pathlib import Path

import pytest

from analysis.config import TODAY

pytestmark = pytest.mark.integration

SCRIPTS_DIR = Path(__file__).parents[2]  # …/scripts

SINGLE_WRAPPERS = [
    ("dcf_valuation_gemini.py", "dcf_valuation"),
    ("fundamental_analysis_gemini.py", "fundamental_analysis"),
    ("stock_eval_gemini.py", "stock_eval"),
]


def _run_script(name, argv, monkeypatch):
    monkeypatch.setattr("sys.argv", [name, *argv])
    runpy.run_path(str(SCRIPTS_DIR / name), run_name="__main__")


@pytest.mark.parametrize("script,prefix", SINGLE_WRAPPERS)
def test_single_wrapper_scripts(script, prefix, monkeypatch, tmp_path,
                                fake_invest_skill, fake_yfinance, fake_gemini):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    out_dir = tmp_path / prefix
    _run_script(script, [
        "aapl", "--output-dir", str(out_dir),
        "--invest-skill-dir", str(fake_invest_skill),
    ], monkeypatch)

    report = out_dir / f"{prefix}_{TODAY}_gemini-2.5-flash.md"
    assert report.exists(), f"{script} did not produce {report.name}"
    assert "訊號框" in report.read_text(encoding="utf-8")


def test_full_report_wrapper_script(monkeypatch, tmp_path, fake_invest_skill,
                                    fake_yfinance, fake_gemini):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    out_dir = tmp_path / "full"
    _run_script("full_report_gemini.py", [
        "aapl", "--skills", "technical-analysis,dcf-valuation", "--sleep", "0",
        "--output-dir", str(out_dir), "--invest-skill-dir", str(fake_invest_skill),
    ], monkeypatch)

    report = out_dir / f"full_report_{TODAY}_gemini-2.5-flash.md"
    assert report.exists()
    text = report.read_text(encoding="utf-8")
    assert "modules: 2" in text
    assert "綜合結論" in text
