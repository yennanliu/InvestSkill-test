"""Custom exceptions for the analysis package."""


class AnalysisError(Exception):
    """Base exception for all analysis-related errors."""


class LLMError(AnalysisError):
    """Raised when an LLM API call fails or is misconfigured."""


class DataFetchError(AnalysisError):
    """Raised when fetching market/financial data fails."""


class PromptError(AnalysisError):
    """Raised when a prompt template or system context cannot be loaded."""


class ConfigError(AnalysisError):
    """Raised for configuration errors."""
