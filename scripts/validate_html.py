#!/usr/bin/env python3
"""Static checks for the generated site under docs/.

Deliberately dependency-free (stdlib only) so it runs anywhere the repo does.
It is not a spec-complete HTML validator; it checks the things that have actually
broken on this site: unbalanced tags, dead internal links and anchors, missing
head metadata, unrendered template artifacts, and accessibility basics.

Usage:
    python scripts/validate_html.py                 # check docs/
    python scripts/validate_html.py docs/showcase   # check one directory
    python scripts/validate_html.py --quiet         # only report problems
"""
from __future__ import annotations

import argparse
import html.parser
import re
import sys
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

# Elements with no closing tag. Includes SVG shapes, which appear inline
# throughout the generated charts.
VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
    "param", "source", "track", "wbr",
    # SVG leaf elements used by the chart generator
    "circle", "ellipse", "line", "path", "polygon", "polyline", "rect", "stop", "use",
}

# Template placeholders that must never reach the rendered page.
ARTIFACTS = [
    (re.compile(r"\{[a-zA-Z_][a-zA-Z0-9_]*\}"), "unrendered format placeholder"),
    (re.compile(r"\bNone\b"), "literal 'None' leaked from Python"),
    (re.compile(r"lambda"), "literal 'lambda' leaked from Python"),
    (re.compile(r"\[tk\]"), "unevaluated dict index"),
    (re.compile(r"\bnan\b(?![a-zA-Z])"), "NaN leaked into output"),
    (re.compile(r"Traceback \(most recent call last\)"), "Python traceback in output"),
]
# Substrings that legitimately contain an ARTIFACTS match; skipped before scanning.
ARTIFACT_ALLOW = ["yennanliu", "finance", "financial", "Financial", "nan-"]


class Balance(html.parser.HTMLParser):
    """Track tag nesting and report the first few imbalances."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, int]] = []
        self.errors: list[str] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag not in VOID:
            self.stack.append((tag, self.getpos()[0]))

    def handle_endtag(self, tag: str) -> None:
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"line {self.getpos()[0]}: stray </{tag}>")
            return
        top, opened = self.stack[-1]
        if top != tag:
            self.errors.append(
                f"line {self.getpos()[0]}: </{tag}> closes <{top}> opened at line {opened}")
            names = [t for t, _ in self.stack]
            if tag in names:
                while self.stack and self.stack.pop()[0] != tag:
                    pass
        else:
            self.stack.pop()


def display_width(text: str) -> int:
    """Monospace cell width; CJK and fullwidth glyphs occupy two."""
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in text)


class Report:
    def __init__(self) -> None:
        self.problems: list[str] = []
        self.notes: list[str] = []

    def fail(self, page: str, msg: str) -> None:
        self.problems.append(f"{page}: {msg}")

    def note(self, msg: str) -> None:
        self.notes.append(msg)


def check_structure(page: str, src: str, rep: Report) -> None:
    parser = Balance()
    parser.feed(src)
    for err in parser.errors[:5]:
        rep.fail(page, f"tag mismatch — {err}")
    unclosed = [f"<{t}> (line {ln})" for t, ln in parser.stack]
    if unclosed:
        rep.fail(page, f"unclosed tags: {', '.join(unclosed[:5])}")


def check_head(page: str, src: str, rep: Report) -> None:
    if not re.search(r'<html[^>]*\blang="[^"]+"', src):
        rep.fail(page, "<html> is missing a lang attribute")
    if not re.search(r"<title>[^<]+</title>", src):
        rep.fail(page, "missing or empty <title>")
    if not re.search(r'<meta\s+name="description"\s+content="[^"]+"', src):
        rep.fail(page, 'missing <meta name="description">')
    if not re.search(r'<meta\s+name="viewport"', src):
        rep.fail(page, "missing viewport meta")
    if not re.search(r'<meta\s+charset="utf-8"', src, re.I):
        rep.fail(page, "missing <meta charset>")


def check_accessibility(page: str, src: str, rep: Report) -> None:
    # every <img> needs alt text
    for tag in re.findall(r"<img\b[^>]*>", src):
        if "alt=" not in tag:
            rep.fail(page, f"<img> without alt: {tag[:70]}")
    # Decorative/meaningful svg must be labelled one way or the other. Inline SVG
    # inside a data: URI (the favicon) is markup-in-an-attribute, not a rendered
    # element, and an aria-hidden wrapper hides its children for us — so strip the
    # first and honour the second.
    scannable = re.sub(r"<link\b[^>]*>", "", src)
    scannable = re.sub(r'href="data:[^"]*"', 'href="data:"', scannable)
    for m in re.finditer(r"<svg\b[^>]*>", scannable):
        tag = m.group(0)
        if 'aria-hidden="true"' in tag or 'role="img"' in tag:
            continue
        # an aria-hidden ancestor immediately wrapping the svg is sufficient
        preceding = scannable[max(0, m.start() - 160):m.start()]
        if 'aria-hidden="true"' in preceding:
            continue
        rep.fail(page, f"<svg> lacks aria-hidden or role=img: {tag[:70]}")
    # heading order: never skip a level going down
    levels = [int(m.group(1)) for m in re.finditer(r"<h([1-6])\b", src)]
    prev = 0
    for lvl in levels:
        if prev and lvl > prev + 1:
            rep.fail(page, f"heading level jumps from h{prev} to h{lvl}")
            break
        prev = lvl
    if levels.count(1) != 1:
        rep.fail(page, f"expected exactly one <h1>, found {levels.count(1)}")
    # tables that carry data should have a header row
    for tbl in re.findall(r"<table\b.*?</table>", src, re.S):
        if "<th" not in tbl:
            rep.fail(page, "a <table> has no <th> header cells")
            break


def check_artifacts(page: str, src: str, rep: Report) -> None:
    text = src
    for allow in ARTIFACT_ALLOW:
        text = text.replace(allow, "")
    # ignore inline <script>/<style> — they legitimately contain braces and 'None'
    text = re.sub(r"<script\b.*?</script>", "", text, flags=re.S)
    text = re.sub(r"<style\b.*?</style>", "", text, flags=re.S)
    for pattern, label in ARTIFACTS:
        m = pattern.search(text)
        if m:
            start = max(0, m.start() - 50)
            rep.fail(page, f"{label}: …{text[start:m.end() + 30]!r}")


def check_signal_boxes(page: str, src: str, rep: Report) -> None:
    """The ASCII signal blocks must have flush borders (CJK is double-width)."""
    for block in re.findall(r'<div class="sig"><pre>(.*?)</pre>', src, re.S):
        widths = {display_width(line) for line in block.split("\n")}
        if len(widths) > 1:
            rep.fail(page, f"signal block borders misaligned (widths {sorted(widths)})")


def check_links(pages: dict[str, str], root: Path, rep: Report) -> None:
    ids = {name: set(re.findall(r'\bid="([^"]+)"', src)) for name, src in pages.items()}
    for name, src in pages.items():
        here = (root / name).parent
        for href in re.findall(r'href="([^"]+)"', src):
            if href.startswith(("http://", "https://", "mailto:", "data:", "tel:")):
                continue
            if href.startswith("#"):
                if href[1:] not in ids[name]:
                    rep.fail(name, f"dead anchor {href}")
                continue
            path, _, frag = href.partition("#")
            if not path:
                continue
            target = (here / path).resolve()
            if not target.exists():
                rep.fail(name, f"link target does not exist: {href}")
                continue
            try:
                key = str(target.relative_to(root))
            except ValueError:
                continue          # outside the checked tree (e.g. ../index.html)
            if frag and key in ids and frag not in ids[key]:
                rep.fail(name, f"dead fragment {href}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("target", nargs="?", default=str(REPO / "docs"),
                    help="directory to check (default: docs/)")
    ap.add_argument("--quiet", action="store_true", help="only print problems")
    args = ap.parse_args(argv)

    root = Path(args.target).resolve()
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2

    files = sorted(root.rglob("*.html"))
    if not files:
        print(f"no HTML files under {root}", file=sys.stderr)
        return 2

    pages = {str(p.relative_to(root)): p.read_text(encoding="utf-8") for p in files}
    rep = Report()

    for name, src in pages.items():
        check_structure(name, src, rep)
        check_head(name, src, rep)
        check_accessibility(name, src, rep)
        check_artifacts(name, src, rep)
        check_signal_boxes(name, src, rep)
    check_links(pages, root, rep)

    if not args.quiet:
        print(f"Validated {len(pages)} page(s) under {root.relative_to(REPO)}:")
        for name, src in pages.items():
            print(f"  {name:26s} {len(src):>8,} bytes  "
                  f"{src.count('<table'):>3} tables  {src.count('<svg'):>3} svg")

    if rep.problems:
        print(f"\n{len(rep.problems)} problem(s):", file=sys.stderr)
        for p in rep.problems:
            print(f"  ✗ {p}", file=sys.stderr)
        return 1

    print(f"\nAll {len(pages)} page(s) passed: structure, head metadata, "
          f"accessibility basics, internal links, no template artifacts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
