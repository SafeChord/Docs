---
version: v0.1.0
module: k3han
role: techdoc          
status: deprecated
summary: K3han 內節點能力描述跟通訊能力說明。
updated: 2024-05-09
submodule_versions: null
--- 
# 🧱 Cluster - K3han 的節點分布概覽

> 本頁記錄 K3han Cluster 的節點配置與網路觀察，聚焦在節點分布與延遲環境說明。
> 
> 
> 每一台機器都是這套系統的執行單位。從雲端的 Hetzner、GCE 到本地桌機與筆電，
> 
> K3han 是一個混合型、自定義、延遲可預期的開發與展示環境。
> 

---

## 🗺️ 節點總覽與硬體配置

| Node Name | CPU / RAM | Location | 機型 | Status |
| --- | --- | --- | --- | --- |
| **hz-serv-sin** | 3 vCPU / 4GB | 新加坡 | Hetzner CX32, Singapore | ✅ 正常運行 |
| **gce-agent-1** | 2 vCPU / 4GB | 台灣 | GCE e2-medium, tw | ✅ 正常運行 |
| **gce-agent-2** | 2 vCPU / 4GB | 台灣 | GCE e2-medium, tw | ✅ 正常運行 |
| **acer-agent** | i5-8500 / 16GB | 台灣、本地 | Acer VERITON N4660G | ✅ 正常運行 |
| **laptop-agent** | i7-4720HQ / 16GB | 台灣、本地 | MSI GE70 2PL | ✅ 按需運行 |
| **desktop-agent** | i5-13600K / 28GB | 台灣、本地 | 自組 + WSL 節點 | ✅ 按需運行 |

> 所有節點皆透過 Tailscale 建立 overlay VPN，模擬單一內網結構。
> 

---

## 📌 網路拓撲（Latency in ms）

根據 `tailscale ping` 結果：

| Source Host | Target Host | Latency (ms) |
| --- | --- | --- |
| gce-agent-1 | gce-agent-2 | 1 |
| gce-agent-1 | desktop-agent | 7 |
| gce-agent-2 | desktop-agent | 8 |
| hz-serv-sin | gce-agent-1 | 47 |
| hz-serv-sin | gce-agent-2 | 46 |
| hz-serv-sin | desktop-agent | 110 |
| laptop-agent | hz-serv-sin | 110 |
| laptop-agent | gce-agent-1 | 6 |
| laptop-agent | gce-agent-2 | 6 |
| laptop-agent | desktop-agent | 1 |
| acer-agent | hz-serv-sin | 64 |
| acer-agent | gce-agent-1 | 6 |
| acer-agent | gce-agent-2 | 6 |
| acer-agent | laptop-agent | 1 |
| acer-agent | desktop-agent | 1 |

📌 **主要觀察點**

- ✔ GCE-Agent 間延遲極低，作為主運算與資料流節點合適
- ✔ hz-serv-sin 與其他節點間延遲較高，PostgreSQL 採主從設計降低影響
- ✔ Acer-Agent 為核心監控 / CLI Relay 節點，延遲穩定，I/O 成本低
- ✔ Laptop-Agent、Desktop-Agent 為可按需啟用節點，支援 Dev / Compile 等重載用途

---

## 📌 常態性流量設計

| 通訊類型 | 發起者 | 來源端 | 目標端 |
| --- | --- | --- | --- |
| K3s API 通訊 | K3s Workers | all nodes | hz-serv-sin |
| SafeZone API 請求 | Dashboard | gce-agent-2 | gce-agent-1 |
| Redis Cache 查詢 | Analytics API | gce-agent-1 | gce-agent-2 |
| PostgreSQL 查詢 | Analytics API | gce-agent-1 | gce-agent-1 |
| Prometheus 抓取 | Prometheus | acer-agent | all nodes |

---

## 📌 非常態性流量設計

| 通訊類型 | 發起者 | 來源端 | 目標端 | 備註 |
| --- | --- | --- | --- | --- |
| cli-relay.db.* | CLI Relay | acer-agent | hz-serv-sin | 需 DB 超級權限 |
| cli-relay.dataflow.* | CLI Relay | acer-agent | acer-agent、gce-agent-1、hz-serv-sin | 資料產生與注入 |
| cli-relay.sys.* | CLI Relay | acer-agent | acer-agent | CLI 部署工具操作 |

> ⚠️ SafeZone UI 與 CLI Relay 也可能發出查詢 Redis 的輕量通訊，用於確認部署階段旗標狀態。
> 

---

## 📌 通訊協定與 Port 對照表

| 服務組件 | 協定 | Port | 用途說明 |
| --- | --- | --- | --- |
| K3s API Server | HTTPS | 6443 | 叢集控制層指令進出點 |
| Redis | TCP | 6379 | 快取 / 部署旗標傳遞 |
| PostgreSQL | TCP | 5432 | 資料儲存查詢主體 |
| CLI Relay | HTTP | 8000 | 內部部署控制與狀態查詢介面 |
| SafeZone Services | HTTP | 動態 | 模組間 RESTful 呼叫（見 Service） |

---

## 📌 監控 & GitOps 現況

### 🔍 Prometheus（監控）

- **監控節點**：6（全部節點均有部署 node-exporter）
- **抓取頻率**：5s（依機器負載動態調整）
- **每秒約 1000+ metrics**
- **儲存保留**：預設 7 天（搭配 Acer-Agent NFS 儲存）
- **注意事項**：尚未導入 Remote Write，未來可擴充支援

### 🔄 ArgoCD（GitOps）

- **應用數量**：3（SafeZone、PostgreSQL、Redis）
- **同步方式**：自動同步
- **來源節點**：目前由 Acer-Agent 管理
- **K3s API 存取方式**：直連，不經 Ingress

### 🪵 Loki（日誌系統）

- **目前尚未正式部署**
- **預計僅收集 SafeZone 模組日誌**，不含底層平台元件

---

## 📌 服務通訊需求摘要（角色分層）

### SafeZone

- **前端與後端串接**：RESTful API via Plotly Dash
- **資料來源模式**：API 多為 read-only 查詢，接 PostgreSQL replica 為主
- **Redis 使用**：透過 Redis Replica 緩存輔助查詢
- **請求頻率**：目前偏低頻，為展示用途設計

### Prometheus

- **節點覆蓋**：全節點部署 `node-exporter`
- **跨區流量**：未啟用 Remote Write，部署位置優化至 acer-agent

### ArgoCD

- **部署節點**：acer-agent（本地）
- **操作節點**：SafeZone、DB、Redis 的部屬節點
- **K3s 存取**：需要 direct access to API server