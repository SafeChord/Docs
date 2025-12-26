---
title: "SafeZone: Health Safety Map Application Overview"
doc_id: safechord.safezone
version: "0.2.1"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
last_updated: "2025-09-12"
summary: "SafeZone v0.2.1 應用層總覽。核心目標是提供即時與歷史的健康安全地圖資訊（以 COVID-19 疫情數據為例）。本文件詳述其如何利用事件驅動架構 (Event-Driven Architecture) 與 Kafka 數據流，實現從大規模數據模擬到視覺化呈現的完整生態系。"
keywords:
  - SafeZone
  - health safety map
  - event-driven
  - kafka
  - golang
  - microservices
  - SafeChord
logical_path: "SafeChord.SafeZone"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.safezone.service.md"
  - "safechord.safezone.deployment.md"
  - "safechord.safezone.changelog.md"
parent_doc: "safechord"
tech_stack:
  - "Frontend: Plotly Dash"
  - "Backend: Python (FastAPI), Golang"
  - "Messaging: Kafka (Redpanda/Franz-Go)"
  - "Storage: PostgreSQL, Redis"
  - "Architecture: Microservice on Kubernetes (K3s)"
---
# SafeZone (v0.2.1)

> SafeZone 是 SafeChord 的資料應用主體。
> 
> 在 v0.2.1 中，我們不僅模擬資料的「產生」，更模擬了資料在現代化分散式系統中的「流動」——從非同步注入、事件緩衝、高效消費到即時查詢。

---

## 🛠 技術選型摘要 (Tech Stack)

*   **Languages**: `Python` (Data/API), `Golang` (High Perf Worker)
*   **Frameworks**: `FastAPI`, `Pydantic`, `Plotly Dash`
*   **Data Infra**: `Kafka` (Streaming), `PostgreSQL` (Persistence), `Redis` (Caching)
*   **Ops**: `Docker`, `GitHub Actions`, `Make`

---

## 📁 SafeZone 文件結構導航

以下表格對應了 [SafeChord.KnowledgeTree](safechord.knowledgetree.md) 的應用層分支：

| 類別 | 模組/文件 | 說明 |
| :--- | :--- | :--- |
| **MACRO** | [**SAFEZONE**](safechord.safezone.md) | **(本文件)** 整體架構說明，定義 v0.2.1 的非同步資料流願景。 |
| **MID** | [SERVICES](safechord.safezone.service.md) | **服務總覽**。詳述 `Source` -> `Kafka` -> `Sink` -> `View` 的完整資料流。 |
| *Micro* | [PANDEMIC-SIMULATOR](safechord.safezone.service.pandemicsimulator.md) | **資料產地**。模擬 CLI 行為產生測試資料 (Python/AsyncIO)。 |
| *Micro* | [DATA-INGESTOR](safechord.safezone.service.dataingestor.md) | **資料入口**。接收 HTTP 請求並作為 Producer 推送至 Kafka。 |
| *Micro* | [WORKER-GOLANG](safechord.safezone.service.worker.md) | **資料處理**。高效能 Golang Consumer，負責資料庫寫入 (At-least-once)。 |
| *Micro* | [ANALYTICS-API](safechord.safezone.service.analyticsapi.md) | **資料出口**。提供查詢服務，整合 Cache-Aside 策略。 |
| *Micro* | [DASHBOARD](safechord.safezone.service.dashboard.md) | **視覺呈現**。Plotly Dash 前端，呈現疫情熱力圖。 |
| *Micro* | [TIME-SERVER](safechord.safezone.toolkit.timeserver.md) | **時間控制**。提供全系統統一的模擬時間軸。 |
| *Micro* | [SZCLI](safechord.safezone.toolkit.cli.md) | **指揮官**。運維 CLI，負責觸發模擬、注入種子資料與驗證。 |
| **MID** | [DEPLOYMENT](safechord.safezone.deployment.md) | **部署總覽**。概述 Helm Umbrella Chart 架構。 |
| *Micro* | [SAFEZONE-INFRA](safechord.safezone.deployment.safezone-infra.md) | 部署基礎設施依賴 (Postgres, Redis, Kafka)。 |
| *Micro* | [SAFEZONE-CORE](safechord.safezone.deployment.safezone-core.md) | 部署後端核心服務 (API, Ingestor, Worker)。 |
| *Micro* | [SAFEZONE-UI](safechord.safezone.deployment.safezone-ui.md) | 部署前端服務 (Dashboard)。 |
| *Micro* | [SAFEZONE-SEED](safechord.safezone.deployment.safezone-seed.md) | 負責初始化 Job 與種子資料植入。 |

---

## 🔭 未來發展方向 (Roadmap)

*   **真實資料源串接**: 讓 Ingestor 支援切換 Source，從模擬器切換至 OurWorldInData 開放 API。
*   **GIS 視覺化升級**: 將 Dashboard 升級為基於 Leaflet/Mapbox 的互動式世界地圖。
*   **多租戶模擬**: 支援多個使用者同時進行不同時間軸的模擬 (需升級 Time Server)。

SafeZone 的願景不只是「跑得起來」，而是成為一套可以被延伸、被接軌、甚至能支援社會議題演練的資料系統範本。

---

## 🧭 推薦閱讀順序

1.  **[Services](safechord.safezone.service.md)**：先看懂資料怎麼流 (Data Flow)。
2.  **[Deployment](safechord.safezone.deployment.md)**：再看程式怎麼跑 (Helm/K8s)。
3.  **[ChangeLog](safechord.safezone.changelog.md)**：最後確認版本差異。
