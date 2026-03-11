---
title: KDD 2.0: Dual-Track CLI & Headless Collaboration
doc_id: safechord.kdd.practice
last_updated: '2026-03-11'
status: active
authors:
  - bradyhau
  - Gemini 2.0 Flash (CLI)
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
archetype: brain
---

# KDD 2.0 實作現狀：三機協同與無頭開發架構

在 2026 年的 SafeChord 開發語境下，我們採用「三機協同」模型：利用 Gemini WebChat 進行高階決策，並配合雙軌 CLI 進行無頭化開發執行。

---

## 1. 三機協同模型 (The Three-Engine Model)

我們根據 AI 模型的特性與 Context 邊界，將開發任務劃分為三個層級：

| 角色 | 實體工具 | 核心職責 | 關注點 |
| :--- | :--- | :--- | :--- |
| **🏛️ 戰略決策中心 (Architect)** | **Gemini WebChat** | **設計與權衡**：定義技術堆疊、架構決策、分析長期 Trade-offs。 | 戰略 (Why/How) |
| **🛡️ 前瞻監督者 (Pioneer)** | **Claude Code** | **技術攻堅與解題**：處理未知技術 Spike、複雜邏輯除錯、突破邏輯死結。 | 戰術 (Spike) |
| **🧠 文件執行者 (Settler)** | **Gemini CLI (我)** | **迭代與沉澱**：日常功能開發、全域 Code Review、KDD 文檔逆向生成與維護。 | 執行 (Structure) |

---

## 2. 溝通介面與協議 (Communication Interface)

在無頭開發環境中，Agent 之間的資訊交換必須具備標準化的媒介。

### 🟢 基礎溝通：Git Commit Protocol
當不需要進行正式「換手 (Handoff)」的日常迭代時，**Git Commit Message** 是兩個 CLI (Claude/Gemini) 與人類之間唯一的溝通橋樑。
*   **原則**: Commit Message 必須包含「變更意圖」與「架構影響」。
*   **格式要求**: 採用 [Conventional Commits](https://www.conventionalcommits.org/)。
*   **Agent 義務**: Gemini CLI 在進行 Review 時，必須解讀上一個 Agent (如 Claude) 的 Commit Message，以理解當前代碼的變更背景。

### 🔴 強制換手：遺言機制 (The Legacy Handoff)
當任務過於複雜、發生邏輯死結、或需要進行跨 Agent 的深度技術移交時，必須啟動「遺言機制」。
*   **媒介**: `LOKI_DEBUG_SESSION.md` 或專案根目錄下的臨時 Markdown 檔案。
*   **內容必備**:
    1.  **環境狀態**: 目前打通到哪裡？哪些服務已啟動？
    2.  **已驗證路徑**: 哪些嘗試已證實可行？哪些是坑？
    3.  **待辦事項 (Next Action)**: 給下一個 Agent 的明確指令。
*   **觸發條件**: Gemini CLI 宣告失敗、Claude Code 完成 Spike、或人類強制要求中斷任務。

---

## 3. 螺旋式 KDD：從戰略到沉澱 (Workflow)

1.  **決策階段 (Strategic Design)**: 與 **Gemini WebChat** 討論架構，確認決策。
2.  **實驗階段 (Spike)**: 若涉及未知技術，啟動 **Claude Code** 進行開發先行。
3.  **同步階段 (Handoff/Commit)**: Claude 完成後，提交代碼並附上詳盡的 Commit Message (或 Legacy Note)。
4.  **定錨與沉澱 (Solidify)**: 由 **Gemini CLI** 讀取 Git 改動與溝通資訊，進行 Review 並將成果反向寫入 `Docs/` 的 Blueprint 中。

---

## 4. 無頭開發 (Headless) 協作守則

*   **Terminal 為唯一真實 (Single Source of Truth)**: 所有的開發與測試均在終端機完成。IDE 僅作為視覺化 Review 提示工具。
*   **Review 即文檔**: Gemini CLI 在 Review 通過後的同時，即具備「文檔撰寫者」的身分。
*   **信任海量記憶**: 充分利用 Gemini CLI 的 Context 窗口進行全專案影響分析，避免破壞 API 契約。

---

## 5. 附錄：操作模板 (Operational Templates)

為了確保 Agent 間的語意對齊，所有協作者必須遵循以下溝通規範：

### 🟢 Git Commit 模板 (Routine)
遵循 [Conventional Commits](https://www.conventionalcommits.org/) 與 [Git Trailers](https://git-scm.com/docs/git-interpret-trailers) 標準，確保 Settler (Gemini) 進行 Review 時具備足夠 Context，同時保持 Git Log 的專業整潔。

```text
<type>(<scope>): <subject> (50 chars max)

[敘述性內文: 為什麼需要這個變更？]
詳細說明本次變更的動機與邏輯。解釋「為什麼 (Why)」而非「怎麼做 (How)」，
並描述其對專案架構或長期決策的影響。

Context: [關聯的 Blueprint 路徑或 Issue ID]
Impact: [對架構、API 契約或基礎設施的具體影響]
Test: [執行了哪些測試驗證？ (e.g. make smoke-test)]
Agent: [執行此提交的 AI 代理人 (e.g. Gemini CLI, Claude Code)]
Legacy: [若有遺留問題，在此標註供下一個 Agent 處理]
```

### 🔴 Legacy Note 模板 (Handoff)
適用於跨 Agent 移交任務（存放在 `LOKI_DEBUG_SESSION.md` 或臨時 Markdown）。
```markdown
# 📝 Legacy Note: [任務名稱]
- **Status**: [已打通 / 部分完成 / 邏輯死結]
- **Environment**: [目前的部署狀態、關鍵環境變數]
- **Verified Path**: 
  - [x] 哪些嘗試已經證實可行？
  - [ ] 哪些是確認的坑 (Dead Ends)？
- **The Blockers**: 為什麼現在停下來？(報錯訊息、邏輯矛盾點)
- **Next Actions**: 
  1. [具體下一步指令]
  2. [需要更新的文檔路徑]
```

---

## 6. 戰略評價
這套架構讓人類架構師進化為 **「AI 資源調度員」**。透過標準化的溝通協議，我們建立了一個具備「自癒力」與「知識沉澱能力」的開發閉環。
