---
title: SafeChord Knowledge Tree Structure
doc_id: safechord.knowledgetree
version: 0.2.1
last_updated: "2025-09-12"
status: active
authors:
  - bradyhau
  - Gemini 2.5 Pro
context_scope: "Project Root"
semantic_versioning:
  safezone: "0.2.1"
  chorde: "0.2.0"
summary: "SafeChord 專案的全域知識地圖與導航索引。定義了 v0.2.1 架構下的模組層次、依賴關係及文檔路徑。作為 AI Agent 載入專案上下文的進入點 (Entry Point)。"
keywords:
  - SafeChord
  - Knowledge Graph
  - Architecture Map
  - v0.2.1
  - Navigation
logical_path: "SafeChord.KnowledgeTree"
related_docs:
  - "safechord.md"
  - "safechord.safezone.changelog.md"
parent_doc: "safechord"
---

# SafeChord 知識地圖 (Knowledge Map) v0.2.1

## 🗺️ AI 閱讀指南 (AI Reading Guide)

*   **Entry Point**: 請優先閱讀標示為 `⭐` 的核心文件以建立 Context。
*   **Version Check**: 遇到 `[📄 changelog.md]` 時，請檢查是否有比你記憶中更新的架構變更 (如 v0.2.1 的 Kafka KRaft 遷移)。
*   **Legend**:
    *   `[📄 檔名.md]` - 實體文件 (Physical Document)
    *   `[🧩 模組]` - 邏輯群組 (Logical Group)
    *   `[🚧 規劃中]` - 尚未建立 (Placeholder)
    *   `[🔄 核心流]` - 關鍵數據路徑 (Critical Data Path)

---

## 🌳 專案結構樹 (Project Structure Tree)

*   🧩 **SafeChord** - 專案根節點
    *   [📄 safechord.md](safechord.md) ⭐ (專案總覽：微服務架構、設計哲學、技術堆疊)
    *   [📄 knowledgetree.md](safechord.knowledgetree.md) (本文件：全域導航)
    *   🧩 **SafeZone** - 應用層 (Application Layer) [v0.2.1]
        *   **核心變更追蹤**
            *   [📄 safechord.safezone.changelog.md](safechord.safezone.changelog.md) ⭐ (🔄 版本差異：v0.2.1 KRaft 遷移、Go Worker 重構、Smoke Test 穩定化)
        *   **架構與設計**
            *   [📄 safechord.safezone.md](safechord.safezone.md) ⭐ (架構視圖：Async Dataflow、Kafka Event-Driven 設計)
            *   [📄 safechord.safezone.service.md](safechord.safezone.service.md) (服務邊界與職責定義)
        *   **服務模組 (Services)**
            *   [📄 safechord.safezone.service.datasimulator.md](safechord.safezone.service.pandemicsimulator.md) (Pandemic Simulator: Python/AsyncIO, 資料生成)
            *   [📄 safechord.safezone.service.dataingestor.md](safechord.safezone.service.dataingestor.md) (Data Ingestor: Python/FastAPI, Kafka Producer)
            *   [📄 safechord.safezone.service.worker.md](safechord.safezone.service.worker.md) [🚧 新增] (Worker: Golang, Kafka Consumer, At-least-once 語意)
            *   [📄 safechord.safezone.service.analyticsapi.md](safechord.safezone.service.analyticsapi.md) (Analytics API: Python/FastAPI, Redis Caching, 讀取層)
            *   [📄 safechord.safezone.service.dashboard.md](safechord.safezone.service.dashboard.md) (Dashboard: Python/Dash, 資料視覺化)
        *   **工具與共享組件 (Toolkit & Shared)**
            *   [📄 safechord.safezone.toolkit.timeserver.md](safechord.safezone.toolkit.timeserver.md) (Time Server: 集中式時間控制)
            *   [📄 safechord.safezone.toolkit.cli.md](safechord.safezone.toolkit.cli.md) [🚧] (SZCLI: 運維與除錯工具)
        *   **品質保證與流程 (QA & Workflow)**
            *   [📄 safechord.safezone.workflow.ci-cd.md](safechord.safezone.workflow.ci-cd.md) (GitHub Actions, Release Flow)
            *   [📄 safechord.safezone.workflow.smoke-test.md](safechord.safezone.workflow.smoke-test.md) (Smoke Test: E2E 驗證, `wait_for_infra` 機制)
        *   **部署配置 (Deployment)**
            *   [📄 safechord.safezone.deployment.md](safechord.safezone.deployment.md) (Helm Charts 結構與環境策略)
    *   🧩 **Chorde** - 基礎設施層 (Infrastructure Layer) [v0.2.0]
        *   [📄 safechord.chorde.k3han.md](safechord.chorde.k3han.md) ⭐ (K3han: K3s Cluster 設計)
            *   [📄 safechord.chorde.k3han.cluster.md](safechord.chorde.k3han.cluster.md) (節點拓撲)
            *   [📄 safechord.chorde.k3han.ingress.md](safechord.chorde.k3han.ingress.md) (網路入口)
            *   [📄 safechord.chorde.k3han.monitoring.md](safechord.chorde.k3han.monitoring.md) [🚧] (Loki/Prometheus/Grafana 觀測堆疊)
            *   [📄 safechord.chorde.k3han.iac.md](safechord.chorde.k3han.iac.md) [🚧] (GitOps & ArgoCD)
    *   🧩 **Archive / Drafts**
        *   [📄 draft/kdd/introduction.md](draft/kdd/introduction.md) (KDD 方法論)
