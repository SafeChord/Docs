---
title: 'K3Han: Changelog'
doc_id: safechord.chorde.k3han.changelog
status: active
authors:
  - bradyhau
  - Gemini 2.5 Pro
last_updated: '2025-05-16'
summary: 本文檔記錄了 K3Han 模塊各個版本的變更歷史，包括新功能、改進、錯誤修復以及重要的更新說明。
keywords:
  - K3Han
  - changelog
  - version history
  - release notes
  - updates
  - bug fixes
  - features
  - SafeChord
logical_path: SafeChord.Chorde.K3Han.Changelog
related_docs:
  - safechord.knowledgetree.md
  - safechord.chorde.k3han.md
parent_doc: safechord.chorde.k3han
tech_stack: []
doc_version: 0.2.0
app_version: 0.2.0
---
# 📜 SafeChord · Chorde · K3Han - 版本變更紀錄

> 本文件記錄 K3Han 架構自 v0.1.0 起的重要變更點，涵蓋節點佈局、模組部署、調度邏輯與設計哲學的轉變。每個版本皆對應可查閱之 `.md` 文件，供對比與回溯使用。

---

## 🔖 [v0.3.0 - Latest] - 2026-03-07

**本版核心變更：**

* **GitOps v2 架構重構**：
    * 引入 `ApplicationSet` 取代單一 `Application` 模式，實現動態服務註冊與層級編排。
    * 實施三階段同步策略 (Stages)：`00-bootstrap` (基礎)、`01-platform` (維運)、`02-components` (應用組件)。
    * 建立 `root.yaml` 作為全域 GitOps 入口點 (Entry Point)。
* **配置模式現代化**：
    *   **基礎設施 Operator 化**：正式完成從 Bitnami 系單體 Helm Charts 轉向 **Operator-managed** 部署模式。
        *   **PostgreSQL**: 採用 CloudNativePG (CNPG) 替代原先的 Bitnami PostgreSQL Chart，實現更原生的備援與擴展管理。
        *   **Kafka**: 採用 Strimzi Operator 替代 Bitnami Kafka Chart，並統一使用官方 Helm Chart 進行 Operator 的生命週期管理。
    *   **ArgoCD Multiple Sources Pattern**：直接引用各組件官方 Helm Chart (Upstream) 並搭配本地 `$chorde-repo` 的 `values-custom.yaml` 進行客製化。
    *   正式廢棄並移除 `helm-charts/` 本地目錄，降低倉庫維護複雜度。
* **基礎設施與維運優化**：
    * 固化所有 Manifests 路徑至 `main` 分支。
    * 明確 Ansible Playbooks 作為「行為紀錄 (Record of Actions)」之定位，以應對高變異度的節點環境。
    * 完成 Loki 存儲後端遷移至 S3 (Amazon S3 JP)。
    * 優化 Prometheus 抓取規則，消除 Grafana 指標抓取的日誌噪音。
* **代理人治理規範**：
    * 更新 `.rule/10-chorde.md`，在授權前提下開放 `kubectl`、`argocd`、`logcli` 等工具存取權，強化 AI 代理人的故障排除能力。

📂 對應文件：

* `safechord.chorde.k3han.md` (架構總覽)
* `safechord.chorde.k3han.cluster.md` (叢集細節)
* `safechord.chorde.k3han.monitoring.md` (監控優化)

---

## 🔖 [v0.2.0] - 2024-05-09 

**本版核心變更：**

* 移除 `hz-serv-sin`、`gce-agent-1`、`gce-agent-2` 等初期測試節點
* 引入單一 control-plane：`ct-serv-jp`（Contabo 日本高配 VPS）
* 建立台灣對外入口節點 `gce-agent-tw`，並移除 UI 模組直接暴露的設計
* 將所有展示模組與 PostgreSQL replica 集中至 `acer-agent`
* 更新 cluster latency 拓撲、overlay 架構與 tailscale 覆蓋節點
* 重新設計 node label/taint，反映 tier 與 avail 優先順序
* 更新模組部署表與 affinity 排程語法，採用三層節點策略（control / ingress / dev）

📂 對應文件：

* `safechord.chorde.k3han.md`
* `safechord.chorde.k3han.cluster.md`
* `safechord.chorde.k3han.scheduling.md`

---

## 🏁 \[v0.1.0] - 2024-05-04

**初始版本特性：**

* 採用 Hetzner 新加坡為主控節點（`hz-serv-sin`）
* GCP 台灣區雙節點部署 Dashboard / API
* PostgreSQL 主從部署於 Hetzner + GCP
* 基於 tailscale overlay 實現初步跨區連線測試
* 各節點設定初步 label 與 taint，用於功能隔離與容錯測試
* 模組皆以單節點配置為主，驗證可行性與資源佔用比

📂 對應文件：

* `archive/chorde/k3han/v0.1.0/safechord.chorde.k3han.md`
* `archive/chorde/k3han/v0.1.0/safechord.chorde.k3han.cluster.md`
* `archive/chorde/k3han/v0.1.0/safechord.chorde.k3han.scheduling.md`
* `archive/chorde/k3han/v0.1.0/safechord.chorde.k3han.spec.md`