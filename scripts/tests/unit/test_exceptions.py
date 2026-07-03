"""Unit tests for the exception hierarchy."""

from analysis import exceptions as exc


def test_all_derive_from_analysis_error():
    for cls in (exc.LLMError, exc.DataFetchError, exc.PromptError, exc.ConfigError):
        assert issubclass(cls, exc.AnalysisError)


def test_analysis_error_is_exception():
    assert issubclass(exc.AnalysisError, Exception)


def test_can_raise_and_catch_as_base():
    try:
        raise exc.LLMError("boom")
    except exc.AnalysisError as e:
        assert str(e) == "boom"
