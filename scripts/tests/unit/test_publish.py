"""Unit tests for the output layer (publish)."""

from analysis import publish
from analysis.config import TODAY


def test_save_report_writes_frontmatter_and_content(tmp_path):
    path = publish.save_report("dcf-valuation", "aapl", "BODY TEXT",
                               tmp_path, "gemini", "gemini-2.5-flash")
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---")
    assert "ticker: AAPL" in text
    assert "analysis_type: dcf-valuation" in text
    assert "provider: gemini" in text
    assert "model: gemini-2.5-flash" in text
    assert "BODY TEXT" in text


def test_save_report_filename_pattern(tmp_path):
    path = publish.save_report("fundamental-analysis", "TSLA", "x",
                               tmp_path, "gemini", "gemini-2.5-flash")
    assert path.name == f"fundamental_analysis_{TODAY}_gemini-2.5-flash.md"


def test_save_report_collision_suffix(tmp_path):
    p1 = publish.save_report("stock-eval", "AAPL", "a", tmp_path, "gemini", "m")
    p2 = publish.save_report("stock-eval", "AAPL", "b", tmp_path, "gemini", "m")
    assert p1 != p2
    assert p2.name.endswith("-2.md")


def test_model_slash_sanitised(tmp_path):
    path = publish.save_report("dcf-valuation", "AAPL", "x", tmp_path,
                               "openai", "openai/gpt-4o")
    assert "/" not in path.name
    assert "openai-gpt-4o" in path.name


def test_save_full_report_structure(tmp_path):
    sections = [("技術分析", "tech body"), ("DCF 估值", "dcf body")]
    path = publish.save_full_report("AAPL", sections, "VERDICT TEXT",
                                    tmp_path, "gemini", "gemini-2.5-flash")
    text = path.read_text(encoding="utf-8")
    assert "analysis_type: full-report" in text
    assert "modules: 2" in text
    assert "綜合結論" in text
    assert "VERDICT TEXT" in text
    assert "### 1. 技術分析" in text
    assert "### 2. DCF 估值" in text
    assert "tech body" in text and "dcf body" in text
