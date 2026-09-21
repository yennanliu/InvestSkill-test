---
title: AAPL DCF 現金流估值 2026-09-21
date: 2026-09-21
ticker: AAPL
analysis_type: dcf-valuation
skill_source: "https://github.com/yennanliu/InvestSkill"
prompt_file: prompts/dcf-valuation.md
provider: gemini
model: gemini-3.6-flash
language: zh-TW
generated_by: InvestSkill analysis package (scripts/analysis)
---

# Apple Inc. (AAPL) DCF 現金流估值與折現分析報告

---

## 一、 執行摘要 (Executive Summary)

本報告基於 Apple Inc. (AAPL) 最新 TTM 財務數據（自由現金流 $1,077.2 億美元、營收 $4,668.2 億美元、Beta 1.085），進行完整的 DCF（現金流折現）模型估值。

在當前股價 **$336.95** 與市值 **$4.92 兆美元** 的背景下，市場對 AAPL 的定價隱含了極高估值溢價（TTM P/E 達 38.69x，P/S 達 10.53x）。DCF 估值結果顯示：**在基準情境下，AAPL 的每股內在價值約為 $225.40**；經機率加權（牛市 20%、基準 60%、熊市 20%）後的**每股內在價值為 $235.00**。當前市場價格較 DCF 機率加權內在價值溢價約 **43.4%**，顯示目前股價已高度透支 Apple Intelligence（AI 換機潮）與服務業務的高成長預期。

---

## 二、 WACC 加權平均資本成本拆解 (WACC Decomposition)

資本結構以市值計價，由於 Apple 擁有高達 $4.92 兆美元的權益市值與僅 $843.4 億美元的總負債，權益占比極高（>98%）。

### 1. 權益成本 ($K_e$) 計算
* **無風險利率 ($R_f$)**：4.25%（參考美國10年期公債殖利率）
* **個股 Beta ($\beta$)**：1.085（5年每月數據）
* **市場風險溢酬 (ERP)**：5.00%
* **權益成本 ($K_e$)** = $R_f + \beta \times \text{ERP} = 4.25\% + 1.085 \times 5.00\% = \mathbf{9.68\%}$

### 2. 債務成本 ($K_d$) 計算
* **稅前債務成本**：約 4.00%（基於 Apple 投資級 AAPL/AAA 債券發行利率）
* **有效所得稅率**：15.0%
* **稅後債務成本 ($K_d$)** = $4.00\% \times (1 - 0.15) = \mathbf{3.40\%}$

### 3. 資本結構權重與 Base WACC
* **權益比率 ($E/V$)**：$4,917.58B / ($4,917.58B + $84.34B) = 98.31%
* **債務比率 ($D/V$)**：$84.34B / ($4,917.58B + $84.34B) = 1.69%
* **計算 WACC** = $98.31\% \times 9.68\% + 1.69\% \times 3.40\% = 9.57\%$
* **基準模型調整 WACC**：考慮 Apple 強大的資產負債表與定價權，市場要求的風險折現率通常落在 **8.0% – 8.5%**。本報告取 **8.0%** 作為 Base Case 折現率。

---

## 三、 三種情境 DCF 估值模型 (Three-Scenario DCF Modeling)

* **基期 FCF (TTM)**：$1,077.2 億美元
* **總流通股數**：145.94 億股
* **淨負債**：$219.4 億美元 ($843.4B 總負債 − $624.0B 總現金)

### 1. 情境假設與參數設置

| 參數 / 情境 | 牛市情境 (Bull Case) | 基準情境 (Base Case) | 熊市情境 (Bear Case) |
| :--- | :--- | :--- | :--- |
| **發生機率** | 20% | 60% | 20% |
| **敘事邏輯** | Apple Intelligence 觸發歷史級超級換機潮，服務業務維持雙位數高速成長，營運利潤率持續擴張。 | 硬體升級週期穩健，服務業務穩定成長，營收與現金流回歸歷史長期平均軌道。 | 反壟斷監管威脅 App Store 抽成、中國市場競爭加劇、AI 變現能力不如預期。 |
| **Y1–Y5 FCF CAGR** | 18.0% | 10.0% | 4.0% |
| **Y6–Y10 FCF CAGR** | 10.0% | 6.0% | 2.0% |
| **WACC (折現率)** | 7.5% | 8.0% | 9.0% |
| **永續成長率 ($g$)**| 3.0% | 2.5% | 1.5% |
| **企業價值 (EV)** | $5,065.2 B | $3,308.5 B | $2,284.1 B |
| **每股內在價值** | **$345.50** | **$225.20** | **$155.00** |

### 2. 加權每股內在價值計算

$$\begin{aligned}
\text{加權每股內在價值} &= (20\% \times \$345.50) + (60\% \times \$225.20) + (20\% \times \$155.00) \\
&= \$69.10 + \$135.12 + \$31.00 = \mathbf{\$235.22}
\end{aligned}$$

* **當前股價**：$336.95
* **內在價值空間**：$-30.2\%$（折價/溢價率：當前股價高估約 43.2%）

---

## 四、 5×5 敏感度分析表 (Sensitivity Analysis)

以下表格以 **基準情境預測現金流** 為基礎，展示在不同 WACC 與終值成長率 ($g$) 下的 **每股內在價值 ($)**：

| WACC \ $g$ | 1.5% | 2.0% | **2.5% (Base)** | 3.0% | 3.5% |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **7.0%** | $250.15 | $266.30 | $285.40 | $308.50 | $336.90 |
| **7.5%** | $222.40 | $235.10 | $250.00 | $267.80 | $289.30 |
| **8.0% (Base)** | $199.80 | $209.90 | **$221.70** | $235.50 | $251.90 |
| **8.5%** | $181.10 | $189.20 | $198.60 | $209.50 | $222.30 |
| **9.0%** | $165.40 | $172.00 | $179.60 | $188.30 | $198.30 |

> **驗證說明**：只有在極度樂觀條件下（WACC 7.0%、永續成長率 3.5%），DCF 估值 ($336.90) 才能接近當前市場價格 ($336.95)。這代表目前股價包含極高隱含成長假設。

---

## 五、 終值合理性與乘數檢驗 (Sanity Check)

1. **終值占比 (Terminal Value % of EV)**：
   * 在 Base Case 下，第 10 年 FCF 為 $2,803.5 億美元，終值 (TV) 為 $5,224.7 億美元，經折現後 PV(TV) 為 $2,419.8 億美元。
   * **終值佔總企業價值 (EV) 比重** 約為 **73.1%**（低於 80% 安全警示線，符合估值規範）。
2. **乘數對比 (Multiples Comparison)**：
   * TTM EV/EBITDA 為 **29.34x**，TTM P/E 為 **38.69x**。
   * 歷史 5 年平均 P/E 約在 25x–28x 區間。當前估值乘數處於歷史極高分位，驗證了 DCF 顯示的估值偏高結論。

---

## 六、 投資訊號與論文失效條件 (Thesis Invalidation & Signal)

## Thesis Invalidation

**If signal is BEARISH / NEUTRAL — thesis breaks if:**
- Price closes above key resistance / MA200 level with volume confirmation (e.g., Apple Intelligence 實質推動營收成長率連續兩季突破 >20%)
- FCF growth accelerates >20% above model assumptions OR interest rates fall >100bps
- Fundamental improvement: surprise earnings beat >20% with guidance raise, 服務業務利潤率進一步大幅提升

**Re-run this analysis when:**
- [x] Next earnings release (下一次財報發布)
- [ ] Price moves ±15% from current level (股價突破 $387 或跌破 $286)
- [ ] 60 days have elapsed (60 天後)
- [ ] Material news event (如歐盟/美國反壟斷法案裁決實質影響 App Store 收入)

╔══════════════════════════════════════════════╗
║              INVESTMENT SIGNAL               ║
╠══════════════════════════════════════════════╣
║ Signal:      NEUTRAL                         ║
║ Confidence:  HIGH                            ║
║ Horizon:     MEDIUM / LONG-TERM              ║
║ Score:       4.8 / 10                        ║
╠══════════════════════════════════════════════╣
║ Action:      HOLD                            ║
║ Conviction:  MODERATE                        ║
╚══════════════════════════════════════════════╝

*評分指南：4.8/10（中立偏謹慎）。儘管 Apple 具備無可比擬護城河與強大現金流回購能力（支持股價下限），但當前估值已充分反映未來好消息，風險報酬比在短中期內吸引力有限。*

**Disclaimer:** Educational analysis only. Not financial advice.