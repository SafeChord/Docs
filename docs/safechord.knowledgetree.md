---
title: SafeChord Knowledge Tree Structure
doc_id: safechord.knowledgetree
version: 0.2.0
last_updated: "2025-12-28"
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
context_scope: "Project Root"
summary: "SafeChord 專案的全域知識地圖及文件概述，作為知識庫系統導航"
keywords:
  - SafeChord
  - Knowledge Graph
  - Architecture Map
logical_path: "SafeChord.KnowledgeTree"
related_docs:
  - "safechord.md"
---

# SafeChord 知識地圖 (Knowledge Map)

## 🗺️ 導航指南 (Navigation Guide)

本專案採用 **Twin-Repo (雙倉)** 策略。閱讀時請根據您的目標選擇路徑：
*   **開發者 (Developer)**: 關注 🟦 **Application Layer**。包含源碼、非同步邏輯與單元測試。
*   **維運/發佈 (Ops/Release)**: 關注 🟨 **Delivery Layer**。包含環境定義、Helm Charts 與 GitOps 流程。
*   **架構師 (Architect)**: 關注 🟥 **Infrastructure Layer** (Chorde Hub) 與 ⬜ **Methodology**。

### 🏷️ 圖標與狀態說明 (Legend)

| 圖標 | 意義 | 說明 |
| :--- | :--- | :--- |
| ⭐ | **Core Concept** | **核心必讀**。理解系統架構的關鍵入口，建議優先閱讀。 |
| 📄 | **Document** | 一般技術文件或詳細設計說明。 |
| 🛡️ | **Security** | 涉及資安架構、憑證管理或權限控制的內容。 |
| 🔄 | **Changelog** | 版本演進紀錄、遷移指南或歷史脈絡。 |
| 🚧 | **WIP** | 建構中 (Work In Progress) 或草稿階段的文件。 |

---

## 🌳 專案結構樹 (Project Structure Tree)

*   🧩 **SafeChord** - 系統全貌
    *   [📄 safechord.md](safechord.md) ⭐ (專案總覽：MVA 哲學、技術堆疊、導航入口)
    *   [📄 knowledgetree.md](safechord.knowledgetree.md) (本文件：全域導航)
    *   [📄 safechord.security.md](safechord.security.md) 🛡️ (安全架構與 SealedSecrets 治理準則)

    *   🌐 **Environment Landscape (環境全景)** 
        *   *Focus: Service Discovery, Resource Strategy, Environment Evolution*
        *   [📄 safechord.environment.md](safechord.environment.md) ⭐ (環境演進論：從 Local Compose 到平台整合的升級之路)

    *   🟦 **Application Layer (Repo: SafeZone)**
        *   *Focus: Source Code, Business Logic, AsyncIO Dataflow*
        *   **核心架構**
            *   [📄 safechord.safezone.md](safechord.safezone.md) ⭐ (Async Dataflow, Event-Driven Design, KEDA)
            *   [📄 safechord.safezone.changelog.md](safechord.safezone.changelog.md) (🔄 版本演進與技術遷移紀錄)
        *   **服務模組 (Microservices)**
            *   [📄 safechord.safezone.service.md](safechord.safezone.service.md) ⭐ (服務邊界與資料流總覽)
            *   [📄 safechord.safezone.service.pandemicsimulator.md](safechord.safezone.service.pandemicsimulator.md) (Simulator: AsyncIO Data Source)
            *   [📄 safechord.safezone.service.dataingestor.md](safechord.safezone.service.dataingestor.md) (Ingestor: Kafka Producer Gateway)
            *   [📄 safechord.safezone.service.worker.md](safechord.safezone.service.worker.md) (Worker: Golang / Franz-Go Consumer)
            *   [📄 safechord.safezone.service.analyticsapi.md](safechord.safezone.service.analyticsapi.md) (API: Cache Versioning Aggregator)
            *   [📄 safechord.safezone.service.dashboard.md](safechord.safezone.service.dashboard.md) (UI: Time-Aware Visualization)
        *   **工具與共享組件 (Toolkit & Shared)**
            *   [📄 safechord.safezone.toolkit.timeserver.md](safechord.safezone.toolkit.timeserver.md) (Time Server: Time Control Tower)
            *   [📄 safechord.safezone.toolkit.cli.md](safechord.safezone.toolkit.cli.md) (SZCLI: Client-Relay Ops Tool)
            *   [📄 safechord.safezone.toolkit.cli.reference.md](safechord.safezone.toolkit.cli.reference.md) (SZCLI: Command Reference)
        *   **開發流程 (Dev Workflow)**
            *   [📄 safechord.safezone.workflow.md](safechord.safezone.workflow.md) ⭐ (CI Pipeline: Build & Smoke Test)

    *   🟨 **Delivery Layer (Repo: SafeZone-Deploy)**
        *   *Focus: Configuration, Environments, GitOps*
        *   [📄 safechord.safezone.deployment.md](safechord.safezone.deployment.md) (交付運維入口)
            *   [📄 safechord.safezone.deployment.charts.md](safechord.safezone.deployment.charts.md) ⭐ (Helm Umbrella Charts 架構與 KEDA 配置)
            *   [📄 safechord.safezone.deployment.workflow.md](safechord.safezone.deployment.workflow.md) ⭐ (GitOps Workflow, ArgoCD, Promotion)

    *   🟥 **Infrastructure Layer (Repo: Chorde Hub)**
        *   *Focus: Kubernetes, Platform Services, Cluster Management*
        *   [📄 safechord.chorde.md](safechord.chorde.md) (Chorde Framework: 叢集平台總倉)
        *   [📄 safechord.chorde.k3han.md](safechord.chorde.k3han.md) ⭐ (K3han: 核心混合雲實作叢集)
            *   [📄 safechord.chorde.k3han.cluster.md](safechord.chorde.k3han.cluster.md) ⭐ (Node Topology & Traffic Flow)
            *   [📄 safechord.chorde.k3han.ingress.md](safechord.chorde.k3han.ingress.md) (Ingress Boundary & Isolation)
            *   [📄 safechord.chorde.k3han.scheduling.md](safechord.chorde.k3han.scheduling.md) (Scheduling Strategy & Labels)
            *   [📄 safechord.chorde.k3han.monitoring.md](safechord.chorde.k3han.monitoring.md) [🚧] (Observability Stack)

    *   ⬜ **Methodology & Collaboration (Meta)**
        *   *Focus: How we build, AI Integration*
        *   [📄 safechord.kdd.introduction.md](safechord.kdd.introduction.md) (KDD: Phase 1 Human-Orchestrated)
        *   [📄 safechord.kdd.practice.md](safechord.kdd.practice.md) ⭐ (AI 協作模型：Architect-Builder-Coder)
        *   [📄 safechord.kdd.workflow.md](safechord.kdd.workflow.md) (KDD 三階段流程)