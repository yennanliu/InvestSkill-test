# AMD 首次覆蓋報告 (Initiating Coverage)

> 指令：`/initiate AMD` ｜ Skill：`initiating-coverage`（equity-research plugin）
> 產出日期：2026-07-05 ｜ 資料為示範用途，非投資建議
>
> ⚠️ **關於此檔**：完整 `initiating-coverage` skill 為 **5 階段、逐步執行** 的機構級工作流，交付物包含：(1) 6–8K 字公司研究 → (2) Excel 財務模型（6 分頁）→ (3) 估值分析 + 目標價 → (4) 25–35 張圖表 → (5) 30–50 頁 DOCX 報告。本檔為 **markdown 濃縮示範**，整合各階段要點；正式流程請於 Claude Code 內以 `/initiate AMD` 逐一執行 Task 1–5。

---

## 投資摘要 (Investment Summary)

| 項目 | 內容 |
|---|---|
| 評級（示範） | **買進 (BUY) — 高信念、估值敏感** |
| 現價 | ~$519.50 ｜ 市值 ~$845B |
| 投資期間 | 中長期（12–24 個月） |
| 核心邏輯 | AI 加速器份額成長 + EPYC 現金牛 + 毛利率擴張；估值極度延伸為主要風險 |

---

## 1. 公司概覽 (Company Research — Task 1 摘要)

**業務**：AMD 為全球高效能運算與繪圖處理器領導者之一，四大分部：
- **資料中心 (Data Center)**：EPYC 伺服器 CPU + Instinct AI GPU（MI300/MI350/MI400 系列）。
- **客戶端 (Client)**：Ryzen PC 處理器。
- **遊戲 (Gaming)**：Radeon GPU + 主機半客製晶片。
- **嵌入式 (Embedded)**：Xilinx（FPGA/自適應運算，通訊、工業、汽車）。

**競爭定位**：在 x86 伺服器 CPU 對 Intel 持續奪取份額；在 AI GPU 為 NVIDIA 之外唯一具規模的替代方案。護城河來自 chiplet 先進封裝設計、與台積電的製程夥伴關係、以及逐步成熟的 ROCm 軟體生態。

**管理層**：CEO Lisa Su 帶領的十年轉型（從瀕危到 AI 晶片挑戰者）具高度執行力與市場信任。

---

## 2. 財務模型重點 (Financial Modeling — Task 2 摘要)

| 指標 | Q1'26 | Q2'26 財測 | 趨勢 |
|---|---|---|---|
| 營收 | $10.3B (+38% YoY) | ~$11.2B ±$300M (+46% YoY) | 加速 |
| 資料中心 | $5.8B | 續強 | 核心引擎 |
| 毛利率（非 GAAP） | 53% | ~56% | 結構性擴張 |
| 非 GAAP EPS | $1.37 | 共識 ~$1.60 | 成長 |

**分部營收動能**：資料中心（AI GPU + EPYC）為未來 3 年主要成長；客戶端／遊戲循環性較高；嵌入式回溫。
**GPU 營收路徑（市場預估）**：2026 ~$15.6B → 2027 ~$40B → 2028 ~$63B。

---

## 3. 估值分析 (Valuation — Task 3 摘要)

- **本益比法**：Fwd P/E ~88x，遠高於半導體同業；估值完全建立在 AI GPU 份額成長曲線的兌現。
- **成長對估值**：若 2027–2028 資料中心 GPU 營收如期放量，高倍數可被高增速消化；反之則面臨估值壓縮。
- **目標價區間（分析師）**：高度分歧 $263 ~ $478，部分已落後股價急漲；反映市場定價尚未收斂。
- **示範性目標價框架**：多方情境繫於 GPU 份額 >15% + 毛利率 56%+；空方情境繫於執行落差或 NVDA 競爭壓制。

---

## 4. 關鍵圖表清單 (Chart Generation — Task 4 應產出項)

正式流程於此階段產出 25–35 張圖，重點包含：
- 分部營收堆疊（資料中心 / 客戶端 / 遊戲 / 嵌入式）
- 毛利率趨勢（50% → 53% → 56%）
- 資料中心 GPU 營收預估曲線（2026–2028）
- AI 加速器市佔演變（AMD vs. NVDA）
- 估值敏感度熱圖（成長率 × 倍數）
- 估值足球場圖 (football field)

---

## 5. 關鍵風險 (Risk Assessment)

1. 估值風險（Fwd P/E ~88x，對完美執行定價）。
2. NVIDIA 競爭與 CUDA 生態壁壘。
3. AI GPU 放量與 HBM4/CoWoS 供應瓶頸。
4. 客戶集中（少數超大廠）。
5. PC／遊戲／嵌入式的景氣循環。

---

## 結論

AMD 具備「AI 加速器份額成長 + 伺服器 CPU 現金牛 + 毛利率擴張」的優質成長組合，是 AI 基礎設施主題中除 NVDA 外最重要的標的。**評級：買進，但屬估值敏感、高波動部位**，建議分批布局並以季度財報重新檢視執行進度。

---

## 資料來源 (Sources)

- [AMD Q1 2026 Earnings Slides (SEC 8-K)](https://www.sec.gov/Archives/edgar/data/0000002488/000000248826000014/amdq425earningsslidesfin.htm)
- [AMD forecasts data center growth to 2030 (Data Center Dynamics)](https://www.datacenterdynamics.com/en/news/amd-posts-q1-2026-data-center-revenue-of-58bn-forecasts-120bn-server-cpu-income-by-2030/)
- [AMD vs NVIDIA AI GPU Market Share 2026 (Silicon Analysts)](https://siliconanalysts.com/analysis/amd-vs-nvidia-ai-gpu-market-share-2026)
- [AMD Stock Forecast & Price Target (Public.com)](https://public.com/stocks/amd/forecast-price-target)

> ⚠️ 免責聲明：本文件為 initiating-coverage skill 之 markdown 示範，僅供教育目的，不構成投資建議。正式機構級交付物（DOCX/Excel/圖表）需於 Claude Code 內逐階段執行。
