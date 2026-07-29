#!/usr/bin/env python3
"""Render the zh-TW showcase pages from the committed yfinance snapshot.

Every figure on every page is derived from ``fixtures/snapshot.json`` — there is
no network access and no hidden state, so a given snapshot always produces
byte-identical HTML. That property is what CI checks: ``--check`` rebuilds into a
temporary directory and diffs against the committed pages, so a page can never
quietly disagree with the data it cites.

Usage:
    python scripts/showcase/build.py                     # write to docs/showcase
    python scripts/showcase/build.py --out /tmp/out       # write elsewhere
    python scripts/showcase/build.py --check              # verify, write nothing
"""
from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))          # flat module layout: context, viz, shell, pages

REPO = HERE.parents[1]
DEFAULT_OUT = REPO / "docs" / "showcase"

TICKERS = ["MU", "SKHY", "MRVL", "SNDL"]


def render() -> dict[str, str]:
    """Return {filename: html} for every showcase page."""
    import page_chain
    import page_hub
    import page_screener
    import page_stock
    import page_workflows

    pages = {
        "index.html": page_hub.build(),
        "screener.html": page_screener.build(),
        "workflows.html": page_workflows.build(),
        "supply-chain.html": page_chain.build(),
    }
    for tk in TICKERS:
        pages[f"{tk.lower()}.html"] = page_stock.build(tk)
    return pages


def write(pages: dict[str, str], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for name, html in sorted(pages.items()):
        (out / name).write_text(html, encoding="utf-8")
        print(f"  wrote {name} ({len(html):,} bytes)")


def check(pages: dict[str, str], committed: Path) -> int:
    """Diff freshly rendered pages against what is committed. Returns exit code."""
    problems = 0
    for name, html in sorted(pages.items()):
        target = committed / name
        if not target.exists():
            print(f"  MISSING  {name} — rendered but not committed")
            problems += 1
            continue
        on_disk = target.read_text(encoding="utf-8")
        if on_disk == html:
            print(f"  ok       {name}")
            continue
        problems += 1
        print(f"  STALE    {name} — committed HTML differs from a fresh render")
        diff = difflib.unified_diff(
            on_disk.splitlines(), html.splitlines(),
            fromfile=f"committed/{name}", tofile=f"rendered/{name}", lineterm="", n=1)
        for line in list(diff)[:40]:
            print(f"      {line}")
    extra = {p.name for p in committed.glob("*.html")} - set(pages)
    for name in sorted(extra):
        print(f"  ORPHAN   {name} — committed but no longer rendered")
        problems += 1
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT,
                    help="output directory (default: docs/showcase)")
    ap.add_argument("--check", action="store_true",
                    help="verify committed pages match a fresh render; write nothing")
    args = ap.parse_args(argv)

    print(f"Rendering {len(TICKERS) + 4} showcase pages from "
          f"{Path('fixtures/snapshot.json')} …")
    pages = render()

    if args.check:
        print(f"\nChecking against {args.out.relative_to(REPO) if args.out.is_relative_to(REPO) else args.out}:")
        problems = check(pages, args.out)
        if problems:
            print(f"\n{problems} page(s) out of date. Run:\n"
                  f"    python scripts/showcase/build.py\n"
                  f"and commit the result.")
            return 1
        print(f"\nAll {len(pages)} pages match the committed HTML.")
        return 0

    print(f"\nWriting to {args.out}:")
    write(pages, args.out)
    print(f"\n{len(pages)} pages written.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
