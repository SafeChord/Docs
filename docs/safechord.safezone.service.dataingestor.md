---
title: "Service: Data Ingestor"
doc_id: safechord.safezone.service.dataingestor
version: "0.2.1"
status: active
authors:
  - bradyhau
  - Gemini 2.5 Pro
last_updated: "2025-09-12"
summary: "Data Ingestor 是 SafeZone 系統的資料入口閘道 (Gateway)。它提供 RESTful API 接收外部事件，並將其轉換為標準化的 Kafka 訊息，實現資料寫入與處理的非同步解耦。"
keywords:
  - Data Ingestor
  - Kafka Producer
  - Gateway
  - Event Driven
  - FastAPI
logical_path: "SafeChord.SafeZone.Service.DataIngestor"
related_docs:
  - "safechord.safezone.changelog.md"
  - "safechord.safezone.service.datasimulator.md"
  - "safechord.safezone.service.worker.md"
parent_doc: "safechord.safezone.service"
tech_stack:
  - Python 3.13
  - FastAPI
  - Kafka (aiokafka)
  - Pydantic
---

# Data Ingestor (v0.2.1)

## 📌 服務定位
Data Ingestor 是系統的 **寫入閘道 (Ingestion Gateway)**。
*   **角色**: Producer (Kafka)。它不負責資料持久化 (Persistence)，僅負責資料驗證與事件發布。
*   **特性**: Stateless, High-Throughput。設計目標是快速接收大量 HTTP 請求並卸載至 Kafka，以應對突發流量 (Spike Traffic)。

---

## 🛠️ 核心規格 (Specifications)

### 1. API 接口與資料契約
本服務作為資料入口，對資料格式有嚴格驗證要求。
*   **Input (HTTP)**: `CovidDataModel` (參見 `utils/pydantic_model/request.py`)。
*   **Output (Kafka)**: 
    *   Topic: 由環境變數 `KAFKA_TOPIC` 決定 (Default: `covid.case.data`)。
    *   Schema: JSON 序列化物件，包含 `payload` (原始數據), `trace_id`, `event_time`。

### 2. 外部依賴與控制 (Dependencies & Control)
*   **Control Plane (Trigger)**: 被動接收來自 [Pandemic Simulator](safechord.safezone.service.datasimulator.md) 的 HTTP POST 請求。
*   **Downstream**: [Kafka Cluster]。
    *   *Note*: 服務啟動時會建立 `AIOKafkaProducer` 連線池。

---

## 🧪 行為驗證 (Behavior Verification)

本服務的驗證邏輯集中管理於單一規格檔中。

| 範疇 | 規格檔路徑 (Source of Truth) | 業務意圖 (Business Intent) |
| :--- | :--- | :--- |
| **整合行為** | `test/cases.json` | 定義了所有 API 場景，包含：<br>1. **正常寫入**: 接收有效 JSON -> 回傳 200 OK。<br>2. **格式驗證**: 日期格式錯誤、欄位缺失 -> 回傳 422 Unprocessable Entity。<br>3. **業務規則**: `cases` 數量 <= 0 -> 回傳 422。<br>4. **健康檢查**: `/health` 端點回傳服務狀態。 |

> **注意**: 目前測試套件使用 `AsyncMock` 模擬 Kafka Producer 行為，側重於 API 層與資料驗證邏輯的測試。

---

## 🧩 設計權衡 (Design Trade-offs)

### 1. 為什麼從直接寫入 DB (v0.1) 改為寫入 Kafka (v0.2)？
*   **削峰填谷 (Peak Shaving)**: 當 Simulator 進行壓力測試時，瞬間流量可能超過 PostgreSQL 的連線數上限。引入 Kafka 作為緩衝，允許 Ingestor 以極高的吞吐量接收請求，而 Worker 可以依照 DB 的處理能力慢慢消化。
*   **解耦 (Decoupling)**: Ingestor 不再需要知道 DB Schema，只需關注資料格式。這讓後端儲存架構的變更（如換 DB）不會影響到資料入口。

### 2. 資料一致性考量
*   **Producer Acks**: 配置 `acks="all"` 與 `enable_idempotence=True`，確保訊息在 Kafka 端被持久化後才回傳 HTTP 200 給客戶端，防止資料丟失。

---

## 🚀 部署與維運
*   **Docker Image**: `safezone-data-ingestor`
*   **環境變數**:
    *   `KAFKA_BOOTSTRAP`: Kafka 連線地址
    *   `KAFKA_TOPIC`: 目標 Topic
*   **Health Check**: `GET /health`