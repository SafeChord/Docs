---
title: "Toolkit: Time Server"
doc_id: safechord.safezone.toolkit.timeserver
version: "0.2.0"
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
last_updated: "2026-01-08"
summary: "Time Server 是 SafeZone 的時間中樞 (Time Nexus)。它負責維持全系統唯一的「模擬時間 (System Date)」，提供時光旅行 (Mock Date) 與時間加速 (Acceleration) 功能，使系統能脫離物理時間限制進行演練。"
keywords:
  - Time Server
  - Mock Time
  - Time Travel
  - Redis
  - FastAPI
logical_path: "SafeChord.SafeZone.Toolkit.TimeServer"
related_docs:
  - "safechord.safezone.toolkit.cli.md"
  - "safechord.safezone.service.dashboard.md"
parent_doc: "safechord.safezone.toolkit"
archetype: blueprint
code_paths:
  - "SafeZone/toolkit/time-server"
tech_stack:
  - Python 3.13
  - FastAPI
  - Redis (State Store)
---

# Time Server (Toolkit Blueprint)

> ⚠️ **Scope Warning**: This blueprint defines the `time-server` toolkit service.
> *繼承自 `archetype.blueprint.md`*

## 1. 職責與定位 (Responsibility)
*   **角色**: Time Nexus / Source of Truth (Time)
*   **特性**: Stateless Logic, Stateful Persistence (Redis)
*   **核心目標**:
    *   **時間去耦合**: 確保系統組件（Dashboard, Simulator）不依賴物理時間，而是向本服務請求當前「系統日期」。
    *   **時光旅行 (Time Travel)**: 支援手動設定「虛擬今天」，便於測試歷史數據或模擬未來場景。
    *   **時間加速 (Acceleration)**: 支援加速系統時間流速（如 1秒=1小時），用於壓力測試或縮短演練週期。

## 2. 檔案結構 (File Structure)
```text
SafeZone/toolkit/time-server/
├── app/
│   ├── main.py                   # Entry Point (FastAPI Factory)
│   ├── api/
│   │   └── endpoints.py          # REST Interface (/now, /set, /status)
│   └── config/
│       └── settings.py           # App Settings (Redis Config)
├── Dockerfile                    # Production Environment Builder
└── requirements.txt              # Service Dependencies
```

## 3. 接口規範 (Interfaces)

### 資料契約 (Contracts)
*   **Input**: `SetTimeModel` (定義於 `utils/pydantic_model/request.py`).
*   **Output**: `SystemDateResponse`, `MocktimeStatusResponse` (定義於 `utils/pydantic_model/response.py`).

### 輸入 (Ingress)
*   **Type**: API (HTTP)
*   **Endpoints**:
    *   `GET /now`: 獲取當前模擬日期。
    *   `POST /set`: 設定模擬參數（mock_date, acceleration）。
    *   `GET /status`: 獲取詳細的時間伺服器狀態與配置。

### 輸出 (Egress)
*   **State Store**: Redis (Hash Key: `safezone:mock_date:config`).

## 4. 核心邏輯 (Time Logic)

系統時間 (`system_date`) 的計算採用 **動態位移算法**，而非靜態儲存。

$$ SystemDate = MockDate + (CurrentTime - MockUpdateTime) \times Acceleration $$

> **⚠️ Implementation Status**:
> *   ✅ **時光旅行 (Mock Date)**: 已完整實作。設定後，系統會鎖定在該日期（若加速為 1，則隨時間平滑推進）。
> *   🚧 **時間加速 (Acceleration)**: 介面與資料庫Schema已預留欄位，但 **加速運算邏輯尚未完全實作**。目前系統預設倍率固定為 `1`。

*   **MockDate**: 使用者設定的模擬起始日期。
*   **MockUpdateTime**: 設定指令下達時的物理時間戳。
*   **Acceleration**: 步進倍率 (Reserved)。

## 5. 依賴與控制 (Dependencies & Control)

| 依賴對象 | 類型 | 說明 |
| :--- | :--- | :--- |
| **Redis** | Storage | 用於持久化配置。即使 Pod 重啟，模擬時間也會根據最後的位移參數繼續前進。 |
| **szcli** | Controller | 唯一受推薦的控制端，用於設定模擬參數。 |
| **Dashboard** | Consumer | 依賴本服務來決定圖表的起始點與「今天」的標記。 |

## 6. 行為驗證 (Behavior Verification)

> **⚠️ Note on QA**: 本服務定位為開發輔助工具，目前採 **Manual/E2E** 驗證模式。

| 範疇 | 驗證策略 | 業務意圖 (Business Intent) |
| :--- | :--- | :--- |
| **加速邏輯** | `Manual` | 設定 `acceleration=3600`，等待 2 秒後呼叫 `/now`，確認日期是否前進了 2 小時。 |
| **重置邏輯** | `Manual` | 執行 `POST /set {"mock": false}`，驗證 `/now` 是否立即回歸真實世界日期。 |

## 7. 部署與配置 (Deployment & Config)

*   **Docker Image**: `safezone-time-server`
*   **Configuration**:
    *   **REDIS_HOST/PORT**: Redis 連線資訊。
    *   **SERVICE_NAME**: 預設為 `time-server`。
