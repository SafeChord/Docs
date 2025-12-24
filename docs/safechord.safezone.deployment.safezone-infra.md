---
title: "SafeZone Deployment: Phase Infra - Data & CLI Foundation"
doc_id: safechord.safezone.deployment.safezone-infra
version: "0.1.1" 
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
  - "ChatGPT 4.1"
last_updated: "2025-05-19"
summary: "本文檔詳細描述 SafeZone 部署流程中的 'infra' 階段，重點闡述作為所有 SafeZone 組件共同依賴的基礎設施（如 Redis 快取、CLI Relay 橋接器）的部署邏輯、拆分原則與健康檢查整合方式，確保資料存取與系統狀態查詢功能可用。" 
keywords:
  - SafeZone
  - deployment phase
  - infra
  - Redis 
  - CLI Relay 
  - data cache
  - status synchronization
  - PostgreSQL connectivity
  - shared dependencies
  - Kubernetes
  - Helm
logical_path: "SafeChord.SafeZone.Deployment.Infra"
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.safezone.deployment.md"
  - "safechord.safezone.service.cli.md"
  - "safechord.safezone.deployment.safezone-core.md"
parent_doc: "safechord.safezone.deployment"
tech_stack:
  - Python 
  - Kubernetes
  - Helm
  - Bitnami Redis
---
# 🧱 Phase: infra — 資料庫與 CLI 功能部署

> 本頁為 SafeZone 整體部署 subchart「infra」的設計導覽，說明本階段如何為系統建立穩定基礎（快取、CLI、共用 config），以及健康檢查條件如何支援 ArgoCD ApplicationSet Wave 自動化。
>
> 實際部署細節與 Helm values.yaml，請參考 GitHub 對應子 chart [Safezone-infra][InfraLink] 的 `README.md` 文件。

---

## 🎯 此階段的設計目標

* 為所有 SafeZone 組件建立共同依賴基礎設施（如 Redis 應用快取、CLI-Relay 指令協調）
* 提供系統公用設定（ConfigMap），使後續服務部署參數一致
* 本階段資源 Ready，才能進入下個 wave 部署（自動由 ArgoCD ApplicationSet 控制）
* CLI Relay 主要協調 CLI 操作本身，不再負責流程 gating/狀態控制

---

## 📦 模組組成

* **Redis**：採用 bitnami/redis，僅作為應用層快取（如查詢加速、session、暫存資料等）。**現階段 Redis 不再用於任何系統 gating、flag 或流程狀態控制。**
* **CLI Relay**：單純負責 CLI 指令橋接與協作服務，不再負責系統部署流程或 flag 判斷，僅提供 CLI 與核心服務之間的溝通能力。詳細功能請見 [CLI 說明文件][InfraService]。
* **ConfigMap**：儲存系統共用配置（如 DB/Redis URI、環境參數），所有組件以此為環境依據。
* **Ingress**：統一管理進出流量，API/UI 服務入口。

---

## 🩺 健康檢查與 gating 條件

為確保部署流程自動化、準確移交下一階段（ArgoCD Wave），本階段健康檢查條件如下：

1. **PostgreSQL primary/replica 可連線**（非僅 Pod Ready，需實際連線 select 測試）
2. **Redis 可連線且回應正確**
3. **CLI Relay /health endpoint 回應 200**
4. **ConfigMap 已正確建立**
5. **Ingress 已正確建立**（可考慮驗證對外端口可通）

所有條件已落實於對應的 ApplicationSet.yaml 或 readinessProbe 實作中。

---

## 📁 對應 Helm chart 結構（部署路徑）

```
safezone-Deploy/helm-charts/safezone-infra/
├── charts/                  # subcharts 路徑
│   ├── redis/               # Bitnami Redis subchart
│   └── cli-relay/           # CLI Relay subchart
├── templates/               # yaml 模板（ConfigMap、Ingress、Probe）
│   ├── configmap.yaml       # 統一層級參數(如相互存取位址)
│   ├── ingress.yaml         # 連線方式統一設定
├── Chart.yaml               # umbrella-chart 設定
└── values.yaml              # 基礎設置與啟用參數
```

---

## 📝 工程決策與未來擴展

> \[決策說明] 自 0.1.2 版起，SafeZone infra phase 不再於 Redis 儲存任何流程 gating/狀態 flag，全部部署/健康檢查 gating 交由 ArgoCD ApplicationSet 與 Kubernetes readinessProbe 自動化控制。Redis 僅作為應用快取層使用。若未來有多環境/高複雜 gating 需求，可考慮額外引入獨立 gating job。

---

## 🔗 回到部屬總覽或繼續下個 PHASE

* [deployment](safechord.safezone.deployment.md)：完整 Phase 流程與依賴條件總覽
* [safezone-core](safechord.safezone.deployment.safezone-core.md)：部屬核心功能
* [CLI](safechord.safezone.service.cli.md)：CLI 系統指令功能說明

[InfraLink]: https://github.com/rebodutch/SafeZone-Deploy/tree/staging/helm-charts/safezone-infra
[InfraService]: safechord.safezone.service.cli.md
