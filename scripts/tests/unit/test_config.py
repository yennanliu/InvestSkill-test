"""Unit tests for the config layer."""

import pytest

from analysis import config
from analysis.config import providers


def test_default_provider_is_gemini():
    assert config.DEFAULT_PROVIDER == "gemini"
    assert config.DEFAULT_LANGUAGE == "zh-TW"


def test_gemini_defaults_match_repo_settings():
    assert providers.provider_default("gemini", "default_model") == "gemini-3.5-flash"
    assert providers.provider_default("gemini", "default_tokens") == 20000


def test_all_providers_have_defaults():
    for prov in config.SUPPORTED_PROVIDERS:
        assert providers.provider_default(prov, "default_model")
        assert providers.provider_default(prov, "default_tokens") > 0


def test_supported_providers():
    assert set(config.SUPPORTED_PROVIDERS) == {"gemini", "openai", "claude"}


def test_provider_default_unknown_raises():
    with pytest.raises(KeyError):
        providers.provider_default("bogus", "default_model")


def test_context_file_mapping():
    assert config.context_file("gemini") == "GEMINI.md"
    assert config.context_file("claude") == "CLAUDE.md"
    # unknown / openai fall back to GEMINI.md
    assert config.context_file("openai") == "GEMINI.md"
    assert config.context_file("nope") == "GEMINI.md"


def test_full_demo_has_15_modules():
    assert len(config.FULL_DEMO_SKILLS) == 15
    assert len(set(config.FULL_DEMO_SKILLS)) == 15  # no dupes


def test_every_full_demo_skill_has_metadata():
    for slug in config.FULL_DEMO_SKILLS:
        assert slug in config.ANALYSIS_TYPES, slug


def test_analysis_meta_known():
    meta = config.analysis_meta("dcf-valuation")
    assert meta["prefix"] == "dcf_valuation"
    assert meta["ext"] == ".md"
    assert meta["label"]


def test_analysis_meta_unknown_fallback():
    meta = config.analysis_meta("brand-new-skill")
    assert meta["prefix"] == "brand_new_skill"
    assert meta["label"] == "Brand New Skill"
    assert meta["ext"] == ".md"


def test_today_is_iso():
    # e.g. 2026-07-03
    assert len(config.TODAY) == 10 and config.TODAY[4] == "-"
