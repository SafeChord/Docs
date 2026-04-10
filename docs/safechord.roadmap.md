---
title: 'Roadmap: The Reliability & Performance Journey'
doc_id: safechord.roadmap
status: active
authors:
  - bradyhau
  - Gemini CLI
last_updated: '2026-04-10'
summary: 定義 SafeChord 從 v0.3.0 到 v0.5.0 的系統演進計畫。本 Roadmap 採「地基先行，數據驅動」策略，從工具解耦 (v0.3.0)、架構測試 (v0.4.0) 到最終的效能躍遷 (v0.5.0)。
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

SafeChord 的演進並非盲目追求功能堆疊，而是遵循嚴謹的工程邏輯。我們將開發路徑劃分為三個關鍵階段，確保每一層優化都建立在穩固且可測量的地基之上。

---

## 🌍 演進三部曲 (The Three-Phase Evolution)

| 版本 | 階段名稱 | 核心目標 | 關鍵戰略 |
| :--- | :--- | :--- | :--- |
| **v0.3.0** | **Tooling & Portability** | **建立實驗室** | 解決環境耦合，實作「容器原生」的觀測與斷言工具鏈，並診斷潛在漏洞。 |
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
