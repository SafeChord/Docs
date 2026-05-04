# 藍圖：Python 微服務 Scaffold

本文件定義了 SafeZone 中所有 Python 微服務的**標準化內部目錄結構與分層慣例**。這是一套「慣例勝於框架」的標準，旨在消除微服務之間架構上的混亂，確保 AI 代理人與人類工程師都能擁有一致的上下文。

## 1. 範圍與邊界

### 納入範圍
*   單一 Python 微服務的內部目錄佈局。
*   各層的責任與依賴注入（DI）規則。

### 不納入範圍
*   **跨服務合約**：Pydantic 模型、資料庫 Schema、日誌、追蹤與事件 Schema。這些由 `utils/` git submodule 定義。微服務**不得**重新定義已存在於 `utils` 中的模型。
*   **部署產物**：Dockerfile、Helm chart 與 CI pipeline 由其他規範管理。
*   **展示層**：儀表板服務（預計遷移至 React SPA）不遵循此僅限後端的 scaffold。

---

## 2. 標準目錄佈局

任何新建或重構的 Python 微服務必須嚴格遵守以下結構：

```text
app/
├── main.py                 # 應用程式組合
├── api/
│   ├── endpoints.py        # HTTP 傳輸層
│   └── dependencies.py     # DI 提供者
├── services/               # 業務邏輯層（不含框架）
│   └── *.py
├── core/
│   ├── settings.py         # 環境設定
│   └── lifecycle.py        # 資源生命週期管理
└── exceptions/
    ├── custom.py           # 領域例外
    └── handlers.py         # 框架例外處理器

test/
├── conftest.py             # 標準化 Fixtures
├── unit/
│   └── test_*.py           # 快速隔離的邏輯測試
├── integration/
│   └── test_*.py           # API 層級的 TestClient 測試
├── cases/
│   └── *.json              # 資料驅動的測試參數
└── data/
    └── *                   # 靜態測試資源（如 CSV）
```

---

## 3. 分層定義與嚴格規則

### 3.1 `app/main.py` — 應用程式組合
*   **責任**：初始化 FastAPI `app` 實例，掛載路由器，註冊中介層與生命週期。
*   **規則**：
    *   必須是 `uvicorn` 的唯一進入點。
    *   **禁止**：不得包含業務邏輯或直接定義路由處理函式。

### 3.2 `app/api/endpoints.py` — HTTP 傳輸層
*   **責任**：定義路由處理函式。將 HTTP 請求轉發至業務邏輯。
*   **規則**：
    *   處理函式應僅：透過 `Depends()` 接收依賴、呼叫 `services/` 中的函式、回傳 response。
    *   **禁止**：不得包含業務邏輯（例如資料轉換、迴圈、條件分支）。
    *   **禁止**：直接存取 `request.app.state`；應使用 `dependencies.py`。

### 3.3 `app/api/dependencies.py` — 依賴注入提供者
*   **責任**：定義與 `Depends()` 相容的函式，以型別提示從 `app.state` 中提取資源。
*   **規則**：
    *   這是除 `main.py` 之外**唯一**允許存取 `request.app.state` 的檔案。
    *   每個提供者必須回傳單一資源（例如 `Session`、`RedisClient`）。

### 3.4 `app/services/` — 業務邏輯層 🚨（核心限制）
*   **責任**：純領域邏輯與業務計算。
*   **絕對規則**：**此目錄中的檔案嚴格禁止從 `fastapi` 或 `starlette` 匯入模組。**
*   **設計哲學**：所有依賴資源（DB、Cache）必須以參數方式傳入（透過引數進行 DI）。此層必須能在沒有 FastAPI 的情況下進行單元測試，並作為未來可能遷移至 Go 的介面基礎。

### 3.5 `app/core/` — 設定與生命週期
*   **`settings.py`**：使用 `pydantic-settings` 處理環境變數定義。不含連接邏輯。
*   **`lifecycle.py`**：實作 FastAPI `lifespan`。初始化共享資源（DB Engine、Redis、Kafka Producer），存入 `app.state`，並確保優雅關閉。

---

## 4. 測試層規範

測試是重構時對抗迴歸的主要防線。

*   **`test/conftest.py`**：提供對應 `dependencies.py` 的 pytest fixtures。整合測試使用 FastAPI `TestClient`，單元測試則提供 mock 資源。
*   **`test/unit/`**：專注於 `services/` 層。**禁止**匯入 FastAPI 或使用 TestClient。必須維持次秒級的回饋速度。
*   **`test/integration/`**：專注於 `api/endpoints.py`。使用 `app.dependency_overrides` 替換底層資源。
*   **`test/cases/`**：鼓勵使用 JSON 檔案進行資料驅動的參數化測試。

---

## 5. 舊服務遷移對照表

將舊服務（例如 `data-ingestor` 或 `pandemic-simulator`）升級至 v0.3.x scaffold 時，請參考以下對照：

| 舊路徑 | Scaffold 路徑 | 操作 |
| :--- | :--- | :--- |
| `pipeline/orchestrator.py` | `services/*.py` | 重新命名並重構（移除 Request 依賴） |
| `pipeline/query_service.py` | `services/query_service.py` | 直接移動 |
| `config/settings.py` | `core/settings.py` | 直接移動 |
| `config/cache.py` | 拆分至 `services/` 與 `api/` | 將連線邏輯移至 `dependencies.py`，計算邏輯移至 `services/cache_service.py` |
| `test/tests/unit_test/` | `test/unit/` | 扁平化目錄 |
| `test/tests/integration_test/`| `test/integration/` | 扁平化目錄 |

---
> **AI 代理人指示**：當新建微服務或重構現有服務時，你必須將此文件載入你的上下文中，作為結構合規的唯一標準。