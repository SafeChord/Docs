# 流行病模擬器（服務藍圖）

> ⚠️ **範圍警告**：此藍圖定義了 `pandemic-simulator` 微服務。
> *繼承自 `archetype.blueprint.microservice.md`*

## 1. 職責與定位
*   **角色**：來源 / 產生器
*   **特性**：被動觸發、無狀態、AsyncIO、唯讀（CSV）
*   **核心目標**：將靜態的 CSV 流行病資料轉換為即時事件串流。它解決了開發與測試階段缺乏真實即時資料來源的問題，並為整個管線的壓力測試提供精確可控的流量模擬。
*   **架構參考**：[Python 微服務 Scaffold](safechord.safezone.service.python_scaffold.md)

## 2. 檔案結構
```text
SafeZone/services/pandemic-simulator/
├── app/
│   ├── main.py                   # App Factory 與路由註冊
│   ├── api/                      # 路由層：接收模擬觸發請求
│   ├── services/                 # 商業邏輯：Orchestrator、Productor（Pandas）、Sender（httpx）
│   ├── core/                     # 設定與全域狀態
│   └── exceptions/               # 領域例外與全域例外處理器
├── data/                         # 靜態資料來源目錄（掛載的 CSV）
├── test/                         # TDD 收斂邊界（單元、整合、端到端）
├── Dockerfile                    # 正式環境映像檔建構器
└── requirements.txt              # 正式環境相依套件
```
*（備註：詳細的資料產生邏輯與測試案例實作於程式碼庫中。）*

## 3. 商業需求

此服務的核心意圖是提供一個靈活的「時光機」，讓系統能重播或預覽任何時間區間的流行病資料流。

### 3-1 資料產生與重播（功能）
*   **每日重播**：從 CSV 中讀取特定日期的所有地理區域資料，並轉換為事件。
*   **區間重播**：支援跨多個日期的批次模擬，並依嚴格時間順序發送。
*   **資料活化**：確保產生的事件包含正確的 `event_time` 與 `payload`，符合 `CovidDataModel` 規格。

### 3-2 流量控制（效能）
*   **並行限制**：限制同時進行的請求數量，避免壓垮下游的 Ingestor。
*   **高效傳輸**：利用 AsyncIO 同時發送資料點，最小化 I/O 等待時間。

### 3-3 韌性
*   **無效日期處理**：當請求的日期不存在於 CSV 中或為未來日期時，服務應回傳空集合或明確的錯誤碼，而非崩潰。
*   **下游故障隔離**：若 Ingestor 回傳錯誤，Simulator 應記錄失敗並繼續處理批次中的其餘資料，以確保模擬完成。

### 3-4 可觀測性
*   **模擬回饋**：每次模擬請求應回傳成功與失敗傳送的總數。

## 4. 相依性與控制

| 相依項目 | 類型 | 說明 |
| :--- | :--- | :--- |
| **控制平面**（CLI） | 觸發器 | 主要啟動器，透過 SafeZone CLI 觸發。 |
| **本地檔案系統** | 來源（輸入） | 依賴掛載的 `covid_data.csv`。 |
| **資料 Ingestor** | 下游（接收端） | 模擬資料的唯一接收者。 |

## 5. TDD 收斂邊界

對此服務的任何修改都必須滿足下列「物理紅線」：

| 維度 | 約束意圖 | 測試範圍 |
| :--- | :--- | :--- |
| **萃取準確性** | 驗證 Productor 能精確萃取指定日期的資料點，且欄位對應正確。 | `test/unit/` |
| **時間旅行有效性** | 確保「未來」或「超出範圍」的日期會觸發正確的領域例外。 | `test/unit/` |
| **並行限制** | 驗證在高量資料突發時，sender 不會超過設定的 Semaphore 臨界值。 | `test/unit/` |
| **HTTP 可靠性** | 確保 Sender 正確處理 Keep-Alive，並記錄下游 5xx 錯誤而不中斷流程。 | `test/integration/` |
| **端點驗證** | 驗證觸發參數（例如結束日期早於開始日期）回傳標準的 400/422 狀態碼。 | `test/integration/` |

## 6. 架構決策記錄（ADR）

*   **[v0.3.1] Python 微服務 Scaffold 整合**
    *   **決策**：將舊有的 `pipeline/` 模組重構為 `services/` 與 `api/` 層。
    *   **原因**：標準化目錄結構，與 `analytics-api` 的開發模式一致。

*   **[v0.2.1] 並行控制（Semaphore 管理）**
    *   **決策**：在 `data_sender.py` 中引入 `asyncio.Semaphore`。
    *   **原因（取捨）**：避免 Simulator 在發送數千個資料點時耗盡系統檔案描述子（FD），同時為下游服務提供「背壓」保護。

*   **[v0.2.0] API 觸發模式**
    *   **決策**：放棄內部 CronJob，改由控制平面（CLI / TimeServer）透過 REST API 觸發。
    *   **原因**：提升可控性，支援任意時間點的手動重播，並將排程邏輯集中化。

## 7. 外部連結
*   **資料來源**：`SafeZone/data/covid_data.csv`
*   **觸發工具**：[SafeZone CLI (szcli)](safechord.safezone.toolkit.cli.md)