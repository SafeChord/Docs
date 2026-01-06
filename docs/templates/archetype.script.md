---
title: "[Workflow Name] Workflow"
doc_id: safechord.[layer].workflow.[name]
version: 0.0.1
status: draft
authors:
  - [Author Name]
context_scope: "[Repository Name]"
summary: "[One sentence description of the process goal.]"
keywords:
  - [Tag1]
  - [Tag2]
logical_path: "SafeChord.[Layer].Workflow.[Name]"
related_docs:
  - "[Related Blueprint Doc]"
parent_doc: "[Parent Doc ID]"
archetype: script
code_paths:
  - "[Script/Workflow Root Path]" # e.g., .github/workflows/
---

# [Workflow Name] (Script)

> **Script (劇本型)**：適用於操作流程、SOP、GitOps 工作流、災害復原演練。
> *重點：步驟、角色、順序、狀態變遷。*

## 1. 目標與範圍 (Objective)
*(必選)*
*   這個流程的目的是什麼？
*   什麼時候觸發這個流程？
*   **先決條件 (Prerequisites)**：
    *   需要具備的權限。
    *   環境狀態要求。

## 2. 參與角色與工具 (Actors & Tools)
*(推薦)*
列出流程中的關鍵執行者。

| 角色/工具 | 職責 (Responsibility) | 類型 |
| :--- | :--- | :--- |
| **Developer** | 發起 PR | 人類 |
| **GitHub Actions** | 執行測試 | 自動化機器人 |

## 3. 標準作業程序 (Standard Operating Procedure)
*(必選)*
使用有序列表詳述步驟。

### 階段一：準備 (Preparation)
1.  步驟 1...

### 階段二：執行 (Execution)
1.  **關鍵動作**: 描述核心操作。
    *   *指令範例*: `make deploy`
2.  **系統回應**: 預期會看到什麼結果？

### 階段三：驗證 (Verification)
1.  如何確認成功？

## 4. 狀態變遷圖 (State Transition)
*(推薦)*
描述實體在流程中的狀態變化 (e.g., Draft -> Merged)。

## 5. 異常處理 (Exception Handling)
*(自由發揮)*
*   Rollback 策略。
*   Hotfix 路徑。