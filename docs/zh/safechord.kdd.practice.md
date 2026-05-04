# KDD 2.0 實務：三引擎與無頭開發模式

2026 年，SafeChord 開發採用 **「三引擎」** 模型：以 Gemini WebChat 處理高層級策略決策，並搭配雙軌 CLI 代理程式進行無頭開發與知識鞏固。

---

## 1. 三引擎模型

根據 AI 模型特性與上下文邊界，任務分為三個層級：

| 角色 | 實體 | 核心職責 | 焦點 |
| :--- | :--- | :--- | :--- |
| **🏛️ 架構師** | **Gemini WebChat** | **設計與取捨**：定義技術堆疊、架構決策與長期分析。 | 策略（Why/How） |
| **🛡️ 開拓者** | **Claude Code** | **實作與問題解決**：負責程式碼實作、技術 Spike 與複雜除錯。 | 戰術（Spike 與程式碼） |
| **🧠 維護者** | **Gemini CLI** | **審查與鞏固**：規劃測試、執行程式碼審查、維護 KDD 文件。 | 執行（結構） |

> **💡 代理角色更新**
> - **CLI 作為策略助手**：由於 WebChat 無法直接存取本地程式碼庫，維護者 CLI 代理程式透過其規劃模式為架構師整理上下文。
> - **任務分割**：主要功能開發由 **Claude Code（開拓者）** 負責，而 **維護者 CLI** 則專注於架構治理與文件對齊。

---

## 2. 溝通介面與協定

在無頭環境中，標準化的協定對於代理之間資訊交換至關重要。

### 🟢 基本溝通：Git Commit 協定
對於無需正式交接的例行迭代，**Git Commit 訊息** 是代理與人類之間的橋樑。
*   **原則**: 訊息必須包含「意圖」與「架構影響」。
*   **格式**: 嚴格遵循 [Conventional Commits](https://www.conventionalcommits.org/)。
*   **代理義務**: 維護者在進行程式碼審查前，必須先解讀開拓者的 commit 歷史以了解實作脈絡。

### 🔴 交接協定（Legacy 筆記）
當任務達到里程碑、遭遇死結，或需要深度技術轉移時，觸發交接協定。
*   **媒介**: 存放在 `.ai-session-handoffs/` 的 Markdown 檔案。
*   **觸發條件**:
    - 開拓者完成一個 Spike 或開發階段。
    - 維護者遇到其操作範圍外的錯誤。
    - 人類介入要求任務移交。
*   **必要內容**:
    1.  **狀態/摘要**: 日期、方向（From/To）、分支狀態與進度。
    2.  **變更內容**: 檔案路徑與核心結構變更。
    3.  **驗證路徑**: 哪些方法已證明可行？（對死結交接尤為重要）
    4.  **後續行動**: 對下一個代理的明確指示與驗證標準。

### ⚪ 設計草稿
對於策略性決策或複雜重構，**設計草稿** 作為開拓者的藍圖。
*   **媒介**: 存放在 `.ai-session-drafts/` 的 Markdown 檔案。
*   **必要內容**: 背景、建議方案、藍圖（模擬程式碼/綱要）、取捨與後續步驟。

---

## 3. 雙軌工作流程：KDD 的平衡

SafeChord 採用基於標籤的 **雙軌工作流程**，以平衡「文件優先」的嚴謹性與「Spike 優先」的靈活性。

### 🟢 路徑 A：`kdd:forward`（有序模式）
應用於現有模組的最佳化與已知架構的延伸。
**規則**: 「先文件後程式碼」——沒有更新後的藍圖，不得進行實作。

1.  **策略設計**: 架構師定義「Why/What」；維護者更新 Markdown 知識地圖（藍圖/ADR）。
2.  **實作**: 開拓者嚴格在定義的邊界內實作程式碼與測試。
3.  **完成**: 開拓者提交 PR 並產生 Legacy 筆記。
4.  **鞏固**: 維護者根據預先定義的文件進行程式碼審查，合併並標記版本。

### 🔴 路徑 B：`kdd:spike`（前線模式）
應用於新技術整合、未知錯誤修正或效能壓力測試。
**規則**: 「先程式碼後文件」——原型開發優先於文件。

1.  **策略設計**: 架構師討論可行性；若需要程式碼庫狀態，維護者建立設計草稿。
2.  **Spike**: 開拓者在沒有文件限制下實作 Demo/Spike。
3.  **完成**: 開拓者提交 PR 並產生詳細的 Legacy 筆記。
4.  **鞏固**: **關鍵階段。** 維護者執行 PR 審查並進行**文件對齊**，將 Spike 結果逆向工程回 `Docs/` 中的單一事實來源（SSOT）。

---

## 4. 無頭協作規則

*   **終端機作為 SSOT**：所有開發與測試都在 CLI 中完成。IDE 僅供視覺審查使用。
*   **審查即文件**：維護者的審查核准隱含表示文件對齊已同步。
*   **上下文效率**：代理需善用其龐大的上下文視窗進行跨服務影響分析，以防止 API 合約中斷。

---

## 5. 操作範本（附錄）

### 🟢 Git Commit 範本
```text
<type>(<scope>): <subject> (最多50字)

[Body: 為何需要這項變更？]
說明動機與邏輯。專注於「Why」而非「How」。
描述對專案架構或長期決策的影響。

Context: [連結至藍圖或 Issue ID]
Impact: [對 API 合約或基礎設施的具體影響]
Test: [執行的驗證方式] (例如：make test-data-ingestor)
Agent: [Gemini CLI / Claude Code]
Legacy: [留待下一個代理處理的待辦事項]
```

### 🔴 交接範本（Legacy 筆記）
```markdown
# 📝 Legacy Note: [Task Name]

> **Date**: YYYY-MM-DD
> **From**: [Agent Name]
> **To**: [Agent Name]
> **Branch**: [Branch Name]
> **Action Required**: [Brief summary]

---

## Status / Summary
[Complete / Partially Complete / Deadlock]

## What Changed
[Structural changes or architectural adjustments]

## Verified Path (Optional)
- [x] What has been proven feasible?
- [ ] Known dead ends or blockers?

## Next Actions
1. [Specific Instruction 1]
2. [Specific Instruction 2]
```