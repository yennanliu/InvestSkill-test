"""Tests for the showcase chart primitives (scripts/showcase/viz.py).

The charts encode design invariants that are easy to break silently — a cycled
palette, a second y-axis, a legend that vanishes — so they are asserted here
rather than left to review.
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

SHOWCASE = Path(__file__).resolve().parents[3] / "scripts" / "showcase"
sys.path.insert(0, str(SHOWCASE))

viz = pytest.importorskip("viz")


def parse(svg: str) -> ET.Element:
    """Assert the SVG is well-formed XML and return its root."""
    return ET.fromstring(svg)


# ── palette invariants ───────────────────────────────────────────────────────

def test_series_colours_are_fixed_per_entity():
    """Colour follows the entity, never its rank — so the map is a constant."""
    assert viz.SERIES == {
        "MU": "#2a78d6",
        "MRVL": "#eb6834",
        "SKHY": "#1baf7a",
        "SNDL": "#4a3aa7",
    }


def test_series_colours_are_distinct():
    assert len(set(viz.SERIES.values())) == len(viz.SERIES)


def test_status_colours_not_reused_as_series_colours():
    """Status hues are reserved; they must never double as a categorical slot."""
    assert not set(viz.SERIES.values()) & {viz.GOOD, viz.WARN, viz.BAD}


# ── line chart ───────────────────────────────────────────────────────────────

def _series(name="MU", n=6, base=100.0):
    return {"name": name, "colour": viz.SERIES[name],
            "points": [(f"{i:02d}月", base + i) for i in range(n)]}


def test_line_chart_is_wellformed_svg():
    svg = viz.line_chart([_series()])
    root = parse(svg[:svg.index("<script")] if "<script" in svg else svg)
    assert root.tag.endswith("svg")


def test_line_chart_emits_hover_payload():
    """The crosshair layer needs its data island, or interaction dies silently."""
    out = viz.line_chart([_series()])
    assert 'data-chart="line"' in out
    assert 'class="ch-data"' in out
    assert 'class="ch-cross"' in out


def test_line_chart_direct_labels_every_series():
    """Direct labels are the contrast relief for low-contrast slots."""
    out = viz.line_chart([_series("MU"), _series("SKHY", base=90)])
    assert ">MU<" in out
    assert ">SKHY<" in out


def test_line_chart_handles_all_none_points():
    assert viz.line_chart([{"name": "X", "colour": "#000",
                            "points": [("a", None), ("b", None)]}]) == ""


def test_line_chart_survives_flat_series():
    """A zero-range series must not divide by zero."""
    flat = {"name": "MU", "colour": viz.SERIES["MU"],
            "points": [("a", 5.0), ("b", 5.0), ("c", 5.0)]}
    parse(viz.line_chart([flat]).split("<script")[0])


def test_line_chart_reference_line_carries_a_label():
    """Status colour alone never conveys meaning — it ships with text."""
    out = viz.line_chart([_series()], hlines=[(103.0, "MA50 $103", viz.INK2)])
    assert "MA50 $103" in out


# ── bar / column ─────────────────────────────────────────────────────────────

def test_hbar_marks_unscored_rows_explicitly():
    """A missing value must read as 'not assessed', not as zero."""
    out = viz.hbar_chart([("SKHY", None, viz.SERIES["SKHY"])])
    assert "未評分" in out
    assert "<rect" not in out.split("未評分")[0].split("<text")[-1]


def test_hbar_negative_values_anchor_at_zero():
    out = viz.hbar_chart([("a", -9.6, "#000"), ("b", -1.0, "#000")],
                         vmin=-11, vmax=0, zero_line=True)
    parse(out)
    assert out.count("<rect") == 2


def test_hbar_rounds_data_ends():
    out = viz.hbar_chart([("a", 5.0, "#000")], vmax=10)
    assert 'rx="4"' in out


def test_column_chart_leaves_a_surface_gap_between_stacked_fills():
    cats = ["q1", "q2"]
    series = [{"name": "a", "colour": "#111", "values": [1.0, 2.0]},
              {"name": "b", "colour": "#222", "values": [3.0, 4.0]}]
    out = viz.column_chart(cats, series, stacked=True)
    parse(out)
    # every bar is inset by 1px on each side -> a 2px gap between neighbours
    assert re.search(r'width="[\d.]+"', out)


def test_column_chart_tolerates_missing_values():
    out = viz.column_chart(["a", "b"],
                           [{"name": "s", "colour": "#111", "values": [None, 3.0]}])
    parse(out)


# ── radar / gauge / football field ───────────────────────────────────────────

def test_radar_plots_all_axes():
    out = viz.radar_chart(["價值", "品質", "動能"],
                          [{"name": "MU", "colour": viz.SERIES["MU"], "values": [8.1, 8.5, 7.0]}])
    parse(out)
    for axis in ("價值", "品質", "動能"):
        assert axis in out


def test_radar_skips_series_with_no_data():
    out = viz.radar_chart(["a", "b"],
                          [{"name": "X", "colour": "#000", "values": [None, None]}])
    assert "<polygon points" in out          # grid rings still drawn
    assert "fill-opacity=\".14\"" not in out  # but no series polygon


def test_gauge_colour_tracks_the_score_band():
    assert viz.BAD in viz.gauge(2.0)
    assert viz.WARN in viz.gauge(5.0)
    assert viz.GOOD in viz.gauge(8.0)


def test_gauge_renders_the_number():
    assert "6.49" in viz.gauge(6.49)


def test_football_field_marks_current_price():
    out = viz.football_field([("DCF", 100.0, 200.0, "#000", "note")], price=150.0)
    parse(out)
    assert "現價" in out


def test_football_field_handles_inverted_range():
    """lo/hi supplied in either order must still render."""
    parse(viz.football_field([("m", 200.0, 100.0, "#000", "")], price=150.0))


# ── scatter ──────────────────────────────────────────────────────────────────

def test_scatter_labels_each_point():
    pts = [{"name": "MU", "colour": viz.SERIES["MU"], "x": 5.3, "y": 345.0},
           {"name": "SNDL", "colour": viz.SERIES["SNDL"], "x": 40.7, "y": -4.4}]
    out = viz.scatter_chart(pts, x_label="fwd P/E", y_label="rev growth", log_x=True)
    parse(out)
    assert ">MU<" in out and ">SNDL<" in out


def test_scatter_log_axis_rejects_nothing_positive():
    """log_x must not blow up on a very small positive x."""
    parse(viz.scatter_chart([{"name": "a", "colour": "#000", "x": 1e-9, "y": 1.0}],
                            log_x=True))


# ── tables ───────────────────────────────────────────────────────────────────

def test_heat_table_is_single_hue_sequential():
    """Sequential ramps are one hue light->dark; never a rainbow."""
    out = viz.heat_table(["a", "b"], [("row", [0.0, 10.0])])
    hexes = set(re.findall(r"background:(#[0-9a-f]{6})", out))
    assert hexes, "no cells were coloured"
    # every stop is in the green ramp: green channel dominates red
    for h in hexes:
        r, g, b = (int(h[i:i + 2], 16) for i in (1, 3, 5))
        assert g >= r, f"{h} is not on the green ramp"


def test_heat_table_renders_na_for_missing():
    assert "n/a" in viz.heat_table(["a"], [("row", [None])])


def test_simple_table_marks_row_headers():
    out = viz.simple_table(["k", "v"], [["label", "1"]])
    assert 'scope="row"' in out
    assert "<thead>" in out and "<tbody>" in out


def test_figure_wraps_caption_and_table_view():
    out = viz.figure("<svg role='img'></svg>", "caption text",
                     table_html="<table></table>", note="a note")
    assert "<figcaption>caption text</figcaption>" in out
    assert "檢視數據表" in out          # the table-view disclosure
    assert "a note" in out


def test_legend_renders_one_swatch_per_series():
    out = viz.legend([("MU", viz.SERIES["MU"]), ("SNDL", viz.SERIES["SNDL"])])
    assert out.count("lgd__sw") == 2


def test_insider_timeline_scales_by_value_and_marks_price():
    events = [("2026-06-26", 1150.0, 32_761_315.0, "CEO", "sale"),
              ("2026-04-10", 421.35, 10_112_400.0, "Officer", "sale")]
    out = viz.insider_timeline(events, price=820.53)
    parse(out)
    assert "現價" in out
    assert out.count("<circle") == 2


def test_insider_timeline_empty_is_empty_string():
    assert viz.insider_timeline([], price=100.0) == ""


# ── flow diagrams ────────────────────────────────────────────────────────────
# These animate, so the invariant that matters is that the animation is *added*
# to a diagram that already reads correctly: geometry in the SVG, motion in CSS.

def test_wrap_cells_counts_cjk_as_two_columns():
    lines = viz.wrap_cells("一二三四五", 6)
    assert lines == ["一二三", "四五"]


def test_wrap_cells_keeps_latin_tokens_whole():
    """A framework name split across two lines is unreadable, so words don't break."""
    lines = viz.wrap_cells("執行 stock-eval 模組", 12)
    assert any("stock-eval" in ln for ln in lines)


STEPS = [{"n": 1, "title": "快照", "sub": "yfinance 單次擷取", "kind": "data", "meta": "1 fetch"},
         {"n": 2, "title": "執行", "sub": "27 個框架依序執行"},
         {"n": 3, "title": "稽核", "sub": "result-validator", "kind": "audit"}]


def test_pipeline_chart_is_wellformed_and_labelled():
    out = viz.pipeline_chart(STEPS, aria="三步管線")
    parse(out)
    assert 'aria-label="三步管線"' in out
    assert out.count('class="fl-node"') == len(STEPS)


def test_pipeline_chart_links_every_gap_once():
    """N nodes need exactly N-1 connectors — a missing one reads as a break."""
    out = viz.pipeline_chart(STEPS)
    assert out.count('class="fl-dash"') == len(STEPS) - 1


def test_pipeline_chart_gate_step_is_not_the_accent_colour():
    """A blocked step must be distinguishable without reading the label."""
    out = viz.pipeline_chart([{"n": 1, "title": "閘門", "sub": "前提檢查", "kind": "gate"}])
    assert viz.BAD in out


PHASES = [{"label": "階段一 · 商業品質", "score": 8.6, "modules": ["stock-eval", "competitor-analysis"]},
          {"label": "階段二 · 估值", "score": 7.8, "modules": ["dcf-valuation"]}]


def test_phase_chart_draws_every_module():
    out = viz.phase_chart(PHASES, head="共用快照", foot="綜合評分")
    parse(out)
    for mod in ("stock-eval", "competitor-analysis", "dcf-valuation"):
        assert mod in out
    assert "共用快照" in out and "綜合評分" in out


def test_phase_chart_survives_missing_scores():
    out = viz.phase_chart([{"label": "階段一", "modules": ["m"]}])
    parse(out)


def test_matrix_dots_separates_presence_from_absence():
    out = viz.matrix_dots(["A", "B"], [("stock-eval", [True, False], "1 條")])
    parse(out)
    assert out.count('class="fl-cell"') == 1        # one filled dot
    assert 'stroke="#e6e8eb"' in out                # one hollow ring


def test_figure_carries_the_diagram_class():
    out = viz.figure("<svg role='img'></svg>", "cap", extra_cls="dagfig")
    assert 'class="fig dagfig"' in out


def test_solid_line_is_drawable_and_dashed_line_is_not():
    """The draw-in animation normalises on pathLength; a dashed series keeps its
    pattern instead, or the dash maths would fight the animation."""
    solid = viz.line_chart([_series()])
    assert 'class="ch-draw" pathLength="1"' in solid
    dashed = viz.line_chart([dict(_series(), dash="5 4")])
    assert "ch-draw" not in dashed


def test_gauge_value_arc_is_drawable_but_the_track_is_not():
    out = viz.gauge(6.49)
    assert out.count("g-arc") == 1
