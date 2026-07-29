# -*- coding: utf-8 -*-
"""full-report --depth comprehensive --lang zh-TW : 15 modules + synthesis, per ticker."""
from context import *
import viz as V
from shell import page, toc
from prose import P

PHASE_LABEL = {"business": "商業品質", "valuation": "估值", "signal": "市場訊號",
               "technical": "技術時機", "risk": "風險剖面"}


def build(tk):
    i = RAW[tk]["info"]; n = C[tk]["norm"]; h = RAW[tk]["hist_1y"]
    rw = C[tk]["rw"]; cy = CYC[tk]; comp = C[tk]["composite"]
    opt = C[tk].get("options") or {}
    pr = P[tk]
    price = i["currentPrice"]
    rate = KRW if tk == "SKHY" else 1.0
    krw = tk == "SKHY"
    col = V.SERIES[tk]
    kind, rec = interp(comp["total"])
    e = EARN[tk]

    b = []
    # ══════════════════════════════════════════════════════════ cover
    b.append(f"""<section class="rhero"><div class="wrap rhero__in">
<p class="crumb"><a href="../index.html">InvestSkill Autopilot</a> ／ <a href="index.html">展示櫃</a> ／ {tk}</p>
<p class="eyebrow">full-report · depth comprehensive · 15 modules · zh-TW</p>
<h1>{tk} — {NAMES[tk][1]}<br><span style="font-size:.5em;font-weight:700;opacity:.9">{pr['tagline']}</span></h1>
<p class="rhero__sub">{pr['spine']}</p>
<div class="grid g4" style="margin-top:var(--s-32)">
<div class="tile" style="background:rgba(255,255,255,.10);border-color:rgba(255,255,255,.28)">
<div class="tile__k" style="color:#9ce8bd">現價</div>
<div class="tile__v" style="color:#fff">{money(price)}</div>
<div class="tile__n" style="color:rgba(255,255,255,.82)">昨日 {arrow(GAP[tk])} {pc(GAP[tk],2,True)}</div></div>
<div class="tile" style="background:rgba(255,255,255,.10);border-color:rgba(255,255,255,.28)">
<div class="tile__k" style="color:#9ce8bd">綜合評分</div>
<div class="tile__v" style="color:#fff">{comp['total']:.2f}</div>
<div class="tile__n" style="color:rgba(255,255,255,.82)">／10 · {rec}</div></div>
<div class="tile" style="background:rgba(255,255,255,.10);border-color:rgba(255,255,255,.28)">
<div class="tile__k" style="color:#9ce8bd">距 52 週高點</div>
<div class="tile__v" style="color:#fff">{pc(DD[tk],1)}</div>
<div class="tile__n" style="color:rgba(255,255,255,.82)">高 {money(i['fiftyTwoWeekHigh'])} · 低 {money(i['fiftyTwoWeekLow'])}</div></div>
<div class="tile" style="background:rgba(255,255,255,.10);border-color:rgba(255,255,255,.28)">
<div class="tile__k" style="color:#9ce8bd">市值</div>
<div class="tile__v" style="color:#fff">{money(i['marketCap'])}</div>
<div class="tile__n" style="color:rgba(255,255,255,.82)">{i.get('sector') or '—'}</div></div>
</div></div></section>""")

    tocg = [(None, [("src", "資料來源"), ("summary", "結論摘要")]),
            ("階段一 · 商業品質", [("m1", "1 · 個股評估"), ("m2", "2 · 競爭護城河"), ("m3", "3 · 基本面")]),
            ("階段二 · 估值", [("m4", "4 · DCF 評價"), ("m5", "5 · 多重估值法")]),
            ("階段三 · 市場訊號", [("m6", "6 · 內部人交易"), ("m7", "7 · 法人持股"), ("m8", "8 · 財報預期")]),
            ("階段四 · 技術時機", [("m9", "9 · 技術分析"), ("m10", "10 · 類股相對強度")]),
            ("階段五 · 風險", [("m11", "11 · 空單分析"), ("m12", "12 · 選擇權"),
                               ("m13", "13 · 總體環境"), ("m14", "14 · 財報稽核")]),
            ("資本配置", [("m15", "15 · 股息與資本配置")]),
            ("綜合", [("thesis", "投資論點"), ("bear", "空方紅隊"), ("card", "評分卡"),
                      ("valsum", "估值總結"), ("entry", "進出場策略"), ("cat", "催化劑日曆"),
                      ("monitor", "監控計畫"), ("valid", "結果稽核"), ("signal", "訊號區塊")])]

    d = []
    # ══════════════════════════════════════════════════════════ sources
    krw_extra = ""
    if krw:
        krw_extra = (f'<p style="font-size:.8125rem;margin-top:10px;color:var(--red-ink)">'
                     f'<strong>🚩 幣別警示</strong>：本檔財報以<strong>韓元</strong>揭露、股價以<strong>美元</strong>報價。'
                     f'原始資料直接混算，產出企業價值 −{abs(i["enterpriseValue"])/1e12:,.1f} 兆、'
                     f'P/S {i["priceToSalesTrailing12Months"]:.4f}、EV/EBITDA {i["enterpriseToEbitda"]:.2f} '
                     f'等不可能數值。本報告所有金額已按 <strong>1 USD = {KRW:,.0f} KRW</strong> 換算，'
                     f'此匯率為<strong>假設值</strong>，非揭露值。詳見 <a href="#m14">模組 14</a>。</p>')
    d.append(f"""<section id="src"><h2>資料來源</h2>
{prov("yfinance（Yahoo Finance）：即時報價與 6 個月價格歷史、四個會計年度損益表／資產負債表／現金流量表、"
      "五個季度季報、13F 前 15 大法人持股、Form 4 內部人交易、選擇權鏈、分析師預估與財報日曆。"
      "基準指數 ^GSPC／^SOX。無風險利率 4.2%、股權風險溢酬 5.0%（CAPM 輸入，假設值）。",
      "程式化擷取（yfinance 1.5.2）· 單次快照 · 四檔共用同一時點",
      pr["sig"]["conf"] + " — 詳見 <a href='#valid'>模組稽核</a>", krw_extra)}
<p class="fignote">依 <code>full-report</code> 規定：本報告執行 <strong>comprehensive</strong> 深度的全部
15 個模組，無模組因深度設定而略過。若個別模組因資料缺失而無法執行，
一律標記「未評估」並在綜合評分中揭露，<strong>不以中性值 5.0 填補</strong>。</p>
</section>""")

    # ══════════════════════════════════════════════════════════ summary
    ph_rows = [(PHASE_LABEL[k], comp["phases"][k], col,
                f'×{comp["weights"][k]:.0%} = {comp["weighted"][k]:.2f}') for k in
               ["business", "valuation", "signal", "technical", "risk"]]
    d.append(f"""<section id="summary"><h2>結論摘要</h2>
<div class="grid g2">
<div>{V.figure(V.gauge(comp['total'], width=300, height=180, caption=rec),
   f"綜合評分 {comp['total']:.2f}／10")}</div>
<div>{V.figure(V.hbar_chart(ph_rows, width=470, vmax=10, fmt="{:.1f}", pad=(12,138,26,86)),
   "五階段子分數（0–10）")}</div>
</div>
{sig_block([("Signal", pr['sig']['signal']), ("Confidence", pr['sig']['conf']),
            ("Horizon", pr['sig']['hz']), ("Score", f"{comp['total']:.2f} / 10"), None,
            ("Action", pr['sig']['action']), ("Conviction", pr['sig']['conv'])])}
<p class="fignote">{pr['sig']['note']}</p>
</section>""")

    # ══════════════════════ M1 stock-eval ══════════════════════
    ev_tbl = V.simple_table(
      ["項目", "數值", "備註"],
      [["公司", NAMES[tk][0], NAMES[tk][1]],
       ["類股／產業", f"{i.get('sector') or '—'} / {i.get('industry') or '—'}", i.get("country") or "—"],
       ["員工數", f"{i['fullTimeEmployees']:,}" if i.get("fullTimeEmployees") else "—", ""],
       ["市值", money(i["marketCap"]), ""],
       ["企業價值（校正後）", money(n["ev_fixed"]),
        "＝市值＋淨負債；原始欄位不可用" if krw else "＝市值＋淨負債"],
       ["TTM 營收", money(n["revenue"]) + ("（校正後）" if krw else ""), ""],
       ["TTM 淨利", money(n["net_income"]) + ("（校正後）" if krw else ""), ""],
       ["毛利率 / 營業利益率 / 淨利率",
        f"{pcf(i.get('grossMargins'))} / {pcf(i.get('operatingMargins'))} / {pcf(i.get('profitMargins'))}", ""],
       ["ROE / ROA", f"{pcf(i.get('returnOnEquity'))} / {pcf(i.get('returnOnAssets'))}", ""],
       ["ROIC / WACC", f"{pcf(rw['roic'])} / {pcf(rw['wacc'])}" if rw else "—",
        f'價差 <strong class="{cls(rw["spread"])}">{pcf(rw["spread"],1,True)}</strong>' if rw else ""],
       ["Beta（5Y 月）", num(i.get("beta")), f"權益成本 Ke = 4.2% + β×5.0% = {pcf(rw['ke']) if rw else '—'}"],
       ["Piotroski F-Score", f"<strong>{C[tk]['piotroski']} / 9</strong>", "九項檢定見下表"]])
    pio = V.simple_table(["#", "檢定項目", "結果", "代入值"],
      [[str(k + 1), t[0], ("✅ 通過" if t[1] else "❌ 未通過"), t[2]]
       for k, t in enumerate(C[tk]["piotroski_tests"])],
      align=["right", "left", "center", "left"])
    d.append(f"""<section id="m1"><h2><span class="modnum">1</span>個股評估<span class="skilltag">stock-eval</span></h2>
{pr['eval']}
<h3>核心數據</h3>
<div class="tblwrap">{ev_tbl}</div>
<h3>Piotroski F-Score 九項檢定</h3>
<div class="tblwrap">{pio}</div>
</section>""")

    # ══════════════════════ M2 competitor ══════════════════════
    peers = ["MU", "SKHY", "MRVL"] if tk != "SNDL" else ["SNDL", "MU", "MRVL"]
    peer_tbl = V.simple_table(
      ["指標"] + peers,
      [["營業利益率（TTM）"] + [pcf(RAW[p]["info"].get("operatingMargins")) for p in peers],
       ["毛利率"] + [pcf(RAW[p]["info"].get("grossMargins")) for p in peers],
       ["ROIC"] + [pcf(C[p]["rw"]["roic"]) if C[p]["rw"] else "—" for p in peers],
       ["WACC"] + [pcf(C[p]["rw"]["wacc"]) if C[p]["rw"] else "—" for p in peers],
       ["ROIC − WACC"] + [f'<strong class="{cls(C[p]["rw"]["spread"])}">{pcf(C[p]["rw"]["spread"],1,True)}</strong>'
                          if C[p]["rw"] else "—" for p in peers],
       ["EV/EBITDA（校正後）"] + [f'{C[p]["norm"]["ev_ebitda"]:.1f}x' for p in peers],
       ["營收 YoY"] + [pcf(RAW[p]["info"].get("revenueGrowth"), 1, True) for p in peers],
       ["Piotroski"] + [f'{C[p]["piotroski"]}／9' for p in peers],
       ["Beta"] + [num(RAW[p]["info"].get("beta")) for p in peers]],
      align=["left"] + ["right"] * len(peers))
    d.append(f"""<section id="m2"><h2><span class="modnum">2</span>競爭護城河<span class="skilltag">competitor-analysis</span></h2>
{pr['moat']}
<h3>同業對照</h3>
<div class="tblwrap">{peer_tbl}</div>
<p class="fignote">SKHY 數值均為幣別校正後。EV/EBITDA 一律以「市值＋淨負債」重算，
不採用 yfinance 的 enterpriseValue 欄位。</p>
</section>""")

    # ══════════════════════ M3 fundamental ══════════════════════
    fyrows = cy["rows"]
    fy_cats = [r["fy"][:7] for r in reversed(fyrows)]
    rev_series = [{"name": "營收", "colour": col, "values": [r["rev"] / 1e9 for r in reversed(fyrows)]}]
    op_series = [{"name": "營業利益率", "colour": V.INK2,
                  "values": [(r["opm"] * 100 if r["opm"] is not None else None) for r in reversed(fyrows)]}]
    rev_chart = V.column_chart(fy_cats, rev_series, y_fmt="${:.0f}B", y_label="十億美元", height=300)
    opm_chart = V.column_chart(fy_cats, op_series, y_fmt="{:.0f}%", y_label="營業利益率",
                               height=300, hlines=[(0, "損益兩平", V.INK3)])
    fy_tbl = V.simple_table(
      ["會計年度", "營收", "營業利益", "營業利益率", "淨利", "淨利率"],
      [[r["fy"][:10], money(r["rev"]), money(r["op"]),
        f'<span class="{cls(r["opm"])}">{pcf(r["opm"])}</span>',
        money(r["ni"]), f'<span class="{cls(r["nim"])}">{pcf(r["nim"])}</span>']
       for r in fyrows] +
      [["<strong>TTM</strong>", f"<strong>{money(cy['ttm_rev'])}</strong>", "—",
        f'<strong>{pcf(cy["opm_now"])}</strong>', f"<strong>{money(cy['ttm_ni'])}</strong>",
        f'<strong>{pcf(i.get("profitMargins"))}</strong>']])

    # quarterly
    qf = RAW[tk].get("quarterly_financials", {})
    qcols = sorted(qf.keys())
    qrev = [(qf[c] or {}).get("Total Revenue") for c in qcols]
    qeps = [(qf[c] or {}).get("Diluted EPS") for c in qcols]
    qni = [(qf[c] or {}).get("Net Income") for c in qcols]
    q_chart = V.column_chart([c[:7] for c in qcols],
        [{"name": "季營收", "colour": col, "values": [(v / rate / 1e9 if v else None) for v in qrev]}],
        y_fmt="${:.1f}B", y_label="十億美元", height=290)
    q_tbl = V.simple_table(["季別", "營收", "營業利益", "淨利", "稀釋 EPS"],
      [[qcols[k][:10], money(qrev[k] / rate) if qrev[k] else "—",
        money(((qf[qcols[k]] or {}).get("Operating Income") or 0) / rate) if (qf[qcols[k]] or {}).get("Operating Income") is not None else "—",
        money(qni[k] / rate) if qni[k] is not None else "—",
        (f'{qeps[k]:,.0f} KRW' if krw and qeps[k] else (f"${qeps[k]:,.2f}" if qeps[k] is not None else "—"))]
       for k in range(len(qcols) - 1, -1, -1)])

    cfd = RAW[tk].get("cashflow", {})
    ccols = sorted(cfd.keys(), reverse=True)
    cf_tbl = V.simple_table(["會計年度", "營運現金流", "資本支出", "自由現金流", "FCF／營收", "股票買回", "股息支付"],
      [[c[:10],
        money(((cfd[c] or {}).get("Operating Cash Flow") or 0) / rate),
        money(((cfd[c] or {}).get("Capital Expenditure") or 0) / rate),
        money(((cfd[c] or {}).get("Free Cash Flow") or 0) / rate),
        (lambda f, r: pcf(f / r) if f and r else "—")(
            (cfd[c] or {}).get("Free Cash Flow"),
            ((RAW[tk]["financials"].get(c) or {}) or {}).get("Total Revenue")),
        money(((cfd[c] or {}).get("Repurchase Of Capital Stock") or 0) / rate) if (cfd[c] or {}).get("Repurchase Of Capital Stock") else "—",
        money(((cfd[c] or {}).get("Cash Dividends Paid") or 0) / rate) if (cfd[c] or {}).get("Cash Dividends Paid") else "—"]
       for c in ccols])

    d.append(f"""<section id="m3"><h2><span class="modnum">3</span>基本面分析<span class="skilltag">fundamental-analysis</span></h2>
{pr['fund']}
<h3>四年損益軌跡</h3>
{V.figure(rev_chart, f"圖 ── {tk} 年度營收（{'幣別校正後美元' if krw else '美元'}）")}
{V.figure(opm_chart, f"圖 ── {tk} 年度營業利益率（%）", None,
  "這張圖是本報告最重要的單一視覺：它顯示了該公司在四年內經歷的完整利益率擺盪幅度。")}
<div class="tblwrap">{fy_tbl}</div>
<h3>五季序列</h3>
{V.figure(q_chart, f"圖 ── {tk} 季度營收")}
<div class="tblwrap">{q_tbl}</div>
<h3>現金流量與資本配置</h3>
<div class="tblwrap">{cf_tbl}</div>
</section>""")

    # ══════════════════════ M4 DCF ══════════════════════
    dcfd = C[tk]["dcf"]
    sc_tbl = V.simple_table(
      ["情境", "年 1–5 成長", "年 6–10 成長", "終值成長", "WACC", "明確期現值", "終值現值", "終值占比", "每股價值", "相對現價"],
      [[{"bear": "空方 Bear", "base": "基準 Base", "bull": "多方 Bull"}[s],
        pcf(dcfd["scenarios"][s]["g1"], 0, True), pcf(dcfd["scenarios"][s]["g2"], 0, True),
        pcf(dcfd["scenarios"][s]["gt"]), pcf(dcfd["scenarios"][s]["wacc"]),
        money(dcfd["scenarios"][s]["pv_explicit"]), money(dcfd["scenarios"][s]["pv_terminal"]),
        pcf(dcfd["scenarios"][s]["tv_pct"]),
        f'<strong>{money(dcfd["scenarios"][s]["per_share"])}</strong>',
        f'<span class="{cls(dcfd["scenarios"][s]["per_share"]/price-1)}">'
        f'{pc((dcfd["scenarios"][s]["per_share"]/price-1)*100,0,True)}</span>']
       for s in ["bear", "base", "bull"]])
    # sensitivity grid: WACC x terminal g
    base = dcfd["scenarios"]["base"]

    def _dcf(_tk, fcf0, g1, g2, gt, wacc, shares, net_debt):
        """Same two-stage DCF as calc.py, re-declared to avoid re-running that module."""
        pv, fcf = 0.0, fcf0
        for yr in range(1, 11):
            fcf *= (1 + (g1 if yr <= 5 else g2))
            pv += fcf / (1 + wacc) ** yr
        tv = fcf * (1 + gt) / (wacc - gt)
        ev = pv + tv / (1 + wacc) ** 10
        return {"per_share": (ev - net_debt) / shares if shares else None}

    grid_w = [dcfd["wacc"] - .02, dcfd["wacc"] - .01, dcfd["wacc"], dcfd["wacc"] + .01, dcfd["wacc"] + .02]
    grid_g = [.015, .020, .025, .030, .035]
    srows = []
    for g in grid_g:
        vals = []
        for w in grid_w:
            if w <= g: vals.append(None); continue
            r = _dcf(tk, dcfd["fcf0"], base["g1"], base["g2"], g, w, dcfd["shares"], dcfd["net_debt"])
            vals.append(r["per_share"])
        srows.append((f"終值成長 {g*100:.1f}%", vals))
    smax = max(v for _, vs in srows for v in vs if v is not None)
    sens = V.heat_table([f"WACC {w*100:.1f}%" for w in grid_w], srows,
                        fmt="${:,.0f}", vmin=0, vmax=smax, first_col="敏感度")
    d.append(f"""<section id="m4"><h2><span class="modnum">4</span>DCF 評價<span class="skilltag">dcf-valuation</span></h2>
<p>十年兩階段自由現金流折現 ＋ Gordon 終值。起始自由現金流 <strong>{money(dcfd['fcf0'])}</strong>
（{'依 TTM 與 FY 現金流量表推估' if tk in ('MU','SKHY') else '採 TTM 自由現金流'}），
流通股數 {dcfd['shares']/1e6:,.0f}M，淨負債 {money(dcfd['net_debt'])}
{'（淨現金，故加回股權價值）' if dcfd['net_debt'] < 0 else ''}。</p>
{pr.get('val_note','')}
<div class="tblwrap">{sc_tbl}</div>
<h3>基準情境的雙變數敏感度（每股價值）</h3>
<div class="tblwrap">{sens}</div>
<p class="fignote">空白格代表終值成長率 ≥ WACC，Gordon 公式失效。
現價 {money(price)} 在此矩陣中的位置，即為市場隱含的 WACC 與永續成長組合。</p>
<div class="call call--warn"><div class="call__h">⚠ 這個 DCF 的方法論限制（必讀）</div>
<p>對<strong>資本密集的循環股</strong>而言，以自由現金流為基礎的 DCF 有系統性偏誤：
在循環頂點，公司同時擁有最高的營運現金流<em>與</em>最高的資本支出，
使自由現金流被壓縮到遠低於盈餘能力的水準。
{f'{tk} 的 TTM 自由現金流 {money(n["fcf"])} 僅為淨利 {money(n["net_income"])} 的 {n["fcf"]/n["net_income"]*100:.0f}%。' if n.get('fcf') and n.get('net_income') and n['net_income'] > 0 else ''}</p>
<p>因此本報告<strong>不以 DCF 為主要估值依據</strong>，而在下一個模組以常態化盈餘法與相對倍數法交叉驗證。
三種方法的分歧程度本身，就是估值不確定性的度量。</p></div>
</section>""")

    # ══════════════════════ M5 stock-valuation ══════════════════════
    SCEN_LBL = {"revert": "均值回歸（含谷底四年均值）", "ex_trough": "除谷底均值",
                "structural": "結構性中循環", "peak": "維持目前 TTM 利益率"}
    SCEN_NOTE = {"revert": "假設完全回到歷史平均，含 2023 年虧損年度",
                 "ex_trough": "排除虧損年度後的平均——溫和的均值回歸",
                 "structural": "除谷底均值與目前峰值的中點——本報告的中心情境",
                 "peak": "假設目前利益率永久維持——市場目前的隱含假設"}
    cyc_rows = ""
    ff_rows = []
    for key in ["revert", "ex_trough", "structural", "peak"]:
        s = cy["scen"].get(key)
        if not s: continue
        cyc_rows += (f'<tr><th scope="row" style="text-align:left"><strong>{SCEN_LBL[key]}</strong><br>'
                     f'<span style="font-weight:400;font-size:.6875rem;color:var(--ink-3)">{SCEN_NOTE[key]}</span></th>'
                     f'<td>{pcf(s["opm"])}</td><td>{money(s["ni"])}</td>'
                     + "".join(f'<td><strong>{money(s[f"m{m}"])}</strong><br>'
                               f'<span style="font-size:.6875rem;color:var(--ink-3)">'
                               f'{pc((s[f"m{m}"]/price-1)*100,0,True)}</span></td>' for m in (10, 12, 15, 18))
                     + "</tr>")
        ff_rows.append((SCEN_LBL[key], s["m10"], s["m18"], col, f"營業利益率 {s['opm']*100:.1f}%，10–18 倍"))
    ff_rows.append(("DCF 三情境", dcfd["scenarios"]["bear"]["per_share"],
                    dcfd["scenarios"]["bull"]["per_share"], V.INK2, f"WACC {dcfd['wacc']*100:.1f}%"))
    if i.get("targetLowPrice") and i.get("targetHighPrice"):
        ff_rows.append(("分析師目標價區間", i["targetLowPrice"], i["targetHighPrice"], "#4a3aa7",
                        f"{i.get('numberOfAnalystOpinions')} 位分析師，平均 {money(i['targetMeanPrice'])}"))
    ff_rows.append(("52 週實際區間", i["fiftyTwoWeekLow"], i["fiftyTwoWeekHigh"], V.INK3, "過去一年市場實際成交範圍"))
    ff = V.football_field(ff_rows, price)

    mult_tbl = V.simple_table(["倍數", tk, "MU", "SKHY", "MRVL", "SNDL", "評註"],
      [["本益比（TTM）"] + [(f'{RAW[p]["info"]["trailingPE"]:.1f}x' if RAW[p]["info"].get("trailingPE") else "n/a")
                            for p in [tk, "MU", "SKHY", "MRVL", "SNDL"]] + ["SNDL 獲利為負，不適用"],
       ["前瞻本益比"] + [(f'{RAW[p]["info"]["currentPrice"]/RAW[p]["info"]["forwardEps"]:.1f}x'
                          if RAW[p]["info"].get("forwardEps") else "—")
                         for p in [tk, "MU", "SKHY", "MRVL", "SNDL"]] +
        ["SKHY 3.2x 與 SNDL 40.7x 均不可信，見各報告稽核"],
       ["P/S（校正後）"] + [f'{C[p]["norm"]["ps"]:.2f}x' for p in [tk, "MU", "SKHY", "MRVL", "SNDL"]] + [""],
       ["EV/EBITDA（校正後）"] + [f'{C[p]["norm"]["ev_ebitda"]:.1f}x' for p in [tk, "MU", "SKHY", "MRVL", "SNDL"]] + [""],
       ["股價淨值比（申報 BS 重算）"] + [(f'{BS[p]["pb"]:.2f}x' if BS.get(p) and BS[p].get("pb") else "—") for p in [tk, "MU", "SKHY", "MRVL", "SNDL"]] +
        ["SNDL 0.30x（依申報資產負債表重算）是唯一低於 1 者"],
       ["PEG"] + [(num(RAW[p]["info"].get("trailingPegRatio"), 2) if RAW[p]["info"].get("trailingPegRatio") else "n/a")
                  for p in [tk, "MU", "SKHY", "MRVL", "SNDL"]] + [""]],
      align=["left", "right", "right", "right", "right", "right", "left"])

    d.append(f"""<section id="m5"><h2><span class="modnum">5</span>多重估值法<span class="skilltag">stock-valuation</span></h2>
<h3>循環常態化盈餘法（本報告的主要方法）</h3>
<p>做法：取 TTM 營收 <strong>{money(cy['ttm_rev'])}</strong> 為基礎（假設營收水準維持），
套用四種不同的營業利益率假設，稅後淨利 ＝ 營收 × 營業利益率 × 0.85，
再乘以 10／12／15／18 倍本益比，除以 {cy['shares']/1e6:,.0f}M 股得每股價值。</p>
{f'''<p><strong>{tk} 的關鍵歷史事實</strong>：TTM 淨利 {money(cy["ttm_ni"])} 是過去
{len(cy["rows"])} 個會計年度平均值（{money(cy["avg_ni"])}）的
<strong>{cy["x_avg"]:.1f} 倍</strong>。這是評估目前獲利可持續性時最重要的單一數字。</p>''' if cy.get("x_avg") else ''}
<div class="tblwrap"><table class="dt dt--sm">
<thead><tr><th style="text-align:left">利益率情境</th><th>營業利益率</th><th>隱含稅後淨利</th>
<th>10 倍</th><th>12 倍</th><th>15 倍</th><th>18 倍</th></tr></thead>
<tbody>{cyc_rows}</tbody></table></div>
{f'''<div class="call call--warn"><div class="call__h">⚠ 現價落在哪一格</div>
<p>現價 <strong>{money(price)}</strong> 最接近「{SCEN_LBL["peak"]} × 15 倍」＝
<strong>{money(cy["scen"]["peak"]["m15"])}</strong>（差距 {abs(price-cy["scen"]["peak"]["m15"])/price*100:.1f}%）。</p>
<p>換言之，市場目前的定價<strong>隱含 {pcf(cy["opm_now"])} 的營業利益率永久維持</strong>。
而同一家公司在 {cy["rows"][2]["fy"][:4]} 會計年度的營業利益率是
<strong>{pcf(cy["rows"][2]["opm"])}</strong>。</p></div>''' if tk in ("MU", "SKHY") and cy["scen"].get("peak") else ''}
<h3>估值方法對照（Football Field）</h3>
{V.figure(ff, f"圖 ── {tk} 各估值方法的價值區間 vs 現價",
  V.simple_table(["方法", "下緣", "上緣", "說明"],
    [[r[0], money(r[1]), money(r[2]), r[4]] for r in ff_rows]),
  "各方法的區間寬度差異本身即是資訊：區間越寬，該方法對假設越敏感。")}
<h3>相對倍數（四檔橫向對照）</h3>
<div class="tblwrap">{mult_tbl}</div>
</section>""")

    # ══════════════════════ M6 insider ══════════════════════
    ins = INS[tk]
    ins_body = pr["insider"]
    if ins["sells"]:
        ev = [(s["date"], s["px"], s["value"], f'{s["who"]}（{s["role"]}）', "sale")
              for s in ins["sells"] if s["px"] and s["value"]]
        tl = V.insider_timeline(ev, price) if ev else ""
        stbl = V.simple_table(["申報日", "內部人", "職位", "股數", "成交價", "金額", "相對現價"],
          [[s["date"], s["who"], s["role"], f'{s["shares"]:,}',
            money(s["px"]) if s["px"] else "—", money(s["value"]),
            f'<span class="dn">{pc((price/s["px"]-1)*100,0,True)}</span>' if s["px"] else "—"]
           for s in ins["sells"]])
        ins_body += (V.figure(tl, f"圖 ── {tk} 內部人賣出價位 vs 現價（圓面積 ∝ 交易金額）", stbl,
            "僅計入明確標示「Sale at price」的申報。股權獎勵歸屬與代扣稅款賣出（無成交價欄位）不計入。")
            if tl else "") + f"""
<div class="grid g3" style="margin-top:var(--s-16)">
<div class="tile"><div class="tile__k">申報賣出總額</div><div class="tile__v dn">{money(ins['sell_total'])}</div>
<div class="tile__n">{ins['n_sell']} 筆 · {ins['sell_shares']:,} 股</div></div>
<div class="tile"><div class="tile__k">申報買進總額</div><div class="tile__v">{money(ins['buy_total']) if ins['buy_total'] else '$0'}</div>
<div class="tile__n">{ins['n_buy']} 筆</div></div>
<div class="tile"><div class="tile__k">淨買賣</div><div class="tile__v dn">{money(-(ins['sell_total']-ins['buy_total']))}</div>
<div class="tile__n">內部人持股比 {pcf(i.get('heldPercentInsiders'),2)}</div></div>
</div>"""
    d.append(f"""<section id="m6"><h2><span class="modnum">6</span>內部人交易<span class="skilltag">insider-trading</span></h2>
{ins_body}
</section>""")

    # ══════════════════════ M7 institutional ══════════════════════
    ih = INST[tk]
    inst_body = pr["inst"]
    if ih:
        chg_rows = [(r["holder"][:26], (r["chg"] or 0) * 100,
                     V.GOOD if (r["chg"] or 0) > 0 else V.BAD,
                     f'（持股 {r["pct"]*100:.2f}%）' if r["pct"] else "")
                    for r in ih[:10]]
        chg = V.hbar_chart(chg_rows, fmt="{:+.0f}%", zero_line=True, vmin=None, pad=(14, 150, 26, 176))
        itbl = V.simple_table(["法人", "持股比", "股數", "市值", "季度變動", "申報基準日"],
          [[r["holder"], pcf(r["pct"], 2), f'{r["shares"]:,}' if r["shares"] else "—",
            money(r["value"]),
            f'<span class="{cls(r["chg"])}">{pcf(r["chg"],1,True)}</span>' if r["chg"] is not None else "—",
            r["asof"]] for r in ih])
        mh = RAW[tk].get("major_holders") or {}
        inst_body += f"""
<div class="grid g4" style="margin-top:var(--s-16)">
<div class="tile"><div class="tile__k">機構持股比</div><div class="tile__v">{pcf(i.get('heldPercentInstitutions'))}</div>
<div class="tile__n">{int(mh.get('institutionsCount',{}).get('Value',0)):,} 家機構</div></div>
<div class="tile"><div class="tile__k">內部人持股比</div><div class="tile__v">{pcf(i.get('heldPercentInsiders'),2)}</div>
<div class="tile__n">流通股 {i['floatShares']/1e6:,.0f}M</div></div>
<div class="tile"><div class="tile__k">前 3 大合計</div><div class="tile__v">{pcf(sum((r['pct'] or 0) for r in ih[:3]))}</div>
<div class="tile__n">{'、'.join(r['holder'].split()[0] for r in ih[:3])}</div></div>
<div class="tile"><div class="tile__k">最大單一減碼</div>
<div class="tile__v dn">{pcf(min((r['chg'] or 0) for r in ih))}</div>
<div class="tile__n">{min(ih, key=lambda r: r['chg'] or 0)['holder'][:22]}</div></div>
</div>
{V.figure(chg, f"圖 ── {tk} 前 10 大法人的季度持股變動（%）", itbl,
  "資料基準日 2026-03-31（13F 有約一季的申報時滯，不反映 4–7 月的實際部位變化）。"
  "pctChange 為 100% 者代表該申報期首次出現，可能是新建部位或申報實體重組。")}"""
    d.append(f"""<section id="m7"><h2><span class="modnum">7</span>法人持股<span class="skilltag">institutional-ownership</span></h2>
{inst_body}
</section>""")

    # ══════════════════════ M8 earnings ══════════════════════
    rc = RECO[tk]
    reco_tbl = ""
    if rc:
        reco_tbl = V.simple_table(["期間", "強力買進", "買進", "持有", "賣出", "強力賣出", "合計"],
          [[{"0m": "本月", "-1m": "1 個月前", "-2m": "2 個月前", "-3m": "3 個月前"}.get(r["period"], r["period"]),
            r.get("strongBuy", 0), r.get("buy", 0), r.get("hold", 0), r.get("sell", 0), r.get("strongSell", 0),
            sum(r.get(k, 0) for k in ("strongBuy", "buy", "hold", "sell", "strongSell"))] for r in rc])
    est = ""
    if e.get("eps_avg") or e.get("rev_avg"):
        est = V.simple_table(["項目", "共識平均", "區間低", "區間高", "離散度", "相對最近一季"],
          [["單季 EPS", f'{e["eps_avg"]:,.2f}' if e.get("eps_avg") else "未提供",
            f'{e["eps_lo"]:,.2f}' if e.get("eps_lo") else "—",
            f'{e["eps_hi"]:,.2f}' if e.get("eps_hi") else "—",
            f'{e["eps_hi"]/e["eps_lo"]:.2f}x' if e.get("eps_hi") and e.get("eps_lo") else "—",
            (f'{e["eps_avg"]/qeps[-1]-1:+.1%}' if e.get("eps_avg") and qeps and qeps[-1] and not krw else "—")],
           ["單季營收", money(e["rev_avg"] / rate) if e.get("rev_avg") else "未提供",
            money(e["rev_lo"] / rate) if e.get("rev_lo") else "—",
            money(e["rev_hi"] / rate) if e.get("rev_hi") else "—",
            f'{e["rev_hi"]/e["rev_lo"]:.2f}x' if e.get("rev_hi") and e.get("rev_lo") else "—",
            (f'{e["rev_avg"]/qrev[-1]-1:+.1%}' if e.get("rev_avg") and qrev and qrev[-1] else "—")]],
          align=["left", "right", "right", "right", "right", "right"])
    d.append(f"""<section id="m8"><h2><span class="modnum">8</span>財報預期與分析師<span class="skilltag">earnings-call-analysis</span></h2>
{pr['earnings']}
{f'<h3>下次財報共識預估（{e["date"]}）</h3><div class="tblwrap">{est}</div>' if est else ''}
{f'<h3>分析師評等變化（近四個月）</h3><div class="tblwrap">{reco_tbl}</div>' if reco_tbl else ''}
{f'''<div class="grid g3" style="margin-top:var(--s-16)">
<div class="tile"><div class="tile__k">平均目標價</div><div class="tile__v">{money(i["targetMeanPrice"])}</div>
<div class="tile__n {cls(i["targetMeanPrice"]/price-1)}">隱含 {pc((i["targetMeanPrice"]/price-1)*100,1,True)}</div></div>
<div class="tile"><div class="tile__k">目標價區間</div>
<div class="tile__v" style="font-size:1.2rem">{money(i["targetLowPrice"])} – {money(i["targetHighPrice"])}</div>
<div class="tile__n">離散度 {i["targetHighPrice"]/i["targetLowPrice"]:.2f} 倍</div></div>
<div class="tile"><div class="tile__k">覆蓋分析師</div><div class="tile__v">{i.get("numberOfAnalystOpinions")}</div>
<div class="tile__n">共識 {i.get("recommendationKey")}</div></div></div>'''
     if i.get("targetMeanPrice") else ''}
</section>""")

    # ══════════════════════ M9 technical ══════════════════════
    tech_body = pr["tech"]
    if h.get("ma50"):
        m = h.get("monthly") or []
        ma_series = [{"name": "收盤", "colour": col, "points": [(dt[5:7] + "月", v) for dt, v in m]}]
        pchart = V.line_chart(ma_series, y_fmt="${:,.0f}", y_label="美元", height=340, area_first=True,
            hlines=[(h["ma50"], f"MA50 ${h['ma50']:,.0f}", V.INK2),
                    (h["ma200"], f"MA200 ${h['ma200']:,.0f}", V.INK3)] if h.get("ma200") else
                   [(h["ma50"], f"MA50 ${h['ma50']:,.0f}", V.INK2)])
        ttbl = V.simple_table(["指標", "數值", "判讀"],
          [["現價", money(price), "—"],
           ["MA20", money(h.get("ma20")), f'<span class="{cls(price/h["ma20"]-1)}">{pc((price/h["ma20"]-1)*100,1,True)}</span>' if h.get("ma20") else "—"],
           ["MA50", money(h.get("ma50")), f'<span class="{cls(price/h["ma50"]-1)}">{pc((price/h["ma50"]-1)*100,1,True)}</span>'],
           ["MA200", money(h.get("ma200")), f'<span class="{cls(price/h["ma200"]-1)}">{pc((price/h["ma200"]-1)*100,1,True)}</span>' if h.get("ma200") else "—"],
           ["RSI(14)", num(h.get("rsi14"), 1),
            "超賣（&lt;30）" if h.get("rsi14", 50) < 30 else ("偏弱（30–50）" if h.get("rsi14", 50) < 50 else "偏強")],
           ["MACD / 訊號線", f'{h.get("macd",0):,.2f} / {h.get("macd_signal",0):,.2f}',
            '<span class="dn">空頭排列（MACD 在訊號線下）</span>' if h.get("macd", 0) < h.get("macd_signal", 0) else '<span class="up">多頭排列</span>'],
           ["ATR(14)", money(h.get("atr14")), f'佔股價 {h["atr14"]/price*100:.1f}%' if h.get("atr14") else "—"],
           ["年化波動率", pc(h.get("vol_ann_pct"), 1), "—"],
           ["一年最大回撤", f'<span class="dn">{pc(h.get("max_dd_pct"),1)}</span>', "—"],
           ["20 日均量", f'{h["avg_vol_20"]/1e6:,.1f}M 股' if h.get("avg_vol_20") else "—",
            f'對照 3 個月均量 {i["averageVolume"]/1e6:,.1f}M' if i.get("averageVolume") else "—"]])
        tech_body += V.figure(pchart, f"圖 ── {tk} 一年月底收盤與移動平均", ttbl,
                              "月底收盤序列；MA20／MA50／MA200 由日收盤計算。")
    else:
        tw = V.simple_table(["指標", "所需最小視窗", "本檔可用資料", "狀態"],
          [["MA20", "20 個交易日", "13 個交易日", "❌ 無法計算"],
           ["MA50", "50 個交易日", "13 個交易日", "❌ 無法計算"],
           ["MA200", "200 個交易日", "13 個交易日", "❌ 無法計算"],
           ["RSI(14)", "15 個交易日", "13 個交易日", "❌ 無法計算"],
           ["ATR(14)", "15 個交易日", "13 個交易日", "❌ 無法計算"],
           ["MACD(12,26,9)", "35 個交易日", "13 個交易日", "⚠ 已計算但不可靠"],
           ["年化波動率", "60 個交易日（穩定估計）", "13 個交易日", "⚠ 185.5%，樣本不足"],
           ["最大回撤", "完整循環", "13 個交易日", "⚠ −32.9%，僅反映上市後區間"],
           ["相對強度（3／6／12M）", "63／126／252 個交易日", "13 個交易日", "❌ 無法計算"]],
          align=["left", "center", "center", "left"])
        tech_body += f"""<div class="tblwrap">{tw}</div>
<p>可觀察的少數事實：ADR 自 2026-07-10 掛牌首日收盤 {money(h['first'])} 起算，
至 {money(price)}，區間報酬 <strong class="dn">{pc(h['ret_pct'],1,True)}</strong>；
期間最高 {money(h['high'])}、最低 {money(h['low'])}（即現價，為掛牌以來新低）。
13 個交易日的日均量 {h['avg_vol_20']/1e6:,.1f}M 股。</p>
<p><strong>結論：本模組標記為「無法評估」。</strong>技術時機階段的子分數 {comp['phases']['technical']:.1f}
並非基於技術訊號，而是反映<strong>「處於掛牌以來低點且無趨勢資訊」</strong>這個狀態本身。</p>"""
    d.append(f"""<section id="m9"><h2><span class="modnum">9</span>技術分析<span class="skilltag">technical-analysis</span></h2>
{tech_body}
</section>""")

    # ══════════════════════ M10 sector ══════════════════════
    rel = C[tk]["rel"]
    is_semi = tk != "SNDL"
    rel_rows = []
    for w, bmk in [("3M", BENCH["^GSPC"]["ret_1y_pct"] / 4), ("6M", BENCH["^GSPC"]["ret_1y_pct"] / 2),
                   ("12M", BENCH["^GSPC"]["ret_1y_pct"])]:
        if w in rel:
            rel_rows.append([w, pc(rel[w], 1, True), pc(bmk, 1, True),
                             f'<span class="{cls(rel[w]-bmk)}">{pc(rel[w]-bmk,1,True)} pp</span>'])
    d.append(f"""<section id="m10"><h2><span class="modnum">10</span>類股相對強度<span class="skilltag">sector-analysis</span></h2>
<p>{tk} 屬 <strong>{i.get('sector') or '—'} / {i.get('industry') or '—'}</strong>。
{'本輪半導體類股（^SOX 一年 +' + f'{BENCH["^SOX"]["ret_1y_pct"]:.0f}%）大幅領先 S&amp;P 500（+' + f'{BENCH["^GSPC"]["ret_1y_pct"]:.1f}%），超額報酬達 {BENCH["^SOX"]["ret_1y_pct"]-BENCH["^GSPC"]["ret_1y_pct"]:.0f} 個百分點。' if is_semi else '與本籃子其他三檔的半導體類股無產業重疊，是唯一的分散化來源。'}</p>
{f'<div class="tblwrap">{V.simple_table(["期間","個股報酬","S&P 500（同期縮放）","超額報酬"], rel_rows, align=["left","right","right","right"])}</div>' if rel_rows else '<div class="call call--bad"><div class="call__h">🚩 相對強度無法計算</div><p>13 個交易日不足以建立 3／6／12 個月的相對強度基準。此為篩選器動能維度 6 個子因子全部無法評分的原因。</p></div>'}
{f'''<div class="call call--warn"><div class="call__h">⚠ 類股集中風險</div>
<p>本籃子中 MU、SKHY、MRVL 三檔同屬半導體，且 MU 與 SKHY 是同一產品循環（HBM／DRAM）的直接同業。
三者 Beta 分別為 {RAW["MU"]["info"]["beta"]:.2f}／{RAW["SKHY"]["info"]["beta"]:.2f}／{RAW["MRVL"]["info"]["beta"]:.2f}。
2026-07-28 三檔同步下跌 {abs(GAP["MU"]):.1f}%／{abs(GAP["SKHY"]):.1f}%／{abs(GAP["MRVL"]):.1f}%，
證實在此籃子內<strong>分散化不存在</strong>。</p></div>''' if is_semi else f'''
<div class="call"><div class="call__h">💡 分散化的實證與極限</div>
<p>Beta {i["beta"]:.2f} 對其他三檔的 2.03–2.20，產業與客戶完全不重疊——{tk} 是本籃子唯一的分散化來源。
但 2026-07-28 它下跌 {abs(GAP[tk]):.1f}%，是四檔中最深（因當日有財報事件）。
<strong>低 Beta 保護系統性風險，不保護個別事件風險。</strong></p></div>'''}
</section>""")

    # ══════════════════════ M11 short ══════════════════════
    ss, ssp = i.get("sharesShort"), i.get("sharesShortPriorMonth")
    sh_tbl = V.simple_table(["指標", "數值", "判讀"],
      [["空單股數", f'{ss/1e6:,.2f}M' if ss else "—", f'前月 {ssp/1e6:,.2f}M' if ssp else "未揭露"],
       ["月變動", f'<span class="{cls(-(ss/ssp-1) if ss and ssp else None)}">{pc((ss/ssp-1)*100,1,True) if ss and ssp else "—"}</span>',
        "空方回補" if (ss and ssp and ss < ssp) else ("空方加碼" if (ss and ssp) else "無法判斷")],
       ["占流通股比", pcf(i.get("shortPercentOfFloat")) if i.get("shortPercentOfFloat") else "未揭露", ""],
       ["回補天數（days-to-cover）", num(i.get("shortRatio")) + " 天" if i.get("shortRatio") else "—",
        "&lt;1 天＝無軋空燃料" if (i.get("shortRatio") or 9) < 1 else "≥5 天＝具軋空條件"],
       ["流通股", f'{i["floatShares"]/1e6:,.0f}M' if i.get("floatShares") else "—", ""]])
    d.append(f"""<section id="m11"><h2><span class="modnum">11</span>空單分析<span class="skilltag">short-interest</span></h2>
{pr['short']}
<div class="tblwrap">{sh_tbl}</div>
</section>""")

    # ══════════════════════ M12 options ══════════════════════
    opt_body = pr["opt"]
    if opt.get("atm_iv"):
        ivhv = (opt["atm_iv"] * 100) / (opt["hv"] or 1)
        otbl = V.simple_table(["指標", "數值", "判讀"],
          [["到期日（採用）", opt["expiry"], f'可用到期日 {len(opt.get("expiries") or [])} 個'],
           ["價平隱含波動率 IV", pc(opt["atm_iv"] * 100, 1),
            f'IV 區間 {pc(opt["iv_min"]*100,0)}–{pc(opt["iv_max"]*100,0)}（±25% 履約價內）'],
           ["歷史波動率 HV（年化）", pc(opt["hv"], 1),
            f'<strong>IV／HV = {ivhv:.2f}</strong>　' +
            ("IV 高於 HV → 賣方策略較有利" if ivhv > 1.1 else
             ("IV 低於 HV → 買方策略較有利" if ivhv < 0.9 else "IV 與 HV 接近"))],
           ["價平跨式權利金", money(opt["straddle"]), f'隱含單日／到期波動 <strong>{pc(opt["implied_move"],1)}</strong>'],
           ["最大痛點（Max Pain）", money(opt["max_pain"]),
            f'<span class="{cls(opt["max_pain"]/price-1)}">相對現價 {pc((opt["max_pain"]/price-1)*100,1,True)}</span>'],
           ["買權未平倉合計", f'{opt["call_oi"]:,}', ""],
           ["賣權未平倉合計", f'{opt["put_oi"]:,}', ""],
           ["賣權／買權未平倉比", num(opt["pc_oi"]),
            ('&gt;1 → 賣權未平倉較多，偏空或避險需求高' if (opt["pc_oi"] or 0) > 1 else '&lt;1 → 買權未平倉較多，偏多')]])
        strat = {
          "MU": lambda: ("賣出現金擔保賣權（Cash-Secured Put）",
                 f"IV／HV ＝ {ivhv:.2f} 代表選擇權相對歷史波動被高估，賣方有利。"
                 f"在最大痛點 {money(opt['max_pain'])} 之下、常態化情境 "
                 f"{money(cy['scen']['structural']['m15'])} 附近賣出賣權，"
                 f"等同於「以本報告認為合理的價位被指派」，且先收權利金。"
                 f"風險：若循環轉折，指派後仍面臨進一步下跌。"),
          "SKHY": lambda: ("不建議任何選擇權策略",
                   f"IV {pc(opt['atm_iv']*100,0)} 而 HV {pc(opt['hv'],0)}——"
                   f"HV 由僅 13 個交易日估計，本身不可靠，使 IV／HV ＝ {ivhv:.2f} 無法解讀。"
                   f"財報就在今日、隱含波動 {pc(opt['implied_move'],1)} 為四檔最高。"
                   f"在標的基本面資料都無法確認的情況下，加上槓桿是不合理的。"),
          "MRVL": lambda: ("多頭買權價差（Bull Call Spread），若必須做多",
                   f"IV／HV ＝ {ivhv:.2f}，選擇權偏貴，單純買買權成本過高。"
                   f"價差策略可降低權利金支出。但本報告的結論是<strong>不進場</strong>——"
                   f"在三個估值方法相差一個數量級時，用選擇權表達方向是把估值不確定性換成時間不確定性，"
                   f"並未改善勝算。"),
          "SNDL": lambda: ("無可執行策略——市場深度不足",
                   f"買權未平倉合計僅 {opt['call_oi']:,} 口、賣權 {opt['put_oi']:,} 口，"
                   f"賣權／買權未平倉比 {num(opt['pc_oi'])}。最大痛點 {money(opt['max_pain'])} "
                   f"由極少數合約決定，統計意義薄弱。"
                   f"股價 {money(price)} 下，履約價間距使任何價差策略的滑價成本超過潛在報酬。"),
        }[tk]()
        opt_body += f"""<div class="tblwrap">{otbl}</div>
<h3>策略評估</h3>
<div class="card card--surface"><div class="card__h">建議：{strat[0]}</div>
<p style="font-size:.9375rem;color:var(--ink-2)">{strat[1]}</p></div>
<p class="fignote">最大痛點以到期日 {opt['expiry']} 的全部履約價計算：
在每個履約價下，加總所有買權與賣權的內在價值 × 未平倉量，取總額最小者。
此指標假設造市商避險行為會使價格趨向該點，屬經驗法則而非預測。</p>"""
    d.append(f"""<section id="m12"><h2><span class="modnum">12</span>選擇權分析<span class="skilltag">options-analysis</span></h2>
{opt_body}
</section>""")

    # ══════════════════════ M13 economics ══════════════════════
    d.append(f"""<section id="m13"><h2><span class="modnum">13</span>總體環境<span class="skilltag">economics-analysis</span></h2>
{pr['econ']}
<h3>折現率推導與敏感度</h3>
<div class="tblwrap">{V.simple_table(["參數","數值","來源／說明"],
  [["無風險利率 rf", "4.2%", "10 年期美債殖利率（假設值，未由本資料取樣）"],
   ["股權風險溢酬 ERP", "5.0%", "假設值"],
   ["Beta（5Y 月）", num(i.get("beta")), "yfinance"],
   ["權益成本 Ke", pcf(rw["ke"]) if rw else "—", "CAPM：rf + β × ERP"],
   ["稅後負債成本 Kd", pcf(rw["kd"]) if rw else "—", f'假設稅前 5.5%、稅率 {pcf(rw["tax"],0) if rw else "—"}'],
   ["WACC（估值用）", pcf(rw["wacc"]) if rw else "—", "以市值與淨負債加權"],
   ["DCF 採用 WACC", pcf(dcfd["wacc"]), "略低於 CAPM 推導值，反映循環股的長期資金成本"]],
  align=["left","right","left"])}</div>
</section>""")

    # ══════════════════════ M14 financial-report-analyst ══════════════════════
    FRA = {
      "MU": [("營收認列", "✅ 通過", "營收成長伴隨存貨<strong>下降</strong>（$8.88B → $8.36B）——與通道塞貨的特徵相反。"),
             ("現金 vs 應計", "✅ 通過", "TTM 營運現金流 $51.43B 對淨利 $50.47B，比率 1.02。獲利有現金支撐。"),
             ("非 GAAP 落差", "✅ 通過", "本報告全程使用 GAAP 數字；前瞻 EPS $153.74 為共識預估，已標示為市場預期而非公司揭露。"),
             ("買回掩飾稀釋", "✅ 通過", "FY2025 買回金額為 0，無以買回美化每股數據的情形。"),
             ("商譽風險", "✅ 通過", "商譽僅 $1.15B，占股東權益 $54.16B 的 2.1%。減損風險極低。"),
             ("負債結構", "✅ 通過", "總負債 $6.38B 對現金 $26.02B，D/E 0.06，流動比 3.43。"),
             ("治理指標", "⚠ 注意", f"yfinance 治理評分：稽核風險 {i.get('auditRisk')}、董事會風險 {i.get('boardRisk')}、綜合 {i.get('overallRisk')}（1 最佳、10 最差）。董事會風險 7 偏高。"),
             ("資本支出強度", "🚩 紅旗", "FY2025 資本支出 $15.86B 對營運現金流 $17.52B（90%）。自由現金流僅 $1.67B。這不是舞弊，但使盈餘倍數法系統性高估股東可得報酬。")],
      "SKHY": [("幣別一致性", "🚩 紅旗", f"財報韓元、股價美元，原始企業價值 −{abs(i['enterpriseValue'])/1e12:,.1f} 兆、P/S {i['priceToSalesTrailing12Months']:.4f}、EV/EBITDA {i['enteroseToEbitda'] if False else i['enterpriseToEbitda']:.2f}。本報告已按 1 USD = 1,380 KRW 校正，但匯率為假設值。"),
               ("前瞻 EPS 合理性", "🚩 紅旗", "前瞻 EPS $40.47 × 70.99 億股 ＝ 隱含年度淨利約 $287B，超過校正後 TTM 淨利（$54.5B）五倍以上。此欄位不可用，連帶使 3.22 倍前瞻本益比不可引用。"),
               ("股息欄位一致性", "🚩 紅旗", "dividendRate／dividendYield 為空、payoutRatio 為 0，但現金流量表顯示 FY2025 支付股息 1,681 兆韓元（約 $1.22B）。兩者矛盾。"),
               ("價格歷史充足性", "🚩 紅旗", "13 個交易日。MA20／MA50／MA200／RSI／ATR 全部無法計算；波動率與最大回撤估計不可靠。"),
               ("內部人與法人資料", "🚩 紅旗", "insider_transactions、institutional_holders、major_holders 全部為空。作為外國私人發行人不受 Form 4 約束，13F 亦尚未涵蓋。"),
               ("治理指標", "🚩 紅旗", "auditRisk／boardRisk／overallRisk 全部為空值（MU 分別為 1／7／2）。無法評估。"),
               ("現金 vs 應計", "✅ 通過", "TTM 營運現金流 $51.2B 對淨利 $54.5B，比率 0.94。比率本身不受幣別影響，可信。"),
               ("商譽風險", "✅ 通過", "商譽 807 兆韓元（約 $0.59B），占股東權益 0.7%。極低。")],
      "MRVL": [("GAAP vs non-GAAP 落差", "🚩 紅旗", "TTM GAAP 營業利益 $1.263B 對 EBITDA $2.712B，差額 $1.449B（折舊攤銷）。前瞻 EPS $6.24 與最近一季 GAAP EPS $0.04 相差 156 倍。共識季度 EPS $0.927 與年度 $6.24 亦無法對帳。基準不明。"),
               ("一次性項目未拆分", "🚩 紅旗", "FY2026 淨利 $2.67B <strong>大於</strong>當年營業利益 $1.34B，代表存在大額非營業收益。季度淨利序列 $178M → $195M → $1,901M → $396M → $34.5M 無法用於趨勢外推。"),
               ("商譽風險", "🚩 紅旗", "商譽 $11.06B 占股東權益 $14.31B 的 <strong>77.3%</strong>、總資產的 49.6%。有形每股淨值約 $3.71（現價的 2.1%）。四年未認列大額減損。"),
               ("現金 vs 應計", "⚠ 注意", "TTM 營運現金流 $2.056B 對淨利 $2.527B，比率 <strong>0.81</strong>（低於 1.0）。與淨利含一次性項目的判斷一致。"),
               ("自由現金流成長", "🚩 紅旗", "FY2026 自由現金流 $1.39B 與 FY2025 的 $1.39B <strong>完全持平</strong>，而同期營收成長 42%。成長未轉化為現金。"),
               ("買回掩飾稀釋", "⚠ 注意", "FY2026 買回 $2.04B，較 FY2025 的 $0.72B 大增 183%。在 ROIC 6.4% 低於 WACC 14.9% 的情況下，大額買回的資本配置合理性需檢視。"),
               ("存貨趨勢", "⚠ 注意", "存貨 $1.03B → $1.39B（+35%），營收 +42%。存貨成長略慢於營收，尚屬同步，但需持續觀察。"),
               ("治理指標", "⚠ 注意", f"稽核風險 {i.get('auditRisk')}、董事會風險 {i.get('boardRisk')}、綜合 {i.get('overallRisk')}。董事會風險 4 中等。")],
      "SNDL": [("現金 vs 應計", "✅ 通過", "TTM 營運現金流 +$66.6M 對淨利 −$11.0M。現金流<strong>優於</strong>帳面獲利，虧損來自非現金費用（折舊、減值）而非現金流出。這是虧損公司中相對健康的形態。"),
               ("商譽風險", "✅ 通過", "商譽 $0.12B 占股東權益 $1.064B 的 11%。對照 MRVL 的 77%，SNDL 的淨值有實體資產支撐。"),
               ("資產負債表流動性", "⚠ 注意", "最新一期現金 <strong>$183.2M</strong>、流動比 4.84、速動比 2.83、淨現金 $45.5M。破產風險在可見期間內極低，但現金半年由 $252M 降至 $183M（−27%），安全邊際在縮小。"),
               ("買回掩飾稀釋", "✅ 通過", "買回為真實註銷（申報類型為 Redemption／Cancelation），且在股價低於淨值 70% 處執行。資本配置方向正確。"),
               ("營收認列", "✅ 通過", "存貨四年持平於 $0.13B，未隨營收波動異常累積。無通道塞貨跡象。"),
               ("Piotroski 基期偏誤", "⚠ 注意", "7／9 中有 3 分來自低基期的改善檢定（ROA 由 −7.0% 升至 −1.2%）。與 MU 的 9／9 不可直接比較——F-Score 衡量「變好」而非「好」。"),
               ("季度趨勢一致性", "🚩 紅旗", "季度營業利益五季正負交替（+$2.9M → −$9.4M → +$10.3M → −$11.2M → −$5.4M），無任何兩季同向。年度尺度的改善趨勢在季度尺度上不存在。"),
               ("股東權益侵蝕（且加速）", "🚩 紅旗", "年度 $1.306B → $1.212B → $1.133B → $1.101B（四年 −16%、年均 −5.3%），最近兩季再降至 <strong>$1.064B</strong>（年化 −7.1%）。這是本報告的主結論：折價會靠分母縮小自行消失。"),
               ("負債比趨勢", "⚠ 注意", "長期負債／總資產由 11.3% 升至 12.7%（Piotroski 未通過項）。金額不大，但方向不利。"),
               ("bookValue 欄位一致性", "🚩 紅旗", "yfinance 的 <code>bookValue</code> 為 $2.9637／股，但申報資產負債表推算為 <strong>$4.086／股</strong>（差 27%）。連帶使該欄位的 P/B 0.4116 與實際的 <strong>0.2986</strong> 不一致。同一欄位在 MU 與 MRVL 上完全吻合（比率 1.000），故此為 SNDL 個別的資料瑕疵。本報告一律採用申報資產負債表。")],
    }[tk]
    fra_tbl = V.simple_table(["檢查項目", "結果", "說明"],
      [[f"<strong>{a}</strong>", b, c] for a, b, c in FRA], align=["left", "center", "left"])
    nred = sum(1 for _, s, _ in FRA if "紅旗" in s)
    nwarn = sum(1 for _, s, _ in FRA if "注意" in s)
    npass = sum(1 for _, s, _ in FRA if "通過" in s)
    d.append(f"""<section id="m14"><h2><span class="modnum">14</span>財報稽核<span class="skilltag">financial-report-analyst</span></h2>
{pr['fra']}
<div class="grid g3" style="margin-bottom:var(--s-16)">
<div class="tile"><div class="tile__k">通過</div><div class="tile__v up">{npass}</div><div class="tile__n">項</div></div>
<div class="tile"><div class="tile__k">注意</div><div class="tile__v fl">{nwarn}</div><div class="tile__n">項</div></div>
<div class="tile"><div class="tile__k">紅旗</div><div class="tile__v dn">{nred}</div><div class="tile__n">項</div></div>
</div>
<div class="tblwrap">{fra_tbl}</div>
</section>""")

    # ══════════════════════ M15 dividend ══════════════════════
    DIV = {
      "MU": f"""<div class="tblwrap">{V.simple_table(["項目","數值","評註"],
        [["年化股息", money(i.get("dividendRate")), "每股"],
         ["股息殖利率", pcf(i.get("dividendYield"),2), "象徵性水準"],
         ["配息率", pcf(i.get("payoutRatio"),2), "TTM 淨利的 1.1%"],
         ["FY2025 股息支付", money(0.52e9), "四年幾乎持平（$0.46B → $0.52B）"],
         ["FY2025 股票買回", "$0", "上一輪循環（FY2022）曾買回 $2.43B"],
         ["FY2025 資本支出", money(15.86e9), "占營運現金流 90%"]], align=["left","right","left"])}</div>
<div class="call call--ink"><div class="call__h">📐 資本配置的排序很清楚</div>
<p>FY2025：營運現金流 $17.52B → 資本支出 $15.86B（90%）→ 股息 $0.52B（3%）→ 買回 $0。
<strong>資本支出吸收了幾乎全部現金流。</strong></p>
<p>這對循環頂點的記憶體廠是<strong>正確的</strong>選擇——不投資就會失去技術世代，
而失去世代在記憶體產業等同於退出市場。但投資人必須理解其後果：
持有 MU 在可見期間內不會獲得有意義的現金回報，全部報酬必須來自股價。
在買回為零的情況下，管理層也沒有以資本配置行動表達「股價便宜」的看法——
這一點與內部人只賣不買的訊號方向一致。</p></div>""",
      "SKHY": "",
      "MRVL": f"""<div class="tblwrap">{V.simple_table(["項目","數值","評註"],
        [["年化股息", money(i.get("dividendRate")), "每股"],
         ["股息殖利率", pcf(i.get("dividendYield"),2), "象徵性水準"],
         ["配息率", pcf(i.get("payoutRatio"),2), ""],
         ["FY2026 股息支付", money(0.21e9), "四年完全持平於 $0.20–0.21B"],
         ["FY2026 股票買回", money(2.04e9), "較 FY2025 的 $0.72B 大增 183%"],
         ["FY2026 自由現金流", money(1.39e9), "<strong>買回金額超過自由現金流 47%</strong>"],
         ["FY2026 資本支出", money(0.36e9), "資本支出強度遠低於記憶體廠"]], align=["left","right","left"])}</div>
<div class="call call--bad"><div class="call__h">🚩 買回金額超過自由現金流</div>
<p>FY2026：自由現金流 $1.39B，但買回 $2.04B ＋ 股息 $0.21B ＝ 股東回報 $2.25B。
<strong>股東回報超過自由現金流 62%</strong>，差額須動用現金餘額或舉債
（現金由 $0.95B 增至 $2.64B，故本年度是以其他來源支應，可能含處分所得）。</p>
<p>更關鍵的問題：在 <strong>ROIC 6.4% 低於 WACC 14.9%</strong> 的情況下大額買回，
資本配置的合理性需要檢視。買回在股價低於內在價值時創造價值；
但本報告的三種估值方法中，兩種（GAAP 常態化 $22.05、DCF $46.84）
都指出現價 {money(price)} 遠高於內在價值。
若這兩種方法接近正確，FY2026 的 $2.04B 買回是在<strong>高價回購</strong>——
而買回均價落在股價 $200–$330 的區間內。</p></div>""",
      "SNDL": f"""<div class="tblwrap">{V.simple_table(["項目","數值","評註"],
        [["股息", "無", "dividendRate 為空、配息率 0"],
         ["FY2025 股票買回", money(15.3e6), "四年累計 $45.7M"],
         ["FY2025 自由現金流", money(58.1e6), "買回占自由現金流 26%"],
         ["股價淨值比（申報 BS）", f'{BS["SNDL"]["pb"]:.2f}', "買回每 $1 註銷約 $3.35 帳面淨值"],
         ["每股帳面淨值", money(BS["SNDL"]["bv_ps"]), f'現價的 {BS["SNDL"]["bv_ps"]/price:.2f} 倍'],
         ["帳上現金（最新一期）", money(BS["SNDL"]["cash"]), f'占市值 {BS["SNDL"]["cash_cover"]*100:.0f}%（半年前為 $252M）'],
         ["股東權益（最新一期）", money(BS["SNDL"]["equity"]), "2026-06-30"],
         ["年化淨值侵蝕金額", f'<span class="dn">{money(abs(BS["SNDL"]["erosion_ann"]))}</span>',
          f'<strong>買回 $15.3M 僅約其 {15.3e6/abs(BS["SNDL"]["erosion_ann"])*100:.0f}%</strong>'],
         ["侵蝕速度趨勢", f'<span class="dn">{BS["SNDL"]["erosion_pct"]:.1f}%／年</span>',
          "四年平均 −5.3%／年 → 最近兩季年化 −7.1%，<strong>加速中</strong>"]], align=["left","right","left"])}</div>
<div class="call call--warn"><div class="call__h">⚠ 本報告最重要的一場賽跑</div>
<p>SNDL 面對一個罕見且數學上明確的處境：<strong>股價淨值比 0.30，手上有 $183.2M 現金。</strong>
在這個折價下買回，每投入 $1 市值即為剩餘股東註銷約 $3.35 的帳面淨值——
這是低於淨值買回在數學上唯一正確的用法，管理層的方向是對的。</p>
<p><strong>但速度不對。</strong>FY2025 買回 $15.3M，而股東權益在最近兩季由 $1.101B 降至 $1.064B——
年化侵蝕 <strong>$75M</strong>。<strong>買回規模僅約侵蝕速度的兩成。</strong></p>
<p>這決定了整個投資論述：若買回速度超過侵蝕速度，每股淨值上升，折價成為真實的報酬來源；
若持續落後，每股淨值下降，折價只會隨分母縮小而自行消失。
目前落後，而這是<strong>可每季驗證</strong>的。</p></div>""",
    }[tk]
    d.append(f"""<section id="m15"><h2><span class="modnum">15</span>股息與資本配置<span class="skilltag">dividend-analysis</span></h2>
{pr['div']}
{DIV}
</section>""")

    # ══════════════════════ synthesis: thesis ══════════════════════
    bull_html = "".join(f'<li><strong>{t}</strong><br><span style="color:var(--ink-2)">{x}</span></li>'
                        for t, x in pr["bull"])
    bear_html = "".join(
        f'<li><strong>{t}</strong>　<span class="st st--{"bad" if p in ("高","已發生") else "warn"}">'
        f'{"🚩" if p in ("高","已發生") else "⚠"} 機率：{p}</span>'
        f'<span class="st st--neut" style="margin-left:6px">影響：{im}</span>'
        f'<br><span style="color:var(--ink-2)">{x}</span></li>' for t, p, im, x in pr["bear"])
    d.append(f"""<section id="thesis"><h2>投資論點</h2>
{"".join(f"<p>{x}</p>" for x in pr["thesis"])}
<h3>多方論述</h3><ul style="line-height:1.8">{bull_html}</ul>
<h3>空方論述</h3><ul style="line-height:1.8">{bear_html}</ul>
</section>""")

    # ══════════════════════ bear-case red team ══════════════════════
    KILLERS = {
      "MU": ["<strong>HBM 供應合約長度與定價機制被證實</strong>——若公司揭露多年期定價鎖定的合約結構，"
             "「峰值利益率不可持續」的核心論點即失效，$516.55（結構性中循環 × 15 倍）以上的價位變得合理。",
             "<strong>資本支出見頂而營收持續成長</strong>——若資本支出強度由 90% 降至 60% 以下"
             "而營收不受影響，自由現金流將大幅轉正，使 FCF-DCF 的 $184.62 大幅上修。",
             "<strong>連續四季毛利率維持 80% 以上</strong>——四季是一個完整的產業訂價週期，"
             "若能維持，則「這次不一樣」從論述變成證據。",
             "<strong>內部人開始買進</strong>——目前 12 賣 0 買。任何一筆有意義的內部人買進"
             "都會反轉市場訊號維度的判讀。",
             "<strong>Samsung 或 SK hynix 出現重大技術挫敗</strong>——三家寡占變二家，定價權大幅提升。"],
      "SKHY": ["<strong>20-F 或韓國交易所財報確認幣別與換股比率</strong>——這是唯一能讓本報告從"
               "「拒絕交付」轉為「可執行」的條件，且它與公司營運無關，純粹是資料問題。",
               "<strong>累積 50 個交易日的價格歷史</strong>（約 2026 年 9 月中）——"
               "使 MA50、RSI、ATR 與相對強度可計算，動能維度的 6 個子因子恢復可用。",
               "<strong>首份 13F 揭露顯示機構大幅建倉</strong>（預計 2026 年 11 月）——"
               "將提供目前完全缺失的法人訊號。",
               "<strong>ROIC 30.8% 在下一輪循環低點仍維持為正</strong>——"
               "若能證實，SK hynix 的護城河評等應由 ★★★★☆ 上調，且應相對 MU 享有溢價而非折價。"],
      "MRVL": ["<strong>GAAP 營業利益率突破 20%</strong>——這是最直接的論點殺手。"
               "若營收持續成長同時 GAAP 利益率明顯擴張，則「規模經濟終將顯現」成立，"
               "常態化盈餘法的 $22.05 將大幅上修，ROIC 也會向 WACC 收斂。",
               "<strong>公司清楚拆分一次性項目與經常性獲利</strong>——"
               "目前 GAAP 獲利序列不可用於趨勢分析的主因是一次性項目未拆分。"
               "若揭露改善，估值的三個矛盾答案可能收斂為一個。",
               "<strong>取得一個大型雲端業者的多世代 ASIC 設計案</strong>——"
               "客製化 ASIC 的營收能見度可達三到五年，一個重大設計案能實質改變成長軌跡的確定性。",
               "<strong>商譽通過減損測試且客製化 ASIC 營收達到預期</strong>——"
               "將消除 $11.06B（權益 77%）的最大單一下行風險。",
               "<strong>被併購</strong>——在 AI 互連領域具戰略價值，"
               "且商譽占比高使帳面價值對併購方的意義低於其技術與客戶關係。"],
      "SNDL": ["<strong>連續兩季營業利益為正</strong>——這是唯一真正重要的論點殺手，"
               "且<strong>下一季財報就能檢驗</strong>。若成立，淨值侵蝕停止，"
               "0.30 倍股價淨值比立刻從陷阱變成機會。",
               "<strong>股東權益季度序列止穩於 $1.064B</strong>——直接推翻本報告的主結論。",
               "<strong>買回速度超過淨值侵蝕速度</strong>——"
               "年度買回若由 $15.3M 提高至 $75M 以上，每股淨值開始上升。",
               "<strong>營收恢復正成長</strong>——TTM −4.4%，需證明市場份額未流失。",
               "<strong>加拿大大麻市場整併</strong>——若供過於求的結構改善，"
               "毛利率 27.2% 有擴張空間，整個產業的估值基準都會上移。",
               "<strong>被併購或主動清算</strong>——市值 $317.6M、淨值 $1.064B、"
               "淨現金 $45.5M，對併購方或行動派股東而言，資產折價足夠明顯。"],
    }[tk]
    floor = {
      "MU": f"<strong>基本面底部：</strong>淨現金 {money(abs(n['net_debt']))}（每股約 {money(abs(n['net_debt'])/n['shares'])}）"
            f"＋ 每股帳面淨值 {money(i.get('bookValue'))}。"
            f"以「均值回歸 × 10 倍」的 {money(cy['scen']['revert']['m10'])} 為極端空方情境下的參考底部——"
            f"但即使該情境成真，MU 也不會破產：FY2023 在 −34.8% 營業利益率下仍存活。",
      "SKHY": f"<strong>基本面底部：</strong>淨現金 {money(abs(n['net_debt']))}（校正後）"
              f"＋ 每股帳面淨值 {money(i.get('bookValue'))}。"
              f"「均值回歸 × 10 倍」對應 {money(cy['scen']['revert']['m10'])}。"
              f"但需誠實說明：<strong>這個底部同樣建立在假設匯率上</strong>，"
              f"因此其精確度低於其他三檔。",
      "MRVL": f"<strong>基本面底部：</strong>這是 MRVL 最脆弱之處。"
              f"股東權益 $14.31B 中商譽 $11.06B，<strong>有形每股淨值僅約 $3.71</strong>"
              f"（現價 {money(price)} 的 2.1%）。淨負債 {money(n['net_debt'])}。"
              f"實質上，MRVL <strong>沒有資產面底部</strong>——若成長論述失效，"
              f"帳面價值無法提供支撐。這使它的下行風險在四檔中最不受限。",
      "SNDL": f"<strong>基本面底部：這是 SNDL 唯一明確優於其他三檔之處。</strong>"
              f"帳上現金 {money(BS[tk]['cash'])} 對市值 {money(i['marketCap'])}——"
              f"<strong>現金覆蓋 {BS[tk]['cash_cover']*100:.0f}% 的市值</strong>。淨現金 {money(abs(n['net_debt']))}、"
              f"每股帳面淨值 {money(BS[tk]['bv_ps'])}（現價 {money(price)} 的 {BS[tk]['bv_ps']/price:.2f} 倍）、流動比 4.84。"
              f"扣除淨現金後，市場對整個營運事業（TTM 營收 {money(n['revenue'])}）"
              f"的定價僅約 {money(i['marketCap']-abs(n['net_debt']))}。"
              f"<strong>下行有實質保護；問題純粹是這個保護會不會隨時間縮小。</strong>",
    }[tk]
    bear_score = {"MU": 7.0, "SKHY": 5.5, "MRVL": 8.0, "SNDL": 6.5}[tk]
    d.append(f"""<section id="bear"><h2>空方紅隊<span class="skilltag">bear-case</span></h2>
<div class="call call--bad"><div class="call__h">⚠ 這是刻意單方面的空方論述</div>
<p>本節為<strong>紅隊／魔鬼代言人</strong>工具，設計上就偏向下行。它的價值來自單方面——
強迫反面證據浮出水面，以壓力測試多方論點。<strong>它不是平衡的判斷，也不應被當作平衡判斷呈現。</strong>
請與上方的<a href="#m1">個股評估</a>與<a href="#thesis">多方論述</a>並讀。</p></div>
<h3>三句話空方論點</h3>
<div class="card" style="background:#fdf0f0;border-color:#f7c4c4">
<p style="font-size:1.0625rem;line-height:1.85">{{}}</p></div>
<h3>空方論點強度：{bear_score:.1f} / 10</h3>
{V.figure(V.gauge(bear_score, width=280, height=170, caption="空方論點強度"), "空方論點強度評分")}
<h3>下行量化與基本面底部</h3>
<p>{floor}</p>
<h3>論點殺手 — 什麼會證明空方是錯的（框架強制項）</h3>
<ol style="line-height:1.8">{"".join(f"<li>{k}</li>" for k in KILLERS)}</ol>
<div class="call"><div class="call__h">🤝 空方自己承認的最大風險</div>
<p>{{}}</p></div>
</section>""".format(
      {"MU": "美光正以歷史平均 16.6 倍的獲利水準交易，而市場給它的估值隱含這個水準永久維持；"
             "自由現金流僅為帳面獲利的 15%，說明這些獲利必須不斷再投入才能存在；"
             "而最了解公司的人——包含執行長——在過去四個月賣出 $169.2M，一股都沒有買。",
       "SKHY": "SK hynix 可能是本籃子中最優秀的公司，但沒有人能從現有資料證實這一點："
       "企業價值是負數、前瞻本益比對不上每股獲利、股息欄位與現金流量表矛盾、"
       "價格歷史只有 13 天，而內部人與法人資料完全不存在。"
       "在能夠稽核之前，優秀是一個假設，不是一個事實。",
       "MRVL": "MRVL 的營收連五季創高，但 GAAP 淨利在最新一季塌到 $34.5M、ROIC 6.4% 低於 WACC 14.9%，"
       "意味著這個成長正在毀滅價值；股東權益的 77% 是併購留下的商譽，有形每股淨值只有 $3.71；"
       "而執行長、總裁、財務長在 $199–$299 之間全數賣出，現價 $174.47 低於他們每一筆成交價。",
       "SNDL": "SNDL 的資產折價是真的——市值只有淨值的 30%，現金覆蓋 58% 的市值。"
       "但股東權益從 $1.306B 融化到 $1.064B，最近兩季年化 −7.1% 且加速中；"
       "季度營業利益五季正負交替、沒有任何兩季同向；"
       "而公司的買回速度只有淨值侵蝕速度的兩成。這個折價不需要股價下跌就會消失。"}[tk],
      {"MU": "估值支撐與軋空風險都不存在（回補天數 0.69 天），但<strong>做空 MU 最大的風險是空方可能太早</strong>。"
             "AI 資本支出循環的持續時間無法從財務數字預測，而 42 位分析師的平均目標價 $1,507.38 意味著"
             "市場共識與空方完全相反。此外 Piotroski 9／9 與淨現金 $19.65B 使基本面崩塌的路徑必須經過"
             "「利益率下滑」而非「財務危機」——這條路徑可能非常緩慢。",
       "SKHY": "空方在此的論點是「資料不足」，而<strong>資料不足會被時間自動修正</strong>。"
       "到 2026 年 11 月 13F 揭露、9 月中累積 50 個交易日之後，本節的大部分論點就會失效。"
       "同時 ROIC 30.8%、ROIC−WACC +16.6pp、循環谷底比 MU 淺 11.2pp 這些<strong>比率</strong>"
       "不受幣別影響，它們指向的是一家品質優於 MU 的公司。空方的立場是暫時的，不是結構的。",
       "MRVL": "<strong>GAAP 常態化盈餘法可能系統性低估 MRVL。</strong>"
       "併購無形資產攤銷是非現金項目，且不需要重複投入——以 EBITDA $2.712B 衡量，"
       "MRVL 的現金獲利能力遠高於 GAAP 呈現的 $1.263B。若市場採用的 non-GAAP 基準才是正確的，"
       "則 28 倍前瞻本益比只是偏貴，而非本節主張的離譜。此外 RSI 28.9 已超賣、"
       "回補天數 0.71 天無軋空燃料、40 位分析師零賣出、且在 AI 互連領域具併購價值。",
       "SNDL": "<strong>現金覆蓋 58% 市值構成真實的下行保護。</strong>"
       "SNDL 不會破產（流動比 4.84、淨現金 $45.5M），因此空方無法期待價格歸零。"
       "同時：年度尺度的營運改善是真實的（營業利益率 −8.6% → −0.5%、自由現金流由負轉正 $58.1M）、"
       "公司在低於淨值 70% 處系統性買回、空單僅占流通股 0.75% 意味著幾乎沒有人在做空。"
       "而「連續兩季營業利益為正」這個論點殺手<strong>下一季就可能出現</strong>。"}[tk]))

    # ══════════════════════ scorecard ══════════════════════
    card = ""
    for k in ["business", "valuation", "signal", "technical", "risk"]:
        v = comp["phases"][k]; w = comp["weights"][k]
        kk = "good" if v >= 6.5 else ("warn" if v >= 4 else "bad")
        card += (f'<tr><th scope="row" style="text-align:left">{PHASE_LABEL[k]}</th>'
                 f'<td>{w:.0%}</td><td><strong>{v:.1f}</strong></td>'
                 f'<td>{comp["weighted"][k]:.3f}</td>'
                 f'<td>{st(kk, "強" if v>=6.5 else ("中" if v>=4 else "弱"))}</td></tr>')
    radar = V.radar_chart([PHASE_LABEL[k] for k in ["business", "valuation", "signal", "technical", "risk"]],
        [{"name": tk, "colour": col,
          "values": [comp["phases"][k] for k in ["business", "valuation", "signal", "technical", "risk"]]}],
        size=380)
    d.append(f"""<section id="card"><h2>綜合評分卡</h2>
<div class="grid g2">
<div class="tblwrap"><table class="dt">
<thead><tr><th style="text-align:left">階段</th><th>權重</th><th>子分數</th><th>加權分</th><th>評等</th></tr></thead>
<tbody>{card}
<tr style="background:var(--green-wash)"><th scope="row" style="text-align:left"><strong>綜合評分</strong></th>
<td><strong>100%</strong></td><td>—</td><td><strong>{comp['total']:.2f}</strong></td>
<td>{st(kind, rec.split(" ")[0])}</td></tr></tbody></table></div>
<div><div class="figbox">{radar}</div><figcaption style="text-align:center">五階段評分（外圈 10）</figcaption></div>
</div>
<p class="fignote">評分區間：8.0–10.0 強力買進　·　6.5–7.9 買進　·　5.0–6.4 持有／觀察　·
3.5–4.9 減碼　·　0.0–3.4 賣出／避開。</p>
</section>""")

    # ══════════════════════ valuation summary ══════════════════════
    vs_rows = []
    for key in ["revert", "ex_trough", "structural", "peak"]:
        s = cy["scen"].get(key)
        if not s: continue
        vs_rows.append([SCEN_LBL[key], money(s["m15"]),
                        f'<span class="{cls(s["m15"]/price-1)}">{pc((s["m15"]/price-1)*100,0,True)}</span>',
                        f'{pcf(s["opm"])} 營業利益率 × 15 倍'])
    DCF_LBL = {"bear": "DCF 空方情境", "base": "DCF 基準情境", "bull": "DCF 多方情境"}
    for s in ["bear", "base", "bull"]:
        v = dcfd["scenarios"][s]["per_share"]
        vs_rows.append([DCF_LBL[s],
                        money(v), f'<span class="{cls(v/price-1)}">{pc((v/price-1)*100,0,True)}</span>',
                        f'WACC {pcf(dcfd["wacc"])}，年 1–5 成長 {pcf(dcfd["scenarios"][s]["g1"],0,True)}'])
    if i.get("targetMeanPrice"):
        vs_rows.append(["分析師共識目標價", money(i["targetMeanPrice"]),
                        f'<span class="{cls(i["targetMeanPrice"]/price-1)}">{pc((i["targetMeanPrice"]/price-1)*100,0,True)}</span>',
                        f'{i.get("numberOfAnalystOpinions")} 位分析師平均'])
    d.append(f"""<section id="valsum"><h2>估值總結</h2>
<p>現價 <strong>{money(price)}</strong>。下表彙整本報告全部估值方法的結論。</p>
<div class="tblwrap">{V.simple_table(["方法／情境", "每股價值", "相對現價", "關鍵假設"], vs_rows,
  align=["left","right","right","left"])}</div>
<div class="call {'call--bad' if tk=='MRVL' else 'call--warn'}"><div class="call__h">
{'🚩' if tk=='MRVL' else '⚠'} 安全邊際評估</div>
<p>{{}}</p></div>
</section>""".format({
  "MU": f"各方法給出的每股價值從 {money(cy['scen']['revert']['m10'])} 到 {money(i['targetMeanPrice'])} "
        f"橫跨 <strong>{i['targetMeanPrice']/cy['scen']['revert']['m10']:.0f} 倍</strong>。"
        f"這不是一個估值區間，而是對「峰值利益率能否維持」這個單一問題的不同答案。"
        f"現價落在「維持 TTM 利益率 × 15 倍」附近，"
        f"意味著<strong>安全邊際為零</strong>：投資人已為最樂觀的營運假設付了全價，"
        f"卻仍完整承擔循環回落的風險。",
  "SKHY": f"各方法的每股價值從 {money(cy['scen']['revert']['m10'])} 到 {money(i['targetMeanPrice'])}。"
          f"現價 {money(price)} 高於「維持 TTM 利益率 × 15 倍」的 {money(cy['scen']['peak']['m15'])}——"
          f"與 MU 的處境相同或更極端。"
          f"但<strong>更重要的是：所有這些數字都依賴 1 USD = 1,380 KRW 的假設匯率</strong>，"
          f"其誤差帶約 ±6%。在誤差帶與方法分歧同時存在的情況下，"
          f"討論安全邊際的精確數值並無意義。",
  "MRVL": "三個方法給出 <strong>$22.05、$46.84、$256.91</strong>——相差超過一個數量級。"
          "這不是區間，而是三個彼此矛盾的答案，源於 GAAP 與 non-GAAP 基準的鴻溝。"
          "<strong>本報告拒絕在此給出單一目標價</strong>，因為那會是虛假的精確。"
          "可以確定的是：MRVL 沒有資產面底部（有形每股淨值 $3.71），"
          "因此若成長論述失效，下行不受限。",
  "SNDL": f"SNDL 是四檔中唯一<strong>估值明確便宜</strong>的標的："
          f"股價淨值比 0.30、P/S 0.34、現金覆蓋 58% 市值、DCF 基準情境 "
          f"{money(dcfd['scenarios']['base']['per_share'])}（+{(dcfd['scenarios']['base']['per_share']/price-1)*100:.0f}%）、"
          f"連空方情境 {money(dcfd['scenarios']['bear']['per_share'])} 都高於現價。"
          f"<strong>安全邊際在靜態意義上存在。</strong>"
          f"本報告仍給出偏空結論，唯一理由是<strong>動態的</strong>："
          f"淨值年化侵蝕 7.1% 且加速中，而買回速度只有其兩成。安全邊際正在縮小。"}[tk]))

    # ══════════════════════ entry / exit ══════════════════════
    entry_title, entry_body = pr["entry"]
    ladder = ""
    if tk == "MU":
        atr = h["atr14"]
        cap_sh = 500
        floor_sh = 300
        per = cap_sh / 5
        cum_sh, cum_cost = 0, 0.0
        lr = []
        for k in range(5):
            px = round((price - k * atr) / 5) * 5
            cum_sh += per; cum_cost += per * px
            lr.append([f"第 {k+1} 階", money(px), f"{per:.0f}", f"{cum_sh:.0f}",
                       money(cum_cost), money(cum_cost / cum_sh),
                       pc((px / price - 1) * 100, 1, True)])
        ladder = f"""<h3>加碼階梯示範<span class="skilltag">position-ladder</span></h3>
<div class="call call--warn"><div class="call__h">⚠ 這是情境模擬，不是操作建議</div>
<ul style="margin:6px 0">
<li><strong>降低平均成本不等於賺錢。</strong>平均成本是會計與心理的定錨，不是報酬指標。
下表同時列出總投入與平均成本，但真正的報酬取決於最終出場價格。</li>
<li><strong>這是波動率收割。</strong>此策略在區間震盪的行情中優於買進持有，
在單邊趨勢（無論漲跌）中都較差。只漲不跌會使階梯填不滿；只跌不漲會填滿後繼續跌。</li>
<li><strong>真正的優勢是控倉。</strong>「到 {cap_sh} 股就停止加碼，無論如何」——
這個硬性上限是把向下攤平從無上限的負債轉為有界限的押注的唯一機制。</li>
</ul></div>
<p><strong>參數</strong>：上限 {cap_sh} 股（約 {money(cap_sh*price)}）、
下限（核心永不賣出）{floor_sh} 股、5 階、階距 1.0 × ATR(14) ＝ {money(atr)}、
等股數配置、稅務假設為應稅帳戶、成本基礎 FIFO。</p>
<div class="tblwrap">{V.simple_table(["階", "價位", "本階股數", "累計股數", "累計投入", "混合平均成本", "距現價"],
  lr, align=["left","right","right","right","right","right","right"])}</div>
<p class="fignote"><strong>完全填滿時</strong>：投入 {money(sum(float(r[4].replace("$","").replace(",","")) for r in lr[-1:]))}、
平均成本 {lr[-1][5]}、需承受自現價下跌 {pc((float(lr[-1][1].replace("$","").replace(",",""))/price-1)*100,1)} 的過程。
若價格停在最低階，未實現損失為 0（平均成本等於該價位上方）。
<strong>階梯填不滿的問題</strong>：若 MU 在此不回落而直接上行，此階梯只會成交第 1 階（20%）。
本報告的處理方式是<strong>不設起始批次</strong>——因為<a href="#valsum">估值總結</a>已指出
現價安全邊際為零，先建立 30–40% 部位與該結論矛盾。</p>
<div class="call call--bad"><div class="call__h">🚩 論點破裂出場閘門</div>
<p>以下任一條件成立時，<strong>停止階梯並出場</strong>，而非繼續向下加碼：</p>
<ul>
<li>連續兩季毛利率下滑（循環轉折確認）</li>
<li>資本支出指引再上調而營收指引下修（現金流惡化）</li>
<li>三家寡占中任一家宣布大幅擴產或降價（定價權假設破裂）</li>
</ul>
<p>在上限 {cap_sh} 股處，加碼停止。進一步下跌不是加碼的理由，而是重新執行論點檢驗的理由。
<strong>在下跌過程中提高上限，是這個計畫最常見的失敗方式。</strong></p></div>"""

    exit_rows = []
    if tk == "MU":
        exit_rows = [["空方目標", money(cy["scen"]["ex_trough"]["m12"]), "利益率回到除谷底均值 × 12 倍"],
                     ["基準目標", money(cy["scen"]["structural"]["m15"]), "結構性中循環 × 15 倍（本報告中心情境）"],
                     ["多方目標", money(cy["scen"]["peak"]["m18"]), "峰值利益率維持 × 18 倍"],
                     ["停損參考", money(cy["scen"]["ex_trough"]["m10"]), "跌破即代表市場已定價完全均值回歸"]]
    elif tk == "SKHY":
        exit_rows = [["空方目標", money(cy["scen"]["ex_trough"]["m12"]), "利益率回到除谷底均值 × 12 倍"],
                     ["基準目標", money(cy["scen"]["structural"]["m15"]), "結構性中循環 × 15 倍"],
                     ["多方目標", money(cy["scen"]["peak"]["m18"]), "峰值利益率維持 × 18 倍"],
                     ["前提", "—", "<strong>以上全部依賴假設匯率，誤差帶約 ±6%</strong>"]]
    elif tk == "MRVL":
        exit_rows = [["GAAP 常態化", money(cy["scen"]["peak"]["m18"]), "目前 GAAP 利益率 × 18 倍"],
                     ["DCF 基準", money(dcfd["scenarios"]["base"]["per_share"]), f'WACC {pcf(dcfd["wacc"])}'],
                     ["分析師共識", money(i["targetMeanPrice"]), "non-GAAP 基準，40 位分析師"],
                     ["有形淨值底部", money(3.71), "<strong>商譽剔除後的每股帳面價值</strong>"]]
    else:
        exit_rows = [["清算價值參考", money(BS[tk]["bv_ps"]), f'每股帳面淨值，依申報 BS（現價的 {BS[tk]["bv_ps"]/price:.2f} 倍）'],
                     ["DCF 基準", money(dcfd["scenarios"]["base"]["per_share"]), f'WACC {pcf(dcfd["wacc"])}'],
                     ["DCF 空方", money(dcfd["scenarios"]["bear"]["per_share"]), "營收年減 8%，仍高於現價"],
                     ["現金底部", money(BS[tk]["cash"] / n["shares"]), f'每股帳上現金（占現價 {BS[tk]["cash"]/n["shares"]/price*100:.0f}%）']]
    d.append(f"""<section id="entry"><h2>進出場策略</h2>
<h3>進場：{entry_title}</h3>
{entry_body}
{ladder}
<h3>出場參考位</h3>
<div class="tblwrap">{V.simple_table(["情境", "價位", "依據"], exit_rows, align=["left","right","left"])}</div>
<h3>部位規模</h3>
<p>依 <code>full-report</code> 的部位規模規範對照本檔的結論：</p>
<div class="tblwrap">{V.simple_table(["風險偏好","框架建議上限","本報告對 " + tk + " 的建議"],
  [["積極型", "5–7% 投組", "0%（不建立部位）"],
   ["穩健型", "2–4% 投組", "0%（不建立部位）"],
   ["試單型", "1–2% 投組",
    {"MU": "0%——若必須參與，僅在上表基準目標以下分批，且套用上方階梯的硬性上限",
     "SKHY": "0%——資料不足，非估值問題。列入觀察名單",
     "MRVL": "0%——三個估值答案相差一個數量級時，任何部位規模都是猜測",
     "SNDL": "0%——除非「連續兩季營業利益為正」成立"}[tk]]],
  align=["left","center","left"])}</div>
<p class="fignote">框架另規定：高 Beta 或單一產品線標的的集中度上限應為 5%（而非大型股的 10%）。
{tk} 的 Beta {num(i.get('beta'))} {'超過 2.0，屬高 Beta 類別。' if (i.get('beta') or 0) > 2 else '低於 1.0，但市值僅 ' + money(i['marketCap']) + '，屬小型股，集中度上限同樣應從嚴。'}</p>
</section>""")

    # ══════════════════════ catalyst calendar ══════════════════════
    cats = {
      "MU": lambda: [(e["date"], "FY2026 Q4 財報", "極高",
              f"共識 EPS ${e['eps_avg']:,.2f}（區間 ${e['eps_lo']:,.2f}–${e['eps_hi']:,.2f}）、"
              f"營收 {money(e['rev_avg'])}。選擇權隱含單日波動 {pc(opt.get('implied_move'),1)}。"
              f"關鍵不是是否超預期，而是<strong>毛利率是否見頂</strong>。"),
             ("2026-08-03", "選擇權到期（本報告採用鏈）", "中",
              f"最大痛點 {money(opt.get('max_pain'))}，較現價高 {pc((opt['max_pain']/price-1)*100,1,True)}。"
              f"賣權／買權未平倉比 {num(opt.get('pc_oi'))}。"),
             ("持續", "Form 4 內部人申報", "高",
              "目前 12 賣 0 買。任何內部人<strong>買進</strong>將反轉市場訊號維度的判讀。"),
             ("2026-11 中", "Q3 13F 申報", "中",
              "將揭露 Capital World（−27.8%）與 FMR（−19.1%）是否延續減碼，"
              "以及主動經理人的估值分歧是否收斂。"),
             ("持續", "三家寡占的擴產與定價公告", "極高",
              "任一家宣布大幅擴產或降價，即為「HBM 定價權」假設破裂的直接證據。")],
      "SKHY": lambda: [(e["date"], "Q2 2026 財報（今日）", "極高",
                f"共識營收 {e['rev_avg']/1e12:,.2f} 兆韓元（約 {money(e['rev_avg']/rate)}），"
                f"相對最近一季 +60.0%。未提供 EPS 共識。"
                f"選擇權隱含波動 {pc(opt.get('implied_move'),1)}——四檔中最高。"
                f"<strong>本報告所有數字將在數小時內過時。</strong>"),
               ("約 2026-09 中", "累積 50 個交易日", "高",
                "MA50、RSI(14)、ATR(14) 恢復可計算，篩選器動能維度的部分子因子恢復可用。"),
               ("2026-11 中", "首份 13F 申報", "高",
                "將首次揭露機構持股，填補目前完全缺失的法人訊號。"),
               ("不定", "20-F 或韓國交易所財報", "極高",
                "<strong>本報告最重要的催化劑，且與營運無關。</strong>"
                "確認幣別與換股比率後，所有估值需重算，信賴分數可由 47 大幅提升。"),
               ("約 2027-07", "累積 200 個交易日", "中",
                "MA200 與可靠 Beta 估計恢復可用，技術分析模組才算完整可執行。")],
      "MRVL": lambda: [(e["date"], "FY2027 Q2 財報", "極高",
                f"共識 non-GAAP EPS ${e['eps_avg']:,.3f}（區間 ${e['eps_lo']:,.2f}–${e['eps_hi']:,.2f}）、"
                f"營收 {money(e['rev_avg'])}（+11.8% QoQ）。"
                f"<strong>關鍵是 GAAP 營業利益率是否從 14.5% 向上突破</strong>，"
                f"而非 non-GAAP EPS 是否達標。"),
               ("2026-07-30", "股息發放日", "極低", "已宣告，金額象徵性（年化 $0.24）。"),
               ("每季（隨財報）", "商譽減損測試", "高",
                "商譽 $11.06B 占股東權益 77.3%。任何減損跡象都應觸發全面重估。"),
               ("持續", "客製化 ASIC 設計案公告", "極高",
                "取得或失去一個大型雲端業者的設計案，將改變三到五年的營收能見度。"
                "這是 MRVL 最大的單一價值驅動因子，且完全無法從財務數字預測。"),
               ("持續", "Form 4 內部人申報", "中",
                "目前 6 賣 0 買，賣價 $199–$299 全數高於現價。"),
               ("2026-11 中", "Q3 13F 申報", "中",
                "FMR 單一持股 15.0%（+3.5%）。若轉為減碼將造成顯著賣壓。")],
      "SNDL": lambda: [("2026-07-28（已發生）", "Q2 2026 財報", "已反映",
                f"營收 {money(236e6)} 落在共識區間下緣（{money(e['rev_lo'])}–{money(e['rev_hi'])}），"
                f"淨利 −$7.8M。股價當日 {pc(GAP[tk],2,True)}，創 52 週新低 {money(i['fiftyTwoWeekLow'])}。"),
               ("約 2026-11", "Q3 2026 財報", "極高",
                "<strong>本報告最重要的催化劑</strong>：檢驗「連續兩季營業利益為正」。"
                "Q2 為 −$5.4M。若 Q3 轉正且 Q4 延續，淨值侵蝕停止，"
                "0.30 倍股價淨值比立刻由陷阱轉為機會。"),
               ("每季", "股東權益餘額", "極高",
                "$1.064B（年化 −7.1%）。止穩＝折價論述成立；續降＝折價自行消失。"),
               ("持續（每日申報）", "公司股票買回", "高",
                "6 月間逐日買回，價位 $1.36–$1.43。需觀察年度買回金額是否由 $15.3M "
                "提升至超過年化淨值侵蝕速度（$75M）。"),
               ("不定", "加拿大大麻市場整併", "中",
                "供過於求結構若改善，毛利率 27.3% 有擴張空間，整個產業估值基準上移。"),
               ("不定", "併購或行動派股東介入", "中",
                f"市值 {money(i['marketCap'])}、淨值 {money(BS[tk]['equity'])}、淨現金 {money(abs(n['net_debt']))}。"
                f"資產折價對併購方或行動派股東足夠明顯。")],
    }[tk]()
    cat_tbl = V.simple_table(["時間", "事件", "預期影響", "說明"],
      [[a, f"<strong>{bb}</strong>",
        st("bad" if c in ("極高",) else ("warn" if c in ("高", "中") else "neut"), c), dd]
       for a, bb, c, dd in cats], align=["left", "left", "center", "left"])
    d.append(f"""<section id="cat"><h2>催化劑日曆<span class="skilltag">catalyst-calendar</span></h2>
<p>未來 90 天（{ASOF} 起）及其後的關鍵事件。
{f'下次財報 <strong>{e["date"]}</strong>（{e["dte"]} 天後）。' if e.get("dte") and e["dte"] > 0 else (f'財報日為 <strong>{e["date"]}</strong>（本報告資料截止當日）。' if e.get("dte") == 0 else f'最近財報 <strong>{e["date"]}</strong>（已公布）。')}</p>
<div class="tblwrap">{cat_tbl}</div>
</section>""")

    # ══════════════════════ monitoring ══════════════════════
    d.append(f"""<section id="monitor"><h2>監控計畫</h2>
<div class="tblwrap">{V.simple_table(["監控指標", "目前值", "為什麼重要／觸發條件"],
  [[f"<strong>{a}</strong>", bb, c] for a, bb, c in pr["monitor"]], align=["left","right","left"])}</div>
</section>""")

    # ══════════════════════ result-validator ══════════════════════
    vt = pr["valid"]
    tot = sum(x[1] for x in vt)
    tier = ("VERY HIGH", "good") if tot >= 85 else ("HIGH", "good") if tot >= 70 else \
           ("MEDIUM", "warn") if tot >= 55 else ("LOW", "bad") if tot >= 40 else ("VERY LOW", "bad")
    vtbl = V.simple_table(["稽核維度", "得分", "說明"],
      [[f"<strong>{a}</strong>", f"<strong>{s} / 20</strong>", desc] for a, s, desc in vt] +
      [["<strong>總信賴分數</strong>", f"<strong>{tot} / 100</strong>",
        f'信賴等級 <strong>{tier[0]}</strong>']], align=["left", "center", "left"])
    fl = pr["vflags"]
    d.append(f"""<section id="valid"><h2>結果稽核<span class="skilltag">result-validator</span></h2>
<div class="grid g2" style="margin-bottom:var(--s-16)">
<div>{V.figure(V.gauge(tot/10, width=290, height=178, caption=f"{tier[0]} · {tot}/100"),
   "綜合信賴分數")}</div>
<div class="card card--surface"><div class="card__h">信賴等級對照</div>
<p style="font-size:.875rem;color:var(--ink-2);line-height:2">
85–100 <strong>VERY HIGH</strong> — 可據以行動<br>
70–84 <strong>HIGH</strong> — 決策的良好基礎<br>
55–69 <strong>MEDIUM</strong> — 可用但有明顯缺口<br>
40–54 <strong>LOW</strong> — 結論僅具方向性參考<br>
0–39 <strong>VERY LOW</strong> — 不應據以行動</p>
<p style="font-size:.875rem;margin-top:10px"><strong>本報告：{tot}／100（{tier[0]}）</strong></p></div>
</div>
<div class="tblwrap">{vtbl}</div>
<div class="grid g3" style="margin-top:var(--s-24)">
<div class="card" style="background:#fff8ef;border-color:#ffd9a8"><div class="card__h">⚠ 警示（中度關切）</div>
<ul style="font-size:.875rem;margin:0">{"".join(f"<li>{x}</li>" for x in fl["warn"])}</ul></div>
<div class="card" style="background:#fdf0f0;border-color:#f7c4c4"><div class="card__h">🚩 紅旗（嚴重關切）</div>
<ul style="font-size:.875rem;margin:0">{"".join(f"<li>{x}</li>" for x in fl["bad"])}</ul></div>
<div class="card card--wash"><div class="card__h">✅ 優點</div>
<ul style="font-size:.875rem;margin:0">{"".join(f"<li>{x}</li>" for x in fl["good"])}</ul></div>
</div>
<h3>信賴度調整後的訊號</h3>
{sig_block([("Original", f"{pr['sig']['signal']}"), ("Orig Score", f"{comp['total']:.2f} / 10"), None,
            ("Confidence", f"{tier[0]}"), ("Conf Score", f"{tot} / 100"), None,
            ("Adjusted", pr['sig']['action']),
            ("Note", "signal WEAKENED by confidence" if tot < 70 else "signal STANDS")],
           title="VALIDATED INVESTMENT SIGNAL")}
</section>""")

    # ══════════════════════ signal ══════════════════════
    others = [x for x in T if x != tk]
    d.append(f"""<section id="signal"><h2>訊號區塊</h2>
{sig_block([("Signal", pr['sig']['signal']), ("Confidence", pr['sig']['conf']),
            ("Horizon", pr['sig']['hz']), ("Score", f"{comp['total']:.2f} / 10"), None,
            ("Action", pr['sig']['action']), ("Conviction", pr['sig']['conv'])])}
<p class="fignote">評分指引：8.0–10.0 強力偏多｜6.0–7.9 偏多｜4.0–5.9 中性｜2.0–3.9 偏空｜0.0–1.9 強力偏空。
信賴度：HIGH（資料充足、訊號清楚）｜MEDIUM（訊號混雜）｜LOW（資料有限或訊號矛盾）。</p>
<div class="disc" style="margin-top:var(--s-24)"><strong>本報告的定位</strong>
本報告為 InvestSkill 框架的能力展示，內容由大型語言模型依 yfinance 公開資料自動生成，
非投資建議。所有計算（Piotroski、ROIC／WACC、DCF、常態化盈餘、最大痛點、隱含波動率）
均以程式由同一份快照推導，可獨立重算；但估值假設（無風險利率、股權風險溢酬、
成長率、利益率情境{'、韓元匯率' if krw else ''}）皆為<strong>假設值</strong>，
不同假設會得出不同結論。任何決策前請查證第一手文件（SEC EDGAR、公司投資人關係網站）。</div>
<div class="chips" style="margin-top:var(--s-32)">
{"".join(f'<a class="btn btn--soft" href="{o.lower()}.html">{o} 報告 →</a>' for o in others)}
<a class="btn" href="screener.html">四檔對決 →</a>
<a class="btn btn--soft" href="index.html">← 回展示櫃</a>
</div></section>""")

    body = f'<div class="wrap shell">{toc(tocg)}<div class="doc">{"".join(d)}</div></div>'
    return page(f"{tk} {NAMES[tk][1]} — {pr['tagline']} | InvestSkill Autopilot 展示櫃",
                f"{tk}（{NAMES[tk][0]}）的 15 模組完整分析報告：{pr['tagline']}。"
                f"綜合評分 {comp['total']:.2f}／10，含 DCF、循環常態化估值、內部人交易、"
                f"空方紅隊與結果稽核。繁體中文。",
                "".join(b) + body, active=f"{tk.lower()}.html")
