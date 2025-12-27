---
title: "Service: Data Ingestor"
doc_id: safechord.safezone.service.dataingestor
version: "0.2.1"
status: active
authors:
  - bradyhau
  - Gemini 2.5 Pro
last_updated: "2025-09-12"
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
tech_stack:
  - Python 3.13
  - FastAPI 0.115
  - Kafka (aiokafka 0.12)
  - Pydantic
---

# Data Ingestor (v0.2.1)

## 📌 服務定位
Data Ingestor 是系統的 **寫入閘道 (Ingestion Gateway)**。
*   **角色**: Producer (Kafka)。它不負責資料持久化 (Persistence)，僅負責資料驗證、結構封裝與事件發布。
*   **特性**: Stateless, High-Throughput。設計目標是快速接收大量 HTTP 請求並卸載至 Kafka，以應對突發流量 (Spike Traffic)。

---

## 🛠️ 核心規格 (Specifications)

### 1. API 接口與資料契約
本服務作為資料入口，對資料格式有嚴格驗證要求。

*   **Input (HTTP)**: `POST /covid_event`
    *   **Body**: `CovidDataModel` (包含 `date`, `city`, `region`, `cases` 等)。
    *   **Validation**: 若 `cases <= 0` 或日期格式錯誤，回傳 `422 Unprocessable Entity`。

*   **Output (Kafka)**:
    *   **Topic**: `covid.raw.data` (Default, via `KAFKA_TOPIC`)。
    *   **Partition Key**: `"{city}-{region}"` (確保同一區域的數據進入同一 Partition，保證順序性)。
    *   **Schema (CovidContract)**:
        ```json
        {
          "event_type": "covid_event",
          "event_time": 1679000000000,
          "trace_id": "uuid-v4",
          "payload": { ...CovidDataModel... },
          "version": "0.1.0"
        }
        ```

### 2. 外部依賴與控制 (Dependencies & Control)
*   **Control Plane (Trigger)**: 被動接收來自 [Pandemic Simulator](safechord.safezone.service.pandemicsimulator.md) 的 HTTP POST 請求。
*   **Downstream**: [Kafka Cluster]。
    *   **Connection**: 啟動時建立 `AIOKafkaProducer` 連線池。
    *   **Reliability**: 設定 `acks="all"` 與 `enable_idempotence=True` 確保訊息不丟失。

---

## 🧪 行為驗證 (Behavior Verification)

本服務的驗證邏輯集中管理於單一規格檔中。

| 範疇 | 規格檔路徑 (Source of Truth) | 業務意圖 (Business Intent) |
| :--- | :--- | :--- |
| **API 行為** | `test/cases.json` | 定義所有 API 場景：<br>1. **正常寫入**: 接收有效 JSON -> 回傳 200 OK。<br>2. **格式驗證**: 日期格式錯誤 (`YYYY/MM/DD`) -> 回傳 422。<br>3. **業務規則**: 欄位缺失 -> 回傳 422。<br>4. **健康檢查**: `/health` 端點回傳 `{"status": {"ingestor": "healthy"}}`。 |

---

## 🧩 設計權衡 (Design Trade-offs)

### 1. 為什麼選擇 `aiokafka`？
*   **Async I/O**: 配合 FastAPI 的非同步特性，`aiokafka` 允許在單一 Event Loop 中處理大量併發請求，避免因等待 Kafka ACK 而阻塞 HTTP 執行緒。

### 2. 分區策略 (Partitioning Strategy)
*   **Natural Key**: 使用 `city-region` 作為 Key，而非隨機 Round-Robin。
*   **Trade-off**: 這可能導致 Partition 熱點 (Skew)，例如「台北市」的數據量遠大於偏鄉。但為了確保後端 Consumer 在計算累積數據時的順序正確性 (Ordering)，這是必要的犧牲。

---

## 🚀 部署與維運
*   **Docker Image**: `safezone-data-ingestor`
*   **環境變數**:
    *   `KAFKA_BOOTSTRAP`: Kafka 連線地址 (Default: `localhost:9092`)
    *   `KAFKA_TOPIC`: 目標 Topic (Default: `covid.raw.data`)
    *   `LOG_LEVEL`: 日誌級別 (Default: `DEBUG`)
*   **Health Check**: `GET /health`