---
title: "SafeZone Deployment: Phase Core - Core Service Modules"
doc_id: safechord.safezone.deployment.safezone-core
version: "0.1.0"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
  - "ChatGPT 4.1"
last_updated: "2025-05-19"
summary: "本文檔闡述 SafeZone 部署流程中的 'core' 階段，涵蓋核心服務模組（數據模擬器 Simulator、數據接收器 Ingestor、分析查詢 API Analytics_API）的部署細節、相依條件與健康檢查策略，旨在提供完整的數據處理流程與後端查詢能力。"
keywords:
  - SafeZone
  - deployment phase
  - core services
  - data simulator 
  - data ingestor 
  - analytics API 
  - data processing pipeline
  - backend services
  - REST API
  - health checks
  - Kubernetes
  - Helm
logical_path: "SafeChord.SafeZone.Deployment.Core"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.safezone.deployment.md" 
  - "safechord.safezone.deployment.safezone-infra.md" 
  - "safechord.safezone.deployment.safezone-init.md" 
  - "safechord.safezone.service.datasimulator.md" 
  - "safechord.safezone.service.dataingestor.md"
  - "safechord.safezone.service.analyticsapi.md"
parent_doc: "safechord.safezone.deployment"
tech_stack:
  - Python
  - FastAPI 
  - Kubernetes
  - Helm
---

# 🧱 Phase: core — 核心服務模組部署

> 本頁為 SafeZone 整體部署 subchart「core」的設計導覽，說明本階段涵蓋的主要模組、CLI 指令分派與自動化健康檢查策略。
>
> 實際部署細節與 Helm values.yaml，請參考 GitHub 對應子 chart [Safezone-Core][CoreLink] 的 `README.md` 文件。

---

## 🎯 此階段的設計目標

* 部署核心服務模組：模擬資料產出（simulator）、資料接收與 DB 寫入（ingestor）、API 查詢（analytics-api）。
* 必須建立在 infra 階段成功的基礎上（CLI 指令可操作 CLI Relay，並能串連 Redis、PostgreSQL）。
* 保證可於終端用 CLI 指令操作三大核心服務（即實際運維可調度/監控服務）。
* ConfigMap 設定需與部署位址一致，確保服務間參數同步。
* 提供完整的資料流、查詢與後端資料服務能力。

---

## 📦 模組組成

* **SIMULATOR**：可經 CLI 指令直接模擬事件產出（非僅 pod 部署，強調互動能力）。
* **INGESTOR**：資料接收與驗證模組，可被 CLI 指令觸發資料注入/處理流程。
* **ANALYTICS\_API**：對外與 CLI 指令皆可查詢資料，負責資料統計、查詢與 Dashboard 服務。

---

## 🩺 健康檢查條件（readiness probe）

* 所有服務皆實作 `/health` endpoint，並於 Deployment/Helm values.yaml 配置 readinessProbe，ArgoCD ApplicationSet 自動根據 probe 決定階段遞進。
* 除健康檢查外，CLI 指令必須能與三大服務互動並取得預期回應（非僅 pod ready，實際 CLI 操作驗證）。
* readiness 條件：

  * simulator `/health` = 200
  * ingestor `/health` = 200
  * analytics-api `/health` = 200

---

## 📁 對應 Helm chart 結構（部署路徑）

```
safezone-Deploy/helm-charts/safezone-core/
├── charts/                  # subcharts 路徑
│   ├── simulator/           # 事件模擬產出器
│   ├── ingestor/            # 資料接收與寫入模組
│   └── analytics-api/       # 資料查詢介面
├── templates/               # 統一層級參數(CONFIGMAP、INGRESS....)
├── Chart.yaml               # umbrella-chart 設定
└── values.yaml              # 基礎設置與啟用參數
```

---

## 🔗 回到部屬總覽或繼續下個 PHASE

* [deployment](safechord.safezone.deployment.md)：完整 Phase 流程與依賴條件總覽
* [safezone-init](safechord.safezone.deployment.safezone-init.md):初始化系統

[CoreLink]: https://github.com/rebodutch/SafeZone-Deploy/tree/staging/helm-charts/safezone-core
