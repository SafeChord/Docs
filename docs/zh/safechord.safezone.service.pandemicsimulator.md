---
title: 'Service: Pandemic Simulator'
doc_id: safechord.safezone.service.pandemicsimulator
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
last_updated: '2026-01-04'
summary: Pandemic Simulator 是 SafeZone 資料流的源頭，負責將靜態的疫情數據轉換為動態的時間序列事件。本服務採用 AsyncIO
  架構，並由 SafeZone CLI 統一調度，支援歷史回放、系統初始化 (Seeding) 與每日排程等多種觸發模式。
keywords:
  - Pandemic Simulator
  - Data Generation
  - AsyncIO
  - Control Plane
  - Event Sourcing
  - System Seeding
logical_path: SafeChord.SafeZone.Service.PandemicSimulator
related_docs:
  - safechord.safezone.changelog.md
  - safechord.safezone.service.dataingestor.md
  - safechord.safezone.toolkit.cli.md
parent_doc: safechord.safezone.service
archetype: blueprint
code_paths:
  - SafeZone/services/pandemic-simulator
tech_stack:
  - Python 3.13
  - FastAPI
  - AsyncIO
  - httpx
  - Pandas
doc_version: 0.2.0
app_version: 0.2.1
---

# Pandemic Simulator (Service Blueprint)

> ⚠️ **Scope Warning**: This blueprint defines the `pandemic-simulator` microservice.
> *繼承自 `archetype.blueprint.microservice.md`*

## 1. 職責與定位 (Responsibility)
*   **角色**: Source / Generator
*   **特性**: Passive-Triggered, Stateless, AsyncIO
*   **核心目標**: 將靜態的 CSV 疫情數據「活化」為即時的事件流。解決了系統在開發與測試階段缺乏真實數據源 (Live Data Source) 的問題，並提供可控的流量壓力測試能力。

## 2. 檔案結構 (File Structure)
```text
SafeZone/services/pandemic-simulator/
├── app/
│   ├── main.py                   # Entry Point (FastAPI App Factory)
│   ├── api/
│   │   └── endpoints.py          # Route Definitions (/simulate, /health)
│   ├── pipeline/
│   │   ├── orchestrator.py       # Logic Controller
│   │   ├── data_productor.py     # CSV Reader & Slicer (Pandas)
│   │   └── data_sender.py        # Async HTTP Client (httpx)
│   └── config/
│       └── settings.py           # Env Loader
├── data/
│   └── covid_data.csv            # Data Source (Mount Point)
├── test/
│   ├── cases/                    # JSON Spec for Behavior Verification
│   │   ├── test_data_productor.json
│   │   ├── test_data_sender.json
│   │   └── test_integration.json
│   └── ...
├── Dockerfile                    # Production Environment Builder
├── Dockerfile.test               # CI/CD Test Environment Builder
├── requirements.txt              # Production Dependencies
└── requirements.test.txt         # Testing Framework & Dependencies (pytest, etc.)
```

## 3. 接口規範 (Interfaces)

### 資料契約 (Contracts)
*   **CovidDataModel**: 定義於 `utils/pydantic_model/request.py` (Shared Lib)。
    *   Fields: `date`, `city`, `region`, `cases`.

### 輸入 (Ingress)
本服務不開放公網存取，僅接受 Cluster 內部的觸發請求。
*   **Type**: API (HTTP GET)
*   **Source**:
    *   `GET /simulate/daily?date=YYYY-MM-DD`: 觸發單日模擬。
    *   `GET /simulate/interval?start_date=...&end_date=...`: 觸發區間模擬。
    *   `GET /health`: 健康檢查。

### 輸出 (Egress)
*   **Dest**: Data Ingestor Service (HTTP POST)
*   **Endpoint**: `${INGESTOR_URL}/covid_event`
*   **Protocol**: HTTP/1.1 (Keep-Alive via `httpx.AsyncClient`)

## 4. 依賴與控制 (Dependencies & Control)

| 依賴對象 | 類型 | 說明 |
| :--- | :--- | :--- |
| **Control Plane** (CLI) | Trigger | 負責喚醒服務。通常由 `szcli dataflow simulate` 指令觸發。 |
| **Local File System** | Source | 必須掛載 `/data/covid_data.csv`，否則服務無法啟動或執行。 |
| **Data Ingestor** | Downstream | 接收模擬數據的閘道。若 Ingestor 離線，Simulator 會記錄錯誤但不會崩潰。 |

## 5. 行為驗證 (Behavior Verification)
本服務採用 **Spec-as-Code** 策略。業務邏輯的正確性由 JSON 測試案例嚴格定義。

| 範疇 | 規格檔路徑 (Source of Truth) | 業務意圖 (Business Intent) |
| :--- | :--- | :--- |
| **資料生產邏輯** | `test/cases/test_data_productor.json` | 確保模擬器能正確讀取 CSV，且在請求「未來日期」或「無數據日期」時能正確回傳空集合或拋出 `EmptyDataError`。 |
| **傳輸邏輯** | `test/cases/test_data_sender.json` | 驗證 `AsyncClient` 能正確處理併發請求，並在 Downstream 回傳非 200 時記錄錯誤。 |
| **API 整合** | `test/cases/test_integration.json` | 定義 RESTful API 的邊界測試（如：結束日期早於開始日期、格式錯誤）應回傳標準 HTTP 400/422。 |

## 6. 實作決策 (Implementation Decisions)

*   **AsyncIO + Semaphore**:
    *   **Why**: 單日模擬可能包含數百個行政區的數據點。同步發送會導致巨大的 I/O Wait。
    *   **Trade-off**: 引入非同步增加了代碼複雜度，但透過 `asyncio.Semaphore` (由 `MAX_CONCURRENT_REQUESTS` 控制) 可以精確控制對 Downstream 的壓力，避免自我阻斷服務 (Self-DoS)。
*   **API Trigger vs CronJob**:
    *   **Why**: 為了支援「時光旅行」與「任意區間回放」，被動式的 API 設計比固定的 CronJob 更靈活。排程邏輯被上移至 `TimeServer` 或外部腳本。

## 7. 部署與維運 (Deployment & Ops)

*   **Docker Image**: `safezone-pandemic-simulator`
*   **Health Check**: `GET /health` (回傳 `{"status": {"simulator": "healthy"}}`)
*   **Configuration**:
    *   **關鍵環境變數**:
        *   `INGESTOR_URL`: 下游服務地址 (e.g., `http://data-ingestor:8000`).
        *   `MAX_CONCURRENT_REQUESTS`: 併發控制閥值 (Default: 10).
    *   **Volume Mount**:
        *   `/data/covid_data.csv`: **必須** 以 Read-Only 模式掛載。