---
title: "[System/Module Name] Overview"
doc_id: safechord.[layer].[module]
doc_version: [Document Version]
app_version: "[Repository Version or null]"
last_updated: "YYYY-MM-DD"
status: draft
authors:
  - [Author Name]
context_scope: "[System-Wide / Repository]"
summary: "[High-level executive summary of this system boundaries and purpose.]"
keywords:
  - [Tag1]
  - [Tag2]
logical_path: "SafeChord.[Layer].[Module]"
related_docs:
  - "[Sub-component Blueprint 1]"
  - "[Sub-component Blueprint 2]"
parent_doc: "[Parent Map ID]"
archetype: map
code_paths:
  - "[Repo/Folder Root Path]" # 指向該模組的程式碼根目錄 (e.g., SafeZone/)
---

# [System/Module Name] (Map)

> **Map (地圖型)**：適用於系統總覽、模組入口或知識導航。
> *重點：導航 (Links)、聚合 (Aggregation)、全景圖 (Big Picture)。*

## 1. 系統總覽 (System Overview)
*(必選)*
*   **一句話定義**：這是什麼？
*   **核心價值**：為什麼需要這個系統？
*   **關鍵能力**：
    *   Capability A
    *   Capability B

## 2. 知識導航 (Knowledge Navigation)
*(必選)*
提供通往子文件的入口。建議使用分類表格或清單。

| 模組/組件 | 類型 | 說明 | 連結 |
| :--- | :--- | :--- | :--- |
| **Component A** | 🔵 Blueprint | 核心服務 A | [Link] |
| **Workflow B** | 📜 Script | 部署流程 SOP | [Link] |
| **Decision C** | 🧠 Brain | 架構決策紀錄 | [Link] |

## 3. 架構全景 (Architecture Landscape)
*(推薦)*
*   **系統邊界圖**：使用 Mermaid 或圖片展示系統邊界。
*   **關鍵互動**：描述本系統如何與外部系統 (Upstream/Downstream) 互動。

## 4. 閱讀指引 (Reading Path)
*(推薦)*
針對不同讀者提供閱讀建議。

*   **我是開發者**：先看 [Component A]，再看 [Workflow B]。
*   **我是維運人員**：請關注 [Monitor Blueprint]。

## 5. 狀態摘要 (Status Summary)
*(可選)*
*   當前版本：v0.x.x
*   已知限制或 Roadmap 連結。
