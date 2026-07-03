"""
InvestSkill analysis package.

Layered architecture (mirrors yennanliu/finance_data):

    config/    — provider defaults, analysis-type metadata, constants
    prompts/   — prompt layer: loads GEMINI.md + prompts/*.md from the cloned
                 InvestSkill repo and exposes them through a PromptRepo
    data/      — data layer: yfinance snapshot (network-touching)
    llm/       — provider layer: run_gemini / run_openai / run_claude + call_llm
    utils/     — formatting, logging helpers
    pipeline   — gen layer: assembles prompt + data + provider into a report
    publish    — output layer: frontmatter + file writing

The standalone ``scripts/*_gemini.py`` entrypoints are thin wrappers over
``analysis.cli``; all real logic lives in these layers.
"""

__all__ = ["__version__"]
__version__ = "2.0.0"
