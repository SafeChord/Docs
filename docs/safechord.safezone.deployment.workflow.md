---
title: SafeZone Deployment Workflow (GitOps & Promotion)
doc_id: safechord.safezone.deployment.workflow
version: 1.0.0
last_updated: "2025-12-25"
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
context_scope: "SafeZone-Deploy Repo"
summary: "定義 SafeZone-Deploy 倉庫的 GitOps 工作流程。描述如何透過修改配置 (Configuration) 來觸發預覽環境 (Preview) 與生產環境 (Production/Staging) 的部署與晉升。"
keywords:
  - GitOps
  - ArgoCD
  - Helm
  - Environment Promotion
  - Deployment
logical_path: "SafeChord.SafeZone.Deployment.Workflow"
related_docs:
  - "safechord.safezone.workflow.ci.md"
  - "safechord.environment.md"
parent_doc: "safechord.safezone.deployment"
---

# SafeZone 部署與 GitOps 流程

本文件規範了 `SafeZone-Deploy` (Config Repository) 的運作邏輯。我們採用 **GitOps** 模式，這意味著「Git 倉庫的狀態即是叢集的狀態」。

我們混合了 **指令式協調 (GitHub Actions)** 與 **聲明式同步 (ArgoCD)** 來達成靈活且穩定的交付。

---

## 1. 核心職責劃分

*   **GitHub Actions (協調器)**:
    *   負責「瞬態」任務：跑測試、動態建立/銷毀 Preview 環境、發送通知。
    *   負責「晉升」操作：將經過驗證的 Config 合併到下一個環境分支。
*   **ArgoCD (執行者)**:
    *   負責「穩態」維護：監控 Git 變更，將 K8s Manifests 同步到叢集 (Sync)。
    *   負責「漂移偵測」：當叢集狀態與 Git 不一致時發出警告 (OutOfSync)。

---

## 2. 環境與分支對應 (Branching Model)

我們使用不同的 Git 分支來對應不同的運行環境。

| 分支名稱 | 對應環境 | 部署模式 | 同步策略 |
| :--- | :--- | :--- | :--- |
| **`deploy/*`** | **Preview (CI)** | Helm Install (CI 觸發) | **指令式**: 用完即丟 |
| **`staging`** | **Staging** | ArgoCD (GitOps) | **手動 Sync**: 人工閘門 |
| **`main`** | **Production** | ArgoCD (GitOps) | **自動/手動**: 黃金版本 |

---

## 3. 標準作業流程 (SOP)

### 場景 A: 版本整合與預覽 (CI Phase)
當開發者在 App 倉完成了 Image 建置後，運維流程開始：

1.  **建立整合分支**: 從 `dev` 切出 `deploy/v0.2.1`。
2.  **配置更新**: 修改 `values.yaml`，將 Image Tag 更新為新的版本。
3.  **啟動預覽環境**:
    *   發起 PR。GitHub Actions 會自動在 K8s 叢集中建立一個 **暫時性 Namespace** (`safezone-preview-pr-123`)。
    *   執行 `helm install` 部署全套應用。
4.  **驗證**: 執行 E2E 測試。
5.  **銷毀**: 測試通過或 PR 合併後，自動銷毀該 Namespace。

### 場景 B: 晉升至 Staging (Promotion)
經過驗證的配置，才有資格進入 Staging。

1.  **合併至 Staging**: 將 `deploy/v0.2.1` 的變更合併到 `staging` 分支。
2.  **ArgoCD 偵測**: ArgoCD 發現 `staging` 分支有變動，狀態變為 `OutOfSync`。
3.  **人工同步**: 運維人員在 ArgoCD UI 點擊 "Sync"，或透過 ChatOps 觸發。
    *   *為什麼不自動？* Staging 通常是穩定的測試環境，我們不希望它在測試進行中突然變更。

### 場景 C: 正式發佈 (Release)
1.  **浸潤測試**: 在 Staging 環境觀察一段時間。
2.  **建立 Release**: 從 `staging` 合併到 `main`，並打上 Git Tag。
3.  **生產同步**: ArgoCD 將 `main` 分支的狀態同步至 Production Cluster。

---

## 4. 緊急修復 (Hotfix Strategy)

如果生產環境出現嚴重 Bug：
1.  從 `main` 切出 `hotfix/xxx` 分支。
2.  修正配置（例如 rollback image tag 或調整資源限額）。
3.  緊急合併回 `main` 進行部署。
4.  **重要**: 必須同時將此修復 Cherry-pick 回 `staging` 和 `dev`，防止 Bug 在下個版本回歸 (Regression)。
