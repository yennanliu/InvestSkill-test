"""Shared context: loaded data, derived facts, formatters, provenance header."""
import json
from datetime import date
from pathlib import Path

import derive

FIXTURES = Path(__file__).resolve().parent / "fixtures"

RAW = json.loads((FIXTURES / "snapshot.json").read_text())
C = derive.DERIVED
T = ["MU", "SKHY", "MRVL", "SNDL"]
ASOF = "2026-07-29"
KRW = 1380.0

NAMES = {
    "MU":   ("Micron Technology, Inc.", "美光科技"),
    "SKHY": ("SK hynix Inc. (ADR)", "SK 海力士"),
    "MRVL": ("Marvell Technology, Inc.", "邁威爾科技"),
    "SNDL": ("SNDL Inc.", "SNDL"),
}
ROLE = {
    "MU":   "HBM／DRAM 純度最高的美股標的",
    "SKHY": "HBM 市佔龍頭，2026-07-10 才在美掛牌 ADR",
    "MRVL": "客製化 ASIC ／ 光電互連，記憶體循環的「賣鏟人」",
    "SNDL": "對照組：與 AI 完全無關的深度價值標的",
}

BENCH = RAW["_bench"]

# --------------------------------------------------- yesterday's gap-down
GAP = {}
for tk in T:
    i = RAW[tk]["info"]
    cp, pc = i.get("currentPrice"), i.get("previousClose")
    GAP[tk] = (cp / pc - 1) * 100 if cp and pc else None

# --------------------------------------------------- drawdown from 52w high
DD = {}
for tk in T:
    i = RAW[tk]["info"]
    cp, hi = i.get("currentPrice"), i.get("fiftyTwoWeekHigh")
    DD[tk] = (cp / hi - 1) * 100 if cp and hi else None

# --------------------------------------------------- earnings dates
EARN = {}
for tk in T:
    cal = RAW[tk].get("calendar") or {}
    ed = cal.get("Earnings Date") or ""
    d = ed.replace("[datetime.date(", "").replace(")]", "").split(", ")
    try:
        EARN[tk] = {"date": date(int(d[0]), int(d[1]), int(d[2])).isoformat(),
                    "eps_avg": cal.get("Earnings Average"), "eps_hi": cal.get("Earnings High"),
                    "eps_lo": cal.get("Earnings Low"), "rev_avg": cal.get("Revenue Average"),
                    "rev_hi": cal.get("Revenue High"), "rev_lo": cal.get("Revenue Low")}
    except Exception:
        EARN[tk] = {"date": None}
    EARN[tk]["dte"] = ((date.fromisoformat(EARN[tk]["date"]) - date.fromisoformat(ASOF)).days
                       if EARN[tk].get("date") else None)

# --------------------------------------------------- cyclical normalisation
def cyc(tk):
    fin = RAW[tk]["financials"]; i = RAW[tk]["info"]
    rate = KRW if tk == "SKHY" else 1.0
    rows = []
    for c in sorted(fin.keys(), reverse=True):
        f = fin[c] or {}
        rv, op, ni = f.get("Total Revenue"), f.get("Operating Income"), f.get("Net Income")
        if rv is None: continue
        rows.append({"fy": c, "rev": rv / rate, "op": (op or 0) / rate, "ni": (ni or 0) / rate,
                     "opm": (op / rv if op is not None and rv else None),
                     "nim": (ni / rv if ni is not None and rv else None)})
    opms = [r["opm"] for r in rows if r["opm"] is not None]
    pos = [o for o in opms if o > 0]
    ttm_rev = i["totalRevenue"] / rate
    ttm_ni = i["netIncomeToCommon"] / rate
    nis = [r["ni"] for r in rows]
    avg_ni = sum(nis) / len(nis) if nis else None
    now_opm = i.get("operatingMargins")
    full = sum(opms) / len(opms) if opms else None
    ex = sum(pos) / len(pos) if pos else None
    mid = ((ex + now_opm) / 2) if (ex and now_opm) else None
    sh = i["sharesOutstanding"]
    def grid(opm):
        if not opm: return None
        ni = ttm_rev * opm * 0.85
        return {"opm": opm, "ni": ni, **{f"m{m}": ni * m / sh for m in (10, 12, 15, 18)}}
    return {"rows": rows, "ttm_rev": ttm_rev, "ttm_ni": ttm_ni, "avg_ni": avg_ni,
            "x_avg": (ttm_ni / avg_ni if avg_ni and avg_ni > 0 else None),
            "opm_full": full, "opm_ex": ex, "opm_mid": mid, "opm_now": now_opm,
            "scen": {"revert": grid(full), "ex_trough": grid(ex),
                     "structural": grid(mid), "peak": grid(now_opm)},
            "shares": sh}

CYC = {tk: cyc(tk) for tk in T}

# --------------------------------------------------- insider aggregates
def insiders(tk):
    it = RAW[tk].get("insider_tx") or {}
    sells, buys, other = [], [], []
    for v in it.values():
        txt = v.get("Text") or ""
        val = v.get("Value") or 0
        sh = v.get("Shares") or 0
        px = None
        if "price" in txt:
            import re
            nums = re.findall(r"(\d[\d,]*\.\d+|\d[\d,]*)", txt.split("price")[1])
            if nums:
                px = sum(float(n.replace(",", "")) for n in nums[:2]) / min(2, len(nums))
        rec = {"who": v.get("Insider"), "role": v.get("Position"), "shares": sh,
               "value": val, "date": (v.get("Start Date") or "")[:10], "px": px, "text": txt}
        if "Sale" in txt: sells.append(rec)
        elif "Purchase" in txt or "Buy" in txt: buys.append(rec)
        else: other.append(rec)
    return {"sells": sorted(sells, key=lambda r: r["date"], reverse=True),
            "buys": buys, "other": other,
            "sell_total": sum(r["value"] for r in sells),
            "sell_shares": sum(r["shares"] for r in sells),
            "buy_total": sum(r["value"] for r in buys),
            "n_sell": len(sells), "n_buy": len(buys)}

INS = {tk: insiders(tk) for tk in T}

# --------------------------------------------------- institutional
def inst(tk):
    ih = RAW[tk].get("inst_holders") or {}
    rows = []
    for v in ih.values():
        rows.append({"holder": v.get("Holder"), "pct": v.get("pctHeld"),
                     "shares": v.get("Shares"), "value": v.get("Value"),
                     "chg": v.get("pctChange"), "asof": (v.get("Date Reported") or "")[:10]})
    return sorted(rows, key=lambda r: -(r["pct"] or 0))

INST = {tk: inst(tk) for tk in T}

# --------------------------------------------------- latest balance sheet
# yfinance's `bookValue` field agrees with the filed balance sheet for MU and
# MRVL (ratio 1.000) but understates SNDL's by 27%. Everything below is derived
# from the filed quarterly balance sheet so the reports never inherit that gap.
BS = {}
for tk in T:
    q = RAW[tk].get("quarterly_balance_sheet") or {}
    if not q:
        BS[tk] = None
        continue
    cols = sorted(q.keys(), reverse=True)
    rate = KRW if tk == "SKHY" else 1.0
    c0 = cols[0]
    eq = (q[c0] or {}).get("Stockholders Equity")
    sh = (q[c0] or {}).get("Ordinary Shares Number") or RAW[tk]["info"].get("sharesOutstanding")
    cash = (q[c0] or {}).get("Cash And Cash Equivalents")
    px = RAW[tk]["info"]["currentPrice"]
    mc = RAW[tk]["info"]["marketCap"]
    series = [(c, ((q[c] or {}).get("Stockholders Equity") or 0) / rate) for c in reversed(cols)]
    BS[tk] = {
        "asof": c0,
        "equity": eq / rate if eq else None,
        "shares": sh,
        "bv_ps": (eq / rate / sh) if (eq and sh) else None,
        "cash": cash / rate if cash else None,
        "pb": (mc / (eq / rate)) if eq else None,          # market cap / filed equity
        "pb_yf": RAW[tk]["info"].get("priceToBook"),
        "bv_yf": RAW[tk]["info"].get("bookValue"),
        "cash_cover": (cash / rate / mc) if cash else None,
        "series": series,
        # erosion over the last two reported quarters, annualised
        "erosion_2q": (series[-1][1] - series[-3][1]) if len(series) >= 3 else None,
        "erosion_ann": ((series[-1][1] - series[-3][1]) * 2) if len(series) >= 3 else None,
    }
    b = BS[tk]
    if b["equity"] and b["erosion_ann"] is not None:
        b["erosion_pct"] = b["erosion_ann"] / b["equity"] * 100
    b["bv_gap"] = ((b["bv_ps"] / b["bv_yf"]) if (b["bv_ps"] and b["bv_yf"]) else None)


def recos(tk):
    rc = RAW[tk].get("recos") or {}
    return [rc[k] for k in sorted(rc.keys(), key=lambda x: int(x))]

RECO = {tk: recos(tk) for tk in T}

# --------------------------------------------------- formatters
def money(v, dp=2, unit=True):
    if v is None: return "—"
    a = abs(v)
    if unit and a >= 1e12: return f"${v/1e12:,.2f} 兆"
    if unit and a >= 1e9:  return f"${v/1e9:,.2f}B"
    if unit and a >= 1e6:  return f"${v/1e6:,.1f}M"
    return f"${v:,.{dp}f}"

def pc(v, dp=1, sign=False):
    if v is None: return "—"
    s = "+" if (sign and v > 0) else ""
    return f"{s}{v:,.{dp}f}%"

def pcf(v, dp=1, sign=False):
    """fraction -> percent"""
    return "—" if v is None else pc(v * 100, dp, sign)

def num(v, dp=2):
    return "—" if v is None else f"{v:,.{dp}f}"

def cls(v, invert=False):
    if v is None: return ""
    good = (v < 0) if invert else (v > 0)
    return "up" if good else ("dn" if v != 0 else "fl")

def arrow(v):
    return "▲" if (v or 0) > 0 else ("▼" if (v or 0) < 0 else "▬")

def st(kind, txt):
    ico = {"good": "✅", "warn": "⚠", "bad": "🚩", "neut": "▬"}[kind]
    return f'<span class="st st--{kind}">{ico} {txt}</span>'

def _dw(s):
    """Display width in monospace cells: CJK / fullwidth glyphs occupy two."""
    import unicodedata
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in s)


def _pad(s, w):
    """Left-align to w display cells (not len(), which miscounts CJK)."""
    return s + " " * max(0, w - _dw(s))


def sig_block(rows, title="INVESTMENT SIGNAL"):
    """Render the InvestSkill house signal block, padded by display width so the
    box borders line up even when values contain CJK text."""
    body = []
    for r in rows:
        if r is None:
            body.append(None)
        else:
            k, v = r
            body.append(" " + _pad(f"{k}:", 13) + str(v) + " ")
    w = max([_dw(x) for x in body if x] + [_dw(title) + 2])
    out = ["╔" + "═" * w + "╗", "║" + _pad(" " * ((w - _dw(title)) // 2) + title, w) + "║",
           "╠" + "═" * w + "╣"]
    for x in body:
        out.append("╠" + "═" * w + "╣" if x is None else "║" + _pad(x, w) + "║")
    out.append("╚" + "═" * w + "╝")
    return '<div class="sig"><pre>' + "\n".join(out) + "</pre></div>"

def prov(source, retrieval, confidence, extra=""):
    return f"""<div class="call call--ink"><div class="call__h">📋 Data &amp; Sources — 資料來源與可信度</div>
<table class="dt dt--sm" style="margin-top:8px"><tbody>
<tr><th scope="row" style="width:112px">As of</th><td style="text-align:left">{ASOF}（收盤後快照）</td></tr>
<tr><th scope="row">Source</th><td style="text-align:left">{source}</td></tr>
<tr><th scope="row">Retrieval</th><td style="text-align:left">{retrieval}</td></tr>
<tr><th scope="row">Confidence</th><td style="text-align:left">{confidence}</td></tr>
</tbody></table>{extra}</div>"""

# composite interpretation
def interp(score):
    if score >= 8.0: return ("good", "強力買進 Strong Buy")
    if score >= 6.5: return ("good", "買進 Buy")
    if score >= 5.0: return ("warn", "持有／觀察 Hold / Watch")
    if score >= 3.5: return ("bad", "減碼 Underweight")
    return ("bad", "賣出／避開 Sell / Avoid")

def screener_signal(total):
    if total >= 7.5: return ("good", "🟢 STRONG BUY")
    if total >= 6.0: return ("good", "🟢 BUY")
    if total >= 4.5: return ("warn", "🟡 HOLD")
    if total >= 3.0: return ("bad", "🔴 AVOID")
    return ("bad", "🔴 STRONG AVOID")
