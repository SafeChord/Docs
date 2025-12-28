---
title: "SafeZone: Health Safety Map Application Overview"
doc_id: safechord.safezone
version: "0.2.1"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
last_updated: "2025-12-28"
summary: "SafeZone v0.2.1 應用層總覽。核心目標是提供即時與歷史的健康安全地圖資訊（以 COVID-19 疫情數據為例）。本文件詳述其如何利用事件驅動架構 (Event-Driven Architecture)、Kafka 數據流與 KEDA 彈性伸縮，實現從大規模數據模擬到視覺化呈現的完整生態系。"
keywords:
  - SafeZone
  - health safety map
  - event-driven
  - kafka
  - golang
  - microservices
  - KEDA
  - SafeChord
logical_path: "SafeChord.SafeZone"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.safezone.service.md"
  - "safechord.safezone.deployment.md"
  - "safechord.safezone.changelog.md"
parent_doc: "safechord"
tech_stack:
  - "Frontend: Plotly Dash (Time-Aware)"
  - "Backend: Python (FastAPI/AsyncIO), Golang (Franz-Go)"
  - "Messaging: Kafka (franz-go batching)"
  - "Scaling: KEDA (Kafka Lag Trigger)"
  - "Storage: PostgreSQL, Redis (Versioned Cache)"
  - "Architecture: Event-Driven Microservices"
---
# SafeZone (v0.2.1)

> SafeZone 是 SafeChord 的資料應用主體。
> 
> 在 v0.2.1 中，我們不僅模擬資料的「產生」，更模擬了資料在現代化分散式系統中的「流動」——從非同步注入、事件緩衝、高效消費、KEDA 彈性伸縮到即時查詢。

---

## 🛠 技術選型摘要 (Tech Stack)

*   **Languages**: `Python` (AsyncIO Data/API), `Golang` (Franz-Go Worker)
*   **Frameworks**: `FastAPI`, `Pydantic`, `Plotly Dash`
*   **Data Infra**: `Kafka` (franz-go implementation), `PostgreSQL` (Persistence), `Redis` (Versioned Cache)
*   **Ops & Scaling**: `Docker`, `KEDA`, `GitHub Actions`, `Make`

---

## 📁 SafeZone 文件結構導航

以下表格對應了 [SafeChord.KnowledgeTree](safechord.knowledgetree.md) 的應用層分支：

| 類別 | 模組/文件 | 說明 |
| :--- | :--- | :--- |
| **MACRO** | [**SAFEZONE**](safechord.safezone.md) | **(本文件)** 整體架構說明，定義 v0.2.1 的非同步資料流與彈性架構願景。 |
| **MID** | [SERVICES](safechord.safezone.service.md) | **服務總覽**。詳述 `Source` -> `Kafka` -> `Sink` -> `View` 的完整資料流技術棧。 |
| *Micro* | [PANDEMIC-SIMULATOR](safechord.safezone.service.pandemicsimulator.md) | **資料產地**。模擬 CLI 行為產生測試資料 (Python/**AsyncIO**)。 |
| *Micro* | [DATA-INGESTOR](safechord.safezone.service.dataingestor.md) | **資料入口**。寫入閘道 (Gateway)，將事件推送至 Kafka。 |
| *Micro* | [WORKER-GOLANG](safechord.safezone.service.worker.md) | **資料處理**。高效能 Golang Consumer (**Franz-Go**)，負責 Batch Upsert。 |
| *Micro* | [ANALYTICS-API](safechord.safezone.service.analyticsapi.md) | **資料出口**。提供查詢服務，整合 **Cache Versioning** 失效機制。 |
| *Micro* | [DASHBOARD](safechord.safezone.service.dashboard.md) | **視覺呈現**。Plotly Dash 前端，具備模擬時間感知能力。 |
| *Micro* | [TIME-SERVER](safechord.safezone.toolkit.timeserver.md) | **時間控制**。提供全系統統一的虛擬時間軸與加速功能。 |
| *Micro* | [SZCLI](safechord.safezone.toolkit.cli.md) | **指揮官**。運維 CLI (**Client-Relay**)，負責觸發模擬與驗證。 |
| **MID** | [**DEPLOYMENT**](safechord.safezone.deployment.md) | **部署總覽**。整合 Helm Umbrella Chart 架構與 GitOps 流程說明。 |
| *Detail* | [HELM CHARTS](safechord.safezone.deployment.charts.md) | 詳解三層式 Chart 設計與 **KEDA** 伸縮配置。 |
| *Detail* | [GITOPS WORKFLOW](safechord.safezone.deployment.workflow.md) | 描述從 Preview 到 Staging 的環境晉升與 ArgoCD 同步策略。 |
| **META** | [CHANGELOG](safechord.safezone.changelog.md) | 追蹤 SafeZone 的版本演進與 API 變更紀錄。 |

---

## 🔭 未來發展方向 (Roadmap)

*   **真實資料源串接**: 讓 Ingestor 支援切換 Source，從模擬器切換至真實 Open Data API。
*   **GIS 視覺化升級**: 將 Dashboard 升級為基於 Leaflet/Mapbox 的高互動性地理資訊系統。
*   **多租戶模擬**: 支援多個使用者同時進行不同時間軸的並行模擬。

SafeZone 的願景不只是「跑得起來」，而是成為一套可以被延伸、被接軌、甚至能支援社會議題演練的資料系統範本。

---

## 🧭 推薦閱讀順序

1.  **[Services](safechord.safezone.service.md)**：先看懂資料怎麼流 (Data Flow)。
2.  **[Deployment](safechord.safezone.deployment.md)**：再看程式怎麼跑 (Helm/K8s/KEDA)。
3.  **[ChangeLog](safechord.safezone.changelog.md)**：最後確認版本差異。
