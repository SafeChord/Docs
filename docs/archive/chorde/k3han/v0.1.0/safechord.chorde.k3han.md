---
version: v0.1.0
module: k3han
role: overview           
status: deprecated
summary: K3han 架構總覽，描述叢集設計理念與各模組整合策略。
updated: 2024-05-09
submodule_versions: null
--- 
# 🧭 K3han - Chorde 的基礎實驗場

> K3han 是 SafeChord 架構中的第一座實驗型叢集，也是我們對「可攜性、可觀察、可持續部署」的架構理想實作場。
> 
> 
> 它不僅支援 SafeZone 的服務開發，更是一張我們自繪的網路拓樸圖 —— 跨雲、跨地、跨裝置。每一個節點都被精心配置，為了讓部署變得更簡單、更可預期，也更貼近實際應用的多元場景。
> 

---

## 🛠 架構組件與技術選型摘要

`K3s`, `Tailscale`, `Traefik`, `Flannel`, `ArgoCD`, `Prometheus`, `Grafana`, `Loki`

---

## 🌐 架構理念與實踐哲學

- **以「可攜式」為核心設計**：K3s 輕量、快部署，讓我們可在個人筆電、雲端主機、桌機自由切換與擴充。
- **跨雲 / 跨區運作**：結合 Hetzner（新加坡）、GCE（台灣）、Local Device（Desktop / Laptop）進行混合部署。
- **內網即平台**：透過 Tailscale 建立一張 overlay VPN，使 K3s 跨機節點能像區網般溝通順暢。
- **模組化部署節奏**：監控、Logging、CI/CD 全以 Helm 管理並分階段上線，結合 ArgoCD 實現 GitOps。

---

## 🛰 目前已整合模組

| 組件 | 功能說明 | 安裝方式 |
| --- | --- | --- |
| K3s | Kubernetes 核心叢集 | 輕量安裝 |
| Flannel | Pod 網路（CNI） | K3s 內建 |
| Traefik | Ingress 管理與反向代理 | K3s 內建 |
| CoreDNS | 內部服務 DNS | K3s 內建 |
| ArgoCD | GitOps 與 IaC 部署控制 | Helm 安裝 |
| Prometheus | Metrics 收集與監控核心 | Helm 安裝 |
| Grafana | 可視化 UI | Helm 安裝 |
| Loki | 日誌系統 | Helm 安裝 |
| Promtail | Log Agent | Helm 安裝 |
| postgredb | 系統共用資料庫，供各模組使用 | ArgoCD 安裝 |
| sealed-secret | 機密資源加密與集中管理 | Helm 安裝 |

> 所有模組皆經過「低資源啟動」與「Tailscale 內網可存取性」測試，並可彈性關閉或切換節點。
> 

---

## 🔭 未來拓展構想

- 導入 Ansible 或 Terraform，強化基礎建設程式碼的可讀性與自動化程度。
- 整合 AlertManager，啟用關鍵組件的警示機制並與 Slack 整合。
- 將 K3han 的部署模組進一步萃取並自動化封裝，作為開源模板提供給社群使用，讓更多開發者能以低成本實作 Kubernetes 架構，無論是用於面試、個人 Lab、或小型新創專案。

---