"""
Shared fixtures for the analysis test suite.

Everything network- or SDK-touching is faked at the import boundary:
  * ``fake_invest_skill`` — a cloned-InvestSkill directory on tmp_path
  * ``fake_yfinance``     — installs a stub ``yfinance`` into sys.modules
  * ``fake_gemini`` / ``fake_openai`` / ``fake_anthropic`` — stub the SDKs

The stubs are installed via monkeypatch (auto-undone after each test) and expose
a ``.responder`` / ``.calls`` handle so tests can script responses and assert
what the provider layer sent.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

# ── Fake cloned InvestSkill repo ─────────────────────────────────────────────

# A superset of the full-demo slugs so any single/full run finds its framework.
_PROMPT_SLUGS = [
    "dcf-valuation", "fundamental-analysis", "stock-eval", "stock-valuation",
    "technical-analysis", "economics-analysis", "sector-analysis",
    "insider-trading", "institutional-ownership", "short-interest",
    "earnings-call-analysis", "chart-master", "options-analysis",
    "dividend-analysis", "competitor-analysis", "financial-report-analyst",
]


@pytest.fixture
def fake_invest_skill(tmp_path: Path) -> Path:
    """Create a minimal cloned-InvestSkill directory and return its path."""
    root = tmp_path / "InvestSkill"
    (root / "prompts").mkdir(parents=True)
    (root / "GEMINI.md").write_text("You are an institutional-quality analyst (GEMINI).", encoding="utf-8")
    (root / "CLAUDE.md").write_text("You are an institutional-quality analyst (CLAUDE).", encoding="utf-8")
    for slug in _PROMPT_SLUGS:
        (root / "prompts" / f"{slug}.md").write_text(f"# {slug} framework\nApply the {slug} framework.", encoding="utf-8")
    return root


# ── Helper to install a fake module (and parent packages) into sys.modules ────

def _install_module(monkeypatch, dotted: str, module: types.ModuleType) -> None:
    parts = dotted.split(".")
    for i in range(1, len(parts)):
        parent = ".".join(parts[:i])
        if parent not in sys.modules:
            monkeypatch.setitem(sys.modules, parent, types.ModuleType(parent))
    monkeypatch.setitem(sys.modules, dotted, module)
    if len(parts) > 1:  # attach as attribute of parent
        monkeypatch.setattr(sys.modules[".".join(parts[:-1])], parts[-1], module, raising=False)


# ── Fake yfinance ────────────────────────────────────────────────────────────

@pytest.fixture
def fake_yfinance(monkeypatch):
    """Install a stub ``yfinance`` and return a controller.

    ``controller.info`` / ``controller.with_history`` tune the fake Ticker.
    """
    pd = pytest.importorskip("pandas")

    class _Controller:
        info = {
            "longName": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics",
            "marketCap": 3_000_000_000_000, "currentPrice": 200.0, "sharesOutstanding": 15_000_000_000,
            "totalRevenue": 400_000_000_000, "freeCashflow": 90_000_000_000,
            "operatingCashflow": 110_000_000_000, "capitalExpenditures": -10_000_000_000,
            "totalCash": 60_000_000_000, "totalDebt": 100_000_000_000,
            "trailingPE": 30.0, "beta": 1.2,
        }
        with_history = True

    ctrl = _Controller()

    def _frame(rows):
        cols = pd.DatetimeIndex(["2024-12-31", "2023-12-31"])
        return pd.DataFrame({c: [1.0] * len(rows) for c in cols}, index=rows)

    class _Ticker:
        def __init__(self, ticker):
            self.ticker = ticker

        @property
        def info(self):
            return dict(ctrl.info)

        def history(self, period="6mo"):
            if not ctrl.with_history:
                return pd.DataFrame()
            n = 60
            dates = pd.date_range("2024-01-01", periods=n, freq="D")
            return pd.DataFrame(
                {"Close": [100.0 + i for i in range(n)], "Volume": [1_000_000 + i for i in range(n)]},
                index=dates,
            )

        @property
        def financials(self):
            return _frame(["Total Revenue", "Gross Profit", "Operating Income", "Net Income", "EBITDA"])

        @property
        def cashflow(self):
            return _frame(["Operating Cash Flow", "Capital Expenditure", "Free Cash Flow"])

    mod = types.ModuleType("yfinance")
    mod.Ticker = _Ticker
    _install_module(monkeypatch, "yfinance", mod)
    return ctrl


# ── Fake Gemini (google.generativeai) ────────────────────────────────────────

class _GeminiResponse:
    def __init__(self, text, finish="STOP"):
        self._text = text
        part = types.SimpleNamespace(text=text or "")
        content = types.SimpleNamespace(parts=[part])
        fr = types.SimpleNamespace(name=finish)
        self.candidates = [types.SimpleNamespace(finish_reason=fr, content=content)]

    @property
    def text(self):
        if self._text is None:
            raise ValueError("empty candidate")
        return self._text


@pytest.fixture
def fake_gemini(monkeypatch):
    """Install a stub ``google.generativeai``; return a controller.

    Set ``ctrl.responder = lambda contents, cfg: _GeminiResponse(text, finish)``
    to script responses. ``ctrl.calls`` records (contents, max_output_tokens, temperature).
    """
    class _Ctrl:
        calls = []
        api_key = None
        responder = staticmethod(lambda contents, cfg: _GeminiResponse("訊號框：評分 7/10 看多"))

    ctrl = _Ctrl()

    class _GenerationConfig:
        def __init__(self, **kw):
            self.__dict__.update(kw)

    class _Model:
        def __init__(self, model_name=None, system_instruction=None, generation_config=None):
            self.model_name = model_name
            self.system_instruction = system_instruction
            self.generation_config = generation_config

        def generate_content(self, contents):
            cfg = self.generation_config
            ctrl.calls.append((contents, getattr(cfg, "max_output_tokens", None),
                               getattr(cfg, "temperature", None), self.system_instruction))
            return ctrl.responder(contents, cfg)

    mod = types.ModuleType("google.generativeai")
    mod.configure = lambda api_key=None: setattr(ctrl, "api_key", api_key)
    mod.GenerativeModel = _Model
    mod.GenerationConfig = _GenerationConfig
    _install_module(monkeypatch, "google.generativeai", mod)
    return ctrl


# ── Fake OpenAI ──────────────────────────────────────────────────────────────

@pytest.fixture
def fake_openai(monkeypatch):
    class _Ctrl:
        calls = []
        responder = staticmethod(lambda **kw: "訊號框：評分 6/10 中性")

    ctrl = _Ctrl()

    class RateLimitError(Exception):
        pass

    class _Client:
        def __init__(self, api_key=None):
            self.api_key = api_key
            self.chat = types.SimpleNamespace(completions=types.SimpleNamespace(create=self._create))

        def _create(self, **kw):
            ctrl.calls.append(kw)
            text = ctrl.responder(**kw)
            msg = types.SimpleNamespace(content=text)
            return types.SimpleNamespace(choices=[types.SimpleNamespace(message=msg)])

    mod = types.ModuleType("openai")
    mod.OpenAI = _Client
    mod.RateLimitError = RateLimitError
    _install_module(monkeypatch, "openai", mod)
    return ctrl


# ── Fake Anthropic ───────────────────────────────────────────────────────────

@pytest.fixture
def fake_anthropic(monkeypatch):
    class _Ctrl:
        calls = []
        responder = staticmethod(lambda **kw: "訊號框：評分 8/10 看多")

    ctrl = _Ctrl()

    class RateLimitError(Exception):
        pass

    class _Client:
        def __init__(self, api_key=None):
            self.api_key = api_key
            self.messages = types.SimpleNamespace(create=self._create)

        def _create(self, **kw):
            ctrl.calls.append(kw)
            text = ctrl.responder(**kw)
            return types.SimpleNamespace(content=[types.SimpleNamespace(text=text)])

    mod = types.ModuleType("anthropic")
    mod.Anthropic = _Client
    mod.RateLimitError = RateLimitError
    _install_module(monkeypatch, "anthropic", mod)
    return ctrl


# Expose the response builder for tests that script Gemini truncation/refusal.
@pytest.fixture
def gemini_response():
    return _GeminiResponse
