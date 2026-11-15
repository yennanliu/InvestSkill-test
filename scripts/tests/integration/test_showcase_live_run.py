"""End to end: the live-showcase CLI with the LLM SDK and yfinance faked."""
from __future__ import annotations

import json

import pytest

from showcase_live import runner, site

pytestmark = pytest.mark.integration

FOOTER = ('{"investskill": "1", "skill": "x", "signal": "NEUTRAL", "confidence": "LOW", '
          '"score": 5.0, "action": "HOLD"}')


@pytest.fixture(autouse=True)
def no_backoff(monkeypatch):
    """The provider layer sleeps between retries; a test must never wait on that."""
    monkeypatch.setattr("analysis.llm.gemini.time.sleep", lambda *_: None)


@pytest.fixture
def clone(fake_invest_skill):
    for slug in ("bear-case", "etf-analysis"):
        (fake_invest_skill / "prompts" / f"{slug}.md").write_text(f"# {slug}", encoding="utf-8")
    (fake_invest_skill / "package.json").write_text('{"version": "9.9.9"}', encoding="utf-8")
    return fake_invest_skill


def _argv(tmp_path, clone, *extra):
    return ["--invest-skill-dir", str(clone), "--live-dir", str(tmp_path / "live"),
            "--output-dir", str(tmp_path / "out"), "--sleep", "0", *extra]


def test_stock_run_writes_page_index_manifest_and_markdown(tmp_path, clone, fake_yfinance,
                                                          fake_gemini, gemini_response,
                                                          monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    text = "分析。\n```json\n" + FOOTER + "\n```"
    fake_gemini.responder = staticmethod(lambda contents, cfg: gemini_response(text))

    assert runner.main(_argv(tmp_path, clone, "--ticker", "mu", "--depth", "quick")) == 0

    live = tmp_path / "live"
    run = json.loads((live / "runs.json").read_text(encoding="utf-8"))["runs"][0]
    assert run["ticker"] == "MU" and run["kind"] == "stock" and run["skill_version"] == "9.9.9"
    assert [m["slug"] for m in run["modules"]] == [
        "stock-eval", "stock-valuation", "insider-trading", "technical-analysis", "bear-case"]
    assert all(m["status"] == "ok" and m["score"] == 5.0 for m in run["modules"])
    assert run["page"].endswith("/show_case.html") and (live / run["page"]).exists()
    assert f'href="{run["page"]}"' in (live / "index.html").read_text("utf-8")
    assert len(list((tmp_path / "out").glob("full_report_*.md"))) == 1


def test_fund_runs_the_etf_module_set(tmp_path, clone, fake_yfinance, fake_gemini, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    fake_yfinance.info = {**fake_yfinance.info, "quoteType": "ETF", "longName": "Total Market ETF"}

    assert runner.main(_argv(tmp_path, clone, "--ticker", "VTI")) == 0

    run = site.load_manifest(tmp_path / "live")["runs"][0]
    assert run["kind"] == "etf" and run["name"] == "Total Market ETF"
    assert [m["slug"] for m in run["modules"]][0] == "etf-analysis"
    assert len(run["modules"]) == 4


def test_nothing_is_published_when_most_modules_fail(tmp_path, clone, fake_yfinance,
                                                    fake_gemini, monkeypatch, capsys):
    monkeypatch.setenv("GEMINI_API_KEY", "k")

    def boom(contents, cfg):
        raise RuntimeError("quota")
    fake_gemini.responder = staticmethod(boom)

    assert runner.main(_argv(tmp_path, clone, "--ticker", "MU", "--depth", "quick")) == 1
    assert "not publishing" in capsys.readouterr().err
    assert not (tmp_path / "live").exists()


def test_print_pick_and_rebuild_index_need_no_key_or_clone(tmp_path, capsys):
    assert runner.main(["--live-dir", str(tmp_path), "--print-pick"]) == 0
    assert capsys.readouterr().out.strip() in runner.UNIVERSE
    assert runner.main(["--live-dir", str(tmp_path), "--rebuild-index"]) == 0
    assert (tmp_path / "index.html").exists()
