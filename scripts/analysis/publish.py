"""Output layer: YAML frontmatter + collision-safe Markdown file writing."""

from __future__ import annotations

from pathlib import Path

from .config import TODAY, analysis_meta
from .utils.logging_utils import setup_logger
from .utils.mermaid import sanitize_mermaid

logger = setup_logger(__name__)


def _unique_path(output_dir: Path, base: str, ext: str) -> Path:
    """Return output_dir/base+ext, appending -2, -3… if it already exists."""
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{base}{ext}"
    counter = 2
    while path.exists():
        path = output_dir / f"{base}-{counter}{ext}"
        counter += 1
    return path


def _frontmatter(fields: dict[str, object]) -> str:
    lines = ["---"]
    for key, value in fields.items():
        if isinstance(value, str) and (":" in value or value.startswith('"')):
            lines.append(f'{key}: "{value}"')
        else:
            lines.append(f"{key}: {value}")
    lines.append("---\n\n")
    return "\n".join(lines)


def save_report(analysis_type: str, ticker: str, content: str, output_dir: str | Path,
                provider: str, model: str) -> Path:
    """Write a single-module report with frontmatter; return the path."""
    meta = analysis_meta(analysis_type)
    ticker = ticker.upper()
    safe_model = model.replace("/", "-")
    base = f"{meta['prefix']}_{TODAY}_{safe_model}"
    path = _unique_path(Path(output_dir), base, meta["ext"])
    content = sanitize_mermaid(content)

    frontmatter = _frontmatter({
        "title": f"{ticker} {meta['label']} {TODAY}",
        "date": TODAY,
        "ticker": ticker,
        "analysis_type": analysis_type,
        "skill_source": "https://github.com/yennanliu/InvestSkill",
        "prompt_file": f"prompts/{analysis_type}.md",
        "provider": provider,
        "model": model,
        "language": "zh-TW",
        "generated_by": "InvestSkill analysis package (scripts/analysis)",
    })
    path.write_text(frontmatter + content, encoding="utf-8")
    logger.info(f"Saved report → {path}")
    return path


def save_full_report(ticker: str, sections: list[tuple[str, str]], synthesis: str,
                     output_dir: str | Path, provider: str, model: str) -> Path:
    """Write the combined full-report (verdict + all module sections); return path."""
    ticker = ticker.upper()
    safe_model = model.replace("/", "-")
    base = f"full_report_{TODAY}_{safe_model}"
    path = _unique_path(Path(output_dir), base, ".md")

    frontmatter = _frontmatter({
        "title": f"{ticker} Full InvestSkill Report {TODAY}",
        "date": TODAY,
        "ticker": ticker,
        "analysis_type": "full-report",
        "modules": len(sections),
        "skill_source": "https://github.com/yennanliu/InvestSkill",
        "demo_reference": "https://yennj12.js.org/InvestSkill/full-demo-rklb.html",
        "provider": provider,
        "model": model,
        "language": "zh-TW",
        "generated_by": "InvestSkill analysis package (scripts/analysis)",
    })

    body = [
        f"# {ticker} 全模組投資分析報告 ({TODAY})",
        "",
        f"> 由 InvestSkill 全套 {len(sections)} 個分析模組生成，供應商：`{provider}`，模型：`{model}`。",
        "",
        "## 🎯 綜合結論 (Consolidated Verdict)",
        "",
        synthesis,
        "",
        "---",
        "",
        "## 📑 各模組分析 (Module Sections)",
        "",
    ]
    for i, (label, content) in enumerate(sections, 1):
        body += [f"### {i}. {label}", "", content, "", "---", ""]

    path.write_text(frontmatter + sanitize_mermaid("\n".join(body)), encoding="utf-8")
    logger.info(f"Saved full report ({len(sections)} modules) → {path}")
    return path
