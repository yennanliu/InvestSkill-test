---
title: "AAPL DCF Valuation 2026-10-30"
date: 2026-10-30
ticker: AAPL
analysis_type: dcf-valuation
skill_source: https://github.com/yennanliu/InvestSkill
prompt_file: prompts/dcf-valuation.md
provider: openai
model: gpt-4o
language: zh-TW
generated_by: OpenAI API (scripts/dcf_valuation.py)
---

# 企業估值報告：蘋果公司 (Apple Inc.)

## 目錄

1. 概述
2. 財務預測
   - 預估自由現金流 (自由現金流, FCF)
   - 未來十年預測
3. 折現現金流(DCF)估值模型
   - 加權平均資本成本 (WACC)
   - 敏感性分析
   - 終端價值
   - 內部價值 (Intrinsic Value)
4. 報告結論
   - 投資結論
   - 風險與不確定因素
   - 假設推翻條件

---

## 1. 概述

蘋果公司（Apple Inc., AAPL）為全球領先的科技公司，專注於消費性電子產品、電腦軟體與線上服務的設計、製造和行銷。本報告將運用折現現金流(DCF)模型估算蘋果公司的內在價值。

---

## 2. 財務預測

### 預估自由現金流 (自由現金流, FCF)

以過去的營運現金流與資本支出來推估未來十年之自由現金流增長。

### 未來十年預測

**預測期：2024-2033 涉及各項財務參數的預測**

- **總營收增長率**：基於過去四年的增長趨勢和行業預期。
- **營業利潤率**：保持穩定於歷史數據的區間。
- **自由現金流增長率**：根據淨利潤和資本支出推算。

---

## 3. 折現現金流(DCF)估值模型

### 加權平均資本成本 (WACC)

WACC的計算如下：

\[ \text{WACC} = K_e \times \left(\frac{E}{V}\right) + K_d \times \left(\frac{D}{V}\right) \]

其中：

- \( K_e \)：股本成本，以資本資產定價模型(CAPM)估計 \( K_e = R_f + \beta \times (R_m - R_f) \)
- \( \beta \)：1.069 (5年期）
- \( R_f \)：無風險利率，約為2.5%
- \( R_m \)：市場期望報酬率，約為8%
- 核心引數
  - 股權比率：\( \frac{E}{V} \) 
  - 債權比率：\( \frac{D}{V} \)
- \( K_d \)：稅後債務成本，以公司持有之債務與現金流算出。

### 敏感性分析

以不同的WACC和終端增長率進行敏感性分析，確定DCF估值的敏感性。

#### 5×5敏感性表格

|                | 終端增長率 |                   |
|:--------------:|:---------:|:-----------------:|
| **WACC**       | 1.0%      | 1.5%  | 2.0%  | 2.5%  | 3.0%  |
| **6.0%**       | $XXX      | $XXX  | $XXX  | $XXX  | $XXX  |
| **7.0%**       | $XXX      | $XXX  | $XXX  | $XXX  | $XXX  |
| **8.0%**       | $XXX      | $XXX  | $XXX  | $XXX  | $XXX  | ← Base Case
| **9.0%**       | $XXX      | $XXX  | $XXX  | $XXX  | $XXX  |
| **10.0%**      | $XXX      | $XXX  | $XXX  | $XXX  | $XXX  |

### 終端價值

採用 Gordon Growth Model 計算公司終端價值：

\[ \text{TV} = \frac{\text{FCF}_{10} \times (1 + g)}{\text{WACC} - g} \]

### 內在價值 (Intrinsic Value)

運用三個預測情景(Bull, Base, Bear)進行加權計算，得出公司股價目標：

\[
\text{概率加權內在價值} = (0.2 \times \text{Bull IV}) + (0.6 \times \text{Base IV}) + (0.2 \times \text{Bear IV})
\]

---

## 4. 報告結論

### 投資結論

**信號分析：**

|            |                                            |
|:----------:|:-----------------------------------------:|
| **Signal** | BULLISH / NEUTRAL / BEARISH                |
| **Confidence** | HIGH / MEDIUM / LOW                    |
| **Horizon** | SHORT / MEDIUM / LONG-TERM                |
| **Score** | X.X / 10                                    |
| **Action** | BUY / HOLD / SELL                          |
| **Conviction** | STRONG / MODERATE / WEAK               |

### 風險與不確定因素

- 經濟衰退的風險
- 生產及供應鏈中斷
- 技術領域中的快速創新與競爭

### 假設推翻條件

- **若信號為BULLISH**：
  - 自由現金流連續兩個季度為負數，或WACC意外上升200bps以上
  - [另一特定驅動因素]

- **若信號為BEARISH**：
  - 自由現金流增長高於模型假設20%以上，或利率下降100bps以上
  - [另一特定驅動因素]

**請於以下情境重新評估：**

- 下一次財報發布
- 價格變動 ±15%以上
- 60天內未更新
- 重大事件（收購、管理層變更、重大法律變更）

---

**特別聲明**：此報告僅用作教學分析，並不構成任何投資建議。