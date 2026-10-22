# KDD 2.0 實務

> **⚙️ 本文件正在調整期。** 雙引擎席位、票的生命週期、以及 §4 的範本都是 v0.4.0 才引入的，還沒跑完一個完整週期，會有粗糙的地方。
>
> **如果某個範本或步驟不合眼前的工作，請提出來，不要默默繞過去。** 文件與實際發生的事對不上，在被論證為其他情況之前都算文件的缺陷——跟人類提，然後在這裡修掉。
>
> **本告示還在的期間，不要遞增 `doc_version`。** 文件停在 v0.4.0 直到調整期結束，改動只反映在 `last_updated`。

## 模式 {#modes}

SafeChord 使用 agent 的方式，依工作內容與人類所在的位置分成幾種模式。§2 的協定與 §4 的範本所有模式共用；各模式自己的席位與流程，在表中列出的頁面。

| 模式 | 涵蓋的工作 | 人類的位置 | agent 怎麼運作 | 定義在 |
| :--- | :--- | :--- | :--- | :--- |
| 討論 | 還沒有票的工作，以及在 `Docs/` 與 harness 上的工作（這兩處直接 commit 到 `main`） | 全程參與，一起做決定 | 單一 agent 與人類對談；產出是票、設計草稿，或對 `Docs/` 或 harness 的修改 | 本文件 |
| 開發 | 經由分支、PR 與合併落進 SafeZone、SafeZone-Deploy 或 Chorde 的程式改動，票上掛著 `kdd:forward` 或 `kdd:spike` | 最後的守門員，合併前看一次 | 兩個席位互相制衡 | [開發](safechord.kdd.practice.development.md) |
| 交付 | 切出、驗證並推進 SafeZone 的 release：交付流程的某個階段或路線 | 全程參與，每個 gate 簽核 | 單一 agent 與人類協作 | [交付](safechord.kdd.practice.delivery.md) |
| 維運 | 未定 | 未定 | 未定 | — |

### 確認自己的模式 {#finding-your-mode}

session 對照上表的描述，自己判斷所在的模式；沒有把票對應到模式的規則。

- **動手前先說出來**：「這是<模式>，因為<理由>」。理由要點出是什麼決定的：票與它的 label、工作落在哪個 repo 以及那個 repo 怎麼收改動、人類要求了什麼。把模式說出來，人類才抓得到判錯的時候。
- **手上沒有票時，就是討論模式。**
- **沒有模式符合，或不只一個符合時，先問人類**再動手。不符合任何模式的工作，不硬塞進最接近的那個。
- **模式跟著工作變。** 開票或接手一張票，通常就是模式改變的時候；那時說出新的模式。
- **由 script 啟動的 session**（`pioneer-dispatch`、CI job）從啟動它的 prompt 取得模式與席位，不自己判斷。

### session 與席位 {#sessions-and-seats}

- 有席位的模式在自己的頁面定義席位，以及一個 session 持有席位多久。session 進入這種模式時，取得它在那裡的工作需要的席位。
- 透過其他途徑向啟動它的 session 回報的執行者，例如 subagent 或工具 run，算在那個 session 的模式與席位底下，自己不持席位。
- 範本要求填席位時，處在沒有席位的模式的 session 改填模式（`Agent: Discussion`）。

---

## 1. 雙引擎模型 {#1-the-two-engine-model}

已搬到[開發 §1](safechord.kdd.practice.development.md#1-the-two-engine-model)。

---

## 2. 溝通介面與協定

標準化的協定負責在代理之間、以及跨 session 傳遞資訊。

### 🎫 票（Ticket）
票是任何實作的開頭，是後續追蹤時做起點的依據。

*   **媒介**: 工作所在 repository 的 GitHub issue。
*   **目的**: 作為實作依據, 補的是 commit（太細）與專案文件（只有終態）都漏掉的那層粒度。
*   **份量**: 票幾乎是永久的，所以只放對日後讀者有追溯價值的內容：問題、決策與理由、範圍、Done When。只為這次任務對齊席位用的 context（推測的機制、調查細節、設計建議、未驗證項目、實作順序）放進 handoff。完成條件只寫合併前驗得了的；部署後才驗得了的，歸[交付流程](safechord.kdd.practice.delivery.md)的 gate。
*   **完成條件寫意圖，不寫形狀**: 寫結果必須成立的事（「logger 的輸出除了 `worker_id` 之外都不變」、「沒有任何 assertion 或測試輸入被改動」），不寫 diff 或名稱長什麼樣（「欄位名稱不變」、「diff 只動到 import」）。寫成形狀的條件，錯的改動照樣過、對的改動反而不過，而且範圍一允許改名，就跟範圍自相矛盾。
*   **時效**: 開票之後過了一段時間才動工的票，動工前要對照當下的藍圖與程式碼再核對一次。指向已經改寫的章節的引用、被後來的票改掉的「現況」，先在票上改正。
*   **分支**: `<type>/issue-<issue_no>-<slug>`，`<type>` 是這次改動的 commit type。`refactor/` 前綴保留給掛著 `mode:refactor` label 的票，這個 label 由人類與維護者在開票時約定：這個前綴會打開 agent 的 refactor mode，在這個模式下結構完整優先於最小 diff，範圍照樣有約束力。沒有掛這個 label 的 `type:refactor` 票，分支用 `chore/`。
*   **必要內容**: [參考範本](#github-issue-template)

### 🟢 基本溝通：Git Commit 協定
*   **媒介**: git
*   **目的**: 在實作過程中的細粒資訊載體。
*   **格式**: 嚴格遵循 [Conventional Commits](https://www.conventionalcommits.org/)。
*   **必要內容**: [參考範本](#git-commit-template)

### 🔴 交接協定 {#the-handoff-protocol}
*   **媒介**: 存放在 `.ai-session-handoffs/` 的 Markdown 檔案。
*   **目的**: 跨 ai 工具 session 的載體。交接對象包含下一個 session，或另一個代理。
*   **觸發條件舉例**:
    - 開拓者完成一個 Spike 或開發階段。
    - 代理遇到其操作範圍外的錯誤。
    - 人類介入要求任務移交(通常是 Context 已經長到開始劣化)。
*   **席位之間的交接**: 開發模式的三種檔在[開發 §2](safechord.kdd.practice.development.md#handoffs-between-the-seats)。
*   **生命週期**: handoff 跟著任務走。PR merge、票關閉、reconciliation 落進 `Docs/` 之後就刪除；harness 的 git history 會留著，需要時可以找回。
*   **連結方向**: handoff 指向票，票不反指。看得到 handoff 的人一定找得到票，看得到票的人卻不一定看得到 handoff；而且 handoff 刪除後，永久的票上會留下一條死連結。
*   **命名規則**: 有對應的票時，handoff 檔名帶上小寫的 `<repo>-<issue_no>`（例如 `2026-09-19-safezone-64-worker-offset-commit.md`）。
*   **叫回 session**: 因里程碑、卡關或人類移交而交接的 session，可以用筆記裡的 `Resume:` 指令叫回來，例如修正審查發現的問題。因 Context 劣化而交接的 session 就此退休，不再叫回。
*   **必要內容**: [參考範本](#handoff-template)

### 🟣 Pull Request {#the-pull-request}
已搬到[開發 §2](safechord.kdd.practice.development.md#the-pull-request)。

### ⚪ 設計草稿
*   **媒介**: 存放在 `.ai-session-drafts/<domain>/` 的 Markdown 檔案。
*   **目的**: 在任何不直接影響 codebase 的前瞻討論須要有延續時，通常出現在開票之前。
*   **domain 分類**：
    - `kdd/`（practice、seat、審查流程）
    - `delivery/`（release workflow、gate、soak）
    - `platform/`（網路、ingress、安全、可觀測性）
    - `app/`（SafeZone 程式的 debug 與改進）。
*   **必要內容**: [參考範本](#draft-template)

---

## 3. 雙軌工作流程：KDD 的平衡 {#3-dual-track-workflow}

已搬到[開發 §3](safechord.kdd.practice.development.md#3-dual-track-workflow)，小節編號與 id 都沒變。

---

## 4. 操作範本（附錄）

### 🎫 GitHub Issue 範本 {#github-issue-template}
```markdown
## 背景
[為什麼需要這件事？現況是什麼？]

## 範圍
- 包含: [這張票要動到的東西]
- 不包含: [明確排除的部分]

## 完成條件
- [ ] [可驗證的條件 1]
- [ ] [可驗證的條件 2]
- [ ] 文件對齊完成（`kdd:spike`：或與人類確認不需要）

## 參考
- Blueprint: [`kdd:forward` 才有，連結至 Docs/ 對應文件]
```

文件對齊那一條是唯一在合併後才勾的完成條件：它是流程的最後一步，不是 PR 能證明的條件。

### 🟢 Git Commit 範本 {#git-commit-template}
```text
<type>(<scope>): <subject> (最多50字)

[Body: 為何需要這項變更？]
說明動機與邏輯。專注於「Why」而非「How」。
描述對專案架構或長期決策的影響。

Context: [票號，或連結至藍圖]
Impact: [對 API 合約或基礎設施的具體影響]
Test: [執行的驗證方式] (例如：make test-data-ingestor)
Agent: [開拓者 / 維護者 / 維護者 (review fix) / 維護者 (requirement test)]
Legacy: [留待下一個代理處理的待辦事項]
```

### 🔴 Handoff 範本 {#handoff-template}
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

開發模式的範本（席位之間的交接、Pull Request）在[開發 §4](safechord.kdd.practice.development.md#4-development-templates)。

### ⚪ Draft 範本 {#draft-template}
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