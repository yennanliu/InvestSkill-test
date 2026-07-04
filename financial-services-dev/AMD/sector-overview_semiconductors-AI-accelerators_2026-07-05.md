# 產業研究：半導體 — AI 加速器 (AI Accelerators)

> 指令：`/sector 半導體 AI 加速器` ｜ Skill：`sector-overview`（equity-research plugin）
> 產出日期：2026-07-05 ｜ 角度：AI 運算硬體 + AMD 定位 ｜ 資料為示範用途，非投資建議

---

## 一、產業範圍界定

- **次產業**：資料中心 AI 加速器（GPU / 客製 ASIC）+ 伺服器 CPU + 先進封裝／HBM 供應鏈。
- **目的**：AMD 首次覆蓋的產業背景，兼作 AI 硬體主題研究。
- **範圍**：以美股上市為主（AMD、NVDA），涵蓋供應鏈（台積電、HBM）與超大廠自研 ASIC。

---

## 二、市場概覽 (Market Overview)

### 市場規模與成長
- 全球半導體市場 2026 上看約 **$1.3T**；資料中心 AI 加速器為成長最快的次領域。
- AMD 資料中心 GPU 營收路徑（市場預估）：**2026 ~$15.6B → 2027 ~$40.6B → 2028 ~$63B**，顯示 AI 加速器的爆發性成長。

### 產業結構
- **價值鏈**：EDA/IP → 晶圓代工（台積電先進製程）→ 先進封裝 (CoWoS) + HBM（記憶體）→ 加速器設計（NVDA/AMD/自研 ASIC）→ 雲端與企業部署。
- **獲利集中點**：目前價值高度集中於「加速器設計 + 先進封裝／HBM 供應」；產能（CoWoS、HBM4）是全產業瓶頸。
- **進入障礙**：先進製程與封裝資本密集、軟體生態（CUDA）、系統級整合能力、與代工／記憶體的產能綁定。

### 關鍵趨勢與驅動
1. **訓練 → 推論轉移**：推論工作負載放量，對「性價比 / TCO」與供應多元化的需求上升，利於 AMD。
2. **供應商多元化**：超大廠為降低對 NVDA 依賴與成本，扶植 AMD 作為第二來源，並發展自研 ASIC。
3. **先進封裝與 HBM 為瓶頸**：CoWoS、HBM4 產能決定實際出貨上限。
4. **主權 AI**：各國自建算力，擴大加速器 TAM。
5. **軟體生態競賽**：CUDA vs. ROCm，生態成熟度是份額移轉的關鍵變數。

---

## 三、競爭地景 (Competitive Landscape)

| 公司 | 定位 | 差異化 | AI 加速器份額 | 估值特徵 |
|---|---|---|---|---|
| **NVIDIA (NVDA)** | AI GPU 龍頭 | CUDA 生態、系統級 (NVLink/機櫃)、龍頭規模 | **~75–80%** | 高，但獲利支撐強 |
| **AMD** | 唯一具規模的挑戰者 | chiplet 設計、MI350/MI400、EPYC 綜效、性價比 | ~9%（2025）→ **>15%（2026E）** | 極高（Fwd P/E ~88x） |
| 超大廠自研 ASIC | 內部工作負載最佳化 | 客製化、成本控制 | 逐步上升 | （多為雲廠內部） |
| 供應鏈（台積電、HBM 業者） | 產能瓶頸持有者 | 先進製程／封裝／HBM | — | 受惠全產業 |

### 競爭動態
- **NVDA 護城河**：CUDA 軟體 + 系統級整合仍是最強壁壘；但份額由 2024 峰值 ~87% 緩降至 2026 ~75%。
- **AMD 切入點**：以性價比 / TCO、推論場景、供應多元化需求奪取份額；ROCm 生態成熟度是能否加速的關鍵。
- **格局**：短中期為「龍頭主導 + 挑戰者份額成長」而非贏者全拿；供應鏈產能是共同天花板。

---

## 四、估值脈絡 (Valuation Context)

- AI 加速器設計商估值普遍偏高，反映爆發性成長預期；AMD Fwd P/E ~88x、NVDA 亦處高檔。
- 溢價驅動：GPU 營收增速、份額移轉、毛利率。溢價風險：增速拐點、供應瓶頸、競爭壓制。
- 供應鏈（代工／HBM）提供較低波動、受惠全產業的曝險方式。

---

## 五、投資含意 (Investment Implications)

1. **龍頭曝險**：NVDA — 生態護城河 + 規模，AI 加速器核心持股。
2. **份額成長／高 beta**：AMD — 挑戰者份額故事，高增速高估值，需嚴格風控。
3. **供應鏈受惠**：台積電、HBM 記憶體業者 — 產能瓶頸持有者，受惠全產業放量。
4. **需求風向球**：雲端 Capex（MSFT/AMZN/GOOGL）指引領先反映加速器訂單能見度。

**核心辯論**：多方認為 AI 資本支出仍在早期、份額多元化利於 AMD；空方認為估值已極度反映、NVDA 生態難撼、供應瓶頸限制實際成長。

---

## 六、後續建議 (Next Steps)

- 對 AMD、NVDA 建立完整模型與估值（`/initiate`、`/model-update`）。
- 以 `/catalysts` 追蹤財報與產品發表（見同資料夾 `catalysts_2026-07-05.md`）。
- 以 `/screen` 尋找供應鏈第二層受惠標的（見 `screen_AI-semiconductors_2026-07-05.md`）。

---

## 資料來源 (Sources)

- [AMD vs NVIDIA AI GPU Market Share 2026 (Silicon Analysts)](https://siliconanalysts.com/analysis/amd-vs-nvidia-ai-gpu-market-share-2026)
- [NVIDIA AI Accelerator Market Share 2024–2026 (Silicon Analysts)](https://siliconanalysts.com/analysis/nvidia-ai-accelerator-market-share-2024-2026)
- [AI Chip Stocks Investment July 2026: NVDA vs AMD (Intellectia)](https://intellectia.ai/blog/ai-chip-stocks-investment-july-2026)
- [AMD data center revenue & 2030 outlook (Data Center Dynamics)](https://www.datacenterdynamics.com/en/news/amd-posts-q1-2026-data-center-revenue-of-58bn-forecasts-120bn-server-cpu-income-by-2030/)

> ⚠️ 免責聲明：本文件由 financial-services plugin 之 sector-overview skill 示範產出，僅供教育目的，不構成投資建議。市場規模估計來源互異，請查證最新數據。
