---
title: "Service: Analytics API"
doc_id: safechord.safezone.service.analyticsapi
version: "0.2.1"
status: active
authors:
  - bradyhau
  - Gemini 2.5 Pro
last_updated: "2025-09-12"
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
tech_stack:
  - Python 3.13
  - FastAPI 0.115
  - Redis (redis-py async)
  - SQLAlchemy 2.0 (Sync)
  - psycopg2-binary
---

# Analytics API (v0.2.1)

## 📌 服務定位
Analytics API 是系統的 **資料出口 (Read Gateway)**。
*   **角色**: Reader / Aggregator。
*   **特性**: High-Concurrency, Read-Heavy。
*   **職責**: 將底層關聯式資料庫 (PostgreSQL) 的原始數據，聚合為前端易於渲染的統計格式，並透過多層次快取保護資料庫。

---

## 🛠️ 核心規格 (Specifications)

### 1. API 接口與資料契約
*   **Endpoints**:
    *   `GET /cases/national`: 查詢全國聚合數據。
    *   `GET /cases/city`: 查詢特定城市的數據。
    *   `GET /cases/region`: 查詢特定行政區的詳細數據。
*   **Features**:
    *   支援 `ratio=true` 參數，自動計算「每萬人確診率」。

### 2. 快取策略 (Caching Strategy)
本服務實作了 **版本化快取 (Versioned Caching)** 與 **全域失效 (Global Invalidation)** 機制：
1.  **Cache Key**: `f"{version}:{endpoint}:{hash(params)}"`
2.  **Version Polling**: 背景任務每隔數秒從 `redis-state` 檢查 `current_cache_version`。
3.  **Invalidation**: 當 Worker 完成新一批數據寫入或 CLI 執行 `seed` 重置時，只需更新 Redis 中的 Version，所有 API 實例的舊快取即刻失效。
4.  **TTL**: 預設 24 小時 (86400s)，依賴版本號控制新鮮度。

### 3. 效能優化 (Optimization)
*   **In-Memory Lookups**: 啟動時將 `City/Region ID` 對照表與 `Population` 數據全量載入記憶體。SQL 查詢時完全不需要 Join 靜態表，僅需對單表 (`covid_cases`) 進行聚合。

### 4. 外部依賴與控制
*   **Upstream**: [Dashboard](safechord.safezone.service.dashboard.md) (Consumer).
*   **Data Source**: 
    *   Primary: [PostgreSQL] (Read-Replica 優先).
    *   Cache: [Redis].

---

## 🧪 行為驗證 (Behavior Verification)

| 範疇 | 規格檔路徑 | 業務意圖 (Business Intent) |
| :--- | :--- | :--- |
| **聚合邏輯** | `test/cases/test_query.json` | 驗證時間區間 (Interval) 與區域層級 (Level) 的聚合算法正確性。 |
| **快取行為** | `Code Review` | 驗證 `@redis_cache` Decorator 是否正確處理 Cache Miss/Hit 並寫入 Redis。 |

---

## 🧩 設計權衡 (Design Trade-offs)

### 1. 為什麼選擇 Sync SQL Driver (`psycopg2`)？
*   **複雜查詢穩定性**: 雖然 `asyncpg` 效能更佳，但在處理 SQLAlchemy 複雜聚合查詢時，同步驅動的相容性與除錯容易度較高。由於我們有 Redis 快取層擋在前面，DB 連線的非同步化並非首要瓶頸。

### 2. 為什麼實作 Cache Versioning？
*   **解決 Cache Stampede 與一致性問題**: 在舊版 TTL 機制中，難以精確控制「數據剛寫入 DB，但 API 還在回傳舊快取」的時間差。版本化機制允許寫入端 (Worker/CLI) 精確通知讀取端 (API) 進行更新，達成近乎即時的資料一致性。

---

## 🚀 部署與維運
*   **Docker Image**: `safezone-analytics-api`
*   **環境變數**:
    *   `DB_URL`: PostgreSQL 連線字串
    *   `REDIS_HOST`, `REDIS_PORT`: Redis 連線資訊
    *   `POLL_CACHE_VERSION_INTERVAL`: 版本輪詢間隔 (Default: 5s)
*   **Health Check**: `GET /health`