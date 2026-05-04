# 🗺️ K3han 子系統地圖

> **類型**：地圖（叢集知識中樞）
> **背景**：SafeChord 的核心運行環境，建構於 K3s 與 Tailscale 之上。

### 🏷️ 詞源
**K3han** = **K3s** + **Khan**（可汗）。
靈感來自歷史上幅員遼闊且強調協調的帝國。在初始架構中，K3han 利用 Tailscale 穿透日本（Contabo）與台灣（GCE/本地端）之間的網路屏障，建立了一個跨境、輕量級的營運疆域。

---

## 1. 文件索引

選擇一個專門的節點以取得深入規格說明：

| 領域 | 文件 | 摘要 | 原型 |
| :--- | :--- | :--- | :--- |
| **拓樸** | [**叢集策略**](safechord.chorde.k3han.cluster.md) | **硬體與 Mesh**。定義 Contabo / GCE / 本地端節點規格、地理分佈以及 Tailscale Mesh 架構。 | `Brain` |
| **網路** | [**流量進入政策**](safechord.chorde.k3han.ingress.md) | **流量進入**。定義公/私雙通道策略、SSL 終止以及防火牆強化。 | `Brain` |
| **編排** | [**排程邏輯**](safechord.chorde.k3han.scheduling.md) | **資源放置**。說明資料本地性決策（資料庫放置）與控制平面隔離（Taints）。 | `Brain` |
| **可觀測性** | [**監控棧**](safechord.chorde.k3han.monitoring.md) | **遙測**。定義 Prometheus / Loki 棧與多維度日誌收集模式。 | `Brain` |
| **歷史** | [**變更日誌**](safechord.chorde.k3han.changelog.md) | **演進**。記錄 K3han 從 v0.1.0 到 v0.3.x 的架構變遷。 | `Timeline` |

---

## 2. 系統背景

**K3han** 是一個實驗性叢集，旨在驗證 **MVA（最低可行架構）** 理念。它證明了即使在極端的資源限制與不佳的網路環境下，仍可透過軟體定義網路（SDN）建構出高可用性的 Kubernetes 環境。

### 主要特性
*   **混合雲**：橫跨 GCP（台灣）、Contabo（日本）以及本地實驗室（台灣）。
*   **覆蓋 Mesh**：所有節點透過 Tailscale Mesh 互連，繞過 NAT 與防火牆限制。
*   **遞迴 GitOps v2**：利用 **ArgoCD ApplicationSet** 同步策略（Stage → Manifests）實現動態服務發現。

---

## 3. 實作資產

*   **原始碼路徑**：
    *   叢集佈建：`Chorde/cluster/k3han/`（Ansible 與 systemd 單元）
    *   GitOps 入口：`Chorde/gitops/k3han/root.yaml`（指向 stages/）
    *   服務清單：`Chorde/gitops/k3han/manifests/`（多重來源模式）
*   **存取方式**：
    *   請參閱 [流量進入政策](safechord.chorde.k3han.ingress.md) 了解如何透過授權通道存取管理介面。