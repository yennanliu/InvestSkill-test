"""Post-process LLM-generated Markdown to repair invalid Mermaid charts.

Two independent classes of hallucinated ``xychart-beta`` syntax get repaired:

1. **Swapped axes** — a categorical band on ``y-axis`` and a numeric range on
   ``x-axis``. Mermaid requires the value axis (``y-axis``) to be a numeric
   ``min --> max`` range and rejects a band there with:

       Parse error … Expecting 'NUMBER_WITH_DECIMAL' … got 'SQUARE_BRACES_START'

2. **Object-literal series** — real xychart-beta only supports a flat
   ``bar [n, n, …]`` / ``line [n, n, …]`` array. LLMs frequently invent a
   richer per-series block instead (``line { name "X" data [...] stroke-color
   ... }``), which Mermaid can't parse at all:

       Lexical error … Unrecognized text

   ``sanitize_mermaid`` extracts the ``data`` array (and optional ``name``,
   surfaced afterwards as a legend caption) from each such block and discards
   the rest, leaving a chart Mermaid can actually render.

Both repairs happen only inside fenced ```mermaid blocks that contain
``xychart-beta`` — everything else in the Markdown passes through unchanged.
"""

from __future__ import annotations

import re

_MERMAID_BLOCK = re.compile(r"(```mermaid\n)(.*?)(\n```)", re.DOTALL)

# ── Axis-swap repair ─────────────────────────────────────────────────────────

# Capture the axis keyword and everything after it on the line.
_X_AXIS = re.compile(r"^(?P<indent>\s*)x-axis(?P<rest>\s+\S.*)$", re.MULTILINE)
_Y_AXIS = re.compile(r"^(?P<indent>\s*)y-axis(?P<rest>\s+\S.*)$", re.MULTILINE)


def _is_band(expr: str) -> bool:
    return "[" in expr


def _is_range(expr: str) -> bool:
    return "-->" in expr


def _fix_axis_swap(block: str) -> str:
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


# ── Object-literal series repair ────────────────────────────────────────────

_Y2_AXIS_LINE = re.compile(r"^[ \t]*y2-axis.*\n?", re.MULTILINE)
_SERIES_START = re.compile(r"(?P<indent>[ \t]*)(?P<type>bar|line)\s*\{")
_NAME_RE = re.compile(r'name\s*:?\s*"([^"]*)"')
_DATA_RE = re.compile(r"data\s*:?\s*(\[[^\]]*\])")

_TYPE_LABEL = {"line": "線", "bar": "柱"}


def _find_matching_brace(text: str, open_idx: int) -> int:
    """Return the index just past the ``}`` matching the ``{`` at ``open_idx``."""
    depth = 0
    for i in range(open_idx, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i + 1
    return len(text)


def _fix_series_blocks(block: str) -> tuple[str, list[tuple[str, str]]]:
    """Rewrite ``bar``/``line`` object-literal blocks as flat array declarations.

    Returns the fixed block plus the ``(type, name)`` pairs recovered from any
    ``name`` field, in source order, so the caller can surface a legend.
    """
    block = _Y2_AXIS_LINE.sub("", block)  # not a real xychart-beta keyword

    legend: list[tuple[str, str]] = []
    out: list[str] = []
    pos = 0
    while True:
        m = _SERIES_START.search(block, pos)
        if not m:
            out.append(block[pos:])
            break
        out.append(block[pos:m.start()])
        end = _find_matching_brace(block, m.end() - 1)
        inner = block[m.end():end - 1]

        data_match = _DATA_RE.search(inner)
        if not data_match:
            # Nothing salvageable (no data array) — drop the whole block.
            pos = end
            continue

        name_match = _NAME_RE.search(inner)
        if name_match:
            legend.append((m.group("type"), name_match.group(1)))
        out.append(f"{m.group('indent')}{m.group('type')} {data_match.group(1)}")
        pos = end

    return "".join(out), legend


def _build_legend_caption(legend: list[tuple[str, str]]) -> str:
    counts: dict[str, int] = {}
    parts = []
    for kind, name in legend:
        counts[kind] = counts.get(kind, 0) + 1
        parts.append(f"{_TYPE_LABEL.get(kind, kind)} {counts[kind]}: {name}")
    return f"*圖例：{' | '.join(parts)}*"


_LEGEND_ALREADY_PRESENT = re.compile(r"^\s*\*?圖例")


def sanitize_mermaid(text: str) -> str:
    """Repair broken ``xychart-beta`` blocks in Markdown; return the text.

    Non-Mermaid content and already-valid charts pass through unchanged.
    """

    def _replace(m: re.Match) -> str:
        block = m.group(2)
        if "xychart-beta" not in block:
            return m.group(0)

        block = _fix_axis_swap(block)
        block, legend = _fix_series_blocks(block)
        result = m.group(1) + block + m.group(3)

        if legend and not _LEGEND_ALREADY_PRESENT.match(
            text[m.end():m.end() + 40].lstrip("\n")
        ):
            result += "\n" + _build_legend_caption(legend)
        return result

    return _MERMAID_BLOCK.sub(_replace, text)
