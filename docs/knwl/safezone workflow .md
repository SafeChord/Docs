# **SafeZone App 倉開發與發佈流程 v1.0**

## **第一章：Git 分支策略 (Git Branching Strategy)**

本倉庫遵循 GitFlow 的核心精神，使用以下分支來管理程式碼的生命週期：

* **main**: 代表生產環境的穩定程式碼。只接受來自 release/\* 或 hotfix/\* 分支的合併。所有在此分支上的 Commit 都應是可發佈的。  
* **dev**: 主要的開發整合分支。所有 feature/\* 分支完成後，都應合併於此。  
* **feature/\***: 用於開發新功能、進行重構或研究。分支名稱應清晰描述其目的 (e.g., feature/add-user-auth)。完成後發起 Pull Request (PR) 到 dev。  
* **release/v\*.\*.\***: 用於準備正式發佈。從 dev 切出，此分支**不再接受新的功能**，只進行發佈前的準備工作，例如：  
  * 更新 CHANGELOG.md  
  * 更新 README.md  
  * (未來) 修改程式碼內部的版本號  
* **hotfix/\***: 用於緊急修復 main 分支上的 bug。從 main 切出，完成後必須**同時**合併回 main 和 dev。

## **第二章：CI 流程 (持續整合 \- smoke-test.yml)**

此流程是程式碼品質的「守門員」，確保所有進入 dev 和 main 的程式碼都符合標準。

* **觸發條件**: 對 dev 或 main 分支發起 Pull Request。  
* **執行環境**: self-hosted runner。  
* **核心步驟**:  
  1. **設定動態版號**: 從 github.sha 提取短版 SHA (前7碼) 作為 VERSION 環境變數。  
  2. **建置映像檔**: 呼叫 make build-all 和 make build-tool-all，在 runner 本地建置所有帶有 SHA 標籤的 Docker image。  
  3. **執行測試**: 呼叫 make test-all 執行單元與整合測試，接著呼叫 make smoke-test 執行完整的端對端測試。  
* **最終產物**: 帶有 SHA 標籤的 Docker image，儲存於 self-hosted runner 的本地 cache 中，**此流程不會將任何 image 推送到遠端**。

## **第三章：CD 流程 (持續交付 \- release.yml)**

此流程是版本的「發行官」，負責將通過驗證的程式碼正式打包並發佈。

* **觸發條件**: 將 v\*.\*.\* 格式的 Git Tag 推送到 main 分支。  
* **執行環境**: self-hosted runner。  
* **核心步驟**:  
  1. **登入 GHCR**: 獲取推送到 GitHub Container Registry 的權限。  
  2. **設定發佈版號**: 從 Git Tag (GITHUB\_REF\_NAME) 提取正式的發佈版號 (e.g., 0.2.0)。  
  3. **重新建置映像檔**: 呼叫 make build-all 和 make build-tool-all，這次使用正式版號作為標籤，重新建置所有 image。  
  4. **推送映像檔**: 呼叫 make push-all，將所有帶有正式版號的 image 推送到 GHCR。