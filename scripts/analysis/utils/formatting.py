"""Value + table formatting helpers used by the data layer."""

from __future__ import annotations


def fmt(value: object, prefix: str = "") -> str:
    """Format a scalar for a Markdown report.

    ``None`` → ``"N/A"``; ints get thousands separators; floats get two
    decimals; everything else is stringified. ``prefix`` (e.g. ``"$"``) is
    applied only to numbers. ``bool`` is checked before ``int`` because ``bool``
    is an ``int`` subclass and should render as ``True``/``False``.
    """
    if value is None:
        return "N/A"
    if isinstance(value, bool):
        return str(value)
    if isinstance(value, int):
        return f"{prefix}{value:,}"
    if isinstance(value, float):
        return f"{prefix}{value:,.2f}"
    return str(value)


def hist_table(df: object, heading: str, rows: list[str]) -> list[str]:
    """Render up to 4 fiscal years of the given rows as a Markdown table.

    Returns a list of lines (empty if the DataFrame is missing/empty) so callers
    can ``lines += hist_table(...)``.
    """
    if df is None or df.empty:
        return []
    cols = df.columns[:4]
    out = [
        heading,
        "| Metric |" + "".join(f" {c.year} |" for c in cols),
        "|---|" + "---|" * len(cols),
    ]
    for row in rows:
        if row in df.index:
            vals = "".join(f" {fmt(df.loc[row, c], '$')} |" for c in cols)
            out.append(f"| {row} |{vals}")
    out.append("")
    return out
