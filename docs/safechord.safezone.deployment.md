---
title: "SafeZone: Application Deployment Overview"
doc_id: safechord.safezone.deployment
version: "0.1.0"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
last_updated: "2025-05-16"
summary: "本文檔作為 SafeZone 應用程式部署的總體指南，概述了其部署策略、各階段 (infra, core, init, ui) 的轉換條件、Helm Chart 結構拆分原則，以及推薦的閱讀順序以理解完整的部署流程與模組化設計。"
keywords:
  - SafeZone
  - application deployment
  - deployment strategy
  - Kubernetes (K3s)
  - Helm charts
  - deployment phases
  - infrastructure setup
  - core services deployment
  - initialization process
  - UI deployment
  - SafeChord
logical_path: "SafeChord.SafeZone.Deployment"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.safezone.md"
  - "safechord.safezone.deployment.safezone-infra.md"
  - "safechord.safezone.deployment.safezone-core.md"
  - "safechord.safezone.deployment.safezone-init.md"
  - "safechord.safezone.deployment.safezone-ui.md"
parent_doc: "safechord.safezone"
tech_stack:
  - Kubernetes (K3s)
  - Helm
  - Docker
  - ArgoCD
---
# 🚀 SafeZone 部署與模組拆解總覽

> 本頁記錄 SafeZone 系統的模組部署邏輯、服務健康檢查策略與各階段 chart 拆分原則。
目標是提供一份完整的部署流程與模組化設計脈絡，方便後續擴展、除錯與 CI/CD 串接。
> 

## 🔄 Phase 轉換條件

系統會根據各模組健康狀態與 Redis flag 判定當前部署階段：

1. **infra → core**：Redis、PostgreSQL 均可連線
2. **core → init**：Simulator / Ingestor / Analytics API 的`/health` 全部回傳 200
3. **init → ui**：Redis flag `safezone:phase:initJob = completed` 
4. **ui**：Dashboard `/health` 回傳 200

---

## 🔧 其他部署補充與未來構想

- Umbrella chart（safezone-master）未來可統籌各 Phase enable/disable。
- safezone-master 未來也講統一 value 窗口，讓部屬更輕鬆。
- 可考慮 ArgoCD Sync Wave 或 GitHub Actions 中增設部署 gating 條件。

---

## 🧭 推薦閱讀順序

若你希望依照模組部署邏輯深入理解，可參考以下子頁：

1. [safezone-infra](safechord.safezone.deployment.safezone-infra.md)：非微服務層的部署與基礎建設設定
2. [safezone-core](safechord.safezone.deployment.safezone-core.md)：主服務模組與其啟動順序
3. [safezone-init](safechord.safezone.deployment.safezone-init,md)：Init Job 流程與 CLI 整合策略
4. [safezone-ui](safechord.safezone.deployment.safezone-ui.md)：Dashboard 視覺化模組的布署策略與前置條件