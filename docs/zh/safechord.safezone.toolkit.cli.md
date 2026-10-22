# SafeZone CLI（工具包藍圖）

SafeZone CLI（`szcli`）是系統編排的主要介面，透過安全的 Proxy 模式，銜接外部開發環境與內部叢集資源。

## 1. 職責與定位
*   **系統控制平面**：管理工作的統一入口，包含資料庫播種、觸發模擬及驗證系統狀態。
*   **安全閘道（Relay 模式）**：透過可信任的內部 API 轉送命令，保護內部基礎設施（PostgreSQL、Redis），不必直接轉送埠，也不必公開資料庫存取。
*   **驗證引擎**：內含**容器原生煙霧測試引擎（Container-Native Smoke Test Engine）**，使用 CSV 驅動的測試案例自動驗證端到端資料流。

## 2. 架構：Client-Relay 模式

不同於標準微服務，`szcli` 分為三個功能層：

### 2.1 Client（`command/`）
*   **技術**：Typer + Rich。
*   **角色**：處理使用者輸入、命令列引數及終端機呈現。
*   **認證**：管理**無頭 Google OAuth**。會自動處理 Token Refresh 邏輯，為 Relay 取得有效的 ID Token。
*   **可追蹤性**：擔任 **Trace ID 起點**。每次 `szcli` 執行都會產生新的 `uuid4` 作為 `trace_id`，注入所有記錄，並透過 `X-Trace-ID` 標頭轉送給 Relay。

### 2.2 Relay（`relay/`）
*   **技術**：FastAPI。
*   **角色**：在 Kubernetes 叢集內執行的可信任 Proxy。
*   **安全性**：驗證 Client 的 Google ID Token，並強制執行以允許清單為基礎的 RBAC。
*   **執行**：將已授權的 HTTP 請求轉換為對內部資料庫與服務的直接操作。

### 2.3 煙霧測試引擎（`ops/`）
*   **邏輯**：以 Python 執行引擎取代複雜的 Bash/JQ 腳本。
*   **機制**：依序執行斷言，並透過智慧輪詢處理最終一致性。如需測試案例模式的詳細清單，請參閱 [CLI 命令參考](safechord.safezone.toolkit.cli.reference.md)。

## 3. 技術需求與可觀測性

### 3.1 分散式可追蹤性
*   **起始要求**：CLI 必須啟動追蹤鏈。每個命令開始時，都會在全域情境中設定 `trace_id`。
*   **傳遞**：所有對 Relay 的請求都必須包含 `X-Trace-ID` 標頭。

### 3.2 命令模式
完整的命令、旗標及意圖導向指令集，請參閱 **[CLI 命令參考（指令集）](safechord.safezone.toolkit.cli.reference.md)**。此手冊是人類操作人員與 AI Agent 的主要依據。

## 4. 相依性與控制

| 相依項目 | 類型 | 說明 |
| :--- | :--- | :--- |
| **Google Identity** | 認證 | 用於 Relay 的身分驗證。 |
| **叢集資源** | 接收端 | Relay 需要直接存取 PostgreSQL 與 Redis。 |
| **時間伺服器** | 下游 | CLI 是虛擬時間設定的主要控制器。 |

---
> **Agent 指示**：此元件採用非標準目錄結構。修改 CLI 命令或 Relay 邏輯時，請確保遵循跨元件相依性（例如 `utils/` 中共用的 Pydantic 模型）。
