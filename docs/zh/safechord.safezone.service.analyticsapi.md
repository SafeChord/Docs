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
*   **特性**: Stateless, High-Concurrency, Read-Heavy, Read-Only
*   **核心目標**: 作為系統的數據出口。它將存儲於 PostgreSQL 中的原始疫情事件，根據使用者的地理層級 (National/City/Region) 需求進行即時聚合運算，並透過多層次快取機制確保在流量高峰時依然能提供毫秒級的回應速度。
*   **架構參考**: [Python Microservice Scaffold](safechord.safezone.service.python_scaffold.md)

## 2. 檔案結構 (File Structure)
```text
SafeZone/services/analytics-api/
├── app/
│   ├── main.py                   # App Factory, Middleware, Lifespan
│   ├── api/                      # 路由層 (Routing Layer): 接收 HTTP 請求並進行參數解析與依賴注入
│   ├── services/                 # 業務邏輯層 (Business Logic): 聚合運算與快取策略 (與 Web 框架解耦)
│   ├── core/                     # 核心配置與全域狀態 (Settings, Lifecycle, Context)
│   └── exceptions/               # 領域異常定義與全域攔截器 
├── test/                         # TDD 收斂邊界 (包含 Unit, Integration, E2E)
├── Dockerfile                    # Production Environment Builder
└── requirements.txt              # Production Dependencies
```
*(註：詳細的 Pydantic Models 與具體的測試案例 (Test Cases) 皆實作於 Codebase 內，本文檔僅定義業務邊界。)*


## 3. 業務需求 (Business Requirements)

本服務的核心意圖是將底層龐雜的關聯式資料，轉化為前端可輕易消費的聚合視圖，並確保在高併發場景下的高可用性。

### 3-1 基礎查詢需求 (Functional)
提供 HTTP 介面供外部查詢疫情數據，必須支援以下三個地理維度的聚合查詢：
*   **National (全國層級)**：查詢指定時間區間內，全國的總體疫情趨勢。
*   **City (城市層級)**：查詢特定城市的疫情數據。
*   **Region (行政區層級)**：查詢最細粒度的行政區疫情數據。
*   **共通查詢條件 (Common Filters)**：所有路由皆須支援動態的「時間區間 (Interval)」、「基準日期 (Now)」以及「確診率計算開關 (Ratio)」。
> *實作參考 (Implementation Reference): 實際的路由定義請參閱 Codebase 中的 `app/api/endpoints.py`。*

### 3-2 效能需求 (Performance)
*   **快取保護機制**：由於聚合查詢極度消耗資料庫資源，系統必須實作完整的快取機制 (Cache Strategy)。所有相同的讀取請求，在快取有效期間內，必須直接由 Redis 攔截並回傳，嚴禁直接穿透至關聯式資料庫。

### 3-3 一致性需求 (Consistency)
*   **全域快取失效 (Global Invalidation)**：本服務必須能感知底層資料的異動。當寫入管線 (Write Pipeline) 更新了原始資料並發布新的「快取版本號 (Cache Version)」時，本服務必須具備機制，使舊版快取資料自動失效，確保前端不會讀取到過時的髒數據。

### 3-4 維運需求 (Observability & Ops)
*   **快取命中狀態追蹤**：每一個 API Request 都必須在 HTTP Header 中明確標示本次請求的快取狀態（如：`X-Cache-Status: Hit/Miss`），以供監控系統分析快取命中率。
*   **健康檢查 (Health Check)**：必須提供輕量級的 `/health` 端點，供 Kubernetes 探針 (Liveness/Readiness Probes) 確認服務存活狀態。

## 4. 依賴與控制 (Dependencies & Control)

| 依賴對象 | 類型 | 說明 |
| :--- | :--- | :--- |
| **PostgreSQL** | Primary Source (Read-Only) | 原始疫情數據存儲。本服務僅執行讀取操作。 |
| **Redis (Cache)** | Storage | 存放高頻存取的聚合結果。 |
| **Redis (State)** | Controller | 監聽全域的 `current_cache_version`。當底層資料異動時，依賴此狀態觸發全域快取失效。 |
| **Dashboard** | Client | 本服務的主要消費者。 |

## 5. TDD 收斂邊界 (Convergence Boundaries)

根據 KDD 哲學，本服務的正確性由 Codebase 中的自動化測試來定義與約束。AI 在實作或修改此服務時，必須確保滿足以下行為的測試覆蓋。這些測試是不可逾越的「物理紅牆」：

| 驗證維度 | 核心約束意圖 (Business Constraints) | Codebase 實作位置指標 |
| :--- | :--- | :--- |
| **聚合邏輯正確性** | 確保不同時間區間與地理層級的聚合計算結果，與資料庫真實狀態完全一致。 | `test/unit/` |
| **領域異常拋出 (Domain Exceptions)** | 確保當業務邏輯執行失敗或參數不合法時，能拋出定義於 `exceptions/` 下的專屬 Exception 實例 (Instance)，而非原生的系統錯誤。 | `test/unit/` |
| **快取擊穿防禦 (Stampede Protection)** | 在高併發且快取失效的瞬間，必須實作鎖定機制 (Double-Check Locking)，防止大量相同請求同時湧入並擊穿資料庫。 | `test/unit/` (針對 Cache Service) |
| **全域快取失效 (Global Invalidation)** | 當接收到新的 `current_cache_version` 狀態變更時，API 必須能正確識別舊快取已過期，並強制重新計算。 | `test/integration/` |
| **API 契約穩定性** | 確保 HTTP 回應格式符合約定的 Schema，並且 HTTP Headers 中能正確反映 `X-Cache-Status` (Hit/Miss)。 | `test/integration/` |
| **HTTP 錯誤碼轉換 (Error Handling)** | 確保所有拋出的 Domain Exception Instances 都能被全域攔截器 (Exception Handlers) 正確捕獲，並轉換為對應的 HTTP Status Code 與標準化錯誤訊息。 | `test/integration/` |

## 6. 架構決策紀錄 (Architecture Decision Records, ADR)

本節紀錄本服務在演進過程中的重大實作決策。這些決策解釋了「為什麼 (Why)」要這樣設計，作為後續重構或擴充時的重要上下文。

*   **[v0.3.1] 分層依賴注入 (Layered Dependency Injection)**
    *   **Decision**: 棄用直接存取 `request.app.state` 的 Service Locator 模式，全面改用 `api/dependencies.py` 進行明確的依賴注入 (DI)。
    *   **Why (Trade-off)**: 犧牲了一點開發的便捷性，換取極大的可測試性。這使得 `services/` 層的業務邏輯能夠完全脫離 FastAPI 框架的耦合，為未來可能的微服務遷移（如改用 Go 語言）打下良好的結構基礎。
*   **[v0.3.1] 純 ASGI 中介軟體 (Pure ASGI Middleware)**
    *   **Decision**: 捨棄常用的 `BaseHTTPMiddleware`，改以純 ASGI 介面實作 `TraceAndCacheMiddleware`。
    *   **Why (Trade-off)**: 解決了 `BaseHTTPMiddleware` 在不同非同步子任務群組 (Task Groups) 執行時，導致 `ContextVar` (如追蹤快取狀態的 `X-Cache-Status`) 無法正確跨層級傳遞的隔離問題，確保了可觀測性 (Observability) 資料的一致性。
*   **[v0.2.0] 快取擊穿防禦與版本控制 (Cache Versioning & Stampede Protection)**
    *   **Decision**: 在 `@redis_cache` 裝飾器中實作基於 `asyncio.Lock` 的雙重檢查鎖定 (Double-Check Locking) 機制，並引入背景版本同步。
    *   **Why (Trade-off)**: 在高併發且全域快取集體失效的瞬間，若無防護機制，會引發 Cache Stampede (快取雪崩) 導致大量相同請求直接擊穿 PostgreSQL。此設計確保了在快取失效時，相同的查詢只會有單一 Request 進入資料庫進行聚合運算，其餘 Request 則排隊等待該計算結果。
*   **[v0.2.0] 回應快取機制 (Response Caching)**
    *   **Decision**: 針對所有聚合查詢端點，全面導入 Redis 進行 API 回應快取。
    *   **Why (Trade-off)**: 由於本服務屬於 Read-Heavy 特性，關聯式資料庫的即時聚合運算成本極高。導入快取是用空間換取時間，旨在極小化 API 回應延遲，並為底層資料庫建立基礎的流量防護網。
*   **[v0.1.0] 記憶體靜態資料預載 (In-Memory Static Data Preloading)**
    *   **Decision**: 於應用程式啟動時 (Lifespan Lifecycle)，將變動頻率極低的「城市/行政區 ID 對照表」與「人口基準數據」全量載入 In-Memory 字典中。
    *   **Why (Trade-off)**: 犧牲了少量的伺服器記憶體空間與微秒級的啟動延遲，但成功將原本複雜的 SQL JOIN 操作，降維簡化為對單一事實表 (Fact Table) 的聚合計算，極大幅度地釋放了資料庫的查詢效能。

## 7. 外部連結
### github issue link
...