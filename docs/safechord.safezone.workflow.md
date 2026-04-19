---
title: 'Script: SafeZone CI/CD Workflow'
doc_id: safechord.safezone.workflow.ci
last_updated: '2026-04-15'
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
context_scope: SafeZone App Repo
summary: 定義 SafeZone 應用程式的 CI/CD 劇本。包含 GitFlow 分支策略、Smoke Test 品質閘門以及 Docker Artifacts
  的建置與發佈流程。
keywords:
  - CI
  - GitHub Actions
  - Smoke Test
  - GitFlow
  - Build Pipeline
  - Container-Native
logical_path: SafeChord.SafeZone.Workflow.CI
related_docs:
  - safechord.safezone.deployment.workflow.md
  - safechord.environment.md
parent_doc: safechord.safezone
archetype: script
code_paths:
  - SafeZone/.github/workflows
doc_version: 0.3.0
app_version: 0.3.0
---

# SafeZone 開發與 CI 流程

本文件規範了 `SafeZone` (App Repository) 的程式碼生命週期。我們的目標是確保每一行進入 `main` 的程式碼都是經過完整測試且可被部署的。

---

## 1. Git 分支策略 (Branching Strategy)

我們遵循標準的 GitFlow 模型，但為了適應 CI/CD 自動化，做了以下定義：

| 分支名稱 | 角色 | 保護規則 | 觸發行為 |
| :--- | :--- | :--- | :--- |
| **`main`** | **生產主幹 (Production)** | 🔒 僅接受 PR 合併 | 發佈正式版號 (Release) |
| **`dev`** | **開發主幹 (Development)** | 🔒 僅接受 PR 合併 | 觸發 Smoke Test |
| **`feature/*`** | 功能開發 | 開放 | Local Test |
| **`release/*`** | 發佈準備 | 開放 | 凍結功能，僅修 Bug |
| **`hotfix/*`** | 緊急修復 | 開放 | 優先合併回 main/dev |

> **開發者守則**:
> *   所有新功能必須從 `dev` 切出 `feature/xxx` 分支。
> *   完成後發起 PR (Pull Request) 回 `dev`，此時會觸發 CI 驗證。

---

## 2. 持續整合流程 (CI Pipeline)

CI 是品質的守門員。我們使用 GitHub Actions 來執行此流程，定義檔位於 `.github/workflows/smoke-test.yml`。

### 觸發條件
*   對 `dev` 或 `main` 分支發起 Pull Request。
*   直接推送到 `dev` (雖然不建議，但允許)。

### 核心步驟 (The Gauntlet)
1.  **動態版號生成**: 提取 Git SHA (前7碼) 作為臨時版本號 (e.g., `0.3.0-a1b2c3d`)。
2.  **建置映像檔 (Build)**:
    *   執行 `make build-all` 與 `make build-tool-cli`。
    *   在 Runner 本地建置所有微服務以及 **Ops 測試映像檔** (`safezone-cli-ops`)。
3. **煙霧測試 (Smoke Test)**:
    *   執行 `make smoke-test`。
    *   **架構**: 採用 **Container-Native** 模式。
        *   測試引擎 (`smoke_test.py`) 運行於 `safezone-cli-ops` 容器中。
        *   **有狀態測試流 (Stateful Test Flows)**: 測試案例由 CSV 定義，支援具備邏輯順序依賴的測試步驟，確保驗證點符合業務場景（如：先模擬再驗證快取命中）。
        *   **非同步事件驗證 (Async Verification)**: 針對系統的非同步特性（Kafka 延遲、資料落盤），引擎內建「自適應輪詢與重試機制」，自動處理資料的最終一致性驗證，而非單純的靜態等待。
        *   引擎直接加入 Docker Compose 內部網路，與微服務通訊，模擬真實環境。
    *   *驗證點*: 包含資料模擬觸發、端到端落盤驗證、快取生命週期 (Cache Hit/Miss) 檢查以及資料庫自動化清理。


> **注意**: CI 階段的 Image **不會** 推送到遠端 Registry (GHCR)，它們只存在於 Runner 的快取中，僅供測試使用。

---

## 3. 持續交付流程 (CD / Release)

當程式碼準備好發佈時，我們執行 Release 流程。定義檔位於 `.github/workflows/release.yml`。

### 觸發條件
*   推送到 `main` 分支的 Git Tag (格式: `v*.*.*`)。

### 執行步驟
1.  **驗證版號**: 從 Git Tag 提取正式版號 (e.g., `0.3.0`)。
2.  **正式建置**: 使用正式版號重新執行 `make build-all`。
3.  **發佈映像檔**:
    *   執行 `make push-all`。
    *   將帶有正式版號的 Image 推送到 **GitHub Container Registry (GHCR)**。
    *   這些 Image 將被 `SafeZone-Deploy` 倉庫引用，用於後續的部署。

---

## 4. 本地開發與測試 (Local Dev)

在提交 PR 之前，開發者應在本地驗證邏輯。

*   **單元測試**: `make test-all` (執行 Python/Go 的 Unit Tests)。
*   **本地整合**: `make dev-up` (啟動 Docker Compose 環境)。
    *   請參考 [環境演進論](safechord.environment.md) 了解如何使用 Profiles (infra/core) 來加速開發。
