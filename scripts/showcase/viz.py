"""SVG chart primitives for the InvestSkill showcase.

Design rules applied (dataviz skill):
  * categorical hues assigned by ENTITY in fixed order, never cycled, never by rank
  * one axis per chart — no dual-scale charts anywhere
  * thin marks, 2px lines, >=8px markers, 4px rounded data-ends on bars
  * 2px surface gap between adjacent fills; 2px surface ring on overlapping marks
  * legend present for >=2 series; direct labels on <=4 series
  * recessive grid/axes; text wears ink tokens, never the series colour
  * every chart ships a table view (built by the page layer) and hover tooltips
Palette validated: node validate_palette.js "#2a78d6,#eb6834,#1baf7a,#4a3aa7"
  --mode light --pairs all  -> ALL CHECKS PASS (aqua contrast 2.74 -> direct labels
  supply the required relief).
"""
from html import escape

# entity -> categorical slot (fixed; never reassigned by rank)
SERIES = {
    "MU":   "#2a78d6",   # slot 1 blue
    "MRVL": "#eb6834",   # slot 2 orange
    "SKHY": "#1baf7a",   # slot 3 aqua  (direct-labelled: contrast 2.74)
    "SNDL": "#4a3aa7",   # slot 4 violet
}
INK, INK2, INK3 = "#16181a", "#4a4f55", "#767c85"
GRID, SURFACE = "#e6e8eb", "#ffffff"
GOOD, WARN, BAD = "#00692e", "#b35c00", "#c0161c"   # status only, always + label

_uid = [0]
def uid(p="c"):
    _uid[0] += 1
    return f"{p}{_uid[0]}"


def _fmt(v, dp=2, prefix="", suffix=""):
    if v is None: return "—"
    if abs(v) >= 1e12: return f"{prefix}{v/1e12:.2f}兆{suffix}"
    if abs(v) >= 1e9:  return f"{prefix}{v/1e9:.2f}B{suffix}"
    if abs(v) >= 1e6:  return f"{prefix}{v/1e6:.1f}M{suffix}"
    return f"{prefix}{v:,.{dp}f}{suffix}"


def figure(svg, caption, table_html=None, note=None, extra_cls=""):
    """Wrap a chart as a <figure> with caption, optional note and table view.

    ``extra_cls="dagfig"`` marks a flow diagram: the shell's CSS staggers its
    nodes in and animates its connectors once the figure scrolls into view.
    """
    tid = uid("t")
    t = ""
    if table_html:
        t = (f'<details class="tblview"><summary>檢視數據表</summary>'
             f'<div class="tblwrap" id="{tid}">{table_html}</div></details>')
    n = f'<p class="fignote">{note}</p>' if note else ""
    cls = f"fig {extra_cls}".strip()
    return (f'<figure class="{cls}"><div class="figbox">{svg}</div>'
            f'<figcaption>{caption}</figcaption>{n}{t}</figure>')


def wrap_cells(text, cells):
    """Greedy line-wrap by monospace display width (CJK/fullwidth glyph = 2).

    SVG has no text flow, so every diagram label is wrapped here. Latin runs stay
    whole; CJK breaks anywhere, which is correct for zh-TW.
    """
    import re as _re
    import unicodedata

    def w(s):
        return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in s)

    tokens = _re.findall(r"[A-Za-z0-9$%.,\-_/+()<>=:']+|\s+|.", str(text))
    lines, cur, cw = [], "", 0
    for t in tokens:
        if t.isspace():
            if cur:
                cur += " "
                cw += 1
            continue
        tw = w(t)
        if cur and cw + tw > cells:
            lines.append(cur.rstrip())
            cur, cw = "", 0
        cur += t
        cw += tw
    if cur.strip():
        lines.append(cur.rstrip())
    return lines or [""]


def aria_attr(label):
    """`role="img"` needs an accessible name; the flow diagrams supply one."""
    return f' aria-label="{escape(str(label))}"' if label else ""


def _arrow(x, y, col, size=6, down=False):
    """Solid arrowhead pointing right (or down)."""
    if down:
        return (f'<path d="M{x-size*.8:.1f},{y-size:.1f} L{x+size*.8:.1f},{y-size:.1f} '
                f'L{x:.1f},{y:.1f} Z" fill="{col}"/>')
    return (f'<path d="M{x-size:.1f},{y-size*.8:.1f} L{x-size:.1f},{y+size*.8:.1f} '
            f'L{x:.1f},{y:.1f} Z" fill="{col}"/>')


def legend(items):
    """items: [(label, colour)] — always present for >=2 series."""
    s = '<div class="lgd">'
    for lbl, col in items:
        s += (f'<span class="lgd__i"><span class="lgd__sw" style="background:{col}"></span>'
              f'<span>{escape(str(lbl))}</span></span>')
    return s + "</div>"


# ---------------------------------------------------------------- line chart
def line_chart(series, width=760, height=320, y_label="", y_fmt="{:.0f}",
               pad=(16, 88, 34, 62), band=None, hlines=(), x_ticks=6, y_ticks=5,
               area_first=False):
    """series: [{name, colour, points:[(x_label, y)], dash?, width?}]

    One shared y-axis. Direct end-labels on every series (this is also the
    contrast relief for the aqua slot). Crosshair+tooltip via shared JS.
    """
    pt, pr, pb, pl = pad
    iw, ih = width - pl - pr, height - pt - pb
    ys = [y for s in series for _, y in s["points"] if y is not None]
    if not ys: return ""
    lo, hi = min(ys), max(ys)
    if band: lo, hi = min(lo, band[0]), max(hi, band[1])
    for h in hlines: lo, hi = min(lo, h[0]), max(hi, h[0])
    if hi == lo: hi = lo + 1
    m = (hi - lo) * 0.10
    lo, hi = lo - m, hi + m

    def X(i, ln): return pl + (iw * i / max(1, ln - 1))
    def Y(v):     return pt + ih - (v - lo) / (hi - lo) * ih

    cid = uid("ln")
    o = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" '
         f'preserveAspectRatio="xMidYMid meet" data-chart="line" id="{cid}">']
    # y grid + ticks (recessive)
    for k in range(y_ticks + 1):
        v = lo + (hi - lo) * k / y_ticks
        y = Y(v)
        o.append(f'<line x1="{pl}" y1="{y:.1f}" x2="{pl+iw}" y2="{y:.1f}" '
                 f'stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{pl-8}" y="{y+4:.1f}" text-anchor="end" font-size="11" '
                 f'fill="{INK3}">{y_fmt.format(v)}</text>')
    if y_label:
        o.append(f'<text x="{pl-8}" y="{pt-6}" text-anchor="end" font-size="11" '
                 f'fill="{INK3}" font-weight="600">{escape(y_label)}</text>')
    # reference h-lines (status colours carry a label, never colour alone)
    for val, lbl, col in hlines:
        y = Y(val)
        o.append(f'<line x1="{pl}" y1="{y:.1f}" x2="{pl+iw}" y2="{y:.1f}" stroke="{col}" '
                 f'stroke-width="1.5" stroke-dasharray="5 4"/>')
        o.append(f'<text x="{pl+iw-4}" y="{y-6:.1f}" text-anchor="end" font-size="11" '
                 f'fill="{col}" font-weight="700">{escape(lbl)}</text>')
    # x ticks
    ln0 = len(series[0]["points"])
    step = max(1, ln0 // x_ticks)
    for i in range(0, ln0, step):
        lbl = series[0]["points"][i][0]
        o.append(f'<text x="{X(i,ln0):.1f}" y="{pt+ih+20}" text-anchor="middle" '
                 f'font-size="11" fill="{INK3}">{escape(str(lbl))}</text>')
    o.append(f'<line x1="{pl}" y1="{pt+ih}" x2="{pl+iw}" y2="{pt+ih}" stroke="{GRID}" stroke-width="1"/>')

    xs_json = []
    for si, s in enumerate(series):
        ps = s["points"]; ln = len(ps)
        pairs = [(X(i, ln), Y(y)) for i, (_, y) in enumerate(ps) if y is not None]
        if not pairs: continue
        d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pairs)
        col = s["colour"]
        if area_first and si == 0:
            o.append(f'<path d="{d} L{pairs[-1][0]:.1f},{pt+ih} L{pairs[0][0]:.1f},{pt+ih} Z" '
                     f'fill="{col}" fill-opacity=".10"/>')
        # pathLength="1" normalises the dash maths so the CSS draw-in animation is
        # exact for any path; a dashed series keeps its pattern and is not animated.
        dash = f' stroke-dasharray="{s["dash"]}"' if s.get("dash") else ""
        anim = "" if s.get("dash") else ' class="ch-draw" pathLength="1"'
        o.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{s.get("width",2)}" '
                 f'stroke-linejoin="round" stroke-linecap="round"{dash}{anim}/>')
        # end marker with 2px surface ring (overlap rule) + direct label
        ex, ey = pairs[-1]
        o.append(f'<circle cx="{ex:.1f}" cy="{ey:.1f}" r="4.5" fill="{col}" '
                 f'stroke="{SURFACE}" stroke-width="2"/>')
        o.append(f'<text x="{ex+9:.1f}" y="{ey+4:.1f}" font-size="12" font-weight="700" '
                 f'fill="{INK2}">{escape(s["name"])}</text>')
        xs_json.append({"name": s["name"], "colour": col,
                        "pts": [[round(X(i, ln), 1), round(Y(y), 1), ps[i][0], y]
                                for i, (_, y) in enumerate(ps) if y is not None]})
    # hover layer
    o.append(f'<g class="ch-hover"><line class="ch-cross" y1="{pt}" y2="{pt+ih}" '
             f'stroke="{INK3}" stroke-width="1" stroke-dasharray="3 3" style="display:none"/></g>')
    o.append(f'<rect class="ch-cap" x="{pl}" y="{pt}" width="{iw}" height="{ih}" fill="transparent"/>')
    o.append("</svg>")
    import json as _j
    o.append(f'<script type="application/json" class="ch-data">{_j.dumps({"series":xs_json,"pt":pt,"ih":ih,"fmt":y_fmt}, ensure_ascii=False)}</script>')
    return "".join(o)


# ------------------------------------------------------------ grouped h-bars
def hbar_chart(rows, width=760, bar_h=26, gap=12, pad=(14, 108, 26, 118),
               fmt="{:.1f}", vmax=None, vmin=0, zero_line=False):
    """rows: [(label, value, colour, note?)] — one axis, 4px rounded data-ends."""
    pt, pr, pb, pl = pad
    height = pt + pb + len(rows) * (bar_h + gap)
    iw = width - pl - pr
    vals = [v for _, v, *_ in rows if v is not None]
    hi = vmax if vmax is not None else max(vals + [0])
    lo = vmin if vmin is not None else min(vals + [0])
    if hi == lo: hi = lo + 1
    def X(v): return pl + (v - lo) / (hi - lo) * iw
    o = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" preserveAspectRatio="xMidYMid meet">']
    for k in range(5):
        v = lo + (hi - lo) * k / 4
        o.append(f'<line x1="{X(v):.1f}" y1="{pt-4}" x2="{X(v):.1f}" y2="{height-pb+2}" '
                 f'stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{X(v):.1f}" y="{height-pb+18}" text-anchor="middle" font-size="11" '
                 f'fill="{INK3}">{fmt.format(v)}</text>')
    if zero_line and lo < 0 < hi:
        o.append(f'<line x1="{X(0):.1f}" y1="{pt-4}" x2="{X(0):.1f}" y2="{height-pb+2}" '
                 f'stroke="{INK3}" stroke-width="1.5"/>')
    for i, row in enumerate(rows):
        lbl, v, col = row[0], row[1], row[2]
        note = row[3] if len(row) > 3 else ""
        y = pt + i * (bar_h + gap)
        o.append(f'<text x="{pl-10}" y="{y+bar_h/2+4:.1f}" text-anchor="end" font-size="12.5" '
                 f'font-weight="600" fill="{INK}">{escape(str(lbl))}</text>')
        if v is None:
            o.append(f'<text x="{pl+6}" y="{y+bar_h/2+4:.1f}" font-size="12" fill="{INK3}" '
                     f'font-style="italic">未評分（資料不足）</text>')
            continue
        x0, x1 = (X(min(0, v)), X(max(0, v))) if lo < 0 else (pl, X(v))
        w = max(2.0, x1 - x0)
        o.append(f'<rect x="{x0:.1f}" y="{y}" width="{w:.1f}" height="{bar_h}" rx="4" ry="4" '
                 f'fill="{col}"><title>{escape(str(lbl))}: {fmt.format(v)}{" · "+escape(str(note)) if note else ""}</title></rect>')
        o.append(f'<text x="{x1+8:.1f}" y="{y+bar_h/2+4:.1f}" font-size="12.5" font-weight="700" '
                 f'fill="{INK2}">{fmt.format(v)}{" "+escape(str(note)) if note else ""}</text>')
    o.append("</svg>")
    return "".join(o)


# ----------------------------------------------------------------- radar
def radar_chart(axes, series, size=390, rmax=10):
    """axes: [label]; series: [{name, colour, values:[..]}] — magnitude on one radial scale."""
    import math
    cx = cy = size / 2
    R = size / 2 - 56
    n = len(axes)
    def P(i, v):
        a = -math.pi / 2 + 2 * math.pi * i / n
        r = R * (v / rmax)
        return cx + r * math.cos(a), cy + r * math.sin(a)
    o = [f'<svg class="chart" viewBox="0 0 {size} {size}" role="img" preserveAspectRatio="xMidYMid meet">']
    for k in range(1, 6):
        r = R * k / 5
        pts = []
        for i in range(n):
            a = -math.pi / 2 + 2 * math.pi * i / n
            pts.append(f"{cx+r*math.cos(a):.1f},{cy+r*math.sin(a):.1f}")
        o.append(f'<polygon points="{" ".join(pts)}" fill="none" stroke="{GRID}" stroke-width="1"/>')
    for i, ax in enumerate(axes):
        x, y = P(i, rmax)
        o.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{GRID}" stroke-width="1"/>')
        lx, ly = P(i, rmax * 1.20)
        anch = "middle" if abs(lx - cx) < 12 else ("start" if lx > cx else "end")
        o.append(f'<text x="{lx:.1f}" y="{ly+4:.1f}" text-anchor="{anch}" font-size="12" '
                 f'font-weight="600" fill="{INK2}">{escape(ax)}</text>')
    for s in series:
        vals = s["values"]
        pts, has = [], False
        for i, v in enumerate(vals):
            if v is None: v = 0
            else: has = True
            x, y = P(i, v)
            pts.append(f"{x:.1f},{y:.1f}")
        if not has: continue
        col = s["colour"]
        o.append(f'<polygon points="{" ".join(pts)}" fill="{col}" fill-opacity=".14" '
                 f'stroke="{col}" stroke-width="2" stroke-linejoin="round"/>')
        for i, v in enumerate(vals):
            if v is None: continue
            x, y = P(i, v)
            o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4.5" fill="{col}" stroke="{SURFACE}" '
                     f'stroke-width="2"><title>{escape(s["name"])} · {escape(axes[i])}: {v}</title></circle>')
    o.append(f'<text x="{cx}" y="{cy+R+44}" text-anchor="middle" font-size="11" fill="{INK3}">'
             f'0（外圈 {rmax}）</text>')
    o.append("</svg>")
    return "".join(o)


# ------------------------------------------------------- football field
def football_field(rows, price, width=760, bar_h=30, gap=16, pad=(30, 30, 34, 196),
                   label="美元／股"):
    """rows: [(method, lo, hi, colour, note)] horizontal value ranges + price marker."""
    pt, pr, pb, pl = pad
    height = pt + pb + len(rows) * (bar_h + gap)
    iw = width - pl - pr
    allv = [v for _, a, b, *_ in rows for v in (a, b)] + [price]
    lo, hi = min(allv), max(allv)
    span = hi - lo or 1
    lo, hi = lo - span * .06, hi + span * .10
    def X(v): return pl + (v - lo) / (hi - lo) * iw
    o = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" preserveAspectRatio="xMidYMid meet">']
    for k in range(5):
        v = lo + (hi - lo) * k / 4
        o.append(f'<line x1="{X(v):.1f}" y1="{pt-8}" x2="{X(v):.1f}" y2="{height-pb+2}" '
                 f'stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{X(v):.1f}" y="{height-pb+18}" text-anchor="middle" font-size="11" '
                 f'fill="{INK3}">${v:,.0f}</text>')
    for i, (mth, a, b, col, note) in enumerate(rows):
        y = pt + i * (bar_h + gap)
        o.append(f'<text x="{pl-10}" y="{y+bar_h/2+1:.1f}" text-anchor="end" font-size="12.5" '
                 f'font-weight="600" fill="{INK}">{escape(mth)}</text>')
        if note:
            o.append(f'<text x="{pl-10}" y="{y+bar_h/2+15:.1f}" text-anchor="end" font-size="10.5" '
                     f'fill="{INK3}">{escape(note)}</text>')
        x0, x1 = X(min(a, b)), X(max(a, b))
        o.append(f'<rect x="{x0:.1f}" y="{y}" width="{max(3,x1-x0):.1f}" height="{bar_h}" rx="4" ry="4" '
                 f'fill="{col}" fill-opacity=".26" stroke="{col}" stroke-width="1.5">'
                 f'<title>{escape(mth)}: ${a:,.2f} – ${b:,.2f}</title></rect>')
        o.append(f'<text x="{x0-6:.1f}" y="{y+bar_h/2+4:.1f}" text-anchor="end" font-size="11" '
                 f'fill="{INK2}" font-weight="600">${a:,.0f}</text>')
        o.append(f'<text x="{x1+6:.1f}" y="{y+bar_h/2+4:.1f}" font-size="11" fill="{INK2}" '
                 f'font-weight="600">${b:,.0f}</text>')
    px = X(price)
    o.append(f'<line x1="{px:.1f}" y1="{pt-14}" x2="{px:.1f}" y2="{height-pb}" stroke="{INK}" '
             f'stroke-width="2"/>')
    o.append(f'<text x="{px:.1f}" y="{pt-19}" text-anchor="middle" font-size="11.5" '
             f'font-weight="800" fill="{INK}">現價 ${price:,.2f}</text>')
    o.append("</svg>")
    return "".join(o)


# ------------------------------------------------------------ scatter
def scatter_chart(pts, width=740, height=400, pad=(24, 34, 56, 74),
                  x_label="", y_label="", x_fmt="{:.0f}", y_fmt="{:.0f}",
                  x_ref=None, y_ref=None, quad_labels=None, log_x=False):
    """pts: [{name, colour, x, y, r?, note?}] — all-pairs-validated palette (<=4 entities)."""
    import math
    pt, pr, pb, pl = pad
    iw, ih = width - pl - pr, height - pt - pb
    xsv = [p["x"] for p in pts]; ysv = [p["y"] for p in pts]
    if log_x: xsv = [math.log10(max(1e-6, v)) for v in xsv]
    xlo, xhi = min(xsv), max(xsv); ylo, yhi = min(ysv), max(ysv)
    if x_ref is not None:
        r = math.log10(x_ref) if log_x else x_ref
        xlo, xhi = min(xlo, r), max(xhi, r)
    if y_ref is not None: ylo, yhi = min(ylo, y_ref), max(yhi, y_ref)
    xm, ym = (xhi - xlo) * .18 or 1, (yhi - ylo) * .18 or 1
    xlo, xhi, ylo, yhi = xlo - xm, xhi + xm, ylo - ym, yhi + ym
    def X(v):
        v = math.log10(max(1e-6, v)) if log_x else v
        return pl + (v - xlo) / (xhi - xlo) * iw
    def Y(v): return pt + ih - (v - ylo) / (yhi - ylo) * ih
    o = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" preserveAspectRatio="xMidYMid meet">']
    for k in range(5):
        yv = ylo + (yhi - ylo) * k / 4
        o.append(f'<line x1="{pl}" y1="{Y(yv):.1f}" x2="{pl+iw}" y2="{Y(yv):.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{pl-8}" y="{Y(yv)+4:.1f}" text-anchor="end" font-size="11" fill="{INK3}">{y_fmt.format(yv)}</text>')
    for k in range(5):
        xv = xlo + (xhi - xlo) * k / 4
        realx = 10 ** xv if log_x else xv
        o.append(f'<line x1="{pl + iw*k/4:.1f}" y1="{pt}" x2="{pl + iw*k/4:.1f}" y2="{pt+ih}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{pl + iw*k/4:.1f}" y="{pt+ih+20}" text-anchor="middle" font-size="11" fill="{INK3}">{x_fmt.format(realx)}</text>')
    if x_ref is not None:
        o.append(f'<line x1="{X(x_ref):.1f}" y1="{pt}" x2="{X(x_ref):.1f}" y2="{pt+ih}" stroke="{INK3}" stroke-width="1.5" stroke-dasharray="5 4"/>')
    if y_ref is not None:
        o.append(f'<line x1="{pl}" y1="{Y(y_ref):.1f}" x2="{pl+iw}" y2="{Y(y_ref):.1f}" stroke="{INK3}" stroke-width="1.5" stroke-dasharray="5 4"/>')
    if quad_labels:
        for (qx, qy, txt, anch) in quad_labels:
            o.append(f'<text x="{pl + iw*qx:.1f}" y="{pt + ih*qy:.1f}" text-anchor="{anch}" font-size="11" '
                     f'fill="{INK3}" font-style="italic">{escape(txt)}</text>')
    o.append(f'<text x="{pl+iw/2:.1f}" y="{height-8}" text-anchor="middle" font-size="12" font-weight="600" fill="{INK2}">{escape(x_label)}</text>')
    o.append(f'<text x="14" y="{pt+ih/2:.1f}" text-anchor="middle" font-size="12" font-weight="600" fill="{INK2}" transform="rotate(-90 14 {pt+ih/2:.1f})">{escape(y_label)}</text>')
    for p in pts:
        x, y = X(p["x"]), Y(p["y"])
        r = p.get("r", 11)
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{p["colour"]}" fill-opacity=".82" '
                 f'stroke="{SURFACE}" stroke-width="2"><title>{escape(p["name"])}: '
                 f'{x_label} {x_fmt.format(p["x"])} · {y_label} {y_fmt.format(p["y"])}'
                 f'{" · "+escape(str(p["note"])) if p.get("note") else ""}</title></circle>')
        o.append(f'<text x="{x:.1f}" y="{y-r-7:.1f}" text-anchor="middle" font-size="12" '
                 f'font-weight="800" fill="{INK}">{escape(p["name"])}</text>')
    o.append("</svg>")
    return "".join(o)


# -------------------------------------------------- insider dot timeline
def insider_timeline(events, price, width=760, height=330, pad=(26, 96, 46, 62)):
    """events: [(date, price, value, who, kind)] — sale prices vs today's price."""
    pt, pr, pb, pl = pad
    iw, ih = width - pl - pr, height - pt - pb
    if not events: return ""
    ev = sorted(events, key=lambda e: e[0])
    ps = [e[1] for e in ev] + [price]
    lo, hi = min(ps), max(ps)
    m = (hi - lo) * .12 or 1
    lo, hi = lo - m, hi + m
    d0, d1 = ev[0][0], ev[-1][0]
    from datetime import date as _d
    def _p(s): return _d.fromisoformat(s[:10])
    span = max(1, (_p(d1) - _p(d0)).days)
    def X(s): return pl + (_p(s) - _p(d0)).days / span * iw
    def Y(v): return pt + ih - (v - lo) / (hi - lo) * ih
    vmax = max(e[2] for e in ev) or 1
    o = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" preserveAspectRatio="xMidYMid meet">']
    for k in range(6):
        v = lo + (hi - lo) * k / 5
        o.append(f'<line x1="{pl}" y1="{Y(v):.1f}" x2="{pl+iw}" y2="{Y(v):.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{pl-8}" y="{Y(v)+4:.1f}" text-anchor="end" font-size="11" fill="{INK3}">${v:,.0f}</text>')
    o.append(f'<line x1="{pl}" y1="{Y(price):.1f}" x2="{pl+iw}" y2="{Y(price):.1f}" stroke="{INK}" stroke-width="2"/>')
    o.append(f'<text x="{pl+iw+6}" y="{Y(price)+4:.1f}" font-size="11.5" font-weight="800" fill="{INK}">現價 ${price:,.0f}</text>')
    for k in range(5):
        frac = k / 4
        from datetime import timedelta
        dd = _p(d0) + timedelta(days=int(span * frac))
        o.append(f'<text x="{pl+iw*frac:.1f}" y="{pt+ih+20}" text-anchor="middle" font-size="11" fill="{INK3}">{dd.isoformat()[5:]}</text>')
    for dt, pr_, val, who, kind in ev:
        x, y = X(dt), Y(pr_)
        r = 5 + 13 * (val / vmax) ** .5
        col = BAD if kind == "sale" else GOOD
        o.append(f'<line x1="{x:.1f}" y1="{y:.1f}" x2="{x:.1f}" y2="{Y(price):.1f}" stroke="{col}" '
                 f'stroke-width="1" stroke-opacity=".35"/>')
        o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}" fill-opacity=".68" '
                 f'stroke="{SURFACE}" stroke-width="2"><title>{escape(who)} · {dt[:10]} · '
                 f'${pr_:,.2f}／股 · {_fmt(val, 1, "$")}（{"賣出" if kind=="sale" else "買進"}）</title></circle>')
    o.append(f'<text x="{pl}" y="{height-8}" font-size="11" fill="{INK3}">'
             f'圓面積 ∝ 交易金額；紅色＝賣出（皆附標籤，不以顏色單獨表意）</text>')
    o.append("</svg>")
    return "".join(o)


# --------------------------------------------------------- column chart
def column_chart(cats, series, width=760, height=330, pad=(22, 20, 58, 70),
                 y_fmt="{:.0f}", y_label="", stacked=False, hlines=()):
    """Grouped/stacked columns. 2px surface gap between adjacent fills."""
    pt, pr, pb, pl = pad
    iw, ih = width - pl - pr, height - pt - pb
    if stacked:
        tot = [sum((s["values"][i] or 0) for s in series) for i in range(len(cats))]
        hi = max(tot + [0]); lo = 0
    else:
        vs = [v for s in series for v in s["values"] if v is not None]
        hi, lo = max(vs + [0]), min(vs + [0])
    for h in hlines: hi = max(hi, h[0])
    if hi == lo: hi = lo + 1
    pad_hi = hi + (hi - lo) * .12
    def Y(v): return pt + ih - (v - lo) / (pad_hi - lo) * ih
    gw = iw / len(cats)
    bw = (gw * 0.62) / (1 if stacked else len(series))
    o = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" preserveAspectRatio="xMidYMid meet">']
    for k in range(5):
        v = lo + (pad_hi - lo) * k / 4
        o.append(f'<line x1="{pl}" y1="{Y(v):.1f}" x2="{pl+iw}" y2="{Y(v):.1f}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<text x="{pl-8}" y="{Y(v)+4:.1f}" text-anchor="end" font-size="11" fill="{INK3}">{y_fmt.format(v)}</text>')
    if y_label:
        o.append(f'<text x="{pl-8}" y="{pt-6}" text-anchor="end" font-size="11" fill="{INK3}" font-weight="600">{escape(y_label)}</text>')
    for val, lbl, col in hlines:
        o.append(f'<line x1="{pl}" y1="{Y(val):.1f}" x2="{pl+iw}" y2="{Y(val):.1f}" stroke="{col}" '
                 f'stroke-width="1.5" stroke-dasharray="5 4"/>')
        o.append(f'<text x="{pl+iw-4}" y="{Y(val)-6:.1f}" text-anchor="end" font-size="11" fill="{col}" font-weight="700">{escape(lbl)}</text>')
    if lo < 0: o.append(f'<line x1="{pl}" y1="{Y(0):.1f}" x2="{pl+iw}" y2="{Y(0):.1f}" stroke="{INK3}" stroke-width="1.5"/>')
    for i, c in enumerate(cats):
        base = 0.0
        for si, s in enumerate(series):
            v = s["values"][i]
            if v is None: continue
            if stacked:
                x = pl + i * gw + (gw - bw) / 2
                y0, y1 = Y(base), Y(base + v)
                base += v
                h = abs(y0 - y1) - 2                       # 2px surface gap
            else:
                x = pl + i * gw + (gw * 0.19) + si * bw
                y1 = Y(max(0, v)); y0 = Y(min(0, v))
                h = abs(y0 - y1)
            if h <= 0: continue
            o.append(f'<rect x="{x+1:.1f}" y="{min(y0,y1):.1f}" width="{bw-2:.1f}" height="{h:.1f}" '
                     f'rx="4" ry="4" fill="{s["colour"]}"><title>{escape(str(c))} · '
                     f'{escape(s["name"])}: {y_fmt.format(v)}</title></rect>')
        o.append(f'<text x="{pl+i*gw+gw/2:.1f}" y="{pt+ih+19}" text-anchor="middle" font-size="11" fill="{INK3}">{escape(str(c))}</text>')
    o.append("</svg>")
    return "".join(o)


# ------------------------------------------------------------- gauge
def gauge(score, width=250, height=158, rmax=10, caption=""):
    """Single headline number with an arc — a stat tile, not a chart."""
    import math
    cx, cy, R = width / 2, height - 26, width / 2 - 26
    def arc(frm, to, col, w, cls=""):
        a0, a1 = math.pi * (1 - frm / rmax), math.pi * (1 - to / rmax)
        x0, y0 = cx + R * math.cos(a0), cy - R * math.sin(a0)
        x1, y1 = cx + R * math.cos(a1), cy - R * math.sin(a1)
        c = f' class="{cls}" pathLength="1"' if cls else ""
        return (f'<path d="M{x0:.1f},{y0:.1f} A{R},{R} 0 0 1 {x1:.1f},{y1:.1f}" fill="none" '
                f'stroke="{col}" stroke-width="{w}" stroke-linecap="round"{c}/>')
    col = BAD if score < 4 else (WARN if score < 6.5 else GOOD)
    o = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" preserveAspectRatio="xMidYMid meet">',
         arc(0, rmax, GRID, 12), arc(0, score, col, 12, cls="g-arc")]
    o.append(f'<text x="{cx}" y="{cy-8}" text-anchor="middle" font-size="40" font-weight="800" fill="{INK}">{score:.2f}</text>')
    o.append(f'<text x="{cx}" y="{cy+12}" text-anchor="middle" font-size="12" fill="{INK3}">／ {rmax}</text>')
    if caption:
        o.append(f'<text x="{cx}" y="{height-4}" text-anchor="middle" font-size="12" font-weight="700" fill="{col}">{escape(caption)}</text>')
    o.append("</svg>")
    return "".join(o)


# --------------------------------------------------------- heat table
def heat_table(col_heads, rows, fmt="{:.1f}", vmin=0, vmax=10, first_col="項目"):
    """rows: [(label, [values])]. Sequential = ONE hue light->dark (green ramp)."""
    def bg(v):
        if v is None: return ("#f7f8f9", INK3)
        t = max(0.0, min(1.0, (v - vmin) / (vmax - vmin)))
        # single-hue sequential ramp (brand green), light -> dark
        stops = ["#f2fbf6", "#dcf3e7", "#b9e7cf", "#8ed6b0", "#5cc08d", "#2ea86c", "#00914f", "#00723d"]
        c = stops[min(len(stops) - 1, int(t * len(stops)))]
        return (c, "#ffffff" if t > 0.62 else INK)
    h = f'<table class="heat"><thead><tr><th>{escape(first_col)}</th>'
    for c in col_heads: h += f"<th>{escape(str(c))}</th>"
    h += "</tr></thead><tbody>"
    for lbl, vals in rows:
        h += f'<tr><th scope="row">{escape(str(lbl))}</th>'
        for v in vals:
            c, t = bg(v)
            txt = fmt.format(v) if v is not None else "n/a"
            h += f'<td style="background:{c};color:{t}">{txt}</td>'
        h += "</tr>"
    return h + "</tbody></table>"


# ------------------------------------------------- pipeline (linear workflow)
KIND_COL = {"": None, "data": "#2a78d6", "gate": BAD, "audit": WARN, "out": GOOD}


def pipeline_chart(steps, width=880, accent="#00b14f", aria=""):
    """A left→right workflow: numbered stages joined by flowing connectors.

    steps: [{"n", "title", "sub", "meta"?, "kind"?}]
    ``kind`` only tints the badge — "gate" (blocked), "audit", "data", "out".
    Animation lives in CSS (``.fl-node`` / ``.fl-dash``); the SVG carries no
    <animate> element so the whole thing degrades to a static diagram.
    """
    n = len(steps)
    padx, gap = 5, 42
    nw = (width - 2 * padx - gap * (n - 1)) / n
    cells = max(10, int((nw - 26) / 5.9))
    wrapped = [wrap_cells(s.get("sub", ""), cells) for s in steps]
    lines = max(len(x) for x in wrapped)
    has_meta = any(s.get("meta") for s in steps)
    nh = 56 + 16 * lines + (20 if has_meta else 6)
    height = nh + 14
    o = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" '
         f'preserveAspectRatio="xMidYMid meet"'
         f'{aria_attr(aria)}>']
    mid = 7 + nh / 2
    for i, s in enumerate(steps):
        x = padx + i * (nw + gap)
        col = KIND_COL.get(s.get("kind", ""), None) or accent
        o.append(f'<g class="fl-node" style="animation-delay:{i*0.11:.2f}s">')
        o.append(f'<rect x="{x:.1f}" y="7" width="{nw:.1f}" height="{nh}" rx="14" ry="14" '
                 f'fill="{SURFACE}" stroke="{GRID}" stroke-width="1"/>')
        o.append(f'<rect x="{x:.1f}" y="7" width="{nw:.1f}" height="3.5" rx="1.8" ry="1.8" fill="{col}"/>')
        o.append(f'<circle cx="{x+26:.1f}" cy="{40}" r="13" fill="{col}"/>')
        o.append(f'<text x="{x+26:.1f}" y="{44.5}" text-anchor="middle" font-size="12.5" '
                 f'font-weight="800" fill="#fff">{escape(str(s["n"]))}</text>')
        o.append(f'<text x="{x+46:.1f}" y="{45}" font-size="13.5" font-weight="800" '
                 f'fill="{INK}">{escape(s["title"])}</text>')
        for k, ln in enumerate(wrapped[i]):
            o.append(f'<text x="{x+16:.1f}" y="{68+k*16}" font-size="11.5" '
                     f'fill="{INK2}">{escape(ln)}</text>')
        if s.get("meta"):
            o.append(f'<text x="{x+16:.1f}" y="{7+nh-13}" font-size="10.5" font-weight="700" '
                     f'fill="{col}">{escape(s["meta"])}</text>')
        o.append("</g>")
        if i < n - 1:
            x0, x1 = x + nw + 7, x + nw + gap - 9
            o.append(f'<line class="fl-dash" x1="{x0:.1f}" y1="{mid:.1f}" x2="{x1:.1f}" '
                     f'y2="{mid:.1f}" stroke="{accent}" stroke-width="2.4" stroke-linecap="round"/>')
            o.append(_arrow(x1 + 8, mid, accent))
    o.append("</svg>")
    return "".join(o)


# ------------------------------------- phase ladder (full-report's five stages)
def phase_chart(phases, width=920, accent="#00b14f", head="", foot="", aria=""):
    """The full-report dependency ladder.

    phases: [{"label", "score"?, "note"?, "modules": [str]}]
    One shared snapshot feeds every phase (the bar across the top), the phases run
    in order (the chevrons between them), and one audited verdict comes out (the
    band at the bottom). That shape is the architecture, so it is drawn, not told.
    """
    n = len(phases)
    padx, gap = 5, 14
    cw = (width - 2 * padx - gap * (n - 1)) / n
    lcells = max(8, int((cw - 18) / 6.2))
    labels = [wrap_cells(p["label"], lcells) for p in phases]
    llines = max(len(x) for x in labels)
    nmods = max(len(p["modules"]) for p in phases)
    head_h, hgap = 38, 26
    ph_y = head_h + hgap
    ph_h = 30 + 15 * llines + (26 if any(p.get("score") is not None for p in phases) else 0)
    mod_y = ph_y + ph_h + 10
    mod_h, mod_gap = 27, 6
    foot_y = mod_y + nmods * (mod_h + mod_gap) + 20
    height = foot_y + 44 + 4
    o = [f'<svg class="chart" viewBox="0 0 {width} {height}" role="img" '
         f'preserveAspectRatio="xMidYMid meet"'
         f'{aria_attr(aria)}>']
    # shared-snapshot bar
    if head:
        o.append('<g class="fl-node">')
        o.append(f'<rect x="{padx}" y="0" width="{width-2*padx:.1f}" height="{head_h}" rx="12" ry="12" '
                 f'fill="#e6f7ee" stroke="#b9e7cf" stroke-width="1.5"/>')
        o.append(f'<text x="{width/2:.1f}" y="{head_h/2+5:.1f}" text-anchor="middle" font-size="12.5" '
                 f'font-weight="800" fill="#00692e">{escape(head)}</text>')
        o.append("</g>")
    for i, p in enumerate(phases):
        x = padx + i * (cw + gap)
        cx = x + cw / 2
        if head:
            o.append(f'<line class="fl-dash" x1="{cx:.1f}" y1="{head_h+3}" x2="{cx:.1f}" '
                     f'y2="{ph_y-9}" stroke="{accent}" stroke-width="2" stroke-linecap="round"/>')
            o.append(_arrow(cx, ph_y - 2, accent, down=True))
        o.append(f'<g class="fl-node" style="animation-delay:{i*0.09:.2f}s">')
        o.append(f'<rect x="{x:.1f}" y="{ph_y}" width="{cw:.1f}" height="{ph_h}" rx="12" ry="12" '
                 f'fill="#fff" stroke="{accent}" stroke-width="1.5"/>')
        for k, ln in enumerate(labels[i]):
            o.append(f'<text x="{cx:.1f}" y="{ph_y+21+k*15}" text-anchor="middle" font-size="12" '
                     f'font-weight="800" fill="{INK}">{escape(ln)}</text>')
        if p.get("score") is not None:
            o.append(f'<text x="{cx:.1f}" y="{ph_y+ph_h-9}" text-anchor="middle" font-size="21" '
                     f'font-weight="800" fill="{accent}">{p["score"]:.1f}</text>')
        o.append("</g>")
        for k, m in enumerate(p["modules"]):
            my = mod_y + k * (mod_h + mod_gap)
            o.append(f'<g class="fl-node" style="animation-delay:{0.2+i*0.05+k*0.04:.2f}s">')
            o.append(f'<rect x="{x:.1f}" y="{my}" width="{cw:.1f}" height="{mod_h}" rx="8" ry="8" '
                     f'fill="{SURFACE}" stroke="{GRID}" stroke-width="1"/>')
            o.append(f'<text x="{cx:.1f}" y="{my+18}" text-anchor="middle" font-size="10.5" '
                     f'font-family="ui-monospace,Menlo,monospace" fill="{INK2}">{escape(m)}</text>')
            o.append("</g>")
        if i < n - 1:
            ax = x + cw + gap / 2
            ay = ph_y + ph_h / 2
            o.append(f'<path d="M{ax-4:.1f},{ay-6:.1f} L{ax+3:.1f},{ay:.1f} L{ax-4:.1f},{ay+6:.1f}" '
                     f'fill="none" stroke="{INK3}" stroke-width="2" stroke-linecap="round" '
                     f'stroke-linejoin="round" class="fl-pulse"/>')
        if foot:
            o.append(f'<line class="fl-dash" x1="{cx:.1f}" y1="{foot_y-17}" x2="{cx:.1f}" '
                     f'y2="{foot_y-7}" stroke="{accent}" stroke-width="2" stroke-linecap="round"/>')
            o.append(_arrow(cx, foot_y - 1, accent, down=True))
    if foot:
        o.append('<g class="fl-node" style="animation-delay:.55s">')
        o.append(f'<rect x="{padx}" y="{foot_y}" width="{width-2*padx:.1f}" height="42" rx="12" ry="12" '
                 f'fill="#00692e"/>')
        o.append(f'<text x="{width/2:.1f}" y="{foot_y+26}" text-anchor="middle" font-size="12.5" '
                 f'font-weight="800" fill="#fff">{escape(foot)}</text>')
        o.append("</g>")
    o.append("</svg>")
    return "".join(o)


# --------------------------------------------------- presence matrix (dot grid)
def matrix_dots(cols, rows, width=760, cell=30, label_w=232, accent="#00b14f", aria=""):
    """rows: [(label, [bool per col], tail)] — which workflow used which framework.

    A presence matrix, not a heatmap: one hue, filled = used, hollow ring = not.
    """
    grid_w = cell * len(cols)
    tail_x = label_w + grid_w + 16
    height = 30 + len(rows) * cell + 8
    o = [f'<svg class="chart" viewBox="0 0 {max(width, tail_x+96)} {height}" role="img" '
         f'preserveAspectRatio="xMidYMid meet"'
         f'{aria_attr(aria)}>']
    for j, c in enumerate(cols):
        o.append(f'<text x="{label_w+cell*j+cell/2:.1f}" y="16" text-anchor="middle" font-size="11.5" '
                 f'font-weight="800" fill="{INK2}">{escape(str(c))}</text>')
    o.append(f'<text x="{tail_x}" y="16" font-size="11" font-weight="700" fill="{INK3}">用量</text>')
    for i, (lbl, flags, tail) in enumerate(rows):
        y = 30 + i * cell
        if i % 2 == 0:
            o.append(f'<rect x="0" y="{y}" width="{max(width, tail_x+96)}" height="{cell}" '
                     f'fill="{SURFACE}"/>')
        o.append(f'<text x="{label_w-14}" y="{y+cell/2+4:.1f}" text-anchor="end" font-size="11.5" '
                 f'font-family="ui-monospace,Menlo,monospace" fill="{INK}">{escape(str(lbl))}</text>')
        for j, on in enumerate(flags):
            cx, cy = label_w + cell * j + cell / 2, y + cell / 2
            if on:
                o.append(f'<circle class="fl-cell" cx="{cx:.1f}" cy="{cy:.1f}" r="7" fill="{accent}" '
                         f'style="animation-delay:{min(0.6, i*0.03+j*0.02):.2f}s">'
                         f'<title>{escape(str(lbl))} · {escape(str(cols[j]))}：使用</title></circle>')
            else:
                o.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="4.5" fill="none" stroke="{GRID}" '
                         f'stroke-width="1.5"/>')
        o.append(f'<text x="{tail_x}" y="{y+cell/2+4:.1f}" font-size="11" font-weight="700" '
                 f'fill="{INK2}">{escape(str(tail))}</text>')
    o.append("</svg>")
    return "".join(o)


def simple_table(heads, rows, cls="dt", align=None):
    a = align or ["left"] + ["right"] * (len(heads) - 1)
    h = f'<table class="{cls}"><thead><tr>'
    for i, c in enumerate(heads):
        h += f'<th style="text-align:{a[i]}">{c}</th>'
    h += "</tr></thead><tbody>"
    for r in rows:
        h += "<tr>"
        for i, c in enumerate(r):
            tag = "th" if i == 0 else "td"
            sc = ' scope="row"' if i == 0 else ""
            h += f'<{tag}{sc} style="text-align:{a[i] if i < len(a) else "right"}">{c}</{tag}>'
        h += "</tr>"
    return h + "</tbody></table>"
