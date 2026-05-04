```markdown
# Analytics API（服務藍圖）

> ⚠️ **範圍警告**：本藍圖定義了 `analytics-api` 微服務。
> *繼承自 `archetype.blueprint.microservice.md`*

## 1. 責任與定位
*   **角色**：Reader / Aggregator / Gateway
*   **特性**：無狀態、高併發、讀取密集、唯讀
*   **核心目標**：作為系統的主要資料出口。根據使用者請求的地理層級（全國/城市/區域），從 PostgreSQL 聚合原始疫情事件。透過實作多層快取策略，確保在尖峰流量下仍能維持毫秒級別的回應時間。
*   **架構參考**：[Python Microservice Scaffold](safechord.safezone.service.python_scaffold.md)

## 2. 檔案結構
```text
SafeZone/services/analytics-api/
├── app/
│   ├── main.py                   # App Factory、Middleware、Lifespan
│   ├── api/                      # 路由層：HTTP 處理與依賴注入
│   ├── services/                 # 業務邏輯：聚合與快取（與 Web 框架解耦）
│   ├── core/                     # 設定與全域狀態（Settings、Lifecycle、Context）
│   └── exceptions/               # 領域例外與全域例外處理器
├── test/                         # TDD 收斂邊界（單元、整合、端到端）
├── Dockerfile                    # 正式環境映像檔建置
└── requirements.txt              # 正式環境依賴套件
```
*(注意：詳細的 Pydantic Models 與具體測試案例已於程式碼實作中；本文件僅定義業務邊界。)*

## 3. 業務需求

本服務的核心意圖是將複雜的關聯資料轉換為直覺的聚合視圖，同時在尖峰負載下維持高可用性。

### 3.1 核心查詢能力（功能層面）
提供跨三個地理維度查詢疫情資料的 HTTP 介面：
*   **全國**：指定時間區間內的整體全國趨勢。
*   **城市**：特定城市的疫情指標。
*   **區域**：特定行政區的細部資料。
*   **查詢彈性**：所有查詢都必須支援依時間區間、參考日期及選擇性計算（例如比率指標）進行過濾。
> *實作參考：查詢參數定義於程式碼中的 `app/api/endpoints.py`。*

### 3.2 效能與快取保護
*   **資料庫防護**：由於聚合查詢資源密集，必須具備強健的快取機制。所有相同的讀取請求必須由 Redis 攔截；在快取有效期間，嚴禁直接穿透至關聯式資料庫。

### 3.3 一致性與失效
*   **全域快取失效**：服務必須能夠感知底層資料的變更。當寫入管線更新原始資料並發布新的「快取版本」時，本服務必須將過時的快取標記為失效，以確保消費者不會收到過期的指標。

### 3.4 可觀測性與維運
*   **快取狀態追蹤**：每個 API 請求必須在 HTTP 標頭中明確標示其快取狀態（例如 `X-Cache-Status: Hit/Miss`），以供監控與分析使用。
*   **健康檢查**：必須提供健康檢查端點，供 Kubernetes 的 Liveness/Readiness 探測使用。

## 4. 相依關係與控制

| 相依項目 | 類型 | 說明 |
| :--- | :--- | :--- |
| **PostgreSQL** | 主要資料來源（唯讀） | 原始疫情事件來源。 |
| **Redis（快取）** | 儲存 | 儲存高頻聚合結果。 |
| **Redis（狀態）** | 控制器 | 監控全域 `current_cache_version` 以觸發失效。 |
| **Dashboard** | 客戶端 | 本服務的主要消費端。 |

## 5. TDD 收斂邊界

依據 KDD 哲學，服務的正確性由程式碼中的自動化測試強制保證。任何實作或修改都必須滿足這些「實體紅線」：

| 維度 | 限制意圖 | 測試範圍 |
| :--- | :--- | :--- |
| **聚合邏輯** | 確保跨時間區間與層級的結果與資料庫真實資料完全一致。 | `test/unit/` |
| **領域例外** | 確保業務失敗時擲出來自 `exceptions/` 的特定 Exception 實例，而非原始系統錯誤。 | `test/unit/` |
| **雪崩防護** | 在快取未命中時實作 Double-Check Locking，以避免相同請求同時湧入資料庫。 | `test/unit/`（快取服務） |
| **全域失效** | API 必須能正確識別過時快取，並在 `current_cache_version` 變更時強制重新計算。 | `test/integration/` |
| **合約穩定性** | 確保 HTTP 回應結構與 `X-Cache-Status` 標頭保持穩定。 | `test/integration/` |
| **錯誤轉譯** | 驗證全域處理器是否正確地將領域例外實例對應至標準 HTTP 狀態碼與 JSON 訊息。 | `test/integration/` |

## 6. 架構決策記錄 (ADR)

*   **[v0.3.1] 分層依賴注入**
    *   **決策**：將 `request.app.state` 存取方式替換為在 `api/dependencies.py` 中的顯式 DI。
    *   **原因**：犧牲少量開發速度以換取顯著的可測試性，使 `services/` 中的業務邏輯能夠保持框架無關。
*   **[v0.3.1] 純 ASGI Middleware**
    *   **決策**：將 `TraceAndCacheMiddleware` 從 `BaseHTTPMiddleware` 遷移至純 ASGI 介面。
    *   **原因**：解決 `ContextVar`（例如用於 `X-Cache-Status`）在多個任務群組間無法正確傳播的隔離問題，確保一致的可觀測性。
*   **[v0.2.0] 快取版本化與雪崩防護**
    *   **決策**：在 `@redis_cache` 裝飾器中實作基於 `asyncio.Lock` 的 Double-Check Locking。
    *   **原因**：防止在快取未命中時多個請求同時擊穿資料庫所造成的「快取雪崩」。
*   **[v0.2.0] 回應快取**
    *   **決策**：對所有聚合端點實作基於 Redis 的回應快取。
    *   **原因**：最小化 API 延遲，並在讀取密集的環境中為 PostgreSQL 提供防禦層。
*   **[v0.1.0] 記憶體內靜態資料預載**
    *   **決策**：在啟動時將低頻資料（城市/區域對應、人口基準值）預載入記憶體。
    *   **原因**：將複雜的 SQL JOIN 簡化為單純的事實表聚合，大幅提升查詢效能。

## 7. 外部連結
*   **GitHub Issues**：[相關 Issue 追蹤器連結]
```