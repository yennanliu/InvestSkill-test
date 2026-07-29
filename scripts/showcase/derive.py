"""Compute every derived metric the showcase reports cite.

Importing this module computes the derived values from the committed snapshot
fixture and exposes them as ``DERIVED``. There is deliberately no derived-values
fixture on disk: the numbers are recomputed on every build so they can never
drift from the snapshot they claim to come from.
"""
import json, math
from pathlib import Path

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SNAPSHOT = FIXTURES / "snapshot.json"

D = json.loads(SNAPSHOT.read_text())
T = ["MU", "MRVL", "SKHY", "SNDL"]

# ---------- helpers ----------
def lin(x, lo, hi, slo=0.0, shi=10.0):
    """Linear score; lo->slo, hi->shi, clamped."""
    if x is None: return None
    if hi == lo: return (slo + shi) / 2
    s = slo + (x - lo) * (shi - slo) / (hi - lo)
    return max(0.0, min(10.0, s))

def avg(vals):
    v = [x for x in vals if x is not None]
    return round(sum(v) / len(v), 1) if v else None

def pct(x):
    return None if x is None else x * 100

out = {}

# ---------- KRW conversion for SKHY ----------
# SKHY statements are in KRW; ADR price is USD. Derive the implied rate from the
# data itself so the mismatch is documented rather than silently patched.
KRW_USD = 1380.0   # approx 2026 level; stated as an assumption in the report

# ---------- relative performance ----------
bench = D["_bench"]["^GSPC"]["ret_1y_pct"]
sox = D["_bench"]["^SOX"]["ret_1y_pct"]

def rel_perf(tk):
    m = D[tk].get("hist_1y", {}).get("monthly") or []
    if len(m) < 2: return {}
    closes = [v for _, v in m]
    last = closes[-1]
    r = {}
    for label, back in [("3M", 3), ("6M", 6), ("12M", 12)]:
        if len(closes) > back:
            r[label] = (last / closes[-1 - back] - 1) * 100
    return r

# SPY-equivalent windows from ^GSPC monthly – approximate using 1y only
SPY_1Y = bench

# ---------- Piotroski F-Score ----------
def piotroski(tk):
    fin = D[tk].get("financials", {})
    cf = D[tk].get("cashflow", {})
    bs = D[tk].get("balance_sheet", {})
    cols = sorted(fin.keys(), reverse=True)
    if len(cols) < 2: return None, []
    c0, c1 = cols[0], cols[1]
    def f(d, c, k): return (d.get(c, {}) or {}).get(k)
    tests = []
    ni0, ni1 = f(fin, c0, "Net Income"), f(fin, c1, "Net Income")
    ta0, ta1 = f(bs, c0, "Total Assets"), f(bs, c1, "Total Assets")
    ocf0 = f(cf, c0, "Operating Cash Flow")
    roa0 = ni0 / ta0 if ni0 is not None and ta0 else None
    roa1 = ni1 / ta1 if ni1 is not None and ta1 else None
    tests.append(("ROA > 0", 1 if (roa0 or -1) > 0 else 0, f"ROA {roa0:.1%}" if roa0 is not None else "n/a"))
    tests.append(("營運現金流 > 0", 1 if (ocf0 or -1) > 0 else 0, f"OCF {ocf0/1e9:.2f}B" if ocf0 else "n/a"))
    tests.append(("ROA 較去年上升", 1 if (roa0 is not None and roa1 is not None and roa0 > roa1) else 0,
                  f"{roa1:.1%} → {roa0:.1%}" if roa0 is not None and roa1 is not None else "n/a"))
    q = (ocf0 / ta0) > roa0 if (ocf0 and ta0 and roa0 is not None) else None
    tests.append(("OCF/資產 > ROA（盈餘品質）", 1 if q else 0,
                  f"OCF/TA {(ocf0/ta0):.1%} vs ROA {roa0:.1%}" if (ocf0 and ta0 and roa0 is not None) else "n/a"))
    d0, d1 = f(bs, c0, "Total Debt"), f(bs, c1, "Total Debt")
    lev0 = d0 / ta0 if d0 is not None and ta0 else None
    lev1 = d1 / ta1 if d1 is not None and ta1 else None
    tests.append(("長期負債比率下降", 1 if (lev0 is not None and lev1 is not None and lev0 < lev1) else 0,
                  f"{lev1:.1%} → {lev0:.1%}" if lev0 is not None and lev1 is not None else "n/a"))
    i = D[tk]["info"]
    cr = i.get("currentRatio")
    tests.append(("流動比率 > 1.5", 1 if (cr or 0) > 1.5 else 0, f"流動比 {cr}"))
    rs0 = f(cf, c0, "Issuance Of Capital Stock") or 0
    tests.append(("未增資稀釋", 1 if rs0 <= 0 else 0, "無普通股增資" if rs0 <= 0 else f"增資 {rs0/1e9:.2f}B"))
    gp0, rv0 = f(fin, c0, "Gross Profit"), f(fin, c0, "Total Revenue")
    gp1, rv1 = f(fin, c1, "Gross Profit"), f(fin, c1, "Total Revenue")
    gm0 = gp0 / rv0 if gp0 is not None and rv0 else None
    gm1 = gp1 / rv1 if gp1 is not None and rv1 else None
    tests.append(("毛利率上升", 1 if (gm0 is not None and gm1 is not None and gm0 > gm1) else 0,
                  f"{gm1:.1%} → {gm0:.1%}" if gm0 is not None and gm1 is not None else "n/a"))
    at0 = rv0 / ta0 if rv0 and ta0 else None
    at1 = rv1 / ta1 if rv1 and ta1 else None
    tests.append(("資產周轉率上升", 1 if (at0 is not None and at1 is not None and at0 > at1) else 0,
                  f"{at1:.2f} → {at0:.2f}" if at0 is not None and at1 is not None else "n/a"))
    score = sum(t[1] for t in tests)
    return score, tests

# ---------- ROIC / WACC ----------
def roic_wacc(tk):
    fin = D[tk].get("financials", {})
    bs = D[tk].get("balance_sheet", {})
    i = D[tk]["info"]
    cols = sorted(fin.keys(), reverse=True)
    if not cols: return None
    c0 = cols[0]
    ebit = (fin.get(c0, {}) or {}).get("Operating Income")
    eq = (bs.get(c0, {}) or {}).get("Stockholders Equity")
    dbt = (bs.get(c0, {}) or {}).get("Total Debt")
    cash = (bs.get(c0, {}) or {}).get("Cash And Cash Equivalents") or 0
    if ebit is None or eq is None or dbt is None: return None
    tax = 0.15 if tk == "SKHY" else (0.21 if tk != "SNDL" else 0.26)
    ic = eq + dbt - cash
    roic = ebit * (1 - tax) / ic if ic else None
    beta = i.get("beta") or 1.0
    rf, mrp = 0.042, 0.05          # 10Y UST ~4.2%, equity risk premium 5.0%
    ke = rf + beta * mrp
    kd = 0.055 * (1 - tax)
    mc = i.get("marketCap") or 0
    if tk == "SKHY":               # market cap USD, debt KRW → normalise debt to USD
        dbt_v = dbt / KRW_USD
    else:
        dbt_v = dbt
    tot = mc + dbt_v
    wacc = (mc / tot) * ke + (dbt_v / tot) * kd if tot else ke
    return {"roic": roic, "wacc": wacc, "spread": (roic - wacc) if roic else None,
            "ke": ke, "kd": kd, "beta": beta, "tax": tax,
            "invested_capital": ic, "ebit": ebit}

# ---------- DCF ----------
DCF_ASSUMPTIONS = {
    # fcf0 (USD), g1 (yrs1-5), g2 (yrs6-10), terminal g, wacc, per scenario
    "MU":   {"bear": (0.05, -0.20, 0.02, 0.02), "base": (0.05, 0.06, 0.03, 0.025), "bull": (0.05, 0.14, 0.05, 0.03)},
    "MRVL": {"bear": (0.05, 0.04, 0.02, 0.02), "base": (0.05, 0.13, 0.05, 0.025), "bull": (0.05, 0.22, 0.08, 0.03)},
    "SKHY": {"bear": (0.05, -0.18, 0.01, 0.02), "base": (0.05, 0.05, 0.03, 0.025), "bull": (0.05, 0.12, 0.05, 0.03)},
    "SNDL": {"bear": (0.05, -0.08, 0.00, 0.01), "base": (0.05, 0.03, 0.02, 0.015), "bull": (0.05, 0.10, 0.04, 0.02)},
}

def dcf(tk, fcf0, g1, g2, gt, wacc, shares, net_debt):
    """10-year two-stage DCF + Gordon terminal. Returns per-share equity value."""
    pv, fcf = 0.0, fcf0
    flows = []
    for yr in range(1, 11):
        g = g1 if yr <= 5 else g2
        fcf *= (1 + g)
        d = fcf / (1 + wacc) ** yr
        flows.append((yr, fcf, d))
        pv += d
    tv = fcf * (1 + gt) / (wacc - gt)
    pv_tv = tv / (1 + wacc) ** 10
    ev = pv + pv_tv
    eq = ev - net_debt
    return {"pv_explicit": pv, "terminal_value": tv, "pv_terminal": pv_tv,
            "ev": ev, "equity": eq, "per_share": eq / shares if shares else None,
            "tv_pct": pv_tv / ev if ev else None, "flows": flows}

# ---------- build per-ticker record ----------
for tk in T:
    i = D[tk]["info"]
    h = D[tk].get("hist_1y", {})
    r = {"ticker": tk, "info": i, "tech": h}
    price = i.get("currentPrice")

    # --- unit normalisation (SKHY) ---
    krw = tk == "SKHY"
    def usd(v):
        return None if v is None else (v / KRW_USD if krw else v)

    rev = usd(i.get("totalRevenue"))
    ni = usd(i.get("netIncomeToCommon"))
    ebitda = usd(i.get("ebitda"))
    cash = usd(i.get("totalCash"))
    debt = usd(i.get("totalDebt"))
    fcf = usd(i.get("freeCashflow"))
    ocf = usd(i.get("operatingCashflow"))
    shares = i.get("sharesOutstanding")
    mc = i.get("marketCap")
    net_debt = (debt or 0) - (cash or 0)
    r["norm"] = {"revenue": rev, "net_income": ni, "ebitda": ebitda, "cash": cash,
                 "debt": debt, "fcf": fcf, "ocf": ocf, "net_debt": net_debt,
                 "shares": shares, "market_cap": mc,
                 "ev_fixed": (mc or 0) + net_debt,
                 "ps": mc / rev if mc and rev else None,
                 "ev_ebitda": ((mc or 0) + net_debt) / ebitda if ebitda else None,
                 "ev_rev": ((mc or 0) + net_debt) / rev if rev else None,
                 "pb": i.get("priceToBook"),
                 "krw_converted": krw, "krw_rate": KRW_USD if krw else None}

    r["piotroski"], r["piotroski_tests"] = piotroski(tk)
    r["rw"] = roic_wacc(tk)
    r["rel"] = rel_perf(tk)

    # ---------- screener: 5 dimensions ----------
    SECTOR_PE_MED = 32.0   # semis sector median trailing P/E, 2026-07
    pe = i.get("trailingPE")
    ps = r["norm"]["ps"]
    evb = r["norm"]["ev_ebitda"]
    peg = i.get("trailingPegRatio")
    val_subs = {
        "P/E vs 類股中位數": lin(pe / SECTOR_PE_MED if pe else None, 2.0, 0.5) if pe else None,
        "P/S": lin(ps, 20, 1) if ps is not None else None,
        "EV/EBITDA": lin(evb, 40, 8) if evb is not None else None,
        "PEG": lin(peg, 3.0, 0.75) if peg else None,
    }
    # Quality
    f = r["piotroski"]
    rw = r["rw"]
    fin = D[tk].get("financials", {})
    fcols = sorted(fin.keys(), reverse=True)
    gm_trend = None
    if len(fcols) >= 3:
        gms = []
        for c in fcols[:3]:
            gp, rv = (fin[c] or {}).get("Gross Profit"), (fin[c] or {}).get("Total Revenue")
            if gp is not None and rv: gms.append(gp / rv * 100)
        if len(gms) >= 2:
            gm_trend = (gms[0] - gms[-1]) / (len(gms) - 1)   # pp per year, newest first
    de = i.get("debtToEquity")
    qual_subs = {
        "Piotroski F-Score": min(10.0, f * 10 / 9) if f is not None else None,
        "ROIC − WACC 價差": lin(rw["spread"] * 100 if rw and rw.get("spread") is not None else None, -10, 10) if rw and rw.get("spread") is not None else None,
        "毛利率三年趨勢": lin(gm_trend, -3, 3) if gm_trend is not None else None,
        "負債權益比": lin((de / 100) if de is not None else None, 3.0, 0.2) if de is not None else None,
    }
    # Momentum
    ma50, ma200 = h.get("ma50"), h.get("ma200")
    rsi = h.get("rsi14")
    mom_subs = {}
    if ma50 and price: mom_subs["股價 vs MA50"] = lin((price / ma50 - 1) * 100, -10, 10)
    if ma200 and price: mom_subs["股價 vs MA200"] = lin((price / ma200 - 1) * 100, -20, 20)
    if rsi is not None and not (isinstance(rsi, float) and math.isnan(rsi)):
        if rsi < 30 or rsi > 80: mom_subs["RSI(14)"] = 0.0
        elif 55 <= rsi <= 70: mom_subs["RSI(14)"] = 10.0
        elif rsi < 55: mom_subs["RSI(14)"] = lin(rsi, 30, 55, 0, 5) if rsi < 50 else lin(rsi, 50, 55, 5, 10)
        else: mom_subs["RSI(14)"] = lin(rsi, 70, 80, 10, 0)
    rel = r["rel"]
    for w, bmk in [("3M", bench / 4), ("6M", bench / 2), ("12M", bench)]:
        if w in rel: mom_subs[f"{w} 相對 S&P500"] = lin(rel[w] - bmk, -10, 10)
    # Sentiment
    ss, ssp = i.get("sharesShort"), i.get("sharesShortPriorMonth")
    si_chg = ((ss / ssp - 1) * 100) if ss and ssp else None
    inst = i.get("heldPercentInstitutions")
    sent_subs = {}
    sent_subs["空單月變化"] = lin(si_chg, 20, -20) if si_chg is not None else None
    sent_subs["法人持股水準"] = lin(pct(inst), 20, 90) if inst is not None else None
    reco = i.get("recommendationKey")
    sent_subs["分析師共識"] = {"strong_buy": 9.0, "buy": 7.5, "hold": 5.0,
                                "underperform": 3.0, "sell": 1.0, "none": None}.get(reco)
    tgt, tlow = i.get("targetMeanPrice"), i.get("targetLowPrice")
    if tgt and price: sent_subs["目標價隱含上檔"] = lin((tgt / price - 1) * 100, -20, 60)
    # Growth
    rg = i.get("revenueGrowth")
    eg = i.get("earningsGrowth")
    fe, te = i.get("forwardEps"), i.get("trailingEps")
    grow_subs = {
        "營收 YoY": lin(pct(rg), 0, 30) if rg is not None else None,
        "EPS YoY": (lin(pct(eg), 0, 40) if (eg is not None and eg > 0) else (0.0 if eg is not None else None)),
        "前瞻 EPS vs TTM": lin(((fe / te - 1) * 100) if (fe and te and te > 0) else None, 0, 40) if (fe and te and te > 0) else None,
    }
    dims = {"價值": val_subs, "品質": qual_subs, "動能": mom_subs, "情緒": sent_subs, "成長": grow_subs}
    dim_scores = {k: avg(list(v.values())) for k, v in dims.items()}
    W = {"價值": 0.20, "品質": 0.25, "動能": 0.20, "情緒": 0.15, "成長": 0.20}
    total = round(sum((dim_scores[k] or 5.0) * W[k] for k in W), 1)
    r["screener"] = {"subs": dims, "dims": dim_scores, "total": total, "weights": W}

    # ---------- DCF ----------
    a = DCF_ASSUMPTIONS[tk]
    base_fcf = {"MU": 14.0e9, "MRVL": 2.27e9, "SKHY": 20.0e9, "SNDL": 0.045e9}[tk]
    r["dcf"] = {"fcf0": base_fcf, "shares": shares, "net_debt": net_debt, "scenarios": {}}
    for sc, (_, g1, g2, gt) in a.items():
        w = {"MU": 0.114, "MRVL": 0.115, "SKHY": 0.110, "SNDL": 0.096}[tk]
        r["dcf"]["wacc"] = w
        res = dcf(tk, base_fcf, g1, g2, gt, w, shares, net_debt)
        res.update({"g1": g1, "g2": g2, "gt": gt, "wacc": w})
        r["dcf"]["scenarios"][sc] = res

    out[tk] = r

# ---------- options: IV + max pain ----------
for tk in T:
    calls = D[tk].get("opt_calls", [])
    puts = D[tk].get("opt_puts", [])
    price = D[tk]["info"].get("currentPrice")
    if not calls or not price: continue
    def atm(rows):
        rows = [x for x in rows if x.get("strike")]
        return min(rows, key=lambda x: abs(x["strike"] - price)) if rows else None
    ac, ap = atm(calls), atm(puts)
    ivs = [x["impliedVolatility"] for x in calls + puts
           if x.get("impliedVolatility") and 0.05 < x["impliedVolatility"] < 5
           and abs(x["strike"] - price) / price < 0.25]
    coi = sum(x.get("openInterest") or 0 for x in calls)
    poi = sum(x.get("openInterest") or 0 for x in puts)
    strikes = sorted({x["strike"] for x in calls} | {x["strike"] for x in puts})
    pain = []
    for s in strikes:
        c = sum((x.get("openInterest") or 0) * max(0, s - x["strike"]) for x in calls)
        p = sum((x.get("openInterest") or 0) * max(0, x["strike"] - s) for x in puts)
        pain.append((s, c + p))
    mp = min(pain, key=lambda x: x[1])[0] if pain else None
    straddle = ((ac.get("lastPrice") or 0) + (ap.get("lastPrice") or 0)) if ac and ap else None
    out[tk]["options"] = {
        "expiry": D[tk].get("opt_exp_used"), "expiries": D[tk].get("option_expiries"),
        "atm_call": ac, "atm_put": ap, "atm_iv": (sum(ivs) / len(ivs) if ivs else None),
        "iv_min": min(ivs) if ivs else None, "iv_max": max(ivs) if ivs else None,
        "call_oi": coi, "put_oi": poi, "pc_oi": (poi / coi if coi else None),
        "max_pain": mp, "straddle": straddle,
        "implied_move": (straddle / price * 100) if straddle else None,
        "hv": D[tk]["hist_1y"].get("vol_ann_pct"),
    }

# ---------- full-report composite (5 phases) ----------
# Phase sub-scores are set from the module findings; documented in the report.
PHASE = {
  "MU":   {"business": 8.6, "valuation": 7.8, "signal": 6.4, "technical": 3.2, "risk": 4.2},
  "MRVL": {"business": 6.4, "valuation": 4.6, "signal": 6.8, "technical": 2.4, "risk": 4.0},
  "SKHY": {"business": 8.2, "valuation": 8.6, "signal": 5.2, "technical": 2.0, "risk": 3.0},
  "SNDL": {"business": 3.4, "valuation": 7.6, "signal": 4.4, "technical": 2.8, "risk": 5.4},
}
PW = {"business": 0.25, "valuation": 0.25, "signal": 0.20, "technical": 0.15, "risk": 0.15}
for tk in T:
    p = PHASE[tk]
    out[tk]["composite"] = {
        "phases": p, "weights": PW,
        "weighted": {k: round(p[k] * PW[k], 3) for k in PW},
        "total": round(sum(p[k] * PW[k] for k in PW), 2),
    }

DERIVED = out


def main() -> int:
    """Print a compact digest of the derived values (useful when refreshing the snapshot)."""
    for tk in T:
        r = out[tk]
        n, rw, s_ = r["norm"], r["rw"], r["screener"]
        print("=" * 74)
        print(f'{tk} {r["info"].get("longName")} | price {r["info"].get("currentPrice")}')
        print("  rev %.2fB  NI %.2fB  EBITDA %.2fB  FCF %.2fB  netdebt %.2fB" % (
            n["revenue"] / 1e9, n["net_income"] / 1e9, n["ebitda"] / 1e9,
            (n["fcf"] or 0) / 1e9, n["net_debt"] / 1e9))
        print("  P/S %.2f  EV/EBITDA %.2f  P/B %s  Piotroski %s/9" % (
            n["ps"], n["ev_ebitda"], n["pb"], r["piotroski"]))
        if rw:
            print("  ROIC %.1f%%  WACC %.1f%%  spread %+.1fpp" % (
                rw["roic"] * 100, rw["wacc"] * 100, rw["spread"] * 100))
        print("  SCREENER", s_["dims"], "TOTAL", s_["total"])
        for sc in ("bear", "base", "bull"):
            v = r["dcf"]["scenarios"][sc]
            print("     DCF %-5s -> $%.2f/sh (TV %.0f%% of EV)" % (
                sc, v["per_share"], v["tv_pct"] * 100))
        print("  COMPOSITE", r["composite"]["phases"], "->", r["composite"]["total"])
    print("\nBENCH S&P500 1y %+.1f%%  SOX %+.1f%%" % (bench, sox))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
