---
title: "SafeZone Toolkit: Time Server"
doc_id: safechord.safezone.toolkit.timeserver
version: "0.2.0"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
last_updated: "2025-05-19"
summary: "Time Server 是 SafeZone 的時間中樞 (Time Nexus)。它負責維持全系統唯一的「模擬時間 (System Date)」，並提供時光旅行 (Mock Date) 與時間加速 (Acceleration) 功能，使系統能脫離物理時間的限制進行演練。"
keywords:
  - Time Server
  - Mock Time
  - Time Travel
  - Redis
  - FastAPI
logical_path: "SafeChord.SafeZone.Toolkit.TimeServer"
related_docs:
  - "safechord.safezone.service.dashboard.md"
  - "safechord.safezone.toolkit.cli.md"
parent_doc: "safechord.safezone.toolkit.cli"
tech_stack:
  - Python 3.13
  - FastAPI
  - Redis
---

# Time Server (v0.2.0)

## 📌 服務定位
Time Server 是系統的 **時間控制塔 (Time Control Tower)**。
*   **角色**: Source of Truth (Time)。
*   **特性**: Stateless Logic, Stateful Config (Redis)。
*   **職責**: 當系統處於「模擬模式 (Mock Mode)」時，所有時間敏感的組件（如 Dashboard, Simulator）必須向 Time Server 請求當前時間，而非使用本地系統時間。

---

## 🛠️ 核心規格 (Specifications)

### 1. 時間計算邏輯 (Time Logic)
系統時間 (`system_date`) 的計算並非靜態存儲，而是基於「相對位移」動態計算：

$$ SystemDate = MockDate + (Now - LastUpdateTime) \times Acceleration $$

*   `MockDate`: 使用者設定的起始模擬日期 (e.g., 2020-01-01)。
*   `LastUpdateTime`: 上次設定指令的時間戳。
*   `Acceleration`: 時間流速倍率 (e.g., 2 代表現實過 1 秒，模擬過 2 秒)。

### 2. API 接口
*   `GET /now`: 獲取當前模擬時間。
    *   Response: `{"system_date": "YYYY-MM-DD"}`
*   `POST /set`: 設定模擬參數。
    *   Payload: `{"mock": true, "mock_date": "...", "acceleration": 2}`
*   `GET /status`: 獲取完整配置狀態。

### 3. 外部依賴
*   **Storage**: Redis (Key: `safezone:mock_date:config`)。用於持久化配置，確保 Pod 重啟後模擬狀態不丟失。

---

## 🧪 行為驗證 (Behavior Verification)

| 範疇 | 測試策略 | 業務意圖 (Business Intent) |
| :--- | :--- | :--- |
| **加速邏輯** | `E2E Test` | 設定 `acceleration=3600` (1小時/秒)，等待 2 秒，驗證 `GET /now` 是否推進了約 2 小時。 |
| **重置邏輯** | `API Test` | 呼叫 `POST /set {"mock": false}`，驗證 `GET /now` 是否立即回歸真實世界時間。 |

---

## 🚀 部署與維運
*   **Docker Image**: `safezone-time-server`
*   **環境變數**:
    *   `REDIS_HOST`, `REDIS_PORT`: Redis 連線資訊。