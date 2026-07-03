"""Logging helpers shared across the analysis package."""

from __future__ import annotations

import logging
import os
import sys

_CONFIGURED: set[str] = set()


def setup_logger(name: str) -> logging.Logger:
    """Return a module logger that writes to stderr once, at ``LOG_LEVEL``.

    Logs go to stderr so stdout stays clean for report content / progress lines.
    Level is controlled by the ``LOG_LEVEL`` env var (default ``INFO``).
    """
    logger = logging.getLogger(name)
    if name not in _CONFIGURED:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(os.environ.get("LOG_LEVEL", "INFO").upper())
        logger.propagate = False
        _CONFIGURED.add(name)
    return logger
