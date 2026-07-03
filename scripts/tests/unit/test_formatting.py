"""Unit tests for the formatting helpers."""

import pytest

from analysis.utils.formatting import fmt, hist_table


def test_fmt_none():
    assert fmt(None) == "N/A"
    assert fmt(None, "$") == "N/A"


def test_fmt_int_thousands():
    assert fmt(1234567) == "1,234,567"
    assert fmt(1000, "$") == "$1,000"


def test_fmt_float_two_decimals():
    assert fmt(3.14159) == "3.14"
    assert fmt(1234.5, "$") == "$1,234.50"


def test_fmt_bool_before_int():
    # bool is an int subclass; must not render as 1/0 with a prefix
    assert fmt(True) == "True"
    assert fmt(False) == "False"


def test_fmt_str_passthrough():
    assert fmt("hello") == "hello"
    assert fmt("x", "$") == "x"  # prefix only applies to numbers


def test_hist_table_none_and_empty():
    pd = pytest.importorskip("pandas")
    assert hist_table(None, "H", ["a"]) == []
    assert hist_table(pd.DataFrame(), "H", ["a"]) == []


def test_hist_table_renders_rows_and_caps_columns():
    pd = pytest.importorskip("pandas")
    cols = pd.DatetimeIndex(["2024-12-31", "2023-12-31", "2022-12-31",
                             "2021-12-31", "2020-12-31"])  # 5 → capped to 4
    df = pd.DataFrame({c: [10.0, 20.0] for c in cols}, index=["Total Revenue", "Net Income"])
    out = hist_table(df, "### Income", ["Total Revenue", "Missing Row", "Net Income"])

    assert out[0] == "### Income"
    # header has 4 year columns, not 5
    assert out[1].count("|") == 6  # | Metric | y1 | y2 | y3 | y4 |
    assert "2024" in out[1] and "2020" not in out[1]
    # present rows rendered, missing row skipped
    body = "\n".join(out)
    assert "| Total Revenue |" in body
    assert "| Net Income |" in body
    assert "Missing Row" not in body
    assert out[-1] == ""  # trailing blank line
