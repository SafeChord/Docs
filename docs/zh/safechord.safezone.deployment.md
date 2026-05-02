---
title: 'Map: SafeZone 部署與維運'
doc_id: safechord.safezone.deployment
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-04-30'
summary: SafeZone 部署層的導航地圖與架構決策紀錄。定義分層 Helm Chart 的設計理念、部署階段順序的意圖，以及與 App 層的職責邊界。
keywords:
  - Deployment
  - Operations
  - Helm
  - GitOps
  - Umbrella Chart
  - KEDA
logical_path: SafeChord.SafeZone.Deployment
related_docs:
  - safechord.safezone.deployment.workflow.md
  - safechord.environment.md
  - safechord.safezone.md
parent_doc: safechord.safezone
archetype: map
code_paths:
  - SafeZone-Deploy/helm-charts
  - SafeZone-Deploy/deploy
doc_version: 0.3.0
---

# SafeZone 部署與維運

> "Code is liability, Deployment is delivery."

本文件定義 SafeZone 部署層的**架構意圖**。實作細節（Chart 結構、Values、Manifests）請直接參閱 `SafeZone-Deploy` 倉庫。

---

## 文件導航

| 主題 | 文件 | 焦點 |
| :--- | :--- | :--- |
| **GitOps 工作流** | [部署工作流](safechord.safezone.deployment.workflow.md) | 分支晉升模型、GitHub Actions 編排、回溯策略 |
| **環境策略** | [環境演進論](safechord.environment.md) | Local / Preview / Staging 三級環境、服務發現、Chorde PaaS 整合 |

> *實作參考：`SafeZone-Deploy/` 倉庫 — Helm Charts、ArgoCD Manifests、部署腳本。*

---

## 邊界：App 層 vs. 部署層

*   **App 層 (`SafeZone`)**：產出不可變的 Docker Image（交付物）。
*   **部署層 (`SafeZone-Deploy`)**：宣告這些 Image 在不同環境下的運行參數（副本數、環境變數、資源配額、密鑰）。完全由 GitOps 驅動——每次 commit 觸發 ArgoCD 調和。

---

## 架構決策：分層式 Umbrella Chart 策略

SafeZone 採用**分層式 Umbrella Chart** 架構，而非單一的巨型 Helm Chart，主要目的是強制執行部署順序並隔離故障域。

### 為什麼：基於 DAG 的部署順序

服務之間存在嚴格的有向無環圖（DAG）依賴關係。分層設計透過 Sync Waves 強制 ArgoCD 依正確順序部署：

| 階段 | 層級 | 意圖 |
| :--- | :--- | :--- |
| **1. 地基** | 基礎設施（ConfigMap、Secret、Ingress、CLI Relay） | 確保所有連線資訊與平台服務在任何應用啟動前就緒。 |
| **2. 引導** | Seed-Init（Schema 遷移、時間服務設定） | 防止 Core 服務因缺少 DB Schema 或時間狀態而 CrashLoop。 |
| **3. 核心** | 業務服務（寫入管線 + 讀取管線） | 建立完整的數據處理 Pipeline。 |
| **4. 數據預熱** | Seed-Data（透過活躍管線注入歷史數據） | 注入 30+ 天歷史資料，讓 Dashboard 首次載入即有完整圖表。必須在 Core **之後**執行，因為它依賴活躍的資料注入管線。 |
| **5. 體驗** | UI（Dashboard） | 面向使用者的層級——僅在後端數據就緒後啟動。 |

### 為什麼：數據生命週期編排

分離 Seed 任務（init vs. data）能實現精細化控制：

*   **冷啟動防護**：Schema 遷移（`seed-init`）在任何應用 Pod 啟動前完成。
*   **真實流量模擬**：`seed-data` 透過實際的資料注入管線發送請求（Simulator → Ingestor → Kafka → Worker → DB），同時兼作端對端整合測試。

### 為什麼：KEDA 作為速率緩衝橋樑

Worker 服務整合 KEDA，根據 Kafka Consumer Lag 自動伸縮。這扮演了**速率緩衝橋樑**的角色——吸收 Kafka 高吞吐量注入與遠端 Primary DB 寫入容量之間的阻抗不匹配，防止突發場景下的資料庫過載。
