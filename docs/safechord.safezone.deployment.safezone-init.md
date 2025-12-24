---
title: "SafeZone Deployment: Phase Init - System Initialization"
doc_id: safechord.safezone.deployment.safezone-init
version: "0.1.0"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
  - "ChatGPT 4.1"
last_updated: "2025-05-19"
summary: "本文檔"記錄 SafeZone 部署流程中的 'init' 階段，聚焦 Init Job 的設計目的、CLI 驗證、依賴資源連線與初始化邏輯，配合自動化流程與 Helm 部署標準。"
keywords:
  - SafeZone
  - deployment phase
  - init 
  - initialization job
  - data initialization
  - database schema
  - seed data
  - Redis flag
  - CLI execution
  - Kubernetes Job
  - Helm
logical_path: "SafeChord.SafeZone.Deployment.Init"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.safezone.deployment.md"
  - "safechord.safezone.deployment.safezone-core.md"
  - "safechord.safezone.deployment.safezone-ui.md"
parent_doc: "safechord.safezone.deployment"
tech_stack:
  - Python
  - Redis
  - PostgreSQ
  - Kubernetes (Job)
  - Helm
---

# 🧱 Phase: init — 系統初始化流程

> 本頁為 SafeZone 部署 subchart「init」的設計導覽，說明本階段如何自動驗證各依賴連線、執行 CLI 初始化指令，以及如何銜接 UI 階段。
> 實際 Helm chart 與 values.yaml 請參見 GitHub 對應子模組的 [README.md][InitLink] 文件。

---

## 🎯 此階段的設計目標

* 在所有核心服務（simulator, ingestor, analytics-api）部署完成後，自動執行初始化任務
* 透過 CLI 指令驗證 infra/core 資源連線（包含 DB/Redis/CLI Relay 等）
* 利用 CLI 指令執行建表、資料初始化與模擬資料流灌入，便於本地測試及 CI/CD 整合

---

## 📦 Init Job 組成與執行任務

* 基於 CLI image，僅需 CLI 指令本體（非 relay server）
* 依序執行「sys/connect」等驗證指令，確認與 DB/Redis/核心服務連線通暢
* 執行主要初始化指令：

  * `db/init`：資料庫建表、系統參數設定
  * `dataflow/simulate`：灌入預設模擬資料（如 2023-03-01 至 2023-06-30）
* 所有指令、參數由環境變數或 ConfigMap 注入，方便多環境複用與 CI/CD 腳本調用

---

## 🩺 健康檢查與成功標準

* Init Job 成功條件為：所有外部依賴（DB/Redis/CLI Relay）連線正常，初始化資料正確寫入
* CLI 指令需能回傳 success（exit code 0）並明確 log 成功/失敗
* 若任一依賴無法連線或資料操作異常，init job 應自動 fail，並由 K8s Job 機制自動重試/報錯
* 此階段成功後，ArgoCD ApplicationSet 自動推進 UI 部署 wave

---

## 📁 對應 Helm chart 結構（部署路徑）

```
safezone-Deploy/helm-charts/safezone-init/
├── templates/               # 所有模板
|   └── job.yaml
├── Chart.yaml               # chart 設定
└── values.yaml              # 基礎設置與啟用參數
```

---

## 🔗 回到部屬總覽或繼續下個 PHASE

* [deployment](safechord.safezone.deployment.md)：完整 Phase 流程與依賴條件總覽
* [safezone-ui](safechord.safezone.deployment.safezone-ui.md)：部屬視覺化頁面

[InitLink]: https://github.com/rebodutch/SafeZone-Deploy/tree/staging/helm-charts/safezone-init
