---
title: "Roadmap & Milestones: The Reliability Journey"
doc_id: safechord.milestone
version: "0.3.0-draft"
status: active
authors:
  - "bradyhau"
  - "Gemini 3 Pro"
last_updated: "2025-12-30"
summary: "定義 SafeChord v0.3.0 的核心目標。本版本採用 'Architecture TDD' (架構測試驅動開發) 思維。我們的目標並非立即達成完美的效能，而是先定義「架構斷言 (Architectural Assertions)」(即 SLO)，並建構對應的觀測工具鏈 (k6, Prometheus) 來執行這些測試，最終產出系統的基準線報告 (Baseline Report)。"
keywords:
  - Roadmap
  - Architecture TDD
  - SLO
  - Reliability
  - k6
  - Baseline
logical_path: "SafeChord.Milestone"
related_docs:
  - "safechord.safezone.md"
  - "safechord.chorde.k3han.monitoring.md"
parent_doc: "safechord"
---

# 🛣️ SafeChord Roadmap: Toward Observable Reliability

> **"Reliability is not an accident; it is a feature."**

SafeChord 的開發策略分為三個階段：
1.  **v0.1.x - v0.2.x (Functional)**: 建構功能完整的 MVP，驗證 AsyncIO 資料流與混合雲架構可行性。[Completed]
2.  **v0.3.0 (Reliability Baseline)**: **Architecture TDD Phase**。不新增業務功能，專注於「寫下架構測試」(SLO) 與「建構測試環境」(Observability)，並確立系統效能基準線。

---

## 🎯 v0.3.0: Architecture TDD (The Setup & Measure Phase)

本版本的核心哲學是 **架構層面的測試驅動開發 (Architecture TDD)**。
如同單元測試需先定義 `Expected Result`，我們在此定義 SLO 作為架構的「斷言 (Assertions)」。本階段的目標是 **「讓測試跑起來」** 並 **「誠實記錄現況 (Baseline)」**，而非立即優化系統以通過測試。

### 📊 1. 架構斷言：業務層 (Business Level)
*測試目標：驗證排程承諾的可觀測性*

| 構面 | 架構斷言 (SLO Hypothesis) | SLI 技術指標 (Indicator) | 測量工具 (Test Runner) |
| :--- | :--- | :--- | :--- |
| **排程準點率** | **Daily Schedule Adherence**<br>每日 `UTC 0:10` 前，Dashboard 需完整呈現當日數據。 | `Sum(Daily_Records) > 0` AND `Timestamp <= UTC 00:10` | **Prometheus** (Blackbox check)<br>**SafeZone CLI** (`verify` command) |
| **例外處理** | 允許 10 分鐘的 E2E Latency (Worker Lag + Polling) 作為一致性緩衝窗。 | N/A | **Documentation** (Known Constraints) |

### ⚡ 2. 架構斷言：應用層 (Application Level)
*測試目標：驗證系統在壓力下的行為邊界*

| 構面 | 架構斷言 (SLO Hypothesis) | SLI 技術指標 (Indicator) | 測量工具 (Test Runner) |
| :--- | :--- | :--- | :--- |
| **寫入韌性** | **Lag Recovery Time < 5 mins**<br>當 Ingestion Rate 飆升至 10 倍 (Burst) 時，系統需在 5 分鐘內消化完畢。 | `kafka_consumer_group_lag > 0` 的持續時間 | **Prometheus** (Kafka Exporter)<br>**KEDA** (HPA Metrics) |
| **讀取可用性** | **Availability under Stress > 99%**<br>在快取失效 (Cache Stampede) 的 1 分鐘內，API 錯誤率需低於 1%。 | `rate(http_requests_total{status=~"5.."}[1m]) / rate(http_requests_total[1m])` | **Prometheus** (Ingress NGINX Metrics)<br>**k6** (Load Testing) |

### 🏗️ 3. 架構斷言：基礎設施層 (Infrastructure Level)
*測試目標：驗證混合雲網路的物理限制*

| 構面 | 架構斷言 (SLO Hypothesis) | SLI 技術指標 (Indicator) | 測量工具 (Test Runner) |
| :--- | :--- | :--- | :--- |
| **網路穩定性** | **Overlay Stability (P95) < 100ms**<br>確保 Contabo (JP) 與 Acer (TW) 之間走 Direct 連線而非 Relay。 | `probe_duration_seconds{target="acer-agent"}` (ICMP/TCP) | **Blackbox Exporter**<br>**Tailscale** (`tailscale ping`) |
| **節點健康度** | **Memory Pressure < 10 mins/month**<br>針對 e2-micro (GCE) 等弱節點的資源飽和度控制。 | `kube_node_status_condition{condition="MemoryPressure", status="true"}` | **Node Exporter**<br>**Kubelet Metrics** |

---

## 🛠️ 實作與驗證計畫 (Implementation Strategy)

本階段不包含 Tuning，而是聚焦於 **Test Implementation (實作測試)**。

### Phase 1: Toolchain Setup (測試工具鏈建置)
1.  **Observability**: 確保 Prometheus 能夠抓取 Kafka Lag, Ingress Metrics 與 Node Metrics。
2.  **Dashboard**: 在 Grafana 建立 **"Reliability Cockpit"**，將上述 SLI 視覺化。
3.  **Load Generator**: 在 `SafeZone-Deploy` 中整合 **k6**，撰寫標準化的壓測腳本 (`tests/k6/*.js`)。

### Phase 2: Establish Baseline (建立基準線)
執行以下劇本，並記錄「真實數據」與「架構斷言」的差距：

#### 1. The Burst Test (寫入壓力基準)
*   **Action**: 使用 `szcli` 或 k6 發送 100x 瞬間流量。
*   **Observe**: 記錄實際的 Lag Recovery Time。是 5 分鐘還是 15 分鐘？
*   **Artifact**: 產出 Lag 收斂曲線圖。

#### 2. The Stampede Test (讀取壓力基準)
*   **Action**: 500 VUs 持續查詢 + 觸發 Cache Invalidation。
*   **Observe**: 記錄 DB CPU 峰值與 API Error Rate。
*   **Artifact**: 產出 API Latency P95/P99 分佈圖。

#### 3. The Edge Failure (混沌測試基準)
*   **Action**: 模擬 `acer-agent` 斷線。
*   **Observe**: 記錄 K3s 偵測到節點失聯並重新調度 Pod 所需的時間。

---

## 📅 版本發布準則 (Release Criteria)

v0.3.0 的 Definition of Done (DoD) 為：

1.  [ ] **Observability Stack Ready**: 所有定義的 SLI 都能在 Grafana 上看到即時數據。
2.  [ ] **Test Scripts Ready**: k6 壓測腳本與 Chaos 劇本已納入版控。
3.  [ ] **Baseline Report**: 完成一份基準線測試報告，列出「理想 SLO」與「實際測量值」的對照表，作為後續 v0.3.x 調優的依據。
