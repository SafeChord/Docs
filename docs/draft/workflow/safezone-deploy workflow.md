### **SafeZone Deploy 倉庫 Git 工作流程 **

#### **核心理念：基於持續整合的專業交付流程**

本文件定義了 `safezone-deploy` GitOps 倉庫的標準作業程序 (SOP)。此流程基於 GitFlow 模型，並融合了「指令式協調 (Orchestration)」與「聲明式狀態管理 (State Management)」的混合模式，旨在為不同發布場景提供兼具效率與安全性的解決方案。

我們的核心是**持續整合 (Continuous Integration)**，確保 `dev` 主幹分支始終處於健康、可測試的狀態。我們追求的是穩健的**「持續交付 (Continuous Delivery)」**，為此在關鍵部署步驟保留了必要的人工決策閘門。

---

#### **1. 核心工具職責劃分**

* **GitHub Actions**: 扮演 **「指令式流程協調器」**。負責處理複雜的、有順序性、或一次性的任務，例如在 PR 階段動態創建與銷毀預覽環境、執行 E2E 測試，以及在接收到人工指令後，觸發對 `staging` 環境的部署。
* **ArgoCD**: 扮演 **「聲明式狀態維護官」**。其唯一職責是監控環境分支 (`staging`, `prod`)，報告 Git 中定義的期望狀態與叢集內的實際狀態之間的差異 (`OutOfSync`)，並在接收到 Action 的明確指令後，執行 `sync` 操作。

---

#### **2. 分支模型**

* **`main`**:
    * **角色**: **黃金版歸檔 (Golden Archive)**。此分支的每一個 Tag 都代表一個經過完整 QA、可交付的正式版本。
    * **規則**: 只接受來自 `release/*` 或 `hotfix/*` 分支的合併。

* **`dev`**:
    * **角色**: **開發整合主幹 (Integration Trunk)**。所有預環境分支（`patch/*`, `deploy/*`）的開發起點與終點。
    * **規則**: 所有預環境分支都從 `dev` 分支出，並透過 PR 合併回 `dev`。PR 合併前必須通過對應的自動化檢查。

* **`staging`**:
    * **角色**: **Staging 環境狀態分支**。此分支的內容 100% 反映了 Staging 環境的**期望狀態**。
    * **規則**:
        * 只接受來自 `dev` 或 `hotfix/staging-*` 分支的合併。
        * **ArgoCD 會監控此分支，但已關閉自動同步 (Auto-Sync)。**

* **`hotfix/staging-*` (Staging 緊急修復)**:
    * **角色**: 用於修復 Staging 環境上**阻礙所有測試**的**緊急 Bug**。這是一個**例外流程**。
    * **流程**: 從 `staging` 分支出，修復後合併回 `staging`，**並且必須立即將同一個修復反向合併（Merge Back）回 `dev` 分支**，以防 Bug 在下個版本中回歸。

* **`deploy/*` (版本整合分支)**:
    * **角色**: 用於整合像 `v0.2.1` 這樣包含多個 `feat` 的大型版本。這是一個相對長期的分支。
    * **流程**: 從 `dev` 分支出。所有與該版本相關的 `feat/*` 都將合併於此。

---

#### **3. 標準作業流程 (SOP)**

##### **場景 A：版本整合開發 (使用 `deploy` 分支)**

1.  **建立整合分支與環境**:
    * 從 `dev` 分支出 `deploy/v0.2.1`。
    * CI/CD 系統會自動（或由你手動觸發）在 Kubernetes 中建立一個唯一的、長期存在的整合環境，Namespace 為 `safezone-preview`。此環境會部署一套完整的輕量級平台工具（DB, Redis, Kafka）。

2.  **分階段開發 (`feat/*`)**:
    * 所有 `v0.2.1` 的工作，都會被拆解成一個個的 `feat/*` 分支（`feat/infra-0.2.1`, `feat/core-0.2.1` 等），並且都從 `deploy/v0.2.1` 分支出來。

3.  **PR 到整合分支並持續部署**:
    * 當 `feat/infra-0.2.1` 完成後，發起 PR 到 `deploy/v0.2.1`。
    * PR 的 CI workflow 只執行**輕量級靜態檢查** (`helm lint`, `helm template`)。
    * PR 合併後，CI/CD 會**自動**將 `infra` 層的變更，透過 `helm upgrade --install` **直接部署**到 `safezone-preview` 環境中。
    * 後續的 `feat/core-0.2.1` 等分支重複此流程，逐步將整個應用程式堆疊建構在 `safezone-preview` 環境裡。

##### **場景 B：最終驗證與晉升 (Promote)**

1.  **完整 E2E 測試**:
    * 當 `deploy/v0.2.1` 分支的所有 `feat` 都整合完畢後，從 `deploy/v0.2.1` 發起一個 PR 到 `dev`。
    * 這個 PR 會觸發一個**重量級的 CI workflow**，該 workflow 會對**已經建構完成**的 `safezone-preview` 環境，執行一次完整的 E2E 測試。

2.  **合併與清理**:
    * E2E 測試通過後，`deploy/v0.2.1` 的 PR 被允許合併到 `dev`。
    * 合併後，可以手動或自動觸發一個清理流程，銷毀 `safezone-preview` 環境並刪除 `deploy/v0.2.1` 分支。

3.  **部署到 Staging**:
    * 從 `dev` 發起 PR 到 `staging`。
    * 合併後，由於 ArgoCD 關閉了自動同步，你需要手動觸發一個 Action (或在 ArgoCD UI 上點擊 Sync)，將這個**已經被完整驗證過**的版本，部署到長期存在的 `safezone` (Staging) 環境進行人工 QA。

##### **場景 C：日常補丁 (`patch`)**

* `patch` 分支的流程與 `deploy` 類似，但生命週期更短。它可以選擇使用同一個 `safezone-preview` 環境（需要鎖定機制），或者（在資源允許的情況下）創建自己的臨時預覽環境。所有 `patch` 的 PR 也必須通過完整的 E2E 測試才能合併。

---
##### **場景 D：正式版本發布 (從 Staging 到 Main)**

1.  **QA 與浸潤測試**: 在 Staging 環境上，對 `staging` 分支的最新版本進行完整的人工 QA、壓力測試、或任何必要的浸潤測試 (Soak Test)。
2.  **建立發布分支**: 當 Staging 版本被確認品質合格後，從 `staging` 分支出 `release/<version>` (例如 `release/v0.2.1`)。
3.  **定版 (Finalize)**: 在 `release/*` 分支上，可進行最後的版本號修改、更新 `CHANGELOG.md` 等發布前的準備工作。
4.  **完成發布**:
    * 將 `release/*` 分支分別發起 PR 合併回 `main` 和 `dev` (確保 `dev` 也包含最新的版本資訊)。
    * 在 `main` 分支的合併 commit 上打上對應的 Git Tag (例如 `v0.2.1`)。
