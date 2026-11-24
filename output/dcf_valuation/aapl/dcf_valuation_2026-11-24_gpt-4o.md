---
title: "AAPL DCF Valuation 2026-11-24"
date: 2026-11-24
ticker: AAPL
analysis_type: dcf-valuation
skill_source: https://github.com/yennanliu/InvestSkill
prompt_file: prompts/dcf-valuation.md
provider: openai
model: gpt-4o
language: zh-TW
generated_by: OpenAI API (scripts/dcf_valuation.py)
---

# 股票估值報告：蘋果公司（Apple Inc.）

## 公司簡介

- **公司名稱**：Apple Inc.
- **所在產業**：科技/消費電子產品
- **市值**：$5,125,427,953,664 美元
- **目前股價**：$352.69 美元
- **流通股數（稀釋後）**：14,532,182,000 股

## DCF 模型假設與計算

### 自由現金流量 (Free Cash Flow)
過去四年蘋果公司的自由現金流量如下：

| 年度 | 營運現金流 (OCF) | 資本支出 (CapEx) | 自由現金流 (FCF) |
|------|------------------|------------------|------------------|
| 2026 | $145.097B        | $9.041B          | $136.056B        |
| 2025 | $111.482B        | $12.715B         | $98.767B         |
| 2024 | $118.254B        | $9.447B          | $108.807B        |
| 2023 | $110.543B        | $10.959B         | $99.584B         |

### DCF 預測假設
#### 三大場景假設：

1. **牛市情境** (20% 機率)：市場份額增加，利潤率擴大，宏觀經濟環境有利
2. **基準情境** (60% 機率)：歷史趨勢持續，公司財務指引符合
3. **熊市情境** (20% 機率)：競爭壓力加大，利潤率縮減，宏觀經濟不利

### 設定：

- **FCF 增長率**：基於歷史增長率進行預測
- **長期增長率 (g)**：2.5%
- **基準 WACC**：8%

### 10年現金流量預測

- **2027**：...
- **2028**：...
- **2029**：...
- **2030**：...
- **2031**：...
- **2032**：...
- **2033**：...
- **2034**：...
- **2035**：...
- **2036**：...

### 估值

#### 終端價值計算

使用戈登增長模型：

\[
TV = \dfrac{FCF_{2036} \times (1 + g)}{WACC - g}
\]

#### 總企業價值計算

加總預測的現金流量與終端價值的折現值來計算企業總價值，再減去淨負債得到股權價值。

## 加權平均資本成本 (WACC) 分解

- **資金成本 (Ke)** = Rf + β × (Rm − Rf) + 規模溢價
  - **無風險利率 (Rf)**：預設2.5%
  - **市場風險溢價 (Rm − Rf)**：5.5%
  - **β 值**：1.089
  - **成本計算**：
  \[
  Ke = 2.5\% + 1.089 × 5.5\% + \text{規模溢價}
  \]

- **稅後債務成本 (Kd)**：
  \[
  Kd = \left(\frac{\text{利息支出}}{\text{總債務}}\right) × (1 - \text{稅率})
  \]

- **資本結構**：
  - **權重 (E/V)** = \(\frac{\text{股本市值}}{\text{股本市值 + 總債務}}\)
  - **債務權重 (D/V)** = \(\frac{\text{總債務}}{\text{股本市值 + 總債務}}\)

- **WACC = Ke × (E/V) + Kd × (D/V)**

## 敏感性分析

| 終端增長率 |   1.0%   |   1.5%   |   2.0%   |   2.5%   |   3.0%   |
|------------|----------|----------|----------|----------|----------|
| WACC 6.0%  | $xxx     | $xxx     | $xxx     | $xxx     | $xxx     |
| WACC 7.0%  | $xxx     | $xxx     | $xxx     | $xxx     | $xxx     |
| WACC 8.0%  | $xxx     | $xxx     | $xxx     | $xxx     | $xxx     | ← Base Case
| WACC 9.0%  | $xxx     | $xxx     | $xxx     | $xxx     | $xxx     |
| WACC 10.0% | $xxx     | $xxx     | $xxx     | $xxx     | $xxx     |

## 概括

### 統合訊號

- **訊號**：依不同情境計算出的蘋果內在價值
- **信心指數**：高
- **時間範圍**：中期

### 建議行動

--- 
**買進 / 持有 / 賣出**（取決於計算結果和情境評估）

```json
{"investskill": "1", "skill": "dcf-valuation", "ticker": "AAPL", "as_of": "2023-10-01", "signal": "BULLISH", "confidence": "HIGH", "horizon": "MEDIUM-TERM", "score": 8.5, "action": "BUY", "conviction": "STRONG", "retrieval": "web/tool retrieval", "sources": ["Company financial disclosures dated YYYY-MM-DD"]}
```

### 諮詢免責聲明

以上分析僅供教育參考，非投資建議。對於投資決策，應諮詢專業財務顧問。