"""Unit tests for provider-agnostic LLM helpers."""

from analysis.llm import base


def test_is_refusal_short_with_phrase():
    assert base.is_refusal("抱歉，我無法協助") is True
    assert base.is_refusal("I cannot help with that") is True


def test_is_refusal_long_text_is_not_refusal():
    # long text is treated as a real report even if it contains a phrase
    assert base.is_refusal("抱歉 " + "x" * 600) is False


def test_is_refusal_no_phrase():
    assert base.is_refusal("Here is your full report.") is False


def test_override_prefix_contains_ticker():
    assert "AAPL" in base.refusal_override_prefix("AAPL", 1)


def test_override_prefix_escalates():
    mild = base.refusal_override_prefix("AAPL", 1)
    strong = base.refusal_override_prefix("AAPL", 3)
    assert mild != strong
    assert "最高優先指令" in strong
    assert "第3次" in strong
