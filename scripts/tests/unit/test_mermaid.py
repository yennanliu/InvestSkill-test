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


# ── Object-literal series repair ────────────────────────────────────────────
# Reproduces the "Lexical error … Unrecognized text" GitHub rendering failure
# caused by LLM-hallucinated `line { name … data […] … }` blocks — real
# xychart-beta only supports a flat `line […]` / `bar […]` array.

OBJECT_LITERAL_LINES = """```mermaid
xychart-beta
    title "AAPL 利潤率趨勢 (%)"
    x-axis [2022, 2023, 2024, 2025, "TTM"]
    y-axis "利潤率 %" 0 --> 50
    line {
        name "毛利率"
        data [43.31, 44.13, 46.21, 46.91, 47.86]
        stroke-color "#3b82f6"
        stroke-width 2
    }
    line {
        name "營運利潤率"
        data [30.29, 29.82, 31.51, 31.97, 32.28]
        stroke-color "#f59e0b"
        stroke-width 2
    }
```"""


def test_flattens_object_literal_line_blocks():
    out = sanitize_mermaid(OBJECT_LITERAL_LINES)
    assert "line {" not in out
    assert "line [43.31, 44.13, 46.21, 46.91, 47.86]" in out
    assert "line [30.29, 29.82, 31.51, 31.97, 32.28]" in out


def test_appends_legend_caption_from_recovered_names():
    out = sanitize_mermaid(OBJECT_LITERAL_LINES)
    assert "*圖例：線 1: 毛利率 | 線 2: 營運利潤率*" in out


def test_object_literal_repair_is_idempotent():
    once = sanitize_mermaid(OBJECT_LITERAL_LINES)
    assert sanitize_mermaid(once) == once


def test_does_not_duplicate_existing_legend_caption():
    text = OBJECT_LITERAL_LINES + "\n*圖例：線 1: 毛利率 | 線 2: 營運利潤率*"
    out = sanitize_mermaid(text)
    assert out.count("圖例") == 1


def test_flattens_bar_block_with_nested_color_map():
    # Some hallucinations nest a per-category color object inside the series
    # block (e.g. `barColor { "06/18": "...", … }`) — the brace matcher must
    # skip over that nested `{...}` to find the series block's real end.
    text = """```mermaid
xychart-beta
    title "META 成交量"
    x-axis ["06/18", "06/22"]
    y-axis "百萬股" 0 --> 50
    bar {
        name "成交量"
        data [28.8, 15.4]
        barColor {
            "06/18": "rgba(16,185,129,0.6)",
            "06/22": "rgba(239,68,68,0.6)"
        }
    }
```"""
    out = sanitize_mermaid(text)
    assert "bar [28.8, 15.4]" in out
    assert "barColor" not in out
    assert "{" not in out.split("```mermaid")[1]


def test_drops_invalid_y2_axis_line():
    text = """```mermaid
xychart-beta
    title "AAPL 股價與成交量"
    x-axis ["06/18", "06/22"]
    y-axis "價格" 260 --> 320
    y2-axis "成交量" 0 --> 300
    line {
        name "股價"
        data [298.01, 297.01]
    }
```"""
    out = sanitize_mermaid(text)
    assert "y2-axis" not in out
    assert "line [298.01, 297.01]" in out


def test_series_block_without_data_is_dropped_not_left_broken():
    text = """```mermaid
xychart-beta
    title "空白系列"
    x-axis [2022, 2023]
    y-axis "USD" 0 --> 10
    line {
        name "沒有資料"
        stroke-color "#3b82f6"
    }
    bar [1, 2]
```"""
    out = sanitize_mermaid(text)
    assert "line {" not in out
    assert "沒有資料" not in out
    assert "bar [1, 2]" in out


def test_series_block_without_name_flattens_without_legend():
    text = """```mermaid
xychart-beta
    x-axis [2022, 2023]
    y-axis "USD" 0 --> 10
    line {
        data [1, 2]
    }
```"""
    out = sanitize_mermaid(text)
    assert "line [1, 2]" in out
    assert "圖例" not in out
