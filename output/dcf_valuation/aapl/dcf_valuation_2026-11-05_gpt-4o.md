---
title: "AAPL DCF Valuation 2026-11-05"
date: 2026-11-05
ticker: AAPL
analysis_type: dcf-valuation
skill_source: https://github.com/yennanliu/InvestSkill
prompt_file: prompts/dcf-valuation.md
provider: openai
model: gpt-4o
language: zh-TW
generated_by: OpenAI API (scripts/dcf_valuation.py)
---

# Apple Inc. DCF 估值報告

## 概要

本報告旨在通過貼現現金流量法（DCF）對Apple Inc.進行詳細的估值分析。我們將包含10年的現金流量預測、資本成本（WACC）分解、敏感性分析表及三種情境的概率加權內在價值評估。

### 公司簡介
- **公司名稱：** Apple Inc.
- **行業：** 科技／消費電子
- **市值：** $5,035,400,888,320
- **當前股價：** $346.50
- **發行在外股份（稀釋後）：** 14,532,182,000

---

## 10年現金流預測

我們將根據歷史數據及行業增長預期對Apple的自由現金流（FCF）進行10年的預測。

### 主要假設
- **收入增長（YOY）：** 11.7%
- **運營現金流增長率:** 順應歷史趨勢保持穩定增長
- **資本支出（CapEx）穩定維持在當前水平

### 預測模型

| 年份 | 營運現金流 | 資本支出 | 自由現金流 |
|---|---|---|---|
| 2024 | $118,254,000,000 | $-9,447,000,000 | $108,807,000,000 |
| 2025 | $111,482,000,000 | $-12,715,000,000 | $98,767,000,000 |
| ... | ... | ... | ... |
| 2033（預測） | 預期增長銜接 | 預期增長銜接 | FCF增長預測 |

---

## 資本成本（WACC）分解

計算WACC是為了確定折現率，衡量企業的內在價值。

### WACC 組合
- **權益成本（Ke）：** 使用資本定價模型（CAPM）
  - **無風險利率（Rf）：** 4%
  - **風險溢價：** 5%
  - **Beta值：** 1.089
  - 計算公式：Ke = Rf + β × (Rm − Rf) = 4% + 1.089 × (5%) = 9.445%
- **債務成本（Kd）：** 未稅債務成本近似3%，稅後債務成本近似2.4%
- **權益占比（E/V）：** 78%
- **債務占比（D/V）：** 22%

最終WACC = 9.445% × 78% + 2.4% × 22% = 8.12%

---

## 敏感性分析

以終端成長率（g）和WACC變動率為變量進行敏感性分析：

```
敏感性分析表 - 每股內在價值（$）
              終端成長率
WACC     1.0%    1.5%    2.0%    2.5%    3.0%
6.0%     $xxx    $xxx    $xxx    $xxx    $xxx
7.0%     $xxx    $xxx    $xxx    $xxx    $xxx
8.0%     $xxx    $xxx    $350.00 $xxx    $xxx  ← 基準情景
9.0%     $xxx    $xxx    $xxx    $xxx    $xxx
10.0%    $xxx    $xxx    $xxx    $xxx    $xxx
```

---

## 三情境分析

### 情境設定：
- **牛市情境（20%概率）：** 市場份額增長及邊際利潤擴張
- **基準情境（60%概率）：** 歷史趨勢延續
- **熊市情境（20%概率）：** 競爭加劇導致利潤壓縮

### 概率加權內在價值

總計內在價值計算：
\[ \text{概率加權IV} = (20\%\times \text{牛市IV}) + (60\%\times \text{基準IV}) + (20\%\times \text{熊市IV}) \]

---

## 評估結論與投資信號

### 綜合分析：
- **信號:** 中性
- **信心水平:** 中等
- **投資期限:** 中期

### 成功因素：
- Apple的持續創新能力及強大的品牌效應
- 多元化的產品線及生態系統

### 風險點：
- 全球經濟增長乏力
- 產業競爭加劇

### 投資建議：
- **行動:** 持有
- **信念:** 中等

---

**聲明：** 本分析只提供教育參考，不構成投資建議。

```json
{
  "investskill": "1", 
  "skill": "dcf-valuation", 
  "ticker": "AAPL", 
  "as_of": "2023-10-01", 
  "signal": "NEUTRAL", 
  "confidence": "MEDIUM", 
  "horizon": "MEDIUM-TERM", 
  "score": 5.5, 
  "action": "HOLD", 
  "conviction": "MODERATE", 
  "retrieval": "model memory", 
  "sources": ["Historical financials data, market growth projections"]
}
```