---
title: SafeChord Project Overview
doc_id: safechord
version: 0.2.0
status: active
authors:
  - bradyhau
  - Gemini 2.5 Pro
last_updated: 2025-12-28
summary: "SafeChord 是一個採用微服務架構的健康安全地圖系統，旨在展示從本地開發到混合雲運維的全鏈路工程能力。專案核心由應用層 (SafeZone) 與叢集管理層 (Chorde) 組成。Chorde 作為叢集平台總倉，目前管理著核心的混合雲 K3s 叢集 K3han。透過環境演進策略 (Environment Evolution)，系統展示了如何在高複雜度的網路拓撲下，實現穩定、安全且具彈性的服務交付。"
keywords:
  - SafeChord
  - project overview
  - MVA
  - Environment Evolution
  - Hybrid Cloud
  - K3s
  - Chorde
  - K3han
  - SafeZone
logical_path: "SafeChord"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.environment.md"
parent_doc: null
tech_stack:
  - Kubernetes (K3s, Tailscale Overlay)
  - Python (FastAPI/AsyncIO)
  - Golang (Franz-Go Batcher)
  - Kafka, PostgreSQL, Redis
  - ArgoCD, KEDA, Cloudflare
---
# SafeChord

> 一筆模擬資料，如何從 CLI 被發送、注入資料庫、經過分析後呈現在 Dashboard。
> 
> SafeChord 是一套以「完整資料流模擬 + 可部署系統設計」為核心的專案，整合應用邏輯與基礎設施技術，挑戰資源受限下的實作極限。

---

## 🎯 專案目的與背景

在資源受限（無商業預算、低成本 VPS、家用節點）的前提下，SafeChord 實踐了 **MVA (Minimum Viable Architecture)** 哲學。這不只是程式，而是將「事件 → 資料 → 視覺結果」轉化為一個具備生產級觀測性與自動化能力的 **敘事式系統實驗場域**。

---

## 🏗️ 系統模組分層

SafeChord 採用嚴格的 **Separation of Concerns (SoC)**，確保應用與設施的解耦：

| 子系統 | 職責定位 | 核心實體 |
| :--- | :--- | :--- |
| 🧪 **SafeZone** | **應用層 (Application)**：負責資料模擬生成、非同步注入、Kafka 流轉與前端可視化。 | `SafeZone` 倉庫 |
| 🛠️ **Chorde** | **叢集管理層 (Cluster Hub)**：叢集平台總倉。管理異構叢集定義與共享 PaaS 服務。 | `Chorde` 倉庫 |
| 🛰️ **K3han** | **核心實作叢集**：隸屬於 Chorde 的混合雲 K3s 叢集，是 SafeZone 的最終部署目標。 | `Docs/docs/safechord.chorde.k3han.md` |

---

## 🌍 環境演進論 (Environment Evolution)

SafeChord 展示了系統如何隨著階段演進而轉變其基礎設施型態：

*   **🟢 Level 1: Local (Dev)**: 使用 `Docker Compose`。極速啟動，專注於邏輯除錯與熱重載。
*   **🟡 Level 2: Preview (CI)**: 基於 `K8s Namespace`。自帶降級版 Infra (Ephemeral Kafka/Redis)，用於 PR 驗證。
*   **🔴 Level 3: Platform (Staging)**: 混合雲頂層環境。SafeZone 部署於 **K3han** 叢集，並作為租戶使用平台級 SaaS 服務。

---

## 🌳 知識結構樹 (Knowledge Tree)

| 層級 | 模組路徑 | 說明 |
| :--- | :--- | :--- |
| **MACRO** | [📄 SafeChord](safechord.md) | **(本頁面)** 專案總覽、目的與 MVA 設計哲學。 |
| **MACRO** | [📄 Environment](safechord.environment.md) | **環境全景**。描述從 Local 到 Staging 的演進路徑與連線對照。 |
| **BLUE** | [📄 SafeZone](safechord.safezone.md) | **應用核心**。定義非同步架構、服務邊界與資料流願景。 |
| **YELLOW** | [📄 Deployment](safechord.safezone.deployment.md) | **交付運維**。Helm Charts 結構與 GitOps (ArgoCD) 同步流程。 |
| **RED** | [📄 Chorde / K3han](safechord.chorde.k3han.md) | **基礎設施**。混合雲網路拓撲、Ingress 隔離與資源調度策略。 |
| **META** | [📄 Methodology](safechord.kdd.introduction.md) | **開發方法論**。關於 KDD (知識驅動開發) 的 AI 協作實踐。 |

---

## 🧪 Demo

  🚫 [Dashboard 前端實際環境](https://safezone.omh.idv.tw/dashboard)：展示模擬資料視覺化結果（需 OAuth 授權）。

---

## 🛠 技術選型摘要

`FastAPI (AsyncIO)`, `Golang (Franz-Go)`, `Kafka (Franz-Go)`, `Postgres`, `Redis (Versioned)`, `K3s`, `Tailscale`, `ArgoCD`, `KEDA`, `Cloudflare`