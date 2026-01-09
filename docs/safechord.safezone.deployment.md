---
title: "Map: SafeZone Deployment & Operations"
doc_id: safechord.safezone.deployment
version: 0.2.2
status: active
authors:
  - "bradyhau"
  - "Gemini 3 Pro"
last_updated: "2026-01-09"
summary: "SafeZone 部署與運維層的導航地圖。整合了 Helm Charts 架構定義與 GitOps 工作流程，指導如何將應用程式交付至不同環境。"
keywords:
  - Deployment
  - Operations
  - Helm
  - GitOps
  - SafeZone-Deploy
logical_path: "SafeChord.SafeZone.Deployment"
related_docs:
  - "safechord.safezone.deployment.charts.md"
  - "safechord.safezone.deployment.workflow.md"
  - "safechord.environment.md"
parent_doc: "safechord.safezone"
archetype: map
---

# SafeZone Deployment

> "Code is liability, Deployment is delivery."

本章節關注於 **SafeZone-Deploy** 倉庫的職責：如何將 `SafeZone` 產出的 Docker Images，轉化為 Kubernetes 上穩定運行的服務。

---

## 📚 核心文檔導航

| 模組 | 說明 | 關鍵字 |
| :--- | :--- | :--- |
| [**Helm Chart Architecture**](safechord.safezone.deployment.charts.md) | **靜態結構**。定義了 `safezone-infra`, `safezone-core`, `safezone-ui` 三層 Umbrella Chart 的依賴關係與全域配置策略。 | `Umbrella Chart`, `Configuration`, `Service Discovery` |
| [**GitOps Workflow**](safechord.safezone.deployment.workflow.md) | **動態流程**。定義了從 `deploy/preview` 到 `staging` 的晉升路徑，以及 **GitHub Actions 驅動** 的編排策略。 | `GitFlow`, `Promotion`, `ArgoCD`, `Preview Env`, `Orchestration` |

---

## 🏗️ 部署策略摘要 (v0.2.2)

在 v0.2.2 版本中，我們的部署策略針對 **非同步架構** 與 **數據生命週期** 進行了以下優化：

1.  **基礎設施優先 (Infra-First)**:
    *   透過 `safezone-infra` Chart 優先部署 **ConfigMap, Secret, Ingress Controller** 與 `CLI Relay`，為上層應用建立穩固的地基 (Foundation)。
    *   確保所有服務連線資訊 (Connection Strings) 在應用啟動前皆已就緒。

2.  **彈性伸縮 (Auto-Scaling)**:
    *   **Worker**: 整合 **KEDA (Kubernetes Event-driven Autoscaling)**。
    *   **Trigger**: 作為「速率緩衝橋樑」，監聽 Kafka Consumer Lag。當 `data-ingestor` 湧入大量模擬數據時，KEDA 自動擴展 `worker-golang` Pod 數量以調節寫入壓力。

3.  **精細化數據初始化 (Seeding)**:
    *   **Stage 2 (Init)**: 透過 `safezone-seed-init` 執行 Schema Migration 與 Mock Time 設定，防止應用層 Crash。
    *   **Stage 4 (Warming)**: 透過 `safezone-seed-data` 注入 **33 天歷史數據** (Cold Start Data)，確保 Dashboard 開箱即有豐富圖表呈現。

---

## 🔄 與 App 層的邊界

*   **App Layer (`SafeZone`)**: 負責產出 Immutable 的 Docker Image (Artifacts)。
*   **Deployment Layer (`SafeZone-Deploy`)**: 負責定義這些 Image 在不同環境 (Preview/Staging) 下的運行參數 (Replicas, Env Vars, Resources)。
