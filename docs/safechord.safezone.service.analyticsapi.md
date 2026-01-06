---
title: "Service: Analytics API"
doc_id: safechord.safezone.service.analyticsapi
version: "0.2.1"
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
last_updated: "2026-01-04"
summary: "Analytics API 是 SafeZone 的數據查詢與分析核心。它提供 RESTful 介面供前端與 CLI 查詢疫情數據，並實作了基於版本控制 (Cache Versioning) 的 Redis 快取策略與 In-Memory 預載優化，以實現極致的查詢效能。"
keywords:
  - Analytics API
  - FastAPI
  - Redis Cache
  - Global Invalidation
  - In-Memory Cache
logical_path: "SafeChord.SafeZone.Service.AnalyticsAPI"
related_docs:
  - "safechord.safezone.changelog.md"
  - "safechord.safezone.service.dashboard.md"
  - "safechord.safezone.service.worker.md"
parent_doc: "safechord.safezone.service"
archetype: blueprint
code_paths:
  - "SafeZone/services/analytics-api"
tech_stack:
  - Python 3.13
  - FastAPI 0.115
  - Redis (redis-py async)
  - SQLAlchemy 2.0 (Sync)
  - psycopg2-binary
---

# Analytics API (Service Blueprint)

> ⚠️ **Scope Warning**: This blueprint defines the `analytics-api` microservice.
> *繼承自 `archetype.blueprint.microservice.md`*

## 1. 職責與定位 (Responsibility)
*   **角色**: Reader / Aggregator / Gateway
*   **特性**: Stateless, High-Concurrency, Read-Heavy
*   **核心目標**: 作為系統的數據出口。它將存儲於 PostgreSQL 中的原始疫情事件，根據使用者的地理層級 (National/City/Region) 需求進行即時聚合運算，並透過多層次快取機制確保在流量高峰時依然能提供毫秒級的回應速度。

## 2. 檔案結構 (File Structure)
```text
SafeZone/services/analytics-api/
├── app/
│   ├── main.py                   # Entry Point (App Factory & Lifespan Tasks)
│   ├── api/
│   │   └── endpoints.py          # RESTful Routes (Region/City/National)
│   ├── pipeline/
│   │   ├── orchestrator.py       # Logic Coordinator
│   │   └── query_service.py      # SQLAlchemy Aggregation Logic
│   ├── config/
│   │   ├── cache.py              # Cache Decorators & Version Poller
│   │   └── settings.py           # App Config & Redis/DB Settings
│   └── exceptions/
│       └── handlers.py           # Custom Exception Handlers
├── test/                         # Comprehensive Testing Suite
│   ├── tests/
│   │   ├── unit_test/            # Query Logic Tests
│   │   └── integration_test/     # API End-to-End Tests
│   └── cases/                    # JSON Spec for Verification
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
| **聚合算法** | `test/tests/cases/test_query_service.json` | 驗證 `SUM(cases)` 與 `ratio` 計算在不同地理層級下的正確性。 |
| **快取一致性** | `SafeZone/scripts/smoke-test.sh` | **自動化 E2E 劇本**：執行 `test_cache_invalidation_flow`，驗證「寫入後自動失效」機制，確保前端不讀取過時數據。 |
| **API 整合** | `test/tests/cases/test_integration.json` | 驗證 RESTful 介面的邊界條件與錯誤回應碼。 |

## 6. 實作決策 (Implementation Decisions)

*   **Cache Versioning & Global Invalidation**:
    *   **Decision**: 實作 `poll_cache_version` 背景任務，每 60s 同步 Redis 中的版本號。
    *   **Why**: 在微服務架構中，傳統的 TTL 失效難以保證資料一致性。透過版本號控制，我們可以在 Worker 完成寫入後立即通知所有 API 實例將舊快取視為無效，達成「近乎即時」的一致性。
*   **In-Memory Static Data Preloading**:
    *   **Decision**: 啟動時將城市/行政區 ID 對照表與人口數據全量載入記憶體。
    *   **Why**: 疫情數據表 (`covid_cases`) 巨大，避免在查詢時執行複雜的 `JOIN` 運算。透過記憶體 Lookups，將 SQL 簡化為對單一事實表的聚合，極大化查詢效能。
*   **Future Roadmap**:
    *   詳見 [Issue #24: Scalability Strategy for Analytics API](https://github.com/SafeChord/SafeZone/issues/24)。
    *   **Trigger**: 當應用層 CPU 成為瓶頸且資料庫負載仍低時啟動評估。
    *   **Strategy**: 若業務邏輯維持單純聚合，優先考慮遷移至 Golang；若涉及 Pandas 等複雜分析，則考慮服務拆分或 Async Driver 優化。

## 7. 部署與維運 (Deployment & Ops)

*   **Docker Image**: `safezone-analytics-api`
*   **Health Check**: `GET /health` (回傳包含 `analytics-api: healthy`)
*   **Configuration**:
    *   **關鍵環境變數**:
        *   `DB_URL`: 資料庫連線字串。
        *   `REDIS_HOST/PORT`: 狀態 Redis 資訊。
        *   `CACHE_HOST/PORT`: 快取 Redis 資訊。
        *   `POLL_CACHE_VERSION_INTERVAL`: 預設 60s (生產建議縮短)。