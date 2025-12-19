---
title: SafeChord Project Overview
doc_id: safechord
version: 0.2.0
status: active
authors:
  - bradyhau
  - Gemini 2.5 Pro
last_updated: 2025-05-16
summary: "SafeChord 是一個採用微服務架構的專案，旨在提供即時與歷史的健康安全地圖資訊（如 COVID-19 疫情數據），並透過輕量級 Kubernetes (K3s) 管理功能，建構安全且具韌性的應用環境。此專案的核心組件包括：以 Kubernetes (K8s) 為基礎的多叢集管理核心 Chorde，以及負責安全資訊地圖的 SafeZone 系統。SafeChord 致力於為使用者提供全面的安全資訊，並為此服務打造穩健可靠的運行平台。"
keywords:
  - SafeChord
  - project overview
  - goals
  - decentralized orchestration
  - secure application environment
  - K3s management
  - Chorde
  - SafeZone
  - system architecture
  - microservice
  - health safety map
  - vision
logical_path: "SafeChord"
related_docs:
  - "safechord.tree.md"
parent_doc: null
tech_stack:
  - Kubernetes (K3s)
  - Microservice application 
---
# SafeChord

> 一筆模擬資料，如何從 CLI 被發送、注入資料庫、經過分析後呈現在 Dashboard
> 
> 
> SafeChord 是一套以「完整資料流模擬 + 可部署系統設計」為核心的專案，整合應用邏輯與基礎設施技術，挑戰資源受限下的實作極限。
> 

---

## 🎯 專案目的與背景

在沒有商業預算、團隊、雲平台優惠的前提下，我希望自己打造一套：

- 可模擬真實事件（如疫情爆發）
- 可觀察數據流動的技術系統
- 可視化、可擴展、可維運的全鏈設計

這不只是程式，而是從「事件 → 資料 → 可見結果」的 **敘事式系統實驗場域**。

---

## 🧱 系統模組分層總覽

SafeChord 拆為兩大子系統：

| 子系統 | 功能概述 |
| --- | --- |
| 🧪 SafeZone | 提供模擬資料流的應用層模組（產生、儲存、查詢、可視化） |
| 🛠 Chorde / K3han | 管理基礎設施的基礎模組（負責部署、串接、觀測與同步控制） |

> 想看整體系統架構圖？📈 [點我查看完整架構圖與模組互動圖](knwl/safechord.workflow.md)
> 

[test](material/index.md)
---

## 🛠 技術選型摘要

`FastAPI`, `Pydantic`, `Redis`, `PostgreSQL`, `K3s`, `Helm`, `Tailscale`, `ArgoCD`, `Loki`, `Grafana`

---

## 🌳 SafeChord 知識結構樹

以下為本專案文件的分層結構。你可以從任一你有興趣的模組開始閱讀，無需依照順序。

||||顆粒度|說明|
|---|---|---|---|---|
|[SAFECHORD](index.md)|||MACRO|本頁面總覽與導航入口|
||[SAFEZONE](knwl/safechord.safezone.md)||MACRO|定義 SafeZone 架構與資料流邏輯|
|||[SERVICE](knwl/safechord.safezone.service.md)|MID|拆解模組職責與資料流動方式|
|||[CI-CD](knwl/safechord.safezone.ci-cd.md)|MID|展示自動化測試、建置與部署流程|
|||[DEPLOYMENT](knwl/safechord.safezone.deployment.md)|MID|總覽部署階段與 Helm Chart 結構|
||[CHORDE/K3HAN](knwl/safechord.chorde.k3han.md)||MACRO|說明 K3HAN 架構與資源管理理念|
|||[CLUSTER](knwl/safechord.chorde.k3han.cluster.md)|MID|描述節點拓撲、效能觀測與資源配置|
|||[SCHEDULING](knwl/safechord.chorde.k3han.scheduling.md)|MICRO|K3HAN 運算分配與排程原則|
|||[MONITORING](knwl/safechord.chorde.k3han.monitoring.md)|MICRO|展示 K3HAN 資源監控與數據管線|
|||[IaC](knwl/safechord.chorde.k3han.iac.md)|MID|描述 K3HAN 的 IaC 管理與重建能力|
|||[BUILD](knwl/safechord.chorde.k3han.build.md)|MICRO|呈現建置流程與各元件組裝方式|

### [想看完整結構樹請點這](knwl/safechord.tree.md)

## 🧪 Demo

  🚫 [Dashboard 前端實際環境](https://safezone.omh.idv.tw/dashboard)：提供模擬資料視覺化結果展示

---

## 🧭 推薦閱讀順序

這份文檔可自由探索，但如果你希望快速掌握整體系統設計，我推薦從以下幾個節點開始：

1. [SafeZone](knwl/safechord.safezone.md)：提供模擬資料流的應用層模組（產生、儲存、查詢、可視化）
2. [K3han](knwl/safechord.chorde.k3han.md)：管理基礎設施的基礎模組（負責部署、串接、觀測與同步控制）