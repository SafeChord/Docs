---
title: "[Decision/Concept Name]"
doc_id: safechord.[layer].[concept]
doc_version: [Document Version]
last_updated: "YYYY-MM-DD"
status: draft
authors:
  - [Author Name]
context_scope: "[System-Wide / Specific Layer]"
summary: "[One sentence summary of the decision or principle.]"
keywords:
  - [Tag1]
  - [Tag2]
logical_path: "SafeChord.[Layer].[Concept]"
related_docs:
  - "[Related Blueprint/Map]"
parent_doc: "[Parent Doc ID]"
archetype: brain
code_paths: [] # Brain 通常不綁定特定程式碼，若有則指向 POC 目錄
---

# [Decision/Concept Name] (Brain)

> **Brain (大腦型)**：適用於架構決策 (ADR)、設計原則、安全策略、環境規劃。
> *重點：背景、原因 (Why)、權衡 (Trade-offs)、限制。*

## 1. 背景與脈絡 (Context)
*(必選)*
*   我們面臨什麼問題？
*   **限制條件 (Constraints)**：
    *   預算限制 (e.g., $50/mo)。
    *   技術限制。

## 2. 核心原則 (Core Principles)
*(必選)*
列出指導此決策的最高指導原則。
1.  **原則一**: e.g., Infrastructure as Code (IaC).

## 3. 決策內容 (Decisions)
*(必選)*
詳細說明我們決定做什麼，以及為什麼這樣做。

### 決策點 A: [Decision Name]
*   **決定**: 我們選擇使用 X 技術。
*   **理由 (Justification)**: 因為 X 支援我們的需求 Y...
*   **替代方案 (Alternatives)**: 我們也考慮過 Z，但因為...所以放棄。

## 4. 權衡與後果 (Consequences & Trade-offs)
*(推薦)*
誠實面對決策帶來的副作用。

| 優點 (Pros) | 缺點 (Cons) | 緩解措施 (Mitigation) |
| :--- | :--- | :--- |
| 開發速度快 | 執行效能較差 | 透過 Horizontal Scaling 解決 |

## 5. 參考資料 (References)
*(自由發揮)*
*   外部連結。
*   相關的 Issue 或 PR。