---
title: "Standard: Documentation Taxonomy"
doc_id: safechord.meta.standard.taxonomy
version: 1.0.0
status: active
authors:
  - bradyhau
  - Gemini 3 Pro
context_scope: "Meta"
summary: "定義 SafeChord 專案的文件分類體系。確立「四大原型 (Map, Blueprint, Script, Brain)」作為撰寫指引，並規範 Frontmatter 的標記方式。"
keywords:
  - Taxonomy
  - Archetypes
  - Standard
  - Documentation
logical_path: "SafeChord.Meta.Standard.Taxonomy"
related_docs:
  - "style.md"
parent_doc: "safechord.meta"
archetype: brain
code_paths: []
---

# 文件分類與架構準則 (Documentation Taxonomy Standard)

> **生效日期**: 2026-01-04
> **適用範圍**: `Docs/docs/` 下的所有業務文件（即 `Docs/docs/*.md` 不包含子路徑 如 `meta/`, `draft/`...）。

本文件定義 SafeChord 專案的知識庫分類體系。為了降低 AI 上下文過載並提升檢索精確度，所有文件必須依據 **「四大原型 (The 4 Archetypes)」** 進行分類與撰寫。

---

## 1. 四大原型定義 (The 4 Archetypes)

我們放棄單純的「顆粒度」分類，改採「功能性」分類。撰寫新文件時，請務必選擇最合適的原型，並套用對應模板。

| 原型 (Archetype) | Frontmatter 標記 | 核心價值 | 典型特徵 | 對應模板 |
| :--- | :--- | :--- | :--- | :--- |
| **地圖型 (Map)** | `archetype: map` | **導航與聚合** | 總覽、索引、連結列表、閱讀路徑 | `archetype.map.md` |
| **藍圖型 (Blueprint)** | `archetype: blueprint` | **靜態結構** | 介面定義 (API)、依賴關係、配置參數 | `archetype.blueprint.md` |
| **劇本型 (Script)** | `archetype: script` | **動態流程** | 步驟 (Step-by-step)、狀態變遷、SOP | `archetype.script.md` |
| **大腦型 (Brain)** | `archetype: brain` | **決策邏輯** | 設計原則、權衡分析 (Trade-offs)、ADR | `archetype.brain.md` |

---

## 2. Frontmatter 規範 (Metadata Standards)

所有 Markdown 文件檔頭 (Frontmatter) 必須包含以下標準欄位，以利 AI 識別。

### 2.1 必選欄位
```yaml
---
# 用於 AI 識別文件類型，必須小寫
archetype: map | blueprint | script | brain

# 指引 AI 去哪裡尋找實作代碼 (若不適用則留空 [])
# 注意：請指向「根目錄」而非特定檔案，保留探索彈性
code_paths:
  - "SafeZone/services/analytics-api" 
---
```

### 2.2 欄位行為定義
*   **`archetype`**: 
    *   若文件性質混合，請優先拆分為不同文件。
    *   若無法拆分，可標記為 `mixed`，但應視為技術債。
*   **`code_paths`**: 
    *   AI Agent 在讀取此文件後，若需進一步實作，**應優先列出 (list)** 這些路徑下的檔案結構，而非直接讀取內容。

---

## 3. 內容撰寫規範 (Content Guidelines)

### A. 模板驅動 (Template-First)
禁止從零開始撰寫文件。必須複製 `Docs/docs/templates/` 下的對應模板開始，以確保「必選區塊」不被遺漏。

### B. 分層展開策略 (Lazy Loading Strategy)
為了節省 Token，在描述檔案結構時，請採用 **分層展開**：
*   **Map/Overview 文件**：僅列出第一層目錄 (Shallow)。
*   **Blueprint 文件**：詳細展開該組件的關鍵檔案 (Deep)。
*   **外部引入 (Vendored Code)**：對於直接複製進專案的第三方套件或 Chart（如 `bitnami/redis`），**嚴禁展開其結構**。請使用括號註明來源即可，以避免雜訊。
    *   *正確範例*：`├── redis/  # (Vendored from Bitnami, customized values only)`
    *   *錯誤範例*：展開 redis 下的所有 templates/* 文件。

### C. 實作連結 (Linking)
*   **Brain -> Map**: 決策文件應連結回它影響的系統地圖。
*   **Script -> Blueprint**: 流程文件應連結至它操作的組件藍圖。

---

## 4. 治理與檢查 (Governance)

*   **Doc Linter**: CI 流程將檢查所有 `.md` 檔案是否包含合法的 `archetype` 欄位。
*   **Review**: 人類在審核 PR 時，應檢查文件類型是否誤用（例如：在 Blueprint 裡寫了大量的心路歷程，應該移至 Brain）。
