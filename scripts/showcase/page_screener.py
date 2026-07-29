"""四檔對決 — stock-screener + sector-analysis + economics-analysis + result-validator."""
from context import *
import viz as V
from shell import page, toc

DIMS = ["價值", "品質", "動能", "情緒", "成長"]

def build():
    b = []
    rank = sorted(T, key=lambda t: -C[t]["screener"]["total"])
    avg = sum(C[t]["screener"]["total"] for t in T) / len(T)

    b.append(f"""<section class="rhero"><div class="wrap rhero__in">
<p class="crumb"><a href="../index.html">InvestSkill Autopilot</a> ／ <a href="index.html">展示櫃</a> ／ 四檔對決</p>
<p class="eyebrow">framework · stock-screener</p>
<h1>四檔對決：22 個子因子<br>的完整推導</h1>
<p class="rhero__sub">同一份資料快照、同一套評分規則，套在四檔產業定位完全不同的標的上。
本頁把 <code style="background:rgba(255,255,255,.16);border-color:rgba(255,255,255,.3);color:#fff">stock-screener</code>
的每一個子因子攤開，讓每個分數都能被反推、被質疑。</p>
<div class="chips">
<span class="chip">5 維度 · 22 子因子</span>
<span class="chip">首選 {rank[0]} · {C[rank[0]]['screener']['total']:.1f}／10</span>
<span class="chip">universe 均分 {avg:.2f}</span>
<span class="chip">{ASOF}</span>
</div></div></section>""")

    tocg = [(None, [("src", "資料來源"), ("board", "排行榜"), ("radar", "五維度雷達"),
                    ("subs", "22 個子因子拆解")]),
            ("維度細節", [("d-val", "價值"), ("d-qual", "品質"), ("d-mom", "動能"),
                          ("d-sent", "情緒"), ("d-grow", "成長")]),
            ("延伸", [("deep", "前三名深潛"), ("avoid", "避開清單"), ("sector", "類股輪動"),
                      ("macro", "總體環境"), ("notes", "篩選註記"), ("valid", "結果稽核"),
                      ("signal", "訊號區塊")])]

    d = []
    # ---------------------------------------------------------------- sources
    d.append(f"""<section id="src"><h2>資料來源</h2>
{prov("yfinance（Yahoo Finance）即時快照：報價、四年年報、五季季報、13F 前 15 大持股、Form 4、選擇權鏈、分析師預估；"
      "基準指數 ^GSPC／^SOX／SMH。類股中位數本益比採 32.0 倍（2026-07 半導體類股）。",
      "程式化擷取（yfinance 1.5.2），單次快照，四檔共用",
      "<strong>MEDIUM</strong> — 三檔資料完整；SKHY 因上市歷史僅 13 個交易日且財報幣別與報價幣別不一致，個別維度不可用",
      f'<p style="font-size:.8125rem;margin-top:10px;color:var(--ink-2)">'
      f'<strong>單位校正</strong>：SKHY 財報以韓元揭露、ADR 以美元報價。本頁所有 SKHY 的絕對金額與比率'
      f'均已按 1 USD = {KRW:,.0f} KRW 換算後計算，並在數值旁標示「校正後」。'
      f'未校正的原始欄位（P/S 0.007、企業價值 −{abs(RAW["SKHY"]["info"]["enterpriseValue"])/1e12:,.1f} 兆）'
      f'一律不採用，理由見 <a href="skhy.html#valid">SKHY 稽核報告</a>。</p>')}
</section>""")

    # ---------------------------------------------------------------- board
    rows = ""
    for n, tk in enumerate(rank, 1):
        s = C[tk]["screener"]
        k, lbl = screener_signal(s["total"])
        cells = ""
        for dm in DIMS:
            v = s["dims"][dm]
            cells += (f'<td style="text-align:center;font-weight:700">{v:.1f}</td>' if v is not None
                      else '<td style="text-align:center;color:var(--ink-3);font-size:.75rem;font-style:italic">未評分</td>')
        rows += (f'<tr><th scope="row" style="text-align:center">{n}</th>'
                 f'<td style="text-align:left"><a href="{tk.lower()}.html"><strong>{tk}</strong></a> '
                 f'<span style="color:var(--ink-3)">{NAMES[tk][1]}</span></td>{cells}'
                 f'<td style="text-align:center;font-size:1.05rem"><strong>{s["total"]:.1f}</strong></td>'
                 f'<td style="text-align:center">{st(k, lbl.split(" ",1)[1])}</td></tr>')

    wtable = V.simple_table(["維度", "權重", "理由"],
        [["價值", "20%", "與動能、成長同權：便宜本身不是理由，但仍是報酬的重要來源"],
         ["品質", "25%", "最高權重——五個因子中最持久，也最不容易被短期價格反轉推翻"],
         ["動能", "20%", "與價值同權，作為進場時機的客觀輸入"],
         ["情緒", "15%", "折價處理：內部人與法人訊號雜訊最大，且常有申報時滯"],
         ["成長", "20%", "與價值同權；循環股需搭配品質維度共同解讀，避免把峰值成長當常態"]],
        align=["left", "center", "left"])

    b_rows = ""
    for tk in rank:
        s = C[tk]["screener"]
        parts = []
        for dm in DIMS:
            v = s["dims"][dm]
            parts.append(f'{dm} {v:.1f}×{s["weights"][dm]:.0%}={v*s["weights"][dm]:.2f}' if v is not None
                         else f'{dm} 未評分→中性 5.0×{s["weights"][dm]:.0%}={5.0*s["weights"][dm]:.2f}')
        b_rows += (f'<tr><th scope="row">{tk}</th><td style="text-align:left;font-family:var(--mono);'
                   f'font-size:.75rem;line-height:1.9">{" ＋ ".join(parts)}</td>'
                   f'<td style="text-align:center"><strong>{s["total"]:.1f}</strong></td></tr>')

    d.append(f"""<section id="board"><h2><span class="modnum">1</span>排行榜<span class="skilltag">stock-screener</span></h2>
<p>總分 ＝ 價值×0.20 ＋ 品質×0.25 ＋ 動能×0.20 ＋ 情緒×0.15 ＋ 成長×0.20。</p>
<div class="tblwrap"><table class="dt">
<caption>訊號門檻：≥7.5 強力買進　·　6.0–7.4 買進　·　4.5–5.9 持有　·　3.0–4.4 避開　·　&lt;3.0 強力避開</caption>
<thead><tr><th style="text-align:center;width:40px">#</th><th style="text-align:left">標的</th>
{''.join(f'<th style="text-align:center">{dm}</th>' for dm in DIMS)}
<th style="text-align:center">總分</th><th style="text-align:center">訊號</th></tr></thead>
<tbody>{rows}</tbody></table></div>

<h3>加權算式逐檔展開</h3>
<div class="tblwrap"><table class="dt dt--sm"><thead><tr><th>標的</th>
<th style="text-align:left">計算</th><th style="text-align:center">總分</th></tr></thead>
<tbody>{b_rows}</tbody></table></div>
<p class="fignote">SKHY 的動能維度依框架規定以中性 5.0 代入並標示「未評分」。若改以其餘四維度重新加權
（權重歸一化至 100%），SKHY 總分會升至 <strong>{(8.2*0.20+9.4*0.25+8.8*0.15+10.0*0.20)/0.80:.1f}</strong>——
換言之，這個「未評分」處理讓 SKHY 的分數被<strong>低估</strong>了約
{(8.2*0.20+9.4*0.25+8.8*0.15+10.0*0.20)/0.80 - C['SKHY']['screener']['total']:.1f} 分。
框架選擇保守處理而非樂觀外推，這個取捨必須明示。</p>

<h3>權重設計</h3>
<div class="tblwrap">{wtable}</div>
</section>""")

    # ---------------------------------------------------------------- radar
    radars = ""
    for tk in rank:
        s = C[tk]["screener"]
        vals = [s["dims"][dm] for dm in DIMS]
        r = V.radar_chart(DIMS, [{"name": tk, "colour": V.SERIES[tk], "values": vals}], size=330)
        miss = [dm for dm in DIMS if s["dims"][dm] is None]
        note = f'<p class="fignote">未評分維度：{"、".join(miss)}（繪為 0，非真實得分）</p>' if miss else ""
        radars += (f'<div><div class="figbox">{r}</div>'
                   f'<figcaption style="text-align:center">{tk} · {NAMES[tk][1]} — 總分 {s["total"]:.1f}</figcaption>{note}</div>')

    heat = V.heat_table(DIMS + ["總分"],
                        [(f"{tk} {NAMES[tk][1]}", [C[tk]["screener"]["dims"][dm] for dm in DIMS] +
                          [C[tk]["screener"]["total"]]) for tk in rank],
                        first_col="標的")
    d.append(f"""<section id="radar"><h2><span class="modnum">2</span>五維度雷達</h2>
<div class="grid g2" style="margin-top:var(--s-24)">{radars}</div>
<h3>維度熱圖</h3>
<p>單一色階（品牌綠，淺→深）代表數值大小；深色＝高分。</p>
<div class="tblwrap">{heat}</div>
<div class="call"><div class="call__h">💡 雷達圖讀出的一件事</div>
<p>MU 與 SKHY 的形狀幾乎相同——高品質、高成長、估值不貴，但動能破損。
MRVL 的形狀相反：情緒面最強（分析師與法人最捧場），但價值維度只有
{C['MRVL']['screener']['dims']['價值']:.1f} 分，是四檔最低。
SNDL 則是唯一一檔成長維度掛零、卻靠價值與品質撐住總分的標的——
這正是<strong>價值陷阱</strong>在五維度模型裡的典型指紋。</p></div>
</section>""")

    # ---------------------------------------------------------------- sub-factors
    SUBEXP = {
      "P/E vs 類股中位數": "P/E ÷ 32.0（半導體類股中位數）。<50% → 10 分；>200% → 0 分，線性內插。",
      "P/S": "市值 ÷ TTM 營收。<1 → 10 分；>20 → 0 分。",
      "EV/EBITDA": "（市值＋淨負債）÷ TTM EBITDA。<8x → 10 分；>40x → 0 分。",
      "PEG": "TTM PEG。<0.75 → 10 分；>3.0 → 0 分；獲利為負時排除。",
      "Piotroski F-Score": "九項會計檢定得分 × (10/9)，上限 10。",
      "ROIC − WACC 價差": "ROIC ＝ EBIT×(1−稅率) ÷ 投入資本；WACC 由 CAPM 推導。價差 ≥+10pp → 10 分；持平 → 5 分；≤−10pp → 0 分。",
      "毛利率三年趨勢": "近三個會計年度毛利率的年均變動。≥+3pp/年 → 10 分；持平 → 5 分；≤−3pp/年 → 0 分。",
      "負債權益比": "D/E。<0.2 → 10 分；>3.0 → 0 分。",
      "股價 vs MA50": "高於 MA50 達 10% → 10 分；等於 MA50 → 5 分；低於 10% → 0 分。",
      "股價 vs MA200": "高於 MA200 達 20% → 10 分；等於 → 5 分；低於 20% → 0 分。",
      "RSI(14)": "55–70 → 10 分（強勢但未超買）；50 → 5 分；<30 或 >80 → 0 分。",
      "3M 相對 S&P500": "相對大盤（同期間縮放）超額 ≥+10pp → 10 分；≤−10pp → 0 分。",
      "6M 相對 S&P500": "同 3M 尺規。",
      "12M 相對 S&P500": "同 3M 尺規。",
      "空單月變化": "空單張數月變動。下降 ≥20%（回補）→ 10 分；上升 ≥20% → 0 分。",
      "法人持股水準": "機構持股比重。20% → 0 分；90% → 10 分（作為機構認可度的替代指標）。",
      "分析師共識": "recommendationKey 映射：strong_buy 9.0／buy 7.5／hold 5.0／sell 1.0；none 排除。",
      "目標價隱含上檔": "分析師平均目標價相對現價的隱含漲幅。−20% → 0 分；+60% → 10 分。",
      "營收 YoY": "≥30% → 10 分；10% → 5 分；≤0% → 0 分。",
      "EPS YoY": "≥40% → 10 分；15% → 5 分；≤0% → 0 分；基數為負時排除。",
      "前瞻 EPS vs TTM": "前瞻 EPS ÷ TTM EPS − 1。≥40% → 10 分。",
    }
    ANCHOR = {"價值": "d-val", "品質": "d-qual", "動能": "d-mom", "情緒": "d-sent", "成長": "d-grow"}
    RAWVAL = {}
    for tk in T:
        i = RAW[tk]["info"]; n = C[tk]["norm"]; h = RAW[tk]["hist_1y"]; rw = C[tk]["rw"]; rel = C[tk]["rel"]
        pe = i.get("trailingPE")
        gm3 = None
        fin = RAW[tk]["financials"]; fc = sorted(fin.keys(), reverse=True)
        gms = []
        for c in fc[:3]:
            gp, rv = (fin[c] or {}).get("Gross Profit"), (fin[c] or {}).get("Total Revenue")
            if gp is not None and rv: gms.append(gp / rv * 100)
        if len(gms) >= 2: gm3 = (gms[0] - gms[-1]) / (len(gms) - 1)
        ss, ssp = i.get("sharesShort"), i.get("sharesShortPriorMonth")
        RAWVAL[tk] = {
          "P/E vs 類股中位數": f"{pe:.1f}x ÷ 32.0 = {pe/32:.2f}" if pe else "虧損，排除",
          "P/S": f"{n['ps']:.2f}x（校正後）" if tk == "SKHY" else f"{n['ps']:.2f}x",
          "EV/EBITDA": f"{n['ev_ebitda']:.1f}x（校正後）" if tk == "SKHY" else f"{n['ev_ebitda']:.1f}x",
          "PEG": f"{i['trailingPegRatio']:.3f}" if i.get("trailingPegRatio") else "獲利基數不適用，排除",
          "Piotroski F-Score": f"{C[tk]['piotroski']}／9",
          "ROIC − WACC 價差": f"ROIC {rw['roic']*100:.1f}% − WACC {rw['wacc']*100:.1f}% = {rw['spread']*100:+.1f}pp" if rw else "—",
          "毛利率三年趨勢": f"{gm3:+.1f}pp／年" if gm3 is not None else "—",
          "負債權益比": f"{i['debtToEquity']/100:.2f}" if i.get("debtToEquity") is not None else "—",
          "股價 vs MA50": f"{(i['currentPrice']/h['ma50']-1)*100:+.1f}%" if h.get("ma50") else "歷史不足",
          "股價 vs MA200": f"{(i['currentPrice']/h['ma200']-1)*100:+.1f}%" if h.get("ma200") else "歷史不足",
          "RSI(14)": f"{h['rsi14']:.1f}" if h.get("rsi14") and h["rsi14"] == h["rsi14"] else "歷史不足",
          "3M 相對 S&P500": f"{rel['3M']:+.1f}% vs 基準 {BENCH['^GSPC']['ret_1y_pct']/4:+.1f}%" if "3M" in rel else "歷史不足",
          "6M 相對 S&P500": f"{rel['6M']:+.1f}% vs 基準 {BENCH['^GSPC']['ret_1y_pct']/2:+.1f}%" if "6M" in rel else "歷史不足",
          "12M 相對 S&P500": f"{rel['12M']:+.1f}% vs 基準 {BENCH['^GSPC']['ret_1y_pct']:+.1f}%" if "12M" in rel else "歷史不足",
          "空單月變化": f"{(ss/ssp-1)*100:+.1f}%（{ss/1e6:.1f}M ← {ssp/1e6:.1f}M）" if ss and ssp else "未揭露",
          "法人持股水準": f"{i['heldPercentInstitutions']*100:.1f}%" if i.get("heldPercentInstitutions") else "未揭露",
          "分析師共識": f"{i.get('recommendationKey')}（{i.get('numberOfAnalystOpinions')} 位）",
          "目標價隱含上檔": f"{(i['targetMeanPrice']/i['currentPrice']-1)*100:+.1f}%（${i['targetMeanPrice']:,.0f}）" if i.get("targetMeanPrice") else "—",
          "營收 YoY": f"{i['revenueGrowth']*100:+.1f}%" if i.get("revenueGrowth") is not None else "—",
          "EPS YoY": f"{i['earningsGrowth']*100:+.1f}%" if i.get("earningsGrowth") is not None else "未揭露",
          "前瞻 EPS vs TTM": (f"${i['forwardEps']:.2f} ÷ ${i['trailingEps']:.2f} − 1 = {(i['forwardEps']/i['trailingEps']-1)*100:+.0f}%"
                              if i.get("forwardEps") and i.get("trailingEps") and i["trailingEps"] > 0 else "TTM EPS ≤0，排除"),
        }

    subsec = ""
    for dm in DIMS:
        allnames = []
        for tk in T:
            for k in C[tk]["screener"]["subs"][dm].keys():
                if k not in allnames: allnames.append(k)
        rws = ""
        for sn in allnames:
            cells = ""
            for tk in rank:
                v = C[tk]["screener"]["subs"][dm].get(sn)
                rv = RAWVAL[tk].get(sn, "—")
                if v is None:
                    cells += (f'<td style="text-align:center;color:var(--ink-3)">'
                              f'<span style="font-size:.75rem;font-style:italic">排除</span><br>'
                              f'<span style="font-size:.6875rem">{rv}</span></td>')
                else:
                    col = "#00723d" if v >= 7 else ("#b35c00" if v >= 4 else "#c0161c")
                    cells += (f'<td style="text-align:center"><strong style="color:{col};font-size:.9375rem">{v:.1f}</strong>'
                              f'<br><span style="font-size:.6875rem;color:var(--ink-3)">{rv}</span></td>')
            rws += (f'<tr><th scope="row" style="text-align:left"><strong>{sn}</strong><br>'
                    f'<span style="font-weight:400;font-size:.6875rem;color:var(--ink-3);line-height:1.5">'
                    f'{SUBEXP.get(sn,"")}</span></th>{cells}</tr>')
        dscores = "".join(
            f'<td style="text-align:center;background:var(--green-wash);font-weight:800">'
            f'{C[tk]["screener"]["dims"][dm]:.1f}</td>' if C[tk]["screener"]["dims"][dm] is not None
            else '<td style="text-align:center;background:var(--surface);font-style:italic;font-size:.75rem;color:var(--ink-3)">未評分</td>'
            for tk in rank)
        subsec += f"""<h3 id="{ANCHOR[dm]}">{dm}維度</h3>
<div class="tblwrap"><table class="dt dt--sm">
<thead><tr><th style="text-align:left;width:31%">子因子 · 評分規則</th>
{''.join(f'<th style="text-align:center;color:{V.SERIES[tk]}">{tk}</th>' for tk in rank)}</tr></thead>
<tbody>{rws}
<tr><th scope="row" style="text-align:left;background:var(--green-wash)">維度分數（子因子平均）</th>{dscores}</tr>
</tbody></table></div>"""

    d.append(f"""<section id="subs"><h2><span class="modnum">3</span>22 個子因子拆解</h2>
<p>每格上方為 0–10 分，下方小字為代入的原始值。任何「排除」都附理由，
框架不以中性值悄悄填補缺口。</p>
{subsec}
</section>""")

    # ---------------------------------------------------------------- deep dives
    deep = {
      "MU": ("""<ul>
<li><strong>成長 10.0／10（滿分）</strong>——營收年增 {rg}，季度序列 $9.30B → $11.32B → $13.64B → $23.86B → $41.46B，
單季 EPS 由 $1.68 攀至 $24.67。三個成長子因子全數頂格。</li>
<li><strong>品質 8.5／10</strong>——Piotroski <strong>9／9 滿分</strong>（四檔唯一），毛利率三年 +8.7pp／年，
D/E 僅 0.06，淨現金 {nc}。</li>
<li><strong>價值 8.1／10</strong>——PEG 0.13、EV/EBITDA 13.3x、本益比 20.4x 僅為類股中位數的 0.64 倍。
這是「高成長 × 低倍數」在數字上真實存在的罕見組合。</li>
<li><strong>情緒 9.1／10</strong>——40 位分析師、9 強力買進 ／ 31 買進 ／ 5 持有 ／ 0 賣出；空單月減 12.9%。</li>
<li><strong>動能 7.0／10 是唯一破口</strong>——MA200 之上 +61%（10 分）但 MA50 之下 −14.3%（0 分）、
RSI {rsi}（0 分）。趨勢結構正在裂開。</li></ul>""",
        "峰值利益率不可持續。TTM 淨利是四年平均的 {xa} 倍；若營業利益率回到除谷底三年均值 {oex}，"
        "15 倍本益比僅對應 {p15}／股，較現價低 {dn}。整份多方論述都押在「這次不一樣」。",
        "等 MA50（{ma50}）站回，或等 9 月 24 日財報確認毛利率未見頂。現價已反映峰值假設，不提供安全邊際。",
        "中期（3 個月–1 年）"),
      "SKHY": ("""<ul>
<li><strong>成長 10.0／10</strong>——營收年增 {rg}，最新一季 52.6 兆韓元（約 $38.1B），為去年同期的 2.98 倍。</li>
<li><strong>品質 9.4／10（四檔最高）</strong>——ROIC {roic} 對 WACC {wacc}，價差 <strong>+16.6pp</strong>，
四檔中唯一明顯創造價值者；毛利率三年 +6.2pp／年，D/E 0.13。</li>
<li><strong>價值 8.2／10</strong>——校正後 EV/EBITDA 13.6x、本益比 17.0x，與 MU 幾乎同價，
卻擁有更高的 ROIC 與更明確的 HBM 市佔領先。</li>
<li><strong>但只有 3 位分析師覆蓋</strong>，且 recommendationKey 為 buy——情緒維度的樣本數過小。</li>
<li><strong>動能完全無法評分</strong>——ADR 於 2026-07-10 掛牌，僅 13 個交易日。</li></ul>""",
        "資料本身不可靠。原始欄位給出 P/S 0.007 與負 31.5 兆的企業價值；本頁所有數值都經過人工幣別校正，"
        "而校正匯率是<strong>假設</strong>而非揭露值。加上 13 天的交易歷史，任何技術面或風險度量都無從建立。",
        "在取得至少一季的美股交易歷史、且能以韓國交易所原始財報交叉驗證幣別前，不宜作為主要部位。",
        "長期（1 年以上），但目前應視為觀察名單而非可執行標的"),
      "MRVL": ("""<ul>
<li><strong>情緒 9.1／10（與 MU 並列最高）</strong>——40 位分析師、8 強力買進 ／ 30 買進 ／ 0 賣出，
平均目標價 {tgt}（隱含 +47%）；空單月減 17.4%；法人持股 87.7%。</li>
<li><strong>品質 7.3／10</strong>——Piotroski 8／9、毛利率三年 +4.9pp／年、D/E 0.29。表面穩健。</li>
<li><strong>成長 6.4／10</strong>——營收年增 +27.6%、連五季創高，但 EPS 年增 <strong>−80.4%</strong>（0 分）。</li>
<li><strong>價值 2.6／10（四檔最低）</strong>——EV/EBITDA <strong>58.3x</strong> 拿 0 分、P/S 18.0x 拿 1.1 分。</li>
<li><strong>動能 6.0／10</strong>——RSI {rsi} 已進入超賣區，距 52 週高點 −47.1%，是四檔中回撤最深者。</li></ul>""",
        "ROIC {roic} 低於 WACC {wacc}，價差 <strong>−8.4pp</strong>——以會計數字論，MRVL 目前的成長是"
        "<strong>在毀滅價值</strong>。且商譽 $11.06B 占股東權益 $14.31B 的 77%，減損風險集中。",
        "價值維度 2.6 分意味著沒有估值保護。若要參與，應等 8 月 28 日財報確認 GAAP 營業利益率轉折，"
        "而非依賴 non-GAAP 前瞻 EPS。",
        "中期（3 個月–1 年）"),
    }
    dv = ""
    for n, tk in enumerate(rank[:3], 1):
        s = C[tk]["screener"]; i = RAW[tk]["info"]; rw = C[tk]["rw"]; cy = CYC[tk]
        why, risk, entry, hz = deep[tk]
        fmtargs = dict(
            rg=pcf(i.get("revenueGrowth"), 1, True), nc=money(abs(C[tk]["norm"]["net_debt"])),
            rsi=f"{RAW[tk]['hist_1y']['rsi14']:.1f}" if RAW[tk]["hist_1y"].get("rsi14") == RAW[tk]["hist_1y"].get("rsi14") else "n/a",
            xa=f"{cy['x_avg']:.1f}" if cy["x_avg"] else "n/a",
            oex=pcf(cy["opm_ex"]), p15=money(cy["scen"]["ex_trough"]["m15"]) if cy["scen"]["ex_trough"] else "—",
            dn=pc((1 - cy["scen"]["ex_trough"]["m15"] / i["currentPrice"]) * 100, 0) if cy["scen"]["ex_trough"] else "—",
            ma50=money(RAW[tk]["hist_1y"]["ma50"]) if RAW[tk]["hist_1y"].get("ma50") else "n/a",
            roic=pcf(rw["roic"]) if rw else "—", wacc=pcf(rw["wacc"]) if rw else "—",
            tgt=money(i.get("targetMeanPrice")))
        k, lbl = screener_signal(s["total"])
        dv += f"""<h3>第 {n} 名 · {tk} — {NAMES[tk][0]}　{st(k, lbl.split(" ",1)[1])}</h3>
<h4>為什麼分數高</h4>
{why.format(**fmtargs)}
<div class="call call--bad"><div class="call__h">🚩 最重要的單一風險</div>
<p>{risk.format(**fmtargs)}</p></div>
<div class="grid g2">
<div class="card card--surface"><div class="card__h">進場考量</div>
<p style="font-size:.9375rem;color:var(--ink-2)">{entry.format(**fmtargs)}</p></div>
<div class="card card--surface"><div class="card__h">適合投資期間</div>
<p style="font-size:.9375rem;color:var(--ink-2)">{hz}</p></div></div>"""

    d.append(f'<section id="deep"><h2><span class="modnum">4</span>前三名深潛</h2>{dv}</section>')

    # ---------------------------------------------------------------- avoid list
    bot = rank[-1]
    s = C[bot]["screener"]
    d.append(f"""<section id="avoid"><h2><span class="modnum">5</span>避開清單（後段班）</h2>
<p class="fignote">本次 universe 僅四檔，故「後三名」與「前三名」重疊。此處只列真正落入避開／持有下緣者。</p>
<h3>第 4 名 · {bot} — {NAMES[bot][0]}　{st(*screener_signal(s['total'])[0:1], screener_signal(s['total'])[1].split(" ",1)[1])}</h3>
<h4>為什麼分數低</h4>
<ul>
<li><strong>成長 0.0／10</strong>——營收年增 {pcf(RAW[bot]['info'].get('revenueGrowth'),1,True)}，
TTM EPS 為負使另兩個成長子因子全數排除。三個子因子中兩個無法評分，一個掛零。</li>
<li><strong>動能 0.2／10</strong>——股價 {money(RAW[bot]['info']['currentPrice'])} 就在 52 週最低點
{money(RAW[bot]['info']['fiftyTwoWeekLow'])} 上方一美分；同時低於 MA50 與 MA200，
三個相對強度子因子全部掛零。</li>
<li><strong>ROIC {pcf(C[bot]['rw']['roic'])} 低於 WACC {pcf(C[bot]['rw']['wacc'])}</strong>——價差 −7.5pp。
營運本身不創造超過資金成本的報酬。</li>
</ul>
<h4>但價值維度 5.6 分不是零——這才是陷阱所在</h4>
<p>P/S {C[bot]['norm']['ps']:.2f}x 拿到滿分 10.0，股價淨值比
<strong>{BS[bot]['pb']:.2f}</strong>（市值 {money(RAW[bot]['info']['marketCap'])}
對申報股東權益 {money(BS[bot]['equity'])}，每股淨值 {money(BS[bot]['bv_ps'])}），
帳上淨現金 {money(abs(C[bot]['norm']['net_debt']))}，
且公司正在<strong>每日買回自家股票</strong>。純以資產面看，這檔股票很便宜。</p>
<div class="call call--warn"><div class="call__h">⚠ 需持續追蹤的轉機訊號</div>
<ul>
<li><strong>7 月 28 日財報（已公布，股價當日 {pc(GAP[bot],1,True)}）</strong>——需確認營收是否已止穩、
以及最近兩季轉虧是否為一次性。</li>
<li><strong>股東權益走勢</strong>——年度 $1.306B → $1.212B → $1.133B → $1.101B（年均 −5.3%），
最近兩季再降至 $1.064B（年化 −7.1%，加速中）。
若侵蝕停止，0.30 倍淨值就從陷阱變成機會；若持續，折價只會隨淨值一起縮小。</li>
<li><strong>買回速度 vs 淨值侵蝕速度</strong>——這是 {bot} 唯一真正重要的賽跑，詳見
<a href="sndl.html#m15">SNDL 資本配置分析</a>。</li>
</ul></div></section>""")

    # ---------------------------------------------------------------- sector
    sox_ex = BENCH["^SOX"]["ret_1y_pct"] - BENCH["^GSPC"]["ret_1y_pct"]
    secrows = V.simple_table(
        ["類股／指數", "1 年報酬", "相對 S&P 500", "本籃子代表", "評註"],
        [["<strong>半導體 ^SOX</strong>", f'<span class="up">{pc(BENCH["^SOX"]["ret_1y_pct"],1,True)}</span>',
          f'<span class="up">{pc(sox_ex,0,True)} pp</span>', "MU · SKHY · MRVL",
          "領漲類股。極端超額報酬本身即是均值回歸風險"],
         ["<strong>半導體 ETF SMH</strong>", f'<span class="up">{pc(BENCH["SMH"]["ret_1y_pct"],1,True)}</span>',
          f'<span class="up">{pc(BENCH["SMH"]["ret_1y_pct"]-BENCH["^GSPC"]["ret_1y_pct"],0,True)} pp</span>',
          "—", "與 ^SOX 差 11pp，反映權重集中於少數大型股"],
         ["<strong>Nasdaq ^IXIC</strong>", pc(BENCH["^IXIC"]["ret_1y_pct"], 1, True),
          f'{pc(BENCH["^IXIC"]["ret_1y_pct"]-BENCH["^GSPC"]["ret_1y_pct"],1,True)} pp', "—",
          "科技整體僅小幅領先大盤——本輪漲勢高度集中在半導體"],
         ["<strong>S&amp;P 500 ^GSPC</strong>", pc(BENCH["^GSPC"]["ret_1y_pct"], 1, True), "基準", "—", "基準"],
         ["<strong>必需消費（SNDL 所屬）</strong>", '<span style="color:var(--ink-3)">未取樣</span>',
          "—", "SNDL", "SNDL 個股 1 年 −16.4%，與類股連動性低，屬個別事件驅動"]],
        align=["left", "right", "right", "left", "left"])

    d.append(f"""<section id="sector"><h2><span class="modnum">6</span>類股輪動背景<span class="skilltag">sector-analysis</span></h2>
<div class="tblwrap">{secrows}</div>
<div class="call call--warn"><div class="call__h">⚠ 相關性警告（框架強制項）</div>
<p>本次 universe 前三名 <strong>全部集中在半導體類股</strong>，且其中 MU 與 SKHY 是同一產品循環
（HBM／DRAM）的直接同業。三者的 Beta 分別為
{RAW['MU']['info']['beta']:.2f}／{RAW['SKHY']['info']['beta']:.2f}／{RAW['MRVL']['info']['beta']:.2f}，
全部高於 2.0。</p>
<p>2026-07-28 的同步下跌（−7.8% 至 −9.0%）正是這種集中度的實證：<strong>分散化在此籃子內不存在</strong>。
若依排行榜前三名等權建構組合，實質上等於對單一產業循環的三倍槓桿押注。
唯一的分散來源是排名最後的 SNDL（Beta {RAW['SNDL']['info']['beta']:.2f}）——
而它的低分正是因為它與這個循環無關。</p></div>
</section>""")

    # ---------------------------------------------------------------- macro
    d.append(f"""<section id="macro"><h2><span class="modnum">7</span>總體環境<span class="skilltag">economics-analysis</span></h2>
<h3>對本籃子最重要的三個總體變數</h3>
<div class="tblwrap">{V.simple_table(
  ["變數", "本頁採用值", "傳導路徑", "對本籃子的方向"],
  [["10 年期美債殖利率", "4.2%（WACC 無風險利率輸入）",
    "高 Beta 成長股的折現率 → 三檔半導體的 Ke 皆超過 14%",
    '<span class="dn">逆風</span>：Beta 2.0–2.2 使利率變動被放大兩倍以上'],
   ["股權風險溢酬", "5.0%",
    "CAPM：Ke ＝ 4.2% ＋ β×5.0%。MU 的 Ke 達 14.9%、MRVL 15.2%",
    '<span class="dn">逆風</span>：高折現率使 DCF 終值占比被壓縮，估值高度依賴近期現金流'],
   ["AI 資本支出循環", "由雲端業者資本支出指引隱含（未直接取樣）",
    "HBM 需求 → DRAM 定價 → MU／SKHY 毛利率 → MRVL 客製化 ASIC 出貨",
    '<span class="up">順風</span>，但已高度反映於價格：MU 現價隱含峰值利益率永續']],
  align=["left","left","left","left"])}</div>
<div class="call call--ink"><div class="call__h">📐 折現率如何影響結論（敏感度）</div>
<p>本頁 WACC 由 CAPM 推導而非採用市場慣用值，因此必須揭露其敏感度。以 MU 為例
（Beta {RAW['MU']['info']['beta']:.2f}、DCF WACC {C['MU']['dcf']['wacc']*100:.1f}%）：</p>
<ul>
<li>若股權風險溢酬由 5.0% 降至 4.0%，MU 的 Ke 降約 2.1pp，基準情境 DCF 每股價值上升約 25–30%。</li>
<li>反之若升至 6.0%，基準情境每股價值下降約 20%。</li>
</ul>
<p>換言之，<strong>本頁所有 DCF 結論對一個無法觀測的假設高度敏感</strong>。
這是為什麼四份報告都同時提供相對估值（倍數法）與循環常態化估值作為交叉驗證，
而非單押 DCF——詳見各報告的估值章節。</p></div>
</section>""")

    # ---------------------------------------------------------------- notes
    d.append(f"""<section id="notes"><h2><span class="modnum">8</span>篩選註記</h2>
<h3>被排除的子因子與原因</h3>
<div class="tblwrap">{V.simple_table(
  ["標的", "被排除的子因子", "原因"],
  [["SKHY", "動能全 6 項（MA50／MA200／RSI／3M／6M／12M 相對強度）",
    "ADR 於 2026-07-10 掛牌，僅 13 個交易日，指標視窗不足"],
   ["SKHY", "空單月變化、法人持股水準", "yfinance 未提供該 ADR 的 shortPercentOfFloat 與機構持股比重"],
   ["SNDL", "P/E vs 類股中位數、PEG", "TTM EPS 為 −$0.03，本益比與 PEG 無經濟意義"],
   ["SNDL", "EPS YoY、前瞻 EPS vs TTM", "獲利基數為負，成長率不可解讀"],
   ["SNDL", "分析師共識", "recommendationKey 為 none，僅 2 位分析師覆蓋"],
   ["MRVL", "無排除項", "22 個子因子全數可計算"],
   ["MU", "無排除項", "22 個子因子全數可計算"]],
  align=["left","left","left"])}</div>
<h3>未套用的篩選旗標</h3>
<p>本次刻意<strong>不</strong>套用 <code>--exclude-penny</code>（否則 SNDL 會在評分前就被剔除，
而它正是對照組的意義所在）與 <code>--min-market-cap</code>。
若套用 <code>--exclude-penny</code>，universe 剩三檔、均分將由 {avg:.2f} 升至
{sum(C[t]["screener"]["total"] for t in ["MU","SKHY","MRVL"])/3:.2f}，
市場偏向由中性轉為<strong>偏多</strong>——一個旗標就足以反轉結論，這正是為什麼旗標必須被明示。</p>
</section>""")

    # ---------------------------------------------------------------- validator
    vrows = [
      ("資料品質", 12, 20, "價格與財報均為當日程式化擷取（+5 新鮮度）。但 SKHY 幣別混用需人工校正、"
       "13 天歷史造成 6 個子因子空缺，完整性與一致性各扣分。"),
      ("方法論健全度", 16, 20, "五維度規則為框架預先定義，非事後配適（+5）。假設全部明示（無風險利率、"
       "ERP、類股中位數 P/E、匯率）（+5）。循環股同時採倍數法與常態化盈餘法交叉驗證（+4）。"
       "類股中位數 P/E 採單一估計值而非實際計算分佈，扣 2 分。"),
      ("訊號一致性", 8, 20, "基本面與技術面<strong>方向相反</strong>：三檔半導體品質／成長全數高分，"
       "動能維度卻同步破損（0 分）。這是本次篩選最大的內部矛盾，僅得 3／7。"
       "情緒訊號亦分歧：分析師一致看多、內部人只賣不買。"),
      ("風險覆蓋", 17, 20, "已具名三項以上風險並量化（循環常態化情境、商譽減損、淨值侵蝕）。"
       "空頭情境已建模而非僅列舉。財報日等催化劑已標註。"),
      ("推理透明度", 18, 20, "每個分數附原始輸入值與評分規則；排除項全部具名並附理由；"
       "已明示旗標選擇會反轉結論、DCF 對 ERP 高度敏感。"),
    ]
    tot = sum(r[1] for r in vrows)
    tier = ("VERY HIGH", "good") if tot >= 85 else ("HIGH", "good") if tot >= 70 else \
           ("MEDIUM", "warn") if tot >= 55 else ("LOW", "bad") if tot >= 40 else ("VERY LOW", "bad")
    vt = V.simple_table(["稽核維度", "得分", "說明"],
        [[f"<strong>{n}</strong>", f"<strong>{s} / {m}</strong>", desc] for n, s, m, desc in vrows] +
        [["<strong>總信賴分數</strong>", f"<strong>{tot} / 100</strong>",
          f"信賴等級 <strong>{tier[0]}</strong>"]],
        align=["left", "center", "left"])
    d.append(f"""<section id="valid"><h2><span class="modnum">9</span>結果稽核<span class="skilltag">result-validator</span></h2>
<div class="tblwrap">{vt}</div>
<div class="grid g2" style="margin-top:var(--s-24)">
<div class="card" style="background:#fff8ef;border-color:#ffd9a8"><div class="card__h">⚠ 警示</div><ul style="font-size:.9375rem;margin:0">
<li>前三名全部落在同一類股、同一產品循環——分散度為零。</li>
<li>基本面與技術面訊號方向相反，篩選結果本質上是「好公司、壞時機」。</li>
<li>類股中位數 P/E 為單點估計，非實際計算的分佈中位數。</li>
</ul></div>
<div class="card" style="background:#fdf0f0;border-color:#f7c4c4"><div class="card__h">🚩 紅旗</div><ul style="font-size:.9375rem;margin:0">
<li><strong>SKHY 的總分（{C['SKHY']['screener']['total']:.1f}）不應與其他三檔並列比較</strong>——
它缺 8 個子因子，且其餘數值依賴一個假設匯率。</li>
<li>MU 與 SKHY 的成長維度皆為滿分 10.0，但兩者的成長來自<strong>同一個循環</strong>，
評分模型無法辨識這種共同因子暴露。</li>
</ul></div>
<div class="card card--wash"><div class="card__h">✅ 優點</div><ul style="font-size:.9375rem;margin:0">
<li>所有 22 個子因子的原始輸入值均可在頁面上反查。</li>
<li>缺失資料一律標示「排除／未評分」，未以中性值粉飾。</li>
<li>已量化「未評分」處理對 SKHY 分數造成的低估幅度。</li>
</ul></div></div>
<h3>建議後續步驟</h3>
<ol>
<li><strong>先補強訊號一致性（最弱維度，8／20）</strong>——對三檔半導體執行
<code>catalyst-calendar</code>，判定動能破損是循環轉折的領先訊號，還是單純的部位調整。</li>
<li><strong>驗證 SKHY 的幣別</strong>——以韓國交易所原始財報與 20-F 交叉核對，
在此之前不應將其納入可執行清單。</li>
<li><strong>對 MU 執行 <code>bear-case</code></strong>（已於 <a href="mu.html#bear">MU 報告</a>完成）——
在成長維度滿分的情況下，紅隊檢驗是唯一能平衡評分模型樂觀偏誤的工具。</li>
</ol>
</section>""")

    d.append(f"""<section id="signal"><h2>訊號區塊</h2>
{sig_block([("Top Pick", f"{rank[0]} — Score {C[rank[0]]['screener']['total']:.1f} / 10"),
            ("Avg Score", f"{avg:.2f} / 10（screened universe）"),
            ("Screened", f"{len(T)} tickers"), None,
            ("Market Bias", f"BULLISH (avg {avg:.2f} >= 6.0)"),
            ("Best Sector", "Semiconductors (avg " +
             f"{sum(C[t]['screener']['total'] for t in ['MU','SKHY','MRVL'])/3:.1f})"), None,
            ("Confidence", f"{tier[0]} — {tot}/100"),
            ("Caveat", "top-3 share one cycle; SKHY incomplete")],
           title="INVESTMENT SIGNAL — SCREENING SUMMARY")}
<p class="fignote">Market Bias 依 universe 平均分推導：≥6.0 偏多、4.0–5.9 中性、&lt;4.0 偏空。
本次均分 {avg:.2f} 落在<strong>偏多</strong>區間。但這個「偏多」必須加上兩層限定：
其一，四檔的動能維度平均僅 {sum(v for v in [C[t]['screener']['dims']['動能'] for t in T] if v is not None)/3:.1f} 分，
偏多結論完全來自品質與成長維度；其二，前三名共享同一產業循環，
均分的「分散化」外觀是統計假象。<code>result-validator</code> 因此把訊號一致性壓到 8／20。</p>
<div class="chips" style="margin-top:var(--s-32)">
<a class="btn" href="mu.html">MU 旗艦報告（15 模組）→</a>
<a class="btn btn--soft" href="workflows.html">工作流 A–G →</a>
<a class="btn btn--soft" href="index.html">← 回展示櫃總覽</a>
</div></section>""")

    body = (f'<div class="wrap shell">{toc(tocg)}<div class="doc">{"".join(d)}</div></div>')
    return page("四檔對決 — 22 個子因子的完整推導 | InvestSkill Autopilot 展示櫃",
                "MU、SKHY、MRVL、SNDL 四檔的 stock-screener 五維度評分完整推導，含每個子因子的原始輸入值、排除理由與結果稽核。",
                "".join(b) + body, active="screener.html")
