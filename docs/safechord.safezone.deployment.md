---
title: "SafeZone: Deployment & Operations Overview"
doc_id: safechord.safezone.deployment
version: "0.2.1"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
last_updated: "2025-12-28"
summary: "SafeZone 的部署與運維層總覽。本文件作為 Delivery Layer 的入口，整合了 Helm Charts 架構定義與 GitOps 工作流程，指導如何將應用程式安全、可控地交付至 Staging 與 Production 環境。"
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
---

# SafeZone Deployment (v0.2.1)

> "Code is liability, Deployment is delivery."

本章節關注於 **SafeZone-Deploy** 倉庫的職責：如何將 `SafeZone` 產出的 Docker Images，轉化為 Kubernetes 上穩定運行的服務。

---

## 📚 核心文檔導航

| 模組 | 說明 | 關鍵字 |
| :--- | :--- | :--- |
| [**Helm Chart Architecture**](safechord.safezone.deployment.charts.md) | **靜態結構**。定義了 `safezone-infra`, `safezone-core`, `safezone-ui` 三層 Umbrella Chart 的依賴關係與全域配置策略。 | `Umbrella Chart`, `Configuration`, `Service Discovery` |
| [**GitOps Workflow**](safechord.safezone.deployment.workflow.md) | **動態流程**。定義了從 `deploy/preview` 到 `staging` 的晉升路徑，以及 ArgoCD 的同步策略。 | `GitFlow`, `Promotion`, `ArgoCD`, `Preview Env` |

---

## 🏗️ 部署策略摘要 (v0.2.1)

在 v0.2.1 版本中，我們的部署策略針對 **非同步架構** 進行了以下優化：

1.  **基礎設施優先 (Infra-First)**:
    *   透過 `safezone-infra` Chart 優先部署 `Time Server` 與 `CLI Relay`，確保核心控制平面 (Control Plane) 就緒。
    *   即使在 Preview 環境，也透過降級配置 (Ephemeral Redis/Kafka) 模擬完整的基礎設施拓撲。

2.  **彈性伸縮 (Auto-Scaling)**:
    *   **Worker**: 整合 **KEDA (Kubernetes Event-driven Autoscaling)**。
    *   **Trigger**: 監聽 Kafka Consumer Lag。當 `data-ingestor` 湧入大量模擬數據時，KEDA 自動擴展 `worker-golang` Pod 數量以加速消化，確保系統在高負載下的穩定性。

3.  **種子數據初始化 (Seeding)**:
    *   引入 `safezone-seed` Job。在部署完成後，自動觸發資料庫 Schema 初始化與基礎地理資訊 (City/Region) 的寫入，讓新環境「開箱即用」。

---

## 🔄 與 App 層的邊界

*   **App Layer (`SafeZone`)**: 負責產出 Immutable 的 Docker Image (Artifacts)。
*   **Deployment Layer (`SafeZone-Deploy`)**: 負責定義這些 Image 在不同環境 (Preview/Staging) 下的運行參數 (Replicas, Env Vars, Resources)。
