---
title: "Service: Dashboard"
doc_id: safechord.safezone.service.dashboard
version: "0.2.1"
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
last_updated: "2026-01-04"
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
archetype: blueprint
code_paths:
  - "SafeZone/services/dashboard"
tech_stack:
  - Python 3.13
  - Plotly Dash 2.18
  - Dash Bootstrap Components
  - Pandas
  - Requests (Sync)
---

# Dashboard (Service Blueprint)

> ⚠️ **Scope Warning**: This blueprint defines the `dashboard` microservice.
> *繼承自 `archetype.blueprint.microservice.md`*

## 1. 職責與定位 (Responsibility)
*   **角色**: Client / Visualizer
*   **特性**: Stateless, Time-Aware, Component-Based
*   **核心目標**: 作為使用者的可視化窗口。它將複雜的時序數據轉化為直觀的熱力圖 (Heatmap) 與趨勢線 (Trend Line)。系統的一個關鍵特性是 **「時間感知 (Time Awareness)」**：Dashboard 不依賴瀏覽器本地時間，而是根據 `Time Server` 的全域時鐘動態渲染過去或未來的模擬狀態。

## 2. 檔案結構 (File Structure)
```text
SafeZone/services/dashboard/
├── app/
│   ├── main.py                   # Entry Point (Dash App Initialization)
│   ├── layout/
│   │   └── dashboard_layout.py   # Global Layout Container
│   ├── components/               # [UI] Reusable UI Components
│   │   ├── map_chart.py          # Interactive Risk Map (Dash Leaflet/Mapbox)
│   │   ├── trend_chart.py        # Time Series Plot (Plotly Graph Object)
│   │   └── card.py               # Stat Cards
│   ├── callbacks/                # [Logic] Event Handlers
│   │   ├── register.py           # Callback Registry
│   │   ├── timer_callbacks.py    # Time Sync & Auto-Refresh Logic
│   │   └── risk_map_callbacks.py # Map Interaction Logic
│   ├── services/                 # [Infrastructure] External Communication
│   │   ├── api_caller.py         # HTTP Client for Analytics API (Traceable)
│   │   └── time_manager.py       # Time Sync Client with Fallback
│   └── config/
│       └── settings.py           # Env Loader
├── test/
│   ├── manual_test/              # UI Integration Scripts
│   └── unit_test/                # Logic Verification
├── Dockerfile                    # Production Environment Builder
├── Dockerfile.test               # CI/CD Test Environment Builder
├── requirements.txt              # Production Dependencies
└── requirements.test.txt         # Testing Dependencies
```

## 3. 接口規範 (Interfaces)

### 輸入 (Ingress)
*   **User Interaction**: 瀏覽器事件 (Clicks, Hover, Interval Ticks)。
*   **Endpoint**: `HTTP :8050` (Dash Default)。

### 輸出 (Egress)
*   **Analytics API**: `GET /cases/{national,city,region}`
    *   **Behavior**: 使用 `X-Trace-ID` 標記每個請求鏈路。
*   **Time Server**: `GET /now`
    *   **Behavior**: 每隔 N 秒 (可配置) 輪詢一次以同步系統時間。

## 4. 依賴與控制 (Dependencies & Control)

| 依賴對象 | 類型 | 說明 |
| :--- | :--- | :--- |
| **Analytics API** | Upstream | 數據來源。Dashboard 對其進行同步 HTTP 呼叫。 |
| **Time Server** | Upstream | 時間來源。若 Time Server 不可用，Dashboard 會 **Fallback** 至本地時間 (Resilience)。 |
| **User Browser** | Client | 負責渲染 Plotly.js 圖表並維持 WebSocket/HTTP 連線。 |

## 5. 行為驗證 (Behavior Verification)

| 範疇 | 驗證策略 | 業務意圖 (Business Intent) |
| :--- | :--- | :--- |
| **API 整合** | `unit_test/test_service/` | 驗證 `api_caller.py` 能正確序列化 Pydantic Request 並解析 API Response，包含錯誤處理。 |
| **時間同步** | `Manual/E2E` | 在 CLI 執行 `szcli time set` 後，觀察 Dashboard 右上角的日期顯示是否同步更新，且圖表數據隨之重繪。 |

## 6. 實作決策 (Implementation Decisions)

*   **Plotly Dash Framework**:
    *   **Decision**: 選擇 Dash 而非 React/Vue 等前端框架。
    *   **Rationale**:
        *   **Backend-Centric Efficiency**: 讓後端工程師能使用熟悉的 Python 堆疊快速構建可視化介面，將精力集中於核心資料流與系統穩定性。
        *   **Unified Stack**: 前後端共用 Python 生態系與 Docker 基礎映像檔，顯著簡化了 CI/CD Pipeline 與依賴管理。
*   **Time-Aware Polling Architecture**:
    *   **Decision**: 前端使用 `dcc.Interval` 觸發 Callback，後端 `TimeManager` 查詢 Time Server。
    *   **Why**: 為了支援「歷史回放」與「快進模擬」。系統必須與物理時間解耦，讓 Dashboard 成為一個可控時間軸的視窗。
*   **Resilience Strategy (Time Fallback)**:
    *   **Decision**: 當 `Time Server` 連線超時或錯誤時，自動降級使用 `date.today()`。
    *   **Why**: 確保即使輔助服務故障，核心展示功能 (針對真實日期) 仍然可用。

## 7. 部署與維運 (Deployment & Ops)

*   **Docker Image**: `safezone-dashboard`
*   **Health Check**: `GET /` (檢查 HTML 回應)
*   **Configuration**:
    *   **關鍵環境變數**:
        *   `API_URL`: Analytics API 地址。
        *   `TIME_SERVER_URL`: Time Server 地址。
        *   `UPDATE_INTERVAL`: 前端輪詢頻率 (ms)。