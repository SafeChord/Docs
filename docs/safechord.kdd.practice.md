---
title: KDD 2.0: Dual-Track CLI & Headless Collaboration
doc_id: safechord.kdd.practice
last_updated: '2026-04-23'
status: active
authors:
  - bradyhau
  - Gemini CLI
context_scope: Methodology
summary: 定義 SafeChord v0.3.x 的三機協同 (Three-Engine) 與無頭開發模型。詳述 Settler (Gemini CLI) 如何透過跨代理人協議維護四層解耦架構的一致性，將 KDD 2.0 轉化為高效的生產力閉環。
keywords:
  - Dual-Track CLI
  - Claude Code
  - Gemini CLI
  - Git Commit Protocol
  - Headless Development
  - Legacy Handoff
logical_path: SafeChord.KDD.Practice
related_docs:
  - safechord.kdd.workflow.md
  - safechord.roadmap.md
parent_doc: safechord.kdd.introduction
doc_version: 0.3.0
archetype: script
---

# KDD 2.0 實作現狀：三機協同與無頭開發架構

在 2026 年的 SafeChord 開發語境下，我們採用「三機協同」模型：利用 Gemini WebChat 進行高階戰略決策，並配合雙軌 CLI 進行無頭化開發與文件沉澱。

---

## 1. 三機協同模型 (The Three-Engine Model)

我們根據 AI 模型的特性與 Context 邊界，將開發任務劃分為三個層級：

| 角色 | 實體工具 | 核心職責 | 關注點 |
| :--- | :--- | :--- | :--- |
| **🏛️ 戰略決策中心 (Architect)** | **Gemini WebChat** | **設計與權衡**：定義技術堆疊、架構決策、分析長期 Trade-offs。 | 戰略 (Why/How) |
| **🛡️ 前瞻監督者 (Pioneer)** | **Claude Code** | **主要開發與解題**：負責大部分的代碼實作、未知技術 Spike、複雜邏輯除錯、突破邏輯死結。 | 戰術 (Spike & Code) |
| **🧠 文件執行者 (Settler)** | **Gemini CLI** | **Review、歸檔與輔助決策**：提前規劃測試、全域 Code Review、KDD 文檔逆向生成與維護。透過 Plan Mode 參與需要 Codebase 狀態的戰略討論（為 WebChat 提供結構化 Context）。 | 執行 (Structure) |

> **💡 協作備註 (Agent Roles Update)**
> - **Gemini CLI 的戰略輔助角色**：由於 WebChat 無法直接讀取本地 Codebase，Gemini CLI 可以透過 `enter_plan_mode` 參與架構討論，整理 codebase 狀態並匯出文件，方便人類將資訊貼給 WebChat 進行高階決策。
> - **職責分流**：目前主要的程式碼撰寫與功能開發皆交由 Claude Code (Pioneer) 負責；而 Gemini CLI (Settler) 則專注於 Review、架構把關與文件歸檔。

---

## 2. 溝通介面與協議 (Communication Interface)

在無頭開發環境中，Agent 之間的資訊交換必須具備標準化的媒介。

### 🟢 基礎溝通：Git Commit Protocol
當不需要進行正式「換手 (Handoff)」的日常迭代時，**Git Commit Message** 是兩個 CLI (Claude/Gemini) 與人類之間唯一的溝通橋樑。
*   **原則**: Commit Message 必須包含「變更意圖」與「架構影響」。
*   **格式要求**: 採用 [Conventional Commits](https://www.conventionalcommits.org/)。
*   **Agent 義務**: Gemini CLI 在進行 Review 時，必須解讀上一個 Agent (如 Claude) 的 Commit Message，以理解當前代碼的變更背景。

### 🔴 換手機制 (the Handoff Protocol)
當任務發生執行死結（鬼打牆）、完成階段性目標，或需要進行跨 Agent 的深度技術移交時，必須啟動「換手機制」。
*   **媒介**: 統一存放在專案根目錄 `.ai-session-handoffs/` 下的臨時 Markdown 檔案。
*   **觸發條件**: 
    - Pioneer (Claude Code) 完成 Spike 或階段性開發。
    - Settler (Gemini CLI) 宣告執行失敗或遇到範圍外的錯誤。
    - 人類工程師強制要求中斷並交接任務。
*   **內容必備**:
    1.  **目前狀態 (Status)**: 換手日期、交接方向 (From/To)、當前分支狀態、進度總結與下一步預計使用的工具。
    2.  **改動內容 (What Changed)**: 檔案路徑與具體的架構變更。
    3.  **已嘗試路徑 (Verified Path)**: 哪些嘗試已證實可行？哪些是坑？*(註：僅在任務未完成的異常換手時才需要詳細記錄此項)*。
    4.  **待辦事項 (Next Actions)**: 給下一個 Agent 的明確指令與驗證標準。

### ⚪ 草稿設計 (Design Draft)
當進行高階戰略決策或規劃複雜重構任務時，人類或 Gemini CLI 應產出設計草稿，作為 Pioneer (Claude Code) 後續實作的明確藍圖。
*   **媒介**: 統一存放在專案根目錄 `.ai-session-drafts/` 下的臨時 Markdown 檔案。
*   **內容必備**: 建議參閱附錄中的 [Design Draft 模板](#-design-draft-模板-draft)，涵蓋 Background, Proposed Solution, Blueprint, Trade-offs, Next Steps 等結構化論述，以維持全域架構的一致性。

---

## 3. 螺旋式 KDD：從戰略到沉澱 (Workflow)

這是一個典型的任務生命週期，展示了三個角色如何交替接棒：

1.  **決策階段 (Strategic Design)**: 
    *   人類與 **Gemini WebChat** 討論架構與可行性。
    *   若需要精確的 Codebase 狀態，可指派 **Gemini CLI** 進入 `Plan Mode`，生成如 `.ai-session-drafts/` 的**設計草稿 (Design Draft)**。
2.  **實作階段 (Spike / Code)**: 
    *   **換手 (Handoff)**: 將設計草稿或明確的 Legacy Note 交接給 **Claude Code**。
    *   **Claude Code** 接手後，建議先透過 Opus 模型（或其內建的 Plan Mode）分析草稿可行性並規劃任務。
    *   計畫確認後，切換至 Sonnet 模型執行具體的代碼變更與測試實作。
3.  **收尾階段 (Completion & Handoff)**: 
    *   Claude 完成開發後，**必須**負責：提交代碼、建立 PR (Pull Request)，並將系統狀態總結為 Legacy Note 交接給 Gemini CLI。
4.  **定錨與沉澱 (Solidify)**: 
    *   由 **Gemini CLI** 接手最後的 Legacy Note，負責：執行 PR Code Review、Merge 程式碼、打上 Version Tag（若有需要）、關閉對應的 GitHub Issue，並進行 **文件對齊 (Documentation Reconciliation)**，將成果反向寫入 `Docs/` 的 SSOT 中，完成知識閉環。

---

## 4. 無頭開發 (Headless) 協作守則

*   **Terminal 為唯一真實 (Single Source of Truth)**: 所有的開發與測試均在終端機完成。IDE 僅作為視覺化 Review 提示工具。
*   **Review 即文檔**: Gemini CLI 在 Review 通過後的同時，即具備「文檔撰寫者」的身分。
*   **信任海量記憶**: 充分利用 Gemini CLI 的 Context 窗口進行全專案影響分析，避免破壞 API 契約。

---

## 5. 附錄：操作模板 (Operational Templates)

為了確保 Agent 間的語意對齊，所有協作者必須遵循以下溝通規範：

### 🟢 Git Commit 模板 (Routine)
遵循 [Conventional Commits](https://www.conventionalcommits.org/) 與 [Git Trailers](https://git-scm.com/docs/git-interpret-trailers) 標準，確保 Settler (Gemini) 進行 Review 時具備足夠 Context。

```text
<type>(<scope>): <subject> (50 chars max)

[敘述性內文: 為什麼需要這個變更？]
詳細說明本次變更的動機與邏輯。解釋「為什麼 (Why)」而非「怎麼做 (How)」，
並描述其對專案架構或長期決策的影響。

Context: [關聯的 Blueprint 路徑或 Issue ID]
Impact: [對架構、API 契約或基礎設施的具體影響]
Test: [執行了哪些測試驗證？ (e.g. make smoke-test)] (若無特定測試可省略此行)
Agent: [執行此提交的 AI 代理人 (e.g. Gemini CLI, Claude Code)]
Legacy: [若有遺留問題，在此標註供下一個 Agent 處理]
```
### 🔴 Handoff 模板 (Legacy Note)
適用於跨 Agent 移交任務（存放在 `.ai-session-handoffs/` 的臨時 Markdown）。

```markdown
# 📝 Legacy Note: [任務名稱]

> **Date**: YYYY-MM-DD
> **From**: [Agent Name]
> **To**: [Agent Name]
> **Branch**: [Branch Name]
> **Action Required**: [Brief summary of expected next steps]

---

## Status / Summary
[描述當前進度：已打通 / 部分完成 / 邏輯死結]

## What Changed
[列出主要的目錄結構變更或核心架構調整]

## Verified Path (Optional)
- [x] 哪些嘗試已經證實可行？
- [ ] 哪些是確認的坑 (Dead Ends) 或報錯？

## Next Actions
1. [具體下一步指令 1]
2. [具體下一步指令 2]
```

#### 💡 Handoff 範例 (v0.3.1 Scaffold Complete)
當 Pioneer (Claude) 完成階段性任務交接給 Settler (Gemini) 時的實際範例：

```markdown
> **Date**: 2026-04-22
> **From**: Claude Code (Pioneer)
> **To**: Gemini CLI (Settler)
> **Branch**: `feature/v0.3.1-scaffold` → merged to `dev` via PR #36
> **Action Required**: Complete PR code review, Complete merge, 0.3.1 version tag, Documentation reconciliation

---

## Summary
v0.3.1 scaffold implementation on `analytics-api` is complete, tested, and merged.
All work is on `SafeZone` repo. The `utils` submodule also received one commit.

## What Changed
### Directory Structure
    ... 

### Key Architectural Changes
    ...


## Next Actions 
### Documentation Reconciliation Needed (Settler Tasks)
    1. Update `safechord.roadmap.md`
    2. Scaffold Blueprint doc ...
```


### ⚪ Design Draft 模板 (Draft)
適用於戰略決策與複雜重構提案（存放在 `.ai-session-drafts/`）。本模板旨在為 Coder Agent 提供清晰的實作藍圖。

```markdown
# Design Draft: [任務名稱/組件名稱]

> **Date**: YYYY-MM-DD
> **Status**: [Proposed / Approved]
> **Component**: [Affected microservices or modules]
> **Context**: [Linked Roadmap version or Issue ID]

## 1. 背景與痛點 (Background & Problem Statement)
[詳細說明為什麼需要這個變更。目前的設計存在哪些缺陷？對於 AI 來說有哪些協作阻礙？]

## 2. 解決方案 (Proposed Solution)
[描述高階設計思路。將如何解決上述痛點？]

## 3. 架構實作藍圖 (Blueprint)
[定義具體的目錄結構變更、API 契約調整或分層規則。]
[包含 Mock 代碼範例或 Pydantic 模型定義。]

## 4. 優缺點分析 (Trade-offs)
[誠實記錄此設計的權衡：為什麼選擇 A 而非 B？目前的架構債在哪裡？]

## 5. 下一步計畫 (Next Steps)
[列出具體的執行步驟，供 Pioneer (Claude) 參考。]
```