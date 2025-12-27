---
title: SafeChord Knowledge Tree Structure (Optimized)
doc_id: safechord.knowledgetree
version: 0.3.2
last_updated: "2025-12-27"
status: active
authors:
  - bradyhau
  - Gemini 3 Pro (PM Role)
context_scope: "Project Root"
summary: "SafeChord 專案的全域知識地圖。本版本(v0.3.2) 針對雙倉策略 (Twin-Repo Strategy) 進行結構優化，明確區分應用開發 (App) 與交付運維 (Deploy) 的邊界，並整合 KDD 方法論。"
keywords:
  - SafeChord
  - Knowledge Graph
  - Architecture Map
  - Twin-Repo
  - GitOps
logical_path: "SafeChord.KnowledgeTree"
related_docs:
  - "safechord.md"
---

# SafeChord 知識地圖 (Knowledge Map) v0.3.2

## 🗺️ 導航指南 (Navigation Guide)

本專案採用 **Twin-Repo (雙倉)** 策略。閱讀時請根據您的目標選擇路徑：
*   **開發者 (Developer)**: 關注 🟦 **Application Layer**。包含源碼、邏輯、單元測試與本地開發。
*   **維運/發佈 (Ops/Release)**: 關注 🟨 **Delivery Layer**。包含環境定義、Helm Charts、GitOps 流程。
*   **架構師 (Architect)**: 關注 🟥 **Infrastructure Layer** 與 ⬜ **Methodology**。

---

## 🌳 專案結構樹 (Project Structure Tree)

*   🧩 **SafeChord** - 系統全貌
    *   [📄 safechord.md](safechord.md) ⭐ (專案總覽：微服務架構、設計哲學、技術堆疊)
    *   [📄 knowledgetree.md](safechord.knowledgetree.md) (本文件：全域導航)
    *   [📄 safechord.security.md](safechord.security.md) 🛡️ (安全架構與治理準則)

    *   🔧 **Trouble Shooting (疑難解決與關鍵貢獻)**
        *   *Focus: Problem Solving, Critical Contributions*
        *   [📄 safechord.troubleshooting.md](safechord.troubleshooting.md) [🚧] (常見問題排解與關鍵貢獻紀錄)

    *   🌐 **Environment Landscape (環境全景)** ⭐
        *   *Focus: Service Discovery, Resource Strategy, Environment Evolution*
        *   [📄 safechord.environment.md](safechord.environment.md) (環境演進論：從 Local Compose 到 Chorde GitOps 的升級之路)

    *   🟦 **Application Layer (Repo: SafeZone)**
        *   *Focus: Source Code, Business Logic, Artifact Generation*
        *   **核心架構**
            *   [📄 safechord.safezone.md](safechord.safezone.md) ⭐ (Async Dataflow, Event-Driven Design)
            *   [📄 safechord.safezone.changelog.md](safechord.safezone.changelog.md) (🔄 版本演進與 API 變更)
        *   **服務模組 (Microservices)**
            *   [📄 safechord.safezone.service.md](safechord.safezone.service.md) (服務邊界定義)
            *   [📄 safechord.safezone.service.pandemicsimulator.md](safechord.safezone.service.pandemicsimulator.md) (Simulator: AsyncIO Data Source)
            *   [📄 safechord.safezone.service.dataingestor.md](safechord.safezone.service.dataingestor.md) (Ingestor: Kafka Producer Gateway)
            *   [📄 safechord.safezone.service.worker.md](safechord.safezone.service.worker.md) (Worker: Golang High-Perf Consumer)
            *   [📄 safechord.safezone.service.analyticsapi.md](safechord.safezone.service.analyticsapi.md) (API: Cache-Aside Aggregator)
            *   [📄 safechord.safezone.service.dashboard.md](safechord.safezone.service.dashboard.md) (UI: Time-Aware Visualization)
        *   **工具與共享組件 (Toolkit & Shared)**
            *   [📄 safechord.safezone.toolkit.timeserver.md](safechord.safezone.toolkit.timeserver.md) (Time Server: Time Control Tower)
            *   [📄 safechord.safezone.toolkit.cli.md](safechord.safezone.toolkit.cli.md) (SZCLI: Client-Relay Ops Tool)
            *   [📄 safechord.safezone.toolkit.cli.reference.md](safechord.safezone.toolkit.cli.reference.md) (SZCLI: Command Reference)
        *   **開發流程 (Dev Workflow)**
            *   [📄 safechord.safezone.ci.md](safechord.safezone.ci.md) (CI Pipeline: Build & Smoke Test)

    *   🟨 **Delivery Layer (Repo: SafeZone-Deploy)**
        *   *Focus: Configuration, Environments, GitOps*
        *   **部署配置 (Configuration)**
            *   [📄 safechord.safezone.deployment.charts.md](safechord.safezone.deployment.charts.md) (Helm Umbrella Charts 架構與全域配置)
        *   **交付流程 (Ops Workflow)**
            *   [📄 safechord.safezone.deployment.workflow.md](safechord.safezone.deployment.workflow.md) (GitFlow for Ops, ArgoCD Sync, Promotion)

    *   🟥 **Infrastructure Layer (Repo: Chorde)**
        *   *Focus: Kubernetes, Platform Services*
        *   [📄 safechord.chorde.k3han.md](safechord.chorde.k3han.md) ⭐ (K3han Cluster Overview)
            *   [📄 safechord.chorde.k3han.cluster.md](safechord.chorde.k3han.cluster.md) (Node Topology)
            *   [📄 safechord.chorde.k3han.ingress.md](safechord.chorde.k3han.ingress.md) (Ingress & Networking)
            *   [📄 safechord.chorde.k3han.scheduling.md](safechord.chorde.k3han.scheduling.md) (Secheduling)
            *   [📄 safechord.chorde.k3han.monitoring.md](safechord.chorde.k3han.monitoring.md) [🚧] (Observability Stack)

    *   ⬜ **Methodology & Collaboration (Meta)**
        *   *Focus: How we build, AI Integration*
        *   [📄 safechord.kdd.introduction.md](safechord.kdd.introduction.md) (Knowledge-Driven Development 核心概念)
        *   [📄 safechord.kdd.practice.md](safechord.kdd.practice.md) (實作現狀：基於知識庫 Context 的 AI 協作模式)
        *   [📄 safechord.kdd.workflow.md](safechord.kdd.workflow.md) (AI-Human Collaboration Steps)