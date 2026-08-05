"""Showcase hub — 戰情室."""
from context import *
import viz as V
from shell import page, IS

def build():
    b = []
    # ------------------------------------------------ hero
    tiles = ""
    for tk in T:
        i = RAW[tk]["info"]
        g = GAP[tk]
        tiles += f"""<div class="tile" style="background:rgba(255,255,255,.10);border-color:rgba(255,255,255,.28)">
<div class="tile__k" style="color:#9ce8bd">{tk} · {NAMES[tk][1]}</div>
<div class="tile__v" style="color:#fff">{countv(money(i['currentPrice']), i['currentPrice'], 2, "$")}</div>
<div class="tile__n" style="color:rgba(255,255,255,.82)">昨日 {arrow(g)} {pc(g,2,True)}　·　距 52 週高點 {pc(DD[tk],0)}</div></div>"""

    b.append(f"""<section class="rhero"><div class="wrap rhero__in">
<p class="crumb"><a href="../index.html">InvestSkill Autopilot</a> ／ 展示櫃</p>
<p class="eyebrow">Showcase · 全框架實戰</p>
<h1>記憶體超級循環的<br>第一道裂縫</h1>
<p class="rhero__sub">2026 年 7 月 28 日，四檔標的在<strong>同一個交易日</strong>全部重挫 7.8%–9.6%。
本展示櫃以 <strong>MU、SKHY、MRVL、SNDL</strong> 四檔為樣本，
把 InvestSkill 的 <strong>27 個分析框架</strong>與 Cookbook 的 <strong>7 條工作流（A–G）</strong>全部跑過一遍，
並刻意挑了一檔資料本身就有嚴重瑕疵的標的，示範框架如何<em>抓出自己的錯</em>。</p>
<div class="chips">
<span class="chip">27 個框架全覆蓋</span>
<span class="chip">工作流 A–G × 7</span>
<span class="chip">8 份報告頁</span>
<span class="chip">yfinance 即時快照 · {ASOF}</span>
<span class="chip">繁體中文輸出</span>
</div>
<div class="grid g4" style="margin-top:var(--s-32)">{tiles}</div>
</div></section>""")

    # ------------------------------------------------ the hook
    gap_rows = [(f"{tk} {NAMES[tk][1]}", GAP[tk], V.SERIES[tk], "") for tk in
                sorted(T, key=lambda t: GAP[t])]
    gap_svg = V.hbar_chart(gap_rows, fmt="{:.1f}%", vmin=-11, vmax=0, zero_line=True)
    gap_tbl = V.simple_table(
        ["標的", "前收盤", "現價", "單日變動", "距 52 週高點", "52 週高／低"],
        [[f"<strong>{tk}</strong> {NAMES[tk][1]}",
          money(RAW[tk]["info"]["previousClose"]), money(RAW[tk]["info"]["currentPrice"]),
          f'<span class="{cls(GAP[tk])}">{pc(GAP[tk],2,True)}</span>',
          f'<span class="dn">{pc(DD[tk],1)}</span>',
          f"{money(RAW[tk]['info']['fiftyTwoWeekHigh'])} / {money(RAW[tk]['info']['fiftyTwoWeekLow'])}"]
         for tk in T])

    b.append(f"""<section class="section section--wash"><div class="wrap">
<p class="eyebrow">起點：一個異常的交易日</p>
<h2>四檔、四種產業定位，同一天一起跌</h2>
<p class="lede" style="margin-top:var(--s-12);max-width:74ch">
三檔記憶體／AI 半導體加上一檔與 AI 毫無關聯的加拿大大麻零售商，
在 2026-07-28 同步下跌近 8%–10%。這種跨產業的同步性通常不是基本面事件，而是<strong>流動性事件</strong>——
它是本展示櫃所有分析的共同起點。</p>
{V.figure(gap_svg, "圖 1 ── 2026-07-28 單日跌幅（%）", gap_tbl,
  "資料：yfinance previousClose → currentPrice。SNDL 於 07-28 盤後公布財報，其跌幅含個別事件因素；另三檔則無公司特定消息。")}
<div class="grid g3" style="margin-top:var(--s-24)">
<div class="card card--surface"><div class="card__h">📉 費半指數 1 年 +{BENCH['^SOX']['ret_1y_pct']:.0f}%</div>
<p style="font-size:.9375rem;color:var(--ink-2)">同期 S&amp;P 500 僅 +{BENCH['^GSPC']['ret_1y_pct']:.1f}%。
半導體與大盤的報酬差距達 <strong>{BENCH['^SOX']['ret_1y_pct']-BENCH['^GSPC']['ret_1y_pct']:.0f} 個百分點</strong>，
是本輪循環的極端程度指標。</p></div>
<div class="card card--surface"><div class="card__h">🔺 MU 一年 +{RAW['MU']['hist_1y']['ret_pct']:.0f}%</div>
<p style="font-size:.9375rem;color:var(--ink-2)">但已從 {money(RAW['MU']['info']['fiftyTwoWeekHigh'])} 的高點回落
<strong>{abs(DD['MU']):.1f}%</strong>。營收仍在加速、股價卻先轉弱——本展示櫃的核心矛盾。</p></div>
<div class="card card--surface"><div class="card__h">🚩 內部人賣超 ${INS['MU']['sell_total']/1e6:.0f}M</div>
<p style="font-size:.9375rem;color:var(--ink-2)">MU 高管自 4 月起申報 {INS['MU']['n_sell']} 筆賣出、
<strong>0 筆買進</strong>，成交價區間 $421–$1,192，全數高於現價。</p></div>
</div></div></section>""")

    # ------------------------------------------------ the central question
    mu = CYC["MU"]
    peak15 = mu["scen"]["peak"]["m15"]
    price = RAW["MU"]["info"]["currentPrice"]
    b.append(f"""<section class="section"><div class="wrap">
<p class="eyebrow">本展示櫃的中心問題</p>
<h2>$820 是 5.3 倍前瞻本益比的便宜貨，<br>還是 16.6 倍歷史平均盈餘的循環頂點？</h2>
<div class="grid g2" style="margin-top:var(--s-32)">
<div class="card card--wash"><div class="card__h">🐂 多方：這是史上最便宜的大型股</div>
<ul style="font-size:.9375rem;margin:0">
<li>前瞻 EPS <strong>${RAW['MU']['info']['forwardEps']:.2f}</strong> → 前瞻本益比僅
<strong>{price/RAW['MU']['info']['forwardEps']:.2f} 倍</strong></li>
<li>最近一季營收 {money(23.860e9)} → {money(41.456e9)}，單季 <strong>+73.7%</strong></li>
<li>毛利率 84.6%、營業利益率 {mu['opm_now']*100:.1f}%，ROE {pcf(RAW['MU']['info']['returnOnEquity'])}</li>
<li>Piotroski F-Score <strong>9／9 滿分</strong>、淨現金 {money(abs(C['MU']['norm']['net_debt']))}</li>
<li>PEG {RAW['MU']['info']['trailingPegRatio']:.2f}、分析師平均目標價 {money(RAW['MU']['info']['targetMeanPrice'])}</li>
</ul></div>
<div class="card" style="background:#fdf0f0;border-color:#f7c4c4"><div class="card__h">🐻 空方：你正在為循環頂點付全價</div>
<ul style="font-size:.9375rem;margin:0">
<li>TTM 淨利 {money(mu['ttm_ni'])} 是過去四個會計年度平均值的
<strong>{mu['x_avg']:.1f} 倍</strong></li>
<li>四年區間內曾出現 <strong>-34.8% 的營業利益率</strong>（FY2023）</li>
<li>現價 {money(price)} ≈「{mu['opm_now']*100:.1f}% 峰值利益率<strong>永久維持</strong> × 15 倍」＝ {money(peak15)}</li>
<li>若利益率回到除谷底三年均值 {mu['opm_ex']*100:.1f}%，15 倍僅值 <strong>{money(mu['scen']['ex_trough']['m15'])}</strong></li>
<li>自由現金流僅 {money(RAW['MU']['info']['freeCashflow'])}——資本支出吃掉了絕大部分營運現金流</li>
</ul></div></div>
<div class="call call--warn"><div class="call__h">⚠ 這個巧合值得停下來看一眼</div>
<p>把 MU 目前 <strong>{mu['opm_now']*100:.1f}%</strong> 的營業利益率視為永久水準、套用 15 倍本益比，
得到的每股價值是 <strong>{money(peak15)}</strong>。今日收盤價是 <strong>{money(price)}</strong>——
兩者相差不到 {abs(price-peak15)/price*100:.1f}%。</p>
<p>市場此刻的定價，幾乎精準等於「記憶體產業永遠不再有下行循環」。這不是本展示櫃的結論，
而是它要用 15 個框架去逐一檢驗的<strong>假設</strong>。</p></div>
</div></section>""")

    # ------------------------------------------------ indexed price chart
    def monthly(tk):
        return RAW[tk]["hist_1y"].get("monthly") or []
    series = []
    for tk in ["MU", "MRVL", "SNDL"]:
        m = monthly(tk)
        if not m: continue
        base = m[0][1]
        series.append({"name": tk, "colour": V.SERIES[tk],
                       "points": [(d[5:7] + "月", round(v / base * 100, 1)) for d, v in m]})
    idx_svg = V.line_chart(series, y_label="指數（起點 = 100）", y_fmt="{:.0f}",
                           hlines=[(100, "起點 100", V.INK3)], height=360)
    idx_tbl = V.simple_table(
        ["標的", "1 年報酬", "3 個月", "6 個月", "年化波動", "最大回撤", "Beta"],
        [[f"<strong>{tk}</strong>",
          f'<span class="{cls(RAW[tk]["hist_1y"]["ret_pct"])}">{pc(RAW[tk]["hist_1y"]["ret_pct"],1,True)}</span>',
          pc(C[tk]["rel"].get("3M"), 1, True), pc(C[tk]["rel"].get("6M"), 1, True),
          pc(RAW[tk]["hist_1y"]["vol_ann_pct"], 1),
          f'<span class="dn">{pc(RAW[tk]["hist_1y"]["max_dd_pct"],1)}</span>',
          num(RAW[tk]["info"].get("beta"))]
         for tk in ["MU", "MRVL", "SNDL"]] +
        [["<strong>S&amp;P 500</strong>", f'<span class="up">{pc(BENCH["^GSPC"]["ret_1y_pct"],1,True)}</span>',
          "—", "—", "—", "—", "1.00"],
         ["<strong>費半 SOX</strong>", f'<span class="up">{pc(BENCH["^SOX"]["ret_1y_pct"],1,True)}</span>',
          "—", "—", "—", "—", "—"]])

    b.append(f"""<section class="section section--surface"><div class="wrap">
<p class="eyebrow">一年走勢</p>
<h2>同一個籃子，三種完全不同的故事</h2>
{V.legend([(f"{tk} {NAMES[tk][1]}", V.SERIES[tk]) for tk in ["MU","MRVL","SNDL"]])}
{V.figure(idx_svg, "圖 2 ── 一年股價指數化走勢（2025-07-29 = 100，月底收盤）", idx_tbl,
  "SKHY 未列入：其 ADR 於 2026-07-10 才開始交易，僅 13 個交易日，無法計算可比的年度報酬——這項資料缺口本身是 SKHY 報告的主軸。")}
<div class="grid g2">
<div class="card"><div class="card__h">MU：+{RAW['MU']['hist_1y']['ret_pct']:.0f}% 之後的 -{abs(DD['MU']):.0f}%</div>
<p style="font-size:.9375rem;color:var(--ink-2)">一年內從 {money(RAW['MU']['hist_1y']['low'])} 漲到
{money(RAW['MU']['hist_1y']['high'])}，再回落至 {money(price)}。
獲利仍在加速，但 RSI(14) 已降至 {RAW['MU']['hist_1y']['rsi14']:.1f}、跌破 MA20 與 MA50。
<strong>價格轉折領先了基本面轉折</strong>——或者是市場錯了。</p></div>
<div class="card"><div class="card__h">MRVL：AI 敘事最強，股東報酬最差</div>
<p style="font-size:.9375rem;color:var(--ink-2)">一年 +{RAW['MRVL']['hist_1y']['ret_pct']:.0f}% 但距高點 -{abs(DD['MRVL']):.0f}%，
是四檔中回撤最深的 AI 標的。營收連五季創高、GAAP 淨利卻在最新一季塌到
{money(3.45e7)}。這個落差是 MRVL 報告的核心。</p></div>
</div></div></section>""")

    # ------------------------------------------------ scatter
    pts = []
    for tk in T:
        i = RAW[tk]["info"]
        fpe = i["currentPrice"] / i["forwardEps"] if i.get("forwardEps") else None
        rg = (i.get("revenueGrowth") or 0) * 100
        if fpe is None: continue
        pts.append({"name": tk, "colour": V.SERIES[tk], "x": fpe, "y": rg,
                    "note": f"前瞻P/E {fpe:.1f}x · 營收YoY {rg:.0f}%"})
    sc = V.scatter_chart(pts, x_label="前瞻本益比（倍，對數軸）", y_label="營收年增率（%）",
                         x_fmt="{:.0f}x", y_fmt="{:.0f}%", log_x=True, x_ref=20.0, y_ref=0,
                         quad_labels=[(.02,.10,"← 便宜且高成長",  "start"),
                                      (.98,.10,"貴且高成長 →",   "end"),
                                      (.02,.96,"便宜但零成長",   "start")])
    sc_tbl = V.simple_table(
        ["標的", "現價", "前瞻 EPS", "前瞻 P/E", "TTM P/E", "營收 YoY", "P/S（校正後）", "EV/EBITDA（校正後）"],
        [[f"<strong>{tk}</strong>", money(RAW[tk]["info"]["currentPrice"]),
          num(RAW[tk]["info"].get("forwardEps")),
          num(RAW[tk]["info"]["currentPrice"]/RAW[tk]["info"]["forwardEps"]) + "x" if RAW[tk]["info"].get("forwardEps") else "—",
          num(RAW[tk]["info"].get("trailingPE")) + "x" if RAW[tk]["info"].get("trailingPE") else "n/a（虧損）",
          pcf(RAW[tk]["info"].get("revenueGrowth"), 1, True),
          num(C[tk]["norm"]["ps"]) + "x", num(C[tk]["norm"]["ev_ebitda"]) + "x"]
         for tk in T])

    b.append(f"""<section class="section"><div class="wrap">
<p class="eyebrow">橫斷面定位</p>
<h2>估值 vs 成長：四檔散落在四個象限</h2>
{V.figure(sc, "圖 3 ── 前瞻本益比 vs 營收年增率（圓點面積無編碼意義）", sc_tbl,
  "P/S 與 EV/EBITDA 均為單位校正後數值：SKHY 的財報以韓元計、股價以美元計，直接取用會得出 P/S 0.007 與負值企業價值。校正匯率 1 USD = 1,380 KRW。")}
<div class="call"><div class="call__h">💡 這張圖為什麼需要對數軸</div>
<p>四檔的前瞻本益比從 <strong>{min(p['x'] for p in pts):.1f} 倍</strong>（SKHY）到
<strong>{max(p['x'] for p in pts):.1f} 倍</strong>（SNDL）橫跨一個數量級。線性軸會把三檔半導體壓成一團。
同時也提醒：SKHY 的 3.2 倍與 SNDL 的 40.7 倍<strong>都不可信</strong>——
前者來自貨幣單位混用，後者來自接近零的獲利基數。兩者都在各自報告裡被 <code>result-validator</code> 標記。</p></div>
</div></section>""")

    # ------------------------------------------------ screener preview
    rank = sorted(T, key=lambda t: -C[t]["screener"]["total"])
    lead = ""
    for n, tk in enumerate(rank, 1):
        s = C[tk]["screener"]
        k, lbl = screener_signal(s["total"])
        unscored = "<em style=\"color:#767c85;font-size:.75rem\">未評分</em>"
        dims = "".join(
            f'<td style="text-align:center">'
            f'{num(s["dims"][d], 1) if s["dims"][d] is not None else unscored}</td>'
            for d in ["價值", "品質", "動能", "情緒", "成長"])
        lead += (f'<tr><th scope="row">{n}</th>'
                 f'<td style="text-align:left"><strong>{tk}</strong> <span style="color:var(--ink-3)">{NAMES[tk][1]}</span></td>'
                 f'{dims}<td style="text-align:center"><strong>{s["total"]:.1f}</strong></td>'
                 f'<td style="text-align:center">{st(k, lbl.split(" ",1)[1])}</td></tr>')
    avg = sum(C[t]["screener"]["total"] for t in T) / len(T)

    b.append(f"""<section class="section section--wash"><div class="wrap">
<p class="eyebrow">框架 1／27 · <code>stock-screener</code></p>
<h2>五維度排行榜</h2>
<p class="lede" style="margin-top:var(--s-12)">
每檔標的在<strong>價值、品質、動能、情緒、成長</strong>五個維度各自由 4–6 個子因子評分（0–10），
加權（品質 25%、價值／動能／成長各 20%、情緒 15%）得出總分。
下表為摘要，完整的 22 個子因子計算過程見<a href="screener.html">四檔對決全文</a>。</p>
<div class="tblwrap"><table class="dt">
<thead><tr><th>#</th><th style="text-align:left">標的</th>
<th style="text-align:center">價值</th><th style="text-align:center">品質</th>
<th style="text-align:center">動能</th><th style="text-align:center">情緒</th>
<th style="text-align:center">成長</th><th style="text-align:center">總分</th>
<th style="text-align:center">訊號</th></tr></thead>
<tbody>{lead}</tbody></table></div>
<p class="fignote">篩選universe平均分 {avg:.2f}／10 → 市場偏向：{"偏多 BULLISH" if avg>=6 else ("中性 NEUTRAL" if avg>=4 else "偏空 BEARISH")}。
SKHY 的動能維度因上市僅 13 個交易日而<strong>無法評分</strong>，依框架規定標示為「未評分」而非以 5.0 中性值填補——
這會使其總分的可信度低於其他三檔，並已反映在 <code>result-validator</code> 的信賴分數中。</p>
<p style="margin-top:var(--s-24)"><a class="btn" href="screener.html">看完整篩選推導 →</a></p>
</div></section>""")

    # ------------------------------------------------ report index
    cards = ""
    meta = {
        "MU": ("旗艦報告 · 15 模組", "循環頂點的估值數學", "good"),
        "SKHY": ("資料完整性稽核", "當框架抓出自己的錯", "bad"),
        "MRVL": ("盈餘品質解剖", "GAAP 與 non-GAAP 的鴻溝", "warn"),
        "SNDL": ("價值陷阱解剖", "0.30 倍淨值，但淨值在融化", "warn"),
    }
    for tk in T:
        c = C[tk]["composite"]
        k, lbl = interp(c["total"])
        tag, sub, _ = meta[tk]
        cards += f"""<a class="card" href="{tk.lower()}.html" style="text-decoration:none;color:inherit;display:block">
<div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px">
<div><div class="tile__k" style="color:{V.SERIES[tk]}">{tag}</div>
<div style="font-family:var(--display);font-weight:800;font-size:1.25rem;margin-top:2px">{tk} · {NAMES[tk][1]}</div>
<div style="font-size:.875rem;color:var(--ink-2);margin-top:4px">{sub}</div></div>
<div style="text-align:right;flex:0 0 auto">
<div style="font-family:var(--display);font-weight:800;font-size:1.75rem;line-height:1">{countv(f"{c['total']:.2f}", c['total'], 2)}</div>
<div style="font-size:.6875rem;color:var(--ink-3)">綜合評分／10</div></div></div>
<div style="margin-top:12px;display:flex;gap:8px;flex-wrap:wrap">{st(k, lbl.split(' ')[0])}
<span class="skilltag" style="margin-left:0">15 模組</span>
<span class="skilltag" style="margin-left:0">{money(RAW[tk]['info']['currentPrice'])}</span></div></a>"""

    b.append(f"""<section class="section"><div class="wrap">
<p class="eyebrow">八份報告</p>
<h2>展示櫃內容</h2>
<div class="grid g2" style="margin-top:var(--s-24)">{cards}</div>
<div class="grid g3" style="margin-top:var(--s-16)">
<a class="card card--surface" href="screener.html" style="text-decoration:none;color:inherit">
<div class="card__h">📊 四檔對決 <code>stock-screener</code></div>
<p style="font-size:.875rem;color:var(--ink-2)">22 個子因子的完整推導、五維度雷達圖、
前三名深潛與後三名避開清單，加上 <code>sector-analysis</code> 與 <code>economics-analysis</code> 的總體背景。</p></a>
<a class="card card--surface" href="workflows.html" style="text-decoration:none;color:inherit">
<div class="card__h">🔗 工作流 A–G <code>cookbook</code></div>
<p style="font-size:.875rem;color:var(--ink-2)">Cookbook 的七條工作流，每一條都用本籃子的真實標的跑一遍：
財報前定位、價值陷阱檢定、股息組合、波段做多、完整投資備忘錄、產業輪動、加碼階梯。</p></a>
<a class="card card--surface" href="supply-chain.html" style="text-decoration:none;color:inherit">
<div class="card__h">🗺 產業鏈地圖 <code>industry-map</code></div>
<p style="font-size:.875rem;color:var(--ink-2)">從矽晶圓到終端推論負載，把 HBM 價值鏈畫成有向圖，
標出瓶頸層、利潤池位置，並推導出四個二階投資標的。</p></a>
</div></div></section>""")

    # ------------------------------------------------ framework coverage
    COV = {
        "stock-screener": ["screener"], "sector-analysis": ["screener"],
        "economics-analysis": ["screener", "MU", "MRVL"],
        "stock-eval": ["MU", "SKHY", "MRVL", "SNDL", "workflows"],
        "technical-analysis": ["MU", "SKHY", "MRVL", "SNDL", "workflows"],
        "dcf-valuation": ["MU", "SKHY", "MRVL", "SNDL", "workflows"],
        "stock-valuation": ["MU", "SKHY", "MRVL", "SNDL"],
        "fundamental-analysis": ["MU", "SKHY", "MRVL", "SNDL"],
        "financial-report-analyst": ["MU", "MRVL", "SNDL", "workflows"],
        "insider-trading": ["MU", "MRVL", "SNDL", "workflows"],
        "institutional-ownership": ["MU", "MRVL", "SNDL"],
        "short-interest": ["MU", "MRVL", "SNDL", "workflows"],
        "options-analysis": ["MU", "SKHY", "MRVL", "SNDL", "workflows"],
        "earnings-call-analysis": ["MU", "MRVL", "workflows"],
        "competitor-analysis": ["MU", "SKHY", "MRVL", "SNDL", "workflows"],
        "dividend-analysis": ["MU", "MRVL", "SNDL", "workflows"],
        "bear-case": ["MU", "SKHY", "MRVL", "SNDL", "workflows"],
        "result-validator": ["MU", "SKHY", "MRVL", "SNDL", "screener", "workflows"],
        "industry-map": ["supply-chain"], "chart-master": ["ALL"],
        "catalyst-calendar": ["MU", "SKHY", "MRVL", "SNDL", "workflows"],
        "position-ladder": ["MU", "workflows"],
        "portfolio-review": ["workflows"], "full-report": ["MU", "SKHY", "MRVL", "SNDL"],
        "10k-digest": ["MRVL"], "report-generator": ["ALL"],
        "research-bundle": ["—"],
    }
    LINKS = {"screener": "screener.html", "workflows": "workflows.html",
             "supply-chain": "supply-chain.html", "MU": "mu.html", "SKHY": "skhy.html",
             "MRVL": "mrvl.html", "SNDL": "sndl.html"}
    rows = ""
    for n, (sk, where) in enumerate(sorted(COV.items()), 1):
        if where == ["—"]:
            w = '<span style="color:var(--ink-3)">已棄用（由 full-report 取代）</span>'
        elif where == ["ALL"]:
            w = '<span style="color:var(--ink-2)">全部 8 頁（圖表與 HTML 產出層）</span>'
        else:
            w = "　".join(f'<a href="{LINKS[x]}">{x if x in ("MU","SKHY","MRVL","SNDL") else {"screener":"四檔對決","workflows":"工作流","supply-chain":"產業鏈"}[x]}</a>' for x in where)
        rows += f'<tr><td style="text-align:right;color:var(--ink-3)">{n}</td><th scope="row" style="text-align:left"><code>{sk}</code></th><td style="text-align:left">{w}</td></tr>'

    b.append(f"""<section class="section section--surface"><div class="wrap">
<p class="eyebrow">覆蓋率</p>
<h2>27 個框架，逐一落點</h2>
<p class="lede" style="margin-top:var(--s-12);max-width:70ch">下表對照 InvestSkill v1.11.0 的
<a href="{IS}/tree/main/plugins/us-stock-analysis/skills">27 個 <code>SKILL.md</code></a>
與本展示櫃的實際使用位置。<code>research-bundle</code> 已被官方標記為棄用，故未使用。</p>
<div class="tblwrap"><table class="dt dt--sm">
<thead><tr><th style="text-align:right;width:44px">#</th><th style="text-align:left">框架</th>
<th style="text-align:left">出現於</th></tr></thead><tbody>{rows}</tbody></table></div>
</div></section>""")

    # ------------------------------------------------ how (pipeline diagrams)
    pipe = V.pipeline_chart(
        [{"n": 1, "title": "單次資料快照", "kind": "data",
          "sub": "yfinance 一次擷取：即時報價、四年三大表、五季季報、13F、Form 4、選擇權鏈",
          "meta": "1 次 fetch · 四檔共用"},
         {"n": 2, "title": "框架依相依序執行",
          "sub": "27 個框架分五階段推進，前階段產出即後階段輸入（Beta → WACC → DCF）",
          "meta": "5 階段 · 15 模組"},
         {"n": 3, "title": "數值全部重算",
          "sub": "Piotroski、ROIC／WACC、22 個子因子、三情境 DCF、最大痛點皆由快照計算",
          "meta": "0 個模型自行宣稱的數字"},
         {"n": 4, "title": "交付前稽核", "kind": "audit",
          "sub": "result-validator 打五維度共 100 分的信賴分數，不足者降級或拒絕出結論",
          "meta": "SKHY 47／100 → LOW"}],
        aria="分析管線四步：單次資料快照 → 框架依相依序執行 → 數值全部重算 → 交付前稽核")
    mucomp = C["MU"]["composite"]
    ladder = V.phase_chart(
        [{"label": f"階段{n} · {PHASE_LABEL[k]}", "score": mucomp["phases"][k],
          "modules": PHASE_MODULES[k]}
         for n, k in zip("一二三四五", PHASE_ORDER)],
        head=f"yfinance 單次快照 · {ASOF} · 所有模組共用同一組數字",
        foot=f"綜合評分 {mucomp['total']:.2f}／10 → result-validator 信賴稽核（訊號一致性 6／20）",
        aria="full-report 的五階段相依階梯：單一共用快照向下餵入五個依序執行的階段，"
             "共 15 個模組，收斂為一個經稽核的結論")

    b.append(f"""<section class="section"><div class="wrap">
<p class="eyebrow">方法論</p>
<h2>這些報告是怎麼產生的</h2>
{V.figure(pipe, "圖 4 ── 報告生成管線（每一步的產出都是下一步的唯一輸入）", None,
  "四個步驟都在 GitHub Actions 內完成，無人工介入。步驟 3 的所有計算由 "
  "<code>scripts/showcase/derive.py</code> 執行，可獨立重跑驗證。",
  extra_cls="dagfig")}
{V.figure(ladder, "圖 5 ── <code>full-report --depth comprehensive</code> 的五階段相依階梯（數字為 MU 報告的階段子分數）",
  V.simple_table(["階段", "模組數", "子分數", "權重", "加權貢獻"],
    [[f"階段{n} · {PHASE_LABEL[k]}", str(len(PHASE_MODULES[k])),
      f'{mucomp["phases"][k]:.1f}', f'{mucomp["weights"][k]:.0%}',
      f'{mucomp["weighted"][k]:.2f}'] for n, k in zip("一二三四五", PHASE_ORDER)] +
    [["<strong>合計</strong>", "<strong>15</strong>", "—", "100%",
      f'<strong>{mucomp["total"]:.2f}</strong>']],
    align=["left", "center", "right", "right", "right"]),
  "階段之間是<strong>相依</strong>而非平行：階段一的 Beta 與資本結構決定階段二的 WACC，"
  "階段二的內在價值決定階段四的進場區間。因此模組不能任意重排，"
  "也不能只跑其中一段就宣稱得到綜合結論。",
  extra_cls="dagfig")}
<div class="grid g4" style="margin-top:var(--s-24)">
<div class="card"><div class="tile__k">步驟 1</div><div class="card__h" style="margin-top:4px">單次資料快照</div>
<p style="font-size:.875rem;color:var(--ink-2)">每檔標的取一份 yfinance 快照：即時報價、四年損益表／現金流量表／資產負債表、
五季季報、13F 前 15 大持股、Form 4 內部人交易、選擇權鏈、分析師預估。<strong>所有框架共用同一份快照</strong>，
避免同一份報告內出現不同時點的價格。</p></div>
<div class="card"><div class="tile__k">步驟 2</div><div class="card__h" style="margin-top:4px">框架依相依序執行</div>
<p style="font-size:.875rem;color:var(--ink-2)">依 <code>full-report</code> 定義的五個階段推進：
商業品質 → 估值 → 市場訊號 → 技術時機 → 風險。前階段的產出成為後階段的輸入
（例如 WACC 由 Beta 推導後才進 DCF）。</p></div>
<div class="card"><div class="tile__k">步驟 3</div><div class="card__h" style="margin-top:4px">數值全部可重算</div>
<p style="font-size:.875rem;color:var(--ink-2)">Piotroski 九項檢定、ROIC／WACC、五維度 22 個子因子、
三情境 DCF、最大痛點、隱含波動率——全部由快照以程式計算，
每個數字在頁面上都附推導過程或原始輸入，而非由模型自行宣稱。</p></div>
<div class="card"><div class="tile__k">步驟 4</div><div class="card__h" style="margin-top:4px">交付前稽核</div>
<p style="font-size:.875rem;color:var(--ink-2)"><code>result-validator</code> 對每份綜合結論打
五維度、共 100 分的信賴分數。SKHY 因貨幣混用與上市歷史不足被降至
<strong>{47}／100（LOW）</strong>，並在頁面頂端明確警示。</p></div>
</div>
<div class="call call--bad" style="margin-top:var(--s-32)"><div class="call__h">🚩 刻意保留的三個資料瑕疵</div>
<p>本展示櫃<strong>沒有</strong>把有問題的資料清乾淨再呈現，因為那會讓 <code>result-validator</code> 無事可做。以下瑕疵被原樣保留並標示：</p>
<ul>
<li><strong>SKHY 貨幣單位混用</strong>──財報韓元、股價美元，導致原始企業價值為
<span class="dn">−{abs(RAW['SKHY']['info']['enterpriseValue'])/1e12:,.1f} 兆</span>、P/S 為 0.007。</li>
<li><strong>SKHY 上市歷史僅 13 個交易日</strong>──MA50／MA200／RSI／ATR 全部無法計算，動能維度只能標示未評分。</li>
<li><strong>MRVL 前瞻 EPS 與 TTM EPS 基準不一致</strong>──前瞻值幾可確定為 non-GAAP，
與 GAAP 的 TTM EPS ${RAW['MRVL']['info']['trailingEps']:.2f} 相除會得出失真的成長率。</li>
</ul></div>
</div></section>""")

    b.append("""<section class="band"><div class="wrap" style="text-align:center">
<h2 style="color:#fff">從這裡開始</h2>
<p style="margin-top:var(--s-12);color:rgba(255,255,255,.9);max-width:60ch;margin-inline:auto">
建議路徑：先看<a href="screener.html">四檔對決</a>建立橫斷面認識，
再進<a href="mu.html">MU 旗艦報告</a>看 15 模組如何收斂成一個結論，
最後用<a href="skhy.html">SKHY</a>檢視框架如何否證自己。</p>
<div class="chips" style="justify-content:center;margin-top:var(--s-32)">
<a class="btn btn--onband" href="screener.html">四檔對決</a>
<a class="btn btn--ghost" href="mu.html">MU 旗艦報告</a>
<a class="btn btn--ghost" href="workflows.html">工作流 A–G</a>
</div></div></section>""")

    return page("展示櫃 — 記憶體超級循環壓力測試 | InvestSkill Autopilot",
                "以 MU、SKHY、MRVL、SNDL 四檔標的，把 InvestSkill 的 27 個分析框架與 7 條工作流全部實跑一遍的繁體中文展示報告。",
                "".join(b), active="index.html")
