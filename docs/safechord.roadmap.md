---
title: 'Roadmap: The Reliability & Performance Journey'
doc_id: safechord.roadmap
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-04-11'
summary: 定義 SafeChord 從 v0.3.0 到 v0.5.0 的系統演進計畫。本 Roadmap 採「地基先行，數據驅動」策略，從工具解耦 (v0.3.0)、展示層現代化 (v0.3.5, Dashboard + Docs i18n)、架構測試 (v0.4.0) 到最終的效能躍遷 (v0.5.0)。
keywords:
  - Roadmap
  - Architecture TDD
  - SLO
  - Reliability
  - Performance
  - Scalability
  - Observability
logical_path: SafeChord.Roadmap
related_docs:
  - safechord.safezone.md
  - safechord.kdd.practice.md
parent_doc: safechord
archetype: brain
doc_version: 0.3.0
---

# 🛣️ SafeChord Roadmap: From Stabilization to Scaling

> **"Reliability is not an accident; it is a feature. Optimization is not a guess; it is a measurement."**

SafeChord 的演進並非盲目追求功能堆疊，而是遵循嚴謹的工程邏輯。我們將開發路徑劃分為四個關鍵階段，確保每一層優化都建立在穩固且可測量的地基之上。

---

## 🌍 演進四部曲 (The Four-Phase Evolution)

| 版本 | 階段名稱 | 核心目標 | 關鍵戰略 |
| :--- | :--- | :--- | :--- |
| **v0.3.0** | **Tooling & Portability** | **建立實驗室** | 解決環境耦合，實作「容器原生」的觀測與斷言工具鏈，並診斷潛在漏洞。 |
| **v0.3.5** | **Presentation Modernization** | **提升展示層體驗** | 以 AI 協作模式雙軌並進：Dashboard 遷移至 React SPA，Docs 全面英文化並導入 i18n。 |
| **v0.4.0** | **Architecture TDD** | **建立基準線** | 定義 SLO 並執行「架構斷言」，產出系統性能體檢報告。 |
| **v0.5.0** | **Performance Scaling** | **外科手術優化** | 根據基準線數據，針對性地突破併發與吞吐量瓶頸。 |

---

## 🟡 Phase 1: v0.3.0 - Tooling & Portability (工程地基)
**定位**: 消除「環境依賴」，並在邁向高階架構前優先診斷系統穩定性。

*   **關鍵任務**:
    *   **Memory Leak Investigation (#17)**：利用更精細的 pprof/Metrics 手段診斷 Go Worker 在長期負載下的內存行為，若確認存在洩漏則一併修復。
    *   **Protocol-Level Observability (#29, #30)**：透過 `X-Cache-Status` Header 暴露快取行為，實現「無侵入式」的即時觀測。
    *   **Container-Native Assertions (#31, #32)**：實作模組化 Python 斷言套件，汰換對宿主機指令的依賴，實現 Local/K8s/CI 的無差別測試。
    *   **Architecture Hardening (#19)**：在 API 層導入 **Dependency Injection (DI)**，提升代碼體質與可測試性。
*   **戰略價值**: 建立一個「可攜式實驗室」，確保後續壓測數據具備再現性 (Reproducibility)。

---

## 🟢 Phase 1.5: v0.3.5 - Presentation Modernization (展示層現代化)
**定位**: 面試展示的兩大入口——Dashboard 與 Docs 網站——同步升級。Dashboard 遷移至 React SPA，Docs 全面英文化並導入多語系架構。兩者皆以 AI 協作模式完成，展現 Tech Lead 委派能力。

### 🖥️ Track A: Dashboard — React SPA Migration

*   **背景與動機**:
    *   現有 Dash 架構下，每次地圖點擊、篩選切換皆觸發 server-side callback，導致互動延遲達秒級。
    *   Dashboard 作為面試展示的兩大入口之一，體驗品質直接影響第一印象。
    *   API 層 (`Analytics API`) 的 contract 已穩定且具備 Redis cache，前端可作為純 consumer 獨立替換。

*   **關鍵任務**:
    *   **React SPA Scaffold**: 以 Vite + TypeScript + React 建立新前端，Mapbox GL JS 處理 GIS 圖層，Recharts 處理趨勢圖。
    *   **API Contract Reuse**: 新前端消費現有 Analytics API (`/cases/national`, `/cases/city`, `/cases/region`) 與 Time Server (`/time/now`)，**後端零改動**。
    *   **GeoJSON Static Bundling**: 縣市/鄉鎮邊界 GeoJSON 打包為 static assets，由瀏覽器 cache，地圖圖層切換為純前端操作。
    *   **Route-Based A/B Deployment**: 透過 Ingress 路由分離，`/dashboard/` 指向新版 React SPA，`/dashboard/classic/` 保留 Dash 版，面試官可即時對比體驗差異。

### 📚 Track B: Docs — English-First Internationalization

*   **背景與動機**:
    *   現有中文技術文件存在術語中英夾雜、語意精度不足的問題，工程概念用中文描述經常搔不到癢處。
    *   面試官（國內外 Engineering Manager）面對中文文件站，第一印象會打折。
    *   英文是技術社群的通用語言，English-first 直接展示工作語言溝通能力。

*   **關鍵任務**:
    *   **English Rewrite (SSOT)**: 所有面向外部的文件以英文重寫（非逐字翻譯），英文版為 Single Source of Truth，路由掛載於 `/` (root)。
    *   **i18n Architecture**: 導入 MkDocs i18n plugin，中文翻譯版路由掛載於 `/zh/`，面試官可切換語系。
    *   **Multi-Model Translation Pipeline**: 英文 SSOT 由 Claude 主導 rewrite；中文翻譯評估 DeepSeek / Qwen 等中文強項模型，透過 OpenRouter 統一 routing，擇優採用。產出 model selection ADR 記錄比較過程。

### 🤖 協作模式（兩軌共用）

*   本階段所有實作以 **AI 協作** 完成（提供 spec + 舊版參考，AI 產出 code/content，人工 review & integration）。
*   展現 Tech Lead 工作模式：定義 contract → 委派實作 → review 產出 → 整合部署。
*   Track B 額外展示 **multi-model orchestration** 能力：根據任務特性選擇最適模型，而非單一模型通吃。

### 🎯 戰略價值

*   **Dashboard**: 將地圖互動從秒級降至毫秒級。同時為 v0.4.0 提供 A/B 基準線——同一 API 後端、兩套前端，量化 presentation layer 的體驗差異。
*   **Docs**: 消除語言障礙，讓技術決策的深度直接傳達給面試官。Multi-model pipeline 本身即為架構能力的展示素材。

---

## 🟠 Phase 2: v0.4.0 - Architecture TDD & Baseline (基準測量)
**定位**: 這是 **Architecture TDD** 的核心階段。我們在此定義「架構斷言 (SLO)」，並誠實記錄系統現況。

### 📊 架構斷言 (Architectural Assertions)
利用 v0.3.0 建立的工具鏈，我們定義以下 SLO 作為系統的「體檢指標」：

| 層級 | 構面 | 架構斷言 (SLO Hypothesis) | 測量工具 |
| :--- | :--- | :--- | :--- |
| **業務** | **排程準點率** | 每日 `UTC 0:10` 前數據完整呈現。 | **Prometheus** / **szcli** |
| **應用** | **寫入韌性** | 10x 流量突發下，Lag 需在 5 分鐘內消化。 | **KEDA** / **Kafka Exporter** |
| **應用** | **讀取可用性** | 快取失效期間，API 錯誤率需 < 1%。 | **k6 (Stampede Test)** |
| **基礎設施** | **網路穩定性** | 跨節點 (JP-TW) Overlay 延遲 P95 < 100ms。 | **Blackbox Exporter** |

*   **戰略價值**: 產出 **"Baseline Report"**。這份報告將指引 v0.5.0 的優化方向，避免盲目優化。

---

## 🔴 Phase 3: v0.5.0 - Performance & Scaling (效能躍遷)
**定位**: 根據基準線數據進行「精確的手術優化」，突破系統瓶頸。

*   **關鍵任務**:
    *   **Go Worker Refactor (#23)**: 對齊 Go 慣用併發模式，優化 Goroutine 與 Channel 管理。
    *   **Idempotency & Batching (#6)**: 實現冪等寫入與批次確認，降低資料庫 I/O 頻率。
    *   **Ingestor Evolution (#22)**: 評估並執行 Data Ingestor 遷移至 Go，解決高吞吐量入口瓶頸。
*   **戰略價值**: 縮小「理想 SLO」與「實際測量值」的差距，實現真正的生產級性能。

---

## 📅 未來展望 (The Future)
當 SafeZone 達成了上述三個階段，它將從一個「功能原型」進化為一個 **「可觀測、可預測、可擴展」** 的現代化微服務架構。這不僅是技術的堆疊，更是對 **SRE (Site Reliability Engineering)** 精神的實踐。
