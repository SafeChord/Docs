# CLI 指令集 (szcli)

> **角色**：AI 操作手冊
> 本文件定義了 `szcli` 的標準操作程序。當代理程式被指派執行系統維護、資料模擬或健康檢查時，應優先採用本手冊所定義的指令範式。

---

## 1. 環境上下文

在呼叫 `szcli` 之前，請確保執行環境（Shell／Container）已配置以下變數：

| 變數 | 必要 | 說明 |
| :--- | :--- | :--- |
| `RELAY_URL` | ✅ | Relay Service 的內部或外部端點（例如 `http://cli-relay:8000`）。 |
| `REFRESH_TOKEN` | ✅ | 用於無頭驗證的 Google OAuth2 Refresh Token。 |
| `CLIENT_ID` | ✅ | GCP 專案的 Client ID。 |
| `CLIENT_SECRET` | ✅ | GCP 專案的 Client Secret。 |

---

## 2. 操作意圖（指令集）

### 🌊 Dataflow 操作

#### 意圖：觸發資料模擬
*   **使用情境**：產生測試資料、回填歷史記錄或執行壓力測試。
*   **指令**：
    ```bash
    szcli dataflow simulate <START_DATE> [--enddate <END_DATE>] [--dry-run]
    ```
*   **參數**：
    *   `START_DATE`：`YYYY-MM-DD`（必要）。
    *   `--enddate`：區間模擬的結束日期（選擇性）。
*   **預期行為**：
    *   成功：回傳 JSON `{"success": true, ...}`。Relay 會非同步觸發 Simulator Service。
    *   副作用：重設系統的全域快取版本（Cache Version）。

#### 意圖：驗證資料完整性
*   **使用情境**：煙霧測試驗證點、檢查資料持久性或觀察快取命中。
*   **指令**：
    ```bash
    # 標準驗證
    szcli dataflow verify <DATE> [--city <NAME>] [--interval <DAYS>]
    
    # 觀察快取狀態（詳細模式）
    szcli -o json -v dataflow verify <DATE>
    ```
*   **驗證邏輯**：
    *   解析回傳的 JSON。若 `total_cases > 0` 且 `success` 為 `true`，則視為管線運作正常。
    *   **快取檢查**：在 `-v` 模式下，檢查 JSON 輸出中的 `.headers.x-cache-status`。`HIT` 表示快取命中；`MISS` 表示穿透資料庫。
    *   若收到 `404` 或 `count == 0`（非預期），則假設為資料擷取延遲或 Worker 故障。

---

### ⚙️ 系統控制

#### 意圖：檢查系統健康狀態
*   **使用情境**：部署後自我檢查。
*   **指令**：
    ```bash
    szcli system health [TARGET]
    ```
*   **目標**：`all`（預設）、`cli-relay`、`db`、`redis-cache`、`simulator`、`ingestor`、`analytics-api`、`dashboard`。
*   **預期行為**：
    *   每個元件回傳 `status: healthy`。若有任何元件回傳 `unhealthy`，代理程式應將該任務標記為失敗。

#### 意圖：管理系統時間
*   **使用情境**：測試未來時間邏輯或重設回真實時間。
*   **指令**：
    ```bash
    # 設定模擬時間
    szcli system time set --mockdate <YYYY-MM-DD> --acceleration <INT>
    
    # 重設為真實時間
    szcli system time set --reset
    
    # 查看目前狀態
    szcli system time status
    
    # 取得目前系統日期
    szcli system time now
    ```

---

### 🗄️ 資料庫操作

> ⚠️ **警告**：這些是破壞性操作，僅限 `admin` 層級存取。

#### 意圖：初始化 Schema
*   **使用情境**：全新環境建置（冷啟動）。
*   **指令**：`szcli db init [--force]`

#### 意圖：清除資料
*   **使用情境**：保留 Schema 但移除所有業務資料（Truncate）。
*   **指令**：
    ```bash
    # 互動式執行
    szcli db clear
    
    # 自動化／非互動式執行
    szcli db clear --yes
    ```

#### 意圖：硬重置
*   **使用情境**：完整資料庫重置（Drop & Init）。
*   **指令**：`szcli db reset`

---

### ℹ️ 通用工具

#### 全域選項
*   `-o, --output [rich|json|yaml]`：設定輸出格式（預設：rich）。
*   `-v, --verbose`：顯示額外除錯資訊（例如 HTTP 標頭）。

#### 意圖：檢查版本資訊
*   **指令**：`szcli version`

#### 意圖：檢視設定
*   **指令**：`szcli config`

---

## 3. 錯誤處理

代理程式在解析 CLI 輸出時，必須遵循以下規則：

| 錯誤模式 | 解釋 | 建議動作 |
| :--- | :--- | :--- |
| `Refreshing authentication token...` | 資訊 | 正常驗證流程；忽略。 |
| `401 Unauthorized` | 驗證失敗 | 檢查 `REFRESH_TOKEN` 是否過期或無效。 |
| `403 Forbidden` | 權限不足 | 檢查已驗證的 `email` 是否在 Relay 白名單中。 |
| `Connection refused` | 網路錯誤 | 確認 `RELAY_URL` 是否正確，或檢查 Relay Pod 是否崩潰。 |