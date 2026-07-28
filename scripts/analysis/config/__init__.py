"""Configuration constants and analysis-type metadata."""

from __future__ import annotations

from datetime import date
from pathlib import Path

from .providers import (  # noqa: F401 (re-exported)
    PROVIDER_CONTEXT_FILE,
    PROVIDER_DEFAULTS,
    SUPPORTED_PROVIDERS,
    context_file,
    provider_default,
)

TODAY = date.today().isoformat()

DEFAULT_PROVIDER = "gemini"
DEFAULT_LANGUAGE = "zh-TW"  # Traditional Chinese

# Where the InvestSkill "plugin" is cloned at runtime (see the CI workflows).
INVEST_SKILL_REPO = "https://github.com/yennanliu/InvestSkill.git"
DEFAULT_INVEST_SKILL_DIR = Path("InvestSkill")

# analysis-type slug (== prompts/<slug>.md in InvestSkill) → output metadata.
ANALYSIS_TYPES = {
    "dcf-valuation":            {"prefix": "dcf_valuation",            "label": "DCF 現金流估值",   "ext": ".md"},
    "fundamental-analysis":     {"prefix": "fundamental_analysis",     "label": "基本面深度分析",   "ext": ".md"},
    "stock-eval":               {"prefix": "stock_eval",               "label": "綜合股票評估",     "ext": ".md"},
    "stock-valuation":          {"prefix": "stock_valuation",          "label": "多方法估值分析",   "ext": ".md"},
    "technical-analysis":       {"prefix": "technical_analysis",       "label": "技術分析",         "ext": ".md"},
    "economics-analysis":       {"prefix": "economics_analysis",       "label": "總體經濟分析",     "ext": ".md"},
    "sector-analysis":          {"prefix": "sector_analysis",          "label": "產業板塊分析",     "ext": ".md"},
    "insider-trading":          {"prefix": "insider_trading",          "label": "內部人交易分析",   "ext": ".md"},
    "institutional-ownership":  {"prefix": "institutional_ownership",  "label": "機構持股分析",     "ext": ".md"},
    "short-interest":           {"prefix": "short_interest",           "label": "空頭部位分析",     "ext": ".md"},
    "earnings-call-analysis":   {"prefix": "earnings_call_analysis",   "label": "財報電話會議分析", "ext": ".md"},
    "chart-master":             {"prefix": "chart_master",             "label": "圖表視覺化",       "ext": ".md"},
    "options-analysis":         {"prefix": "options_analysis",         "label": "選擇權分析",       "ext": ".md"},
    "dividend-analysis":        {"prefix": "dividend_analysis",        "label": "股利與資本回報",   "ext": ".md"},
    "competitor-analysis":      {"prefix": "competitor_analysis",      "label": "競爭護城河分析",   "ext": ".md"},
    "financial-report-analyst": {"prefix": "financial_report_analyst", "label": "財報深度分析",     "ext": ".md"},
    "full-report":              {"prefix": "full_report",              "label": "全模組投資分析",   "ext": ".md"},
    # ── added upstream after v1.6.0 (labels follow InvestSkill's README-zh-TW) ──
    "10k-digest":               {"prefix": "10k_digest",               "label": "10-K 年報摘要",    "ext": ".md"},
    "bear-case":                {"prefix": "bear_case",                "label": "空頭觀點",         "ext": ".md"},
    "catalyst-calendar":        {"prefix": "catalyst_calendar",        "label": "催化劑日曆",       "ext": ".md"},
    "industry-map":             {"prefix": "industry_map",             "label": "產業地圖",         "ext": ".md"},
    "position-ladder":          {"prefix": "position_ladder",          "label": "分批建倉與降成本", "ext": ".md"},
    "stock-screener":           {"prefix": "stock_screener",           "label": "股票篩選器",       "ext": ".md"},
    "portfolio-review":         {"prefix": "portfolio_review",         "label": "投資組合檢視",     "ext": ".md"},
    "report-generator":         {"prefix": "report_generator",         "label": "報告產出工具",     "ext": ".md"},
    "result-validator":         {"prefix": "result_validator",         "label": "結果驗證與信心評分", "ext": ".md"},
    # Deprecated upstream in 1.8.0 — folded into full-report's --depth flag.
    "research-bundle":          {"prefix": "research_bundle",          "label": "研究套組（已棄用）", "ext": ".md"},
}


def analysis_meta(analysis_type: str) -> dict:
    """Return metadata for an analysis type, with a sensible fallback."""
    if analysis_type in ANALYSIS_TYPES:
        return ANALYSIS_TYPES[analysis_type]
    return {
        "prefix": analysis_type.replace("-", "_"),
        "label": analysis_type.replace("-", " ").title(),
        "ext": ".md",
    }


# The module sets behind InvestSkill's ``full-report --depth`` flag (1.8.0+),
# in the plugin's own analytical order — each tier extends the previous one.
# Source: InvestSkill prompts/full-report.md § "Module Sets by Depth"
# https://yennj12.js.org/InvestSkill/full-demo-rklb.html
_QUICK_SKILLS = [
    "stock-eval",
    "technical-analysis",
    "dcf-valuation",
    "insider-trading",
    "earnings-call-analysis",
]

_STANDARD_EXTRA = [
    "institutional-ownership",
    "competitor-analysis",
    "sector-analysis",
    "options-analysis",
    "short-interest",
]

_COMPREHENSIVE_EXTRA = [
    "fundamental-analysis",
    "stock-valuation",
    "economics-analysis",
    "financial-report-analyst",
    "dividend-analysis",
]

DEPTH_TIERS = {
    "quick": list(_QUICK_SKILLS),
    "standard": _QUICK_SKILLS + _STANDARD_EXTRA,
    "comprehensive": _QUICK_SKILLS + _STANDARD_EXTRA + _COMPREHENSIVE_EXTRA,
}

SUPPORTED_DEPTHS = tuple(DEPTH_TIERS)
DEFAULT_DEPTH = "comprehensive"  # matches the plugin's own default

# Back-compat alias: the full 15-module set.
FULL_DEMO_SKILLS = DEPTH_TIERS[DEFAULT_DEPTH]


def depth_skills(depth: str) -> list[str]:
    """Return the module slugs for a ``full-report`` depth tier."""
    try:
        return list(DEPTH_TIERS[depth])
    except KeyError as exc:
        raise KeyError(
            f"Unknown depth {depth!r}. Supported depths: {', '.join(SUPPORTED_DEPTHS)}"
        ) from exc

__all__ = [
    "TODAY",
    "DEFAULT_PROVIDER",
    "DEFAULT_LANGUAGE",
    "INVEST_SKILL_REPO",
    "DEFAULT_INVEST_SKILL_DIR",
    "ANALYSIS_TYPES",
    "FULL_DEMO_SKILLS",
    "DEPTH_TIERS",
    "SUPPORTED_DEPTHS",
    "DEFAULT_DEPTH",
    "SUPPORTED_PROVIDERS",
    "PROVIDER_DEFAULTS",
    "PROVIDER_CONTEXT_FILE",
    "analysis_meta",
    "depth_skills",
    "provider_default",
    "context_file",
]
