"""Unit tests for the per-provider runners (SDKs faked)."""

import pytest

from analysis.exceptions import LLMError
from analysis.llm.claude import run_claude
from analysis.llm.gemini import run_gemini
from analysis.llm.openai import run_openai


# ── Gemini ───────────────────────────────────────────────────────────────────

def test_run_gemini_happy(monkeypatch, fake_gemini):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    out = run_gemini("AAPL", "prompt", "sys", model="gemini-2.5-flash", max_tokens=20000)
    assert "訊號框" in out
    assert fake_gemini.api_key == "k"
    # config threaded through
    contents, max_out, temp, sysmsg = fake_gemini.calls[0]
    assert max_out == 20000 and sysmsg == "sys"


def test_run_gemini_missing_key_raises(monkeypatch, fake_gemini):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(LLMError):
        run_gemini("AAPL", "p", "s", model="gemini-2.5-flash", max_tokens=100)


def test_run_gemini_truncation_recovery(monkeypatch, fake_gemini, gemini_response):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    calls = {"n": 0}

    def responder(contents, cfg):
        calls["n"] += 1
        if calls["n"] == 1:
            return gemini_response("partial", finish="MAX_TOKENS")
        return gemini_response("full report", finish="STOP")

    fake_gemini.responder = responder
    out = run_gemini("AAPL", "p", "s", model="m", max_tokens=1000, token_ceiling=65536)
    assert out == "full report"
    assert calls["n"] == 2  # retried once at the ceiling


def test_run_gemini_refusal_retry(monkeypatch, fake_gemini, gemini_response):
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    monkeypatch.setattr("analysis.llm.gemini.time.sleep", lambda *_: None)
    calls = {"n": 0}

    def responder(contents, cfg):
        calls["n"] += 1
        if calls["n"] == 1:
            return gemini_response("抱歉，我無法協助")
        return gemini_response("完整報告內容")

    fake_gemini.responder = responder
    out = run_gemini("AAPL", "p", "s", model="m", max_tokens=1000,
                     recover_truncation=False)
    assert out == "完整報告內容"
    assert calls["n"] >= 2


# ── OpenAI ───────────────────────────────────────────────────────────────────

def test_run_openai_happy(monkeypatch, fake_openai):
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    out = run_openai("AAPL", "prompt", "sys", model="gpt-4o", max_tokens=16000)
    assert "訊號框" in out
    kw = fake_openai.calls[0]
    assert kw["model"] == "gpt-4o"
    assert kw["messages"][0]["role"] == "system"


def test_run_openai_token_cap(monkeypatch, fake_openai):
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    run_openai("AAPL", "p", "s", model="gpt-4", max_tokens=99999)
    # gpt-4 caps at 8192
    assert fake_openai.calls[0]["max_tokens"] == 8192


def test_run_openai_missing_key_raises(monkeypatch, fake_openai):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(LLMError):
        run_openai("AAPL", "p", "s", model="gpt-4o", max_tokens=100)


# ── Claude ───────────────────────────────────────────────────────────────────

def test_run_claude_happy(monkeypatch, fake_anthropic):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    out = run_claude("AAPL", "prompt", "sys", model="claude-sonnet-4-6", max_tokens=8000)
    assert "訊號框" in out
    assert fake_anthropic.calls[0]["system"] == "sys"


def test_run_claude_missing_key_raises(monkeypatch, fake_anthropic):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises(LLMError):
        run_claude("AAPL", "p", "s", model="claude-sonnet-4-6", max_tokens=100)
