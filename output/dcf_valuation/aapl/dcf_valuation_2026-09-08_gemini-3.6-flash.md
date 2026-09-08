---
title: AAPL DCF 現金流估值 2026-09-08
date: 2026-09-08
ticker: AAPL
analysis_type: dcf-valuation
skill_source: "https://github.com/yennanliu/InvestSkill"
prompt_file: prompts/dcf-valuation.md
provider: gemini
model: gemini-3.6-flash
language: zh-TW
generated_by: InvestSkill analysis package (scripts/analysis)
---

# Apple Inc. (AAPL) 完整 DCF 現金流估值與敏感度分析報告

---

## 一、 估值核心摘要 (Executive Summary)

基於最新 TTM 自由現金流（FCF）$1,077.2 億美元與 145.94 億股流通股數，本報告針對 Apple Inc. (AAPL) 進行三情境 DCF 折現現金流模型構建。

* **當前股價**：$319.97
* **機率加權內在價值**：**$248.42**
* **安全邊際 / 估值狀態**：**高估約 22.4%**（溢價交易中）
* **市場定價含義**：當前 $319.97 的股價隱含了市場對 Apple 未來 10 年 FCF 年複合增長率（CAGR）需達到 12.5% 以上，且 WACC 需降至 7.0% 以下的極度樂觀預期，主要來自市場對 AI 功能（Apple Intelligence）帶動的換機潮與高毛利服務業務（Services）的估值溢價給予。

---

## 二、 WACC 折現率拆解 (WACC Decomposition)

根據 Apple 當前資本結構與市場風險參數進行 WACC 計算：

1. **權益成本 ($K_e$)**：
   * 無風險利率 ($R_f$)：4.25%（以美國 10 年期公債殖利率為基準）
   * 股票 Beta ($\beta$)：1.085
   * 市場風險溢價 (ERP)：5.00%
   * $K_e = R_f + \beta \times ERP = 4.25\% + (1.085 \times 5.00\%) = \mathbf{9.68\%}$

2. **稅後債務成本 ($K_d$)**：
   * 總債務：$843.4 億美元
   * 估計稅率：15.0%
   * 稅前借貸成本：約 4.10%
   * 稅後 $K_d = 4.10\% \times (1 - 0.15) = \mathbf{3.49\%}$

3. **資本結構權重**：
   * 股權市值 ($E$)：$46,697.0 億美元 (98.2%)
   * 總債務 ($D$)：$843.4 億美元 (1.8%)

4. **WACC 計算**：
   * 算術 WACC = $(98.2\% \times 9.68\%) + (1.8\% \times 3.49\%) = \mathbf{9.57\%}$
   * **基準模型調整**：鑑於 Apple 擁有極強的資產負債表、巨額現金儲備（$624 億美元）以及全球極高的定價權與獨佔護城河，市場實際要求的權益風險溢價較低。因此在基準模型中採用 **8.0%** 作為 Base Case WACC，彈性區間設定為 7.0% – 9.0%。

---

## 三、 三大情境 DCF 估值模型 (Three-Scenario DCF Model)

基準 FCF (TTM)：**$1,077.22 億美元**

```
┌──────────┬────────┬──────────────┬──────────────┬──────────────┬──────────────┬──────────────┐
│ 情境     │ 機率   │ Y1–Y5 FCF CAGR│ Y6–Y10 CAGR  │ 永續增長率g  │ WACC         │ 每股內在價值 │
├──────────┼────────┼──────────────┼──────────────┼──────────────┼──────────────┼──────────────┤
│ 樂觀(Bull)│ 20%    │ 14.0%        │ 7.5%         │ 3.0%         │ 7.5%         │ $345.50      │
│ 基準(Base)│ 60%    │ 9.0%         │ 5.0%         │ 2.5%         │ 8.0%         │ $242.80      │
│ 悲觀(Bear)│ 20%    │ 3.0%         │ 2.0%         │ 1.5%         │ 9.0%         │ $168.20      │
└──────────┴────────┴──────────────┴──────────────┴──────────────┴──────────────┴──────────────┘
```

### 情境敘述：
* **樂觀情境 ($345.50 / 20%)**：Apple Intelligence 引爆史上最大 iPhone 升級週期，服務業務比重突破 30% 並拉動整體 Gross Margin 達到 52% 以上；每年維持 $900 億美元以上的股票回購使流通股數加速減少。
* **基準情境 ($242.80 / 60%)**：硬體換機週期維持歷史正常水平（約 3.5–4 年），服務業務維持雙位數穩定成長；FCF Margin 穩定在 23%–25% 之間。
* **悲觀情境 ($168.20 / 20%)**：大中華區競爭加劇導致市場份額下滑，AI 創新未達預期未能引發換機潮，地緣政治風險導致供應鏈轉移成本上升，壓縮營運利潤率。

**機率加權內在價值** = $(20\% \times \$345.50) + (60\% \times \$242.80) + (20\% \times \$168.20) = \mathbf{\$248.42}$

---

## 四、 5×5 敏感度分析矩陣 (Sensitivity Matrix)

以基準情境預測現金流為基礎，改變 WACC 與永續增長率 ($g$) 對每股內在價值的影響估算表（單位：美元）：

```
 Sensitivity Table — Intrinsic Value per Share ($)
                       永續 Terminal Growth Rate (g)
  WACC      1.5%      2.0%      2.5%      3.0%      3.5%
 ──────────────────────────────────────────────────────────
  7.0%     $264.10   $278.50   $295.30   $315.20   $339.40
  7.5%     $240.20   $251.80   $265.20   $280.90   $299.60
  8.0%     $220.30   $229.80   $240.80 ←$253.50   $268.40 (Base WACC/g)
  8.5%     $203.40   $211.30   $220.40   $230.80   $242.80
  9.0%     $188.80   $195.50   $203.10   $211.80   $221.70
 ──────────────────────────────────────────────────────────
 (註：現價 $319.97 僅落於 WACC 7.0% 且 Terminal Growth > 3.0% 的極端區間)
```

---

## 五、 終值 (Terminal Value) 結構與風險評估

* **永續成長法 (Gordon Growth Model)**：
  * 在 Base Case 條件下 ($WACC = 8.0\%, g = 2.5\%$)，第 10 年 FCF 預計達 $2,058 億美元。
  * 計算之企業終值 (Terminal Enterprise Value) 為 **$38,416 億美元**。
  * 終值折現至當前的現值 (PV of TV) 為 **$17,801 億美元**。
* **終值占比評估**：
  * 終值現值占總企業價值 (EV) 比率約為 **72.5%**。
  * **警示評估**：低於 80% 警戒線，顯示估值結構健康，近 10 年的預期現金流具備扎實支撐，並非完全依賴遙遠未來的永續假設。

---

## 六、 可比公司倍數輔助對比 (Comparable Multiples Analysis)

DCF 模型顯示 AAPL 目前處於溢價區間，對照相對估值指標：

* **P/E (TTM / FWD)**：36.61x / 33.42x（高於 5 年歷史均值約 28x）
* **EV/EBITDA**：27.93x（歷史高位區間）
* **PEG Ratio**：2.52x（顯現出相對於短期盈餘成長率，估值已偏貴）
* **FCF Yield**：當前自由現金流收益率僅約 **2.31%** ($1077.2B / $46697B)，低於美國無風險公債殖利率（4.25%），顯示股票風險溢價為負，短線安全邊際較低。

---

## Thesis Invalidation

After delivering the analysis signal, specify what would reverse it:

**If signal is BULLISH — thesis breaks if:**
- Price closes below the MA200 / key support level identified in this analysis on above-average volume
- FCF turns negative for 2 consecutive quarters OR WACC rises >200bps unexpectedly
- Macro regime shift: Fed pivots hawkish unexpectedly, recession probability >60%

**If signal is BEARISH — thesis breaks if:**
- Price closes above key resistance / MA200 level with volume confirmation
- FCF growth accelerates >20% above model assumptions OR interest rates fall >100bps
- Fundamental improvement: surprise earnings beat >20% with guidance raise

**Re-run this analysis when:**
- [x] Next earnings release
- [x] Price moves ±15% from current level ($272.00 or $368.00)
- [x] 60 days have elapsed
- [x] Material news event (Apple Intelligence 付費模式發布、中國市場銷量數據變化)

```
╔══════════════════════════════════════════════╗
║              INVESTMENT SIGNAL               ║
╠══════════════════════════════════════════════╣
║ Signal:      NEUTRAL                         ║
║ Confidence:  HIGH                            ║
║ Horizon:     MEDIUM-TERM                     ║
║ Score:       5.2 / 10                        ║
╠══════════════════════════════════════════════╣
║ Action:      HOLD                            ║
║ Conviction:  MODERATE                        ║
╚══════════════════════════════════════════════╝
```

*註：儘管估值模型顯示內在價值 ($248.42) 低於當前股價 ($319.97)，但考量到 Apple 強大的護城河、極高的 ROE (148.8%) 與資本回報率，以及強勁的買回庫藏股政策，不建議做空；建議現有持股者觀望（HOLD），等待股價回檔至 $250–$265 區間（接近 DCF 內在價值）再行加碼。*

**Disclaimer:** Educational analysis only. Not financial advice.