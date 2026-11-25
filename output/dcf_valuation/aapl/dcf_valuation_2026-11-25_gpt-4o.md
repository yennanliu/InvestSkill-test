---
title: "AAPL DCF Valuation 2026-11-25"
date: 2026-11-25
ticker: AAPL
analysis_type: dcf-valuation
skill_source: https://github.com/yennanliu/InvestSkill
prompt_file: prompts/dcf-valuation.md
provider: openai
model: gpt-4o
language: zh-TW
generated_by: OpenAI API (scripts/dcf_valuation.py)
---

# 蘋果公司（AAPL） DCF 估值報告

## 公司概況

- **公司名稱**: 蘋果公司（Apple Inc.）
- **產業/部門**: 科技/消費電子產品
- **市值**: $5,144,102,043,648
- **目前股價**: $353.98
- **已發行股數（稀釋後）**: 14,532,182,000股

---

## 折現現金流（DCF）分析

### 分析方法概述

折現現金流法（DCF）是一種以預測未來現金流並將其折現後計算企業現值的估值技術。此方法主要基於企業的自由現金流（FCF）、加權平均資本成本（WACC）與長期增長率。

### 加權平均資本成本（WACC）計算

#### 公式
\[ WACC = Ke \times (E/V) + Kd \times (D/V) \]

#### WACC 參數解析：

- **股本成本（Ke）**: \[ Ke = Rf + β \times (Rm − Rf) + Size \]  
  - \[ Rf \] = 無風險利率
  - \[ β \] = 貝他值 (5Y monthly 為1.089)
  - 市場風險溢酬（Rm − Rf）= 使用歷史數據預測
  - 規模溢酬 = 使用小型企業的溢酬

- **債務成本（Kd）**: \[ (Interest Expense / Total Debt) \times (1 - Tax Rate) \]
  - 利息支出和稅率暫未明確，假設使用產業均值

- **股權比率（E/V）**及**債務比率（D/V）**:
  - \[ E/V = Equity Market Cap / (Equity Market Cap + Total Debt) \]
  - \[ D/V = Total Debt / (Equity Market Cap + Total Debt) \]

### 現金流預測（10年）

以蘋果的歷史收入增長率和未來預測來推算下面幾年的自由現金流。

#### 自由現金流(FCF)計算模板:

``` 
| 年份 | 2024 | 2025 | 2026 | ... | 2033 |
| --- | --- | --- | --- | --- | --- |
| FCF | 公式: (OCF - CapEx) * Growth Rate |
```

...

### 終值計算

#### 戈登增長模型 (Gordon Growth Model): 
\[ TV = FCF_{10} \times (1 + g) / (WACC − g) \]

注意：終值不應佔總企業價值的80％以上。如果超過，需審查增長率和折現率。

---

## 敏感性分析

下表顯示了於不同折現率（WACC）及終值增長率（g）下的每股內在價值：

```
敏感性分析表 --- 每股內在價值（美元）
              終值增長率
WACC         1.0%    1.5%    2.0%    2.5%    3.0%
6.0%         $XXX    $XXX    $XXX    $XXX    $XXX
7.0%         $XXX    $XXX    $XXX    $XXX    $XXX
8.0%　(Base Case) $XXX    $XXX    $XXX    $XXX    $XXX
9.0%         $XXX    $XXX    $XXX    $XXX    $XXX
10.0%        $XXX    $XXX    $XXX    $XXX    $XXX
```

---

## 場景分析與潛在價值風險

### 場景描述

- **牛市（Bull）:** 市場份額增加，邊際擴張，宏觀經濟利好影響。
- **基準（Base）:** 歷史趨勢延續，按公司指引執行。
- **熊市（Bear）:** 競爭壓力增大，利潤空間收縮，宏觀經濟不利。

\[
概率加權內在價值 = (20\% \times Bull IV) + (60\% \times Base IV) + (20\% \times Bear IV)
\]

---

## 投資信號

```                                                  
╔══════════════════════════════════════════════╗
║              投資信號報告                                ║
╠══════════════════════════════════════════════╣
║ 信號:      BULLISH / NEUTRAL / BEARISH      ║
║ 信心:      HIGH / MEDIUM / LOW              ║
║ 時間範圍:  SHORT / MEDIUM / LONG-TERM       ║
║ 評分:      X.X / 10                         ║
╠══════════════════════════════════════════════╣
║ 行動:      BUY / HOLD / SELL                ║
║ 信念:      STRONG / MODERATE / WEAK         ║
╚══════════════════════════════════════════════╝
```

### 重新分析條件

- [ ] 下一季度財務報告發布
- [ ] 股價變動超過±15%
- [ ] 60天周期
- [ ] 發生重大新聞事件（如並購、領導層變化、監管決定）

---

**免責聲明**：本分析僅供教育用途，非財務建議。