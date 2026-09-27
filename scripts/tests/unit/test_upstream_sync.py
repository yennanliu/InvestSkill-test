"""Unit tests for scripts/upstream_sync.py (InvestSkill drift detection)."""

import json
import shutil
import subprocess

import pytest

import upstream_sync as us
from analysis import config

FULL_REPORT = """# Full Report

## Module Sets by Depth

### Quick (5 modules)

| # | Module | Focus |
|---|--------|-------|
| 1 | `stock-eval` | overview |
| 2 | `technical-analysis` | charts |

### Standard (10 modules — Quick + 5 more)

| # | Module | Focus |
|---|--------|-------|
| 3 | `sector-analysis` | rotation |

### Comprehensive (15 modules — Standard + 5 more)

| # | Module | Focus |
|---|--------|-------|
| 4 | `bear-case` | red team |

## Research Process

| 9 | `not-a-tier-row` | ignored after the section ends |
"""

LOCAL_TIERS = {
    "quick": ["stock-eval", "technical-analysis"],
    "standard": ["stock-eval", "technical-analysis", "sector-analysis"],
    "comprehensive": ["stock-eval", "technical-analysis", "sector-analysis", "bear-case"],
}


@pytest.fixture
def upstream(tmp_path):
    """A small InvestSkill checkout whose config matches LOCAL_* below."""
    root = tmp_path / "InvestSkill"
    (root / "prompts").mkdir(parents=True)
    (root / "GEMINI.md").write_text("ctx", encoding="utf-8")
    (root / "CLAUDE.md").write_text("ctx", encoding="utf-8")
    (root / "package.json").write_text(json.dumps({"version": "9.9.9"}), encoding="utf-8")
    (root / "prompts" / "full-report.md").write_text(FULL_REPORT, encoding="utf-8")
    for slug in ("stock-eval", "technical-analysis", "sector-analysis", "bear-case"):
        (root / "prompts" / f"{slug}.md").write_text(f"# {slug}", encoding="utf-8")
    (root / "prompts" / "dcf-valuation.md").write_text(
        "# DCF\n\n> **This skill has been merged into `stock-eval`.** Use it.", encoding="utf-8")
    return root


def _local_types(root):
    return {p.stem: {} for p in (root / "prompts").glob("*.md")}


def _compare(root, lock=None, **overrides):
    kw = dict(analysis_types=_local_types(root), depth_tiers=LOCAL_TIERS,
              aliases={"dcf-valuation": "stock-eval"})
    kw.update(overrides)
    return us.compare(root, lock or {}, **kw)


def test_parse_depth_tiers_is_cumulative_and_scoped():
    tiers = us.parse_depth_tiers(FULL_REPORT)
    assert tiers == LOCAL_TIERS


def test_parse_depth_tiers_reads_the_real_upstream_shape():
    # mirrors the upstream table row format: | 11 | `bear-case` | Focus |
    md = "### Quick (5 modules)\n\n| 11 | `stock-valuation` | DCF |\n"
    assert us.parse_depth_tiers(md) == {"quick": ["stock-valuation"]}


def test_detect_aliases_handles_merged_and_unified(upstream):
    (upstream / "prompts" / "research-bundle.md").write_text(
        "# RB\n\n> **This skill has been unified into `full-report`.**", encoding="utf-8")
    assert us.detect_aliases(upstream) == {"dcf-valuation": "stock-eval",
                                           "research-bundle": "full-report"}


def test_no_drift_when_config_matches(upstream):
    status = _compare(upstream)
    assert status["has_drift"] is False
    assert status["upstream"]["version"] == "9.9.9"


def test_new_and_removed_slugs_are_drift(upstream):
    local = _local_types(upstream)
    local["gone-skill"] = {}
    (upstream / "prompts" / "brand-new.md").write_text("# new", encoding="utf-8")
    status = _compare(upstream, analysis_types=local)
    assert status["drift"]["missing_slugs"] == ["brand-new"]
    assert status["drift"]["removed_slugs"] == ["gone-skill"]
    assert status["has_drift"] is True


def test_tier_mismatch_is_drift(upstream):
    local = dict(LOCAL_TIERS, quick=["stock-eval", "dcf-valuation"])
    status = _compare(upstream, depth_tiers=local)
    assert set(status["drift"]["tier_mismatch"]) == {"quick"}
    assert status["drift"]["tier_mismatch"]["quick"]["upstream"] == LOCAL_TIERS["quick"]


def test_new_alias_upstream_is_drift(upstream):
    status = _compare(upstream, aliases={})
    assert status["drift"]["alias_mismatch"] == {
        "dcf-valuation": {"local": None, "upstream": "stock-eval"}}


def test_missing_context_file_is_drift(upstream):
    (upstream / "CLAUDE.md").unlink()
    assert _compare(upstream)["drift"]["missing_context"] == ["CLAUDE.md"]


def test_file_changes_against_lock(upstream):
    lock = us.build_lock(upstream)
    assert _compare(upstream, lock)["changed"] is False

    (upstream / "prompts" / "bear-case.md").write_text("# bear-case v2", encoding="utf-8")
    (upstream / "prompts" / "sector-analysis.md").unlink()
    status = _compare(upstream, lock,
                      depth_tiers={}, analysis_types=_local_types(upstream))
    assert status["changed"] is True
    assert status["files"]["modified"] == ["prompts/bear-case.md"]
    assert status["files"]["removed"] == ["prompts/sector-analysis.md"]


@pytest.mark.skipif(shutil.which("git") is None, reason="git not installed")
def test_commit_log_since_lock(upstream):
    def git(*args):
        return subprocess.run(["git", "-C", str(upstream), "-c", "user.name=t",
                               "-c", "user.email=t@t", *args],
                              check=True, capture_output=True, text=True).stdout.strip()

    git("init", "-q")
    git("add", ".")
    git("commit", "-qm", "base")
    lock = us.build_lock(upstream)
    (upstream / "prompts" / "bear-case.md").write_text("# v2", encoding="utf-8")
    (upstream / "README.md").write_text("docs", encoding="utf-8")
    git("add", ".")
    git("commit", "-qm", "feat: sharpen bear-case")

    status = _compare(upstream, lock)
    assert status["changed"] is True
    assert [c["subject"] for c in status["commits"]] == ["feat: sharpen bear-case"]
    assert "prompts/bear-case.md" in status["commits"][0]["files"]
    report = us.render_markdown(status)
    assert "feat: sharpen bear-case 📝" in report
    assert "prompts/bear-case.md" in report


def test_unreachable_lock_commit_is_reported(upstream):
    status = _compare(upstream, {"commit": "0" * 40})
    # fixture is not a git repo: no HEAD, so nothing to compare commits against
    assert status["commits"] == []
    assert "None." in us.render_markdown(status)


def test_main_writes_lock_report_and_github_output(upstream, tmp_path, monkeypatch):
    lock, report, gh_out = tmp_path / "lock.json", tmp_path / "r.md", tmp_path / "gh"
    monkeypatch.setenv("GITHUB_OUTPUT", str(gh_out))
    rc = us.main(["--invest-skill-dir", str(upstream), "--lock", str(lock),
                  "--report", str(report), "--write-lock"])
    assert rc == 0
    assert json.loads(lock.read_text())["version"] == "9.9.9"
    assert report.read_text().startswith("## InvestSkill upstream sync")
    assert "changed=true" in gh_out.read_text()


def test_main_check_fails_on_drift(upstream, tmp_path):
    (upstream / "prompts" / "brand-new-skill.md").write_text("# new", encoding="utf-8")
    rc = us.main(["--invest-skill-dir", str(upstream), "--lock", str(tmp_path / "l.json"),
                  "--check"])
    assert rc == 1  # brand-new-skill is not in the real ANALYSIS_TYPES


def test_main_requires_a_clone(tmp_path):
    assert us.main(["--invest-skill-dir", str(tmp_path / "missing")]) == 2


def test_committed_lock_matches_config():
    """The lock and ANALYSIS_TYPES must move together.

    A sync PR that bumps the lock to a revision with a new or removed skill fails
    here until the config row is added — the drift cannot be merged unnoticed.
    """
    lock = json.loads(us.DEFAULT_LOCK.read_text(encoding="utf-8"))
    locked_slugs = {path[len("prompts/"):-len(".md")] for path in lock["files"]
                    if path.startswith("prompts/")}
    assert locked_slugs == set(config.ANALYSIS_TYPES)
    assert len(lock["commit"]) == 40
