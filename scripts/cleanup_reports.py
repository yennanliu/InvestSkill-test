#!/usr/bin/env python3
"""
cleanup_reports.py — delete generated reports older than a retention window.

A report's age is its *generation date*, read from the filename
(``stock_eval_2026-08-01_gemini-3.6-flash.md``, ``AMD_report_2026-05-12.html``)
and, failing that, from a ``date:`` line in its YAML frontmatter. File mtimes are
never used: a fresh checkout stamps every file with the clone time. A file with
no readable date is kept, not guessed at.

Deleted reports stay recoverable from git history; the ``cleanup_reports.yml``
workflow commits the deletions to main.

Usage:
  python scripts/cleanup_reports.py                 # delete reports > 30 days old
  python scripts/cleanup_reports.py --dry-run       # list what would be deleted
  python scripts/cleanup_reports.py --days 60 --root output
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROOTS = ("output", "InvestSkill_output")
DEFAULT_DAYS = 30
REPORT_SUFFIXES = {".md", ".html"}

_NAME_DATE = re.compile(r"(?<!\d)(\d{4}-\d{2}-\d{2})(?!\d)")
_FRONTMATTER_DATE = re.compile(r'^date:\s*"?(\d{4}-\d{2}-\d{2})"?\s*$', re.MULTILINE)
# OS clutter that should not keep an otherwise-empty report directory alive.
_JUNK = {".DS_Store", "Thumbs.db"}


def report_date(path: Path) -> date | None:
    """The generation date of a report, or None when it cannot be determined."""
    for candidate in _NAME_DATE.findall(path.name):
        try:
            return date.fromisoformat(candidate)
        except ValueError:
            continue
    if path.suffix == ".md":
        try:
            head = path.read_text(encoding="utf-8", errors="replace")[:2000]
        except OSError:
            return None
        if head.startswith("---"):
            match = _FRONTMATTER_DATE.search(head)
            if match:
                try:
                    return date.fromisoformat(match.group(1))
                except ValueError:
                    return None
    return None


def find_expired(roots: list[Path], cutoff: date) -> tuple[list[tuple[Path, date]], list[Path]]:
    """Split report files under ``roots`` into (expired, undated)."""
    expired, undated = [], []
    for root in roots:
        if not root.is_dir():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix not in REPORT_SUFFIXES:
                continue
            generated = report_date(path)
            if generated is None:
                undated.append(path)
            elif generated < cutoff:
                expired.append((path, generated))
    return expired, undated


def prune_empty_dirs(root: Path) -> list[Path]:
    """Remove directories (``root`` included) left holding only OS clutter; return them."""
    removed = []
    subdirs = sorted((p for p in root.rglob("*") if p.is_dir()),
                     key=lambda p: len(p.parts), reverse=True)
    for directory in [*subdirs, root]:
        entries = list(directory.iterdir())
        if all(e.is_file() and e.name in _JUNK for e in entries):
            for junk in entries:
                junk.unlink()
            directory.rmdir()
            removed.append(directory)
    return removed


def _display(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT)) if path.is_relative_to(REPO_ROOT) else str(path)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Delete generated reports older than N days.")
    ap.add_argument("--days", type=int, default=DEFAULT_DAYS,
                    help=f"Retention window in days (default: {DEFAULT_DAYS})")
    ap.add_argument("--root", action="append", dest="roots",
                    help=f"Report directory, repeatable (default: {', '.join(DEFAULT_ROOTS)})")
    ap.add_argument("--today", type=date.fromisoformat, default=None,
                    help="Reference date, YYYY-MM-DD (default: today)")
    ap.add_argument("--dry-run", action="store_true", help="List deletions without deleting")
    args = ap.parse_args(argv)

    if args.days < 1:
        ap.error("--days must be at least 1")
    today = args.today or date.today()
    cutoff = today - timedelta(days=args.days)
    roots = [Path(r) if Path(r).is_absolute() else REPO_ROOT / r
             for r in (args.roots or DEFAULT_ROOTS)]

    expired, undated = find_expired(roots, cutoff)
    verb = "Would delete" if args.dry_run else "Deleting"
    print(f"{verb} {len(expired)} report(s) generated before {cutoff} "
          f"({args.days}-day window ending {today}).")
    for path, generated in expired:
        print(f"  {generated}  {_display(path)}")
        if not args.dry_run:
            path.unlink()
    if undated:
        print(f"Kept {len(undated)} report(s) with no readable date:")
        for path in undated:
            print(f"  {_display(path)}")

    if not args.dry_run:
        for root in roots:
            if root.is_dir():
                for directory in prune_empty_dirs(root):
                    print(f"  pruned empty directory {_display(directory)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
