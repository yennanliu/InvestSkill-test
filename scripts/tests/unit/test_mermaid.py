"""Unit tests for the Mermaid xychart-beta sanitizer."""

from analysis.utils.mermaid import sanitize_mermaid

SWAPPED = """前言
```mermaid
xychart-beta horizontal
    title "UBER 估值指標"
    x-axis 0 --> 30
    y-axis ["P/E (TTM)", "EV/EBITDA"]
    bar [18.47, 22.64]
```
後記"""

FIXED = """前言
```mermaid
xychart-beta horizontal
    title "UBER 估值指標"
    x-axis ["P/E (TTM)", "EV/EBITDA"]
    y-axis 0 --> 30
    bar [18.47, 22.64]
```
後記"""

VALID = """```mermaid
xychart-beta
    x-axis [2022, 2023, "TTM"]
    y-axis "USD" 0 --> 60
    bar [1, 2, 3]
```"""


def test_swaps_band_off_value_axis():
    assert sanitize_mermaid(SWAPPED) == FIXED


def test_valid_chart_untouched():
    assert sanitize_mermaid(VALID) == VALID


def test_idempotent():
    once = sanitize_mermaid(SWAPPED)
    assert sanitize_mermaid(once) == once


def test_non_mermaid_untouched():
    text = "just some `code` and a [link](x) with x-axis words"
    assert sanitize_mermaid(text) == text


def test_multiple_blocks_only_broken_one_fixed():
    text = VALID + "\n\n" + SWAPPED
    out = sanitize_mermaid(text)
    assert VALID in out
    assert 'x-axis ["P/E (TTM)", "EV/EBITDA"]' in out
