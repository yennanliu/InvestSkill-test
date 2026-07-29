"""End-to-end: the committed showcase HTML must match a fresh render.

This is the guarantee that makes the pages trustworthy — every figure they cite
is recomputed from ``fixtures/snapshot.json`` on each build, so committed HTML
that disagrees with the snapshot is a hard failure rather than a silent drift.

Marked ``integration`` because it renders all eight pages (a few seconds).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
BUILD = REPO / "scripts" / "showcase" / "build.py"
COMMITTED = REPO / "docs" / "showcase"

pytestmark = pytest.mark.integration


def test_build_script_exists():
    assert BUILD.is_file()


def test_committed_pages_match_a_fresh_render():
    """The check the CI job runs; failing means someone edited HTML by hand."""
    proc = subprocess.run([sys.executable, str(BUILD), "--check"],
                          capture_output=True, text=True, cwd=REPO)
    assert proc.returncode == 0, (
        "committed showcase HTML is stale — run "
        "`python scripts/showcase/build.py` and commit the result.\n\n"
        f"{proc.stdout}\n{proc.stderr}")


def test_render_is_deterministic(tmp_path):
    """Two renders of the same snapshot must be byte-identical."""
    first, second = tmp_path / "a", tmp_path / "b"
    for out in (first, second):
        proc = subprocess.run([sys.executable, str(BUILD), "--out", str(out)],
                              capture_output=True, text=True, cwd=REPO)
        assert proc.returncode == 0, proc.stderr
    names = sorted(p.name for p in first.glob("*.html"))
    assert names, "no pages were rendered"
    for name in names:
        assert (first / name).read_bytes() == (second / name).read_bytes(), name


def test_renders_the_expected_page_set(tmp_path):
    proc = subprocess.run([sys.executable, str(BUILD), "--out", str(tmp_path)],
                          capture_output=True, text=True, cwd=REPO)
    assert proc.returncode == 0, proc.stderr
    assert sorted(p.name for p in tmp_path.glob("*.html")) == [
        "index.html", "mrvl.html", "mu.html", "screener.html",
        "skhy.html", "sndl.html", "supply-chain.html", "workflows.html",
    ]


def test_check_detects_a_tampered_page(tmp_path):
    """Prove --check actually compares content rather than just listing files."""
    proc = subprocess.run([sys.executable, str(BUILD), "--out", str(tmp_path)],
                          capture_output=True, text=True, cwd=REPO)
    assert proc.returncode == 0, proc.stderr
    tampered = tmp_path / "index.html"
    tampered.write_text(tampered.read_text(encoding="utf-8").replace("</body>", "<p>x</p></body>"),
                        encoding="utf-8")
    proc = subprocess.run([sys.executable, str(BUILD), "--check", "--out", str(tmp_path)],
                          capture_output=True, text=True, cwd=REPO)
    assert proc.returncode == 1
    assert "STALE" in proc.stdout


def test_check_detects_an_orphaned_page(tmp_path):
    """A committed page that is no longer rendered should be reported."""
    proc = subprocess.run([sys.executable, str(BUILD), "--out", str(tmp_path)],
                          capture_output=True, text=True, cwd=REPO)
    assert proc.returncode == 0, proc.stderr
    (tmp_path / "stale-extra.html").write_text("<html></html>", encoding="utf-8")
    proc = subprocess.run([sys.executable, str(BUILD), "--check", "--out", str(tmp_path)],
                          capture_output=True, text=True, cwd=REPO)
    assert proc.returncode == 1
    assert "ORPHAN" in proc.stdout


def test_committed_docs_pass_the_html_validator():
    """The other half of the site gate, run over docs/ as CI does."""
    proc = subprocess.run([sys.executable, str(REPO / "scripts" / "validate_html.py"),
                           str(REPO / "docs"), "--quiet"],
                          capture_output=True, text=True, cwd=REPO)
    assert proc.returncode == 0, f"{proc.stdout}\n{proc.stderr}"
