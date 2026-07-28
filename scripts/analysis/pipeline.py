"""
Gen layer — orchestration.

Assembles the four layers into a report:
  prompt layer (framework + system context) + data layer (yfinance snapshot)
  → provider layer (call_llm) → report text.

Two entrypoints:
  * ``generate_analysis``     — one InvestSkill module → Markdown report
  * ``generate_full_report``  — a depth tier's modules + a synthesised verdict
"""

from __future__ import annotations

import time
from pathlib import Path

from .config import DEFAULT_DEPTH, analysis_meta, depth_skills
from .data import fetch_stock_data
from .llm import call_llm
from .prompts import PromptRepo
from .utils.logging_utils import setup_logger

logger = setup_logger(__name__)

_SIGNAL_BOX = (
    "最後請附上 InvestSkill『投資訊號框』，包含："
    "評分 (1–10)、訊號方向 (看多/中性/看空)、信心水準、建議動作 (買進/持有/避開)。"
)


def _language_directive(language: str) -> str:
    if language == "zh-TW":
        return "Write all analysis reports in Traditional Chinese (繁體中文)."
    return f"Write all analysis reports in {language}."


def _system_message(repo: PromptRepo, provider: str, language: str) -> str:
    return repo.system_context(provider) + "\n\n---\n\n" + _language_directive(language)


def _single_message(framework: str, ticker: str, label: str, stock_data: str) -> str:
    return (
        framework
        + "\n\n---\n\n"
        + f"請套用以上框架，為 **{ticker.upper()}** 產出完整的{label}報告，全文使用繁體中文。"
        + "請直接分析下方共用數據，不要原樣覆述數據表。\n\n"
        + stock_data
    )


def _module_message(framework: str, ticker: str, stock_data: str) -> str:
    return (
        framework
        + "\n\n---\n\n"
        + f"請套用以上框架，為 **{ticker.upper()}** 撰寫這個模組在完整研究報告中的段落，全文使用繁體中文。"
        + "請直接分析下方共用數據，不要原樣覆述數據表。"
        + _SIGNAL_BOX
        + "\n\n"
        + stock_data
    )


def generate_analysis(ticker: str, analysis_type: str, *, provider: str,
                      model: str | None, max_tokens: int | None,
                      invest_skill_dir: str | Path, language: str = "zh-TW",
                      stock_data: str | None = None,
                      repo: PromptRepo | None = None) -> str:
    """Generate one InvestSkill module's report and return the Markdown text.

    ``stock_data`` / ``repo`` can be injected so a full-report run reuses one
    fetch + one PromptRepo across every module.
    """
    ticker = ticker.upper()
    repo = repo or PromptRepo(invest_skill_dir)
    framework = repo.framework(analysis_type)
    system_message = _system_message(repo, provider, language)
    if stock_data is None:
        stock_data = fetch_stock_data(ticker)

    label = analysis_meta(analysis_type)["label"]
    message = _single_message(framework, ticker, label, stock_data)
    logger.info(f"Generating {analysis_type} for {ticker} via {provider}")
    return call_llm(provider, ticker, message, system_message,
                    model=model, max_tokens=max_tokens)


def synthesize(ticker: str, module_signals: str, module_count: int, *,
               provider: str, model: str | None, max_tokens: int | None,
               system_message: str) -> str:
    """Synthesise a consolidated verdict from all module signal boxes."""
    prompt = (
        f"你已完成對 **{ticker.upper()}** 的 {module_count} 個模組 InvestSkill 分析。"
        "以下是各模組的投資訊號框，請綜合成一份整體結論（繁體中文）：\n"
        "1. 綜合評分 (加權 1–10) 與整體訊號 (看多/中性/看空)\n"
        "2. 信心水準與理由\n"
        "3. 各模組共識與分歧點\n"
        "4. 最終投資建議 (買進/持有/避開) 與關鍵風險\n\n"
        + module_signals
    )
    return call_llm(provider, ticker, prompt, system_message,
                    model=model, max_tokens=max_tokens)


def generate_full_report(ticker: str, *, provider: str, model: str | None,
                         max_tokens: int | None, invest_skill_dir: str | Path,
                         skills: list[str] | None = None, depth: str = DEFAULT_DEPTH,
                         language: str = "zh-TW", sleep: float = 1.0) -> dict:
    """Run a full-report depth tier's modules + a synthesis pass.

    ``depth`` selects the module set (``quick`` / ``standard`` /
    ``comprehensive``), mirroring the plugin's own ``full-report --depth`` flag.
    An explicit ``skills`` list overrides the tier.

    Returns ``{"sections": [(label, content), …], "synthesis": str,
    "skills": [slug, …]}``. One yfinance fetch and one PromptRepo are shared
    across all modules. A module that fails is recorded with an error note so a
    single failure never aborts the run.
    """
    ticker = ticker.upper()
    skills = skills or depth_skills(depth)
    repo = PromptRepo(invest_skill_dir)
    system_message = _system_message(repo, provider, language)
    stock_data = fetch_stock_data(ticker)

    sections: list[tuple[str, str]] = []
    ran: list[str] = []
    logger.info(f"Full report: {len(skills)} modules for {ticker} via {provider}")
    for i, slug in enumerate(skills, 1):
        if not repo.available(slug):
            logger.warning(f"[{i}/{len(skills)}] skipping {slug}: framework not found")
            continue
        label = analysis_meta(slug)["label"]
        print(f"  [{i}/{len(skills)}] {label} ({slug})…")
        try:
            framework = repo.framework(slug)
            message = _module_message(framework, ticker, stock_data)
            content = call_llm(provider, ticker, message, system_message,
                               model=model, max_tokens=max_tokens)
            sections.append((label, content))
            ran.append(slug)
        except Exception as exc:  # keep the run alive
            logger.warning(f"module {slug} failed: {exc}")
            sections.append((label, f"_模組生成失敗：{exc}_"))
            ran.append(slug)
        if sleep and i < len(skills):
            time.sleep(sleep)

    print("  Synthesising consolidated verdict…")
    module_signals = "\n\n".join(f"## {label}\n{content}" for label, content in sections)
    try:
        synthesis = synthesize(ticker, module_signals, len(sections),
                               provider=provider, model=model, max_tokens=max_tokens,
                               system_message=system_message)
    except Exception as exc:
        logger.warning(f"synthesis failed: {exc}")
        synthesis = f"_綜合結論生成失敗：{exc}_"

    return {"sections": sections, "synthesis": synthesis, "skills": ran}
