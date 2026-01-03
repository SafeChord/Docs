---
title: SafeZone Deployment Workflow (GitOps & Promotion)
doc_id: safechord.safezone.deployment.workflow
version: 0.2.1
last_updated: "2026-01-03"
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
context_scope: "SafeZone-Deploy Repo"
summary: "定義 SafeZone-Deploy 倉庫的 GitOps 工作流程。描述如何透過指令式編排與聲明式同步，達成從 Preview 到 Staging 的版本晉升與發布歸檔。"
keywords:
  - GitOps
  - ArgoCD
  - GitHub Actions
  - Environment Promotion
  - Deployment
logical_path: "SafeChord.SafeZone.Deployment.Workflow"
related_docs:
  - "safechord.safezone.deployment.charts.md"
  - "safechord.environment.md"
parent_doc: "safechord.safezone.deployment"
---

# SafeZone 部署與 GitOps 流程

本文件規範了 `SafeZone-Deploy` (Config Repository) 的運作邏輯。我們採用 **GitOps** 模式，這代表「Git 倉庫的狀態即是叢集的期望狀態」。

為了克服純 GitOps 在複雜依賴部署上的限制，我們採用混合策略：使用 **GitHub Actions** 作為「指令式協調器 (Orchestrator)」，負責跨 Application 的編排任務；使用 **ArgoCD** 作為「聲明式執行者 (Executor)」，維護環境穩態。

---

## 1. 核心職責劃分

*   **GitHub Actions (協調器)**:
    *   負責「瞬態」與「編排」任務：如動態建立與銷毀 Preview 環境。
    *   **解決同步相依性**：由 Action Workflow 直接控制各階段的安裝順序 (Infra -> Init -> Core)，Bash Script 僅作為底層執行輔助，確保依賴鏈完整。
    *   負責「晉升」操作：協調配置合併與跨環境的同步觸發。
*   **ArgoCD (執行者)**:
    *   負責「穩態」維護：監控 Git 變更，將 K8s Manifests 持續同步到叢集。
    *   負責「漂移偵測」：當叢集狀態與 Git 期望不一致時發出警告 (OutOfSync)。

---

## 2. 環境與分支對應 (Branching Model)

| 分支名稱 | 對應環境 | 部署模式 | 同步策略 |
| :--- | :--- | :--- | :--- |
| **`deploy/*`** | **Preview (CI)** | Helm Install (CI 直接觸發) | **指令式**: 長期存在的整合環境 (`safezone-preview`) |
| **`staging`** | **Staging** | ArgoCD (GitOps) | **人工驅動**: 透過 Action 觸發環境同步 |
| **`main`** | **Production (Archive)** | N/A (僅作歸檔) | **無**: 作為黃金版本 (Golden Archive) 儲存庫 |

> **注意**：根據 MVA (Minimum Viable Architecture) 策略，目前不設獨立 Production Cluster。`main` 分支僅作為經過浸潤測試後的穩定版本記錄。

---

## 3. 標準作業流程 (SOP)

### 場景 A: 版本變更與整合 (Version Integration)
此流程為所有配置變更的**統一入口**。無論是架構調整、參數調優或映像檔更新，皆遵循此流程。

1.  **建立整合分支**: 從 `dev` 切出 `deploy/v0.2.x`。
2.  **配置變更**: 執行 Helm Chart 修改、`values-preview.yaml` 調整。
3.  **預覽環境更新**:
    *   發起 PR 到 `deploy/v0.2.x`。
    *   GitHub Actions 自動更新長期存在的 **`safezone-preview`** 環境。
    *   供開發者進行端對端驗證與數據流測試。

### 場景 B: 晉升至 Staging (Promotion)
當配置在預覽環境驗證通過後：

1.  **E2E 驗收**: 合併至 `dev` 分支，觸發完整的驗收測試。
2.  **資源回收**: 測試通過後，自動銷毀 `safezone-preview` 環境 (回收資源) 並關閉 deploy 分支。
3.  **推送到 Staging**: 將 `dev` 變更合併至 `staging` 分支。
4.  **人工觸發同步**: 運維人員手動執行 GitHub Action。該 Action 會根據環境差異 (使用 `values-staging.yaml`) 重新在 `safezone` (Staging) 環境執行與 Preview 相同的編排邏輯。
    *   *為什麼不自動？* Staging 是穩定的測試環境，需人工確認同步時機以避免干擾現有測試。

### 場景 C: 正式發佈與歸檔 (Release & Archive)
1.  **浸潤測試 (Soak Test)**: 在 Staging 環境運行一段時間，觀察 Long-term 指標。
2.  **版本固化**: 確認無誤後，將穩定版本合併至 `main` 並建立 Git Tag (如 `v0.2.2`)。
3.  **開發主幹同步**: 合併回 `dev` 分支，確保下一個週期的開發起點已包含最新的版本記錄與文件更新。

---

## 4. 緊急修復 (Hotfix Strategy)

1.  從 `staging` 切出 `hotfix/staging-xxx` 分支進行修復。
2.  合併回 `staging` 並觸發 Action 重建 Staging 環境驗證。
3.  **Backport**: 驗證後必須立即將修復 Cherry-pick 回 `dev`，確保 Bug 不會在下一個 `deploy` 週期再次出現。