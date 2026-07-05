"""Post-process LLM-generated Markdown to repair invalid Mermaid charts.

LLMs frequently emit ``xychart-beta`` blocks with the axes swapped — a
categorical band on ``y-axis`` and a numeric range on ``x-axis``. Mermaid
requires the value axis (``y-axis``) to be a numeric ``min --> max`` range and
rejects a band there with:

    Parse error … Expecting 'NUMBER_WITH_DECIMAL' … got 'SQUARE_BRACES_START'

which breaks rendering of the whole chart. ``sanitize_mermaid`` detects that
swap and puts each axis expression back on the correct axis.
"""

from __future__ import annotations

import re

_MERMAID_BLOCK = re.compile(r"(```mermaid\n)(.*?)(\n```)", re.DOTALL)
# Capture the axis keyword and everything after it on the line.
_X_AXIS = re.compile(r"^(?P<indent>\s*)x-axis(?P<rest>\s+\S.*)$", re.MULTILINE)
_Y_AXIS = re.compile(r"^(?P<indent>\s*)y-axis(?P<rest>\s+\S.*)$", re.MULTILINE)


def _is_band(expr: str) -> bool:
    return "[" in expr


def _is_range(expr: str) -> bool:
    return "-->" in expr


def _fix_block(block: str) -> str:
    if "xychart-beta" not in block:
        return block

    x_match = _X_AXIS.search(block)
    y_match = _Y_AXIS.search(block)
    if not x_match or not y_match:
        return block

    x_rest = x_match.group("rest")
    y_rest = y_match.group("rest")

    # Invalid only when the value axis (y) holds a band and x holds the range.
    if not (_is_band(y_rest) and _is_range(x_rest)):
        return block

    # Swap the expressions so x carries the band and y carries the range.
    new_x = f"{x_match.group('indent')}x-axis{y_rest}"
    new_y = f"{y_match.group('indent')}y-axis{x_rest}"
    block = block[:x_match.start()] + new_x + block[x_match.end():]
    # Re-locate y-axis after the x replacement (offsets shifted).
    y_match = _Y_AXIS.search(block)
    block = block[:y_match.start()] + new_y + block[y_match.end():]
    return block


def sanitize_mermaid(text: str) -> str:
    """Repair swapped-axis ``xychart-beta`` blocks in Markdown; return the text.

    Non-Mermaid content and already-valid charts pass through unchanged.
    """
    return _MERMAID_BLOCK.sub(
        lambda m: m.group(1) + _fix_block(m.group(2)) + m.group(3), text
    )
