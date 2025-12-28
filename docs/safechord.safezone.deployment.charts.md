---
title: SafeZone Helm Chart Architecture
doc_id: safechord.safezone.deployment.charts
version: 0.2.0
last_updated: "2025-12-28"
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
context_scope: "SafeZone-Deploy/helm-charts"
summary: "詳解 SafeZone 的 Helm Umbrella Chart 架構。包含基礎設施層 (Infra)、核心業務層 (Core) 與 UI 層的依賴關係、服務發現機制 (Common Library) 以及全域配置策略。"
keywords:
  - Helm
  - Umbrella Chart
  - Kubernetes
  - Architecture
  - Configuration
  - KEDA
logical_path: "SafeChord.SafeZone.Deployment.Charts"
related_docs:
  - "safechord.safezone.deployment.workflow.md"
  - "safechord.safezone.md"
parent_doc: "safechord.safezone"
---

# 📦 SafeZone Helm Chart 架構

SafeZone 的部署架構採用 **分層式 Umbrella Chart (Tiered Umbrella Strategy)** 設計。我們將系統拆分為三個獨立但有依賴順序的部署單元，以確保基礎設施就緒後才啟動業務邏輯。

> **注意**：本文檔專注於 Charts 的靜態結構與配置邏輯。關於 GitOps 部署流程與環境晉升，請參閱 [📄 Deployment Workflow](safechord.safezone.deployment.workflow.md)。

---

## 🏗️ 架構總覽 (High-Level Architecture)

系統由底層向上層依序堆疊，每一層都封裝為一個獨立的 Helm Chart。所有 Charts 共享一個基礎函式庫 `safezone-common` 以確保命名與服務發現的一致性。

以下是 `SafeZone-Deploy/helm-charts` 的實際結構視圖：

```text
helm-charts/
├── 📚 safezone-common/       # [Library] 共用的 Templates 與 Helpers (無實體資源)
├── 🔴 safezone-infra/        # [Umbrella] 基礎設施層 (Infrastructure Layer)
│   ├── cache/                # Redis Service (應用層快取)
│   ├── timeServer/           # Global Time Service (時間控制)
│   └── cliRelay/             # CLI Gateway (指令中繼站 & Auth)
├── 🟢 safezone-core/         # [Umbrella] 核心業務層 (Core Layer)
│   ├── writePipeline/        # 寫入路徑 Subchart
│   │   ├── pandemic-simulator
│   │   ├── ingestor
│   │   └── worker            # [Auto-Scaling] 整合 KEDA 監聽 Kafka Lag
│   └── readPipeline/         # 讀取路徑 Subchart
│       └── analytics-api
├── 🟡 safezone-ui/           # [Umbrella] 前端層 (UI Layer)
│   └── dashboard/            # Web Dashboard
└── ⚙️ safezone-seed/         # [Utilities] 初始化任務 (Jobs/Hooks)
```

---

## 🧩 組件詳解 (Component Details)

### 1. 📚 Library Layer: `safezone-common`
這是一個 **Library Chart**，不部署任何實際資源。
*   **職責**：定義全域通用的 `_helpers.tpl`。
*   **核心功能**：
    *   **服務發現 (Service Discovery)**：標準化生成 Service URL（例如 `http://safezone-analytics-api.namespace...`），讓跨 Chart 通訊不再依賴硬編碼。
    *   **標籤管理 (Labelling)**：統一管理 `app.kubernetes.io/*` 標籤，確保監控與 GitOps 追蹤的準確性。

### 2. 🔴 Infrastructure Layer: `safezone-infra`
負責部署支撐系統運作的平台級服務。它是整個應用程式的地基。
*   **包含子 Charts**：
    *   `cache`: 包裝 `bitnami/redis`，提供應用層快取。
    *   `timeServer`: 全域時間控制服務 (支援 Time-Travel 測試)。
    *   `cliRelay`: **API Gateway**。作為 `szcli` 進入叢集內部的安全通道，處理 Google OAuth 驗證並轉發指令。
*   **關鍵產出**：
    *   **Global ConfigMap (`safezone-config`)**：將上述服務的連線資訊匯總，供 Core 與 UI 層掛載使用。

### 3. 🟢 Core Layer: `safezone-core`
包含核心業務邏輯與數據流處理。
*   **包含子 Charts**：
    *   `writePipeline`: 負責數據寫入路徑。
        *   `pandemic-simulator`: 模擬數據生成器 (掛載 PVC)。
        *   `ingestor`: 接收數據並轉發至 Kafka。
        *   `worker`: Kafka 消費者，負責寫入 DB。
            *   **KEDA Integration**: 定義 `ScaledObject`，監控 Kafka Topic Lag。當堆積量超過閾值時，自動水平擴展 Pod 數量，消化突發流量。
    *   `readPipeline`: 負責數據讀取路徑。
        *   `analytics-api`: 提供數據查詢 API。

### 4. 🟡 UI Layer: `safezone-ui`
負責前端展示。
*   **包含子 Charts**：
    *   `dashboard`: 基於 Plotly Dash 的視覺化介面，讀取 `analytics-api` 的數據。

### 5. ⚙️ Utilities: `safezone-seed`
負責系統初始化與數據填充的短暫任務 (Jobs)。
*   **用途**：
    *   `safezone-seed-init`: 初始化資料庫 Schema。
    *   `safezone-seed-data`: 寫入測試或預覽用的種子數據。
*   **機制**：通常配合 ArgoCD Hooks 或 CI Pipeline 觸發。

---

## 🔧 配置介面 (Configuration Interface)

我們使用 **Global Values** 模式來管理跨 Chart 的共用設定。這使得在 `values-preview.yaml` 或 `values-staging.yaml` 中切換環境變得非常容易。

### 關鍵全域變數 (`global`)

在任何上層 `values.yaml` 中，您通常會看到以下結構：

```yaml
global:
  # 環境標識 (影響 Log Level, Debug 模式等)
  environment: "staging" 

  # 容器映像庫憑證
  ghcr:
    imagePullSecrets: "ghcr-pull-secret"

  # 外部服務連線 (Infrastructure dependencies)
  # 這些通常指向由 Terraform 或 Cloud Provider 提供的資源
  database:
    existingSecret: "k3han-db-secrets" # DB 連線字串
  redis:
    host: "bitnami-redis-master..."    # System Redis Host
    existingSecret: "k3han-redis-secrets"
  kafka:
    brokers: "kafka.svc..."            # Kafka Brokers
```

### 配置流轉機制
1.  **定義**：使用者在 Umbrella Chart (如 `safezone-core`) 的 `values.yaml` 中定義 `global.*`。
2.  **傳遞**：Helm 自動將 `global` 區塊傳遞給所有 Subcharts。
3.  **使用**：Subchart 的 Template (如 `deployment.yaml`) 讀取 `global.database.existingSecret` 並將其注入為 Pod 的環境變數 (`envFrom` / `valueFrom`)。

---

## 🧭 開發指南

### 如何新增一個微服務？
1.  在 `SafeZone-Deploy/helm-charts` 下建立新的 Chart (或加入現有 Subchart)。
2.  在 `Chart.yaml` 中加入 `safezone-common` 依賴。
3.  在 `templates/_helpers.tpl` 中使用 `safezone-common` 的模板定義服務名稱。
4.  在對應的 Umbrella Chart (Core 或 Infra) 的 `Chart.yaml` 中加入該新 Chart 為依賴。

### 如何修改全域配置？
*   **不建議**直接修改 Library Chart。
*   **建議**修改對應環境的 Value File (例如 `deploy/preview/apps/values-preview.yaml`)，這將覆蓋預設值並觸發 ArgoCD 同步。
