"""Tests for scripts/validate_html.py.

A checker that only ever passes is worthless, so each test feeds it a specific
defect and asserts it is caught — and the last group asserts the shapes that
legitimately appear on this site are *not* flagged.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(SCRIPTS))

vh = pytest.importorskip("validate_html")

GOOD_HEAD = (
    '<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width, initial-scale=1">'
    "<title>T</title><meta name=\"description\" content=\"d\"></head><body>"
)


def page(body: str, head: str = GOOD_HEAD) -> str:
    return f"{head}<h1>Title</h1>{body}</body></html>"


def run(tmp_path: Path, files: dict[str, str]) -> int:
    for name, src in files.items():
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(src, encoding="utf-8")
    return vh.main([str(tmp_path), "--quiet"])


# ── structure ────────────────────────────────────────────────────────────────

def test_accepts_a_clean_page(tmp_path):
    assert run(tmp_path, {"a.html": page("<p>fine</p>")}) == 0


def test_catches_unclosed_tag(tmp_path):
    assert run(tmp_path, {"a.html": page("<div><p>oops</p>")}) == 1


def test_catches_crossed_tags(tmp_path):
    assert run(tmp_path, {"a.html": page("<div><span>x</div></span>")}) == 1


def test_void_elements_need_no_closing_tag(tmp_path):
    body = '<p>x<br><img src="i.png" alt="a"><hr></p>'
    assert run(tmp_path, {"a.html": page(body)}) == 0


def test_svg_leaf_elements_are_treated_as_void(tmp_path):
    """The chart generator emits self-closing SVG shapes."""
    body = ('<svg role="img"><rect x="0" y="0" width="1" height="1"/>'
            '<circle cx="1" cy="1" r="1"/><path d="M0,0"/></svg>')
    assert run(tmp_path, {"a.html": page(body)}) == 0


# ── head metadata ────────────────────────────────────────────────────────────

@pytest.mark.parametrize("head", [
    '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="w">'
    '<title>T</title><meta name="description" content="d"></head><body>',           # no lang
    '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    '<meta name="viewport" content="w"><meta name="description" content="d"></head><body>',  # no title
    '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    '<meta name="viewport" content="w"><title>T</title></head><body>',              # no description
    '<!doctype html><html lang="en"><head><meta charset="utf-8"><title>T</title>'
    '<meta name="description" content="d"></head><body>',                          # no viewport
    '<!doctype html><html lang="en"><head><meta name="viewport" content="w">'
    '<title>T</title><meta name="description" content="d"></head><body>',           # no charset
])
def test_catches_missing_head_metadata(tmp_path, head):
    assert run(tmp_path, {"a.html": page("<p>x</p>", head=head)}) == 1


# ── accessibility ────────────────────────────────────────────────────────────

def test_catches_img_without_alt(tmp_path):
    assert run(tmp_path, {"a.html": page('<img src="i.png">')}) == 1


def test_catches_unlabelled_svg(tmp_path):
    assert run(tmp_path, {"a.html": page("<svg></svg>")}) == 1


def test_accepts_svg_hidden_by_a_wrapper(tmp_path):
    """The homepage pattern: aria-hidden on the wrapping span."""
    body = '<span class="icon" aria-hidden="true"><svg width="24"></svg></span>'
    assert run(tmp_path, {"a.html": page(body)}) == 0


def test_accepts_favicon_svg_inside_a_data_uri(tmp_path):
    head = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="w"><title>T</title>'
        '<meta name="description" content="d">'
        '<link rel="icon" href="data:image/svg+xml,<svg xmlns=\'x\'><rect/></svg>">'
        "</head><body>"
    )
    assert run(tmp_path, {"a.html": page("<p>x</p>", head=head)}) == 0


def test_catches_skipped_heading_level(tmp_path):
    assert run(tmp_path, {"a.html": page("<h2>a</h2><h4>b</h4>")}) == 1


def test_accepts_descending_then_ascending_headings(tmp_path):
    body = "<h2>a</h2><h3>b</h3><h2>c</h2><h3>d</h3>"
    assert run(tmp_path, {"a.html": page(body)}) == 0


def test_catches_multiple_h1(tmp_path):
    assert run(tmp_path, {"a.html": page("<h1>second</h1>")}) == 1


def test_catches_table_without_header_cells(tmp_path):
    assert run(tmp_path, {"a.html": page("<table><tr><td>1</td></tr></table>")}) == 1


def test_accepts_table_with_header_cells(tmp_path):
    body = "<table><thead><tr><th>k</th></tr></thead><tbody><tr><td>1</td></tr></tbody></table>"
    assert run(tmp_path, {"a.html": page(body)}) == 0


# ── template artifacts ───────────────────────────────────────────────────────

def test_catches_unrendered_placeholder(tmp_path):
    assert run(tmp_path, {"a.html": page("<p>score {total}</p>")}) == 1


def test_catches_leaked_none(tmp_path):
    assert run(tmp_path, {"a.html": page("<p>value None</p>")}) == 1


def test_catches_leaked_nan(tmp_path):
    assert run(tmp_path, {"a.html": page("<p>RSI nan</p>")}) == 1


def test_catches_unevaluated_dict_index(tmp_path):
    assert run(tmp_path, {"a.html": page("<p>x[tk]</p>")}) == 1


def test_allows_none_and_braces_inside_script_and_style(tmp_path):
    """Inline JS/CSS legitimately contain braces and the word None."""
    body = "<style>.a{color:red}</style><script>var x={a:1};/*None*/</script><p>ok</p>"
    assert run(tmp_path, {"a.html": page(body)}) == 0


def test_allows_words_that_merely_contain_nan(tmp_path):
    """'finance' and 'yennanliu' must not trip the NaN check."""
    body = '<p>yfinance data from <a href="https://github.com/yennanliu/x">repo</a></p>'
    assert run(tmp_path, {"a.html": page(body)}) == 0


# ── signal blocks ────────────────────────────────────────────────────────────

def test_catches_misaligned_signal_block(tmp_path):
    body = '<div class="sig"><pre>╔════╗\n║ x ║\n╚════╝</pre></div>'
    assert run(tmp_path, {"a.html": page(body)}) == 1


def test_accepts_aligned_signal_block(tmp_path):
    body = '<div class="sig"><pre>╔══╗\n║ab║\n╚══╝</pre></div>'
    assert run(tmp_path, {"a.html": page(body)}) == 0


def test_accepts_aligned_signal_block_with_cjk(tmp_path):
    """Two CJK glyphs occupy four cells, so this box is flush."""
    body = '<div class="sig"><pre>╔════╗\n║中文║\n╚════╝</pre></div>'
    assert run(tmp_path, {"a.html": page(body)}) == 0


# ── links ────────────────────────────────────────────────────────────────────

def test_catches_dead_anchor(tmp_path):
    assert run(tmp_path, {"a.html": page('<a href="#nope">x</a>')}) == 1


def test_accepts_live_anchor(tmp_path):
    assert run(tmp_path, {"a.html": page('<div id="yes"></div><a href="#yes">x</a>')}) == 0


def test_catches_missing_link_target(tmp_path):
    assert run(tmp_path, {"a.html": page('<a href="gone.html">x</a>')}) == 1


def test_accepts_existing_link_target(tmp_path):
    files = {"a.html": page('<a href="b.html">x</a>'), "b.html": page("<p>b</p>")}
    assert run(tmp_path, files) == 0


def test_catches_dead_fragment_in_another_page(tmp_path):
    files = {"a.html": page('<a href="b.html#nope">x</a>'), "b.html": page("<p>b</p>")}
    assert run(tmp_path, files) == 1


def test_accepts_live_fragment_in_another_page(tmp_path):
    files = {"a.html": page('<a href="b.html#sec">x</a>'),
             "b.html": page('<div id="sec"></div>')}
    assert run(tmp_path, files) == 0


def test_ignores_external_and_mailto_links(tmp_path):
    body = ('<a href="https://example.com">a</a><a href="mailto:x@y.z">b</a>'
            '<a href="tel:+1">c</a>')
    assert run(tmp_path, {"a.html": page(body)}) == 0


def test_resolves_links_relative_to_the_page_not_the_root(tmp_path):
    files = {"sub/a.html": page('<a href="b.html">x</a>'), "sub/b.html": page("<p>b</p>")}
    assert run(tmp_path, files) == 0


# ── CLI behaviour ────────────────────────────────────────────────────────────

def test_missing_directory_returns_2(tmp_path):
    assert vh.main([str(tmp_path / "nope"), "--quiet"]) == 2


def test_directory_without_html_returns_2(tmp_path):
    (tmp_path / "readme.txt").write_text("hi")
    assert vh.main([str(tmp_path), "--quiet"]) == 2


def test_display_width_counts_cjk_as_two():
    assert vh.display_width("ab") == 2
    assert vh.display_width("中文") == 4
