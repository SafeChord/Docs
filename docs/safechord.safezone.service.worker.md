---
title: "Service: Worker (Golang)"
doc_id: safechord.safezone.service.worker
version: "0.2.1"
status: active
authors:
  - bradyhau
  - Gemini 2.5 Pro
last_updated: "2025-09-12"
summary: "Worker 是 SafeZone 系統的資料處理核心，採用 Golang 1.24 與 Franz-Go 實作。負責從 Kafka 高效消費數據，並透過批次寫入 (Batch Insert) 與等冪更新 (Idempotent Upsert) 機制，將數據持久化至 PostgreSQL。"
keywords:
  - Worker
  - Kafka Consumer
  - Golang
  - Franz-Go
  - PostgreSQL
  - Batch Processing
logical_path: "SafeChord.SafeZone.Service.Worker"
related_docs:
  - "safechord.safezone.changelog.md"
  - "safechord.safezone.service.dataingestor.md"
  - "safechord.safezone.service.analyticsapi.md"
parent_doc: "safechord.safezone.service"
tech_stack:
  - Golang 1.24
  - Franz-Go (High-perf Kafka Lib)
  - pgx/v5 (PostgreSQL Driver)
  - sqlx
---

# Worker - Golang (v0.2.1)

## 📌 服務定位
Worker 是系統的 **資料落盤者 (Persister)**。
*   **角色**: Consumer Group (Kafka)。
*   **特性**: High-Throughput, Idempotent。
*   **目標**: 以 Golang 的高併發特性，消化 Kafka 中的流量峰值，並確保資料庫寫入的穩定性。

---

## 🛠️ 核心規格 (Specifications)

### 1. 資料處理流程 (Pipeline)
Worker 透過 Orchestrator 協調以下組件運作：
1.  **Source (Kafka Adapter)**:
    *   使用 `franz-go` 進行消費。
    *   **Commit Strategy**: 採用 Explicit Commit。當前實作在讀取後立即 Commit，依賴下游的 DB Upsert 機制保證最終一致性。
2.  **Buffer**: 
    *   暫存 `CovidEvent` 結構。
    *   執行 **In-Memory De-duplication**：在送往 DB 前，先過濾掉同一批次內重複的 `(date, city, region)` 數據。
3.  **Sink (DB Strategy)**: 
    *   當 Buffer 滿或達到時間閾值時觸發 `Flush`。
    *   執行 `Batch Insert` 寫入 PostgreSQL。

### 2. 資料契約 (Contracts)
*   **Input**: Kafka Topic `covid.raw.data` (JSON: `CovidContract`)
*   **Output**: PostgreSQL Table `covid_cases`
    *   Schema: `date` (PK), `city_id` (PK), `region_id` (PK), `cases`.

### 3. 外部依賴與控制
*   **Upstream**: [Kafka Cluster]
*   **Downstream**: [PostgreSQL]
    *   依賴 `cache` package 進行 `City/Region Name` -> `ID` 的快速轉換，減少 DB Lookup 開銷。

---

## 🧪 行為驗證 (Behavior Verification)

| 範疇 | 測試策略 | 業務意圖 (Business Intent) |
| :--- | :--- | :--- |
| **等冪寫入** | `Integration Test` | 發送兩筆相同 `(Date, City, Region)` 但不同 `Cases` 的數據，驗證 DB 最終狀態是否為最新一筆 (Upsert 行為)。 |
| **批次處理** | `Benchmark` | 模擬高流量場景，驗證 Worker 是否能正確觸發 Batch Flush，且無 Memory Leak。 |

---

## 🧩 設計權衡 (Design Trade-offs)

### 1. 為什麼選擇 `franz-go`？
*   **效能優勢**: 相較於 `segmentio/kafka-go`，`franz-go` 在處理高吞吐量與連線管理上表現更優，且原生支援 KRaft 協議。
*   **功能完整**: 提供了更細粒度的 Offset 控制與 Group Rebalancing 策略。

### 2. 寫入衝突處理 (Collision Handling)
*   **雙重防護**: 
    1.  **Memory Level**: `DBSink` 在組裝 SQL 前會檢查 `collisionCheck` map，過濾同批次重複項。
    2.  **DB Level**: SQL 使用 `ON CONFLICT DO UPDATE`，確保即使多個 Worker 同時寫入，資料庫也能保持一致。

---

## 🚀 部署與維運
*   **Docker Image**: `safezone-worker-golang`
*   **環境變數**:
    *   `KAFKA_BROKERS`: Kafka 位址
    *   `POSTGRES_DSN`: 資料庫連線字串
    *   `CONSUMER_GROUP`: 消費者群組 (Default: `covid-worker-group`)
    *   `BATCH_SIZE`: 批次寫入筆數
*   **Health Check**: 
    *   Worker 啟動時會執行 `Client.Ping()` 檢查 Kafka 連線，失敗則 Panic 重啟 (依賴 K8s Restart Policy)。