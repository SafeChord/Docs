---
title: 'Map: Chorde Platform Framework'
doc_id: safechord.chorde
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
last_updated: '2026-01-21'
summary: Chorde 平台層的導航地圖。定義多叢集管理框架與 GitOps 同步機制。
keywords:
  - Chorde
  - Platform Layer
  - Multi-cluster
  - GitOps
  - Horde
logical_path: SafeChord.Chorde
related_docs:
  - safechord.md
  - safechord.chorde.k3han.md
parent_doc: safechord
archetype: map
code_paths:
  - Chorde/gitops/k3han
doc_version: 0.2.0
app_version: 0.2.0
---

# 🛠️ Chorde 平台層地圖 (Map)

> **Map (地圖型)**：SafeChord 生產環境的「基礎設施總指揮部」。
> *職責：管理異構叢集、統一 IaC 配置、維護交付標準。*

---

## 1. 平台願景與詞源 (Vision & Etymology)

### 🏷️ 命名由來
**Chorde** = **C**luster + **Horde** (部落)。
這個名字象徵著將散落在不同地理位置、不同供應商的計算資源，聚合為一個強大且協調的「部落」。它不僅是一個管理框架，更是 SafeChord 所有基礎設施的集結地。

---

## 2. 倉庫結構 (Repository Structure)

Chorde 採用 **Recursive GitOps (App-of-Apps)** 架構，將部署邏輯、服務目錄與實際資源解耦。

```text
Chorde/
├── cluster/                 # [Physical] 物理基礎設施配置 (K3s, Ansible)
│   └── k3han/               # k3han 叢集的節點與網路定義
│
├── gitops/                  # [State] GitOps 狀態定義根目錄
│   └── k3han/               # 特定叢集 (k3han) 的專屬配置
│       ├── stages/          # [Layer 0: Orchestrator] 部署階段指令 (入口)
│       │   ├── 00-bootstrap.yaml  # 初始化基礎套件 (ArgoCD, SealedSecrets)
│       │   ├── 01-infra.yaml      # 部署基礎設施服務 (Kafka, DB)
│       │   └── 02-ops.yaml        # 部署維運工具 (Monitoring)
│       │
        └── manifests/       # [Content] 純粹的 Kubernetes 資源聲明
            ├── 00-bootstrap/      # [Layer 1: App List] 該階段包含的 ArgoCD Application 指標
            │   ├── sealed-secret.yaml # 指向 manifests/sealed-secret/
            │   └── ...
            └── sealed-secret/     # [Layer 2: Resources] 實際的 K8s 資源定義 (Deployment/CRD)
│
├── helm-charts/             # [Logic] 本地封裝/修改的 Helm Charts (僅限必要自訂)
│
├── scripts/                 # [Imperative] 命令式工具與驗證腳本
│   ├── bootstrap.sh         # 叢集引導腳本
│   └── test/                # 連通性與健康檢查工具
│
└── legacy/                  # [Archive] 舊版本架構歸檔
```

---

## 3. 核心組件導航 (Navigation)

### 3.1 運行叢集 (Runtime Clusters)
Chorde 目前管理以下叢集實體：

*   [**K3han (Hybrid K3s)**](safechord.chorde.k3han.md):
    *   **定位**: 實驗性混合雲叢集，橫跨歐亞(v0.1.0，新版跨越台日)的輕量級平台。
    *   **用途**: SafeZone v0.2.0 的核心運行環境。

---

## 4. 工程實踐 (Engineering Practices)

Chorde 嚴格遵循以下工程準則：

1.  **GitOps as Law (Recursive)**: 所有的環境狀態（除了 Secrets）都必須在 `Chorde/gitops` 中定義。採用 **Recursive App-of-Apps** 模式，嚴格分離「階段指令 (Stages)」、「應用清單 (App List)」與「實際資源 (Resources)」。
2.  **Upstream First**: 優先使用官方/上游 Helm Charts。只有在需要深度自訂時，才將 Chart 放入 `helm-charts/` 進行封裝。
3.  **MVA (Minimum Viable Architecture)**: 在保證安全的前提下，優先選擇低資源消耗的方案（如 K3s 而非標準 K8s）。
4.  **Pure Declarative State**: `gitops/` 目錄下禁止存放命令式腳本，確保 ArgoCD 同步狀態的純淨性。

---

## 5. 快速跳轉 (Quick Access)

*   **地圖**: [K3han 叢集地圖](safechord.chorde.k3han.md)
*   **代碼**: [GitOps 配置根目錄 (K3han)](https://github.com/rebodutch/Chorde/tree/main/gitops/k3han)
*   **環境**: [環境演進策略](safechord.environment.md)
