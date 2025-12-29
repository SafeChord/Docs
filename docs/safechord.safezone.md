---
title: "SafeZone: Health Safety Map Application Overview"
doc_id: safechord.safezone
version: "0.2.0"
app_version: "0.2.1"
status: active
authors:
  - "bradyhau"
  - "Gemini 3 Pro"
last_updated: "2025-12-28"
summary: "SafeZone 是 SafeChord 專案的應用核心，負責實作健康安全地圖的完整業務邏輯。本文件概述其採用的微服務架構、事件驅動設計 (Event-Driven Design) 以及如何處理從模擬生成到視覺化呈現的端對端資料流。"
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
# SafeZone

> **應用層核心 (Application Layer)**
> 
> SafeZone 是 SafeChord 生態系中的業務邏輯載體。它不僅僅是一個地圖網站，而是一套完整的 **分散式資料模擬與處理系統**。
>
> 系統模擬了真實世界中「事件發生 (Source) → 資料傳輸 (Flow) → 分析決策 (Sink)」的生命週期，並透過微服務架構，展示如何在高併發場景下保持資料的即時性與一致性。

---

## 🏗️ 核心設計理念 (Core Concepts)

SafeZone 的設計圍繞著三個關鍵工程目標：

1.  **事件驅動 (Event-Driven)**: 系統不依賴同步請求 (Request-Response)，而是透過 **Kafka** 訊息佇列進行解耦。這確保了當模擬數據瞬間爆發時，後端服務不會因為流量衝擊而崩潰。
2.  **多語言微服務 (Polyglot Microservices)**: 我們根據服務特性選擇語言。**Python** 負責複雜的業務模擬與 API 邏輯，而 **Golang** 則負責高吞吐量的資料消費 (Worker)，體現了「適才適所」的架構思維。
3.  **彈性伸縮 (Auto-Scaling)**: 結合 **KEDA**，系統能根據佇列積壓量 (Lag) 自動調整運算資源，實現真正的雲原生彈性。

---

## 🛠 技術堆疊 (Tech Stack)

*   **Languages**: `Python (FastAPI)`, `Golang`
*   **Messaging**: `Kafka` (Franz-Go client)
*   **Storage**: `PostgreSQL` (Relational Data), `Redis` (Cache & PubSub)
*   **Frontend**: `Plotly Dash` (Interactive Visualization)

---

## 📁 核心文件導航 (Documentation Map)

以下表格引導您深入了解 SafeZone 的各個組成部分：

| 模組/文件 | 核心職責與說明 |
| :--- | :--- |
| 📦 **[SafeZone](safechord.safezone.md)** | **(本文件)** 應用層架構總覽，定義非同步資料流與微服務設計理念。 |
| 　├─ 🧩 **[Services](safechord.safezone.service.md)** | **服務全景圖**。詳述 `Source` -> `Kafka` -> `Sink` -> `View` 的完整資料流技術實作。 |
| 　│　├─ [Pandemic Simulator](safechord.safezone.service.pandemicsimulator.md) | **資料產地**。使用 Python **AsyncIO** 模擬使用者行為，持續產生測試數據。 |
| 　│　├─ [Data Ingestor](safechord.safezone.service.dataingestor.md) | **流量入口**。作為寫入閘道 (Gateway)，負責將 HTTP 請求轉換為 Kafka 訊息。 |
| 　│　├─ [Worker (Golang)](safechord.safezone.service.worker.md) | **資料處理**。採用高效能 **Franz-Go** 實作，負責將 Kafka 訊息批次寫入資料庫。 |
| 　│　├─ [Analytics API](safechord.safezone.service.analyticsapi.md) | **查詢介面**。提供前端聚合數據，並整合 **Cache Versioning** 機制處理快取失效。 |
| 　│　└─ [Dashboard](safechord.safezone.service.dashboard.md) | **視覺呈現**。具備「時間感知 (Time-Aware)」能力的 Plotly Dash 前端。 |
| 　├─ 🧰 **Toolkit** | **輔助工具組**。 |
| 　│　├─ [Time Server](safechord.safezone.toolkit.timeserver.md) | **時間控制塔**。提供統一的虛擬時間軸，支援系統時間的加速與暫停。 |
| 　│　└─ [SZCLI](safechord.safezone.toolkit.cli.md) | **指揮官**。維運專用 CLI，用於觸發模擬任務與驗證系統狀態。 |
| 　├─ 🚀 **[Deployment](safechord.safezone.deployment.md)** | **部署與交付**。Helm Umbrella Chart 設計與 ArgoCD GitOps 流程總覽。 |
| 　│　├─ [Helm Charts](safechord.safezone.deployment.charts.md) | **配置細節**。三層式 Chart 結構解析與 KEDA 伸縮參數配置。 |
| 　│　└─ [GitOps Workflow](safechord.safezone.deployment.workflow.md) | **環境晉換**。描述從 Preview 到 Staging 的自動化部署路徑。 |
| 　└─ 📝 **[ChangeLog](safechord.safezone.changelog.md)** | **版本紀錄**。追蹤 SafeZone 的架構演進與重大 API 變更。 |

---

## 🔭 未來展望 (Roadmap)

SafeZone 的願景是成為一套可擴展的**資料系統範本 (Blueprint)**。未來我們計畫引入真實 Open Data 作為資料源，並將前端升級為更具互動性的 GIS 系統，證明即便是資源受限的團隊，也能構建出生產級的資料處理流水線。

---

## 🧭 建議閱讀路徑

1.  **[Services](safechord.safezone.service.md)**：先看懂資料怎麼流 (Data Flow)。
2.  **[Deployment](safechord.safezone.deployment.md)**：再看程式怎麼跑 (Helm/K8s/KEDA)。
3.  **[ChangeLog](safechord.safezone.changelog.md)**：最後確認當前版本的架構變更 (v0.2.x)。