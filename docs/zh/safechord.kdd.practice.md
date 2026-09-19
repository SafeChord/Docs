# KDD 2.0 實務：雙引擎開發模式

SafeChord 的開發跑在 **「雙引擎」** 模型上：開拓者席負責實作，維護者席負責審查與鞏固。

> **⚙️ 本文件正在調整期。** 雙引擎席位、票的生命週期、以及 §4 的範本都是 v0.4.0 才引入的，還沒跑完一個完整週期，會有粗糙的地方。
>
> **如果某個範本或步驟不合眼前的工作，請提出來，不要默默繞過去。** 文件與實際發生的事對不上，在被論證為其他情況之前都算文件的缺陷——跟人類提，然後在這裡修掉。
>
> **本告示還在的期間，不要遞增 `doc_version`。** 文件停在 v0.4.0 直到調整期結束，改動只反映在 `last_updated`。

---

## 1. 雙引擎模型

| 角色 | 能力要求 | 當前載體 | 核心職責 |
| :--- | :--- | :--- | :--- |
| **🛡️ 開拓者** | 實作產出量；錯誤由測試攔截 | Antigravity CLI · **Gemini Flash / high effort** | **實作與問題解決**：程式碼、Spike、複雜除錯。 |
| **🧠 維護者** | Repo 理解力與長流程專注度；沒有別的東西會攔下它的錯 | Claude Code · **Opus / high effort** | **`Docs/` 的持有者**，兩個方向都管。開票之前：撰寫藍圖或設計草稿，然後開票並上標籤。開票之後：程式碼審查、測試規劃、文件對齊，以及推動[發版流程](safechord.safezone.delivery.workflow.md)。 |

**能力要求是契約，當前載體是實作細節。** 換掉載體，不要動席位。

**開拓者偏向獨立開發，維護者偏向與人類協作。** 開拓者通常自己把一張票做完；維護者遇到不明確該由自己決定的事，就交給人類。

**`Docs/` 屬於維護者。** 開拓者在那裡是唯讀。實作過程中發現的偏離，先把程式碼做完，再交接出去做文件對齊。

**席位綁定在 session 上。** 一個 session 持一個席位，持到結束。換席位就是換 session，用交接把 context 帶過去。因此程式碼審查不會跟它所審查的實作共用 session——寫程式碼的那個 session 持開拓者，而審查是維護者的事。

---

## 2. 溝通介面與協定

標準化的協定負責在代理之間、以及跨 session 傳遞資訊。

### 🎫 票（Ticket）
票是任何實作的開頭 是後續追蹤時做起點的依據
*   **媒介**: 工作所在 repository 的 GitHub issue。
*   **目的**: 作為實作依據, 補的是 commit（太細）與專案文件（只有終態）都漏掉的那層粒度。
*   **份量**: 票幾乎是永久的，所以只放對日後讀者有追溯價值的內容：問題、決策與理由、範圍、Done When。只為這次任務對齊席位用的 context（推測的機制、調查細節、設計建議、未驗證項目、實作順序）放進 handoff。
*   **必要內容**: [參考範本](#-github-issue-範本)

### 🟢 基本溝通：Git Commit 協定
*   **媒介**: git
*   **目的**: 在實作過程中的細粒資訊載體。
*   **格式**: 嚴格遵循 [Conventional Commits](https://www.conventionalcommits.org/)。
*   **必要內容**: [參考範本](#-git-commit-範本)

### 🔴 交接協定
*   **媒介**: 存放在 `.ai-session-handoffs/` 的 Markdown 檔案。
*   **目的**: 跨 ai 工具 session 的載體。交接對象包含下一個 session，或另一個代理。
*   **觸發條件舉例**:
    - 開拓者完成一個 Spike 或開發階段。
    - 代理遇到其操作範圍外的錯誤。
    - 人類介入要求任務移交(通常是 Context 已經長到開始劣化)。
*   **兩個方向都適用**: GitHub 放摘要，handoff 放詳情。
    - 維護者 → 開拓者（開工）：票；維護者判斷光靠票 context 不夠時，另寫 handoff。
    - 開拓者 → 維護者：PR description，每次都另寫 handoff。
    - 維護者 → 開拓者（審查）：PR review comment。只有在開拓者 session 叫不回來、必須開新 session 從頭接手時，才另寫 handoff。
*   **生命週期**: handoff 跟著任務走。PR merge、票關閉、reconciliation 落進 `Docs/` 之後就刪除；harness 的 git history 會留著，需要時可以找回。
*   **連結方向**: handoff 指向票，票不反指。看得到 handoff 的人一定找得到票，看得到票的人卻不一定看得到 handoff；而且 handoff 刪除後，永久的票上會留下一條死連結。有對應的票時，檔名帶上小寫的 `<repo>-<issue_no>`（例如 `2026-09-19-safezone-64-worker-offset-commit.md`），從票這端用 `ls .ai-session-handoffs | grep safezone-64-` 就能找到。
*   **叫回 session**: 因里程碑、卡關或人類移交而交接的 session，可以用筆記裡的 `Resume:` 指令叫回來，例如修正審查發現的問題。因 Context 劣化而交接的 session 就此退休，不再叫回。
*   **必要內容**: [參考範本](#-handoff-範本)

### ⚪ 設計草稿
*   **媒介**: 存放在 `.ai-session-drafts/` 的 Markdown 檔案。
*   **目的**: 在任何不直接影響 codebase 的前瞻討論須要有延續時，通常出現在開票之前。
*   **必要內容**: [參考範本](#-draft-範本)

---

## 3. 雙軌工作流程：KDD 的平衡

SafeChord 採用基於標籤的 **雙軌工作流程**，以平衡「文件優先」的嚴謹性與「Spike 優先」的靈活性。

### 3.1 選擇路徑

兩條路徑**不是**用「動工前規劃了多少」來分的。分界只有一個問題，而且開票當下就答得出來：

> **`Docs/` 裡已經有這塊的藍圖了嗎？**

這個答案決定了文件對齊**是什麼**——一次查核，還是一次著作。

| 路徑 | 動工前有藍圖 | 文件對齊是 |
| :--- | :--- | :--- |
| `kdd:forward` | 有 | **查核**——確認程式符合規格；有偏差則修規格 |
| `kdd:spike` | 沒有 | **著作**——把結果寫回成一個新的 SSOT 節點 |

標籤告訴開拓者該往哪看：`kdd:forward` → 先讀藍圖，照著實作；`kdd:spike` → 別去 `Docs/` 翻，翻了也是空的。

票由維護者開立並貼標籤，人類視需要調整。

### 🟢 路徑 A：`kdd:forward`（有序模式）
應用於現有模組的最佳化與已知架構的延伸。
**規則**: 「先文件後程式碼」——沒有更新後的藍圖，不得進行實作。

1.  **策略設計**: 人類定義「Why/What」；維護者更新 Markdown 知識地圖（藍圖/ADR），並寫好守住藍圖「TDD 收斂邊界」（列出測試必須守住之約束的段落）的測試，接著**開票並標記 `kdd:forward`**。
2.  **實作**: 開拓者先讀藍圖，實作能通過這些測試的程式碼，視需要補上自己的測試，並嚴格在定義的邊界內進行。
3.  **完成**: 開拓者提交 PR 並產生 Legacy 筆記。
4.  **鞏固**: 維護者根據預先定義的文件進行程式碼審查並合併。**文件對齊在此是一次查核；程式有偏差就修藍圖，然後關票。**

### 🔴 路徑 B：`kdd:spike`（前線模式）
應用於新技術整合、未知錯誤修正或效能壓力測試。
**規則**: 「先程式碼後文件」——原型開發優先於文件。

1.  **策略設計**: 人類討論可行性；若需要程式碼庫狀態，維護者建立設計草稿，接著**開票並標記 `kdd:spike`**。
2.  **Spike**: 開拓者在沒有藍圖需要遵守的情況下實作 Demo/Spike，所有測試也由開拓者撰寫。
3.  **完成**: 開拓者提交 PR 並產生詳細的 Legacy 筆記。
4.  **鞏固**: **關鍵階段。** 維護者執行 PR 審查並進行**文件對齊**，將 Spike 結果逆向工程回 `Docs/` 中的單一事實來源（SSOT）。值得保留的約束寫進新文件的 TDD 收斂邊界；已經在守這些約束的 Spike 測試原樣保留。**把票結算成新的專案文件並關票。**

### 3.2 處理審查發現的問題

審查時，測試的 diff 與程式的 diff 分開讀。為了讓測試通過而修改測試，是第一個要追問的地方。

**發現的問題以 PR review comment 退回開拓者修**（見[交接協定](#-交接協定)）。開拓者在 PR branch 上修正，修正需要的測試一併處理，維護者再審一次後合併。

**有些問題在這張票裡改不動。** 開拓者不修改也不開立票：它在目前的票上留 comment，寫明發現了什麼、為什麼，然後繼續做其他部分。票的處理由維護者負責：

| 發現的問題 | 維護者 |
| :--- | :--- |
| 修正需要放寬藍圖 TDD 收斂邊界裡的約束，或放寬守住該約束的測試 | 動手修正前先交給人類決定 |
| 藍圖本身有誤 | 為藍圖開新票 |
| 是一個還沒做的決定，或超出本票範圍的工作 | 開新票並連結，PR 不含這部分照常合併 |

**例外：不影響行為的修正。** 如果修正只動到註解或文件，不可能改變程式的行為，維護者直接 commit。不確定的話，問人類。這個 commit：

1.  自成一個，不併入開拓者的 commit；
2.  帶 trailer `Agent: Settler (review fix)`；
3.  在 `Impact:` 寫明為什麼這個修改不影響行為，讓人用讀的就能稽核。

---

## 4. 操作範本（附錄）

### 🎫 GitHub Issue 範本
```markdown
## 背景
[為什麼需要這件事？現況是什麼？]

## 範圍
- 包含: [這張票要動到的東西]
- 不包含: [明確排除的部分]

## 完成條件
- [ ] [可驗證的條件 1]
- [ ] [可驗證的條件 2]
- [ ] 文件對齊完成

## 參考
- Blueprint: [`kdd:forward` 才有，連結至 Docs/ 對應文件]
```

### 🟢 Git Commit 範本
```text
<type>(<scope>): <subject> (最多50字)

[Body: 為何需要這項變更？]
說明動機與邏輯。專注於「Why」而非「How」。
描述對專案架構或長期決策的影響。

Context: [票號，或連結至藍圖]
Impact: [對 API 合約或基礎設施的具體影響]
Test: [執行的驗證方式] (例如：make test-data-ingestor)
Agent: [開拓者 / 維護者 / 維護者 (review fix)]
Legacy: [留待下一個代理處理的待辦事項]
```

### 🔴 Handoff 範本
```markdown
# 📝 Legacy Note: [Task Name]

> **Date**: YYYY-MM-DD
> **From**: [Seat] / [Carrier] / [session id]
> **Resume**: [command that resumes this session in its tool]
> **To**: [Seat] / [new session, or blank if not yet known]
> **Trigger**: [Reactive: milestone | blocked | human handover] or [Deliberate: context degradation]
> **Ticket**: [<repo>-<issue_no>，例如 safezone-64；沒有就留空]
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

## Unverified / Uncertain
- [ ] What was assumed but never checked?
- [ ] What is the author unsure of?

## Next Actions
1. [Specific Instruction 1]
2. [Specific Instruction 2]
```

### ⚪ Draft 範本
```markdown
---
title: 'Design Draft: [Topic]'
doc_id: safechord.draft.[slug]
last_updated: 'YYYY-MM-DD'
status: draft
authors: [bradyhau, <agent>]
context_scope: [Methodology | Infrastructure | ...]
summary: [一段話說明這份草稿在決定什麼]
logical_path: SafeChord.Draft.[Name]
related_docs: []
archetype: script
doc_version: 0.1.0
---

# Design Draft: [Topic]

## 1. Background
[問題是什麼？有哪些約束？]

## 2. Proposed Solution
[提案內容，含必要的 mock code / schema]

## 3. Alternatives Considered
[還考慮過什麼？為什麼落選？]

## 4. Trade-offs
[接受了什麼代價？]

## 5. Next Steps
1. [ ] [下一步]
```