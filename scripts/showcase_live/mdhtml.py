"""A small Markdown → HTML converter for LLM-written reports. Standard library only.

It is not a CommonMark implementation. It covers what the reports contain —
headings, paragraphs, nested lists, pipe tables, fenced code, block quotes,
rules, and inline bold / italic / code / links — and it is strict about two
things the published site checks:

  * every character of the source is HTML-escaped, so model output can never
    inject markup; only http(s) links become anchors;
  * heading levels are normalised. Models jump between ``#`` and ``####`` at
    will; here every heading becomes ``<h3>`` or ``<h4>`` under the page's own
    ``<h2>``, and an ``<h4>`` is only used once an ``<h3>`` has opened.
"""
from __future__ import annotations

import html
import re

_FENCE = re.compile(r"^\s*(```+|~~~+)\s*([\w+-]*)\s*$")
_HEADING = re.compile(r"^\s{0,3}(#{1,6})\s+(.*?)\s*#*\s*$")
_RULE = re.compile(r"^\s{0,3}([-*_])(\s*\1){2,}\s*$")
_ITEM = re.compile(r"^(\s*)([-*+]|\d{1,3}[.)])\s+(.*)$")
_TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{2,}:?\s*(\|\s*:?-{2,}:?\s*)*\|?\s*$")
_CODE_SPAN = re.compile(r"`([^`\n]+)`")
_LINK = re.compile(r"\[([^\]\n]+)\]\((https?://[^\s)]+)\)")
_BOLD = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*")
_ITALIC = re.compile(r"(?<![*\w])\*(?=[^\s*])(.+?)(?<=[^\s*])\*(?![*\w])")
_BR = re.compile(r"&lt;br\s*/?&gt;", re.I)


def inline(text: str) -> str:
    """Escape ``text`` and apply inline formatting."""
    spans: list[str] = []

    def stash(match: re.Match) -> str:
        spans.append("<code>" + html.escape(match.group(1), quote=False) + "</code>")
        return f"\x00{len(spans) - 1}\x00"

    text = _CODE_SPAN.sub(stash, text)
    text = html.escape(text, quote=True)
    text = _LINK.sub(lambda m: f'<a href="{m.group(2)}" rel="noopener">{m.group(1)}</a>', text)
    text = _BOLD.sub(r"<strong>\1</strong>", text)
    text = _ITALIC.sub(r"<em>\1</em>", text)
    text = _BR.sub("<br>", text)
    text = text.replace("[ ] ", "☐ ").replace("[x] ", "☑ ").replace("[X] ", "☑ ")
    return re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], text)


def _cells(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|") and not line.endswith("\\|"):
        line = line[:-1]
    return [c.strip().replace("\\|", "|") for c in re.split(r"(?<!\\)\|", line)]


def _table(rows: list[str]) -> str:
    head = _cells(rows[0])
    out = ['<div class="tblwrap"><table class="dt dt--sm"><thead><tr>']
    out += [f'<th scope="col" style="text-align:left">{inline(c)}</th>' for c in head]
    out.append("</tr></thead><tbody>")
    for row in rows[2:]:
        cells = _cells(row)
        cells = (cells + [""] * len(head))[:max(len(head), 1)]
        out.append("<tr>" + "".join(
            f'<td style="text-align:left">{inline(c)}</td>' for c in cells) + "</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def _list(items: list[tuple[int, str, str]]) -> str:
    """items: (indent, 'ul'|'ol', text). Nested by indent, always balanced."""
    out: list[str] = []
    stack: list[tuple[int, str]] = []          # (indent, tag) of open lists
    for indent, tag, text in items:
        while stack and indent < stack[-1][0]:
            out.append(f"</li></{stack.pop()[1]}>")
        if stack and indent == stack[-1][0]:
            out.append("</li>")
            if tag != stack[-1][1]:            # bullet ↔ number at the same depth
                out.append(f"</{stack.pop()[1]}>")
        if not stack or indent > stack[-1][0] or tag != stack[-1][1]:
            out.append(f"<{tag}>")
            stack.append((indent, tag))
        out.append(f"<li>{inline(text)}")
    while stack:
        out.append(f"</li></{stack.pop()[1]}>")
    return "".join(out)


def convert(markdown: str) -> str:
    """Convert a Markdown fragment to HTML (headings become h3 / h4)."""
    lines = markdown.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out: list[str] = []
    para: list[str] = []
    seen_h3 = False
    i = 0

    def flush() -> None:
        if para:
            out.append("<p>" + "\n".join(inline(p) for p in para) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]

        fence = _FENCE.match(line)
        if fence:
            flush()
            marker, lang = fence.group(1), fence.group(2).lower()
            body: list[str] = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith(marker[:3]):
                body.append(lines[i])
                i += 1
            i += 1                               # closing fence (or end of input)
            label = ' aria-label="Mermaid 原始碼"' if lang == "mermaid" else ""
            out.append(f'<pre class="lv-code"{label}><code>'
                       + html.escape("\n".join(body), quote=False) + "</code></pre>")
            continue

        if not line.strip():
            flush()
            i += 1
            continue

        heading = _HEADING.match(line)
        if heading:
            flush()
            level = 3 if (len(heading.group(1)) <= 2 or not seen_h3) else 4
            seen_h3 = seen_h3 or level == 3
            out.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
            i += 1
            continue

        if _RULE.match(line):
            flush()
            out.append("<hr>")
            i += 1
            continue

        if "|" in line and i + 1 < len(lines) and _TABLE_SEP.match(lines[i + 1]) \
                and "-" in lines[i + 1]:
            flush()
            rows = [line, lines[i + 1]]
            i += 2
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append(lines[i])
                i += 1
            out.append(_table(rows))
            continue

        if line.lstrip().startswith(">"):
            flush()
            quote: list[str] = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                quote.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            text = "\n".join(inline(q) for q in quote if q.strip())
            out.append(f"<blockquote><p>{text}</p></blockquote>")
            continue

        if _ITEM.match(line):
            flush()
            items: list[tuple[int, str, str]] = []
            while i < len(lines):
                m = _ITEM.match(lines[i])
                if m:
                    indent = len(m.group(1).replace("\t", "    "))
                    tag = "ul" if m.group(2) in "-*+" else "ol"
                    items.append((indent, tag, m.group(3)))
                    i += 1
                elif lines[i].strip() and lines[i].startswith((" ", "\t")) and items \
                        and not _FENCE.match(lines[i]):
                    indent, tag, text = items[-1]          # continuation line
                    items[-1] = (indent, tag, text + " " + lines[i].strip())
                    i += 1
                else:
                    break
            out.append(_list(items))
            continue

        para.append(line.strip())
        i += 1

    flush()
    return "\n".join(out)
