---
title: "Map: K3han Hybrid Cluster" 
doc_id: safechord.chorde.k3han
version: "0.2.1"
status: active
authors:
  - "bradyhau"
  - "Gemini 3 Pro"
last_updated: "2026-01-09"
summary: "K3han 子系統的導航地圖。索引關於混合雲拓撲 (Cluster)、網路邊界 (Ingress) 與資源調度 (Scheduling) 的規格文件。"
keywords:
  - K3han
  - Map
  - Hybrid Cloud
  - Index
  - Navigation
logical_path: "SafeChord.Chorde.K3han"
related_docs:
  - "safechord.chorde.md"
  - "safechord.chorde.k3han.cluster.md"
  - "safechord.chorde.k3han.ingress.md"
  - "safechord.chorde.k3han.scheduling.md"
parent_doc: "safechord.chorde"
archetype: map
code_paths:
  - "Chorde/cluster/k3han"
---

# 🗺️ K3han 子系統地圖 (Map)

> **Map (地圖型)**：K3han 混合雲叢集的知識導航中心。
> *定位：SafeChord 的核心運行載體 (Runtime)，基於 K3s 與 Tailscale 構建。*

### 🏷️ 命名由來 (Etymology)
**K3han** = **K3s** + **Khan** (可汗)。
取其橫跨歐亞、霸氣且具歷史底蘊之意。在初始架構中，K3han 透過 Tailscale 穿透了日本 (Contabo) 與台灣 (GCE/Home) 的網路壁壘，建立了一個跨國界的輕量級運作版圖。

## 1. 導航索引 (Documentation Index)

請依據您的需求選擇對應的規格文件：

| 領域 | 文件名稱 | 內容摘要 | 原型 |
| :--- | :--- | :--- | :--- |
| **物理層** | [**Cluster Blueprint**](safechord.chorde.k3han.cluster.md) | **硬體與拓撲**。定義 Contabo/GCE/Home 節點規格、地理分佈與 Tailscale 內網架構。 | `Blueprint` |
| **網路層** | [**Ingress Blueprint**](safechord.chorde.k3han.ingress.md) | **流量入口**。定義 Public/Private 雙通道策略、SSL 終止與防火牆規則。 | `Blueprint` |
| **調度層** | [**Scheduling Strategy**](safechord.chorde.k3han.scheduling.md) | **資源決策**。解釋為何要將 DB 放地端 (Data Locality) 以及如何隔離控制層 (Taints)。 | `Brain` |
| **監控層** | [**Monitoring Spec**](safechord.chorde.k3han.monitoring.md) | **可觀測性**。*(待補完)* 定義 Prometheus/Grafana 監控堆疊。 | `Blueprint` |
| **變更歷程** | [**Changelog**](safechord.chorde.k3han.changelog.md) | **版本演進**。紀錄 K3han 從 v0.1.0 到 v0.2.0 的架構變遷。 | `History` |

---

## 2. 系統摘要 (System Summary)

**K3han** (代號) 是一個為了驗證 **MVA (Minimum Viable Architecture)** 而設計的實驗性叢集。它證明了即使在資源極度受限與網路環境惡劣的情況下，仍能透過軟體定義網路 (SDN) 構建出高可用的 Kubernetes 環境。

### 核心特徵
*   **Hybrid Cloud**: 跨越 GCP (台灣)、Contabo (日本) 與 Home Lab (台灣) 三地。
*   **Overlay Network**: 全節點透過 Tailscale Mesh 互連，無視 NAT 與防火牆限制。
*   **Split Architecture**: 控制面 (Control Plane) 與 資料面 (Data Plane) 物理分離，兼顧穩定性與效能。

---

## 3. 實作資源 (Resources)

*   **原始碼路徑**:
    *   叢集配置: `Chorde/cluster/k3han/`
    *   基礎設施: `Chorde/gitops/base/`
*   **相關入口**:
    *   請參閱 [Ingress Blueprint](safechord.chorde.k3han.ingress.md) 了解如何透過授權通道存取管理介面。
