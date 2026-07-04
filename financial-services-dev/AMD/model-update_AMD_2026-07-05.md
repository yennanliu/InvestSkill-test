# AMD 財務模型更新 (Model Update)

> 指令：`/model-update AMD` ｜ Skill：`model-update`（equity-research plugin）
> 產出日期：2026-07-05 ｜ 資料為示範用途，非投資建議
>
> 用途：將最新財報、財測與修訂假設「插入」既有財務模型，並記錄變更與對估值的影響。（正式流程會直接更新 Excel 模型；此檔為變更摘要 changelog。）

---

## 一、本次更新的輸入 (New Data Ingested)

| 來源 | 內容 |
|---|---|
| Q1'26 實際 | 營收 $10.3B (+38% YoY)、資料中心 $5.8B、毛利率 53%、非 GAAP EPS $1.37 |
| Q2'26 公司財測 | 營收 ~$11.2B ±$300M (+46% YoY, +9% QoQ)、非 GAAP 毛利率 ~56%、伺服器 CPU +70% YoY |
| 市場預估 | 2026 資料中心 GPU 營收 ~$15.6B；2027 ~$40B；2028 ~$63B |

---

## 二、模型假設變更 (Assumption Changes)

| 假設項 | 舊值（前次） | 新值（本次） | 理由 |
|---|---|---|---|
| FY26 營收成長 | 中高雙位數 | **上修**（Q1/Q2 皆超財測） | 資料中心 AI 需求強於預期 |
| 資料中心分部占比 | — | **上調** | GPU + EPYC 動能 |
| 非 GAAP 毛利率 | ~52–53% | **~54–56%（逐季升）** | 組合改善（資料中心占比↑） |
| 資料中心 GPU 營收（FY26） | 基準 | 對齊 ~$15.6B 市場預估 | MI350 放量 |
| FY27–28 GPU 斜率 | 保守 | 納入 $40B / $63B 情境 | MI400 需求前瞻 |

---

## 三、對每股盈餘與估值的影響 (EPS / Valuation Impact)

- **EPS**：FY26 因營收上修 + 毛利率擴張，非 GAAP EPS 預估上調（Q2 共識已達 ~$1.60）。
- **估值**：現價 ~$519.50、Fwd P/E ~88x。模型顯示——即使 EPS 上修，高倍數仍使估值支撐**高度依賴 FY27–28 GPU 營收兌現**。
- **敏感度**：GPU 營收斜率是估值最大變數；毛利率每 +1pp 對非 GAAP 營業利益具明顯槓桿。

---

## 四、待驗證項目 (To Verify at Next Print — Q2'26, 8/4)

- [ ] 資料中心營收與 AI GPU 全年指引是否較 ~$15.6B 上修。
- [ ] 非 GAAP 毛利率是否達 56% 財測。
- [ ] MI350 放量斜率、MI400 需求前瞻。
- [ ] 伺服器 CPU 是否維持 >70% 增速。
- [ ] 供應（HBM4/CoWoS）是否構成產能上限。

---

## 資料來源 (Sources)

- [AMD Q1 2026 Form 8-K (SEC)](https://www.sec.gov/Archives/edgar/data/0000002488/000000248826000072/q12026991.htm)
- [AMD Beats Q1 2026, Guides $11.2B for Q2 (TradingKey)](https://www.tradingkey.com/analysis/stocks/us-stocks/261863081-amd-earnings-beat-data-center-ai-gpu-guidance-technical-tradingkey)
- [AMD data center GPU revenue forecasts (Silicon Analysts)](https://siliconanalysts.com/analysis/amd-vs-nvidia-ai-gpu-market-share-2026)

> ⚠️ 免責聲明：本文件由 financial-services plugin 之 model-update skill 示範產出，僅供教育目的，不構成投資建議。
