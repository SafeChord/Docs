---
title: SafeZone CI Workflow (Build & Test)
doc_id: safechord.safezone.workflow.ci
version: 1.0.0
last_updated: "2025-12-25"
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
context_scope: "SafeZone App Repo"
summary: "定義 SafeZone 應用程式倉庫的開發與持續整合流程。涵蓋 Git 分支策略、Smoke Test 驗證機制以及 Docker Image 的建置與發佈標準。"
keywords:
  - CI
  - GitHub Actions
  - Smoke Test
  - GitFlow
  - Build Pipeline
logical_path: "SafeChord.SafeZone.Workflow.CI"
related_docs:
  - "safechord.safezone.deployment.workflow.md"
  - "safechord.environment.md"
parent_doc: "safechord.safezone"
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
1.  **動態版號生成**: 提取 Git SHA (前7碼) 作為臨時版本號 (e.g., `0.2.0-a1b2c3d`)。
2.  **建置映像檔 (Build)**:
    *   執行 `make build-all`。
    *   在 Runner 本地建置所有微服務的 Docker Image。
3.  **煙霧測試 (Smoke Test)**:
    *   執行 `make smoke-test`。
    *   這是一個 E2E 測試：它會使用 Docker Compose 啟動整個系統（包含 DB, Kafka 等），並模擬真實的使用者行為來驗證系統是否「冒煙」（崩潰）。
    *   *關鍵技術*: 使用 `wait_for_infra` 機制確保相依服務就緒後才開始測試。

> **注意**: CI 階段的 Image **不會** 推送到遠端 Registry (GHCR)，它們只存在於 Runner 的快取中，僅供測試使用。

---

## 3. 持續交付流程 (CD / Release)

當程式碼準備好發佈時，我們執行 Release 流程。定義檔位於 `.github/workflows/release.yml`。

### 觸發條件
*   推送到 `main` 分支的 Git Tag (格式: `v*.*.*`)。

### 執行步驟
1.  **驗證版號**: 從 Git Tag 提取正式版號 (e.g., `0.2.0`)。
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
