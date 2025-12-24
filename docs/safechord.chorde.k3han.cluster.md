---
title: "K3Han: K3s Cluster Management"
doc_id: safechord.chorde.k3han.cluster
version: "0.2.0" 
status: active 
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
last_updated: "2025-05-16" 
summary: "本文檔闡述 K3Han 模塊在描述 K3s 集群各項物理條件，包括節點配置、連線拓樸和流量預想等。"
keywords:
  - K3Han
  - K3s
  - Kubernetes
  - cluster provisioning
  - node spec
  - network topology
  - default dataflow
  - SafeChord
logical_path: "SafeChord.Chorde.K3Han.Cluster"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.chorde.k3han.md"
  - "safechord.chorde.k3han.scheduling.md"
  - "safechord.chorde.k3han.changelog.md"
parent_doc: "safechord.chorde.k3han"
tech_stack:
  - K3s
  - Kubernetes
  - Tailscale
---
# 🧱 Cluster - K3han 的節點分布概覽

> 本頁記錄 K3han Cluster 經歷節點精簡與入口重構後的版本狀態，聚焦在新版節點分布、Tailscale overlay 結構與實際延遲觀察。

> v0.2.0 起，我們將公網入口與控制平面解耦，採單點 proxy gateway 設計，同時移除多個 GCE 測試節點，強調低成本、可控、可觀測的最低可行架構（MVA）。

---

## 🗺️ 節點總覽與硬體配置

| Node Name         | CPU / RAM        | Location   | 機型                        | Status |
| ----------------- | ---------------- | ---------- | ------------------------- | ------ |
| **ct-serv-jp**    | 6 vCPU / 12GB    | 日本 Contabo | Contabo Cloud VPS 20 NVMe | ✅ 正常運行 |
| **gce-agent-tw** | 2 vCPU / 1GB     | 台灣 GCP     | GCE e2-micro, asia-east1  | ✅ 正常運行 |
| **acer-agent**    | i5-8500 / 16GB   | 台灣、本地      | Acer VERITON N4660G       | ✅ 正常運行 |
| **laptop-agent**  | i7-4720HQ / 16GB | 台灣、本地      | MSI GE70 2PL              | ✅ 按需運行 |
| **desktop-agent** | i5-13600K / 28GB | 台灣、本地      | 自組 + WSL                  | ✅ 按需運行 |

> 所有節點皆透過 Tailscale 建立 overlay VPN，模擬單一內網結構。

---

## 📌 網路拓撲（Latency in ms）

根據 `tailscale ping` 結果：

| Source Host   | Target Host   | Latency (ms) |
| ------------- | ------------- | ------------ |
| gce-agent-tw | ct-serv-jp    | \~48         |
| gce-agent-tw | acer-agent    | \~6          |
| ct-serv-jp    | acer-agent    | \~80         |
| laptop-agent  | acer-agent    | \~1          |
| laptop-agent  | desktop-agent | \~1          |
| acer-agent    | desktop-agent | \~1          |

📌 **主要觀察點**：

* ✔ ct-serv-jp 為高延遲但穩定的 control-plane，避免即時互動壓力
* ✔ gce-agent-tw 延遲最低，作為唯一對外公開 UI/HTTP 通道
* ✔ acer-agent 仍為核心展示與同步節點，維持操作流暢與部署支援

---

## 📌 常態性流量設計

| 通訊類型           | 發起者           | 來源端          | 目標端                        |
| -------------- | ------------- | ------------ | -------------------------- |
| K3s API 通訊     | K3s Workers   | all nodes    | ct-serv-jp                 |
| SafeZone 請求流量  | Public Users  | browser (外部) | gce-agent-tw → acer-agent |
| Redis Cache 查詢 | Analytics API | acer-agent   | local Redis                |
| PostgreSQL 查詢  | Analytics API | acer-agent   | pgsql-primary (ct-serv-jp) |
| Prometheus 抓取  | Prometheus    | ct-serv-jp   | all nodes                  |

---

## 📌 非常態性流量設計

| 通訊類型                  | 發起者       | 來源端        | 目標端                   | 備註          |
| --------------------- | --------- | ---------- | --------------------- | ----------- |
| cli-relay.db.\*       | CLI Relay | acer-agent | pgsql-primary         | 高權限操作       |
| cli-relay.dataflow.\* | CLI Relay | acer-agent | acer-agent、ct-serv-jp | 資料注入流程      |
| cli-relay.sys.\*      | CLI Relay | acer-agent | acer-agent            | 本地 shell 操作 |

---

## 📌 通訊協定與 Port 對照表

| 服務組件            | 協定    | Port   | 用途說明                   |
| --------------- | ----- | ------ | ---------------------- |
| K3s API Server  | HTTPS | 6443   | 叢集控制層指令進出點             |
| Redis           | TCP   | 6379   | 快取 / 部署旗標傳遞            |
| PostgreSQL      | TCP   | 5432   | 資料儲存查詢主體               |
| CLI Relay       | HTTP  | 8000   | 內部部署控制與狀態查詢介面          |
| SafeZone UI/API | HTTP  | 80/443 | 公網入口 → ingress gateway |

---

## 📌 監控 & GitOps 現況（v0.2.0）

### 🔍 Prometheus（監控）

* **監控節點**：目前保留於 `ct-serv-jp` 上部署
* **抓取頻率**：5s
* **日誌儲存與警示功能尚未開啟**，未來可補 Loki + AlertManager

### 🔄 ArgoCD（GitOps）

* **部署節點**：ct-serv-jp
* **來源倉庫**：GitHub private + workflow CI
* **控制方式**：自動同步，後續考慮加入 webhook + slack notify

### 🪵 Loki（日誌系統）

* **部署位置**：ct-serv-jp
* **目前僅收集 SafeZone API/UI log**，未包含底層元件

---

## 📌 服務通訊需求摘要（角色分層）

### SafeZone

* **前端與後端串接**：RESTful API via Plotly Dash（透過 ingress gw 代理）
* **資料來源模式**：主要讀取 pgsql-replica，寫入最小化
* **Redis 使用**：仍為輔助快取，讀多於寫

### Prometheus

* **節點覆蓋**：目前保留 node-exporter 於主要節點
* **遠端寫入尚未啟用**，視流量與儲存情況擴展

### ArgoCD

* **操作節點**：掌控 GitOps 與主體 deploy 任務
* **K3s 存取**：直接透過 tailscale 網段連至 control-plane

---