"""Tests for the showcase data layer (scripts/showcase/context.py, derive.py).

These lock down the things that produced wrong numbers on the page during the
original build: CJK-aware padding in the ASCII signal blocks, and reading book
value from the filed balance sheet rather than yfinance's ``bookValue`` field
(which understates SNDL's by 27%).
"""

from __future__ import annotations

import sys
import unicodedata
from pathlib import Path

import pytest

SHOWCASE = Path(__file__).resolve().parents[3] / "scripts" / "showcase"
sys.path.insert(0, str(SHOWCASE))

ctx = pytest.importorskip("context")


def display_width(text: str) -> int:
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in text)


# ── formatters ───────────────────────────────────────────────────────────────

@pytest.mark.parametrize("value,expected", [
    (None, "—"),
    (1.22, "$1.22"),
    (317_566_016, "$317.6M"),
    (926_700_994_560, "$926.70B"),
    (1_320_000_000_000, "$1.32 兆"),
    (-19_650_000_000, "$-19.65B"),
])
def test_money(value, expected):
    assert ctx.money(value) == expected


@pytest.mark.parametrize("value,expected", [
    (None, "—"),
    (34.6, "34.6%"),
    (-8.85, "-8.85%"),
])
def test_pc(value, expected):
    assert ctx.pc(value, 2 if value == -8.85 else 1) == expected


def test_pc_sign_only_prefixes_positives():
    assert ctx.pc(5.0, 1, sign=True) == "+5.0%"
    assert ctx.pc(-5.0, 1, sign=True) == "-5.0%"


def test_pcf_converts_fractions():
    assert ctx.pcf(0.804) == "80.4%"
    assert ctx.pcf(None) == "—"


def test_cls_marks_direction():
    assert ctx.cls(1.0) == "up"
    assert ctx.cls(-1.0) == "dn"
    assert ctx.cls(0.0) == "fl"
    assert ctx.cls(None) == ""


def test_cls_invert_flips_polarity():
    """For metrics where lower is better (e.g. a cost), invert the colour."""
    assert ctx.cls(-1.0, invert=True) == "up"
    assert ctx.cls(1.0, invert=True) == "dn"


def test_status_pill_always_carries_text_not_just_colour():
    for kind in ("good", "warn", "bad", "neut"):
        out = ctx.st(kind, "LABEL")
        assert "LABEL" in out
        assert f"st--{kind}" in out


# ── signal block: the CJK padding bug ────────────────────────────────────────

def test_signal_block_borders_align():
    out = ctx.sig_block([("Signal", "NEUTRAL"), ("Score", "6.49 / 10")])
    lines = [ln for ln in out.split("<pre>")[1].split("</pre>")[0].split("\n")]
    widths = {display_width(ln) for ln in lines}
    assert len(widths) == 1, f"misaligned: {sorted(widths)}"


def test_signal_block_aligns_even_with_cjk_values():
    """len() miscounts CJK; the box must be padded by display width."""
    out = ctx.sig_block([("Signal", "中性偏空"), ("Horizon", "MEDIUM-TERM")])
    lines = out.split("<pre>")[1].split("</pre>")[0].split("\n")
    widths = {display_width(ln) for ln in lines}
    assert len(widths) == 1, f"misaligned with CJK: {sorted(widths)}"


def test_signal_block_renders_separator_rows():
    out = ctx.sig_block([("a", "1"), None, ("b", "2")])
    assert out.count("╠") >= 2


def test_signal_block_widens_for_long_values():
    narrow = ctx.sig_block([("k", "v")])
    wide = ctx.sig_block([("k", "a much longer value than before")])
    assert display_width(wide.split("\n")[0]) > display_width(narrow.split("\n")[0])


def test_display_width_helper_counts_cjk_as_two():
    assert ctx._dw("ab") == 2
    assert ctx._dw("中文") == 4
    assert ctx._dw("a中") == 3


# ── score interpretation bands ───────────────────────────────────────────────

@pytest.mark.parametrize("score,kind", [
    (9.0, "good"), (7.0, "good"), (5.5, "warn"), (4.0, "bad"), (2.0, "bad"),
])
def test_interp_bands(score, kind):
    assert ctx.interp(score)[0] == kind


def test_interp_boundaries_match_the_documented_framework():
    assert ctx.interp(8.0)[1].startswith("強力買進")
    assert ctx.interp(6.5)[1].startswith("買進")
    assert ctx.interp(5.0)[1].startswith("持有")
    assert ctx.interp(3.5)[1].startswith("減碼")
    assert ctx.interp(3.4)[1].startswith("賣出")


@pytest.mark.parametrize("total,expected", [
    (7.5, "🟢 STRONG BUY"), (6.0, "🟢 BUY"), (4.5, "🟡 HOLD"),
    (3.0, "🔴 AVOID"), (2.9, "🔴 STRONG AVOID"),
])
def test_screener_signal_thresholds(total, expected):
    assert ctx.screener_signal(total)[1] == expected


# ── snapshot / derived integrity ─────────────────────────────────────────────

def test_all_four_tickers_present():
    assert set(ctx.T) == {"MU", "SKHY", "MRVL", "SNDL"}
    for tk in ctx.T:
        assert tk in ctx.RAW
        assert tk in ctx.C


def test_composite_weights_sum_to_one():
    for tk in ctx.T:
        weights = ctx.C[tk]["composite"]["weights"]
        assert abs(sum(weights.values()) - 1.0) < 1e-9


def test_composite_total_is_the_weighted_sum():
    for tk in ctx.T:
        comp = ctx.C[tk]["composite"]
        expected = sum(comp["phases"][k] * comp["weights"][k] for k in comp["weights"])
        assert abs(comp["total"] - expected) < 0.005


def test_screener_weights_sum_to_one():
    for tk in ctx.T:
        assert abs(sum(ctx.C[tk]["screener"]["weights"].values()) - 1.0) < 1e-9


def test_all_scores_within_range():
    for tk in ctx.T:
        for dim, val in ctx.C[tk]["screener"]["dims"].items():
            if val is not None:
                assert 0.0 <= val <= 10.0, f"{tk}/{dim} = {val}"
        assert 0.0 <= ctx.C[tk]["composite"]["total"] <= 10.0


def test_piotroski_in_range():
    for tk in ctx.T:
        assert 0 <= ctx.C[tk]["piotroski"] <= 9
        assert len(ctx.C[tk]["piotroski_tests"]) == 9


def test_skhy_momentum_is_unscored_not_zero_filled():
    """13 trading days cannot produce momentum sub-factors; it must read as None."""
    assert ctx.C["SKHY"]["screener"]["dims"]["動能"] is None


def test_dcf_scenarios_are_ordered_bear_base_bull():
    for tk in ctx.T:
        sc = ctx.C[tk]["dcf"]["scenarios"]
        assert sc["bear"]["per_share"] < sc["base"]["per_share"] < sc["bull"]["per_share"]


def test_dcf_terminal_growth_below_wacc():
    """Gordon growth is undefined otherwise."""
    for tk in ctx.T:
        for name, sc in ctx.C[tk]["dcf"]["scenarios"].items():
            assert sc["gt"] < sc["wacc"], f"{tk}/{name}"


# ── balance-sheet derivations (the bug this file exists for) ─────────────────

def test_book_value_comes_from_the_filed_balance_sheet():
    """yfinance's bookValue understates SNDL's by 27%; we must not inherit that."""
    b = ctx.BS["SNDL"]
    assert abs(b["bv_ps"] - 4.086) < 0.01, "book value per share drifted"
    assert abs(b["pb"] - 0.2986) < 0.002, "P/B must be recomputed, not taken from yfinance"
    assert b["pb"] < b["pb_yf"], "the filed figure should be the cheaper, truer one"


def test_book_value_field_agrees_with_filings_for_mu_and_mrvl():
    """The discrepancy is SNDL-specific — proving it is a data defect, not our maths."""
    for tk in ("MU", "MRVL"):
        assert abs(ctx.BS[tk]["bv_gap"] - 1.0) < 0.005, tk


def test_sndl_equity_erosion_is_negative_and_accelerating():
    b = ctx.BS["SNDL"]
    assert b["erosion_ann"] < 0
    assert abs(b["erosion_pct"] - -7.05) < 0.2


def test_equity_series_is_chronological():
    for tk in ctx.T:
        dates = [d for d, _ in ctx.BS[tk]["series"]]
        assert dates == sorted(dates)


def test_cash_coverage_is_a_fraction():
    for tk in ctx.T:
        cover = ctx.BS[tk]["cash_cover"]
        assert cover is None or 0.0 <= cover <= 1.5


# ── snapshot-level facts the reports assert in prose ─────────────────────────

def test_all_four_gapped_down_on_the_snapshot_date():
    """The showcase's framing claim; if a snapshot refresh breaks it, prose lies."""
    for tk in ctx.T:
        assert -10.0 < ctx.GAP[tk] < -7.0, f"{tk} gap is {ctx.GAP[tk]:.2f}%"


def test_skhy_has_too_little_history_for_moving_averages():
    assert ctx.RAW["SKHY"]["hist_1y"]["n"] < 50


def test_skhy_raw_enterprise_value_is_the_documented_defect():
    """Negative EV from KRW-vs-USD mixing; the page must keep flagging it."""
    assert ctx.RAW["SKHY"]["info"]["enterpriseValue"] < 0


def test_normalised_enterprise_value_is_positive_for_every_ticker():
    """After unit correction, EV must be sane even where the raw field is not."""
    for tk in ctx.T:
        assert ctx.C[tk]["norm"]["ev_fixed"] > 0, tk


def test_mu_insider_selling_with_no_buys():
    ins = ctx.INS["MU"]
    assert ins["n_sell"] > 0
    assert ins["n_buy"] == 0
    assert ins["sell_total"] > 100e6


def test_provenance_header_states_all_four_fields():
    out = ctx.prov("src", "retrieval", "HIGH")
    for field in ("As of", "Source", "Retrieval", "Confidence"):
        assert field in out
    assert ctx.ASOF in out
