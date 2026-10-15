# KDD 2.0 實務：雙引擎開發模式

SafeChord 的開發跑在 **「雙引擎」** 模型上：開拓者席負責實作，維護者席負責審查與鞏固。

> **⚙️ 本文件正在調整期。** 雙引擎席位、票的生命週期、以及 §4 的範本都是 v0.4.0 才引入的，還沒跑完一個完整週期，會有粗糙的地方。
>
> **如果某個範本或步驟不合眼前的工作，請提出來，不要默默繞過去。** 文件與實際發生的事對不上，在被論證為其他情況之前都算文件的缺陷——跟人類提，然後在這裡修掉。
>
> **本告示還在的期間，不要遞增 `doc_version`。** 文件停在 v0.4.0 直到調整期結束，改動只反映在 `last_updated`。

SafeChord 使用 agent 的方式，依人類所在的位置分成幾種模式。§2 的協定與 §4 的範本所有模式共用；§1 的席位與 §3 的流程只屬於開發模式，止於合併與關票。

| 模式 | 人類的位置 | agent 怎麼運作 | 定義在 |
| :--- | :--- | :--- | :--- |
| 討論 | 全程參與，一起做決定 | 單一 agent 與人類對談；產出是票、設計草稿，或對 `Docs/` 的修改 | 本文件 §2 |
| 開發 | 最後的守門員，合併前看一次 | 兩個席位互相制衡 | 本文件 §1、§3 |
| 發版 | 全程參與，每個 gate 簽核 | 單一 agent 與人類協作 | [發版流程](safechord.safezone.delivery.workflow.md) |
| live 維運 | 未定 | 未定 | — |

---

## 1. 雙引擎模型

| 角色 | 能力要求 | 當前載體 | 核心職責 |
| :--- | :--- | :--- | :--- |
| **🛡️ 開拓者** | 實作能力及格、價格性價比高、反應時間快；錯誤由測試攔截 | opencode（headless），經由 OpenRouter · **GPT-6 Luna / high effort** | **實作與問題解決**：程式碼、初步除錯。 |
| **🧠 維護者** | 完整理解力、長流程處理、審查能力優秀；錯誤由人類負責 | Claude Code · **Opus 5.5 / medium (or high) effort** | **文件管理與任務審核**：開票之前：與人類討論設計，修改藍圖並開票。開票之後：程式碼審查、測試規劃、文件對齊。|

**能力要求是契約，當前載體是實作細節。** 換掉載體，不要動席位。

**`Docs/` 屬於維護者。** 開拓者在那裡是唯讀。實作過程中發現的偏離，先把程式碼做完，並寫下偏離原因交給維護者審核。

**席位綁定在 session 上。** 一個 session 持一個席位，持到結束。換席位就是換 session，用交接把 context 帶過去。因此程式碼審查不會跟它所審查的實作共用 session——寫程式碼的那個 session 持開拓者，而審查是維護者的事。

**維護者 session 可以啟動開拓者 session。** 開拓者 session 從空的 context 開始，只拿到票與 handoff；兩者之間的溝通仍然只有[交接協定](#-交接協定)為各個方向列出的那些。透過其他途徑向啟動它的 session 回報的執行者，例如 subagent，算在那個 session 的席位底下，自己不持席位。

**例外：維護者能單 session 完成任務。** 人類與維護者討論後，可以讓該輪任務只由維護者執行，票掛上 `exec:settler` label。詳細說明見 [§3.3](#33-選擇執行者)。

---

## 2. 溝通介面與協定

標準化的協定負責在代理之間、以及跨 session 傳遞資訊。

### 🎫 票（Ticket）
票是任何實作的開頭，是後續追蹤時做起點的依據。

*   **媒介**: 工作所在 repository 的 GitHub issue。
*   **目的**: 作為實作依據, 補的是 commit（太細）與專案文件（只有終態）都漏掉的那層粒度。
*   **份量**: 票幾乎是永久的，所以只放對日後讀者有追溯價值的內容：問題、決策與理由、範圍、Done When。只為這次任務對齊席位用的 context（推測的機制、調查細節、設計建議、未驗證項目、實作順序）放進 handoff。完成條件只寫合併前驗得了的；部署後才驗得了的，歸[發版流程](safechord.safezone.delivery.workflow.md)的 gate。
*   **完成條件寫意圖，不寫形狀**: 寫結果必須成立的事（「logger 的輸出除了 `worker_id` 之外都不變」、「沒有任何 assertion 或測試輸入被改動」），不寫 diff 或名稱長什麼樣（「欄位名稱不變」、「diff 只動到 import」）。寫成形狀的條件，錯的改動照樣過、對的改動反而不過，而且範圍一允許改名，就跟範圍自相矛盾。
*   **時效**: 開票之後過了一段時間才動工的票，動工前要對照當下的藍圖與程式碼再核對一次。指向已經改寫的章節的引用、被後來的票改掉的「現況」，先在票上改正。
*   **分支**: `<type>/issue-<issue_no>-<slug>`，`<type>` 是這次改動的 commit type。`refactor/` 前綴保留給掛著 `mode:refactor` label 的票，這個 label 由人類與維護者在開票時約定：這個前綴會打開 agent 的 refactor mode，在這個模式下結構完整優先於最小 diff，範圍照樣有約束力。沒有掛這個 label 的 `type:refactor` 票，分支用 `chore/`。
*   **必要內容**: [參考範本](#-github-issue-範本)

### 🟢 基本溝通：Git Commit 協定
*   **媒介**: git
*   **目的**: 在實作過程中的細粒資訊載體。
*   **格式**: 嚴格遵循 [Conventional Commits](https://www.conventionalcommits.org/)。
*   **必要內容**: [參考範本](#-git-commit-範本)

### 🔴 交接協定
*   **媒介**: 存放在 `.ai-session-handoffs/` 的 Markdown 檔案。
*   **目的**: 跨 ai 工具 session 的載體。交接對象包含下一個 session，或另一個代理。
*   **觸發條件舉例**:
    - 開拓者完成一個 Spike 或開發階段。
    - 代理遇到其操作範圍外的錯誤。
    - 人類介入要求任務移交(通常是 Context 已經長到開始劣化)。
*   **席位之間的交接**: 一張票的來回最多三個檔，每個檔只有一個作者。
    - `kickoff`（維護者 → 開拓者，開工）：開工的依據是票；維護者判斷光靠票 context 不夠時才寫，寫一次。裡面註明維護者已經完成的完成條件，開拓者就不必重做，也不必再提出來。
    - `delivery`（開拓者 → 維護者，交付）：描述分支的現況。每一輪交付都原地更新，不另開新檔；已經處理掉的內容直接刪除，舊的狀態留在 harness 的 git history。表頭記下這是第幾輪、描述的是哪個 commit。
    - `review`（維護者 → 開拓者，審查）：每一輪審查在同一個檔追加一節（`## Round N`），前面的輪次不改寫也不刪除，讓每一輪的發現有沒有收窄看得出來。每個發現有固定編號（`R<輪>-<序>`），Blocking 的發現另外標上成因；每一輪開頭結算先前還開著的發現，所以開拓者只需要讀最新一輪。每一輪結尾記下涵蓋範圍：維護者跑了什麼、做了哪些實驗、哪些沒查，讓「發現少」與「看得少」分得出來。
*   **生命週期**: handoff 跟著任務走。PR merge、票關閉、reconciliation 落進 `Docs/` 之後就刪除；harness 的 git history 會留著，需要時可以找回。
*   **連結方向**: handoff 指向票，票不反指。看得到 handoff 的人一定找得到票，看得到票的人卻不一定看得到 handoff；而且 handoff 刪除後，永久的票上會留下一條死連結。
*   **命名規則**: 有對應的票時，handoff 檔名帶上小寫的 `<repo>-<issue_no>`（例如 `2026-09-19-safezone-64-worker-offset-commit.md`）。席位之間交接的三種檔再以種類結尾：`-kickoff`、`-delivery`、`-review`（例如 `2026-09-19-safezone-64-worker-offset-commit-review.md`）。
*   **叫回 session**: 因里程碑、卡關或人類移交而交接的 session，可以用筆記裡的 `Resume:` 指令叫回來，例如修正審查發現的問題。因 Context 劣化而交接的 session 就此退休，不再叫回。
*   **必要內容**: [參考範本](#-handoff-範本)

### 🟣 Pull Request
*   **媒介**: 工作所在 repository 的 GitHub PR。
*   **目的**: 給人類審核與合併的介面。迭代期間兩個席位只靠分支與 handoff 來回，不開 PR。
*   **時機**: 審查通過後，由維護者撰寫並開出。`exec:settler` 的任務在實作完成後開出，另見 [§3.3](#33-選擇執行者)。
*   **必要內容**: 目前不設範本，寫法與結構由維護者依該次工作決定，累積幾份之後再歸納。只有下面兩段，有內容時必須各自成段：
    - **審查中的決定**：審查來回期間做了、而人類沒看到的決定。
    - **衍生問題**：從這張票切出去的新票，見 [§3.2](#32-處理審查發現的問題)。

### ⚪ 設計草稿
*   **媒介**: 存放在 `.ai-session-drafts/<domain>/` 的 Markdown 檔案。
*   **目的**: 在任何不直接影響 codebase 的前瞻討論須要有延續時，通常出現在開票之前。
*   **domain 分類**：
    - `kdd/`（practice、seat、審查流程）
    - `delivery/`（release workflow、gate、soak）
    - `platform/`（網路、ingress、安全、可觀測性）
    - `app/`（SafeZone 程式的 debug 與改進）。
*   **必要內容**: [參考範本](#-draft-範本)

---

## 3. 雙軌工作流程：KDD 的平衡

SafeChord 採用基於標籤的 **雙軌工作流程**，以平衡「文件優先」的嚴謹性與「Spike 優先」的靈活性。

### 3.1 選擇路徑

兩條路徑**不是**用「動工前規劃了多少」來分的。分界只有一個問題，而且開票當下就答得出來：

> **`Docs/` 裡已經有這塊的藍圖了嗎？**

這個答案決定了文件對齊**是什麼**——一次查核，還是一次著作。

| 路徑 | 動工前有藍圖 | 文件對齊是 |
| :--- | :--- | :--- |
| `kdd:forward` | 有 | **查核**——確認程式符合規格；有偏差則修規格 |
| `kdd:spike` | 沒有 | **著作**——與人類討論後，視需要把結果寫回成一個新的 SSOT 節點 |

標籤告訴開拓者該往哪看：`kdd:forward` → 先讀藍圖，照著實作；`kdd:spike` → 別去 `Docs/` 翻，翻了也是空的。

票由維護者開立並貼標籤，人類視需要調整。

### 🟢 路徑 A：`kdd:forward`（有序模式）
應用於現有模組的最佳化與已知架構的延伸。
**規則**: 「先文件後程式碼」——沒有更新後的藍圖，不得進行實作。

1.  **策略設計**（維護者）: 
    1. 與人類討論並定義「Why/What」
    2. 更新藍圖的「需求」（列出測試必須守住之承諾的段落），把藍圖的 `app_version` 設成該票所在的 milestone
    3. 與人類討論決策是否寫入決策日誌，要寫入就將決定與理由追加到決策日誌
    4. 然後**開票並標記 `kdd:forward`**
    5. 接著從 `dev` 開出該票的分支，把守住變動需求的測試 commit 在上面，每個測試帶上對應的需求 ID，commit 帶 trailer `Agent: Settler (requirement test)`。寫法見[下方](#撰寫需求測試)
    6. 若有需要，撰寫 kickoff handoff
2.  **實作**（開拓者）: 當維護者完成需求的測試提交並換手
    1. 讀取文件包含票、藍圖、handoff(若存在)
    2. 在同一個分支上實作能通過這些測試的程式碼
    3. 視需要補上自己的測試，以確保開發遵循 TDD 
    4. 實作完成後 push 分支、不開 PR，並產生 handoff 筆記
3.  **審查**（維護者）: 當開拓者實作完成
    1. 讀取開拓者的 handoff，根據藍圖定義進行程式碼審查。派遣與審查的做法、何時該停，見 `pioneer-dispatch` skill（`.claude/skills/pioneer-dispatch/SKILL.md`）
    2. 若有審查意見退回實作，詳情參考 [§3.2](#32-處理審查發現的問題)。
    3. 審查通過則撰寫 PR
    4. 若 PR 觸發的 CI 沒有通過，退回審查；通過後等待人類審核合併
4.  **鞏固**（維護者）: 當 PR 被人類合併。
    1. 如果程式實作跟藍圖有被審核過的偏差，對齊到藍圖當中
    2. 刪除過程中產生的 handoff 文件
    3. 把 repo 的 checkout 切回 `dev` 並更新，刪掉該票的本地分支與 run 目錄（`.ai-runs/<repo>-<issue_no>/`，有的話）。遠端分支在合併時已自動刪除
    4. 關閉票

**沒有改動任何需求的票**（純文件，或行為不變的重構）跳過步驟 1 的第 2、5 小步，文件對齊就是確認藍圖的措辭仍然相符。如果改動還是逼得需求測試要跟著改，例如搬移造成的改名，那個改動依 [§3.2](#32-處理審查發現的問題) 的規則自成一個 commit，assertion 與輸入維持原樣。

#### 撰寫需求測試

維護者在任何人選定機制之前就寫好需求測試，所以測試只守得住維護者想得到的情況。下面這幾項檢查，補的是先前的票掉進去過的洞：

1. **替身的失敗方式跟真的依賴一樣。** 用真的依賴重現很便宜的時候（例如容器裡的資料庫或 broker），先重現，再照重現的結果做替身。否則逐一考慮失敗可能的形狀：呼叫拋錯、連線被拒、呼叫被接受卻一直不回應、回錯誤 status、一筆壞資料讓整批被拒。
2. **測試資料的形狀跟真實系統一樣。** 正式環境裡跨事件共用的值（例如請求的 trace ID），在測試裡也要共用；對照合約與服務標準檢查。
3. **前置條件不假設機制。** GIVEN 不依賴實作可以自由選擇的 buffer、批次邊界或順序。
4. **證明每個測試會紅也會綠。** 只因為被守的東西還不存在而紅，兩件事都沒證明：做一次 mutation 證明測試會咬；需求有設上限的，證明一個符合上限的 stub 能讓測試轉綠。
5. **先找出呼叫到這張票要改的程式碼的地方。** 在需求測試裡搜尋這張票會改的函式與 package。呼叫到的需求測試在同一個 commit 裡改好，並在 kickoff 寫明這樣就定下了新的簽名。

**兩種測試分屬兩個席位。** 需求測試寫的是系統其他部分依賴的承諾，歸維護者：開拓者不修改、不放寬、不刪除 (但是可以提交意見給維護者審核)。其餘的測試是工程層面的，歸開拓者：它隨實作的需要新增、修改、汰換，並在交接筆記列出新增了哪些測試、改了哪些既有測試，以及為什麼。審查時如果發現開拓者的某個測試守著系統其他部分依賴的承諾，維護者可以把它升級：維護者把這條需求加進藍圖、給測試加上需求 ID，並用 trailer `Agent: Settler (requirement test)` commit。從此這個測試歸維護者。

**有些問題這張票裡改不動。** 開拓者不修改也不開立票：它在交接給維護者的 handoff，寫明發現了什麼、為什麼，然後繼續做其他部分。

### 🔴 路徑 B：`kdd:spike`（前線模式）
應用於新技術整合、未知錯誤修正或效能壓力測試。
**規則**: 「先程式碼後文件」——原型開發優先於文件。

1.  **策略設計**（維護者）: 
    1. 與人類討論並定義「Why/What」
    2. 然後**開票並標記 `kdd:spike`**，並且若有需要撰寫 kickoff handoff 
    3. 接著從 `dev` 開出該票的分支。
2.  **Spike**（開拓者）: 當維護者開出分支並換手
    1. 讀取文件包含票、handoff(若存在)
    2. 遵循 TDD 原則開發程式碼。例外是範圍明寫不加測試碼的票，因為沒有任何測試守得住的東西；這種票的完成條件要寫出驗證用的指令。這件事由人類與維護者在開票時約定
    3. 實作完成後 push 分支、不開 PR，並產生 handoff 筆記
3.  **審查**（維護者）: 當開拓者實作完成
    1. 讀取開拓者的 handoff，根據票的範圍與完成條件進行程式碼審查。派遣與審查的做法、何時該停，見 `pioneer-dispatch` skill（`.claude/skills/pioneer-dispatch/SKILL.md`）
    2. 若有審查意見退回實作，詳情參考 [§3.2](#32-處理審查發現的問題)。
    3. 審查通過則撰寫 PR
    4. 若 PR 觸發的 CI 沒有通過，退回審查；若 CI 不存在該輪開發元件，與人類討論是否有 CI 需求，有需求就開新票處理，並逕行後續流程。通過後等待人類審核合併
4.  **鞏固**（維護者）: 當 PR 被人類合併。
    1. 與人類討論是否有文件固化的需求，存在的話撰寫該輪開發對應類型的文件
    2. 刪除過程中產生的 handoff 文件
    3. 把 repo 的 checkout 切回 `dev` 並更新，刪掉該票的本地分支與 run 目錄（`.ai-runs/<repo>-<issue_no>/`，有的話）。遠端分支在合併時已自動刪除
    4. 關閉票

### 3.2 處理審查發現的問題

審查時，測試的 diff 與程式的 diff 分開讀。為了讓測試通過而修改測試，是第一個要追問的地方。

**發現的問題以 handoff 退回開拓者修**（見[交接協定](#-交接協定)）。

**需求測試跟藍圖需求對不上。** 有以下兩種狀況：

1. 測試撰寫有問題
    1. 測試太鬆：由維護者加嚴
    2. 測試太嚴：由維護者放鬆，需要特別檢查是否仍在藍圖需求內

    維護者遵守下列規則自行提交，再交還給開拓者過測試：

    1. 每次改動自成一個 commit
    2. 帶 trailer `Agent: Settler (requirement test)`
    3. body 寫明理由
2. 藍圖有問題：中斷目前任務，要求人類對於目前狀況作出判斷

**是一個還沒做的決定，或超出本票範圍的工作。** 不論是維護者審查時發現，還是來自開拓者的 handoff，都由維護者開新票。連結寫兩處：新票的背景指回原票，讓日後讀新票的人知道它從哪來；PR 用一個獨立章節列出這些衍生的票，讓人類合併前看一眼。PR 主體不需要描述這些問題。

**例外：不影響行為的修正。** 如果修正只動到註解或文件，不可能改變程式的行為，維護者直接 commit。不確定的話，問人類。這個 commit：

1.  自成一個，不併入開拓者的 commit；
2.  帶 trailer `Agent: Settler (review fix)`；
3.  在 `Impact:` 寫明為什麼這個修改不影響行為，讓人用讀的就能稽核。

### 3.3 選擇執行者

§3.1 決定任務的形式 **是什麼**。另一個問題決定**誰來執行**：

**絕大多數時候，我們都應該採用席位分離**，但是有時候會例外發生，可能因為：

1. 人類或維護者能提前判斷，開拓者因種種原因無法完成任務，包括但不限於
    1. 任務涵蓋範圍過大
    2. 開拓者無法操作驗證工具
    3. 開拓者被認為能力一定不夠
2. 這是一個純腦力但輕實作的任務，舉例來說，討論完只需要加少數幾行程式碼的工作

但是這些條件都不是必然，人類跟維護者應該根據當下狀況討論判斷要不要這樣處理。

**標記與流程。** 決定由維護者執行的票掛上 `exec:settler` label，可以跟 `kdd:forward` 或 `kdd:spike` 並存。流程沿用 [§3.1](#31-選擇路徑) 的路徑，只是實作者換成維護者：席位之間的 handoff 與步驟 3 的審查省略，實作完成後直接開 PR，由人類審查。執行中碰到的票外工作，照樣依 [§3.2](#32-處理審查發現的問題) 開新票，列在 PR 裡。

**審查責任。** 分離席位是為了讓做事的 session 不審查自己的成果。在 `exec:settler` 下這個獨立性不存在了，所以由人類明確接手審查並承擔責任。

**PR 特殊標籤。** 維護者開 PR 時掛上 `review:human` label，並在開頭放這段警語：

```markdown
> ⚠️ **Executed by the Settler.** No independent agent review took place; the executor and
> reviewer are the same seat. The human reviewer is the only independent check, and merging
> transfers accountability to them.
```

**PR 要多寫的一節。** 沒有 review 檔，就沒有別的地方記下哪些沒查過，而人類是唯一的審查者。所以 PR 要有 **Not checked** 一節，列出維護者沒驗證的路徑、條件與指令。

**合併就是簽核。** 人類審查完後合併，合併本身就把責任轉移給人類。任何 agent 都不合併 `exec:settler` 的 PR。

---

## 4. 操作範本（附錄）

### 🎫 GitHub Issue 範本
```markdown
## 背景
[為什麼需要這件事？現況是什麼？]

## 範圍
- 包含: [這張票要動到的東西]
- 不包含: [明確排除的部分]

## 完成條件
- [ ] [可驗證的條件 1]
- [ ] [可驗證的條件 2]
- [ ] 文件對齊完成（`kdd:spike`：或與人類確認不需要）

## 參考
- Blueprint: [`kdd:forward` 才有，連結至 Docs/ 對應文件]
```

文件對齊那一條是唯一在合併後才勾的完成條件：它是流程的最後一步，不是 PR 能證明的條件。

### 🟢 Git Commit 範本
```text
<type>(<scope>): <subject> (最多50字)

[Body: 為何需要這項變更？]
說明動機與邏輯。專注於「Why」而非「How」。
描述對專案架構或長期決策的影響。

Context: [票號，或連結至藍圖]
Impact: [對 API 合約或基礎設施的具體影響]
Test: [執行的驗證方式] (例如：make test-data-ingestor)
Agent: [開拓者 / 維護者 / 維護者 (review fix) / 維護者 (requirement test)]
Legacy: [留待下一個代理處理的待辦事項]
```

### 🔴 Handoff 範本
```markdown
# 📝 Legacy Note: [Task Name]

> **Date**: YYYY-MM-DD
> **From**: [Seat] / [Carrier] / [session id]
> **Resume**: [command that resumes this session in its tool]
> **To**: [Seat] / [new session, or blank if not yet known]
> **Trigger**: [Reactive: milestone | blocked | human handover] or [Deliberate: context degradation]
> **Ticket**: [<repo>-<issue_no>，例如 safezone-64；沒有就留空]
> **Branch**: [Branch Name]
> **Action Required**: [Brief summary]

---

## Status / Summary
[Complete / Partially Complete / Deadlock]

## What Changed
[Structural changes or architectural adjustments]

## Verified Path (Optional)
- [x] What has been proven feasible?
- [ ] Known dead ends or blockers?

## Unverified / Uncertain
- [ ] What was assumed but never checked?
- [ ] What is the author unsure of?

## Next Actions
1. [Specific Instruction 1]
2. [Specific Instruction 2]
```

席位之間交接的 `kickoff` 直接用上面的範本。`delivery` 與 `review` 有下列差異。

**`delivery`**（開拓者，每輪原地更新）：用上面的範本，表頭多兩行，內文多兩節。

```markdown
> **Round**: [N, counted from 1]
> **Head**: [the commit this note describes]

## Response to Review
[From round 2 on. One line per finding still open in the latest review round.]
- R1-1: [how it was fixed, or why you disagree]

## Raised for the Settler
- [A problem that cannot be fixed inside this ticket: what was found, and why]
- [An objection to a requirement test]
```

**`review`**（維護者，每輪追加）：

```markdown
# 📝 Review: [Task Name]

> **From**: Settler / [Carrier] / [session id]
> **Resume**: [command that resumes this session in its tool]
> **To**: Pioneer / [session id]
> **Ticket**: [<repo>-<issue_no>]
> **Branch**: [Branch Name]

---

## Round 1 — reviewed [commit]
**Verdict**: [Returned / Passed]

### Findings
- **R1-1** [Blocking] [impl / boundary / kickoff] [what is wrong, where, how to reproduce it]
- **R1-2** [Minor] [...]

### Coverage
- Ran: [the tests the Settler ran itself, and their result]
- Probed: [each throwaway experiment: what it varied, what it showed]
- Not checked: [the paths, conditions and files this round did not examine]

## Round 2 — reviewed [commit]
**Verdict**: [Returned / Passed]

### Earlier findings
- R1-1: Resolved
- R1-2: Open — [what is still missing]

### Findings
- **R2-1** [Blocking] [impl / boundary / kickoff] [...]

### Coverage
- [...]
```

每個 Blocking 的發現都標上成因，可以不只一個：

| 成因 | 意思 |
| :--- | :--- |
| `impl` | 邊界內的錯：票、藍圖或需求測試已經說了什麼是對的，實作沒做到 |
| `boundary` | 邊界移動：這個情境在開工前沒有人想到 |
| `kickoff` | 追溯到維護者交出去的東西：票、kickoff，或某個需求測試 |

成因記的是這一輪從哪裡來，之後才能按成因比較不同的票，不只是數輪數。

### ⚪ Draft 範本
```markdown
---
title: 'Design Draft: [Topic]'
doc_id: safechord.draft.[slug]
last_updated: 'YYYY-MM-DD'
status: draft
authors: [bradyhau, <agent>]
context_scope: [Methodology | Infrastructure | ...]
summary: [一段話說明這份草稿在決定什麼]
logical_path: SafeChord.Draft.[Name]
related_docs: []
archetype: script
doc_version: 0.1.0
---

# Design Draft: [Topic]

## 1. Background
[問題是什麼？有哪些約束？]

## 2. Proposed Solution
[提案內容，含必要的 mock code / schema]

## 3. Alternatives Considered
[還考慮過什麼？為什麼落選？]

## 4. Trade-offs
[接受了什麼代價？]

## 5. Next Steps
1. [ ] [下一步]
```