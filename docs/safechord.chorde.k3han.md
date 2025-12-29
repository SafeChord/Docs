---
title: "K3Han: Experimental Lightweight K3s Cluster Platform" 
doc_id: safechord.chorde.k3han
version: "0.2.0"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
last_updated: "2025-05-16"
summary: "本文檔詳細介紹 Chorde 管理下的一個實驗性子模塊 K3Han，說明其作為一個基於 K3s 的輕量級 Kubernetes 平台的具體作用、特性、基礎套件描述，及其在 Chorde 框架下的定位。"
keywords:
  - K3Han
  - K3s
  - Kubernetes
  - cluster management
  - lightweight platform 
  - experimental
  - Chorde
  - SafeChord
  - node management
  - service deployment
logical_path: "SafeChord.Chorde.K3Han"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.chorde.md"
  - "safechord.chorde.k3han.cluster.md"
  - "safechord.chorde.k3han.scheduling.md"
  - "safechord.chorde.k3han.changelog.md"
parent_doc: "safechord.chorde"
tech_stack:
  - K3s
  - Kubernetes
---
# 🧭 K3han - Chorde 的基礎實驗場

> 本版本為 K3han 架構在初始部署後的首次重構。
>
> 相較於 v0.1.0，我們重新定義了節點角色與網路邊界，強調對外流量與控制層的分離，進一步強化了 overlay-based 架構的安全性與可控性。

---

## 🛠 架構組件與技術選型摘要

`K3s`, `Tailscale`, `NGINX`, `Flannel`, `ArgoCD`, `Prometheus`, `Grafana`, `Loki`

---

## 🌐 架構理念與實踐哲學

* **將對外入口與控制層拆離**：原本由控制層 Hetzner node 處理 ingress，現已轉交由 GCP 台灣節點獨立承擔，降低延遲與風險。
* **調整節點數量與來源**：淘汰早期多個 GCE agent 測試節點，精簡為單一高配 control + 台灣入口 + 本地展示節點的 3-node 結構。
* **強化對 SafeZone 的支援與隔離**：將 SafeZone 所有模組集中至家用節點 `acer-agent`，與 control-plane 明確分層。

---

## 🛰 目前已整合模組

| 組件            | 功能說明                                         | 安裝方式                      |
| ------------- | -------------------------------------------- | ------------------------- |
| K3s           | Kubernetes 核心叢集                              | 輕量安裝                |
| Flannel       | Pod 網路（CNI）                                  | K3s 內建                |
| CoreDNS       | 內部服務 DNS                                     | K3s 內建                |
| ArgoCD        | GitOps 與 IaC 部署控制                           | Helm 安裝                |
| Prometheus    | Metrics 收集與監控核心                            | Helm 安裝               |
| Grafana       | 可視化 UI                                         | Helm 安裝               |
| Loki          | 日誌系統                                          | Helm 安裝 |
| Promtail      | Log Agent                                        | Helm 安裝              |
| sealed-secret | 機密資源加密與集中管理                                  | Helm 安裝               |
| db primary    | postgredb 主節點                                       | ArgoCD 安裝    |
| db replica    | postgredb Read-Only 副節點                       | ArgoCD 安裝    |
| NGINX         | Proxy 與基礎網路資安                              | ArgoCD 安裝        |

---

## 🔭 未來拓展構想

* 根據 GCP egress 帳單與延遲表現，考慮引入 Cloudflare Tunnel 或 Oracle Free 作為 fallback 入口
* 拆出 Loki/Prometheus 為單獨模組部署於觀察節點，或交由 acer-agent 承擔子系統收集任務
* 引入 nodeSelector 與 affinity 語意標籤，優化部署模組的調度與 zone 感知能力

---

## 🔑 建議閱讀順序

1. [cluster](safechord.chorde.k3han.cluster.md)：理解節點、網路、Tailscale 拓撲與跨區延遲策略
2. [scheduling](safechord.chorde.k3han.scheduling.md)：設定節點各種標籤以及部署策略
3. [monitoring](safechord.chorde.k3han.monitoring.md)：設定監控流程與視覺化資料串接手法

---