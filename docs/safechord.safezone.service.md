---
title: "SafeZone: Application Services & Data Flow Architecture"
doc_id: safechord.safezone.service
version: "0.2.1"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
last_updated: "2025-12-28"
summary: "本文檔詳細描述 SafeZone v0.2.1 的服務架構。區分了核心業務服務與工具組件，並特別強調 szcli (Client-Relay) 與 Time Server 在非同步資料流與驗證中的核心作用。"
keywords:
  - SafeZone
  - service architecture
  - szcli
  - dataflow
  - smoke-test
  - kafka
  - pandemic-simulator
  - cache versioning
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
| 服務名稱 | 職責類型 | 核心職責 | 關鍵技術特性 |
| :--- | :--- | :--- | :--- |
| **pandemic-simulator** | **Source** | **資料產地**。接收觸發指令後，依據模擬時間產生災情事件。 | **AsyncIO**, Passive-Triggered |
| **data-ingestor** | **Producer** | **資料入口**。寫入閘道 (Gateway)，驗證結構並推送 Kafka。 | **FastAPI**, High-Throughput |
| **worker-golang** | **Consumer** | **資料落盤**。高效消費 Kafka 訊息，確保資料寫入 PostgreSQL。 | **Franz-Go**, Batch Insert, Idempotent |
| **analytics-api** | **Reader** | **資料出口**。提供查詢介面，整合進階快取策略。 | **Cache Versioning**, Global Invalidation |
| **dashboard** | **Visualizer** | **視覺化前端**。呈現疫情曲線圖與統計資訊。 | **Plotly Dash**, Time-Aware |

### 🛠️ 工具與控制 (Toolkit & Controllers) - 負責系統運作與觸發
| 服務名稱 | 職責類型 | 核心職責 | 關鍵技術特性 |
| :--- | :--- | :--- | :--- |
| **szcli** | **Orchestrator** | **發令槍與裁判**。觸發模擬、植入種子資料與驗證數據。 | **Client-Relay Pattern**, OAuth 2.0 |
| **time-server** | **Controller** | **時間塔**。維持全系統唯一的「模擬時間 (System Date)」。 | **Time Travel**, Redis Backend |

---

## 🖼 關鍵路徑：從觸發到驗證 (E2E Flow)

在 Smoke Test 或生產環境初始化時，資料流遵循以下路徑：

### 1. 觸發與生成 (Trigger & Generate)
1.  **指令下達**：`User` 或 `CI` 執行 `szcli dataflow simulate --days=30`。
2.  **時間同步**：`szcli` 取得 `time-server` 的當前系統時間以決定模擬區間。
3.  **任務委派**：`szcli` (Relay) 呼叫 `pandemic-simulator` 啟動非同步生成任務。

### 2. 非同步注入 (Async Ingestion)
4.  **事件發送**：`simulator` 使用 **AsyncIO** 高併發將生成數據發送至 `data-ingestor`。
5.  **進入緩衝**：`data-ingestor` 將數據寫入 Kafka Topic (`covid.raw.data`)。
6.  **持久化**：`worker-golang` 使用 **Franz-Go** 批次消費並執行 **Batch Insert** 寫入 PostgreSQL。

### 3. 驗證與觀測 (Verify & Observe)
7.  **快取失效**：模擬結束時，CLI 觸發 `analytics-api` 的 **Global Invalidation** (更新 Cache Version)。
8.  **主動驗證**：`szcli dataflow verify` 呼叫 `analytics-api` 檢查資料是否已落盤。
9.  **快取行為**：在 Smoke Test 中，`szcli` 連續執行驗證，透過 Trace ID 檢查 **Cache Miss** (第一次) 與 **Cache Hit** (第二次) 的行為。

### 4. 使用者瀏覽 (User Journey)
10. **圖表請求**：使用者開啟瀏覽器，`dashboard` 向 `analytics-api` 請求數據。
11. **版本檢查**：`analytics-api` 檢查 Redis 中的 `cache_version`，確保不回傳過期數據 (Cache-Aside)。
12. **視覺呈現**：`dashboard` 接收 JSON 響應，繪製熱力圖與趨勢線。

---

## 🧭 運維參考 (CLI Usage)

- **自動化測試**：參閱 `SafeZone/scripts/smoke-test.sh`。
- **預覽環境初始化**：參閱 `SafeZone/toolkit/cli/command/scripts/preview/seed_data.sh`。