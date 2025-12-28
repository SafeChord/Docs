---
title: Knowledge-Driven Development (KDD)
doc_id: safechord.kdd.introduction
version: 1.0.0
last_updated: "2025-12-28"
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
context_scope: "Methodology"
summary: "介紹 SafeChord 專案的核心開發方法論——知識驅動開發 (KDD)。闡述如何以文檔為「唯一真理來源 (Source of Truth)」，驅動 AI Agent 進行精準的程式碼生成與架構維護，並定義當前的人機協作模式。"
keywords:
  - KDD
  - AI Collaboration
  - Documentation-First
  - Prompt Engineering
  - Human-in-the-Loop
logical_path: "SafeChord.KDD.Introduction"
related_docs:
  - "safechord.kdd.practice.md"
  - "safechord.knowledgetree.md"
parent_doc: "safechord.knowledgetree"
---

# 知識驅動開發 (Knowledge-Driven Development)

SafeChord 不僅是一個軟體專案，更是一場關於 **「AI 時代如何寫軟體」** 的實驗。我們採用的核心方法論稱為 **KDD (Knowledge-Driven Development)**。

---

## 1. 核心哲學 (Core Philosophy)

傳統開發是「人寫程式 -> 補文檔（如果有時間）」。KDD 則反其道而行：

> **"Code is the Artifact of Knowledge. Documentation is the Source."**
> (程式碼是知識的產物，文檔才是源頭。)

在 KDD 流程中，我們不直接對 AI 說「幫我寫一個登入功能」，而是：
1.  **定義知識**: 在文檔中定義「登入」的規格、資料模型、安全約束。
2.  **載入 Context**: 讓 AI 閱讀這些文檔。
3.  **生成實作**: AI 根據文檔生成符合規範的程式碼。

---

## 2. 當前狀態與成熟度 (Status & Maturity)

> **💡 Project Status: KDD Phase 1 - Human-Orchestrated Agents**
>
> 為了避免誤解，我們誠實定義本專案目前的自動化程度：

SafeChord 目前處於 KDD 的 **第一階段 (Phase 1)**。這意味著我們已經建立了 AI-Ready 的知識結構，但 Agent 之間的互動仍需 **人類介入**。

*   **Vision (願景)**: 實現 "Text-to-App" 的全自動化流水線。
*   **Reality (現狀)**: 採用 **人機協同 (Human-in-the-Loop)** 模式。
    *   **人類 (Human)**: 扮演 **Orchestrator (指揮官)**。負責在不同 AI Agent 之間傳遞 Context，進行決策仲裁，並手動觸發生成任務。
    *   **Builder Agent (Gemini CLI)**: 負責維護知識庫結構與 Spec 文件。
    *   **Coder Agent (Cline / DeepSeek)**: 負責讀取 Spec 並產出程式碼。
*   **價值**: 雖然尚未全自動，但這種模式強迫我們將所有隱性知識 (Tacit Knowledge) 轉化為顯性文檔，確保了系統架構的一致性，並大幅減少了 AI 幻覺。

---

## 3. 為什麼需要 KDD？

*   **消除幻覺**: AI 容易胡說八道，除非你有明確的「邊界」限制它。結構化的知識庫就是這個邊界。
*   **長期記憶**: 對話視窗 (Context Window) 是短暫的，但文件是永恆的。KDD 讓專案的智商隨著文件積累而成長，而不是隨著對話結束而重置。
*   **架構一致性**: 當所有 Agent 都參考同一份架構圖工作時，系統就不會長歪。

---

## 4. KDD 的演進路線圖 (Roadmap)

### Level 1: Context Awareness (當前階段)
*   建立完整的知識地圖 (`knowledgetree.md`)。
*   人類負責確保 Agent 在執行任務前，已閱讀正確的文件。
*   **Human-Orchestrated**: 手動協調 Builder 與 Coder 的工作交接。

### Level 2: Spec-Driven Generation (中期目標)
*   撰寫結構化的 Markdown Spec (Prompt Code)。
*   開發簡單的 CLI 工具，自動提取 Markdown 中的 TestCase 並生成測試腳本。
*   "Document is the Code."

### Level 3: Autonomous Evolution (長期願景)
*   AI 在修改程式碼後，自動回過頭來更新文件。
*   知識庫與程式碼庫達成即時雙向同步，無需人類介入文檔維護。

---

## 5. 下一步

要了解我們目前如何實作 Level 1 的協作模式，請閱讀 [實作現狀：基於知識庫的協作模式](safechord.kdd.practice.md)。
