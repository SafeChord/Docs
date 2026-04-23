---
title: 'Service: Analytics API'
doc_id: safechord.safezone.service.analyticsapi
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-04-23'
summary: Analytics API 是 SafeZone 的數據查詢與分析核心。它提供 RESTful 介面供前端與 CLI 查詢疫情數據，並實作了基於版本控制
  (Cache Versioning) 的 Redis 快取策略與 In-Memory 預載優化，以實現極致的查詢效能。此服務也是 SafeZone 中第一個實作 Python Microservice Scaffold 的藍圖專案。
keywords:
  - Analytics API
  - FastAPI
  - Redis Cache
  - Global Invalidation
  - In-Memory Cache
  - Scaffold Blueprint
logical_path: SafeChord.SafeZone.Service.AnalyticsAPI
related_docs:
  - safechord.safezone.changelog.md
  - safechord.safezone.service.dashboard.md
  - safechord.safezone.service.worker.md
  - safechord.safezone.service.python_scaffold.md
parent_doc: safechord.safezone.service
archetype: blueprint
code_paths:
  - SafeZone/services/analytics-api
tech_stack:
  - Python 3.13
  - FastAPI 0.115
  - Redis (redis-py async)
  - SQLAlchemy 2.0 (Sync)
  - psycopg2-binary
doc_version: 0.3.1
app_version: 0.3.1
---

# Analytics API (Service Blueprint)

> ⚠️ **Scope Warning**: This blueprint defines the `analytics-api` microservice.
> *繼承自 `archetype.blueprint.microservice.md`*

## 1. 職責與定位 (Responsibility)
*   **角色**: Reader / Aggregator / Gateway
*   **特性**: Stateless, High-Concurrency, Read-Heavy
*   **核心目標**: 作為系統的數據出口。它將存儲於 PostgreSQL 中的原始疫情事件，根據使用者的地理層級 (National/City/Region) 需求進行即時聚合運算，並透過多層次快取機制確保在流量高峰時依然能提供毫秒級的回應速度。
*   **架構指標**: 作為 v0.3.1 Scaffold 標準化的第一站，本服務的架構設計是其他 Python 微服務的參考藍圖。

## 2. 檔案結構 (File Structure)
本服務嚴格遵循 [Python Microservice Scaffold](safechord.safezone.service.python_scaffold.md) 規範：
```text
SafeZone/services/analytics-api/
├── app/
│   ├── main.py                   # App Factory, Middleware, Lifespan
│   ├── api/
│   │   ├── endpoints.py          # RESTful Routes (Region/City/National)
│   │   └── dependencies.py       # DI Providers (DB Session, Cache Client)
│   ├── services/                 # Business Logic (Framework-Free)
│   │   ├── query_service.py      # SQLAlchemy Aggregation Logic
│   │   └── cache_service.py      # In-Memory Cache Loaders
│   ├── core/
│   │   ├── settings.py           # App Config & Redis/DB Settings
│   │   ├── lifecycle.py          # Resource Init & Cache Decorators
│   │   └── context.py            # ContextVar for Cache Status
│   └── exceptions/
│       ├── custom.py             # Domain Exceptions
│       └── handlers.py           # Custom Exception Handlers
├── test/                         # Comprehensive Testing Suite
│   ├── conftest.py               # Shared Test Fixtures
│   ├── unit/                     # Fast isolated logic tests
│   ├── integration/              # API End-to-End Tests
│   ├── cases/                    # JSON Spec for Verification
│   └── scripts/                  # Data seeder
├── Dockerfile                    # Production Environment Builder
├── Dockerfile.test               # CI/CD Test Environment Builder
├── requirements.txt              # Production Dependencies
└── requirements.test.txt         # Testing Dependencies
```

## 3. 接口規範 (Interfaces)

### 資料契約 (Contracts)
*   **Input Models**: `NationalParameters`, `CityParameters`, `RegionParameters` (定義於 `utils/pydantic_model/request.py`)。
*   **Output Models**: `AnalyticsAPIResponse` (定義於 `utils/pydantic_model/response.py`)。

### 輸入 (Ingress)
*   **Type**: API (HTTP GET)
*   **Source**:
    *   `GET /cases/national`: 獲取全國累計數據。
    *   `GET /cases/city`: 獲取特定城市的聚合數據。
    *   `GET /cases/region`: 獲取特定行政區的詳細數據。
    *   **Common Params**: `interval` (天數), `now` (基準日期), `ratio` (是否計算確診率)。

### 輸出 (Egress)
*   **Data Source**: PostgreSQL (Read-Replica 優先)。
*   **Cache Sink**: Redis (用於存儲聚合結果)。

## 4. 依賴與控制 (Dependencies & Control)

| 依賴對象 | 類型 | 說明 |
| :--- | :--- | :--- |
| **PostgreSQL** | Primary Source | 原始疫情數據存儲。 |
| **Redis (Cache)** | Storage | 存放 `@redis_cache` 生成的熱點數據結果。 |
| **Redis (State)** | Controller | 監聽 `current_cache_version` 以執行全域快取失效。 |
| **Dashboard** | Client | 本服務的主要消費者。 |

## 5. 行為驗證 (Behavior Verification)
本服務採用多層次驗證，確保聚合計算與快取行為的一致性。

| 範疇 | 驗證路徑 (Source of Truth) | 業務意圖 (Business Intent) |
| :--- | :--- | :--- |
| **業務邏輯** | `test/unit/` | 單元測試 `query_service` 與 `lifecycle`，確保邏輯隔離與快取鎖定機制正確。 |
| **API 整合** | `test/integration/` | 透過 `TestClient` 驗證 HTTP Headers (`X-Cache-Status`)、相依注入與路由。 |
| **快取一致性** | `SafeZone/scripts/ops/smoke_test.py` | **容器原生 E2E 劇本**：驗證跨服務的寫入後自動失效機制，確保前端不讀取過時數據。 |

## 6. 實作決策 (Implementation Decisions)

*   **Layered Dependency Injection (v0.3.1)**:
    *   **Decision**: 移除直接存取 `request.app.state` 的 Service Locator 模式，改為透過 `api/dependencies.py` 進行明確依賴注入。
    *   **Why**: 提升可測試性，並使 `services/` 層的程式碼完全脫離 FastAPI 框架耦合，為未來可能的 Go 語言遷移打下結構基礎。
*   **Pure ASGI Middleware (v0.3.1)**:
    *   **Decision**: 使用純 ASGI 介面實作 `TraceAndCacheMiddleware`。
    *   **Why**: 解決 `BaseHTTPMiddleware` 執行於不同子任務群組所導致的 `ContextVar` (如 `X-Cache-Status`) 隔離問題。
*   **Cache Versioning & Stampede Protection**:
    *   **Decision**: 實作背景版本同步，並在 `@redis_cache` 裝飾器中加入基於 `asyncio.Lock` 的 Double-Check Locking。
    *   **Why**: 防止快取失效瞬間大量相同請求擊穿資料庫 (Cache Stampede)。
*   **In-Memory Static Data Preloading**:
    *   **Decision**: 啟動時將城市/行政區 ID 對照表與人口數據全量載入記憶體。
    *   **Why**: 極大化查詢效能，將 SQL 簡化為對單一事實表的聚合。

## 7. 部署與維運 (Deployment & Ops)

*   **Docker Image**: `safezone-analytics-api`
*   **Health Check**: `GET /health` (回傳包含 `analytics-api: healthy`)
*   **Configuration**:
    *   **關鍵環境變數**:
        *   `DB_URL`: 資料庫連線字串。
        *   `REDIS_HOST/PORT`: 狀態 Redis 資訊。
        *   `CACHE_HOST/PORT`: 快取 Redis 資訊。
        *   `POLL_CACHE_VERSION_INTERVAL`: 預設 60s (生產建議縮短)。