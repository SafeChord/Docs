---
title: KDD Workflow (Three-Step Process)
doc_id: safechord.kdd.workflow
version: 1.0.0
last_updated: "2025-12-25"
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
context_scope: "Methodology"
summary: "詳細定義 Knowledge-Driven Development (KDD) 的三階段工作流程：從高階架構定義 (Step 1)，到詳細語意與 TDD 規格標記 (Step 2)，最終達成自動化生成 (Step 3)。"
keywords:
  - KDD Process
  - Semantic Tagging
  - TDD
  - Prompt Engineering
logical_path: "SafeChord.KDD.Workflow"
related_docs:
  - "safechord.kdd.practice.md"
  - "safechord.knowledgetree.md"
parent_doc: "safechord.kdd.introduction"
---

# KDD 工作流程 (KDD Workflow)

KDD 不是一個單一的動作，而是一個**「從抽象到具體」**的漸進式過程。我們將其劃分為三個核心階段。

---

## 🟢 Step 1: 高階描述語言 (High-Level Description)
> **目標**: 建立專案的「骨架」與「地圖」。

在此階段，人類工程師與 AI (Builder Role) 協同工作，產出結構化的文件集合。

### 核心活動
1.  **知識樹構建**: 建立 `knowledgetree.md`，定義專案的邊界與模組關係。
2.  **節點定義**: 為每個核心概念（如 `SafeZone`, `Chorde`）建立初步的 Markdown 文件。
3.  **元數據填充**: 確保每個文件都有標準的 YAML Frontmatter (`doc_id`, `summary`, `related_docs`)。

### 產出物 (Artifacts)
*   **Knowledge Tree**: 專案的 AST (Abstract Syntax Tree)。
*   **Metadata**: 為 RAG 系統提供索引依據。

---

## 🟡 Step 2: 語意標記與 TDD (Semantic Tagging & TDD)
> **目標**: 將「意圖」轉化為「可測試的規格」。

這是 KDD 最關鍵的一步。我們使用 **泛型模板 (Generic Templates)** 與 **TDD (Test-Driven Development)** 來填充細節。

### 核心理念
*   **文件即規格**: 不只是寫「做一個登入功能」，而是寫出 API 的輸入輸出、錯誤碼。
*   **TDD as Spec**: 在 Markdown 中定義 `TestCase` 表格。這些測試案例不僅是 QA 的依據，更是 AI 理解業務邏輯的 Rosetta Stone。

### 核心活動
1.  **應用模板**: 根據節點類型（如 Service, Library），套用對應的 Markdown 模板。
2.  **定義介面**: 明確 API Endpoints, Event Topics, Data Models (JSON Schema)。
3.  **撰寫測試案例**:
    *   *Input*: 使用者傳送 `POST /login`。
    *   *Expected*: 回傳 `200 OK` 與 JWT Token。
    *   *Error*: 密碼錯誤回傳 `401`。

### 產出物
*   **Rich Spec Documents**: 包含詳細 API 定義與測試矩陣的 Markdown 文件 (e.g., `safechord.safezone.service.auth.md`)。

---

## 🔴 Step 3: 自動化生成 (Generation & Evolution)
> **目標**: 讓 AI (Coder Role) 讀取規格，生成實作。

*(註：目前 SafeChord 專案正處於從 Step 2 過渡到 Step 3 的階段)*

### 核心活動
1.  **Context 載入**: AI 讀取 Step 2 產出的 Spec 文件。
2.  **程式碼生成**:
    *   生成 Pydantic/Go Structs (基於 Data Model Spec)。
    *   生成 Unit Tests (基於 TestCase 表格)。
    *   生成 Implementation (通過測試)。
3.  **反向更新**: 如果實作過程中發現規格有誤，AI 應回頭修正 Step 2 的文檔，保持一致性。

---

## 總結

| 階段 | 關注點 | 主導角色 | 關鍵產出 |
| :--- | :--- | :--- | :--- |
| **Step 1** | **廣度 (Breadth)** | Architect + Builder | 知識地圖, 檔案結構 |
| **Step 2** | **深度 (Depth)** | Architect + Builder | API Spec, TDD Cases |
| **Step 3** | **實作 (Implementation)** | Coder | Source Code, Tests |
