---
title: "SafeZone: Health Safety Map Application Overview"
doc_id: safechord.safezone
version: "0.1.0"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
last_updated: "2025-05-16"
summary: "本文檔作為 SafeZone 應用程式的總體概述，介紹其核心目標——提供即時與歷史的健康安全地圖資訊（以 COVID-19 疫情數據為例）。它將引導讀者了解 SafeZone 的主要服務組件、CI/CD 實踐，以及其專屬的部署架構與流程。" 
keywords:
  - SafeZone
  - health safety map 
  - data application
  - COVID-19 data
  - application overview
  - service architecture 
  - deployment strategy 
  - CI/CD process 
  - data visualization 
  - API services 
  - microservices 
  - SafeChord 
logical_path: "SafeChord.SafeZone"
related_docs:
  - "safechord.knowledgetree.md" 
  - "safechord.md"
  - "safechord.safezone.service.md"
  - "safechord.safezone.deployment.md"
  - "safechord.safezone.ci-cd.md"
  - "safechord.safezone.changelog.md"
parent_doc: "safechord"
tech_stack:
  - "Frontend: Plotly Dash"
  - "Backend: FastAPI"
  - "Architecture: Microservice on Kubernetes (K3s)"
  - "Primary Language: Python"
  - "Data Storage: PostgreSQL, Redis"
---
# SafeZone

> SafeZone 是 SafeChord 的資料應用主體，負責從資料產生、處理、查詢到前端呈現的整條流程。
> 
> 
> 在這個模擬場域裡，SafeZone 就像是一條自造資料之河，讓事件不只是發生，更能被觀察、理解、再利用。
> 

---

## 🛠 技術選型摘要

`FastAPI`, `Pydantic`, `Redis`, `PostgreSQL`, `Plotly Dash`, `Docker`, `GitHub Actions`

---

## 📁 SafeZone 文件結構

||||顆粒度|說明|
|---|---|---|---|---|
|[SAFEZONE](safechord.safezone.md)|||MACRO|整體架構說明，負責疫情數據處理與視覺化的模組化系統|
||[CI-CD](safechord.safezone.ci-cd.md)||MID|描述 TDD 測試策略、GitHub Actions 與 ArgoCD 部署流程|
||[SERVICES](safechord.safezone.service.md)||MID|統整各模組職責與資料在系統中的流動關係|
|||[DATASIMULATOR](safechord.safezone.service.datasimulator.md)|MICRO|模擬 CLI 行為產生測試資料，支援 CI/CD 驗證與本地測試|
|||[DATAINGESTOR](safechord.safezone.service.dataingestor.md)|MICRO|接收模擬或實際資料並寫入 PostgreSQL 資料庫|
|||[ANALYTICSAPI](safechord.safezone.service.safezoneanalyticsapi.md)|MICRO|對外提供查詢服務並負責資料驗證與快取處理|
|||[DASHBOARD](safechord.safezone.service.safezonedashboard.md)|MICRO|將查詢與分析結果以前端圖表呈現供使用者瀏覽|
|||[SAFEZONECLI](safechord.safezone.servicesafezonecli.md)|MICRO|提供登入、模擬操作等命令行工具，為測試與互動入口|
||[DEPLOYMENT](safechord.safezone.deployment.md)||MID|概述 Helm 架構與模組部署策略，含階段性發佈邏輯|
|||[SAFEZONE-INFRA](safechord.safezone.deployment.safezone-infra.md)|MICRO|定義 Redis、PostgreSQL 與系統服務的基礎部署設定|
|||[SAFEZONE-CORE](safechord.safezone.deployment.safezone-core.md)|MICRO|部署 SafeZone 主核心（API + Dashboard），並與資料層對接|
|||[SAFEZONE-INIT](safechord.safezone.deployment.safezone-init.md)|MICRO|初始化模組，負責設定預設值與部署流程初期狀態|
|||[SAFEZONE-UI](safechord.safezone.deployment.safezone-ui.md)|MICRO|部署 CLI Relay 與登入互動模組，連接內部模組與前端|

---

## 🔭 未來發展方向

- 可切換至真實資料來源，例如 OurWorldInData 或政府開放資料平台，驗證整體資料流架構的健壯性與實用性。
- 前端視覺化模組可擴展為世界地圖樣式，整合多語系、國際風險地圖與互動式 UI 控制。
- 模擬主題不僅限於疫情，未來可涵蓋 PM2.5、紫外線、地震速報、用電安全等「時效性強」的公共資料應用場景。
- 與其他開放平台資料整合，實作資料轉換標準與資料治理機制，提升系統資料兼容性與外部拓展能力。

SafeZone 的願景不只是「跑得起來」，而是成為一套可以被延伸、被接軌、甚至能支援社會議題演練的資料系統範本。

---

## 🧭 推薦閱讀順序

如果你希望循序掌握整個 SafeZone 系統，可以依照以下順序深入：

1. [services](safechord.safezone.service.md)：模組與功能總覽
2. [ci-cd](safechord.safezone.ci-cd.md)：測試與部署整合策略
3. [deployment](safechord.safezone.deployment.md)：部署細節頁面入口