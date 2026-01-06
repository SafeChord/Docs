---
title: "ADR: Evolution of Data Ingestor Architecture"
doc_id: safechord.safezone.ingestor_evolution
version: "1.0.0"
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
context_scope: "SafeZone Architecture"
summary: "記錄 Data Ingestor 從 v0.1.0 直接寫入資料庫模式，演進至 v0.2.0 事件驅動架構 (Event-Driven) 的決策過程與權衡。"
keywords:
  - ADR
  - Architecture Evolution
  - Event-Driven
  - Kafka
  - Load Leveling
logical_path: "SafeChord.SafeZone.Brain.IngestorEvolution"
related_docs:
  - "safechord.safezone.service.dataingestor.md"
  - "safechord.safezone.service.worker.md"
parent_doc: "safechord.safezone"
archetype: brain
code_paths: []
---

# ADR: Data Ingestor 架構演進 (Direct DB -> Event Sourcing)

> **生效版本**: SafeZone v0.2.0

## 1. 背景與脈絡 (Context)

在 SafeZone v0.1.0 (MVP) 階段，系統採用了最直觀的同步架構：
*   **流程**: `Simulator` -> HTTP -> `Ingestor` -> SQL Insert -> `PostgreSQL`。
*   **問題**:
    1.  **強耦合 (Tight Coupling)**: Ingestor 的吞吐量直接受限於 DB 的寫入效能 (IOPS)。
    2.  **抗壓性差 (Low Resilience)**: 當模擬流量暴增 (Burst) 時，資料庫連線池耗盡，導致 Ingestor 請求超時並拒絕服務 (503 Service Unavailable)。
    3.  **擴展困難**: 無法在不升級資料庫規格的情況下，單純透過增加 Ingestor 實例來提升寫入能力。

## 2. 核心原則 (Core Principles)

本次重構遵循以下架構原則：
1.  **削峰填谷 (Load Leveling)**: 使用佇列緩衝突發流量，保護後端資料庫。
2.  **職責分離 (SoC)**: Ingestor 專注於「接收」，Worker 專注於「寫入」。
3.  **非同步優先 (Async First)**: 在 I/O 密集處全面採用非同步模型。

## 3. 決策內容 (Decisions)

### 決策點 A: 引入 Kafka 作為緩衝層
*   **決定**: 將 Ingestor 重構為純粹的 **Kafka Producer**，移除所有 DB 連線代碼。新增 `Worker` 服務專職消費。
*   **理由**:
    *   Kafka 能夠以極低的延遲接收海量數據 (High Throughput)，且具備持久化能力。
    *   即使後端 DB 宕機，Ingestor 仍能持續接收請求，實現 **高可用性 (High Availability)**。
*   **替代方案**:
    *   *Redis List*: 雖然速度快，但在資料持久性與 Consumer Group 管理上不如 Kafka 成熟 (雖然 v0.2.1 引入了 Franz-Go，Kafka 成為更佳選擇)。

### 決策點 B: 採用 Natural Key Partitioning
*   **決定**: 使用 `city-region` 作為 Kafka Partition Key。
*   **理由**: 確保同一行政區的數據變更（如確診數修正）嚴格按照時序進入同一個 Partition，讓 Worker 能依序處理，避免並發寫入時的 Race Condition。

## 4. 權衡與後果 (Consequences & Trade-offs)

| 優點 (Pros) | 缺點 (Cons) | 緩解措施 (Mitigation) |
| :--- | :--- | :--- |
| **高吞吐量**: HTTP 回應時間不再受 DB 影響，僅取決於 Kafka ACK 速度。 | **架構複雜度增加**: 需維護 Kafka 叢集與額外的 Worker 服務。 | 透過 Chorde 平台層統一管理 Kafka，並使用 Helm Charts 簡化部署。 |
| **彈性擴展**: Ingestor 與 Worker 可獨立依據 CPU/Lag 進行水平擴展 (KEDA)。 | **資料一致性延遲**: 資料寫入後需等待 Worker 處理才能被查詢到 (Eventual Consistency)。 | 在 UI/CLI 實作 `Verify` 指令，主動檢查資料落盤狀態。 |
| **容錯性**: DB 維護期間系統仍可接收數據。 | **分區傾斜 (Skew)**: 熱點城市可能導致特定 Partition 積壓。 | 目前量級尚可接受，未來可考慮更細粒度的 Partition Key。 |

## 5. 參考資料 (References)
*   [SafeZone ChangeLog v0.2.0](safechord.safezone.changelog.md)
*   [Issue #XX: Async Architecture Refactor](https://github.com/...)
