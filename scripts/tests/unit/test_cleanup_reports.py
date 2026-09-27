"""Unit tests for scripts/cleanup_reports.py (report retention)."""

from datetime import date

import cleanup_reports as cr


def _touch(path, text="body"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_report_date_from_filename(tmp_path):
    for name, expected in [
        ("stock_eval_2026-08-01_gemini-3.6-flash.md", date(2026, 8, 1)),
        ("stock_eval_2026-04-21.md", date(2026, 4, 21)),
        ("full_report_2026-09-25_gemini-3.6-flash-2.md", date(2026, 9, 25)),
        ("AMD_report_2026-05-12.html", date(2026, 5, 12)),
        ("KTOS_基本面分析報告_2026-05-06.html", date(2026, 5, 6)),
    ]:
        assert cr.report_date(_touch(tmp_path / name)) == expected, name


def test_report_date_skips_impossible_dates(tmp_path):
    # 2026-13-40 is not a date; fall through to the frontmatter
    path = _touch(tmp_path / "x_2026-13-40.md", "---\ndate: 2026-07-01\n---\n\nbody")
    assert cr.report_date(path) == date(2026, 7, 1)


def test_report_date_from_frontmatter(tmp_path):
    path = _touch(tmp_path / "notes.md", '---\ntitle: "X"\ndate: "2026-06-02"\n---\n\nbody')
    assert cr.report_date(path) == date(2026, 6, 2)


def test_report_date_unknown(tmp_path):
    assert cr.report_date(_touch(tmp_path / "README.md", "no frontmatter")) is None
    # a date: line outside frontmatter does not count
    assert cr.report_date(_touch(tmp_path / "b.md", "text\ndate: 2026-01-01\n")) is None


def test_main_deletes_only_expired(tmp_path):
    root = tmp_path / "output"
    old = _touch(root / "stock_eval" / "aapl" / "stock_eval_2026-08-27_m.md")
    edge = _touch(root / "stock_eval" / "aapl" / "stock_eval_2026-08-28_m.md")
    new = _touch(root / "stock_eval" / "aapl" / "stock_eval_2026-09-25_m.md")
    undated = _touch(root / "stock_eval" / "aapl" / "notes.md")
    other = _touch(root / "stock_eval" / "aapl" / "data_2020-01-01.json")

    rc = cr.main(["--root", str(root), "--today", "2026-09-27", "--days", "30"])

    assert rc == 0
    assert not old.exists()
    assert edge.exists() and new.exists()      # cutoff day itself is kept
    assert undated.exists()                    # never guess an age
    assert other.exists()                      # only .md / .html are reports


def test_dry_run_deletes_nothing(tmp_path, capsys):
    root = tmp_path / "output"
    old = _touch(root / "dcf" / "t" / "dcf_2026-01-01_m.md")
    cr.main(["--root", str(root), "--today", "2026-09-27", "--dry-run"])
    assert old.exists()
    assert "Would delete 1 report(s)" in capsys.readouterr().out


def test_prunes_directories_left_empty(tmp_path):
    root = tmp_path / "InvestSkill_output"
    _touch(root / "AMD_report_2026-05-12.html")
    _touch(root / ".DS_Store", "")
    keep_root = tmp_path / "output"
    _touch(keep_root / "a" / "old" / "r_2026-01-01_m.md")
    fresh = _touch(keep_root / "a" / "new" / "r_2026-09-26_m.md")

    cr.main(["--root", str(root), "--root", str(keep_root), "--today", "2026-09-27"])

    assert not root.exists()                   # held only junk once the report went
    assert not (keep_root / "a" / "old").exists()
    assert fresh.exists()


def test_rejects_non_positive_window(tmp_path):
    import pytest
    with pytest.raises(SystemExit):
        cr.main(["--root", str(tmp_path), "--days", "0"])
