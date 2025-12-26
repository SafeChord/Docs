---
title: "SafeZone: Application Services & Data Flow Architecture"
doc_id: safechord.safezone.service
version: "0.2.1"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
last_updated: "2025-09-12"
summary: "本文檔詳細描述 SafeZone v0.2.1 的服務架構。區分了核心業務服務與工具組件，並特別強調 szcli 作為系統觸發者與驗證者在數據流中的核心作用。"
keywords:
  - SafeZone
  - service architecture
  - szcli
  - dataflow
  - smoke-test
  - kafka
  - pandemic-simulator
logical_path: "SafeChord.SafeZone.Service"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.safezone.md"
  - "safechord.safezone.service.pandemicsimulator.md"
  - "safechord.safezone.toolkit.cli.md"
parent_doc: "safechord.safezone"
tech_stack:
  - Python
  - Golang
  - Kafka
  - PostgreSQL
  - Redis
---
# SafeZone-Service (v0.2.1)

> SafeZone 的架構圍繞著「自動化驗證」設計。
> 所有的資料流動，通常始於 `szcli` 的一個指令，終於 `szcli` 的一個驗證。

---

## 🧪 服務模組與工具分類

### 🧩 核心服務 (Core Services) - 負責資料的生命週期
| 服務名稱 | 職責類型 | 核心職責 |
| :--- | :--- | :--- |
| **pandemic-simulator** | **Source** | **資料產地**。接收觸發指令後，依據模擬時間產生災情事件。 |
| **data-ingestor** | **Producer** | **資料入口**。驗證資料結構並推送到 Kafka Topic (`covid-data`)。 |
| **worker-golang** | **Consumer** | **資料落盤**。高效消費 Kafka 訊息，確保資料寫入 PostgreSQL。 |
| **analytics-api** | **Reader** | **資料出口**。提供具備 Redis 快取機制的查詢介面。 |
| **dashboard** | **Visualizer** | **視覺化前端**。呈現疫情曲線圖與統計資訊。 |

### 🛠️ 工具與控制 (Toolkit & Controllers) - 負責系統運作與觸發
| 服務名稱 | 職責類型 | 核心職責 |
| :--- | :--- | :--- |
| **szcli** | **Orchestrator** | **發令槍與裁判**。觸發模擬 (`simulate`)、種子資料植入 (`seed`) 與數據驗證 (`verify`)。 |
| **time-server** | **Controller** | **時間塔**。維持全系統唯一的「模擬時間 (System Date)」。 |

---

## 🖼 關鍵路徑：從觸發到驗證 (E2E Flow)

在 Smoke Test 或生產環境初始化時，資料流遵循以下路徑：

### 1. 觸發與生成 (Trigger & Generate)
1.  **指令下達**：`User` 或 `CI` 執行 `szcli dataflow simulate --days=30`。
2.  **時間同步**：`szcli` 取得 `time-server` 的當前系統時間以決定模擬區間。
3.  **任務委派**：`szcli` 呼叫 `pandemic-simulator` 啟動非同步生成任務。

### 2. 非同步注入 (Async Ingestion)
4.  **事件發送**：`simulator` 將生成數據發送至 `data-ingestor`。
5.  **進入緩衝**：`data-ingestor` 將數據寫入 Kafka。
6.  **持久化**：`worker-golang` 監聽 Kafka 並寫入 PostgreSQL。

### 3. 驗證與觀測 (Verify & Observe)
7.  **主動驗證**：`szcli dataflow verify` 呼叫 `analytics-api` 檢查資料是否已落盤且正確。
8.  **快取驗證**：在 Smoke Test 中，`szcli` 會連續執行兩次 verify，透過 Trace ID 檢查 `analytics-api` 是否正確觸發了 **Cache Hit/Miss** 機制。

### 4. 使用者瀏覽 (User Journey)
9.  **圖表請求**：使用者開啟瀏覽器，`dashboard` 前端向 `analytics-api` 請求聚合數據。
10. **快取優先**：`analytics-api` 查詢 Redis。若 Miss 則查詢 PostgreSQL 並回填 Redis (Cache-Aside)。
11. **視覺呈現**：`dashboard` 接收 JSON 響應，繪製熱力圖與趨勢線。

---

## 🧭 運維參考 (CLI Usage)

- **自動化測試**：參閱 `SafeZone/scripts/smoke-test.sh`。
- **預覽環境初始化**：參閱 `SafeZone/toolkit/cli/command/scripts/preview/seed_data.sh`。