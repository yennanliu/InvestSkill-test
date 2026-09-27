"""Unit tests for the shared CLI layer."""

import pytest

from analysis import cli


def test_run_single_wires_args(monkeypatch, tmp_path, fake_invest_skill):
    captured = {}

    def fake_generate(ticker, analysis_type, *, provider, model, max_tokens, invest_skill_dir, language, **kw):
        captured.update(ticker=ticker, analysis_type=analysis_type, provider=provider,
                        model=model, max_tokens=max_tokens, invest_skill_dir=invest_skill_dir)
        return "REPORT"

    def fake_save(analysis_type, ticker, content, output_dir, provider, model, **kw):
        captured["saved"] = (analysis_type, ticker, content, str(output_dir), provider, model)
        captured["skill_commit"] = kw.get("skill_commit")
        return tmp_path / "out.md"

    monkeypatch.setattr(cli, "generate_analysis", fake_generate)
    monkeypatch.setattr(cli, "save_report", fake_save)
    monkeypatch.setattr("sys.argv", [
        "dcf_valuation_gemini.py", "aapl",
        "--output-dir", str(tmp_path), "--invest-skill-dir", str(fake_invest_skill),
    ])

    cli.run_single("dcf-valuation")

    assert captured["ticker"] == "AAPL"
    assert captured["analysis_type"] == "dcf-valuation"
    # provider default gemini → model/token defaults resolved
    assert captured["provider"] == "gemini"
    assert captured["model"] == "gemini-3.6-flash"
    assert captured["max_tokens"] == 20000
    assert captured["saved"][2] == "REPORT"
    # the fixture is not a git checkout, so there is no revision to record
    assert captured["skill_commit"] is None


def test_run_single_explicit_provider_and_model(monkeypatch, tmp_path, fake_invest_skill):
    captured = {}
    monkeypatch.setattr(cli, "generate_analysis",
                        lambda *a, **k: captured.update(k) or "R")
    monkeypatch.setattr(cli, "save_report", lambda *a, **k: tmp_path / "o.md")
    monkeypatch.setattr("sys.argv", [
        "x", "NVDA", "--provider", "claude", "--model", "claude-x", "--max-tokens", "5000",
        "--output-dir", str(tmp_path), "--invest-skill-dir", str(fake_invest_skill),
    ])
    cli.run_single("stock-eval")
    assert captured["provider"] == "claude"
    assert captured["model"] == "claude-x"
    assert captured["max_tokens"] == 5000


def test_run_single_default_output_dir(monkeypatch, fake_invest_skill):
    captured = {}
    monkeypatch.setattr(cli, "generate_analysis", lambda *a, **k: "R")
    monkeypatch.setattr(cli, "save_report",
                        lambda at, tk, c, out, pv, md, **kw: captured.update(out=str(out)) or out)
    monkeypatch.setattr("sys.argv", ["x", "AAPL", "--invest-skill-dir", str(fake_invest_skill)])
    cli.run_single("dcf-valuation")
    # default: output/<prefix>/<ticker_lower>
    assert captured["out"].replace("\\", "/").endswith("output/dcf_valuation/aapl")


def test_run_full_parses_skills(monkeypatch, tmp_path, fake_invest_skill):
    captured = {}

    def fake_full(ticker, *, provider, model, max_tokens, invest_skill_dir, skills,
                  depth, language, sleep):
        captured.update(ticker=ticker, skills=skills, depth=depth, sleep=sleep)
        return {"sections": [("t", "b")], "synthesis": "v", "skills": ["technical-analysis"]}

    monkeypatch.setattr(cli, "generate_full_report", fake_full)
    monkeypatch.setattr(cli, "save_full_report", lambda *a, **k: tmp_path / "full.md")
    monkeypatch.setattr("sys.argv", [
        "full_report_gemini.py", "aapl", "--skills", "technical-analysis, dcf-valuation",
        "--sleep", "0", "--output-dir", str(tmp_path), "--invest-skill-dir", str(fake_invest_skill),
    ])
    cli.run_full()
    assert captured["ticker"] == "AAPL"
    assert captured["skills"] == ["technical-analysis", "dcf-valuation"]
    assert captured["depth"] == "comprehensive"  # default when --depth is omitted
    assert captured["sleep"] == 0.0


def test_run_full_parses_depth(monkeypatch, tmp_path, fake_invest_skill):
    captured = {}

    def fake_full(ticker, *, depth, skills, **kwargs):
        captured.update(depth=depth, skills=skills)
        return {"sections": [("t", "b")], "synthesis": "v", "skills": []}

    monkeypatch.setattr(cli, "generate_full_report", fake_full)
    monkeypatch.setattr(cli, "save_full_report", lambda *a, **k: tmp_path / "full.md")
    monkeypatch.setattr("sys.argv", [
        "full_report_gemini.py", "aapl", "--depth", "quick", "--sleep", "0",
        "--output-dir", str(tmp_path), "--invest-skill-dir", str(fake_invest_skill),
    ])
    cli.run_full()
    assert captured["depth"] == "quick"
    assert captured["skills"] is None  # --depth alone leaves module selection to the tier


def test_run_full_rejects_unknown_depth(monkeypatch, tmp_path, fake_invest_skill):
    monkeypatch.setattr("sys.argv", [
        "full_report_gemini.py", "aapl", "--depth", "exhaustive",
        "--invest-skill-dir", str(fake_invest_skill),
    ])
    with pytest.raises(SystemExit):  # argparse choices=
        cli.run_full()


def test_run_full_empty_sections_exits(monkeypatch, tmp_path, fake_invest_skill):
    monkeypatch.setattr(cli, "generate_full_report",
                        lambda *a, **k: {"sections": [], "synthesis": "", "skills": []})
    monkeypatch.setattr("sys.argv", ["x", "AAPL", "--invest-skill-dir", str(fake_invest_skill), "--sleep", "0"])
    with pytest.raises(SystemExit):
        cli.run_full()


def test_run_single_warns_on_alias_stub(monkeypatch, tmp_path, fake_invest_skill, capsys):
    monkeypatch.setattr(cli, "generate_analysis", lambda *a, **k: "R")
    monkeypatch.setattr(cli, "save_report", lambda *a, **k: tmp_path / "o.md")
    monkeypatch.setattr("sys.argv", ["x", "AAPL", "--output-dir", str(tmp_path),
                                     "--invest-skill-dir", str(fake_invest_skill)])
    cli.run_single("dcf-valuation")
    assert "alias stub merged into stock-valuation" in capsys.readouterr().err


def test_run_skill_takes_slug_then_ticker(monkeypatch, tmp_path, fake_invest_skill):
    captured = {}

    def fake_generate(ticker, analysis_type, **kw):
        captured.update(ticker=ticker, analysis_type=analysis_type, provider=kw["provider"])
        return "R"

    monkeypatch.setattr(cli, "generate_analysis", fake_generate)
    monkeypatch.setattr(cli, "save_report",
                        lambda at, tk, c, out, pv, md, **kw: captured.update(out=str(out)) or out)
    monkeypatch.setattr("sys.argv", ["run_skill.py", "bear-case", "nvda", "--provider", "claude",
                                     "--invest-skill-dir", str(fake_invest_skill)])
    cli.run_skill()
    assert captured["analysis_type"] == "bear-case"
    assert captured["ticker"] == "NVDA"
    assert captured["provider"] == "claude"
    assert captured["out"].replace("\\", "/").endswith("output/bear_case/nvda")


def test_run_skill_unknown_slug_uses_derived_prefix(monkeypatch, fake_invest_skill):
    captured = {}
    monkeypatch.setattr(cli, "generate_analysis", lambda *a, **k: "R")
    monkeypatch.setattr(cli, "save_report",
                        lambda at, tk, c, out, pv, md, **kw: captured.update(out=str(out)) or out)
    monkeypatch.setattr("sys.argv", ["run_skill.py", "brand-new-skill", "AAPL",
                                     "--invest-skill-dir", str(fake_invest_skill)])
    cli.run_skill()
    assert captured["out"].replace("\\", "/").endswith("output/brand_new_skill/aapl")


def test_run_skill_rejects_full_report(monkeypatch, fake_invest_skill):
    monkeypatch.setattr("sys.argv", ["run_skill.py", "full-report", "AAPL",
                                     "--invest-skill-dir", str(fake_invest_skill)])
    with pytest.raises(SystemExit):
        cli.run_skill()
