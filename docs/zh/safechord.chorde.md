---
title: 'Map: Chorde Platform Framework'
doc_id: safechord.chorde
status: active
authors:
  - bradyhau
  - Gemini 2.0 Flash
last_updated: '2026-03-11'
summary: Chorde 平台層的導航地圖。定義多叢集管理框架、GitOps v2 同步機制與基礎設施生命週期管理。
keywords:
  - Chorde
  - Platform Layer
  - Multi-cluster
  - GitOps v2
  - ApplicationSet
  - Hybrid Cloud
logical_path: SafeChord.Chorde
related_docs:
  - safechord.md
  - safechord.chorde.k3han.md
parent_doc: safechord
archetype: map
code_paths:
  - Chorde/cluster
  - Chorde/gitops
doc_version: 0.3.0
app_version: 0.3.0
---

# 🛠️ Chorde 平台層地圖 (Map)

> **Map (地圖型)**：SafeChord 生產環境的「基礎設施總指揮部」。
> *職責：管理異構叢集、實施 GitOps v2 交付、維護混合雲安全邊界。*

---

## 1. 平台願景 (Vision)

**Chorde** (= Cluster + Horde) 旨在建立一個「去中心化但高度協調」的基礎設施部落。在 v0.3.0 中，平台已從單純的 IaC 腳本集轉型為 **Operator-managed** 的現代化平台，實現了「代碼即環境，文檔即來源」的 KDD 閉環。

---

## 2. 倉庫結構 (Repository Structure)

Chorde 採用 **Recursive GitOps v2** 架構，透過 `root.yaml` 實現單一入口的自動化編排。

```text
Chorde/
├── cluster/                 # [Physical] 物理基礎設施定義
│   └── k3han/               
│       ├── ansible/         # 行為紀錄：節點初始化與防火牆硬化
│       └── k3s/             # 節點描述：K3s 配置備份
│
├── gitops/                  # [State] GitOps 狀態定義核心 (SSOT)
│   └── k3han/               
│       ├── root.yaml        # 全域入口點 (The Root App)
│       ├── stages/          # [Layer 0: Orchestrator] 部署階段指令
│       │   ├── 00-bootstrap.yaml  # 核心：ArgoCD, SealedSecrets
│       │   ├── 01-platform.yaml   # 維運：Monitoring, Logging, Ingress
│       │   └── 02-components.yaml # 應用：DB, MQ, SafeZone Services
│       │
│       └── manifests/       # [Content] 宣告式資源 (YAML)
│           ├── alloy/       # 採用 Multiple Sources Pattern 
│           ├── cnpg-*/      # CloudNativePG 資源定義
│           └── ...          # 其他 20+ 平台服務
│
├── scripts/                 # [Lifecycle] 運作與測試工具
│   ├── ops/                 # bootstrap-cluster.sh, seal.sh
│   └── test/                # 跨區連線、DB 同步、Ingress 隔離測試
│
└── legacy/                  # [Archive] 舊版 (v0.1.x / v0.2.x) 歸檔
```

---

## 3. 核心組件導航 (Navigation)

### 3.1 運行叢集 (Runtime Clusters)
*   [**K3han (Hybrid K3s)**](safechord.chorde.k3han.md):
    *   **定位**: 高度非對稱的台日混合雲。
    *   **現況**: 運行 K3s v1.34+，透過 Tailscale Overlay 屏蔽地理差異。

---

## 4. 工程實踐 (Engineering Practices v2)

Chorde 嚴格遵循以下 SRE 工程準則：

1.  **ArgoCD Multiple Sources**: 廢棄 `helm-charts/` 本地目錄。直接引引用官方 Helm Chart (Upstream) 並搭配本地 `values-custom.yaml` 進行覆蓋，減少倉庫體積。
2.  **ApplicationSet Pattern**: 採用 `ApplicationSet` 取代單體 `Application`，實現自動化的服務偵測與層級同步 (Sync Waves)。
3.  **Operator-First**: 基礎設施服務（DB, Kafka）全面轉向 **Operator-managed** 模式，確保具備自我修復與平滑升級能力。
4.  **Availability Filter**: 利用 Taints (`PreferNoSchedule`) 建立地端與雲端的可用性分層，保護關鍵負載不誤入非 HA 環境。
5.  **Test-Driven Ops**: 所有重大配置更動後，必須執行 `scripts/test/` 下的驗證腳本以符合「Test is the Law」政策。

---

## 5. 快速跳轉 (Quick Access)

*   **叢集地圖**: [K3han 混合雲地圖](safechord.chorde.k3han.md)
*   **調度策略**: [K3han 排程大腦 (Brain)](safechord.chorde.k3han.scheduling.md)
*   **倉庫源碼**: [SafeChord/Chorde (GitHub)](https://github.com/SafeChord/Chorde)
