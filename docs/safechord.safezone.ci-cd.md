---
title: "SafeZone: CI/CD Pipeline and Automation"
doc_id: safechord.safezone.workflow.ci-cd
version: "0.1.0"
status: active
authors:
  - "bradyhau"
  - "Gemini 2.5 Pro"
last_updated: "2025-05-16"
summary: "本文檔詳細說明 SafeZone 應用程式的持續整合 (CI) 與持續部署 (CD) 流程，包括測試策略 (單元測試、整合測試)、容器化階段、以及使用 Docker Compose 進行本地驗證和 ArgoCD 進行分段部署至 Kubernetes 集群的實踐。"
keywords:
  - SafeZone
  - CI/CD
  - continuous integration
  - continuous deployment
  - testing strategy
  - unit testing
  - integration testing
  - containerization
  - Docker
  - Docker Compose
  - ArgoCD
  - GitOps
  - Kubernetes deployment
  - SafeChord
logical_path: "SafeChord.SafeZone.Workflow.CICD" 
related_docs:
  - "safechord.knowledgetree.md"
  - "safechord.safezone.md"
  - "safechord.safezone.deployment.md"
parent_doc: "safechord.safezone"
tech_stack:
  - Docker
  - Docker Compose
  - Kubernetes (K3s)
  - ArgoCD 
  - GitHub Actions
  - Pytest
---
# Safezone/CI-CD

## SafeZone CI/CD Flow

本文件說明 SafeZone 專案的 CI/CD 策略與實作導向，目標是確保每階段服務部署穩定、可驗證，並可被日後擴展自動化流程所支援。

---

### CI: Continuous Integration

### 1. Service 測試流程

- **目的**：確保每個模組（API、Dashboard 等）具備基本邏輯正確性與邊界測試覆蓋
- **包含**：
    - Unit test：模組內部的單元測試
    - Integration test：模組內部含 DB 或 Redis 的互動測試

### 2. Containerize 階段

- **目的**：將通過測試的服務封裝為容器，準備進入部署流程
- **步驟**：
    - Build Image：依據各個 service 的 Dockerfile 建構映像檔
    - Push to GHCR：推送至 GitHub Container Registry 作為後續部署基底
- **對應資源**：
    - GitHub Workflow：`.github/workflows/service-build.yaml`
    - Image Path 範例：`ghcr.io/user/safezone-api:latest`

---

### CD: Continuous Deployment

### Phase 1: Compose 驗證（手動）

- **目的**：本地模擬部署環境進行快速整合驗證
- **方式**：使用 Docker Compose 啟動 SafeZone 所有核心模組
- **判定**：服務皆可正常啟動且無錯誤日誌
- **備註**：此階段目前保留為手動驗證以確保模組行為一致性
- **對應資源**：
    - Compose YAML：`compose/test/safezone-core.yaml`

### Phase 2: 本機驗證程序（手動）

- **目的**：透過 CLI 工具執行測試資料注入與輸出驗證
- **方式**：使用開發用 CLI Relay 工具與腳本測試整體 API 與儲存邏輯
- **對應資源**：
    - 測試腳本範例：`cli/tests/validate-core.py`
    - CLI 工具：`safezone-relay`

### Phase 3: ArgoCD 分段部署（自動）

- **目的**：將 SafeZone 各個模組按階段部署至 K3s cluster
- **方式**：每完成一個 ArgoCD Application，同步狀態正常後進入下一階段
- **範例階段**：`safezone-init` → `safezone-core` → `safezone-ui`
- **對應資源**：
    - ArgoCD App YAML：`k8s/argocd/applications/safezone-core.yaml`

### Phase 4: 線上驗證（手動）

- **目的**：確保部署後服務在實際運行環境中維持正確行為
- **方式**：重複 Phase 2 本機驗證程序，但針對 cluster 中已部署實例
- **對應 CLI 指令**：與 Phase 2 相同，但改為 `-env=prod`

---

> 💡 備註：本流程目前支援部分自動化流程；未來預計將 Phase 1~2 整合為可被 GitHub Actions 驅動之 pipeline，並支援對應狀態回報與 rollback。
>