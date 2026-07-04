# Financial Services Plugin — 範例輸出

本資料夾示範 Anthropic **[financial-services](https://github.com/anthropics/financial-services)** plugin 的使用。

## 安裝方式

```bash
# 1. 加入 marketplace
claude plugin marketplace add anthropics/financial-services

# 2. 安裝 equity-research（股票研究）plugin
claude plugin install equity-research@claude-for-financial-services

# 3. 重啟 Claude Code 後即可使用下列 slash commands
```

安裝後可用的 `equity-research` 指令：

| 指令 | 對應 skill | 用途 |
|---|---|---|
| `/earnings-preview [ticker]` | earnings-preview | 財報前瞻：情境分析與關鍵數據預測 |
| `/earnings [ticker]` | earnings-analysis | 財報後更新：秒級產出季度更新報告 |
| `/initiate [ticker]` | initiating-coverage | 首次覆蓋報告（5 階段機構級工作流） |
| `/model-update [ticker]` | model-update | 更新財務模型 |
| `/thesis [ticker]` | thesis-tracker | 建立／維護投資論點 |
| `/morning-note` | morning-note | 晨會筆記 |
| `/sector [industry]` | sector-overview | 產業研究 |
| `/screen [criteria]` | idea-generation | 選股篩選／投資點子 |
| `/catalysts [timeframe]` | catalyst-calendar | 催化事件追蹤 |

> 完整 marketplace 另含 investment-banking、private-equity、wealth-management、financial-analysis、fund-admin、operations 等垂直 plugin，以及多個 agent plugin（pitch-agent、model-builder…）。

## 本次示範產出（繁體中文）

### Palantir Technologies (PLTR)

| 檔案 | 對應指令 | 說明 |
|---|---|---|
| [`earnings-preview_PLTR_2026-07-05.md`](./earnings-preview_PLTR_2026-07-05.md) | `/earnings-preview PLTR` | 2026 Q2 財報前瞻 + 多空情境 |
| [`thesis_PLTR_2026-07-05.md`](./thesis_PLTR_2026-07-05.md) | `/thesis PLTR` | 投資論點與追蹤紀錄 |
| [`sector-overview_AI-analytics-software_2026-07-05.md`](./sector-overview_AI-analytics-software_2026-07-05.md) | `/sector AI 數據分析軟體` | 產業地景研究 |

### Microsoft Corporation (MSFT)

| 檔案 | 對應指令 | 說明 |
|---|---|---|
| [`earnings-preview_MSFT_2026-07-05.md`](./earnings-preview_MSFT_2026-07-05.md) | `/earnings-preview MSFT` | 2026 Q4（FY 尾季，7/28 公布）財報前瞻 + 多空情境 |
| [`thesis_MSFT_2026-07-05.md`](./thesis_MSFT_2026-07-05.md) | `/thesis MSFT` | 投資論點與追蹤紀錄 |

**資料日期：2026-07-05**。市場數據取自公開來源（SEC 8-K、分析師共識、財經媒體），詳見各文件末的來源清單。

> ⚠️ 本內容僅供教育與示範，不構成投資建議。數據會隨時間變動，實際交易前請自行查證最新資訊並諮詢合格顧問。
