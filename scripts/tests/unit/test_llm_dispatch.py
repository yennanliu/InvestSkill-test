"""Unit tests for the call_llm dispatcher."""

import pytest

import analysis.llm as llm
from analysis.exceptions import LLMError


def test_dispatches_to_named_provider(monkeypatch):
    seen = {}

    def fake_runner(ticker, prompt, system_message, *, model, max_tokens, temperature):
        seen.update(provider="gemini", model=model, max_tokens=max_tokens)
        return "ok"

    monkeypatch.setitem(llm._RUNNERS, "gemini", fake_runner)
    out = llm.call_llm("gemini", "AAPL", "p", "s", model="m", max_tokens=123)
    assert out == "ok"
    assert seen == {"provider": "gemini", "model": "m", "max_tokens": 123}


def test_resolves_provider_defaults(monkeypatch):
    seen = {}

    def fake_runner(ticker, prompt, system_message, *, model, max_tokens, temperature):
        seen.update(model=model, max_tokens=max_tokens)
        return "ok"

    monkeypatch.setitem(llm._RUNNERS, "gemini", fake_runner)
    llm.call_llm("gemini", "AAPL", "p", "s")  # no model/max_tokens
    assert seen["model"] == "gemini-3.5-flash"
    assert seen["max_tokens"] == 20000


def test_unknown_provider_raises():
    with pytest.raises(LLMError):
        llm.call_llm("bogus", "AAPL", "p", "s")
