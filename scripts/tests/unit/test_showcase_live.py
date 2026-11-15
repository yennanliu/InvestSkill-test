"""Live showcase: the picker, the Markdown converter, signal parsing, and the pages."""
from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts"))

import validate_html  # noqa: E402
from showcase_live import mdhtml, runner, site  # noqa: E402
from showcase_live.universe import ETF_SKILLS, UNIVERSE, pick  # noqa: E402


# ── universe / picker ───────────────────────────────────────────────────────
def test_universe_is_the_32_requested_tickers_without_duplicates():
    assert len(UNIVERSE) == 32
    assert len(set(UNIVERSE)) == 32
    for ticker in ("SPCX", "MU", "SKHY", "UBER", "TSLA", "NVDA", "ORCL", "VTI"):
        assert ticker in UNIVERSE


def test_pick_avoids_the_most_recent_half():
    recent = list(UNIVERSE[:16])
    for seed in range(40):
        assert pick(recent, rng=random.Random(seed)) in UNIVERSE[16:]


def test_pick_ignores_tickers_outside_the_universe_and_duplicates():
    recent = ["ZZZZ", "MU", "MU", "mu"]
    for seed in range(40):
        choice = pick(recent, rng=random.Random(seed))
        assert choice in UNIVERSE and choice != "MU"


def test_pick_covers_the_whole_universe_over_time():
    recent: list[str] = []
    rng = random.Random(7)
    for _ in range(len(UNIVERSE) * 3):
        recent.insert(0, pick(recent, rng=rng))
    assert set(recent) == set(UNIVERSE)


# ── markdown ────────────────────────────────────────────────────────────────
def test_markup_in_the_source_is_escaped():
    out = mdhtml.convert('<script>alert(1)</script> and <img src=x onerror=y> & "q"')
    assert "<script" not in out and "<img" not in out
    assert "&lt;script&gt;" in out and "&amp;" in out


def test_only_http_links_become_anchors():
    out = mdhtml.convert("[ok](https://example.com/a) [bad](javascript:alert(1)) [rel](../x.html)")
    assert out.count("<a ") == 1 and 'href="https://example.com/a"' in out
    assert "javascript:" not in out.replace("[bad](javascript:alert(1))", "")


def test_headings_never_skip_a_level_under_h2():
    out = mdhtml.convert("#### deep first\n\n# top\n\n##### deeper\n\n## second")
    assert [int(c) for c in __import__("re").findall(r"<h(\d)", out)] == [3, 3, 4, 3]


def test_table_has_header_cells_and_pads_short_rows():
    out = mdhtml.convert("| A | B |\n|---|---|\n| 1 | 2 |\n| only |\n")
    assert out.count("<th ") == 2 and out.count("<tr>") == 3
    assert out.count("<td ") == 4


def test_nested_and_mixed_lists_stay_balanced():
    out = mdhtml.convert("- a\n  - b\n  - c\n- d\n1. e\n    - f\n")
    for tag in ("ul", "ol", "li"):
        assert out.count(f"<{tag}>") == out.count(f"</{tag}>")
    assert out.startswith("<ul><li>a<ul><li>b</li><li>c</li></ul></li><li>d</li></ul><ol>")


def test_code_fence_is_literal_and_an_unclosed_fence_does_not_swallow_tags():
    out = mdhtml.convert("```json\n{\"a\": \"<b>\"}\n```\n\ntext\n\n```\nopen")
    assert "&lt;b&gt;" in out and out.count("<pre") == out.count("</pre>") == 2


def test_inline_formatting():
    out = mdhtml.inline("**bold** and *it* and `a*b*c` and 5 * 3 * 2")
    assert "<strong>bold</strong>" in out and "<em>it</em>" in out
    assert "<code>a*b*c</code>" in out and "5 * 3 * 2" in out


# ── signals ─────────────────────────────────────────────────────────────────
FOOTER = ('{"investskill": "1", "skill": "stock-eval", "ticker": "MU", "signal": "BULLISH", '
          '"confidence": "MEDIUM", "score": 6.8, "action": "HOLD"}')


def test_signal_from_the_json_footer():
    got = site.parse_signal("text\n```json\n" + FOOTER + "\n```\n")
    assert got == {"signal": "BULLISH", "action": "HOLD", "confidence": "MEDIUM",
                   "score": 6.8, "source": "json"}


def test_signal_from_the_box_when_there_is_no_footer():
    got = site.parse_signal("║ Signal:      BEARISH ║\n║ Score:       3.5 / 10 ║\n║ Action: SELL ║")
    assert got["signal"] == "BEARISH" and got["score"] == 3.5 and got["source"] == "box"


def test_no_signal_is_empty_not_neutral():
    assert site.parse_signal("評分 7/10 看多") == {}
    assert site.parse_signal('{"investskill": "1", "score": 55}') == {}


def test_failed_module_is_recorded_without_a_score():
    rec = site.module_record("bear-case", "空頭觀點", "_模組生成失敗：timeout_")
    assert rec == {"slug": "bear-case", "label": "空頭觀點", "status": "failed"}


def test_mean_score_uses_only_modules_that_reported_one():
    mods = [{"status": "ok", "score": 8.0}, {"status": "ok"}, {"status": "failed"},
            {"status": "ok", "score": 6.0}]
    assert site.mean_score(mods) == (7.0, 2)
    assert site.mean_score([{"status": "failed"}]) == (None, 0)


# ── pages ───────────────────────────────────────────────────────────────────
def _run(**over):
    sections = [("綜合股票評估", "## 分析\n\n內容 {CF} None\n\n```json\n" + FOOTER + "\n```"),
                ("空頭觀點", "_模組生成失敗：boom_")]
    run = runner.build_run(
        "MU", kind="stock", name="Micron Technology", mode="full-report · depth quick",
        requested=["stock-eval", "bear-case", "made-up-skill"], ran=["stock-eval", "bear-case"],
        sections=sections, synthesis="整體結論。", provider="gemini", model="gemini-test",
        date="2026-11-16", version="1.15.0", commit="35d68f92c0cb", source_md="output/x.md")
    run.update(over)
    return run, sections


def _validate(pages: dict[str, str]) -> list[str]:
    rep = validate_html.Report()
    for name, src in pages.items():
        validate_html.check_structure(name, src, rep)
        validate_html.check_head(name, src, rep)
        validate_html.check_accessibility(name, src, rep)
        validate_html.check_artifacts(name, src, rep)
    return rep.problems


def test_run_record_marks_ok_failed_and_missing_modules():
    run, _ = _run()
    assert [m["status"] for m in run["modules"]] == ["ok", "failed", "missing"]
    assert run["modules"][0]["score"] == 6.8
    assert "score" not in run                       # synthesis carried no signal
    assert (run["mean_score"], run["mean_n"]) == (6.8, 1)


def test_report_page_is_valid_and_states_what_was_not_assessed():
    run, sections = _run(page="20261116/show_case.html")
    older = {"page": "20261110/show_case.html", "date": "2026-11-10", "ticker": "NVDA"}
    page = site.render_report(run, sections, "整體結論。", older)
    assert _validate({"show_case.html": page}) == []
    assert 'href="../20261110/show_case.html"' in page       # older neighbour, one level up
    assert 'href="../assets/live.css"' in page and "<style>" not in page
    assert "未評估 — 生成失敗" in page and "未評估 — 上游沒有這個框架" in page
    assert "v1.15.0" in page and "35d68f9" in page
    assert "算術平均" in page                         # the mean is labelled as a mean
    assert validate_html.MODEL_WRITTEN in page


def test_index_is_valid_empty_and_populated(tmp_path):
    empty = site.render_index({"runs": []}, UNIVERSE)
    assert _validate({"index.html": empty}) == [] and "尚未有展示" in empty
    assert validate_html.MODEL_WRITTEN not in empty   # the index is template-written

    run, sections = _run()
    page = runner.publish(run, sections, "整體結論。", tmp_path)
    assert page == tmp_path / "20261116" / "show_case.html"
    index = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert _validate({"index.html": index}) == []
    assert 'href="20261116/show_case.html"' in index and "尚未輪到的標的（31）" in index
    assert (tmp_path / "assets" / "live.css").exists() and (tmp_path / "assets" / "live.js").exists()


def test_every_run_keeps_its_own_dated_page(tmp_path):
    run, sections = _run()
    runner.publish(run, sections, "x", tmp_path)
    runner.publish(dict(run), sections, "x", tmp_path)            # same ticker, same day: replaced
    older, _ = _run(date="2026-11-10")
    runner.publish(older, sections, "x", tmp_path)                # imported out of order
    other, _ = _run()
    other["ticker"] = "NVDA"
    runner.publish(other, sections, "x", tmp_path)                # second ticker on the 16th

    runs = site.load_manifest(tmp_path)["runs"]
    assert [(r["ticker"], r["date"], r["page"]) for r in runs] == [
        ("NVDA", "2026-11-16", "20261116-nvda/show_case.html"),
        ("MU", "2026-11-16", "20261116/show_case.html"),
        ("MU", "2026-11-10", "20261110/show_case.html")]
    for r in runs:
        assert (tmp_path / r["page"]).exists()
    assert len(site.latest_per_ticker(runs)) == 2
    index = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert index.count('class="lv-card"') == 3 and "全部 3 次展示，2 檔標的" in index


def test_landing_block_is_rewritten_between_its_markers(tmp_path):
    landing = tmp_path / "index.html"
    landing.write_text(f"<p>before</p>\n{site.LANDING_START}stale{site.LANDING_END}\n<p>after</p>",
                       encoding="utf-8")
    run, sections = _run()
    runner.publish(run, sections, "x", tmp_path / "live", landing=landing)
    text = landing.read_text(encoding="utf-8")
    assert "stale" not in text and "<p>before</p>" in text and "<p>after</p>" in text
    assert 'href="showcase/live/20261116/show_case.html"' in text and "All 1 live showcases" in text
    assert text.count(site.LANDING_START) == 1 and text.count(site.LANDING_END) == 1

    bare = tmp_path / "bare.html"
    bare.write_text("<p>no markers</p>", encoding="utf-8")
    assert site.update_landing({"runs": []}, bare) is False
    assert bare.read_text(encoding="utf-8") == "<p>no markers</p>"


# ── importing a saved full-report file ──────────────────────────────────────
def test_parse_report_does_not_split_on_a_modules_own_numbered_heading():
    text = ("---\nticker: MU\ndate: 2026-11-16\nprovider: gemini\nmodel: m\n---\n\n"
            "# MU 全模組投資分析報告\n\n## 🎯 綜合結論 (Consolidated Verdict)\n\n結論。\n\n---\n\n"
            "## 📑 各模組分析 (Module Sections)\n\n"
            "### 1. 綜合股票評估\n\n### 1. 投資論點\n\n甲\n\n### 2. 公司概覽\n\n乙\n\n---\n\n"
            "### 2. 空頭觀點\n\n丙\n\n---\n")
    meta, synthesis, sections = runner.parse_report(text)
    assert meta["ticker"] == "MU" and synthesis == "結論。"
    assert [label for label, _ in sections] == ["綜合股票評估", "空頭觀點"]
    assert "公司概覽" in sections[0][1] and sections[1][1] == "丙"


def test_parse_report_rejects_other_files():
    with pytest.raises(ValueError):
        runner.parse_report("# just a note")


def test_etf_module_set_leads_with_etf_analysis():
    assert ETF_SKILLS[0] == "etf-analysis" and "full-report" not in ETF_SKILLS
