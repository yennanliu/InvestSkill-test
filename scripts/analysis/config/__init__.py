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


# The 15 "comprehensive" modules from InvestSkill's prompts/full-report.md,
# in the plugin's own analytical order (quick 1-5, standard 6-10, comprehensive 11-15).
# https://yennj12.js.org/InvestSkill/full-demo-rklb.html
FULL_DEMO_SKILLS = [
    "stock-eval",
    "technical-analysis",
    "dcf-valuation",
    "insider-trading",
    "earnings-call-analysis",
    "institutional-ownership",
    "competitor-analysis",
    "sector-analysis",
    "options-analysis",
    "short-interest",
    "fundamental-analysis",
    "stock-valuation",
    "economics-analysis",
    "financial-report-analyst",
    "dividend-analysis",
]

__all__ = [
    "TODAY",
    "DEFAULT_PROVIDER",
    "DEFAULT_LANGUAGE",
    "INVEST_SKILL_REPO",
    "DEFAULT_INVEST_SKILL_DIR",
    "ANALYSIS_TYPES",
    "FULL_DEMO_SKILLS",
    "SUPPORTED_PROVIDERS",
    "PROVIDER_DEFAULTS",
    "PROVIDER_CONTEXT_FILE",
    "analysis_meta",
    "provider_default",
    "context_file",
]
