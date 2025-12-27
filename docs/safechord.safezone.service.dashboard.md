---
title: "Service: Dashboard"
doc_id: safechord.safezone.service.dashboard
version: "0.2.1"
status: active
authors:
  - bradyhau
  - Gemini 2.5 Pro
last_updated: "2025-09-12"
summary: "Dashboard 是 SafeZone 的使用者互動介面，基於 Plotly Dash 構建。它具備「時光旅行」感知能力，能透過 Time Server 同步模擬時間，並將 Analytics API 的數據轉化為動態的疫情地圖與趨勢圖表。"
keywords:
  - Dashboard
  - Plotly Dash
  - Data Visualization
  - Time Travel
  - Interactive Map
logical_path: "SafeChord.SafeZone.Service.Dashboard"
related_docs:
  - "safechord.safezone.changelog.md"
  - "safechord.safezone.service.analyticsapi.md"
  - "safechord.safezone.toolkit.timeserver.md"
parent_doc: "safechord.safezone.service"
tech_stack:
  - Python 3.13
  - Plotly Dash 2.18
  - Dash Bootstrap Components
  - Pandas
  - Requests (Sync)
---

# Dashboard (v0.2.1)

## 📌 服務定位
Dashboard 是系統的 **視覺化呈現層 (Presentation Layer)**。
*   **角色**: Client / Consumer。
*   **特性**: Time-Aware, Stateless。
*   **職責**: 不直接連接資料庫，完全依賴 [Analytics API](safechord.safezone.service.analyticsapi.md) 獲取業務數據，並依賴 [Time Server](safechord.safezone.toolkit.timeserver.md) 獲取時間上下文。

---

## 🛠️ 核心規格 (Specifications)

### 1. 頁面佈局與互動
*   **核心組件**:
    *   **Risk Map**: 基於 `dash_leaflet` (或 Plotly Mapbox) 的互動式熱力圖，支援行政區層級下鑽。
    *   **Trend Chart**: 顯示當前模擬日期的前 7/14/30 天趨勢。
    *   **Global Timer**: 背景輪詢組件，負責同步系統時間。

### 2. 時間同步機制 (Time Sync)
Dashboard 不使用 `datetime.now()`，而是實作了「模擬時間同步」：
1.  **Polling**: 前端 `dcc.Interval` 每隔數秒觸發 Callback。
2.  **Sync**: 後端 `TimeManager` 呼叫 Time Server 的 `GET /now` 接口。
3.  **Update**: 若發現模擬時間變更（例如從 Day 1 跳轉至 Day 10），自動觸發所有圖表的數據重抓 (Re-fetch)。

### 3. 外部依賴與控制
*   **Upstream**: 
    *   [Analytics API](safechord.safezone.service.analyticsapi.md): 數據來源。
    *   [Time Server](safechord.safezone.toolkit.timeserver.md): 時間來源。
*   **Traceability**: 每次 API 呼叫皆會生成新的 `X-Trace-ID` (UUID v4)，以利全鏈路除錯。

---

## 🧪 行為驗證 (Behavior Verification)

| 範疇 | 測試策略 | 業務意圖 (Business Intent) |
| :--- | :--- | :--- |
| **API 整合** | `Integration Test` | 驗證 `api_caller.py` 能正確處理 Pydantic Model 的序列化與反序列化，並妥善處理 API 錯誤 (非 200 狀態)。 |
| **時間同步** | `Manual/E2E` | 在 CLI 執行 `time accelerate` 後，觀察 Dashboard 上的日期是否自動加速推進。 |

---

## 🧩 設計權衡 (Design Trade-offs)

### 1. 為什麼選擇 Plotly Dash？
*   **Python 全端體驗**: 允許資料科學家或後端工程師直接使用 Python 定義 UI 與互動邏輯 (`app/layout` + `app/callbacks`)，大幅降低了開發「資料密集型」儀表板的門檻。
*   **Pandas 整合**: API 回傳的 JSON 數據可直接轉為 DataFrame 進行二次處理（如計算移動平均），再送給 Plotly 繪圖。

### 2. 同步 API 呼叫 (`requests`)
*   **簡化邏輯**: Dash 的 Callback 預設是多執行緒 (Threaded) 的。使用同步 `requests` 雖然會阻塞單一執行緒，但在目前併發量下（主要為 Demo 用途），相比引入 `aiohttp` 與非同步 Callback 的複雜度，同步模式更易於維護。

---

## 🚀 部署與維運
*   **Docker Image**: `safezone-dashboard`
*   **環境變數**:
    *   `API_URL`: Analytics API 地址
    *   `TIME_SERVER_URL`: Time Server 地址
*   **Health Check**: `GET /` (檢查 HTML 回應)