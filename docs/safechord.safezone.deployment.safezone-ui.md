---
title: "SafeZone Deployment: Phase UI - Dashboard Visualization Module"
doc_id: safechord.safezone.deployment.safezone-ui
version: "0.1.0"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
last_updated: "2025-05-16"
summary: "本文檔為 SafeZone 部署流程中 'ui' 階段的設計導覽，說明前端 Dashboard 視覺化模組的啟動條件、健康檢查機制、及其與後端查詢 API (analytics-api) 和 Redis 的依賴與整合方式，目標是提供系統前端介面與數據展示，同時也會部屬公開文件展示網站。"
keywords:
  - SafeZone
  - deployment phase
  - ui 
  - dashboard deployment
  - data visualization
  - frontend interface
  - Plotly Dash
  - health checks
  - API integration
  - Redis connectivity
  - Kubernetes
  - Helm
  - documentation site
  - MkDocs 
logical_path: "SafeChord.SafeZone.Deployment.UI"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.safezone.deployment.md" 
  - "safechord.safezone.deployment.safezone-init.md" 
  - "safechord.safezone.service.dashboard.md"
parent_doc: "safechord.safezone.deployment"
tech_stack:
  - Plotly Dash 
  - Python
  - Redis
  - Kubernetes
  - Mkdoc
  - Helm
---
# 🧱 Phase: ui — Dashboard 視覺化模組部署（設計導覽）

> 本頁為 safezone-ui chart 的部署設計導覽，
說明 Dashboard 的啟動條件、健康檢查與依賴模組整合方式。
實際 Helm chart 設定與 values.yaml 說明，請參考 GitHub 對應子模組的 README.md 文件。
> 

---

## 🎯 此階段的設計目標

- 提供系統前端介面與資料視覺化展示
- 僅在核心模組與資料初始化完成後啟動
- 保持與後端查詢 API 與 Redis 的穩定連線，確保資料一致性

---

## 📦 模組組成

- **DASHBOARD**：採用 Plotly Dash 架構，展示模擬資料、疫情趨勢圖與資料摘要表格
- 所有呈現皆依賴後端 `analytics-api` 提供的查詢接口

---

## 🩺 健康檢查條件（readiness probe）

- 實作 `/health` endpoint，啟動後回傳 200 表示 UI 已可服務
- CLI Relay 使用此 endpoint 判斷是否已完成 `ui` 階段

---

## 📁 對應 Helm chart 結構（部署路徑）

```
safezone-Deploy/helm-charts/safezone-ui/
├── charts/                  # subcharts 路徑
│   └── dashboard/           # 使用者介面
├── templates/               # 統一層級參數(CONFIGMAP、INGRESS....)
├── Chart.yaml               # umbrella-chart 設定
└── values.yaml              # 基礎設置與啟用參數

```

---

## 🔗 回到部屬總覽

- [deployment](safechord.safezone.deployment.md)：完整 Phase 流程與依賴條件總覽