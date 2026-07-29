# -*- coding: utf-8 -*-
"""industry-map — HBM／AI 記憶體價值鏈有向圖。"""
from context import *
import viz as V
from shell import page, toc

# layer: (name, position, tickers, concentration, value capture, margin note, flag)
LAYERS = [
 ("原材料與基板", "上游", "信越化學 · SUMCO · 環球晶(6488.TW)", "寡占（4 家占矽晶圓 ~70%）",
  "中等", "矽晶圓為長約定價，漲價傳導慢；毛利率 20–35%", None),
 ("半導體設備", "上游", "ASML · AMAT · LRCX · KLAC · TEL",
  "<strong>ASML 在 EUV 為獨家</strong>", "極高",
  "EUV 微影無替代供應商，毛利率 50%+。整條鏈的實質收費站", "choke"),
 ("記憶體製造（DRAM／HBM）", "中游", "<strong>MU</strong> · <strong>SKHY</strong> · Samsung",
  "三家寡占", "極高（循環頂點）",
  f"TTM 營業利益率 MU {pcf(RAW['MU']['info']['operatingMargins'])}／"
  f"SKHY {pcf(RAW['SKHY']['info']['operatingMargins'])}。"
  f"歷史區間 −35% 至 +80%——本層的利潤是循環性的", "target"),
 ("先進封裝（CoWoS 類）", "中游", "台積電 · ASE(3711.TW) · Amkor",
  "<strong>台積電主導</strong>", "高",
  "HBM 堆疊與 2.5D／3D 整合的實體瓶頸。決定記憶體廠的實際出貨上限", "choke"),
 ("邏輯代工", "中游", "台積電(TSM) · Samsung · Intel",
  "台積電在先進製程近獨占", "極高",
  "先進製程毛利率 50%+；AI 加速器與客製化 ASIC 皆依賴此層", "choke"),
 ("加速器與客製化 ASIC", "中游", "NVDA · AMD · AVGO · <strong>MRVL</strong>",
  "NVDA 主導通用市場；ASIC 為 AVGO／MRVL 競逐", "極高（NVDA）／中等（MRVL）",
  f"MRVL 的 GAAP 營業利益率僅 {pcf(RAW['MRVL']['info']['operatingMargins'])}，"
  f"ROIC {pcf(C['MRVL']['rw']['roic'])} 低於 WACC {pcf(C['MRVL']['rw']['wacc'])}"
  f"——同一層裡，領先者與挑戰者的價值捕獲差距極大", "target"),
 ("互連與網路", "中游", "AVGO · ANET · <strong>MRVL</strong> · Coherent",
  "寡占", "高",
  "光電互連隨叢集規模擴大而需求非線性成長。MRVL 的第二條腿", "target"),
 ("伺服器與系統組裝", "中游", "SMCI · Dell · HPE · 鴻海 · 廣達",
  "分散（代工競爭）", "低",
  "毛利率 5–15%。承擔記憶體與 GPU 的成本上漲，議價力最弱的一層", None),
 ("雲端與資料中心", "下游", "MSFT · AMZN · GOOGL · META · CoreWeave",
  "少數超大型業者", "高",
  "<strong>本層的資本支出＝上游全部層級的營收</strong>。"
  "同時是記憶體廠與 ASIC 商的唯一客戶群", "demand"),
 ("模型實驗室", "下游", "OpenAI · Anthropic · xAI（未上市）",
  "少數", "尚未穩定", "推論成本結構決定長期記憶體需求的形狀", None),
 ("AI 應用與終端用戶", "下游", "企業軟體 · 消費端應用",
  "分散", "待觀察", "最終付費方。若此層的變現不如預期，需求會沿鏈向上收縮", None),
]

MERMAID = """flowchart LR
  MAT["原材料與基板<br/>信越 · SUMCO · 環球晶"] --> EQ["半導體設備<br/>ASML · AMAT · LRCX"]
  EQ --> MEM["記憶體 DRAM／HBM<br/>MU · SKHY · Samsung"]
  EQ --> FAB["邏輯代工<br/>TSM · Samsung · INTC"]
  MEM --> PKG["先進封裝 CoWoS<br/>TSM · ASE · Amkor"]
  FAB --> PKG
  FAB --> ACC["加速器／客製化 ASIC<br/>NVDA · AMD · AVGO · MRVL"]
  PKG --> ACC
  ACC --> NET["互連與網路<br/>AVGO · ANET · MRVL"]
  NET --> SYS["伺服器組裝<br/>SMCI · Dell · 鴻海"]
  ACC --> SYS
  SYS --> CSP["雲端／資料中心<br/>MSFT · AMZN · GOOGL · META"]
  CSP --> LAB["模型實驗室<br/>OpenAI · Anthropic"]
  LAB --> APP["AI 應用<br/>企業 · 消費端"]
  APP --> USER["終端付費用戶"]
  CSP -. 資本支出指引決定上游營收 .-> MEM
  classDef choke fill:#fdf0f0,stroke:#e02020,stroke-width:2px
  classDef target fill:#e6f7ee,stroke:#00b14f,stroke-width:2px
  class EQ,PKG,FAB choke
  class MEM,ACC,NET target"""

ASCII = """上游 ──────────────────────────► 中游 ──────────────────────────► 下游

原材料 ──► 設備 ──┬──► 記憶體 DRAM/HBM ──┐
(信越,SUMCO)  (ASML*) │    (MU, SKHY, Samsung)  │
                      │                          ▼
                      └──► 邏輯代工 ──────► 先進封裝* ──► 加速器/ASIC
                           (TSM*)           (TSM, ASE)    (NVDA, AVGO, MRVL)
                                                              │
                                                              ▼
   終端用戶 ◄── AI 應用 ◄── 模型實驗室 ◄── 雲端/CSP ◄── 伺服器 ◄── 互連
                                          (MSFT,AMZN)   (SMCI)   (AVGO,MRVL)
                                              │
                                              └─ 資本支出指引 ──► 決定上游全鏈營收

* ＝ 瓶頸層（可信供應商最少，議價力最強）"""


def build():
    b = []
    b.append("""<section class="rhero"><div class="wrap rhero__in">
<p class="crumb"><a href="../index.html">InvestSkill Autopilot</a> ／ <a href="index.html">展示櫃</a> ／ 產業鏈</p>
<p class="eyebrow">framework · industry-map</p>
<h1>HBM 價值鏈：<br>錢在哪一層被收走</h1>
<p class="rhero__sub">其他框架橫向比較同業；這個框架<strong>縱向</strong>切開整條產業鏈，
問一個不同的問題：這個產業實際上如何運作，以及<strong>每一層由誰捕獲利潤</strong>。
把鏈畫出來之後，三件單一公司視角看不見的事會浮現：定位、瓶頸、與利潤池的遷移方向。</p>
<div class="chips">
<span class="chip">11 個層級</span>
<span class="chip">3 個瓶頸層</span>
<span class="chip">4 個二階標的</span>
<span class="chip">本籃子定位：中游 × 2 層</span>
</div></div></section>""")

    tocg = [(None, [("scope", "範圍界定"), ("graph", "價值鏈有向圖"), ("table", "分層資料表"),
                    ("choke", "瓶頸層分析"), ("pos", "本籃子的定位"),
                    ("migrate", "利潤池遷移"), ("second", "二階投資標的"),
                    ("risk", "全鏈風險"), ("signal", "訊號區塊")])]

    d = []
    d.append(f"""<section id="scope"><h2>範圍界定</h2>
<p>本圖繪製的是<strong>「AI 記憶體」這個主題</strong>的完整價值鏈，
起點為精煉後的矽晶圓與基板（不往上追至礦砂），
終點為<strong>付費的終端用戶</strong>（企業與消費端的 AI 應用付費方）。</p>
<p>選擇這個範圍的理由：本展示櫃的四檔標的中有三檔落在這條鏈上（MU、SKHY 在記憶體層，
MRVL 在加速器／ASIC 與互連兩層），而<strong>它們共同的需求驅動因子在鏈的最下游</strong>——
雲端業者的資本支出。把鏈畫完整，才能看出這個共同暴露的位置。</p>
{prov("層級劃分與代表標的為產業結構判斷（非取自本次資料快照）。"
      "利潤率數字取自 yfinance 快照：MU、SKHY、MRVL 為 TTM 實際值，其餘層級為區間判斷。",
      "產業結構為模型推理；本籃子三檔的財務數字為程式化擷取",
      "<strong>MEDIUM</strong> — 鏈的結構與瓶頸位置為判斷而非量測；"
      "僅 MU／SKHY／MRVL 的層級數字有本次資料支撐")}
</section>""")

    # graph
    flow = ""
    groups = [("上游", ["原材料與基板", "半導體設備"]),
              ("中游", ["記憶體製造（DRAM／HBM）", "先進封裝（CoWoS 類）", "邏輯代工",
                        "加速器與客製化 ASIC", "互連與網路", "伺服器與系統組裝"]),
              ("下游", ["雲端與資料中心", "模型實驗室", "AI 應用與終端用戶"])]
    for gname, names in groups:
        flow += (f'<div class="toc__grp" style="margin-top:var(--s-24);font-size:.75rem">'
                 f'{gname}</div><div class="flow__row">')
        for nm in names:
            L = next(x for x in LAYERS if x[0] == nm)
            _, pos, tickers, conc, cap, note, flag = L
            cl = ("node node--choke" if flag == "choke" else
                  "node node--target" if flag == "target" else "node")
            badge = ("🔴 瓶頸層" if flag == "choke" else
                     "🟢 本籃子所在" if flag == "target" else
                     "🔵 需求源頭" if flag == "demand" else pos)
            flow += (f'<div class="{cl}"><div class="node__pos">{badge}</div>'
                     f'<div class="node__n">{nm}</div>'
                     f'<div class="node__t">{tickers}</div>'
                     f'<div class="node__m"><strong>集中度</strong>：{conc}<br>'
                     f'<strong>價值捕獲</strong>：{cap}</div></div>')
        flow += "</div>"
        if gname != "下游":
            flow += '<div class="arrowrow">▼　▼　▼</div>'

    d.append(f"""<section id="graph"><h2>價值鏈有向圖</h2>
<p>箭頭方向 ＝ 商品與服務的流向（供應商 → 購買方）。</p>
{flow}
<h3>Mermaid 原始碼（可貼進 GitHub／Claude／Cursor 直接渲染）</h3>
<div class="mm"><pre>{MERMAID}</pre></div>
<h3>ASCII 備援格式</h3>
<div class="mm"><pre>{ASCII}</pre></div>
</section>""")

    # table
    tbl = V.simple_table(
      ["層級", "定位", "代表標的", "集中度", "當前價值捕獲", "利潤率備註"],
      [[f'<strong>{nm}</strong>', pos, tk, conc,
        ("🔴 " if flag == "choke" else "🟢 " if flag == "target" else "") + cap, note]
       for nm, pos, tk, conc, cap, note, flag in LAYERS],
      align=["left", "center", "left", "left", "left", "left"])
    d.append(f"""<section id="table"><h2>分層資料表</h2>
<div class="tblwrap">{tbl}</div>
</section>""")

    # chokepoints
    d.append(f"""<section id="choke"><h2>瓶頸層分析</h2>
<p>可信供應商最少的層級，會不成比例地捕獲整條鏈的價值。本鏈有三個明確瓶頸，
<strong>而本籃子的三檔標的都不在其中任何一個</strong>。</p>
<div class="grid g3">
<div class="card" style="background:#fdf0f0;border-color:#f7c4c4">
<div class="card__h">🔴 EUV 微影 — ASML</div>
<p style="font-size:.9375rem;color:var(--ink-2)">先進 DRAM 與邏輯製程的<strong>獨家</strong>設備供應商。
沒有替代來源、沒有二手市場、交期以年計。</p>
<p style="font-size:.9375rem;color:var(--ink-2);margin-top:8px"><strong>對 MU／SKHY 的意義</strong>：
兩家的擴產速度<strong>不由自己決定</strong>。這既是風險（無法快速回應需求）
也是保護（限制了同業殺價擴產的能力）——本輪循環利潤率能達到 70–80% 的結構性原因之一。</p></div>
<div class="card" style="background:#fdf0f0;border-color:#f7c4c4">
<div class="card__h">🔴 先進封裝 — 台積電主導</div>
<p style="font-size:.9375rem;color:var(--ink-2)">HBM 的堆疊與 2.5D／3D 整合產能，
是 AI 加速器實際出貨量的<strong>物理上限</strong>。</p>
<p style="font-size:.9375rem;color:var(--ink-2);margin-top:8px"><strong>對 MU／SKHY 的意義</strong>：
HBM 賣得出去多少，取決於封裝產能而非記憶體產能。
這使記憶體廠的營收預測必須參考<strong>另一家公司</strong>的產能擴張計畫。</p></div>
<div class="card" style="background:#fdf0f0;border-color:#f7c4c4">
<div class="card__h">🔴 先進邏輯代工 — 台積電</div>
<p style="font-size:.9375rem;color:var(--ink-2)">加速器與客製化 ASIC 全部依賴此層。
先進製程近乎獨占，毛利率 50% 以上。</p>
<p style="font-size:.9375rem;color:var(--ink-2);margin-top:8px"><strong>對 MRVL 的意義</strong>：
MRVL 無自有產能，其產品成本與供貨節奏都受制於此層。
這是 MRVL 的 Porter 五力中「供應商議價力」被評為高壓力的直接原因。</p></div>
</div>
<div class="call call--warn"><div class="call__h">⚠ 這張圖對本籃子最不利的一個推論</div>
<p>MU 與 SKHY 位於<strong>兩個瓶頸層之間</strong>：上游被 ASML 限制擴產速度，
中游被台積電的封裝產能限制出貨量。它們的高利潤率來自產業結構
（三家寡占 ＋ 上下游雙重產能限制），而<strong>不是來自自身的議價力</strong>。</p>
<p>這解釋了一個看起來矛盾的數字：MU 的 TTM 營業利益率高達
{pcf(RAW['MU']['info']['operatingMargins'])}，但
<strong>ROIC 僅 {pcf(C['MU']['rw']['roic'])}，低於 WACC {pcf(C['MU']['rw']['wacc'])}</strong>。
在史上最好的獲利年度，MU 仍未賺回資金成本——因為它必須把幾乎全部營運現金流
（FY2025 資本支出占營運現金流 90%）投回設備，而設備的定價權在 ASML 手上。</p>
<p><strong>結構的受益者，不等於結構的擁有者。</strong></p></div>
</section>""")

    # position
    roic_rows = [("ASML（EUV 瓶頸）", None, V.INK3, "未取樣"),
                 ("SKHY 記憶體", C["SKHY"]["rw"]["roic"] * 100, V.SERIES["SKHY"], ""),
                 ("MU 記憶體", C["MU"]["rw"]["roic"] * 100, V.SERIES["MU"], ""),
                 ("MRVL ASIC／互連", C["MRVL"]["rw"]["roic"] * 100, V.SERIES["MRVL"], ""),
                 ("SNDL（鏈外對照）", C["SNDL"]["rw"]["roic"] * 100, V.SERIES["SNDL"], "")]
    rc = V.hbar_chart(roic_rows, fmt="{:.1f}%", zero_line=True, vmin=-5, vmax=35,
                      pad=(14, 120, 26, 150))
    wacc_note = V.simple_table(
      ["標的", "鏈上層級", "ROIC", "WACC", "價差", "判讀"],
      [[f'<strong>{tk}</strong>',
        {"MU": "記憶體製造（中游）", "SKHY": "記憶體製造（中游）",
         "MRVL": "加速器／ASIC ＋ 互連（中游）", "SNDL": "不在此鏈上"}[tk],
        pcf(C[tk]["rw"]["roic"]), pcf(C[tk]["rw"]["wacc"]),
        f'<strong class="{cls(C[tk]["rw"]["spread"])}">{pcf(C[tk]["rw"]["spread"],1,True)}</strong>',
        {"MU": "循環頂點仍未賺回資金成本——資本密集度抵銷了定價權",
         "SKHY": "<strong>四檔中唯一明確創造價值</strong>。同一層裡的營運效率差異",
         "MRVL": "成長正在毀滅價值。挑戰者在瓶頸層下游的典型處境",
         "SNDL": "鏈外對照組：無 AI 曝險，同樣未賺回資金成本"}[tk]]
       for tk in ["SKHY", "MU", "MRVL", "SNDL"]],
      align=["left", "left", "right", "right", "right", "left"])
    d.append(f"""<section id="pos"><h2>本籃子的定位</h2>
<p>四檔標的中有三檔落在這條鏈的<strong>中游</strong>，且分屬兩個不同層級。
第四檔（SNDL）完全不在鏈上——這是它在本展示櫃中作為對照組的意義。</p>
{V.figure(rc, "圖 ── 各標的 ROIC（%），以鏈上層級排序", wacc_note,
  "ROIC ＝ EBIT×(1−稅率) ÷ 投入資本。WACC 由 CAPM 推導（無風險利率 4.2%、股權風險溢酬 5.0%）。"
  "SKHY 數值為幣別校正後。ASML 未納入本次資料快照，故無數值。")}
<div class="call"><div class="call__h">💡 同一層裡的 17.6 個百分點差距</div>
<p>MU 與 SKHY 在<strong>完全相同的層級</strong>、面對相同的瓶頸、賣給相同的客戶，
但 ROIC 相差 <strong>{(C['SKHY']['rw']['roic']-C['MU']['rw']['roic'])*100:.1f} 個百分點</strong>
（SKHY {pcf(C['SKHY']['rw']['roic'])} vs MU {pcf(C['MU']['rw']['roic'])}）。</p>
<p>產業鏈地圖解釋了為什麼<em>這一層</em>有高利潤，但它<strong>無法解釋層內的差異</strong>——
那需要 <code>competitor-analysis</code>（製程良率、產品組合、HBM 世代領先程度）。
<strong>兩個框架回答不同層級的問題，缺一不可。</strong></p>
<p>順帶一提，這個差距也是 SKHY 報告的核心張力：它可能是本籃子最優秀的公司，
但它的資料<a href="skhy.html#valid">無法支撐這個結論</a>。</p></div>
</section>""")

    # value migration
    d.append(f"""<section id="migrate"><h2>利潤池遷移</h2>
<p>利潤池不是固定的。它隨<strong>稀缺性的移動</strong>沿鏈上下遷移。
以下是本鏈的三個階段判斷：</p>
<div class="tblwrap">{V.simple_table(
  ["階段", "稀缺點所在", "利潤集中層", "本籃子的處境"],
  [["<strong>2023 前</strong>：AI 前", "無明顯稀缺（記憶體供過於求）",
    "設備（ASML）與代工（TSM）",
    'MU FY2023 營業利益率 <strong class="dn">−34.8%</strong>、SKHY FY2023 <strong class="dn">−23.6%</strong>'],
   ["<strong>2024–2026</strong>：現在", "<strong>HBM 產能與先進封裝</strong>",
    "記憶體（暫時）＋ 加速器（NVDA）＋ 瓶頸層",
    f'MU TTM {pcf(RAW["MU"]["info"]["operatingMargins"])}、'
    f'SKHY TTM {pcf(RAW["SKHY"]["info"]["operatingMargins"])}——歷史級的利潤率'],
   ["<strong>下一階段</strong>：判斷", "資本支出落地後，稀缺點下移至<strong>電力、散熱、推論成本</strong>",
    "從記憶體遷出，往電力基礎設施與推論效率移動",
    "<strong>這是本籃子最大的結構風險</strong>：記憶體的高利潤率是稀缺性的租金，"
    "而三家供應商正在同時擴產以消除該稀缺性"]],
  align=["left","left","left","left"])}</div>
<div class="call call--bad"><div class="call__h">🚩 這條鏈的自我毀滅機制</div>
<p>記憶體層目前 70–80% 的營業利益率，是<strong>供給落後於需求</strong>的租金。
而這個租金會誘發三件事，全部都在消除它自己：</p>
<ol>
<li><strong>三家供應商同時擴產</strong>——MU FY2025 資本支出 $15.86B、
SKHY FY2025 約 $20.7B（校正後）。這些產能會在 12–24 個月內落地。</li>
<li><strong>瓶頸層擴產</strong>——ASML 與台積電封裝產能的擴張會解除物理上限，
反而讓記憶體層的供給更快釋放。</li>
<li><strong>客戶尋求替代</strong>——雲端業者自研 ASIC（MRVL 的機會）
與推論效率優化，都在降低單位算力的記憶體需求。</li>
</ol>
<p>換言之，<strong>本籃子三檔標的當前的高獲利，正在資助消除自身高獲利的產能</strong>。
這不是對這輪循環的否定——它是真實的；而是對
<a href="mu.html#m5">「峰值利益率永久維持」這個市場隱含假設</a>的結構性質疑。</p></div>
</section>""")

    # second-order
    d.append("""<section id="second"><h2>二階投資標的</h2>
<p>畫完鏈之後，可以問一個單一公司分析問不出的問題：
<strong>如果本籃子的論點是對的，還有誰會受益？如果是錯的，誰受傷最小？</strong></p>
<div class="grid g2">
<div class="card card--wash"><div class="card__h">① 瓶頸層 — 收費站邏輯</div>
<p style="font-size:.9375rem;color:var(--ink-2)"><strong>ASML · 台積電（TSM）</strong></p>
<p style="font-size:.9375rem;color:var(--ink-2)">三家記憶體廠同時擴產時，
它們<strong>共同的供應商</strong>會收到全部三份訂單。
瓶頸層的營收與「哪一家贏」無關，只與「總擴產金額」有關。</p>
<p style="font-size:.9375rem;color:var(--ink-2);margin-top:8px"><strong>為什麼這是二階</strong>：
本籃子的資本支出（MU $15.86B ＋ SKHY 約 $20.7B）是這兩家的營收。
若記憶體循環見頂，記憶體廠的獲利先崩，但擴產計畫通常有 12–24 個月的執行慣性——
瓶頸層的營收會<strong>晚一段時間</strong>才受影響。</p></div>
<div class="card card--wash"><div class="card__h">② 先進封裝純度標的</div>
<p style="font-size:.9375rem;color:var(--ink-2)"><strong>ASE(3711.TW) · Amkor</strong></p>
<p style="font-size:.9375rem;color:var(--ink-2)">HBM 的實體瓶頸在堆疊與整合。
封裝層的產能是 HBM 出貨的硬上限，且此層的競爭者少於記憶體層。</p>
<p style="font-size:.9375rem;color:var(--ink-2);margin-top:8px"><strong>為什麼這是二階</strong>：
封裝廠<strong>不承擔記憶體的價格風險</strong>——它收取加工費，
無論 DRAM 每 GB 賣多少錢。這使它在循環下行時的獲利波動小於 MU／SKHY。</p></div>
<div class="card card--surface"><div class="card__h">③ 下一個稀缺點 — 電力與散熱</div>
<p style="font-size:.9375rem;color:var(--ink-2)"><strong>Vertiv(VRT) · Eaton · Schneider · 電力事業</strong></p>
<p style="font-size:.9375rem;color:var(--ink-2)">利潤池遷移的判斷指向此處：
記憶體與算力的產能問題解決後，資料中心的限制因素變成<strong>電力供應與散熱</strong>。</p>
<p style="font-size:.9375rem;color:var(--ink-2);margin-top:8px"><strong>為什麼這是二階</strong>：
這一層的需求驅動因子與記憶體<strong>相同</strong>（雲端資本支出），
但供給端的擴產週期<strong>更長</strong>（電網建設以 5–10 年計）。
若 AI 資本支出持續，稀缺性租金會從記憶體轉移到此處。</p></div>
<div class="card card--surface"><div class="card__h">④ 反向 — 議價力最弱的一層</div>
<p style="font-size:.9375rem;color:var(--ink-2)"><strong>伺服器組裝（SMCI · Dell · 代工廠）</strong></p>
<p style="font-size:.9375rem;color:var(--ink-2)">毛利率 5–15%。它<strong>同時</strong>承擔
上游記憶體與 GPU 的成本上漲、以及下游雲端業者的殺價。</p>
<p style="font-size:.9375rem;color:var(--ink-2);margin-top:8px"><strong>為什麼值得注意</strong>：
這一層是記憶體漲價的<strong>受害者</strong>。若持有 MU／SKHY，
組裝層是天然的反向部位；反之若記憶體價格回落，此層的毛利率會先改善。
<strong>這是整條鏈上唯一與本籃子負相關的層級。</strong></p></div>
</div>
<div class="call call--ink"><div class="call__h">📐 這四個標的都不在本次資料快照中</div>
<p>本節列出的標的<strong>沒有任何一檔</strong>經過本展示櫃的資料擷取與評分流程——
它們是<code>industry-map</code> 依產業結構推導出的<strong>研究方向</strong>，不是投資結論。</p>
<p>正確的下一步是把它們送進 <a href="screener.html"><code>stock-screener</code></a> 排名，
再對前幾名執行 <a href="mu.html"><code>full-report</code></a>。
<strong>產業鏈地圖產生假設，其他框架驗證假設。</strong></p></div>
</section>""")

    # whole-chain risk
    d.append(f"""<section id="risk"><h2>全鏈風險</h2>
<div class="tblwrap">{V.simple_table(
  ["風險", "傳導路徑（沿鏈方向）", "本籃子的曝險"],
  [["<strong>雲端資本支出下修</strong>",
    "雲端（下游）→ 加速器 → 記憶體 ＋ 封裝 → 代工 → 設備（上游）。<strong>由下往上收縮</strong>",
    '<span class="dn">最高</span>。三檔全部依賴同一批客戶的資本支出決策。'
    'MU 與 SKHY 的客戶重疊度接近 100%'],
   ["<strong>記憶體產能過剩</strong>",
    "三家同時擴產 → 供給釋放 → DRAM 現貨價下跌 → 記憶體層利潤率壓縮",
    '<span class="dn">最高</span>。MU 與 SKHY 直接受衝擊。'
    '歷史前例：FY2023 兩家營業利益率分別為 −34.8% 與 −23.6%'],
   ["<strong>瓶頸層產能解除</strong>",
    "ASML／台積電封裝擴產 → 物理上限放寬 → 記憶體供給更快釋放",
    '<span class="dn">高</span>。諷刺的是，<strong>瓶頸鬆綁對記憶體廠是壞消息</strong>——'
    '它移除了限制同業擴產的結構性保護'],
   ["<strong>客戶自研替代</strong>",
    "雲端業者自研 ASIC → 減少對通用加速器的依賴",
    '<span class="fl">分歧</span>。對 MRVL 是<strong>機會</strong>（客製化 ASIC 需求），'
    '對 NVDA 是威脅，對記憶體層<strong>中性</strong>（無論誰的晶片都需要 HBM）'],
   ["<strong>地緣政治 ／ 出口管制</strong>",
    "設備出口限制 → 代工與記憶體擴產受阻 → 供給收縮（對現有廠商可能有利）",
    '<span class="fl">分歧</span>。限制中國廠商（CXMT）反而保護三家寡占；'
    '但 SKHY 在中國有產能，曝險高於 MU'],
   ["<strong>AI 應用變現不如預期</strong>",
    "終端用戶（最下游）→ 應用 → 模型實驗室 → 雲端 → 全鏈由下往上收縮",
    '<span class="dn">最高，也最難觀測</span>。這是整條鏈的<strong>最終需求假設</strong>，'
    '且鏈上任何一層的財報都不會提前顯示它']],
  align=["left","left","left"])}</div>
<div class="call call--warn"><div class="call__h">⚠ 本籃子的分散化幻覺</div>
<p>MU、SKHY、MRVL 分屬鏈上<strong>兩個不同層級</strong>（記憶體 vs 加速器／互連），
表面上看是分散的。但沿鏈往下追，它們的需求全部匯聚到<strong>同一個節點</strong>：
雲端業者的資本支出。</p>
<p>2026-07-28 三檔同步下跌 {abs(GAP['MU']):.1f}%／{abs(GAP['SKHY']):.1f}%／{abs(GAP['MRVL']):.1f}%，
是這個共同節點的實證。<strong>層級分散不等於風險分散</strong>——
這是產業鏈地圖相對於「持有不同類股」這種直覺最有價值的修正。</p></div>
</section>""")

    d.append(f"""<section id="signal"><h2>訊號區塊</h2>
{sig_block([("Scope", "AI memory value chain (11 layers)"),
            ("Chokepoints", "3 (EUV / adv. packaging / logic foundry)"),
            ("Basket layers", "2 of 11 (midstream)"), None,
            ("Profit pool", "currently MEMORY + accelerators"),
            ("Migration", "toward power / cooling / inference"), None,
            ("Signal", "NEUTRAL on the basket's layer"),
            ("Confidence", "MEDIUM (structure = judgement)")],
           title="INDUSTRY MAP — SUMMARY")}
<p class="fignote">本框架不產出買賣訊號，而產出<strong>定位判斷</strong>：
本籃子位於一個當前利潤極高、但利潤來源為<strong>暫時性稀缺租金</strong>的層級，
且該租金正被本籃子自身的資本支出所消除。</p>
<div class="chips" style="margin-top:var(--s-32)">
<a class="btn" href="mu.html">MU 完整報告 →</a>
<a class="btn btn--soft" href="workflows.html">工作流 A–G →</a>
<a class="btn btn--soft" href="index.html">← 回展示櫃</a>
</div></section>""")

    body = f'<div class="wrap shell">{toc(tocg)}<div class="doc">{"".join(d)}</div></div>'
    return page("HBM 產業鏈地圖 — 錢在哪一層被收走 | InvestSkill Autopilot 展示櫃",
                "以 industry-map 框架把 AI 記憶體價值鏈畫成 11 層有向圖，標出 3 個瓶頸層、"
                "利潤池遷移方向與 4 個二階投資標的，並定位 MU／SKHY／MRVL 在鏈上的位置。",
                "".join(b) + body, active="supply-chain.html")
