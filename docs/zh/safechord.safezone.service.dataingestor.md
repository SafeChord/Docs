# 資料攝入器（服務藍圖）

> ⚠️ **範圍警告**：本藍圖定義 `data-ingestor` 微服務。
> *繼承自 `archetype.blueprint.microservice.md`*

## 1. 職責與定位
*   **角色**：Gateway / Producer (Kafka)
*   **特性**：無狀態、高吞吐量、事件驅動、唯寫
*   **核心目標**：作為所有疫情資料攝入的單一入口。專注於接收來自外部來源（例如模擬器或 CLI）的 HTTP 事件請求，執行結構性與業務約束驗證，並將其作為 `CovidContract` 訊息卸載至 Kafka 緩衝區，供下游消費。
*   **架構參考**：[Python 微服務 Scaffold](safechord.safezone.service.python_scaffold.md)

## 2. 檔案結構
```text
SafeZone/services/data-ingestor/
├── app/
│   ├── main.py                   # App Factory 與 Kafka Producer 生命週期
│   ├── api/                      # 路由層：Ingress 處理與 Schema 驗證
│   ├── services/                 # 業務邏輯：事件包裝與 Kafka 生產
│   ├── core/                     # 配置與 Kafka Producer 狀態管理
│   └── exceptions/               # 領域例外與全域例外處理器
├── test/                         # TDD 收斂邊界（單元測試、整合測試、端到端測試）
├── Dockerfile                    # 正式環境映像建置檔
└── requirements.txt              # 正式環境相依套件
```
*(注意：詳細的 Pydantic 模型與特定測試案例實作於程式碼庫中；本文件僅定義業務邊界。)*

## 3. 業務需求

本服務的核心意圖是提供一個高可用、低延遲的資料攝入視窗，將不受控的外部流量轉換為可管理的內部串流。

### 3.1 資料接收與驗證（功能性）
*   **單一入口**：提供標準 HTTP 介面，接收符合 `CovidDataModel` 的疫情事件。
*   **結構驗證**：使用 Pydantic 進行嚴格的型別檢查，防止格式錯誤的資料擴散至下游。
*   **合約包裝**：將原始酬載包裝成 `CovidContract`，其中包含 `trace_id`、`event_time` 與 `version` 等元資料。

### 3.2 效能與可靠性
*   **非同步解耦**：實作非同步 Producer，確保 HTTP 請求在訊息緩衝完成後立即回覆，無需等待下游處理。
*   **負載平衡**：使用 Kafka 作為中介，保護資料庫與運算叢集免受突發流量衝擊。

### 3.3 一致性與順序
*   **區域順序保證**：確保來自相同「城市-地區」的事件在傳輸過程中保持嚴格的時間順序，使 Worker 層能計算準確的累計統計資料。

### 3.4 可觀測性
*   **健康檢查**：必須提供反映 API 活性與 Kafka Producer 連線狀態的健康檢查端點。

## 4. 依賴與控制

| 依賴項目 | 類型 | 描述 |
| :--- | :--- | :--- |
| **上游** | 來源 | 產生原始資料的疫情模擬器或 CLI 工具。 |
| **Kafka 叢集** | 下游（Sink） | 事件緩衝的訊息佇列（主題名稱定義於程式碼庫中）。 |
| **控制平面** | 不適用 | 被外部請求觸發的被動 Gateway。 |

## 5. TDD 收斂邊界

對本服務的任何修改都必須滿足下列透過自動化測試強制執行的「實體紅線」：

| 維度 | 約束意圖 | 測試範圍 |
| :--- | :--- | :--- |
| **合約包裝** | 確保 `CovidContract` 包含所有必要的元資料，且酬載保持不變。 | `test/unit/` |
| **分區策略** | 驗證相同 `city-region` 的資料總是被對應到相同的分區鍵。 | `test/unit/` |
| **入口嚴格性** | 驗證格式正確的資料可以通過，格式錯誤的請求（422）則以標準錯誤訊息阻擋。 | `test/integration/` |
| **斷路器（Kafka）** | 當 Kafka 叢集不可用時，應拋出特定的領域例外，而非讓程序崩潰。 | `test/integration/` |
| **生命週期完整性** | 確保 Kafka Producer 在啟動時正確初始化，並在關閉時優雅停止，以避免訊息遺失。 | `test/integration/` |

## 6. 架構決策記錄 (ADR)

*   **[v0.3.1] 整合 Python 微服務 Scaffold**
    *   **決策**：將扁平目錄結構重構成 `api/core/services/exceptions` 分層模式。
    *   **原因**：統一 SafeZone 所有服務的開發方式，降低 AI 與人類工程師的認知負擔。

*   **[v0.2.1] 非同步生產（aiokafka）**
    *   **決策**：將 `aiokafka` 整合至 FastAPI 事件迴圈中。
    *   **原因**：解決因同步 Kafka 寫入導致的 HTTP 執行緒阻塞問題，大幅提升 Gateway 吞吐量。

*   **[v0.2.0] 自然鍵分區**
    *   **決策**：改用 `city-region` 作為 Kafka 分區鍵。
    *   **原因（取捨）**：雖然可能導致分區傾斜，但能保證區域資料嚴格的時間順序，這是後端精確統計的必要條件。

*   **[v0.2.0] 演進：從同步資料庫到事件驅動攝入**
    *   **決策**：移除直接寫入 PostgreSQL 的邏輯，改為 Kafka Producer。
    *   **原因（負載平衡）**：先前的同步模型將 Ingestor 的吞吐量與資料庫 IOPS 綁定。透過 Kafka 解耦，可為流量突發提供緩衝，並允許資料庫離線維護而不中斷資料攝入。

## 7. 外部連結
*   **重構追蹤**：[Issue #22: Refactor Data Ingestor to Golang](https://github.com/SafeChord/SafeZone/issues/22)（已規劃）