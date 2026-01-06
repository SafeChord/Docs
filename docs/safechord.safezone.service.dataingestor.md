---
title: "Service: Data Ingestor"
doc_id: safechord.safezone.service.dataingestor
version: "0.2.1"
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
last_updated: "2026-01-04"
summary: "Data Ingestor 是 SafeZone 系統的資料入口閘道 (Gateway)。它提供 RESTful API 接收外部事件，並將其封裝為標準化的 Kafka 訊息 (CovidContract)，實現資料寫入與處理的非同步解耦。"
keywords:
  - Data Ingestor
  - Kafka Producer
  - Gateway
  - Event Driven
  - FastAPI
logical_path: "SafeChord.SafeZone.Service.DataIngestor"
related_docs:
  - "safechord.safezone.changelog.md"
  - "safechord.safezone.service.pandemicsimulator.md"
  - "safechord.safezone.service.worker.md"
parent_doc: "safechord.safezone.service"
archetype: blueprint
code_paths:
  - "SafeZone/services/data-ingestor"
tech_stack:
  - Python 3.13
  - FastAPI 0.115
  - Kafka (aiokafka 0.12)
  - Pydantic
---

# Data Ingestor (Service Blueprint)

> ⚠️ **Scope Warning**: This blueprint defines the `data-ingestor` microservice.
> *繼承自 `archetype.blueprint.microservice.md`*

## 1. 職責與定位 (Responsibility)
*   **角色**: Gateway / Producer (Kafka)
*   **特性**: Stateless, High-Throughput, Event-Driven
*   **核心目標**: 作為系統的資料寫入入口。它不負責資料的長期存儲，而是專注於接收 HTTP 請求、執行結構化驗證，並將其快速卸載至 Kafka 緩衝區。這為系統提供了強大的削峰填谷 (Load Leveling) 能力。

## 2. 檔案結構 (File Structure)
```text
SafeZone/services/data-ingestor/
├── app/
│   ├── main.py                   # Entry Point (FastAPI Lifespan for Producer)
│   ├── api/
│   │   └── endpoints.py          # Route Handlers (/covid_event, /health)
│   └── config/
│       ├── kafka.py              # Kafka Producer Lifecycle (aiokafka)
│       └── settings.py           # App Settings & Env Loader
├── test/
│   ├── cases.json                # JSON Spec for API Behavior Verification
│   └── test_main.py              # Integration Tests
├── Dockerfile                    # Production Environment Builder
├── Dockerfile.test               # CI/CD Test Environment Builder
├── requirements.txt              # Production Dependencies
└── requirements.test.txt         # Testing Framework (pytest)
```

## 3. 接口規範 (Interfaces)

### 資料契約 (Contracts)
*   **Input (CovidDataModel)**: 定義於 `utils/pydantic_model/request.py`。
*   **Internal (CovidContract)**: 封裝層，包含 `event_type`, `event_time`, `trace_id`, `payload`, `version`。

### 輸入 (Ingress)
*   **Type**: API (HTTP POST)
*   **Source**:
    *   `POST /covid_event`: 接收疫情事件數據。
    *   `GET /health`: 健康檢查。

### 輸出 (Egress)
*   **Dest**: Kafka Cluster (Producer)
*   **Topic**: `covid.raw.data` (可透過 `KAFKA_TOPIC` 配置)
*   **Partition Key**: `city-region` (確保同區域事件的時序一致性)

## 4. 依賴與控制 (Dependencies & Control)

| 依賴對象 | 類型 | 說明 |
| :--- | :--- | :--- |
| **Upstream** | Source | Pandemic Simulator 或 CLI 工具。 |
| **Kafka Cluster** | Downstream | 訊息中繼站。Ingestor 依賴 Kafka 的可用性來完成資料卸載。 |
| **Control Plane** | N/A | 本服務為被動接收請求的 Gateway。 |

## 5. 行為驗證 (Behavior Verification)
本服務採用 **Spec-as-Code** 策略。業務邏輯的正確性由 JSON 測試案例嚴格定義。

| 範疇 | 規格檔路徑 (Source of Truth) | 業務意圖 (Business Intent) |
| :--- | :--- | :--- |
| **API 行為** | `test/cases.json` | 驗證正常寫入、格式錯誤 (422) 與服務健康狀態。 |
| **傳輸契約** | `app/api/endpoints.py` | 驗證 `CovidContract` 的封裝邏輯是否符合後端 Consumer 的預期。 |

## 6. 實作決策 (Implementation Decisions)

*   **Asynchronous Production (aiokafka)**:
    *   **Why**: 為了不阻塞 HTTP 請求的執行緒。`aiokafka` 允許 Ingestor 在極短時間內完成請求接收並返回 ACK，將真正的寫入壓力交給 Kafka。
*   **Natural Key Partitioning**:
    *   **Why**: 使用 `city-region` 作為 Partition Key 而非 Round-Robin。
    *   **Trade-off**: 雖然這可能導致數據分區傾斜 (Skew)，但能保證同一地理區域的數據在 Kafka 中是有序的，這對於後續 Worker 計算累積數據至關重要。
*   **Lifespan Management**:
    *   **Why**: 使用 FastAPI 的 `lifespan` 來管理 Kafka Producer 的啟動與優雅停機 (Graceful Shutdown)，確保連接池在服務關閉時能正確釋放。
*   **Architecture Evolution**:
    *   詳見 [ADR: From Sync DB to Event-Driven Ingestion](safechord.safezone.ingestor_evolution.md)。(簡述：為了解耦寫入壓力，於 v0.2.0 重構為 Kafka Producer。)
*   **Potential Bottleneck & Scaling Plan**:
    *   **Observation**: 目前 Python (FastAPI) 實作在高併發場景下可能成為 CPU 瓶頸，因此在 Upstream (Simulator) 實施了限流 (`Semaphore`)。
    *   **Future Plan**: 詳見 [Issue #22: Refactor Data Ingestor to Golang](https://github.com/SafeChord/SafeZone/issues/22)。規劃在預見效能瓶頸時遷移至 Golang 並整合 KEDA。

## 7. 部署與維運 (Deployment & Ops)

*   **Docker Image**: `safezone-data-ingestor`
*   **Health Check**: `GET /health` (回傳 `{"status": {"ingestor": "healthy"}}`)
*   **Configuration**:
    *   **關鍵環境變數**:
        *   `KAFKA_BOOTSTRAP`: Kafka 連線地址。
        *   `KAFKA_TOPIC`: 目標 Topic。
        *   `LOG_LEVEL`: 調節日誌詳細度 (預設為 DEBUG)。