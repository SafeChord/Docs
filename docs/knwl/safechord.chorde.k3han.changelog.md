---
title: "K3Han: Changelog" 
doc_id: safechord.chorde.k3han.changelog
version: "N/A"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
last_updated: "2025-05-16"
summary: "本文檔記錄了 K3Han 模塊各個版本的變更歷史，包括新功能、改進、錯誤修復以及重要的更新說明。"
keywords:
  - K3Han
  - changelog
  - version history
  - release notes
  - updates
  - bug fixes
  - features
  - SafeChord
logical_path: "SafeChord.Chorde.K3Han.Changelog"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.chorde.k3han.md"
parent_doc: "safechord.chorde.k3han"
tech_stack: []
---
# 📜 SafeChord · Chorde · K3Han - 版本變更紀錄

> 本文件記錄 K3Han 架構自 v0.1.0 起的重要變更點，涵蓋節點佈局、模組部署、調度邏輯與設計哲學的轉變。每個版本皆對應可查閱之 `.md` 文件，供對比與回溯使

---

## 🔖 \[v0.2.0 - Latest] - 2024-05-09 

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

* `archive/k3han/v0.1.0/safechord.chorde.k3han.md`
* `archive/k3han/v0.1.0/safechord.chorde.k3han.cluster.md`
* `archive/k3han/v0.1.0/safechord.chorde.k3han.scheduling.md`