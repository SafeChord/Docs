# SafeZone 部署

> 「程式碼是負債，部署才是交付。」

本文定義 SafeZone 部署層背後的**架構意圖**。關於實作細節（Chart 結構、values、資源清單），請直接參考 `SafeZone-Deploy` 儲存庫。

---

## 導覽

| 主題 | 文件 | 重點 |
| :--- | :--- | :--- |
| **GitOps 工作流程** | [部署工作流程](safechord.safezone.deployment.workflow.md) | 分支推進、GitHub Actions 編排、回滾策略 |
| **環境策略** | [環境總覽](safechord.environment.md) | 本機 / 預覽 / 暫存層級、服務發現、Chorde PaaS 整合 |

> *實作參考：`SafeZone-Deploy/` 儲存庫 — Helm charts、ArgoCD 資源清單、部署腳本。*

---

## 邊界：應用層 vs. 部署層

*   **應用層 (`SafeZone`)**：產出不可變的 Docker 映像檔（成品）。
*   **部署層 (`SafeZone-Deploy`)**：宣告這些映像檔如何在各環境中執行（副本數、環境變數、資源、機密）。完全由 GitOps 驅動 — 每次提交都會觸發 ArgoCD 同步。

---

## ADR：分層 Umbrella Chart 策略

SafeZone 採用**分層 Umbrella Chart** 架構，而非單一的整體式 Helm chart，主要目的是強制部署順序並隔離故障域。

### 原因：基於 DAG 的部署順序

服務之間存在嚴格的**有向無環圖**（DAG）依賴關係。分層設計強制 ArgoCD 透過 Sync Waves 以正確順序部署：

| 階段 | 層級 | 意圖 |
| :--- | :--- | :--- |
| **1. 基礎設施** | 基礎架構（ConfigMap、Secret、Ingress、CLI Relay） | 確保所有連線字串與平台服務在應用啟動前準備就緒。 |
| **2. 引導** | Seed-Init（Schema 遷移、時間伺服器設定） | 防止核心服務因缺少資料庫 Schema 或時間狀態而 CrashLoop。 |
| **3. 核心** | 業務服務（寫入管線 + 讀取管線） | 建立完整的資料處理管線。 |
| **4. 資料預熱** | Seed-Data（透過即時管線注入歷史資料） | 注入 30 天以上的歷史資料，讓儀表板在首次載入時呈現有意義的圖表。**必須在 Core 之後執行**，因為依賴即時資料擷取管線。 |
| **5. 體驗** | UI（儀表板） | 面向使用者的層級 — 僅在後端資料準備就緒後才啟動。 |

### 原因：資料生命週期編排

將種子任務分離（init vs. data）可實現精細控制：

*   **冷啟動保護**：在任何應用 Pod 啟動前，Schema 遷移（`seed-init`）必須先完成。
*   **即時流量模擬**：`seed-data` 透過實際的資料擷取管線（Simulator → Ingestor → Kafka → Worker → DB）發送請求，同時作為端到端整合測試。

### 原因：KEDA 作為速率緩衝橋樑

Worker 服務整合 KEDA，根據 Kafka 消費者延遲自動擴展。這扮演了**速率緩衝橋樑**的角色 — 吸收 Kafka 高吞吐量擷取與遠端 Primary DB 寫入能力之間的阻抗不匹配，防止突發場景下的資料庫過載。