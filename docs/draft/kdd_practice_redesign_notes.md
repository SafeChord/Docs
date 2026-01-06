# Draft: KDD Practice 流程重構隨筆 (Redesign Notes)

**最後更新日期**：2026-01-04
**狀態**：待實戰驗證 (Pending Validation)

## 🎯 重構核心目標
將目前的 `safechord.kdd.practice.md` 與新建立的 **Meta Standard (Taxonomy)** 及 **Templates** 體系進行掛鉤，並強化「實作後回饋」的閉環機制。

---

## 🔍 關鍵觀察點 (Key Observations)

### 1. 語意對齊 (Archetype Alignment)
*   **現狀**：舊流程使用模糊的 "Spec" 或 "Docs" 描述。
*   **優化方向**：未來 SOP 應明確指示 Builder 根據任務屬性選擇 `Blueprint` (改動介面)、`Script` (改動流程) 或 `Brain` (改動設計)。

### 2. 閉環校準 (The Reconciliation Loop)
*   **痛點**：Coder (Cline) 在寫代碼時常會發現 Blueprint 定義的不合理處，若此時直接改 Code 卻沒回頭改文件，KDD 就會崩潰。
*   **待驗證機制**：
    *   **"Doc-First" 修正**：是否強制要求先暫停 Code 改動，回頭更新 Blueprint 並同步 Version？
    *   **"Final Audit"**：任務結束前，Builder 是否應自動 Diff 程式碼註釋與 Blueprint 規格的一致性？

### 3. 自動化與人為介入的邊界 (Human-in-the-Loop)
*   **手動操作點**：目前由人類扮演 Orchestrator 傳遞 Context。需觀察哪些「傳遞」動作最枯燥，未來可透過腳本自動化。
*   **決策點**：當文件與程式碼發生衝突時，決策權歸屬於 Architect。

---

## 🏗️ 建議的實踐流程 (Proposed Workflow to be tested)

1.  **Discovery (Map)**: 透過 `archetype: map` 文件定位受影響的子系統。
2.  **Design/Update (Blueprint/Brain)**: 使用 `templates/` 下的對應原型更新規格，並利用 `code_paths` 指向實作目錄。
3.  **Implementation (Coder)**: Coder 讀取更新後的 Blueprint 進行開發。
4.  **Sync (Reconciliation)**: 若開發中規格有變，**Builder 必須同步修正 Blueprint**。
5.  **Finalize (Meta)**: 更新 `CHANGELOG.md` 並確保 `archetype` 標記正確。

---

## 🧪 待驗證清單 (Validation Checklist)
*   [ ] `code_paths` 指向根目錄是否真的讓 AI 更容易定位檔案？
*   [ ] 移除 Env 列表改用連結，AI 讀取時是否會產生斷層？
*   [ ] Map 原型是否能有效降低進入新模組時的認知負擔？
