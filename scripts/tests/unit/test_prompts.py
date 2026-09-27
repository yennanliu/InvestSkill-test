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


def test_revision_none_outside_git(fake_invest_skill):
    # tmp_path lives outside any repo, so the fixture has no HEAD to report
    assert PromptRepo(fake_invest_skill).revision() is None


def test_revision_reads_git_head(fake_invest_skill):
    import shutil
    import subprocess
    if shutil.which("git") is None:
        pytest.skip("git not installed")
    run = lambda *a: subprocess.run(["git", "-C", str(fake_invest_skill), *a],  # noqa: E731
                                    check=True, capture_output=True, text=True)
    run("init", "-q")
    run("add", ".")
    run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")
    head = run("rev-parse", "HEAD").stdout.strip()
    assert PromptRepo(fake_invest_skill).revision() == head
