---
title: 'Service: Worker (Golang)'
doc_id: safechord.safezone.service.worker
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
last_updated: '2026-04-16'
summary: Worker 是 SafeZone 系統的資料處理核心，採用 Golang 1.24 與 Franz-Go 實作。負責從 Kafka 高效消費數據，並透過批次寫入
  (Batch Insert) 與等冪更新 (Idempotent Upsert) 機制，將數據持久化至 PostgreSQL。
keywords:
  - Worker
  - Kafka Consumer
  - Golang
  - Franz-Go
  - PostgreSQL
  - Batch Processing
logical_path: SafeChord.SafeZone.Service.Worker
related_docs:
  - safechord.safezone.changelog.md
  - safechord.safezone.service.dataingestor.md
  - safechord.safezone.service.analyticsapi.md
parent_doc: safechord.safezone.service
archetype: blueprint
code_paths:
  - SafeZone/services/worker-golang
tech_stack:
  - Golang 1.24
  - Franz-Go (Kafka)
  - pgx/v5 (PostgreSQL)
  - sqlx
doc_version: 0.3.0
app_version: 0.3.0-dev
---

# Worker - Golang (Service Blueprint)

> ⚠️ **Scope Warning**: This blueprint defines the `worker-golang` microservice.
> *繼承自 `archetype.blueprint.microservice.md`*

## 1. 職責與定位 (Responsibility)
*   **角色**: Consumer (Kafka) / Persister
*   **特性**: High-Throughput, Idempotent, Batch-Oriented
*   **核心目標**: 作為高吞吐量的數據落盤組件。利用 Golang 的併發特性消化 Kafka 峰值流量，並負責將非結構化的事件流轉化為結構化的關聯式數據 (Relational Data)。

## 2. 檔案結構 (File Structure)
```text
SafeZone/services/worker-golang/
├── app/
│   ├── main.go                     # Entry Point (Signal Handling & Lifecycle)
│   ├── service/
│   │   ├── worker.go               # Core Business Logic (Batch & Flush)
│   │   ├── worker_test.go          # [Unit Test] Flow verification
│   │   └── orchestrator.go         # Worker Pool Execution (Parallelism control)
│   ├── adapter/                    # [Ports] Input Adapters
│   │   ├── source.go               # Interface: EventSource
│   │   ├── kafkaSource.go          # Impl: Franz-Go Consumer
│   │   └── mockSource.go           # Impl: Channel-based Mock (for Testing)
│   ├── strategy/                   # [Ports] Output Ports
│   │   ├── sink.go                 # Interface: EventSink
│   │   ├── dbSink.go               # Impl: PostgreSQL Batch Upsert
│   │   └── mockSink.go             # Impl: Capture-based Mock (for Testing)
│   ├── schema/
│   │   ├── event.go                # Data Models (Contracts)
│   │   ├── validator.go            # Validation Logic (Depends on CacheReader)
│   │   └── validator_test.go       # [Unit Test] Rule verification
│   ├── config/                     # Configuration Loader
│   └── pkg/                        # Shared Utilities (Logger, Cache)
├── go.mod / go.sum                 # Dependency Management
├── Dockerfile                      # Production Builder
└── Dockerfile.test                 # Test Runner (used in CI)
```

## 3. 接口規範 (Interfaces)

### 資料契約 (Contracts)
*   **Input**: `CovidEvent` (定義於 `app/schema/event.go`)
    *   對應 Kafka Topic `covid.raw.data` 的 JSON Payload。
*   **Output**: Database Table `covid_cases`

### 輸入 (Ingress)
*   **Type**: Worker Consumer
*   **Source**: Kafka Topic `covid.raw.data`
*   **Consumer Group**: `covid-worker-group` (可配置)

### 輸出 (Egress)
*   **Dest**: PostgreSQL Database
*   **Behavior**: Batch Upsert (`ON CONFLICT DO UPDATE`)

## 4. 依賴與控制 (Dependencies & Control)

| 依賴對象 | 類型 | 說明 |
| :--- | :--- | :--- |
| **Kafka Cluster** | Upstream | 數據來源。在 `TEST` 模式下可被 `MockSource` 替換。 |
| **PostgreSQL** | Downstream | 數據去向。在 `TEST` 模式下可被 `MockSink` 替換。 |
| **Control Plane** | Trigger | 服務啟動後持續運行 (Daemon)，由 Kubernetes 控制生命週期。 |

## 5. 行為驗證 (Behavior Verification)
本服務採用 **Ports & Adapters** 模式，支援在無基礎設施的情況下驗證邏輯。

| 範疇 | 驗證策略 | 業務意圖 (Business Intent) |
| :--- | :--- | :--- |
| **核心邏輯** | `go test ./...` | 透過 `MockSource` 注入固定事件，驗證 `Worker` 的去重複 (De-duplication) 與驗證邏輯是否正確。 |
| **等冪寫入** | `Integration Test` | 發送重複的 `(Date, City, Region)` 數據，驗證 DB 最終狀態的一致性 (Upsert)。 |
| **批次處理** | `Benchmark` | 模擬高流量場景，驗證 Batch Flush 機制是否如期觸發 (Time-based or Size-based)。 |

## 6. 實作決策 (Implementation Decisions)

*   **Idiomatic Go Refactor (v0.3.0)**:
    *   **Decision**: 移除 Java 風格的 `WorkerFactory` 與 `Orchestrator` struct，改用 Package-level 函式（如 `NewWorker`, `RunWorkers`）進行依賴注入與生命週期管理。
    *   **Rationale**: 減少不必要的抽象層與物件狀態，利用 Go 的組合性與函式化特性提升程式碼可讀性與測試便利性。
*   **Interface-based Testability**:
    *   **Decision**: 引入 `CacheReader` Interface 並透過消費者定義 (Consumer-defined) 介面實作 `CovidValidator`。
    *   **Rationale**: 徹底解耦 `schema` 與 `pkg/cache` 實作，讓單元測試能在完全不連線資料庫的情況下驗證複雜的業務規則。
*   **Memory Leak Hardening**:
    *   **Decision**: 嚴格管控 Context 的 `cancel` 呼叫，確保 `defer cancel()` 位於正確的作用域（即迴圈外或立即呼叫）。
    *   **Why**: 避免在長時間運行的 Worker 循環中堆積未釋放的 Timer goroutines，確保生產環境的記憶體穩定性。
*   **Franz-Go Library**:
    *   **Decision**: 使用 `twmb/franz-go` 取代 `segmentio/kafka-go`。
    *   **Why**: 為了更好的效能與 KRaft 協議支援 (詳見 ADR: Ingestor Evolution)。
*   **Explicit Commit Strategy**:
    *   **Decision**: 讀取後立即 Commit (At-most-once 傾向)，但在 DB 層使用 Upsert 保證一致性。
    *   **Why**: 為了追求極致的消費吞吐量。雖然理論上有丟失風險，但在 `k3han` 的架構權衡下，我們優先保證即時性，並依賴上游重送機制補償。

## 7. 部署與維運 (Deployment & Ops)

*   **Docker Image**: `safezone-worker-golang`
*   **Health Check**: 
    *   Liveness Probe: 檢查 Process 是否存活。
    *   Startup Probe: 檢查 Kafka 連線是否建立。
*   **Configuration**:
    *   **關鍵環境變數**:
        *   `ENVIRONMENT`: `PROD` (Default) 或 `TEST` (啟用 Mock)。
        *   `KAFKA_BROKERS`: Kafka 位址。
        *   `POSTGRES_DSN`: DB 連線字串。
        *   `BATCH_SIZE`: 批次寫入筆數 (Default: 1000)。