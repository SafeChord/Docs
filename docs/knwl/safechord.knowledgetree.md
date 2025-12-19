---
title: SafeChord Knowledge Tree Structure
doc_id: safechord.knowledgetree
version: 0.2.0
submodule_versions:
  - chorde@0.2.0
  - safezone@0.1.0
status: active
authors:
  - bradyhau
  - Gemini 2.5 Pro
last_updated: "2025-05-16"
summary: "本文檔定義了 SafeChord 專案知識庫的分層結構和組織方式，作為所有專案文檔的導航地圖和索引。" 
keywords:
  - SafeChord
  - knowledge tree
  - documentation structure
  - project map
  - table of contents
  - metadata
  - information architecture
logical_path: "SafeChord.KnowledgeTree"
related_docs:
  - "safechord.md"
parent_doc: "safechord"
---

# SafeChord 知識地圖 (Knowledge Map)

## 🗺️ 圖例 (Legend)

* `[📄 檔名.md]` - 已存在的實際文件 (點擊可跳轉)
* `[🧩 模組/概念]` - 結構性節點，代表一個模組、概念或一系列相關文件
* `[🚧 規劃中]` - 預計建立的文件或章節
* `⭐` - 核心/入口文件
* `(描述)` - 對節點或文件的簡短說明

---

## 🌳 SafeChord 專案結構

* 🧩 **SafeChord** - 專案整體
    * [📄 safechord.md](safechord.md) ⭐ (專案總覽，一頁式描述系統整合脈絡與子模組版本狀態)
    * [📄 knowledgetree.md](safechord.knowledgetree.md) (本知識地圖文件)
    * [📄 changelog.md](safechord.changelog.md) (🚧 專案級別的變更日誌 - 規劃中)
    * 🧩 **SafeZone** - 應用層：模擬資料流 (產生、儲存、查詢、可視化)
        * [📄 safezone.md](safechord.safezone.md) ⭐ (SafeZone 架構總覽與資料流邏輯)
        * [📄 changelog.md](safechord.safezone.changelog.md) (SafeZone 模組變更日誌)
        * 🧩 **Services** - 核心服務拆解
            * [📄 service.md](safechord.safezone.service.md) (各服務模組職責與資料流動方式)
                * [📄 datasimulator.md](safechord.safezone.service.datasimulator.md) (Covid-19 資料模擬器：功能、API、TDD)
                * [📄 dataingestor.md](safechord.safezone.service.dataingestor.md) (Safezone 資料接入器：功能、API、TDD) 
                * [📄 analyticsapi.md](safechord.safezone.service.analyticsapi.md) (Safezone 資料後端：功能、API、TDD)
                * [📄 dashboard.md](safechord.safezone.service.dashboard.md) (Safezone 看板呈現：功能、API、TDD)
        * 🧩 **Toolkit** - 輔助工具
            * [📄 cli.md](safechord.safezone.toolkit.cli.md) (🚧 SafeZone 命令列工具：系統管理工具、功能、模組說明)
              * [reference.md](safechord.safezone.toolkit.cli.reference.md) (SafeZone 命令列指令集：功能說明、使用及輸出範例)
            * [📄 time-server.md](safechord.safezone.toolkit.timeserver.md) (🚧 SafeZone 時間中樞：集中時間管理、功能、模組說明)
        * 🧩 **Workflow** - 工作流程
            * [📄 docker-compose.md](safechord.safezone.workflow.docker-compose.md) (服務整合模擬)
            * [📄 ci-cd.md](safechord.safezone.workflow.ci-cd.md) (自動化測試、建置與部署流程)
        * 🧩 **Deployment** - 部署總覽與配置
            * [📄 deployment.md](safechord.safezone.deployment.md) (SafeZone 部署階段總覽與 Helm Chart 結構)
            * [📄 safezone-infra.md](safechord.safezone.deployment.safezone-infra.md) (基礎設施層部署 (Cli, Redis etc.))
            * [📄 safezone-core.md](safechord.safezone.deployment.safezone-core.md) (核心應用服務部署)
            * [📄 safezone-init.md](safechord.safezone.deployment.safezone-init.md) (初始化任務與配置)
            * [📄 safezone-ui.md](safechord.safezone.deployment.safezone-ui.md) (前端介面部署)
    * 🧩 **Chorde/K3han** - 基礎設施層：管理與部署 (K3s)
        * [📄 safechord.chorde.md](safechord.chorde.md) (🚧 Chorde 多叢集入口統一導引)
        * [📄 safechord.chorde.k3han.md](safechord.chorde.k3han.md) ⭐ (K3han 架構總覽，描述叢集設計理念與整合策略)
            * [📄 changelog.md](safechord.chorde.k3han.changelog.md) (K3han 模組變更日誌)
            * [📄 cluster.md](safechord.chorde.k3han.cluster.md) (節點拓撲、硬體配置、網路延遲與流量設計)
            * [📄 scheduling.md](safechord.chorde.k3han.scheduling.md) (節點標籤、Taints/Tolerations 與模組部署原則)
            * [📄 ingress.md](safechord.chorde.k3han.ingress.md) (k3han 對內對外連線通道設計及部屬說明)
            * [📄 monitoring.md](safechord.chorde.k3han.monitoring.md) (🚧 K3han 資源監控與數據管線)
            * [📄 iac.md](safechord.chorde.k3han.iac.md) (🚧 K3han 的 IaC 管理與重建能力)
            * [📄 build.md](safechord.chorde.k3han.build.md) (🚧 K3han 元件建置流程與常見問題排除)
    * 🧩 **Others** (歷史文件、私人檔案、草稿)
---

## 📝 如何維護此地圖

* **同步更新**：當新增、刪除、移動或重命名專案文件時，請記得同步更新此知識地圖。
* **路徑化檔名**：本圖基於您的「路徑化檔名」約定 (`專案.模組.子模組.細項.md`) 來組織層級。
* **簡潔描述**：為每個主要節點或文件添加一句話的核心功能描述。
* **標示狀態**：使用圖例中的符號來標示文件狀態 (例如 `🚧` 表示規劃中)。