"""Unit tests for the prompt layer (PromptRepo)."""

import pytest

from analysis.exceptions import PromptError
from analysis.prompts import PromptRepo


def test_system_context_gemini(fake_invest_skill):
    repo = PromptRepo(fake_invest_skill)
    assert "GEMINI" in repo.system_context("gemini")


def test_system_context_claude(fake_invest_skill):
    repo = PromptRepo(fake_invest_skill)
    assert "CLAUDE" in repo.system_context("claude")


def test_system_context_openai_falls_back_to_gemini(fake_invest_skill):
    repo = PromptRepo(fake_invest_skill)
    # openai maps to GEMINI.md
    assert "GEMINI" in repo.system_context("openai")


def test_system_context_missing_provider_file_falls_back(fake_invest_skill):
    # remove CLAUDE.md → claude should fall back to GEMINI.md
    (fake_invest_skill / "CLAUDE.md").unlink()
    repo = PromptRepo(fake_invest_skill)
    assert "GEMINI" in repo.system_context("claude")


def test_system_context_missing_all_raises(tmp_path):
    (tmp_path / "prompts").mkdir()
    repo = PromptRepo(tmp_path)
    with pytest.raises(PromptError):
        repo.system_context("gemini")


def test_framework_loads(fake_invest_skill):
    repo = PromptRepo(fake_invest_skill)
    text = repo.framework("dcf-valuation")
    assert "dcf-valuation framework" in text


def test_framework_missing_raises(fake_invest_skill):
    repo = PromptRepo(fake_invest_skill)
    with pytest.raises(PromptError):
        repo.framework("does-not-exist")


def test_available(fake_invest_skill):
    repo = PromptRepo(fake_invest_skill)
    assert repo.available("dcf-valuation") is True
    assert repo.available("nope") is False


def test_read_is_cached(fake_invest_skill):
    repo = PromptRepo(fake_invest_skill)
    first = repo.framework("stock-eval")
    # mutate file on disk; cached value should be returned unchanged
    (fake_invest_skill / "prompts" / "stock-eval.md").write_text("CHANGED", encoding="utf-8")
    assert repo.framework("stock-eval") == first
