# 🧠 Meta: Documentation Governance

## 📂 用途說明 (Directory Purpose)

本目錄存放 SafeChord 專案的 **「關於文件的文件 (Meta-documentation)」**。
這裡定義了我們「如何寫文件」、「如何做決策」以及「AI 應扮演什麼角色」。它是專案知識庫的 **憲法與治理中心**。

---

## 🏗️ 結構導航 (Structure)

### 1. ⚖️ Standards (現行法規)
> **位置**: `standards/`

此目錄存放 **已經定案** 且 **必須嚴格遵守** 的規範。所有新產出的程式碼與文件都必須符合此處的定義。

*   **[taxonomy.md](standards/taxonomy.md)**: **文件分類與架構準則**。定義了四大原型 (Map, Blueprint, Script, Brain) 與 Metadata 規範。
*   **[style.md](standards/style.md)**: **寫作風格指南**。定義了語氣 (Persona)、禁語表以及 Markdown 格式規範。

### 2. 🗳️ Proposals (提案與 RFC)
> **位置**: `proposals/`

此目錄存放 **討論中**、**實驗性** 或 **待審核** 的架構建議 (Request for Comments)。
這些文件代表未來的方向，但尚未具備強制力。一旦提案通過，將被合併至 `standards/` 或實作為具體文件。

*   *(暫無活躍提案)*

---

## 🤖 AI Agent 指南 (AI Directives)

> **Core Mandate**: You are the **Guardian of Consistency**.

1.  **Rule Enforcement**: 在生成或修改任何 `Docs/docs/` 下的文件時，**必須優先讀取 `standards/taxonomy.md` 與 `standards/style.md`**。
2.  **Archetype Awareness**: 
    *   看到 `archetype: map` -> 專注於導航與索引。
    *   看到 `archetype: blueprint` -> 專注於介面與規格。
    *   看到 `archetype: script` -> 專注於步驟執行。
    *   看到 `archetype: brain` -> 專注於脈絡理解。
3.  **Governance Flow**: 當使用者提出新的架構想法時，請建議將其整理為一份新的 RFC 並存入 `proposals/`。