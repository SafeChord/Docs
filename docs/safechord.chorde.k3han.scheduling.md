---
title: K3han Scheduling Strategy
doc_id: safechord.chorde.k3han.scheduling
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
context_scope: Chorde/cluster/k3han
summary: 定義混合雲環境下的 Pod 調度邏輯，包含親和性 (Affinity)、污點 (Taints) 與資源隔離策略。
keywords:
  - Scheduling
  - Affinity
  - Taints
  - Data Locality
  - Isolation
logical_path: SafeChord.Chorde.K3han.Scheduling
related_docs:
  - safechord.chorde.k3han.cluster.md
  - safechord.safezone.deployment.charts.md
parent_doc: safechord.chorde.k3han
archetype: brain
code_paths: []
doc_version: 0.2.0
---

# K3han Scheduling Strategy (Brain)

> **Brain (大腦型)**：定義 SafeChord 生產環境的資源調度邏輯與決策原則。
> *重點：為何這樣調度？如何解決高延遲與資源爭奪？*

## 1. 背景與挑戰 (Context)
K3han 是一個 **分散式混合雲 (Distributed Hybrid Cloud)**。與標準雲端叢集不同，我們面臨以下挑戰：
*   **極端延遲差異**: 同區節點 (<1ms) vs 跨國節點 (~80ms)。
*   **異質算力**: 弱小的雲端入口 (1 vCPU) vs 強大的本地節點 (6 Core)。
*   **功能單一性**: 某些節點 (如 GCE) 僅為了單一目的 (Ingress) 存在，不應執行其他負載。

**問題陳述**: 如何在不拖慢系統回應速度的前提下，精確地將 Pod 放置在最合適的物理節點上？

## 2. 核心原則 (Core Principles)
1.  **就近運算 (Data Locality)**: 計算 (Compute) 必須發生在資料 (Data) 所在的節點上。避免跨國讀取資料庫。
2.  **角色隔離 (Role Isolation)**: 專用節點 (Ingress/Control Plane) 必須透過 Taints 強制淨空，防止業務 Pod 搶佔資源。
3.  **任務價值優先 (Mission Criticality)**: CSP 資源的投入是為了換取其不可替代的特性（Contabo 的 24/7 穩定性、GCE 的固定公網 IP），而非單純為了算力。高負載運算應優先卸載至已付費的本地硬體 (`Sunk Cost`)，確保每一分雲端預算都花在刀口上（穩定與連通）。

## 3. 調度決策 (Decisions)

### 3.1 隔離策略 (Isolation Strategy)
我們使用 **Taints (污點)** 來建立嚴格的防禦邊界，確保關鍵節點不被非預期的負載干擾。

*   **Control Plane 隔離 (`node-role.kubernetes.io/control-plane:NoSchedule`)**:
    *   **理由**: `ct-serv-jp` 承載全叢集的管理邏輯 (GitOps, API Server)。隔離它是為了防止業務 Pod 爆量導致控制面崩潰。
    *   **結果**: 僅允許具備對應 Toleration 的系統級組件 (如 ArgoCD, Prometheus) 部署於此。
*   **Gateway 隔離 (`chorde.io/purpose=proxy-only:NoSchedule`)**:
    *   **理由**: `gce-agent-tw` 資源極其有限 (1GB RAM)，作為唯一公網入口，必須保證其資源 100% 用於 Ingress Proxy。

### 3.2 佈署策略 (Placement Strategy)
我們使用 **Node Affinity (節點親和性)** 將 Workload 導向最適實體。

*   **資料密集型 (Data-Intensive) -> 本地供應商 (`provider=local`)**:
    *   **目標**: PostgreSQL, Redis, Analytics API。
    *   **邏輯**: 這些服務對硬體 IOPS 與網路延遲極度敏感，必須部署在具備 NVMe/SSD 且延遲 <1ms 的地端環境（如 `acer-agent`）。
*   **展示型 (Presentation) -> 本地供應商 (`provider=local`)**:
    *   **目標**: Dashboard, CLI Relay。
    *   **邏輯**: 雖然 CPU 負載不高，但為了減少跨國頻寬消耗 (JP-TW) 並提升響應速度，應就近部署於資料源節點。

## 4. 實作參考 (Implementation Reference)
以下表格定義了目前叢集 (v0.2.x) 實際運行的配置。

### 模組部署原則 (Component Placement Map)
| 模組 | 部署目標 | 策略依據 | 部署分類 |
| :--- | :--- | :--- | :--- |
| **PostgreSQL Primary** | `ct-serv-jp` | Control Plane 高可用性，供全系統寫入 | Cloud |
| **PostgreSQL Replica** | `acer-agent` | Data Locality，降低讀取延遲 (80ms -> <1ms) | Local |
| **SafeZone API** | `acer-agent` | 需與 Replica 和 Redis 同區，降低 I/O 延遲 | Local |
| **Redis Cache** | `acer-agent` | 高頻存取，需極致速度 | Local |
| **Dashboard** | `acer-agent` | 展示層，為了就近存取資料源 | Local |
| **CLI Relay** | `acer-agent` | 資料注入入口，需靠近 DB | Local |
| **Prometheus / ArgoCD** | `ct-serv-jp` | 管理層工具，必須與 Worker 隔離 | Cloud |

### Node Labels
| Node Name | Region (`chorde.io/region`) | Provider (`chorde.io/provider`) | Tier (`chorde.io/tier`) | Avail (`chorde.io/avail`) |
| :--- | :--- | :--- | :--- | :--- |
| **ct-serv-jp** | `jp` | `contabo` | `medium` | `always` |
| **gce-agent-tw** | `tw` | `gce` | `low` | `always` |
| **acer-agent** | `tw` | `local` | `medium` | `always` |

### Taints
| Node Name | Taint Key | Effect | 用途 |
| :--- | :--- | :--- | :--- |
| **ct-serv-jp** | `node-role.kubernetes.io/control-plane` | `NoSchedule` | 保護系統中樞 |
| **gce-agent-tw** | `chorde.io/purpose=proxy-only` | `NoSchedule` | 保護流量入口 |

### 建議的 Affinity 寫法
```yaml
# 範例：要求部署在地端節點 (High IOPS)
nodeAffinity:
  requiredDuringSchedulingIgnoredDuringExecution:
    nodeSelectorTerms:
    - matchExpressions:
      - key: chorde.io/provider
        operator: In
        values:
          - local
      - key: chorde.io/avail
        operator: In
        values:
          - always
```

## 5. 權衡與後果 (Trade-offs)

| 優點 (Pros) | 缺點 (Cons) | 緩解措施 (Mitigation) |
| :--- | :--- | :--- |
| **極致效能**：確保 DB 享用 NVMe/SSD | **低彈性**：單點故障 (SPOF) 風險高 | 在 Spot 節點建立 Cold Standby |
| **成本可控**：雲端資源不會被濫用 | **維運複雜**：需手動管理 Label | 使用 Ansible 統一標記 |
| **穩定性**：關鍵組件 (Ingress/Argo) 不受干擾 | **資源閒置**：專用節點利用率可能偏低 | 接受這是 MVA 的必要保險費 |

