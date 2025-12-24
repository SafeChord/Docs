---
title: "Service: Pandemic Simulator"
doc_id: safechord.safezone.service.datasimulator
version: "0.2.3"
status: active
authors:
  - bradyhau
  - Gemini 2.5 Pro
last_updated: "2025-09-12"
summary: "Pandemic Simulator 是 SafeZone 資料流的源頭，負責將靜態的疫情數據轉換為動態的時間序列事件。本服務採用 AsyncIO 架構，並由 SafeZone CLI 統一調度，支援歷史回放、系統初始化 (Seeding) 與每日排程等多種觸發模式。"
keywords:
  - Pandemic Simulator
  - Data Generation
  - AsyncIO
  - Control Plane
  - Event Sourcing
  - System Seeding
logical_path: "SafeChord.SafeZone.Service.PandemicSimulator"
related_docs:
  - "safechord.safezone.changelog.md"
  - "safechord.safezone.service.dataingestor.md"
  - "safechord.safezone.toolkit.cli.md"
parent_doc: "safechord.safezone.service"
tech_stack:
  - Python 3.13
  - FastAPI
  - AsyncIO
  - httpx
  - Pandas
---

# Pandemic Simulator (v0.2.1)

## 📌 服務定位
Pandemic Simulator 是一個 **被動觸發 (Passive-Triggered)** 的資料產生服務。它不自行維護排程，而是作為 **SafeZone CLI (Control Plane)** 的執行單元。其職責是讀取容器內的靜態 CSV 數據，根據請求參數進行切片 (Slicing)，並透過非同步請求將模擬事件「注入」到系統中。

這種「啞組件 (Dumb Component)」設計使其能靈活支援多種運維劇本：
1.  **Smoke Test**: 驗證單點功能與快取失效機制。
2.  **System Seeding**: 系統啟動時，自動回填過去 33 天的歷史數據 (參考 `preview/seed_data.sh`)。
3.  **Daily Cron**: 配合 TimeServer，模擬每日疫情推進 (規劃中)。

---

## 🛠️ 核心規格 (Specifications)

### 1. API 接口與資料契約
本服務遵循統一的資料契約。AI Agent 應優先參考 Pydantic 模型以獲取最新欄位定義。
*   **Request Models**: `DailyParameters` (單日模擬), `IntervalParameters` (區間模擬) -> 參見 `utils/pydantic_model/request.py`
*   **Response Models**: `APIResponse`, `HealthResponse` -> 參見 `utils/pydantic_model/response.py`

### 2. 外部依賴與控制 (Dependencies & Control)
*   **Control Plane (Trigger)**: [SafeZone CLI](safechord.safezone.toolkit.cli.md) 
    *   *Rationale*: 模擬器由 CLI 指令 (e.g., `szcli dataflow simulate`) 喚醒。這允許外部腳本精確控制「模擬時間」的流速與範圍。
*   **Downstream**: [Data Ingestor](safechord.safezone.service.dataingestor.md)
    *   *Interaction*: 透過 HTTP POST 發送標準化的 `CovidDataModel` 事件。
*   **Data Source**: `/data/covid_data.csv` (唯讀掛載)

---

## 🧪 行為驗證 (Behavior Verification)

本服務採用 **Spec-as-Code** 策略。業務邏輯的正確性由 JSON 測試案例嚴格定義：

| 範疇 | 規格檔路徑 (Source of Truth) | 業務意圖 (Business Intent) |
| :--- | :--- | :--- |
| **資料生產邏輯** | `test/cases/test_data_productor.json` | 確保模擬器能正確讀取 CSV，且在請求「未來日期」或「無數據日期」時能正確回傳空集合或錯誤，而非崩潰。 |
| **傳輸邏輯** | `test/cases/test_data_sender.json` | 驗證資料發送器能正確處理 HTTP 狀態碼，並在 Downstream 離線時有適當的錯誤處理。 |
| **API 整合** | `test/cases/test_integration.json` | 定義 RESTful API 的各種邊界測試（如：結束日期早於開始日期、格式錯誤等）的標準 HTTP 回應碼 (400/422/500)。 |

---

## 🧩 設計權衡 (Design Trade-offs)

### 1. 為什麼 Simulator 設計為 API Service 而非 CronJob？
*   **支援多重時間軸 (Time Decoupling)**: 系統的「邏輯時間」可能與「物理時間」不同。透過 API 介面，外部排程器（如 `seed_data.sh` 或未來的 CronJob）可以自由決定要產生「哪一天」的數據，甚至在 10 分鐘內模擬一年的疫情演變。
*   **無狀態與擴展性**: 這種設計讓 Simulator 容器極其輕量且無狀態，隨時可以重啟或水平擴展，而不必擔心排程狀態遺失或重複執行。

### 2. 為什麼在 v0.2.0 引入 AsyncIO？
*   **解決 I/O 阻塞**: 舊版同步請求在模擬大量資料（如全台疫情爆發）時會因網路延遲而阻塞。改用 `AsyncIO` + `httpx` 並配合 `Semaphore` 控制併發數，顯著提升了資料注入的吞吐量 (Throughput)，確保壓力測試的有效性。

---

## 🚀 部署與維運
*   **Docker Image**: `safezone-pandemic-simulator`
*   **環境變數**:
    *   `INGESTOR_URL`: 下游服務地址
    *   `MAX_CONCURRENT_REQUESTS`: AsyncIO 併發控制閥值 (Default: 10)
*   **Health Check**: `GET /health` (回傳 JSON 包含 `status: healthy`)
