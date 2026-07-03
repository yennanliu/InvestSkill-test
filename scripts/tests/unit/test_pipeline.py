"""Unit tests for the gen layer (pipeline)."""

import pytest

from analysis import pipeline


@pytest.fixture
def capture_llm(monkeypatch):
    """Stub call_llm + fetch_stock_data; record every call."""
    calls = []

    def fake_call(provider, ticker, prompt, system_message, *, model=None, max_tokens=None, temperature=0.7):
        calls.append({"provider": provider, "ticker": ticker, "prompt": prompt,
                      "system": system_message, "model": model, "max_tokens": max_tokens})
        return "訊號框：評分 7 看多"

    monkeypatch.setattr(pipeline, "call_llm", fake_call)
    monkeypatch.setattr(pipeline, "fetch_stock_data", lambda t: f"DATA[{t}]")
    return calls


def test_generate_analysis_builds_prompt(capture_llm, fake_invest_skill):
    out = pipeline.generate_analysis(
        "aapl", "dcf-valuation", provider="gemini", model="m", max_tokens=100,
        invest_skill_dir=fake_invest_skill,
    )
    assert out == "訊號框：評分 7 看多"
    call = capture_llm[0]
    assert call["ticker"] == "AAPL"
    assert "dcf-valuation framework" in call["prompt"]   # framework injected
    assert "DATA[AAPL]" in call["prompt"]                # shared data injected
    assert "GEMINI" in call["system"]                    # system context injected


def test_generate_analysis_reuses_injected_data(capture_llm, fake_invest_skill):
    # If stock_data is provided, fetch_stock_data must NOT be called.
    def boom(_):
        raise AssertionError("should not fetch")

    import analysis.pipeline as p
    p.fetch_stock_data = boom
    try:
        pipeline.generate_analysis(
            "AAPL", "stock-eval", provider="gemini", model="m", max_tokens=100,
            invest_skill_dir=fake_invest_skill, stock_data="INJECTED",
        )
    finally:
        p.fetch_stock_data = lambda t: f"DATA[{t}]"
    assert "INJECTED" in capture_llm[0]["prompt"]


def test_single_message_has_no_signal_box_but_module_does():
    single = pipeline._single_message("FW", "AAPL", "DCF", "DATA")
    module = pipeline._module_message("FW", "AAPL", "DATA")
    assert "投資訊號框" not in single
    assert "投資訊號框" in module


def test_generate_full_report_runs_all_and_synthesises(capture_llm, fake_invest_skill):
    result = pipeline.generate_full_report(
        "AAPL", provider="gemini", model="m", max_tokens=100,
        invest_skill_dir=fake_invest_skill,
        skills=["technical-analysis", "dcf-valuation"], sleep=0,
    )
    assert len(result["sections"]) == 2
    assert result["skills"] == ["technical-analysis", "dcf-valuation"]
    # 2 modules + 1 synthesis
    assert len(capture_llm) == 3
    # synthesis prompt references the module count
    assert "2 個模組" in capture_llm[-1]["prompt"]


def test_full_report_skips_unavailable_skill(capture_llm, fake_invest_skill):
    result = pipeline.generate_full_report(
        "AAPL", provider="gemini", model="m", max_tokens=100,
        invest_skill_dir=fake_invest_skill,
        skills=["technical-analysis", "no-such-skill"], sleep=0,
    )
    # only the available one ran (+ synthesis)
    assert result["skills"] == ["technical-analysis"]
    assert len(result["sections"]) == 1


def test_full_report_survives_module_failure(monkeypatch, fake_invest_skill):
    monkeypatch.setattr(pipeline, "fetch_stock_data", lambda t: "DATA")

    def flaky(provider, ticker, prompt, system_message, *, model=None, max_tokens=None, temperature=0.7):
        if "technical-analysis framework" in prompt:
            raise RuntimeError("boom")
        return "ok signal"

    monkeypatch.setattr(pipeline, "call_llm", flaky)
    result = pipeline.generate_full_report(
        "AAPL", provider="gemini", model="m", max_tokens=100,
        invest_skill_dir=fake_invest_skill,
        skills=["technical-analysis", "dcf-valuation"], sleep=0,
    )
    # both recorded; the failing one carries an error note
    assert len(result["sections"]) == 2
    labels = dict(result["sections"])
    assert any("模組生成失敗" in v for v in labels.values())
