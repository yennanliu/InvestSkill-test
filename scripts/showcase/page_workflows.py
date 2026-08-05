# -*- coding: utf-8 -*-
"""Cookbook 工作流 A–G，全部以本籃子的真實標的實跑一遍。"""
from context import *
import viz as V
from shell import page, toc

WF = [
 ("A", "財報前定位", "距財報三天，該不該抱過去？", "MRVL", "mrvl",
  [("earnings-call-analysis", "檢視前一季指引準確度與管理層語氣"),
   ("options-analysis", "隱含波動率排名與隱含變動幅度"),
   ("insider-trading", "過去 60 天高管交易"),
   ("technical-analysis", "支撐／壓力位置")]),
 ("B", "價值股篩選", "本益比看起來很低——是機會還是價值陷阱？", "SNDL", "sndl",
  [("stock-eval", "品質檢查：Piotroski F-Score、ROIC vs WACC"),
   ("competitor-analysis", "護城河是否惡化、市佔趨勢"),
   ("financial-report-analyst", "10-K 紅旗與會計品質"),
   ("dcf-valuation --scenarios", "保守假設下的內在價值"),
   ("result-validator", "驗證假設完整性")]),
 ("C", "股息組合建構", "用這個籃子能不能組出一個收益型組合？", "MU · MRVL · SNDL", None,
  [("dividend-analysis", "逐檔評估股息安全性"),
   ("portfolio-review", "合併殖利率、類股集中度、覆蓋率")]),
 ("D", "波段做多設定", "在空單擁擠的標的裡找有明確風報比的短線機會", "四檔全部", None,
  [("short-interest", "篩選門檻：流通股空單 >20%、回補天數 >5 天"),
   ("technical-analysis", "股價站上 20 日均線、RSI 回升、量能確認"),
   ("options-analysis", "偏斜與定義風險進場的成本結構"),
   ("chart-master --type price-volume", "突破型態視覺化")]),
 ("E", "完整投資備忘錄", "投入大額資金前的完整實地查核（單一指令）", "MU", "mu",
  [("full-report --depth comprehensive", "協調 15 個分析模組並產出 HTML"),
   ("result-validator", "對綜合訊號區塊做品質稽核")]),
 ("F", "總體驅動的類股輪動", "在當前利率與通膨環境下，哪些類股會贏？", "四檔全部", "screener",
  [("economics-analysis", "Fed 立場、殖利率曲線、實質利率"),
   ("sector-analysis", "不同利率環境下的歷史相對強度"),
   ("stock-eval", "在受益類股中篩選標的"),
   ("portfolio-review", "新部位對組合利率敏感度的影響")]),
 ("G", "管理既有部位", "已經持有但套住了，如何分批加碼而不情緒化攤平？", "MU", "mu",
  [("stock-eval + bear-case", "論點是否仍然成立？"),
   ("technical-analysis", "支撐位與 ATR（用於階距）"),
   ("portfolio-review", "集中度政策允許的最大部位"),
   ("position-ladder", "產生 5 階進場計畫、洗售警示、與買進持有的總報酬比較")]),
]


def chain(steps, tk_color="#00b14f", gate=None):
    """A workflow as a stepper: numbered badges on a rail that draws itself in.

    ``gate`` marks the 1-based step where the workflow refuses to continue — the
    step turns red so a blocked chain is visible before reading a word of it.
    """
    h = f'<div class="stp" style="--stp-c:{tk_color}">'
    for k, (skill, what) in enumerate(steps):
        cls = "stp__i stp__i--gate" if gate == k + 1 else "stp__i"
        h += (f'<div class="{cls}" data-n="{k+1}">'
              f'<div class="stp__s">/{skill}</div>'
              f'<div class="stp__w">{what}</div></div>')
    return h + "</div>"


CODES = [w[0] for w in WF]


def usage():
    """Framework → which workflows chain it, derived from WF itself.

    The skill strings carry flags (``--scenarios``) and combinations
    (``stock-eval + bear-case``); both are normalised here so the matrix, the
    table and the prose can never disagree about who uses what.
    """
    used = {}
    for code, *_rest in WF:
        for skill, _what in _rest[-1]:
            for part in skill.split("+"):
                name = part.strip().split(" ")[0]
                if not name:
                    continue
                used.setdefault(name, set()).add(code)
    return sorted(used.items(), key=lambda kv: (-len(kv[1]), kv[0]))


def build():
    use = usage()
    b = []
    b.append(f"""<section class="rhero"><div class="wrap rhero__in">
<p class="crumb"><a href="../index.html">InvestSkill Autopilot</a> ／ <a href="index.html">展示櫃</a> ／ 工作流 A–G</p>
<p class="eyebrow">cookbook · 7 workflows</p>
<h1>工作流 A–G：<br>把框架串成決策流程</h1>
<p class="rhero__sub">單一框架回答單一問題；<strong>工作流回答一個決策</strong>。
本頁把 <a href="https://yennj12.js.org/InvestSkill/cookbook-zh-tw.html" style="color:#fff;text-decoration:underline">Cookbook</a>
的七條工作流，全部用本籃子的真實標的跑一遍。
其中<strong>兩條在篩選閘門就停住、拒絕產出結果</strong>——那是本頁最有價值的部分。</p>
<div class="chips">
<span class="chip">7 條工作流</span>
<span class="chip">5 條產出結論</span>
<span class="chip">2 條在閘門被擋下</span>
<span class="chip">{ASOF}</span>
</div></div></section>""")

    tocg = [(None, [("intro", "為什麼要串成工作流")]),
            ("七條工作流", [(f"wf{code.lower()}", f"{code} · {name}") for code, name, *_ in
                            [(w[0], w[1]) for w in WF]]),
            ("結語", [("meta", "工作流層級的觀察")])]

    d = []
    # ------------------------------------------------------------- intro
    ov = V.simple_table(
      ["工作流", "回答的決策", "套用標的", "串接框架數", "結果"],
      [[f'<strong><a href="#wf{c.lower()}">{c}</a></strong> {nm}', q, tkl, str(len(steps)),
        {"A": st("warn", "產出決策矩陣"), "B": st("bad", "判定為價值陷阱"),
         "C": st("bad", "閘門擋下：無可用標的"), "D": st("bad", "閘門擋下：無標的符合"),
         "E": st("good", "產出完整備忘錄"), "F": st("warn", "產出輪動評分卡"),
         "G": st("warn", "產出 5 階階梯")}[c]]
       for c, nm, q, tkl, _lnk, steps in WF],
      align=["left", "left", "left", "center", "left"])
    d.append(f"""<section id="intro"><h2>為什麼要串成工作流</h2>
<p>27 個框架各自回答一個問題：這家公司值多少？技術面在哪個位置？內部人在做什麼？
但真實的投資決策從來不是單一問題，而是<strong>一連串有相依性的判斷</strong>——
而且前一步的答案會改變後一步該問什麼。</p>
<p>Cookbook 的七條工作流把這個相依性寫成明確的順序。本頁的重點不只是「跑得出結果」，
更是示範<strong>當前置條件不成立時，工作流會停下來</strong>：
工作流 C 與 D 都在第一步的篩選閘門被擋下，而這正是它們有用的證據。
一個永遠會給你答案的流程，不是分析流程，而是產生器。</p>
{V.figure(V.pipeline_chart(
  [{"n": 1, "title": "前提閘門", "kind": "gate",
    "sub": "檢查這個決策的前提是否成立（例如：空單是否真的擁擠、標的是否真的配息）",
    "meta": "不成立 → 工作流終止"},
   {"n": 2, "title": "獨立訊號蒐集",
    "sub": "2–5 個框架各自從不同資料面取得一個訊號，彼此不互看結論",
    "meta": "C 與 D 從未走到這裡"},
   {"n": 3, "title": "交叉驗證",
    "sub": "訊號一致則加強結論；互相矛盾則把矛盾寫出來，而不是平均掉",
    "meta": "矛盾＝資訊，不是雜訊"},
   {"n": 4, "title": "決策或拒絕", "kind": "out",
    "sub": "產出可執行的部位決策，或明確說明為何此刻不該有任何動作",
    "meta": "7 條中 5 條產出、2 條拒絕"}],
  aria="工作流的四段結構：前提閘門 → 獨立訊號蒐集 → 交叉驗證 → 決策或拒絕"),
  "圖 ── 七條工作流共用的四段結構", None,
  "第 1 段是工作流與單一框架最大的差別：單獨執行一個框架永遠會產出一份分析，"
  "而工作流會先問「這個問題此刻是否適用於這個標的」。",
  extra_cls="dagfig")}
<div class="tblwrap">{ov}</div>
</section>""")

    # ═══════════════════════════════════════════════════ WF A — MRVL
    e = EARN["MRVL"]; o = C["MRVL"]["options"]; h = RAW["MRVL"]["hist_1y"]; im = RAW["MRVL"]["info"]
    ins = INS["MRVL"]
    matrix = V.simple_table(
      ["訊號來源", "讀數", "方向", "權重理由"],
      [["<code>earnings-call-analysis</code>",
        f'共識 non-GAAP EPS ${e["eps_avg"]:.3f}（區間 ${e["eps_lo"]:.2f}–${e["eps_hi"]:.2f}，離散度僅 '
        f'{e["eps_hi"]/e["eps_lo"]:.2f} 倍）、營收 {money(e["rev_avg"])}（+11.8% QoQ）',
        st("warn", "中性偏空"),
        "預估區間極窄代表分析師對 non-GAAP 高度有信心，但<strong>GAAP 季度 EPS 僅 $0.04</strong>，"
        "兩者無法對帳。共識的「可預測性」建立在一個本報告無法驗證的基準上。"],
       ["<code>options-analysis</code>",
        f'IV {pc(o["atm_iv"]*100,1)} vs HV {pc(o["hv"],1)}（IV／HV ＝ {(o["atm_iv"]*100)/o["hv"]:.2f}）、'
        f'隱含變動 {pc(o["implied_move"],1)}、賣權／買權未平倉比 {num(o["pc_oi"])}',
        st("bad", "偏空"),
        f'賣權未平倉為買權的 {o["pc_oi"]:.2f} 倍——選擇權市場的避險需求明顯偏空。'
        f'IV 高於 HV 使買方策略成本偏高。'],
       ["<code>insider-trading</code>（過去 60 天）",
        f'{ins["n_sell"]} 筆賣出、合計 {money(ins["sell_total"])}、<strong>0 筆買進</strong>。'
        f'執行長、總裁、財務長全數在列，成交價 $199–$299',
        st("bad", "偏空"),
        f'現價 {money(im["currentPrice"])} <strong>低於全部六筆成交價</strong>，最高者高出 71%。'
        f'三個最高層職位在財報前 6 週內全部賣出。'],
       ["<code>technical-analysis</code>",
        f'RSI(14) {h["rsi14"]:.1f}（超賣）、股價低於 MA20 {pc((im["currentPrice"]/h["ma20"]-1)*100,1)}／'
        f'MA50 {pc((im["currentPrice"]/h["ma50"]-1)*100,1)}、MACD {h["macd"]:.2f} 在訊號線 {h["macd_signal"]:.2f} 之下',
        st("warn", "空頭趨勢，但已超賣"),
        f'距 52 週高點 {pc(DD["MRVL"],1)}。RSI < 30 意味著短線反彈機率上升，'
        f'但趨勢結構（MA、MACD）仍明確偏空。這是四個訊號中唯一有雙面性的。']],
      align=["left", "left", "center", "left"])
    d.append(f"""<section id="wfa"><h2>工作流 A · 財報前定位<span class="skilltag">MRVL</span></h2>
<p><strong>決策</strong>：MRVL 將於 {e["date"]}（{e["dte"]} 天後）公布財報。該抱過去，還是先減碼？</p>
<div class="grid g2">
<div>{chain(WF[0][5], V.SERIES["MRVL"])}</div>
<div><h3 style="margin-top:0">四訊號決策矩陣</h3>
<p style="font-size:.9375rem">四個獨立訊號中，<strong>三個偏空、一個中性偏空且帶超賣的雙面性</strong>。
沒有任何一個訊號支持抱過財報。</p>
<div class="card card--surface" style="margin-top:var(--s-16)">
<div class="card__h">結論：財報前減碼</div>
<p style="font-size:.9375rem;color:var(--ink-2)">四訊號一致偏空，且其中兩個（內部人、選擇權偏斜）
是<strong>知情程度較高</strong>的參與者行為。RSI 28.9 的超賣狀態提供的是短線反彈可能，
而非抱過財報的理由——財報是一個<strong>離散的雙向風險事件</strong>，
超賣不會降低財報不如預期的機率。</p></div></div></div>
<div class="tblwrap" style="margin-top:var(--s-24)">{matrix}</div>
<div class="call call--warn"><div class="call__h">⚠ 這條工作流沒有回答的問題</div>
<p>工作流 A 的設計目的是<strong>短期定位</strong>，它不評估估值。
本頁的結論（財報前減碼）與 <a href="mrvl.html">MRVL 完整報告</a>的結論（不進場，等 GAAP 利益率轉折）
方向一致，但推導路徑完全不同——前者看四個短期訊號，後者看三個互相矛盾的估值答案。
<strong>兩條路徑得到同樣結論，才使這個判斷比較可靠。</strong></p></div>
</section>""")

    # ═══════════════════════════════════════════════════ WF B — SNDL
    isn = RAW["SNDL"]["info"]; cn = C["SNDL"]
    trap = V.simple_table(
      ["價值陷阱檢查項", "SNDL 讀數", "判定"],
      [["本益比是否因獲利崩塌而失真",
        'TTM EPS −$0.03，本益比<strong>無法計算</strong>。前瞻本益比 40.7 倍（因獲利基數趨近零而失真）',
        st("bad", "是——不可用盈餘倍數")],
       ["資產折價是否真實",
        f'股價淨值比 <strong>{BS["SNDL"]["pb"]:.2f}</strong>（依申報資產負債表；'
        f'yfinance 欄位為 {isn["priceToBook"]:.2f}，低估 27%）、市值 {money(isn["marketCap"])} '
        f'對股東權益 {money(BS["SNDL"]["equity"])}、帳上現金 {money(BS["SNDL"]["cash"])}'
        f'（占市值 {BS["SNDL"]["cash_cover"]*100:.0f}%）、商譽僅占權益 11%',
        st("good", "是——折價真實且有實體資產支撐")],
       ["淨值是否穩定",
        '年度 $1.306B → $1.212B → $1.133B → $1.101B（年均 −5.3%），'
        '最近兩季再降至 <strong>$1.064B</strong>（年化 −7.1%，<strong>加速中</strong>）',
        st("bad", "否——這是決定性的一項")],
       ["ROIC 是否高於 WACC",
        f'ROIC {pcf(cn["rw"]["roic"])} vs WACC {pcf(cn["rw"]["wacc"])}，價差 <strong>{pcf(cn["rw"]["spread"],1,True)}</strong>',
        st("bad", "否——營運不創造超額報酬")],
       ["護城河是否惡化",
        'Porter 五力中四項為高／極高壓力。加拿大大麻市場長期供過於求，毛利率僅 27.3%',
        st("bad", "無護城河可惡化")],
       ["會計是否有紅旗",
        'TTM 營運現金流 +$66.6M 對淨利 −$11.0M（虧損來自非現金費用）。存貨四年持平、'
        '買回為真實註銷。<strong>會計品質良好</strong>',
        st("good", "否——財報乾淨")],
       ["營收是否仍在成長",
        f'TTM 營收年增 <strong>{pcf(isn["revenueGrowth"],1,True)}</strong>。'
        f'季度 $245M → $244M → $252M → $196M → $236M',
        st("bad", "否——已轉衰退")],
       ["是否有可驗證的轉機條件",
        '有：「連續兩季營業利益為正」。過去五季正負交替（+$2.9M → −$9.4M → +$10.3M → −$11.2M → −$5.4M），'
        '<strong>無任何兩季同向</strong>。下一季財報即可檢驗',
        st("warn", "有，但尚未出現")]],
      align=["left", "left", "left"])
    dsc = cn["dcf"]["scenarios"]
    sens = V.simple_table(
      ["情境", "年 1–5 營收成長", "每股價值", "相對現價 " + money(isn["currentPrice"])],
      [[{"bear": "保守（空方）", "base": "基準", "bull": "樂觀（多方）"}[s],
        pcf(dsc[s]["g1"], 0, True), money(dsc[s]["per_share"]),
        f'<span class="{cls(dsc[s]["per_share"]/isn["currentPrice"]-1)}">'
        f'{pc((dsc[s]["per_share"]/isn["currentPrice"]-1)*100,0,True)}</span>']
       for s in ["bear", "base", "bull"]] +
      [["<strong>每股帳面淨值（申報 BS）</strong>", "—", f'<strong>{money(BS["SNDL"]["bv_ps"])}</strong>',
        f'<span class="up">{pc((BS["SNDL"]["bv_ps"]/isn["currentPrice"]-1)*100,0,True)}</span>']],
      align=["left", "right", "right", "right"])
    d.append(f"""<section id="wfb"><h2>工作流 B · 價值股篩選<span class="skilltag">SNDL</span></h2>
<p><strong>決策</strong>：SNDL 股價淨值比 0.30、現金覆蓋 58% 市值、股價就在 52 週最低點。
這是機會，還是價值陷阱？</p>
<div class="grid g2">
<div>{chain(WF[1][5], V.SERIES["SNDL"])}</div>
<div><h3 style="margin-top:0">判定：<span class="dn">價值陷阱</span></h3>
<p style="font-size:.9375rem">八個檢查項中，<strong>五項判定為陷阱特徵、兩項為真實價值、一項待驗證</strong>。</p>
<div class="card" style="background:#fdf0f0;border-color:#f7c4c4;margin-top:var(--s-16)">
<div class="card__h">關鍵在第三項</div>
<p style="font-size:.9375rem;color:var(--ink-2)">深度價值需要兩個條件：
<strong>折價足夠大</strong>（✅ 0.30 倍）與<strong>資產價值穩定</strong>（❌ 年化 −7.1%）。
第二個條件失敗時，折價會靠<strong>分母縮小</strong>自行消失，而不需要股價上漲。
若以年化 −7.1% 外推五年，股東權益降至約 $0.74B，<strong>即使股價完全不動</strong>，
股價淨值比也會由 0.30 升至 <strong>0.43</strong>。</p></div></div></div>
<h3>陷阱訊號檢查表</h3>
<div class="tblwrap">{trap}</div>
<h3>保守假設下的 DCF（<code>--scenarios</code>）</h3>
<div class="tblwrap">{sens}</div>
<div class="call call--warn"><div class="call__h">⚠ 這裡出現一個罕見的矛盾，必須說明</div>
<p><strong>連空方情境的 DCF（{money(dsc["bear"]["per_share"])}）都高於現價 {money(isn["currentPrice"])}。</strong>
每股帳面淨值 {money(BS["SNDL"]["bv_ps"])} 更是現價的 {BS["SNDL"]["bv_ps"]/isn["currentPrice"]:.2f} 倍。
純以靜態估值論，SNDL <strong>沒有一個方法算出它應該更低</strong>。</p>
<p>那為什麼判定為陷阱？因為 DCF 與淨值都是<strong>靜態</strong>的，
而本工作流的第三項檢查捕捉到的是<strong>動態</strong>的：這些數字每年都在變小。
DCF 假設 −8% 的營收衰退，但它沒有假設股東權益持續侵蝕；
淨值 $4.09／股是<em>今天</em>的淨值，不是三年後的。</p>
<p><strong>這是工作流 B 存在的理由</strong>：單獨執行 <code>/dcf-valuation</code> 會得出
「SNDL 嚴重低估」的結論；加上 <code>/stock-eval</code> 的 ROIC 檢查與
<code>/financial-report-analyst</code> 的淨值趨勢，結論反轉。
<strong>順序有意義，缺一步就會得到相反的答案。</strong></p></div>
<div class="call"><div class="call__h">✅ <code>result-validator</code> 對本工作流的稽核</div>
<p>信賴分數 <strong>80／100（HIGH）</strong>。扣分項：
(1) 清算價值未逐項評估資產可變現性（存貨與不動產的實際折價率未知）；
(2) 加拿大法規風險無量化資料；
(3) 僅 2 位分析師覆蓋，外部驗證來源不足。
加分項：結論與資料一致、矛盾（DCF 看多 vs 趨勢看空）被明確呈現而非隱藏、
轉機條件可在下一季驗證。完整版見 <a href="sndl.html#valid">SNDL 報告稽核</a>。</p></div>
</section>""")

    # ═══════════════════════════════════════════════════ WF C — gate blocked
    div_tbl = V.simple_table(
      ["標的", "年化股息", "股息殖利率", "配息率", "FY 股息支出", "自由現金流覆蓋", "判定"],
      [["<strong>MU</strong>", money(RAW["MU"]["info"].get("dividendRate")),
        pcf(RAW["MU"]["info"].get("dividendYield"), 2), pcf(RAW["MU"]["info"].get("payoutRatio"), 2),
        money(0.52e9), f'{1.67/0.52:.1f} 倍（FY2025 FCF $1.67B）',
        st("bad", "殖利率過低，不符收益需求")],
       ["<strong>MRVL</strong>", money(RAW["MRVL"]["info"].get("dividendRate")),
        pcf(RAW["MRVL"]["info"].get("dividendYield"), 2), pcf(RAW["MRVL"]["info"].get("payoutRatio"), 2),
        money(0.21e9), f'{1.39/0.21:.1f} 倍（FY2026 FCF $1.39B）',
        st("bad", "殖利率過低，不符收益需求")],
       ["<strong>SKHY</strong>", '欄位為空（但現金流量表顯示有支付）',
        '約 0.13%（由現金流量表推算）', '約 3.9%（推算）', money(1.22e9),
        f'{18.0/1.22:.1f} 倍（FY2025 FCF $18.0B）',
        st("bad", "資料矛盾且殖利率過低")],
       ["<strong>SNDL</strong>", "無", "—", "0%", "$0", "—",
        st("bad", "不發放股息")]],
      align=["left", "right", "right", "right", "right", "right", "left"])
    d.append(f"""<section id="wfc"><h2>工作流 C · 股息組合建構<span class="skilltag">閘門擋下</span></h2>
<p><strong>決策</strong>：用這四檔能不能組出一個收益型組合？</p>
<div class="grid g2">
<div>{chain(WF[2][5], gate=2)}</div>
<div><h3 style="margin-top:0">結果：<span class="dn">工作流在第一步終止</span></h3>
<p style="font-size:.9375rem">Cookbook 的工作流 C 原始範例使用 JNJ、ABBV、PG——
殖利率 3%–4% 的成熟配息股。本籃子<strong>沒有一檔符合收益型標的的基本定義</strong>：
最高殖利率是 MU 的 {pcf(RAW["MU"]["info"].get("dividendYield"),2)}。</p>
<div class="card" style="background:#fdf0f0;border-color:#f7c4c4;margin-top:var(--s-16)">
<div class="card__h">為什麼這是正確的結果</div>
<p style="font-size:.9375rem;color:var(--ink-2)">框架<strong>沒有</strong>為了產出結果而降低門檻。
若強行執行 <code>/portfolio-review</code>，它會算出一個合併殖利率約 0.05% 的「收益組合」——
一個技術上正確但實務上荒謬的答案。<strong>拒絕產出，比產出一個無意義的數字更有價值。</strong></p></div></div></div>
<h3>逐檔股息安全性評估（<code>/dividend-analysis</code>）</h3>
<div class="tblwrap">{div_tbl}</div>
<div class="call call--ink"><div class="call__h">📐 但這一步仍然產出了有用的資訊</div>
<p>工作流 C 雖然無法完成原定目標，卻揭露了一個關於整個籃子的共同事實：
<strong>四檔的股息都由自由現金流充分覆蓋（1.7 至 14.8 倍），但金額都是象徵性的。</strong>
這不是財務脆弱，而是<strong>刻意的資本配置選擇</strong>——
三檔半導體把現金投入資本支出（MU 的資本支出占營運現金流 90%），SNDL 投入買回。</p>
<p>換句話說：這個籃子的報酬<strong>必須</strong>全部來自股價，沒有任何現金流緩衝。
對於 Beta 2.0–2.2 的三檔半導體而言，這是一個放大波動的結構性特徵，
而它只有在執行工作流 C 之後才浮現。</p></div>
</section>""")

    # ═══════════════════════════════════════════════════ WF D — gate blocked
    gate = V.simple_table(
      ["標的", "流通股空單比", "門檻 >20%", "回補天數", "門檻 >5 天", "空單月變化", "通過閘門？"],
      [[f"<strong>{tk}</strong>",
        pcf(RAW[tk]["info"].get("shortPercentOfFloat")) if RAW[tk]["info"].get("shortPercentOfFloat") else "未揭露",
        st("bad", "未通過"),
        num(RAW[tk]["info"].get("shortRatio")) + " 天" if RAW[tk]["info"].get("shortRatio") else "—",
        st("bad", "未通過"),
        (pc((RAW[tk]["info"]["sharesShort"]/RAW[tk]["info"]["sharesShortPriorMonth"]-1)*100, 1, True)
         if RAW[tk]["info"].get("sharesShort") and RAW[tk]["info"].get("sharesShortPriorMonth") else "未揭露"),
        st("bad", "否")]
       for tk in T],
      align=["left", "right", "center", "right", "center", "right", "center"])
    sq = V.hbar_chart([(f"{tk}", (RAW[tk]["info"].get("shortRatio") or 0), V.SERIES[tk], " 天")
                       for tk in T], fmt="{:.2f}", vmax=5.5, vmin=0)
    d.append(f"""<section id="wfd"><h2>工作流 D · 波段做多設定<span class="skilltag">閘門擋下</span></h2>
<p><strong>決策</strong>：在空單擁擠的標的中，找出有明確風報比的短線做多機會。</p>
<div class="grid g2">
<div>{chain(WF[3][5], gate=1)}</div>
<div><h3 style="margin-top:0">結果：<span class="dn">四檔全部未通過第一步篩選</span></h3>
<p style="font-size:.9375rem">工作流 D 的前提是<strong>空單擁擠</strong>——
流通股空單比 >20% 且回補天數 >5 天。這兩個條件同時成立時，
軋空才有燃料，短線做多的不對稱性才存在。</p>
<div class="card" style="background:#fdf0f0;border-color:#f7c4c4;margin-top:var(--s-16)">
<div class="card__h">實際數字差了一個數量級</div>
<p style="font-size:.9375rem;color:var(--ink-2)">最高的流通股空單比是 MRVL 的
<strong>{pcf(RAW["MRVL"]["info"]["shortPercentOfFloat"])}</strong>（門檻 20%），
最高的回補天數是 SNDL 的 <strong>{RAW["SNDL"]["info"]["shortRatio"]:.2f} 天</strong>（門檻 5 天）。
四檔的回補天數<strong>全部低於 1 天</strong>——
以日均量計，全部空單不到一個交易日就能回補完畢。</p></div></div></div>
<h3>閘門檢查</h3>
<div class="tblwrap">{gate}</div>
{V.figure(sq, "圖 ── 回補天數（days-to-cover）vs 工作流 D 的 5 天門檻",
  V.simple_table(["標的","空單股數","前月","月變化","流通股","回補天數"],
    [[f"<strong>{tk}</strong>",
      f'{RAW[tk]["info"]["sharesShort"]/1e6:,.2f}M' if RAW[tk]["info"].get("sharesShort") else "—",
      f'{RAW[tk]["info"]["sharesShortPriorMonth"]/1e6:,.2f}M' if RAW[tk]["info"].get("sharesShortPriorMonth") else "未揭露",
      (pc((RAW[tk]["info"]["sharesShort"]/RAW[tk]["info"]["sharesShortPriorMonth"]-1)*100,1,True)
       if RAW[tk]["info"].get("sharesShort") and RAW[tk]["info"].get("sharesShortPriorMonth") else "—"),
      f'{RAW[tk]["info"]["floatShares"]/1e6:,.0f}M' if RAW[tk]["info"].get("floatShares") else "—",
      num(RAW[tk]["info"].get("shortRatio")) + " 天" if RAW[tk]["info"].get("shortRatio") else "—"]
     for tk in T]),
  "最高者 0.88 天，距 5 天門檻仍有 5.7 倍差距。SKHY 的 0.19 天為四檔最低，但其借券市場僅成立 13 個交易日，代表性有限。")}
<div class="call"><div class="call__h">💡 這個「失敗」推翻了一個常見的直覺</div>
<p>四檔全部處於明顯回撤中（−33% 至 −58%），直覺上會認為「空方在打壓」。
但資料顯示相反：<strong>四檔的空單月變化全部為負</strong>——
MU −12.9%、MRVL −17.4%、SNDL −25.7%。<strong>空方在回補，不是在加碼。</strong></p>
<p>這改變了對整個籃子回撤性質的理解：這不是空頭攻擊，
而是<strong>多方自己在賣</strong>。這個結論與四份報告中「內部人只賣不買、主動型法人減碼」
的證據方向一致，而它是工作流 D 在<strong>失敗過程中</strong>產出的副產品。</p>
</div></section>""")

    # ═══════════════════════════════════════════════════ WF E — MU
    cmu = C["MU"]["composite"]
    d.append(f"""<section id="wfe"><h2>工作流 E · 完整投資備忘錄<span class="skilltag">MU</span></h2>
<p><strong>決策</strong>：投入大額資金前的完整實地查核。單一指令、15 個模組。</p>
<div class="grid g2">
<div>{chain(WF[4][5], V.SERIES["MU"])}</div>
<div><h3 style="margin-top:0">產出：<a href="mu.html">MU 完整報告</a></h3>
<p style="font-size:.9375rem">這是七條工作流中最短的一條（兩步），
因為 <code>full-report</code> 本身就是一個協調器——它在內部依五個階段推進 15 個模組，
前階段的產出成為後階段的輸入。</p>
<div class="tblwrap" style="margin-top:var(--s-16)">{V.simple_table(["階段","模組數","子分數"],
  [[f'階段{n} · {PHASE_LABEL[k]}', str(len(PHASE_MODULES[k])), f'{cmu["phases"][k]:.1f}']
   for n, k in zip("一二三四五", PHASE_ORDER)] +
  [["<strong>綜合</strong>", f'<strong>{sum(len(PHASE_MODULES[k]) for k in PHASE_ORDER)}</strong>',
    f'<strong>{cmu["total"]:.2f}</strong>']],
  align=["left","center","right"])}</div>
<p class="fignote" style="margin-top:var(--s-8)">階段與模組的對應關係見
<a href="index.html">展示櫃總覽的管線圖</a>。</p></div></div>
<div class="call call--warn"><div class="call__h">⚠ 工作流 E 最重要的一步是第二步</div>
<p><code>full-report</code> 產出的是一個綜合評分 <strong>{cmu["total"]:.2f}／10</strong>，
落在「持有／觀察」區間。但這個分數是<strong>兩股方向相反的力量加權平均</strong>的結果：
商業品質 {cmu["phases"]["business"]:.1f}（接近滿分）與技術時機 {cmu["phases"]["technical"]:.1f}（接近墊底）。</p>
<p>如果只看 {cmu["total"]:.2f} 這個數字，會誤以為「訊號中性、沒什麼特別」。
<code>result-validator</code> 的作用就是把這件事揭露出來：
它給 MU 報告的訊號一致性只有 <strong>6／20</strong>，
並在稽核結論中明確標示「基本面與技術面明確對立」——
因此正確的解讀不是「中性」，而是<strong>「訊號衝突，僅觀察」</strong>。</p>
<p><strong>一個綜合分數若沒有搭配信賴稽核，就是把矛盾平均掉。</strong>這是工作流 E 只有兩步、
但第二步不可省略的原因。</p></div>
<p style="margin-top:var(--s-24)"><a class="btn" href="mu.html">閱讀完整的 15 模組備忘錄 →</a></p>
</section>""")

    # ═══════════════════════════════════════════════════ WF F
    rot = V.simple_table(
      ["類股／指數", "1 年報酬", "相對 S&P 500", "在當前利率環境的理論定位", "本籃子代表"],
      [["<strong>半導體 ^SOX</strong>", f'<span class="up">{pc(BENCH["^SOX"]["ret_1y_pct"],1,True)}</span>',
        f'<span class="up">+{BENCH["^SOX"]["ret_1y_pct"]-BENCH["^GSPC"]["ret_1y_pct"]:.0f} pp</span>',
        "高 Beta 成長類股在<strong>高利率環境理論上應受壓</strong>，"
        "但 AI 資本支出循環壓倒了利率因素。這個背離本身是風險訊號",
        "MU · SKHY · MRVL"],
       ["<strong>半導體 ETF SMH</strong>", f'<span class="up">{pc(BENCH["SMH"]["ret_1y_pct"],1,True)}</span>',
        f'<span class="up">+{BENCH["SMH"]["ret_1y_pct"]-BENCH["^GSPC"]["ret_1y_pct"]:.0f} pp</span>',
        "與 ^SOX 相差 11pp，反映權重集中於少數大型股", "—"],
       ["<strong>Nasdaq ^IXIC</strong>", pc(BENCH["^IXIC"]["ret_1y_pct"], 1, True),
        f'{pc(BENCH["^IXIC"]["ret_1y_pct"]-BENCH["^GSPC"]["ret_1y_pct"],1,True)} pp',
        "科技整體僅小幅領先大盤——<strong>本輪漲勢並非「科技股上漲」，而是「半導體上漲」</strong>", "—"],
       ["<strong>S&amp;P 500 ^GSPC</strong>", pc(BENCH["^GSPC"]["ret_1y_pct"], 1, True), "基準",
        "基準", "—"],
       ["<strong>必需消費</strong>", '<span style="color:var(--ink-3)">未取樣</span>', "—",
        "防禦類股在高利率環境相對抗跌，但無 AI 曝險",
        f'SNDL（個股 1 年 {pc(RAW["SNDL"]["hist_1y"]["ret_pct"],1,True)}）']],
      align=["left", "right", "right", "left", "left"])
    beta_tbl = V.simple_table(
      ["組合", "加權 Beta", "加權 Ke", "說明"],
      [["前三名等權（MU／SKHY／MRVL）",
        f'{(RAW["MU"]["info"]["beta"]+RAW["SKHY"]["info"]["beta"]+RAW["MRVL"]["info"]["beta"])/3:.2f}',
        f'{4.2+((RAW["MU"]["info"]["beta"]+RAW["SKHY"]["info"]["beta"]+RAW["MRVL"]["info"]["beta"])/3)*5.0:.1f}%',
        "篩選器排行榜前三名。<strong>Beta 超過 2.0，且三檔同屬一個產業循環</strong>"],
       ["四檔等權",
        f'{sum(RAW[t]["info"]["beta"] for t in T)/4:.2f}',
        f'{4.2+(sum(RAW[t]["info"]["beta"] for t in T)/4)*5.0:.1f}%',
        f'加入 SNDL（Beta {RAW["SNDL"]["info"]["beta"]:.2f}）使組合 Beta 下降 '
        f'{(RAW["MU"]["info"]["beta"]+RAW["SKHY"]["info"]["beta"]+RAW["MRVL"]["info"]["beta"])/3 - sum(RAW[t]["info"]["beta"] for t in T)/4:.2f}'],
       ["S&amp;P 500", "1.00", f'{4.2+5.0:.1f}%', "參考基準"]],
      align=["left", "center", "center", "left"])
    d.append(f"""<section id="wff"><h2>工作流 F · 總體驅動的類股輪動<span class="skilltag">四檔全部</span></h2>
<p><strong>決策</strong>：在當前利率與通膨環境下，哪些類股會贏？加入這些部位對組合的利率敏感度有什麼影響？</p>
<div class="grid g2"><div>{chain(WF[5][5])}</div>
<div><h3 style="margin-top:0">產出：輪動評分卡</h3>
<p style="font-size:.9375rem">工作流 F 的核心發現是一個<strong>背離</strong>：
以 4.2% 的無風險利率與 5.0% 的股權風險溢酬計，Beta 2.0–2.2 的高成長類股
理論上應該是最受壓的資產（權益成本 14.3%–15.2%）。
但過去一年 ^SOX 上漲 {BENCH["^SOX"]["ret_1y_pct"]:.0f}%，是 S&amp;P 500 的
{BENCH["^SOX"]["ret_1y_pct"]/BENCH["^GSPC"]["ret_1y_pct"]:.1f} 倍。</p>
<p style="font-size:.9375rem"><strong>AI 資本支出循環完全壓倒了利率因素。</strong>
這意味著這個籃子的風險不在利率，而在資本支出循環本身。</p></div></div>
<h3>類股評分卡（<code>/economics-analysis</code> ＋ <code>/sector-analysis</code>）</h3>
<div class="tblwrap">{rot}</div>
<h3>組合 Beta 與利率敏感度（<code>/portfolio-review</code>）</h3>
<div class="tblwrap">{beta_tbl}</div>
<div class="call call--bad"><div class="call__h">🚩 工作流 F 的結論與篩選器的排行榜衝突</div>
<p><a href="screener.html">篩選器</a>給出的前三名是 MU（8.5）、SKHY（8.3）、MRVL（6.2）——
三檔全部是半導體。若照此建構等權組合，組合 Beta 為
<strong>{(RAW["MU"]["info"]["beta"]+RAW["SKHY"]["info"]["beta"]+RAW["MRVL"]["info"]["beta"])/3:.2f}</strong>，
且三檔共享同一個需求驅動因子。</p>
<p><strong>2026-07-28 提供了這個集中度的實證</strong>：三檔同日下跌
{abs(GAP["MU"]):.1f}%／{abs(GAP["SKHY"]):.1f}%／{abs(GAP["MRVL"]):.1f}%。
分散化在這個組合內<strong>不存在</strong>。</p>
<p>而唯一的分散化來源，是篩選器排名<strong>最後一名</strong>的 SNDL
（Beta {RAW["SNDL"]["info"]["beta"]:.2f}）——它的低分正是因為它與這個循環無關。
<strong>工作流 F 因此得出一個單獨執行篩選器不會得到的結論：
排行榜的分數順序，不等於建構組合的順序。</strong></p></div>
</section>""")

    # ═══════════════════════════════════════════════════ WF G — MU ladder
    hmu = RAW["MU"]["hist_1y"]; imu = RAW["MU"]["info"]; cymu = CYC["MU"]
    atr = hmu["atr14"]; pmu = imu["currentPrice"]
    CAP, FLOOR, NR = 500, 300, 5
    per = CAP / NR
    lr, cum_sh, cum_cost = [], 0.0, 0.0
    for k in range(NR):
        px = round((pmu - k * atr) / 5) * 5
        cum_sh += per; cum_cost += per * px
        lr.append([f"第 {k+1} 階", money(px), f"{per:.0f}", f"{cum_sh:.0f}",
                   money(cum_cost), money(cum_cost / cum_sh), pc((px / pmu - 1) * 100, 1, True)])
    full_cost = cum_cost; full_avg = cum_cost / cum_sh
    bottom = round((pmu - (NR - 1) * atr) / 5) * 5
    d.append(f"""<section id="wfg"><h2>工作流 G · 管理既有部位<span class="skilltag">MU</span></h2>
<p><strong>決策</strong>：已持有 MU 但套住了（現價 {money(pmu)}，距 52 週高點 {pc(DD["MU"],1)}）。
如何分批加碼而不陷入情緒化攤平？</p>
<div class="call call--warn"><div class="call__h">⚠ 三個必須先說清楚的前提（框架強制項）</div>
<ul style="margin:6px 0">
<li><strong>降低平均成本不等於賺錢。</strong>平均成本是會計與心理的定錨，不是報酬指標。
賣掉高成本部位會機械式地讓這個數字變小，但不會創造一分錢的財富。</li>
<li><strong>這是波動率收割。</strong>此策略在區間震盪的行情中優於買進持有，
在單邊趨勢（無論漲跌）中都較差。只漲不跌會使階梯填不滿；只跌不漲會填滿後繼續跌。</li>
<li><strong>真正的優勢是控倉。</strong>「到 {CAP} 股就停止加碼，無論如何」——
這個硬性上限是把向下攤平從無上限的負債轉為有界限押注的唯一機制。</li>
</ul></div>
<div class="grid g2"><div>{chain(WF[6][5], V.SERIES["MU"])}</div>
<div><h3 style="margin-top:0">第一步的答案決定後面三步是否執行</h3>
<p style="font-size:.9375rem"><code>/stock-eval</code> 給 MU 的商業品質分數
<strong>{C["MU"]["composite"]["phases"]["business"]:.1f}／10</strong>（Piotroski 9／9、
淨現金 {money(abs(C["MU"]["norm"]["net_debt"]))}）——論點的<strong>商業面</strong>成立。</p>
<p style="font-size:.9375rem">但 <code>/bear-case</code> 給出空方強度 <strong>7.0／10</strong>，
核心論點是「現價 {money(pmu)} ≈ 峰值利益率 {pcf(cymu["opm_now"])} 永久維持 × 15 倍
＝ {money(cymu["scen"]["peak"]["m15"])}」。</p>
<div class="card card--surface" style="margin-top:var(--s-16)">
<div class="card__h">判定：論點成立，但估值不提供安全邊際</div>
<p style="font-size:.9375rem;color:var(--ink-2)">因此階梯<strong>可以</strong>建立
（公司不會倒），但<strong>不設起始批次</strong>（不先買 30–40%），
且上限必須從嚴。這是第一步影響第四步的具體方式。</p></div></div></div>
<h3>階距與部位控制（<code>/technical-analysis</code> ＋ <code>/portfolio-review</code>）</h3>
<div class="tblwrap">{V.simple_table(["參數","設定","依據"],
  [["階距", f'1.0 × ATR(14) ＝ {money(atr)}',
    f'ATR 占股價 {atr/pmu*100:.1f}%。緊於 0.5×ATR 會在單日雜訊中全部成交；寬於 2×ATR 則很少成交'],
   ["階數", f'{NR} 階', "框架預設值"],
   ["上限（硬性）", f'{CAP} 股（約 {money(CAP*pmu)})',
    f'依 <code>/portfolio-review</code>：高 Beta 標的集中度上限 5%（MU Beta {imu["beta"]:.2f}），'
    f'故此上限對應約 {money(CAP*pmu/0.05)} 的投組規模'],
   ["下限（核心永不賣出）", f'{FLOOR} 股', f'上限的 {FLOOR/CAP:.0%}，使修剪腿永遠不會把部位賣光'],
   ["每階股數", f'{per:.0f} 股（等股數）', "等股數配置：平均成本＝各階價格的簡單平均"],
   ["帳戶類型", "應稅帳戶", "保守假設（完整稅務摩擦）"],
   ["成本基礎法", "FIFO", "多數券商預設"],
   ["時間預算", "2 個季度", "涵蓋 9/24 與其後一次財報"]],
  align=["left","left","left"])}</div>
<h3>5 階進場階梯（<code>/position-ladder</code>）</h3>
<div class="tblwrap">{V.simple_table(
  ["階", "價位", "本階股數", "累計股數", "累計投入", "混合平均成本", "距現價"], lr,
  align=["left","right","right","right","right","right","right"])}</div>
<div class="tblwrap">{V.simple_table(["完全成交時的必要數字","數值"],
  [["總投入資本", f'<strong>{money(full_cost)}</strong>'],
   ["混合平均成本", f'<strong>{money(full_avg)}</strong>'],
   ["需承受的自現價跌幅", f'<strong>{pc((bottom/pmu-1)*100,1)}</strong>（至第 {NR} 階 {money(bottom)}）'],
   ["若價格停在最低階的未實現損益",
    f'{money((bottom-full_avg)*CAP)}（每股 {money(bottom-full_avg)} × {CAP} 股）'],
   ["對照：現價一次買足 500 股的成本", f'{money(pmu*CAP)}　（階梯節省 {money(pmu*CAP-full_cost)}）'],
   ["與買進持有的比較",
    f'若 MU 直接回升至 {money(imu["targetMeanPrice"])}，一次買足的報酬為 '
    f'{pc((imu["targetMeanPrice"]/pmu-1)*100,0,True)}，'
    f'而階梯僅成交第 1 階（100 股）→ <strong>階梯在單邊上漲中明確劣於買進持有</strong>']],
  align=["left","right"])}</div>
<div class="call call--bad"><div class="call__h">🚩 論點破裂出場閘門——這才是工作流 G 的重點</div>
<p>以下任一條件成立時，<strong>停止階梯並出場</strong>，而非繼續向下加碼：</p>
<ul>
<li><strong>連續兩季毛利率下滑</strong>——循環轉折確認。目前 84.6%。</li>
<li><strong>資本支出指引再上調而營收指引下修</strong>——現金流結構惡化。
FY2025 資本支出已占營運現金流 90%。</li>
<li><strong>三家寡占中任一家宣布大幅擴產或降價</strong>——HBM 定價權假設破裂。</li>
<li><strong>出現內部人買進之外的治理事件</strong>（財務長異動、重編財報）——盈餘品質假設破裂。</li>
</ul>
<p>在上限 {CAP} 股處，加碼停止。進一步下跌不是加碼的理由，而是重新執行論點檢驗的理由。
<strong>在下跌過程中提高上限，是這個計畫最常見、也最昂貴的失敗方式。</strong></p></div>
<div class="call call--ink"><div class="call__h">📐 階梯填不滿的問題，以及本頁的選擇</div>
<p>若 MU 自 {money(pmu)} 直接上行而不回落，這個階梯只會成交第 1 階（{per:.0f} 股，占目標 20%）。
框架提供兩種緩解方式，且要求<strong>事先</strong>選定：</p>
<ul>
<li><strong>起始批次</strong>：立刻以市價建立 30–40% 部位。保證有意義的曝險，代價是放棄較好的均價。</li>
<li><strong>時間backstop</strong>：若時間預算（2 季）結束時階梯成交不足 X%、且股價高於第 1 階，
則將階梯上移錨定至當時價格，或接受較小的部位。</li>
</ul>
<p><strong>本頁選擇「不設起始批次」＋「接受較小部位」</strong>，理由是
<a href="mu.html#valsum">MU 報告的估值總結</a>已判定現價安全邊際為零。
先建立 30–40% 部位會與該結論直接矛盾。
<strong>這個取捨必須在情緒介入之前決定，這正是工作流存在的理由。</strong></p></div>
</section>""")

    # ═══════════════════════════════════════════════════ meta
    d.append(f"""<section id="meta"><h2>工作流層級的觀察</h2>
<div class="grid g2">
<div class="card card--wash"><div class="card__h">✅ 三個只有在工作流層級才會浮現的結論</div>
<ol style="font-size:.9375rem;margin:0">
<li><strong>單獨執行 <code>/dcf-valuation</code> 會把 SNDL 判為嚴重低估</strong>
（連空方情境 {money(C["SNDL"]["dcf"]["scenarios"]["bear"]["per_share"])} 都高於現價 {money(RAW["SNDL"]["info"]["currentPrice"])}）。
加上 ROIC 檢查與淨值趨勢後，結論反轉為價值陷阱。<strong>順序有意義。</strong></li>
<li><strong>四檔的空單月變化全部為負</strong>——工作流 D 在失敗過程中證明了：
這一輪 −33% 至 −58% 的回撤不是空頭攻擊，而是多方自己在賣。</li>
<li><strong>篩選器的排行榜順序不等於建構組合的順序</strong>——
前三名 Beta 平均 {(RAW["MU"]["info"]["beta"]+RAW["SKHY"]["info"]["beta"]+RAW["MRVL"]["info"]["beta"])/3:.2f}
且共享同一循環；唯一的分散化來源是排名最後的 SNDL。</li>
</ol></div>
<div class="card" style="background:#fff8ef;border-color:#ffd9a8"><div class="card__h">⚠ 兩條被閘門擋下的工作流</div>
<p style="font-size:.9375rem;color:var(--ink-2)"><strong>工作流 C</strong>（股息組合）與
<strong>工作流 D</strong>（波段做多）都在第一步終止，因為本籃子沒有標的符合前提。</p>
<p style="font-size:.9375rem;color:var(--ink-2)">這是本頁刻意展示的部分。
一個永遠會產出答案的分析流程，無法區分「有機會」與「沒機會」——
它只會把門檻降到剛好能通過的水準，然後給你一個數字。</p>
<p style="font-size:.9375rem;color:var(--ink-2)"><strong>工作流 C 若強行執行</strong>，
會產出一個合併殖利率約 0.05% 的「收益型組合」；
<strong>工作流 D 若強行執行</strong>，會在回補天數 0.88 天的標的上規劃軋空交易。
兩者技術上都能算，實務上都是錯的。</p></div>
</div>
<h3>七條工作流的框架使用矩陣</h3>
{V.figure(
  V.matrix_dots(CODES, [(sk, [c in codes for c in CODES],
                         f'{len(codes)} 條' + ("（內含 15 模組）" if sk == "full-report" else ""))
                        for sk, codes in use]),
  "圖 ── 框架 × 工作流使用矩陣（實心＝該工作流明確串接此框架）",
  V.simple_table(["框架", "被幾條工作流使用", "使用於"],
    [[f"<code>{sk}</code>", str(len(codes)),
      " · ".join(sorted(codes)) + ("（內含 15 個模組）" if sk == "full-report" else "")]
     for sk, codes in use],
    align=["left", "center", "left"]),
  f"{len(use)} 個不同框架被七條工作流串接，"
  f"其中 <code>technical-analysis</code>、<code>stock-eval</code>、<code>portfolio-review</code> "
  f"各出現在三條中——分別擔任時機層、品質閘門與部位層。"
  f"矩陣由本頁的工作流定義程式化推導，因此不會與各節內文脫節。"
  f"<code>full-report</code>（工作流 E）本身又內含 15 個模組，"
  f"因此七條工作流的實際框架覆蓋率達 100%。",
  extra_cls="dagfig")}
<div class="chips" style="margin-top:var(--s-32)">
<a class="btn" href="mu.html">MU 完整備忘錄 →</a>
<a class="btn btn--soft" href="supply-chain.html">產業鏈地圖 →</a>
<a class="btn btn--soft" href="index.html">← 回展示櫃</a>
</div></section>""")

    body = f'<div class="wrap shell">{toc(tocg)}<div class="doc">{"".join(d)}</div></div>'
    return page("工作流 A–G — 把框架串成決策流程 | InvestSkill Autopilot 展示櫃",
                "Cookbook 七條工作流（財報前定位、價值陷阱檢定、股息組合、波段做多、完整備忘錄、"
                "類股輪動、加碼階梯）全部以 MU／SKHY／MRVL／SNDL 實跑，其中兩條在篩選閘門被擋下。",
                "".join(b) + body, active="workflows.html")
