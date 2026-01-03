---
title: SafeZone Helm Chart Architecture
doc_id: safechord.safezone.deployment.charts
version: 0.2.1
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
  - "safechord.safezone.service.md"
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
    *   **Ingress**：預先設定服務的對外曝光路徑與連線方式。

### 3. 🟢 Core Layer: `safezone-core`
包含核心業務邏輯與數據流處理。
*   **包含子 Charts**：
    *   `writePipeline`: 負責數據寫入路徑。
        *   `pandemic-simulator`: 模擬數據生成器 (掛載 PVC)。
        *   `ingestor`: 接收數據並轉發至 Kafka。
        *   `worker`: Kafka 消費者，負責寫入 DB。
                        *   **KEDA Integration**: 定義 `ScaledObject`，監控 Kafka Topic Lag。
                        *   **架構意義**: 作為 **速率緩衝橋樑 (Rate Buffering Bridge)**。Worker 負責調節 Kafka 高速吞吐量與遠端 Primary DB 寫入限制之間的速率差異 (Impedance Mismatch)，保護資料庫不被瞬間流量壓垮。
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
    *   `safezone-seed-data`: 寫入測試或預覽用的種子數據，以及 **生產環境冷啟動 (Cold Start) 數據**。
        *   **目的**：預先注入 30 天的歷史數據窗口，確保前端 Dashboard 在系統剛上線時即可呈現完整趨勢圖表，避免視覺上的空窗期。
*   **機制**：透過 **CI Pipeline (GitHub Actions)** 觸發，通常在部署流程的初始化階段執行。

---

## 💡 架構決策：為什麼採用分層 Chart 設計？

本專案不使用單一巨大的 Helm Chart，而是採用 **Umbrella Chart (分層依賴)** 模式，主要解決以下工程問題：

### 1. 解決依賴與啟動順序 (DAG Resolution)
服務之間存在嚴格的有向無環圖 (DAG) 依賴關係，分層設計能強制 GitOps (ArgoCD) 依循正確順序部署 (Sync Waves)：

*   **Stage 1: Infra (`safezone-infra`)**
    *   建立 ConfigMap, Secret, Ingress Controller 與 `cli-relay`。
    *   **目標**: 確保地基穩固，所有連線字串與基礎設施就緒。
*   **Stage 2: Bootstrap (`safezone-seed-init`)**
    *   執行 `szcli db init` (Schema Migration) 與 `szcli system time set` (Mock Time 設定)。
    *   **目標**: 確保 Core 服務啟動時，資料庫結構與全域時間服務已就緒，避免 CrashLoop。
*   **Stage 3: Core (`safezone-core`)**
    *   啟動 Ingestor, Worker, Analytics API 等核心服務。
    *   **目標**: 建立完整的數據處理 Pipeline。
*   **Stage 4: Data Warming (`safezone-seed-data`)**
    *   執行 `szcli dataflow simulate`，注入過去 33 天的歷史模擬數據。
    *   **依賴**: **必須在 Core 啟動後執行**，因為它依賴運作中的 Ingestion Pipeline 進行數據流轉。
*   **Stage 5: Experience (`safezone-ui`)**
    *   啟動 Dashboard 前端。
    *   **目標**: 確保使用者首次登入時，已有完整的歷史圖表可供瀏覽。

### 2. 資料生命週期編排 (Lifecycle Orchestration)
分離 `safezone-seed` 的不同子任務允許我們精細控制環境狀態：
*   **冷啟動防護**: 透過 `seed-init` 確保資料庫 Schema 優先於應用程式就緒。
*   **真實流量模擬**: `seed-data` 不僅是寫入靜態資料，而是透過 `szcli` 實際發送請求穿過系統 (Traffic Simulation)，這同時驗證了 Ingestor -> Kafka -> Worker -> DB 的完整路徑功能正常。

### 如何新增一個微服務？
1.  在 `SafeZone-Deploy/helm-charts` 下建立新的 Chart (或加入現有 Subchart)。
2.  在 `Chart.yaml` 中加入 `safezone-common` 依賴。
3.  在 `templates/_helpers.tpl` 中使用 `safezone-common` 的模板定義服務名稱。
4.  在對應的 Umbrella Chart (Core 或 Infra) 的 `Chart.yaml` 中加入該新 Chart 為依賴。

### 如何修改全域配置？
*   **不建議**直接修改 Library Chart。
*   **建議**修改對應環境的 Value File (例如 `deploy/preview/apps/values-preview.yaml`)，這將覆蓋預設值並觸發 ArgoCD 同步。
