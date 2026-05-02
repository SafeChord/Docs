---
title: Knowledge-Driven Development (KDD)
doc_id: safechord.kdd.introduction
last_updated: '2026-04-27'
status: active
authors:
  - bradyhau
  - Gemini CLI
context_scope: Methodology
summary: 介紹 SafeChord 專案的核心開發方法論——知識驅動開發 (KDD)。闡述如何透過實體的知識地圖 (Knowledge Map) 建立具備複利效應的長期記憶，並以 TDD 作為 AI 的收斂邊界，重新定義 AI 時代的軟體工程。
keywords:
  - KDD
  - Knowledge Map
  - TDD
  - AI Collaboration
  - LLM Wiki
logical_path: SafeChord.KDD.Introduction
related_docs:
  - safechord.kdd.practice.md
  - safechord.knowledgetree.md
parent_doc: safechord.knowledgetree
doc_version: 0.3.0
archetype: brain
---

# 知識驅動開發 (Knowledge-Driven Development)

SafeChord 不僅是一個軟體專案，更是一場關於 **「AI 時代如何寫軟體」** 的架構實驗。我們採用的核心方法論稱為 **KDD (Knowledge-Driven Development)**。

## 1. 典範轉移：什麼是 KDD？

在過去，開發流程是「人類寫程式，最後再補文檔（如果有時間的話）」。
但在 AI 程式碼生成能力逐漸超越人類實作者的今天，KDD 反其道而行：

> **"Code is the Artifact of Knowledge. Documentation is the Source."**
> (程式碼只是產物，知識才是源頭。)

KDD 是一種以 AI 原生 (AI-native) 思維為基礎的開發哲學。它將結構化的「知識 (Knowledge)」與「意圖 (Intent)」作為開發的起點和核心驅動引擎，重新定義了「人機協作的邊界」。

---

## 2. 核心轉變：從「微觀規格 (Spec)」到「高階知識 (Knowledge)」

在 AI 時代，為什麼我們不再提倡傳統的 Spec-Driven (規格驅動)？

*   **微觀管理會扼殺 AI 的潛能**：傳統的 Spec 就像是一張「施工手冊」，把需求寫到最底層的實作細節。但現今的 AI（如 Claude 3.5 或更高階模型），其底層實作能力與演算法廣度往往超越了寫 Spec 的人類。如果我們用底層指令限縮它，就等於把一位「資深協作夥伴」當成了「打字機」。
*   **知識是活的，規格是死的**：KDD 放棄了「告訴 AI 怎麼做 (How)」，轉而提供「我們面臨的真實問題是什麼 (What)」、「架構的意圖為何 (Why)」，以及「過去嘗試過什麼、為何失敗 (ADR - 架構決策紀錄)」。
*   **將實作的自由還給 AI**：在 KDD 中，人類扮演架構師與指揮官，負責給予最完整的「背景知識」與「上下文」。在了解了這些 Knowledge 後，AI 能夠自由發揮創意，找到最佳的底層實作路徑。

---

## 3. 核心約束：TDD 作為 AI 的「收斂邊界」

既然我們給了 AI 最大的實作自由，那要如何防止它「暴走」？

*   **沒有邊界的 AI 就是災難**：給予強大的 Agent 工具一個模糊的目標，它往往會無止盡地發散、腦補出你沒要的功能、進行無效重構，最終不僅燒光 Token，系統也無法運行。
*   **從「品質保證」升級為「收斂機制」**：在 KDD 框架下，**TDD (Test-Driven Development)** 的意義發生了質變。測試不再只是為了防呆，更是引導強大 AI **收斂 (Convergence)** 的「物理紅牆」。
*   **意圖在文檔，規格在程式**：這是一個極其重要的分野。我們在 Markdown 知識地圖中，**只保留「為什麼要做 (Why)」、「問題是什麼 (What)」以及「架構決策紀錄 (ADR)」**。至於衍生出的詳細 API Contract (Schema) 與具體的 Test Cases，則應該直接交由 AI 實作並保存在 **Codebase 內**（即真實的程式碼與測試檔中），而非寫死在文檔裡。
*   **測試代碼即邊界**：我們要求 AI 在實作功能時，必須在 Codebase 中建立並通過對應的自動化測試。這等於告訴 AI：「你的底層實作無論怎麼發揮創意，最終都必須跑過程式庫裡的這些測試。」這把 AI 的幻覺 (Hallucination) 完美地鎖死在可執行的程式碼邊界內，同時也避免了讓文檔淪為難以維護的瑣碎規格書。

---

## 4. 知識的實體載體：為什麼是「知識地圖」而非「向量資料庫」？

目前 AI 領域的顯學是將文件丟進 Vector DB (向量資料庫) 進行 RAG 檢索，但 **KDD 堅持使用 Markdown 文件與實體樹狀目錄 (Knowledge Map)**，這與 Andrej Karpathy 提出的 **"LLM Wiki"** 概念高度共鳴：

*   **確定性 (Deterministic) vs. 機率性 (Probabilistic)**：
    Vector DB 將知識切碎，並依賴機率性的「語意相似度」來檢索。這容易導致 AI 每次都在「重新發現知識」，甚至將字面上相似但邏輯無關的模組混在一起，產生嚴重的「架構幻覺 (Retrieval Loss)」。
    相反地，KDD 透過 [**知識地圖 (`knowledgetree.md`)**](safechord.knowledgetree.md) 作為全局的路由中心。父子關係、模組依賴是**絕對確定**的。當 AI 處理特定任務時，必須「按圖索驥」，精準索引它「應該知道的檔案」，確立不可逾越的邊界。
*   **知識的複利效應 (Compound Knowledge)**：
    KDD 的知識樹不是靜態的，而是一個持續演進、具備複利效應的實體資產 (Persistent Artifact)。每一次的 PR、每一次的架構調整，都會在 Markdown 中留下交叉引用與矛盾標記。
*   **消除簿記 (Bookkeeping) 的勞動**：
    人類過去難以維護龐大的 Wiki，是因為繁瑣的連結與狀態更新。但在 KDD 的協作模式中，人類負責高階架構決策（Architect），而將這座龐大 Markdown 樹的維護、對齊與沉澱工作，交給不知疲倦的 AI 代理人（Settler）來執行。
*   **工具抽象化與載體適應性 (Tool-Agnostic Adaptability)**：
    AI 工具的迭代極快，SafeChord 在發展過程中經歷了從早期的 Web Chat 介面，到 API 調用，再演進至當前雙軌 CLI Agent 的無頭協作。之所以能無痛遷移，正是因為 **Markdown 檔案本身就是最強大的工具抽象層**。無論使用什麼廠商的模型或介面，這棵實體的知識樹永遠是同步各方認知 (包含人類與多種 Agent) 的通用橋樑。

> 📖 **Reference**: 此「知識地圖」與「檔案即知識庫」的理念，與 Andrej Karpathy 於 2025 年提出的 [LLM Wiki](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f) 概念不謀而合。KDD 早在 SafeChord 專案初期即實踐了此一「由 AI 維護持久性知識樹」的先進模式。

---

## 5. 動態平衡：雙向演進模型 (Bi-directional Evolution)

在真實的軟體工程中，如果死板地教條化 KDD，會遇到一個巨大的矛盾：理論上「知識是源頭 (Docs ➡️ Code)」，但在探索未知技術 (Spike) 時，強求先寫出完美的架構文檔，會徹底扼殺 AI 與人類的敏捷性。

為了擁抱開發過程中的「未知」，KDD 在宏觀理念上建立了一套**雙向演進 (Bi-directional Evolution)** 的動態平衡模型：

*   **戰略的秩序 (Forward: Docs ➡️ Code)**：
    對於既有模組的優化與已知架構的擴充，嚴格遵守「文件先行」。Markdown 知識節點作為不可逾越的法律，先發布意圖，再約束 AI 的實作邊界。
*   **戰術的拓荒 (Spike: Code ➡️ Docs)**：
    對於未知的技術探索，允許「實作先行」。給予 AI 拓荒的特權，去碰撞、去測試極限。但拓荒結束後，必須將實驗結果結構化，**逆向 (Reverse-engineer)** 寫回知識樹中，稱為「文件對齊 (Documentation Reconciliation)」。

這不是對 KDD 理念的妥協，而是系統在「呼吸」——以高階知識定義大局邊界（吸氣），以實戰淬鍊出的真實架構反哺知識樹（呼氣），形成生生不息的知識閉環。

---

## 6. 邁向實踐：雙軌制與無頭協作

上述是 KDD 的「道」與「北極星」。

至於在 2026 年的當下，SafeChord 專案具體是如何透過實體的 AI 工具（如 Gemini CLI、Claude Code）與標準化的協議（如 Git Commit 規範、雙軌工作流）來實踐這套理念，讓「文件即程式碼庫 (Docs as Codebase)」成為可能？

👉 請參閱：**[KDD 實作現狀：三機協同與無頭開發架構 (Practice)](safechord.kdd.practice.md)**