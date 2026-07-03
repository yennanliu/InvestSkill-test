"""Unit tests for logging setup."""

import logging

from analysis.utils.logging_utils import setup_logger


def test_returns_logger():
    log = setup_logger("analysis.test.one")
    assert isinstance(log, logging.Logger)
    assert log.handlers  # a handler was attached


def test_idempotent_no_duplicate_handlers():
    log1 = setup_logger("analysis.test.two")
    n = len(log1.handlers)
    log2 = setup_logger("analysis.test.two")
    assert log1 is log2
    assert len(log2.handlers) == n  # not doubled


def test_writes_to_stderr():
    import sys
    log = setup_logger("analysis.test.three")
    handler = log.handlers[0]
    assert getattr(handler, "stream", None) is sys.stderr
