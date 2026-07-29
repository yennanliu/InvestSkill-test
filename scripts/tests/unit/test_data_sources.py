"""Unit tests for the data layer (fetch_stock_data)."""

import sys

import pytest

from analysis.data.sources import fetch_stock_data
from analysis.exceptions import DataFetchError


def test_snapshot_contains_core_sections(fake_yfinance):
    md = fetch_stock_data("AAPL")
    assert "Live Financial Data for AAPL" in md
    assert "Apple Inc." in md
    assert "### Income Statement (TTM)" in md
    assert "### Balance Sheet" in md
    assert "### Short Interest & Ownership" in md


def test_snapshot_includes_price_action_and_history(fake_yfinance):
    md = fetch_stock_data("AAPL")
    assert "### Price Action (last 6 months)" in md
    assert "20-day MA" in md
    assert "### Historical Income Statement" in md
    assert "### Historical Cash Flow" in md


def test_net_debt_and_fcf_margin_computed(fake_yfinance):
    # totalDebt 100B - totalCash 60B = 40B net debt
    md = fetch_stock_data("AAPL")
    assert "Net Debt: $40,000,000,000" in md
    assert "FCF Margin:" in md


def test_missing_history_is_tolerated(fake_yfinance):
    fake_yfinance.with_history = False
    md = fetch_stock_data("AAPL")
    # price-action section skipped, but the snapshot still returns
    assert "Live Financial Data for AAPL" in md
    assert "### Price Action" not in md


def test_yfinance_missing_raises_datafetcherror(monkeypatch):
    # Force `import yfinance` to fail inside fetch_stock_data.
    monkeypatch.setitem(sys.modules, "yfinance", None)
    with pytest.raises(DataFetchError):
        fetch_stock_data("AAPL")
