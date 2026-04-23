---
title: 'Blueprint: Python Microservice Scaffold'
doc_id: safechord.safezone.service.python_scaffold
last_updated: '2026-04-23'
status: active
authors:
  - bradyhau
  - Gemini CLI
context_scope: SafeZone App Repo
summary: 定義 SafeZone 內所有 Python 微服務的標準內部目錄結構與分層架構 (Layered DI)。此為 v0.3.x 之後所有 Python 服務開發的單一真理來源 (SSOT)。
keywords:
  - Scaffold
  - Microservice
  - Dependency Injection
  - FastAPI
  - Architecture
logical_path: SafeChord.SafeZone.Service.PythonScaffold
related_docs:
  - safechord.safezone.md
  - safechord.roadmap.md
parent_doc: safechord.safezone
archetype: blueprint
doc_version: 0.3.1
---

# Blueprint: Python Microservice Scaffold

本文件定義 SafeZone 內部所有 Python 微服務的**標準內部目錄結構與分層規範**。這是一套「約定優於框架 (Convention over Framework)」的標準，旨在消除微服務間的架構熵增，確保 AI Agent 與人類工程師在跨服務開發時能擁有一致的 Context。

## 1. 範圍與邊界 (Scope & Boundaries)

### 本藍圖規範的範圍 (In-Scope)
* 單一 Python 微服務內部的目錄佈局 (Directory Layout)。
* 各層級 (Layer) 的職責與依賴注入 (DI) 規則。

### 本藍圖不規範的範圍 (Out-of-Scope)
* **跨服務契約 (Cross-service contracts)**: Pydantic models, DB schema, logging, tracing, event schemas。這些定義在 `utils/` git submodule 中。微服務**絕對不可**在內部重新定義已存在於 `utils/` 的模型。
* **部署構件 (Deployment artifacts)**: Dockerfile, Helm charts, CI pipelines 不在此限。
* **展示層 (Presentation Layer)**: 例如 Dashboard 服務 (預計遷移至 React SPA) 不適用此純後端 API 的 Scaffold。

---

## 2. 標準目錄結構 (Canonical Directory Layout)

任何新建或重構的 Python 微服務都必須嚴格遵守以下目錄結構：

```text
app/
├── main.py                 # Application Assembly
├── api/
│   ├── endpoints.py        # HTTP Transport Layer
│   └── dependencies.py     # DI Providers
├── services/               # Business Logic Layer (Framework-Free)
│   └── *.py
├── core/
│   ├── settings.py         # Environment Configuration
│   └── lifecycle.py        # Resource Lifecycle Management
└── exceptions/
    ├── custom.py           # Domain Exceptions
    └── handlers.py         # Framework Exception Handlers

test/
├── conftest.py             # Standardized Fixtures
├── unit/
│   └── test_*.py           # Fast isolated logic tests
├── integration/
│   └── test_*.py           # API level TestClient tests
├── cases/
│   └── *.json              # Data-driven test parameters
└── data/
    └── *                   # Static test assets (e.g. CSV)
```

---

## 3. 分層定義與嚴格守則 (Layer Definitions & Rules)

### 3.1 `app/main.py` — Application Assembly
* **職責**: 建立 FastAPI `app` 實例、掛載 router、註冊 middleware 與 lifespan。
* **守則**:
  * 必須是 `uvicorn` 的唯一進入點。
  * **禁止** 包含任何業務邏輯或定義 route handlers。

### 3.2 `app/api/endpoints.py` — HTTP Transport Layer
* **職責**: 定義 Route Handlers。負責將 HTTP 請求轉發給業務邏輯。
* **守則**:
  * Handler 只能做三件事：透過 `Depends()` 接收依賴、呼叫 `services/` 函式、回傳 Response。
  * **禁止** 包含業務邏輯（如資料轉換、迴圈、條件判斷）。
  * **禁止** 直接存取 `request.app.state`，必須透過 `dependencies.py` 注入。

### 3.3 `app/api/dependencies.py` — Dependency Injection Providers
* **職責**: 定義相容於 `Depends()` 的函式，從 `app.state` 提取資源並提供型別標註。
* **守則**:
  * 這是除了 `main.py` 之外，**唯一允許**存取 `request.app.state` 的檔案。
  * 每個 Provider 必須只回傳單一資源（如 `Session`, `RedisClient`）。

### 3.4 `app/services/` — Business Logic Layer 🚨 (核心約束)
* **職責**: 純粹的領域邏輯與業務運算。
* **絕對守則**: **此目錄下的任何檔案，絕對禁止 `import` 來自 `fastapi` 或 `starlette` 的模組。**
* **設計理念**: 所有相依資源（DB、Cache）都必須透過參數傳入 (DI via arguments)。這層的程式碼必須能在不依賴 FastAPI 的情況下進行單元測試，並為未來的 Go 語言遷移打下介面基礎。

### 3.5 `app/core/` — Settings & Lifecycle
* **`settings.py`**: 負責環境變數定義 (使用 `pydantic-settings`)。不包含連線邏輯。
* **`lifecycle.py`**: 實作 FastAPI `lifespan`。負責初始化共用資源 (DB Engine, Redis, Kafka Producer) 並存入 `app.state`，同時確保優雅關機 (Graceful Shutdown)。

---

## 4. 測試層規範 (Test Layer Specification)

測試是確保重構不致崩壞的唯一防線。

* **`test/conftest.py`**: 負責提供對應 `dependencies.py` 的 pytest fixtures。整合測試使用 FastAPI `TestClient`，單元測試則提供 Mock 資源。
* **`test/unit/`**: 針對 `services/` 層的單元測試。**禁止** import FastAPI 或使用 TestClient。必須具備亞秒級 (sub-second) 的回饋速度。
* **`test/integration/`**: 針對 `api/endpoints.py` 的整合測試。允許使用 `app.dependency_overrides` 抽換底層資源。
* **`test/cases/`**: 鼓勵使用 JSON 檔案驅動 (Data-driven) 的參數化測試。

---

## 5. 歷史遺留遷移對照表 (Migration Map)

對於舊有的服務（如 `data-ingestor` 或 `pandemic-simulator`），在升級至 v0.3.x 腳手架時，請依循以下對照表：

| 舊路徑 (Legacy) | 新路徑 (Scaffold) | 處理動作 (Action) |
| :--- | :--- | :--- |
| `pipeline/orchestrator.py` | `services/*.py` | 重新命名並重構 (移除 Request 依賴) |
| `pipeline/query_service.py` | `services/query_service.py` | 直接移動 |
| `config/settings.py` | `core/settings.py` | 直接移動 |
| `config/cache.py` | 分拆至 `services/` 與 `api/` | 將連線邏輯移入 `dependencies.py`，運算邏輯移入 `services/cache_service.py` |
| `test/tests/unit_test/` | `test/unit/` | 目錄攤平 |
| `test/tests/integration_test/`| `test/integration/` | 目錄攤平 |

---
> **Agent 指示**: 當建立新微服務或重構舊服務時，請務必將此文件載入 Context 作為結構檢核的唯一標準。