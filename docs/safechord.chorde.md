---
title: "Map: Chorde Platform Framework" 
doc_id: safechord.chorde
version: "0.2.1"
status: active
authors:
  - "bradyhau"
  - "Gemini 3 Pro"
last_updated: "2026-01-09"
summary: "Chorde 平台層的導航地圖。定義多叢集管理框架與 GitOps 同步機制。"
keywords:
  - Chorde
  - Platform Layer
  - Multi-cluster
  - GitOps
  - Horde
logical_path: "SafeChord.Chorde"
related_docs:
  - "safechord.md"
  - "safechord.chorde.k3han.md"
parent_doc: "safechord"
archetype: map
code_paths:
  - "Chorde/gitops"
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

## 2. 核心組件導航 (Navigation)

### 2.1 運行叢集 (Runtime Clusters)
Chorde 目前管理以下叢集實體：

*   [**K3han (Hybrid K3s)**](safechord.chorde.k3han.md):
    *   **定位**: 實驗性混合雲叢集，橫跨歐亞的輕量級平台。
    *   **用途**: SafeZone v0.2.0 的核心運行環境。

---

## 3. 工程實踐 (Engineering Practices)

Chorde 嚴格遵循以下工程準則：

1.  **GitOps as Law**: 所有的環境狀態（除了 Secrets）都必須在 `Chorde/gitops` 倉庫中有對應的定義。禁止手動使用 `kubectl` 修改狀態。
2.  **MVA (Minimum Viable Architecture)**: 在保證安全的前提下，優先選擇低資源消耗的方案（如 K3s 而非標準 K8s）。
3.  **Horde Resilience**: 平台設計考量了異構網路的穩定性，確保即使在地端節點斷線時，雲端控制面仍能保持管理能力。

---

## 4. 快速跳轉 (Quick Access)

*   **地圖**: [K3han 叢集地圖](safechord.chorde.k3han.md)
*   **代碼**: [GitOps 配置根目錄](https://github.com/bradyhau/SafeChord/tree/main/Chorde/gitops)
*   **環境**: [環境演進策略](safechord.environment.md)