---
title: SafeChord Knowledge Tree Structure
doc_id: safechord.knowledgetree
last_updated: '2026-03-11'
status: active
authors:
  - bradyhau
  - Gemini 2.0 Flash
context_scope: Project Root
summary: SafeChord 專案的全域知識地圖及文件概述，作為知識庫系統導航。反映 v0.3.0 四層解耦架構。
keywords:
  - SafeChord
  - Knowledge Graph
  - Architecture Map
  - Navigation
logical_path: SafeChord.KnowledgeTree
related_docs:
  - safechord.md
doc_version: 0.3.0
archetype: map
app_version: null
---

# SafeChord 知識地圖 (Knowledge Map)

## 🗺️ 導航指南 (Navigation Guide)

本專案採用 **Decoupled 4-Layer (四層解耦)** 架構。閱讀時請根據您的角色與目標選擇路徑：

*   **⬜ Knowledge (Docs)**: 專案的 **Single Source of Truth (SSOT)**。定義方法論與全域規範。
*   **🟦 Application (SafeZone)**: 核心業務邏輯。關注 Python/Go 源碼、非同步處理與單元測試。
*   **🟨 Deployment (SafeZone-Deploy)**: 交付與包裝。關注 Helm Charts 與 GitOps 晉升流程。
*   **🟥 Infrastructure (Chorde)**: 平台層。管理混合雲 K3s 叢集、網路邊界與資源調度策略。

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

*   🧩 **SafeChord Ecosystem** - 系統全貌
    *   [📄 safechord.md](safechord.md) ⭐ (專案總覽：MVA 哲學、技術堆疊、入口導航)
    *   [📄 knowledgetree.md](safechord.knowledgetree.md) (本文件：全域導航)
    *   [📄 safechord.roadmap.md](safechord.roadmap.md) (🔄 發展藍圖：SLO 定義與架構 TDD 演進目標)
    *   [📄 safechord.security.md](safechord.security.md) 🛡️ (安全架構與 SealedSecrets 治理準則)

    *   🌐 **Environment Landscape (環境全景)** 
        *   [📄 safechord.environment.md](safechord.environment.md) ⭐ (環境演進論：從 Local Compose 到平台整合的升級之路)

    *   ⬜ **Knowledge Layer (Repo: Docs)**
        *   *Focus: KDD Methodology, Standards, SSOT*
        *   [📄 safechord.kdd.introduction.md](safechord.kdd.introduction.md) (KDD: 知識驅動開發引言)
        [📄 safechord.kdd.practice.md](safechord.kdd.practice.md) ⭐ (三機協作實踐：Architect-Pioneer-Settler 模型與無頭開發協議)
        *   [📄 safechord.kdd.workflow.md](safechord.kdd.workflow.md) (KDD 工作流：Map-Blueprint-Script-Brain)

    *   🟦 **Application Layer (Repo: SafeZone)**
        *   *Focus: Source Code, Business Logic, AsyncIO Dataflow*
        *   **核心架構**
            *   [📄 safechord.safezone.md](safechord.safezone.md) ⭐ (Async Dataflow, Event-Driven Design, KEDA)
            *   [📄 safechord.safezone.changelog.md](safechord.safezone.changelog.md) (🔄 應用版本演進與技術遷移紀錄)
        *   **服務模組 (Microservices)**
            *   [📄 safechord.safezone.service.pandemicsimulator.md](safechord.safezone.service.pandemicsimulator.md) (Simulator: AsyncIO 資料源)
            *   [📄 safechord.safezone.service.dataingestor.md](safechord.safezone.service.dataingestor.md) (Ingestor: Kafka Producer 閘道)
            *   [📄 safechord.safezone.service.dataingestor_evolution.md](safechord.safezone.service.dataingestor_evolution.md) (進化論：從同步到非同步的架構重構)
            *   [📄 safechord.safezone.service.worker.md](safechord.safezone.service.worker.md) (Worker: Golang / Franz-Go 消費者)
            *   [📄 safechord.safezone.service.analyticsapi.md](safechord.safezone.service.analyticsapi.md) (API: 快取版本化聚合器)
            *   [📄 safechord.safezone.service.dashboard.md](safechord.safezone.service.dashboard.md) (UI: 時序感知視覺化)
        *   **工具與開發流 (Toolkit & Workflow)**
            *   [📄 safechord.safezone.toolkit.timeserver.md](safechord.safezone.toolkit.timeserver.md) (Time Server: 時鐘控制塔)
            *   [📄 safechord.safezone.toolkit.cli.md](safechord.safezone.toolkit.cli.md) (SZCLI: 運維工具與中繼代理)
            *   [📄 safechord.safezone.workflow.md](safechord.safezone.workflow.md) ⭐ (CI 工作流：構建與煙囪測試規範)

    *   🟨 **Deployment Layer (Repo: SafeZone-Deploy)**
        *   *Focus: Configuration, Helm, GitOps CD*
        *   [📄 safechord.safezone.deployment.md](safechord.safezone.deployment.md) (交付運維地圖)
            *   [📄 safechord.safezone.deployment.charts.md](safechord.safezone.deployment.charts.md) ⭐ (Helm Umbrella Charts 與 KEDA 配置)
            *   [📄 safechord.safezone.deployment.workflow.md](safechord.safezone.deployment.workflow.md) ⭐ (GitOps Workflow, ArgoCD, 環境晉升)

    *   🟥 **Infrastructure Layer (Repo: Chorde Hub)**
        *   *Focus: Kubernetes, Platform Operators, Scheduling*
        *   [📄 safechord.chorde.md](safechord.chorde.md) (Chorde Framework: 平台總綱與倉庫結構)
        *   [📄 safechord.chorde.k3han.md](safechord.chorde.k3han.md) ⭐ (K3han: 核心混合雲叢集導航)
            *   [📄 safechord.chorde.k3han.cluster.md](safechord.chorde.k3han.cluster.md) ⭐ (物理拓撲、延遲矩陣與 Tailscale Overlay)
            *   [📄 safechord.chorde.k3han.ingress.md](safechord.chorde.k3han.ingress.md) (Ingress 邊界：雙通道隔離策略)
            *   [📄 safechord.chorde.k3han.scheduling.md](safechord.chorde.k3han.scheduling.md) ⭐ (排程大腦：可靠性分層與 Taints 策略)
            *   [📄 safechord.chorde.k3han.monitoring.md](safechord.chorde.k3han.monitoring.md) (可觀測性：Loki S3 與 Prometheus Operator)
            *   [📄 safechord.chorde.k3han.changelog.md](safechord.chorde.k3han.changelog.md) (🔄 平台版本演進紀錄)
