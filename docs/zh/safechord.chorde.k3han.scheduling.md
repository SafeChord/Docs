---
title: K3han Scheduling Strategy
doc_id: safechord.chorde.k3han.scheduling
status: active
authors:
  - bradyhau
  - Gemini 2.0 Flash
context_scope: Chorde/cluster/k3han
summary: 定義混合雲環境下的 Pod 調度邏輯，包含親和性 (Affinity)、污點 (Taints) 與 Operator 驅動的資源隔離策略。
keywords:
  - Scheduling
  - Affinity
  - Taints
  - Data Locality
  - Isolation
  - Operator Pattern
logical_path: SafeChord.Chorde.K3han.Scheduling
related_docs:
  - safechord.chorde.k3han.cluster.md
  - safechord.safezone.deployment.md
parent_doc: safechord.chorde.k3han
archetype: brain
code_paths:
  - Chorde/gitops/k3han/manifests
doc_version: 0.3.0
app_version: 0.3.0
---

# K3han Scheduling Strategy (Brain)

> **Brain (大腦型)**：定義 SafeChord 生產環境的資源調度邏輯與決策原則。
> *重點：為何這樣調度？如何解決高延遲與資源爭奪？*

## 1. 背景與挑戰 (Context)
K3han 是一個 **高度非對稱的分散式混合雲 (Highly Asymmetric Hybrid Cloud)**。在 v0.3.0 中，我們面臨的挑戰不再僅是算力分配，而是來自物理特性與經營成本的複雜交織：

*   **雲端核心 (`ct-serv-jp`)**：
    *   **優勢**：資源量充足且穩定（12GB RAM），適合作為管理中樞。
    *   **限制**：物理頻寬僅 300Mb/s，且與台灣節點存在 ~80ms 的跨境延遲。必須嚴格限制非預期的業務負載進入此區域，以確保控制面 (Control Plane) 的反應靈敏。
*   **邊緣入口 (`gce-agent-tw`)**：
    *   **優勢**：擁有最頂級的網路品質（Google 骨幹網路、全叢集各點最低延遲）。
    *   **限制**：運算能力極其貧弱（1GB RAM），且存在昂貴的網路流量帳單報表風險。必須「物理性地淨空」所有非流量轉發的任務。
*   **地端算力 (`acer-agent` / Local)**：
    *   **優勢**：擁有全叢集最強大的運算效能 (CPU/IOPS) 與 1Gb/s 內部頻寬，且為 Spot/Sunk Cost 資源。
    *   **限制**：受限於家用網路架構與非 24/7 電源，無法給出漂亮的 SLA。必須建立「可靠性邊界」，防止關鍵服務誤入。

**問題陳述**: 標準的 Kubernetes 排程器僅關注資源 (CPU/Memory) 的剩餘量，無法理解「網路頻寬上限」、「帳單爆炸風險」與「家用可靠性差異」。因此，我們必須建立一套明確的「主動拒絕」與「精確引流」機制。

## 2. 核心原則 (Core Principles)
1.  **控制器近端化 (Control Plane Locality)**: 所有 Operators (CNPG, Strimzi, KEDA) 必須部署於 Control Plane 節點，確保與 API Server 的通訊延遲 < 1ms。
2.  **資料局部性 (Data Locality)**: 寫入密集型任務 (PostgreSQL Primary) 部署於高穩定雲端；讀取密集型/高流量任務 (Replica, Kafka Broker, Apps) 部署於台灣本地。
3.  **邊緣隔離 (Edge Isolation)**: 公網入口節點 (`gce-agent-tw`) 嚴禁執行任何業務邏輯，確保 100% 頻寬與 CPU 用於 Ingress 轉發。
4.  **可靠性分層 (Reliability Tiering)**: 透過 `PreferNoSchedule` 污點，軟性拒絕需要 24/7 高可用性的 Pod 進入 `acer-agent` (Local Tier)，確保這些負載留在雲端。只有明確宣告 `Affinity` 的 Pod，代表其開發者已接受「服務可能隨地端停機而中斷」的風險。

## 3. 調度決策 (Decisions)

### 3.1 隔離策略 (Isolation Strategy)
我們使用 **Taints (污點)** 建立三層防禦體系：

| Taint Key | Effect | 目標節點 | 理由 |
| :--- | :--- | :--- | :--- |
| `node-role.kubernetes.io/control-plane` | `NoSchedule` | `ct-serv-jp` | **控制中樞保護**：防止業務負載干擾 ArgoCD、Prometheus 與 Operators。 |
| `chorde.io/purpose=proxy-only` | `NoSchedule` | `gce-agent-tw` | **入口保護**：GCE 資源極小 (1GB)，僅供 Nginx-Ingress 使用。 |
| `chorde.io/provider=local` | `PreferNoSchedule` | `acer-agent` | **可靠性過濾 (Availability Filter)**：`acer-agent` 為非 24/7 的地端硬體。透過軟性拒絕，防止需要高可用性的 Pod 誤入，僅允許能接受地端可靠性風險的負載。 |

### 3.2 佈署策略 (Placement Strategy)
我們使用 **Node Affinity (節點親和性)** 將 Workload 導向最適實體。

#### 管理層 (Management & Operators)
*   **目標**: ArgoCD, CNPG Operator, Strimzi Operator, Sealed Secrets, KEDA。
*   **親和性**: 鎖定 `node-role.kubernetes.io/control-plane: true`。
*   **理由**: 這些組件是叢集的心臟，需物理性地與業務流量隔開。

#### 資料層 (Data Layer - Split Strategy)
*   **PostgreSQL Primary**: 部署於 `ct-serv-jp` (Cloud)，享用 Contabo 的 24/7 穩定電源與儲存備份。
*   **PostgreSQL Replica**: 部署於 `acer-agent` (Local)，實現 < 1ms 的地端查詢延遲。
*   **Kafka (Strimzi)**: 部署於 `acer-agent`，利用本地 NFS 處理高吞吐的事件流。
*   **Redis (Valkey)**: 部署於 `acer-agent`，為地端應用程式提供極速緩存。

#### 流量入口 (Traffic Ingress)
*   **Private Ingress (Nginx)**: 部署於 `ct-serv-jp`，綁定 Tailscale 內網。
*   **Public Ingress (Nginx)**: 部署於 `gce-agent-tw`，綁定公網 IP。

## 4. 實作參考 (Implementation Reference)

### 節點標籤 Schema (v0.3.x)
| Node Name | region (`chorde.io/`) | provider (`chorde.io/`) | tier (`chorde.io/`) | Role / Purpose (Actual Key) |
| :--- | :--- | :--- | :--- | :--- |
| **ct-serv-jp** | `jp` | `contabo` | `medium` | `node-role.kubernetes.io/control-plane: "true"` |
| **gce-agent-tw** | `tw` | `gce` | `low` | `chorde.io/purpose: "proxy-only"` |
| **acer-agent** | `tw` | `local` | `medium` | `chorde.io/provider: "local"` (Worker) |

### 親和性 YAML 範例
```yaml
# 1. 鎖定控制面 (Operators / Management)
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: node-role.kubernetes.io/control-plane
              operator: Exists

# 2. 鎖定台灣地端 (Data Replica / Apps)
affinity:
  nodeAffinity:
    requiredDuringSchedulingIgnoredDuringExecution:
      nodeSelectorTerms:
        - matchExpressions:
            - key: chorde.io/region
              operator: In
              values: ["tw"]
            - key: chorde.io/tier
              operator: In
              values: ["medium"]
```

## 5. 權衡與後果 (Trade-offs)

| 優點 (Pros) | 缺點 (Cons) | 緩解措施 (Mitigation) |
| :--- | :--- | :--- |
| **控制器極致穩定**：Operator 與 API Server 無延遲。 | **地端單點風險**：若 `acer-agent` 離線，Replica 即失效。 | 在 `Docs/` 中定義 `acer-agent` 故障時切換至 `laptop-agent` 的 Script。 |
| **安全隔離**：公網 IP 節點完全不執行應用程式。 | **跨國流量費用**：Master 與 Worker 的通訊會產生微量跨國流量。 | 透過 Tailscale 壓縮通訊，並將高流量組件留在同區域。 |
| **高性價比算力**：將計算與儲存留在本地以大幅節約預算。 | **高停機風險**：`acer-agent` 可能離線。 | 透過 `PreferNoSchedule` 確保只有「非關鍵」或「已做容錯處理」的 Pod 才進入此層。 |
