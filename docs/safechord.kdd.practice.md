---
title: KDD Practice & AI Agent Collaboration Guide
doc_id: safechord.kdd.practice
version: 0.2.0
last_updated: "2025-12-25"
status: active
authors:
  - bradyhau
  - Gemini 3 Pro (CLI)
context_scope: "Methodology"
summary: "定義 SafeChord 專案當前與 AI Agent 協作的實作模式。基於 Architect-Builder-Coder 三位一體模型，規範文檔驅動開發的具體流程與 Repo 邊界管理。"
keywords:
  - AI Agents
  - Collaboration
  - KDD
  - Multi-Agent Workflow
logical_path: "SafeChord.KDD.Practice"
related_docs:
  - "safechord.kdd.introduction.md"
  - "safechord.knowledgetree.md"
  - "safechord.environment.md"
parent_doc: "safechord.kdd.introduction"
---

# KDD 實作現狀：AI Agent 協作守則

在 SafeChord 的開發流程中，AI 不再只是「輔助工具」，而是系統架構的「共同維護者」。我們採用三位一體的身分模型來進行協作。

---

## 1. AI 協作管道 (Collaborative Pipeline)

我們將 AI Agent 劃分為三個角色，每個角色有其明確的職責與 Context 邊界：

| 角色 | 實體工具 | 核心職責 | 關注點 |
| :--- | :--- | :--- | :--- |
| **1. Architect** | Gemini WebChat | **決策與設計**：定義技術堆疊、設計架構、分析權衡 (Trade-offs)。 | 戰略 (Why/How) |
| **2. Builder** | **Gemini CLI (我)** | **協調與文檔**：建立檔案結構 (Scaffolding)、管理知識庫 (KDD)、執行 Review。 | 結構 (Structure) |
| **3. Coder** | Cline + DeepSeek | **實作與語法**：撰寫具體程式碼、填充模板、將 Spec 轉化為邏輯。 | 速度 (Syntax) |

### 協作流程 (Flow)
1. **Architect** 提出架構變更建議 -> 2. **Builder (CLI)** 根據建議更新 `Docs/` -> 3. **Coder (Cline)** 讀取文檔並完成代碼。

---

## 2. 基於 Repo 的權責管理 (Repo Strategy)

協作者在執行任務時，必須遵守 Repo 的分層原則 (Separation of Concerns)：

### 🟢 Application Layer (`SafeZone`)
*   **Agent 準則**: 專注於業務邏輯。不要在代碼中寫死 K8s 的 Service DNS，應依賴環境變數。
*   **KDD 產物**: `CHANGELOG.md`, `test_*.py`, 微服務 Spec。

### 🟡 Delivery Layer (`SafeZone-Deploy`)
*   **Agent 準則**: 專注於配置 (Config)。定義環境差異 (Values override)，建立與環境對齊的 `SealedSecrets`。
*   **KDD 產物**: Helm Charts, Workflow 定義, 環境策略。

### 🔴 Infrastructure Layer (`Chorde`)
*   **Agent 準則**: 專注於平台穩定。管理 GitOps Base，確保 Kafka/Postgres 叢集版本的一致性。
*   **KDD 產物**: `k3han` 叢集定義, IaC 腳本。

---

## 3. 當前 KDD 操作 SOP (Step-by-Step)

當你需要進行一項新功能開發時，Agent 應採取以下步驟：

1.  **Context 載入**: 讀取 `safechord.knowledgetree.md` 定位相關文檔。
2.  **知識對齊**: 詢問人類：「根據當前設計，我應該先更新哪一份 Spec 文件？」
3.  **文檔先行**:
    *   Builder (CLI) 更新 `safechord.safezone.service.xxx.md`。
    *   定義 `TestCase` 列表。
4.  **代碼轉化**: Coder (Cline) 讀取 Spec，開始實作邏輯。
5.  **閉環更新**: 任務完成後，Builder (CLI) 檢查 `CHANGELOG.md` 與 `Docs/` 是否同步。

---

## 4. 關鍵原則

*   **無文檔不開工**: 嚴禁在未更新知識庫的情況下直接修改核心邏輯。
*   **信任文檔**: 如果程式碼與文檔發生衝突，預設文檔是正確的，除非 Architect (WebChat) 重新下達決策。
*   **保持扁平**: 正式文件統一存放在 `Docs/docs/` 下，以便 Agent 快速讀取。
