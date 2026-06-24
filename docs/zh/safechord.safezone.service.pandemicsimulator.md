# 疫情模擬器（服務藍圖）

## 1. 責任與定位
*   **角色**：Source / Generator
*   **特性**：被動觸發、無狀態、AsyncIO、唯讀（CSV）
*   **核心目標**：將靜態 CSV 疫情資料轉換為即時事件串流。它解決了開發與測試階段缺乏真實即時資料來源的問題，並為壓力測試整個 pipeline 提供精確可控的流量模擬。
*   **架構參考**：[Python Microservice Scaffold](safechord.safezone.service.python_scaffold.md)

## 2. 結構設計
*   **目錄結構**：遵循 [Python Microservice Scaffold](safechord.safezone.service.python_scaffold.md) 所定義的標準結構。
*   **技術棧**：Python 3.13, FastAPI 0.115, AsyncIO, Pandas。

## 3. 業務需求

該服務的核心意圖是提供一個靈活的「時光機」，讓系統能夠重播或預覽任何時間範圍的疫情資料流。

### 3-1 資料生成與重播（功能）
*   **每日重播**：從 CSV 中讀取特定日期的地理區域資料，並將其轉換為事件。
*   **區間重播**：支援跨多個日期的批次模擬，並嚴格依時間順序進行。

### 3-2 流量控制（效能）
*   **並發節流**：透過 `asyncio.Semaphore` 限制並發請求數，以防止下游 Ingestor 被壓垮。

### 3-3 韌性
*   **無效日期處理**：對不存在或未來的日期返回明確的錯誤碼。
*   **下游故障隔離**：即使個別 ingest 請求失敗，仍繼續批次處理。

### 3.4 可觀測性與營運
*   **技術標準**：遵循 [Python Microservice Scaffold](safechord.safezone.service.python_scaffold.md) 中定義的通用服務標準（可追溯性與健康檢查）。
*   **模擬回饋**：每次模擬請求應回傳成功與失敗傳輸的總數。

## 4. 依賴關係與控制

| 依賴項目 | 類型 | 說明 |
| :--- | :--- | :--- |
| **控制平面**（CLI） | 觸發器 | 主要啟動器，透過 SafeZone CLI 觸發。 |
| **本地檔案系統** | 來源（輸入） | 依賴環境特定的 `covid_data.csv`（根據環境掛載：`smoke-test`、`dev` 或 `staging`）。 |
| **資料攝取器** （Data Ingestor） | 下游（Sink） | 模擬資料的唯一接收端。 |

## 5. TDD 收斂邊界

對此服務的任何修改都必須滿足這些「實體紅線」：

| 維度 | 約束意圖 | 測試範圍 |
| :--- | :--- | :--- |
| **提取準確性** | 驗證 Productor 能精確提取給定日期的資料點，且欄位對映正確。 | `test/unit/` |
| **時間旅行有效性** | 確保「未來」或「超出範圍」的日期觸發正確的領域例外。 | `test/unit/` |
| **並發節流** | 驗證在高量資料爆發期間，sender 不會超過設定的 Semaphore 閾值。 | `test/unit/` |
| **HTTP 可靠性** | 確保 Sender 正確處理 Keep-Alive 並記錄下游 5xx 錯誤，且不停止程序。 | `test/integration/` |
| **端點驗證** | 驗證觸發參數（例如結束日期早於開始日期）回傳標準的 400/422 狀態碼。 | `test/integration/` |

## 6. 架構決策記錄（ADR）

*   **[v0.3.1] Python Microservice Scaffold 整合**
    *   **決策**：將舊有的 `pipeline/` 模組重構為 `services/` 與 `api/` 層。
    *   **原因**：標準化目錄結構，使其與 `analytics-api` 開發模型保持一致。

*   **[v0.2.1] 並發控制（Semaphore 管理）**
    *   **決策**：在 `data_sender.py` 中引入 `asyncio.Semaphore`。
    *   **原因（取捨）**：防止模擬器在發送數千筆資料點時耗盡系統檔案描述子（FD），同時為下游服務提供「背壓」保護。

*   **[v0.2.0] API 觸發模式**
    *   **決策**：放棄內部 CronJob，改用來自控制平面（CLI/TimeServer）的 REST API 觸發。
    *   **原因**：提高可控性，支援對任何時間點的手動重播，同時集中排程邏輯。

## 7. 外部連結
*   **資料來源**：`SafeZone/data/{smoke-test,dev,staging}/covid_data.csv`（按年份範圍區分：1970/2000/2023~）
*   **觸發工具**：[SafeZone CLI (szcli)](safechord.safezone.toolkit.cli.md)