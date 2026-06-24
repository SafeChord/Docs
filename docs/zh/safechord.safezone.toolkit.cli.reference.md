# CLI 指令集 (szcli) - AI 優化操作手冊

> **角色**：AI 操作員參考手冊  
> 本文件定義 `szcli` 的確切指令、驗證規則、輸出結構以及複合操作 runbook。  
> **AI 操作員必須嚴格遵守此處定義的 schema 與指令組合。**

---

## 1. 環境與全域選項

在呼叫 `szcli` 之前，請確保以下環境變數已設定：
- `RELAY_URL`：Relay 服務的內部或外部端點（例如 `http://cli-relay:8000`）。
- `REFRESH_TOKEN`：用於無頭認證的 Google OAuth2 Refresh Token。
- `CLIENT_ID` / `CLIENT_SECRET`：GCP OAuth 憑證。

### 全域 CLI 旗標
任何指令都可以加上以下旗標來調整記錄與輸出格式：
- `-o, --output [rich|json|yaml]`：輸出顯示格式。**AI 代理應始終使用 `-o json` 以確保輸出可供程式化解析。**
- `-v, --verbose`：顯示通訊協定層級的中繼資料（例如 HTTP 標頭）。
- `-d, --debug`：啟用用戶端操作的除錯日誌。

### 🔴 重要：輸出 JSON 包裹（Envelope）
使用 `-o json` 執行指令時，輸出會先被客戶端包裝器包裹在一個標準信封結構中。  
- **目標資料**：底層的 `APIResponse` 內容永遠巢狀在 **`.response`** 鍵之下。  
- **標頭**：在 `-v` 模式中，API 的 HTTP 回應標頭會出現在 **`.headers`** 鍵之下（鍵名為小寫）。  
- **AI 路徑**：一律使用 `.response.<欄位>` 來查詢數值（例如 `.response.success` 或 `.response.data.aggregated_cases`）。直接查詢頂層欄位會得到 `null`。

---

## 2. 指令參考與 API 規格

### 🗄️ 資料庫操作（`db` 群組）
高權限資料庫維護操作。

#### 意圖：初始化 Schema
- **指令**：`szcli db init [--force]`
- **限制**：
  - `--force` 會清除所有資料表並重新植入管理與人口資料。不會刪除資料庫結構。
- **預期的包裹回應**：
  ```json
  {
    "task": {
      "name": "db.init",
      "trace_id": "8f2b3c1a-..."
    },
    "response": {
      "success": true,
      "message": "Database initialized successfully.",
      "detail": null,
      "errors": null,
      "timestamp": "2026-06-24T01:00:00Z"
    }
  }
  ```

#### 意圖：剪除資料（僅事實資料表）
- **指令**：`szcli db prune [--year YYYY] [--all] [--yes/-y]`
- **驗證規則**：
  - **XOR 要求**：必須且只能指定 `--year YYYY` 或 `--all` 其中之一。同時提供或兩者皆無會導致客戶端中止。
  - **確認**：若省略 `--yes`（或 `-y`），客戶端會提示確認。對於自動化腳本，務必加上 `--yes`。
- **副作用**：
  - 只針對 **`covid_cases` 事實資料表**。維度資料表（`cities`、`regions`、`populations`）不會受影響。
- **預期的包裹回應**：
  ```json
  {
    "task": {
      "name": "db.prune",
      "trace_id": "8f2b3c1a-..."
    },
    "response": {
      "success": true,
      "message": "Covid cases pruned successfully.",
      "detail": null,
      "errors": null,
      "timestamp": "2026-06-24T01:00:00Z"
    }
  }
  ```

#### 意圖：資料庫重置（截斷所有資料表）
- **指令**：`szcli db reset`
- **確認**：一定會以互動方式要求確認。（基於安全考量，不支援非互動式旗標。）
- **預期的包裹回應**：
  ```json
  {
    "task": {
      "name": "db.reset",
      "trace_id": "8f2b3c1a-..."
    },
    "response": {
      "success": true,
      "message": "Database reset successfully.",
      "detail": null,
      "errors": null,
      "timestamp": "2026-06-24T01:00:00Z"
    }
  }
  ```

---

### 🌊 Dataflow 操作（`dataflow` 群組）
控制攝入模擬器並驗證已持久化的資料。

#### 意圖：觸發模擬
- **指令**：`szcli dataflow simulate <DATE> [--enddate YYYY-MM-DD] [--dry-run]`
- **限制**：
  - `<DATE>`：攝入開始日期（必需參數，格式：`YYYY-MM-DD`）。
  - `--enddate`：可選的結束日期，用於區間生成。
- **預期的包裹回應**：
  ```json
  {
    "task": {
      "name": "dataflow.simulate",
      "trace_id": "8f2b3c1a-..."
    },
    "response": {
      "success": true,
      "message": "Simulation triggered successfully.",
      "detail": "Data ingestion process initiated.",
      "errors": null,
      "timestamp": "2026-06-24T01:00:00Z"
    }
  }
  ```

#### 意圖：驗證資料完整性
- **指令**：`szcli dataflow verify <DATE> [--interval INT] [--city NAME] [--region NAME] [--ratio]`
- **限制**：
  - `<DATE>`：目標驗證日期（必需參數，格式：`YYYY-MM-DD`）。
  - `--interval`：天數區間（預設：`1`）。
  - `--city` / `--region`：可選的字串篩選條件（後端驗證長度須為 1-50 個字元）。
  - `--ratio`：若設定，則回傳人口比例而非原始病例數。
- **預期的包裹回應（啟用 -v verbose）**：
  ```json
  {
    "task": {
      "name": "dataflow.verify",
      "trace_id": "8f2b3c1a-..."
    },
    "response": {
      "success": true,
      "message": "Verification completed.",
      "detail": null,
      "errors": null,
      "timestamp": "2026-06-24T01:00:00Z",
      "data": {
        "start_date": "1970-01-01",
        "end_date": "1970-01-01",
        "city": "台北市",
        "region": "信義區",
        "aggregated_cases": 1500,
        "cases_population_ratio": 0.015
      }
    },
    "headers": {
      "content-type": "application/json",
      "x-cache-status": "HIT"
    }
  }
  ```
- **快取斷言**：在 `-v` 模式中，檢查包裹 JSON 輸出的 `.headers["x-cache-status"]` 小寫鍵，判斷回應是否來自快取（值為 `HIT` 或 `MISS`）。

---

### ⚙️ 時間控制（`system time` 子群組）
控制虛擬系統時鐘。所有活躍元件都會查詢此時鐘。

#### 意圖：取得虛擬日期
- **指令**：`szcli system time now`
- **預期的包裹回應**：
  ```json
  {
    "task": {
      "name": "time.now",
      "trace_id": "8f2b3c1a-..."
    },
    "response": {
      "success": true,
      "message": "Current virtual time retrieved.",
      "detail": null,
      "errors": null,
      "timestamp": "2026-06-24T01:00:00Z",
      "system_date": "2000-01-01"
    }
  }
  ```

#### 意圖：取得虛擬時間設定
- **指令**：`szcli system time status`
- **預期的包裹回應**：
  ```json
  {
    "task": {
      "name": "time.status",
      "trace_id": "8f2b3c1a-..."
    },
    "response": {
      "success": true,
      "message": "Mock time config retrieved.",
      "detail": null,
      "errors": null,
      "timestamp": "2026-06-24T01:00:00Z",
      "data": {
        "mock": true,
        "mock_date": "2000-01-01",
        "mock_update_time": "2026-06-24T01:00:00Z",
        "launch_time": "2026-06-24T00:00:00Z",
        "acceleration": 5,
        "system_date": "2000-01-01"
      }
    }
  }
  ```

#### 意圖：設定虛擬時間
- **指令**：`szcli system time set [--reset] [--mockdate YYYY-MM-DD] [--acceleration INT]`
- **驗證規則**：
  - **Mock 限制**：除非指定 `--reset`，否則**必須**至少提供 `--mockdate` 或 `--acceleration` 其中一個。
  - **加速上下界**：`--acceleration` 必須是介於 **`1` 到 `10`**（含）之間的整數。
- **預期的包裹回應**：
  ```json
  {
    "task": {
      "name": "time.set",
      "trace_id": "8f2b3c1a-..."
    },
    "response": {
      "success": true,
      "message": "System time configured successfully.",
      "detail": null,
      "errors": null,
      "timestamp": "2026-06-24T01:00:00Z"
    }
  }
  ```

---

### 🩺 健康檢查（`health` 群組）
檢查叢集中各元件狀態。注意：這是獨立群組（`szcli health`），不屬於 `system` 之下。

#### 意圖：元件診斷
- **指令**：`szcli health <COMPONENT>`
- **有效元件**：
  - `all`, `cli-relay`, `db`, `redis-state`, `redis-cache`, `simulator`, `ingestor`, `analytics-api`, `dashboard`
- **預期的包裹回應**：
  ```json
  {
    "task": {
      "name": "health.all",
      "trace_id": "8f2b3c1a-..."
    },
    "response": {
      "success": true,
      "message": "Health check completed successfully.",
      "detail": null,
      "errors": null,
      "timestamp": "2026-06-24T01:00:00Z",
      "status": {
        "db": "healthy",
        "redis-state": "healthy",
        "simulator": "healthy"
      }
    }
  }
  ```

---

## 3. 標準失敗場景

當指令在客戶端、Relay 或下游層級失敗時，回應會解析 `errors` 結構：

### 常見驗證錯誤（例如無效的日期格式）
```json
{
  "task": {
    "name": "time.set",
    "trace_id": "8f2b3c1a-..."
  },
  "response": {
    "success": false,
    "message": "Validation failed.",
    "detail": "Invalid input format.",
    "errors": {
      "field": "mock_date",
      "summary": "Invalid value",
      "detail": "Invalid date format. Expected 'YYYY-MM-DD'."
    },
    "timestamp": "2026-06-24T01:00:00Z"
  }
}
```

---

## 4. AI Runbook 食譜（情境模式）

### Recipe A：乾淨冷啟動植入與驗證
由測試代理使用，從乾淨狀態開始，移動到目標時間，攝入資料，再進行驗證。

1. **執行資料庫重置**：
   ```bash
   szcli db reset
   # （需要互動確認，請手動執行）
   ```
2. **設定目標時間線**：
   ```bash
   szcli -o json system time set --mockdate 2000-01-01 --acceleration 5
   # 驗證 .response.success == true
   ```
3. **驗證空狀態**：
   ```bash
   szcli -o json dataflow verify 2000-01-01
   # 驗證 .response.success == true 且 .response.data.aggregated_cases == null
   ```
4. **觸發生成**：
   ```bash
   szcli -o json dataflow simulate 2000-01-01
   # 驗證 .response.success == true
   ```
5. **輪詢並驗證持久化**：
   ```bash
   szcli -o json dataflow verify 2000-01-01
   # 驗證 .response.success == true 且 .response.data.aggregated_cases > 0
   ```