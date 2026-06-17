# SafeZone 開發與 CI 工作流程

這份文件標準化了 `SafeZone`（應用程式）儲存庫的程式碼生命週期。我們的目標是確保每一行進入 `main` 分支的程式碼都經過完整測試、容器化且可部署。

---

## 1. Git 分支策略

我們採用標準的 GitFlow 模型，並針對自動化 CI/CD 觸發進行調整：

| 分支名稱 | 角色 | 保護機制 | 觸發動作 |
| :--- | :--- | :--- | :--- |
| **`main`** | **生產主線** | 🔒 僅限 PR | 發布正式 Release |
| **`dev`** | **開發主線** | 🔒 僅限 PR | 觸發 Smoke Test 套件 |
| **`feature/*`** | 功能開發 | 開放 | 本機測試 |
| **`release/*`** | 發布準備 | 開放 | 功能凍結 / 錯誤修正 |
| **`hotfix/*`** | 緊急修復 | 開放 | 立即合併至 Main / Dev |

> **開發人員守則**：所有新功能必須從 `dev` 分支出發，命名為 `feature/xxx`。完成後，發起 Pull Request（PR）合併回 `dev`，以觸發 CI 關卡。

---

## 2. 持續整合（CI Pipeline）

CI 扮演品質守門員的角色。我們使用 GitHub Actions（`smoke-test.yml`）來執行這個階段。

### 核心步驟（關卡）

1.  **動態版本標記**：提取 Git SHA（前 7 個字元）作為臨時版本標籤（例如 `0.3.2-a1b2c3d`）。
2.  **產出建置**：
    *   執行 `make build-all` 與 `make build-tool-cli`。
    *   在 GitHub Runner 中建置所有微服務以及 **Ops 測試映像檔**（`safezone-cli-ops`）。
3.  **Smoke 測試（容器原生）**：
    *   執行 `make smoke-test`。
    *   **架構**：測試引擎（`smoke_test.py`）運行在 `safezone-cli-ops` 容器內部，直接加入 Docker Compose 內部網路。
    *   **有狀態測試流程**：測試案例透過 CSV 定義，支援邏輯步驟相依性（例如 *模擬資料* ➡️ *驗證快取命中*）。
    *   **非同步事件驗證**：為處理系統非同步性（Kafka 延遲、資料庫寫入），引擎採用「適應性輪詢與重試」機制來驗證最終一致性，而非依賴靜態 sleep 計時器。
    *   **檢查點**：包含端到端資料持久化、快取生命週期檢查，以及自動化資料庫清理。

> **注意**：CI 階段的映像檔**不會**推送至 GHCR，僅保留在 Runner 快取中供測試使用。

---

## 3. 持續交付（CD / Release）

當程式碼準備好進行生產交付時，Release 工作流程（`release.yml`）就會被觸發。

### 觸發條件

*   推送一個符合 `v*.*.*` 模式的 Git Tag 到 `main` 分支。

### 執行步驟

1.  **Tag 驗證**：從 Tag 中提取正式版本號碼（例如 `0.3.2`）。
2.  **正式建置**：使用正式版本標籤重新建置所有服務。
3.  **映像檔發佈**：
    *   執行 `make push-all`。
    *   將正式映像檔推送至 **GitHub Container Registry（GHCR）**。這些產出隨後由 `SafeZone-Deploy` 儲存庫引用以進行部署。

---

## 4. 本地開發與測試

提交 PR 之前，開發人員**必須**在本機驗證邏輯。根據 v0.3.2 自動化改進，測試命令現在具備自我修復能力：

*   **單元測試與整合測試**：`make test-<服務名稱>`（例如 `make test-data-ingestor`）。
    *   **自動建置**：該指令會自動觸發 `make build-<服務名稱>`，確保測試執行在最新的容器映像檔上，無需手動預先建置。
    *   **標準化佈局**：所有 Python 服務遵循 Scaffold 標準，測試分為 `test/unit/`（邏輯）與 `test/integration/`（API）。
*   **全域驗證**：`make test-all`（執行所有服務測試）。
*   **本地整合**：`make dev-up`（啟動完整 Docker Compose 環境）。
    *   請參閱[環境演進](safechord.environment.md)了解如何利用 **Profiles**（`infra`/`core`）加快本地開發循環。