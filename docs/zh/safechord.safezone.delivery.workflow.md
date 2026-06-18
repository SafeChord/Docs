---
title: 'Script: SafeZone 統一交付工作流程'
doc_id: safechord.safezone.workflow.delivery
doc_version: 0.3.6
app_version: 0.3.6
last_updated: '2026-06-18'
status: active
authors:
  - bradyhau
  - Claude Code
  - Gemini CLI
context_scope: SafeZone App & Deploy Repos
summary: 定義涵蓋 SafeZone (App) 與 SafeZone-Deploy (Deploy) 儲存庫的端到端統一交付管線，採用混合式 GitOps + IssueOps 推廣模型與解耦版號規則。
keywords:
  - CI/CD
  - GitOps
  - IssueOps
  - 管線
  - 提升
logical_path: SafeChord.SafeZone.Workflow.Delivery
related_docs:
  - safechord.safezone.md
  - safechord.safezone.deployment.md
  - safechord.environment.md
parent_doc: safechord.safezone
archetype: script
code_paths:
  - SafeZone/.github/workflows
  - SafeZone-Deploy
---

# SafeChord 統一交付工作流程（App + Deploy）

> **狀態**：正式版本（canonical）。取代 `delivery-workflow-final.md` 並已對齊至 `Docs/`。
> **範圍**：端到端交付，涵蓋 `SafeZone`（App）與 `SafeZone-Deploy`（Deploy）。
> **運行測試**：`v0.3.6` 已出貨並提升至 staging（自 2026-06-15 起 soaking），採用先前的 **4 階段原地**模型。
> **A–E 重構**（5 階段、teardown-rebuild staging、frozen-pin 切版、無 promote branch）**尚未按文件實際執行** — 請參閱 §9。
> **決策負責人**：bradyhau（架構師）· **作者**：Claude Code（開拓者）。流程與回覆由 Gemini（維護者）審查。

---

**第一部分 — 流程**（你要做的事）

## 1. Repos、branches、tags 與 IssueOps 接觸點

**App `SafeZone` — GitFlow**
| Branch | 角色 / 動作 |
| :- | :- |
| `feature/*` | 功能開發（本機） |
| `dev` | 整合主幹 — CI 關卡（**GATE 1**）+ `publish-dev` 推送 `0.X.Y-<sha>` |
| `release/*` | **發行版切版 — frozen pin**（在經過驗證的 sha 上切版；PR → `main`；不得新增 commits） |
| `hotfix/*` | 緊急修復 — **流程待定**（目前：經由正常流程進行 forward-fix） |
| `main` | 生產主幹 — tag `v*.*.*` → `release.yml` 進行提升 |

**Deploy `SafeZone-Deploy` — 3 分支（Actions 驅動的提升 + GitOps）**
| Branch | 階段 | ArgoCD |
| :- | :- | :- |
| `preview/<ver>` | dev 與叢集內的驗證（臨時；每週期從 `staging` 重新切版） | 自動同步，`targetRevision=preview/<ver>` |
| `staging` | soaking + 持續的展示環境 | 自動同步，`targetRevision=staging` |
| `main` | 黃金設定歸檔（完整 repo 快照；不從此處同步） | — |

**Tags**：`0.X.Y-<sha>`（dev / preview）· `0.X.Y`（正式版，crane）· `v0.X.Y`（git）· `v0.X.Y-staging`（救援基準線）。
> `v*-staging` **永遠不刪除**；回滾的*資格*由樓層（floor）管理（§8），而非靠移除 tag 來控制。

**IssueOps 接觸點**（deploy repo）：`freight: 0.X.Y-<sha>`（preview 佇列 → 獲得 `validated` 標籤）→ `release: v0.X.Y`（staging / 歸檔佇列）。

## 2. Pipeline — Phase A–E

### Phase A — App 整合（`SafeZone`）
- **A1.** 開啟週期：在 `dev` 上提交 `chore(release): open v0.X.Y`（更新 `VERSION`）。
- **A2.** PR → `dev`；CI 關卡（`make ci-all` + `make smoke-test`）= **GATE 1**。
- **A3.** Merge → `publish-dev` 推送 `0.X.Y-<sha>` **並在 deploy repo 中開啟** `freight: 0.X.Y-<sha>` issue。

### Phase B — Preview 驗證（`SafeZone-Deploy`）
- **B1.** 接起 `freight: 0.X.Y-<sha>` issue。
- **B2.** 為 `0.X.Y-<sha>` 撰寫 `preview/0.X.Y` 設定（架構 + image tag）→ **推送該分支**。
- **B3.** `SETUP_INFRA` — 啟動 preview 基礎設施。
- **B4.** 執行 `init-deploy.yml`（env=preview）→ 在 freight issue 上張貼自動化檢查清單。
- **B5.** 執行 `/validate-freight`。
- **B6.** 人員簽核（UI 回應 + 外部連通性）。
- **B7.** 簽核後 → 蓋上 `validated` 標籤。
- **B8.** 卸除 preview — **先卸 app，再卸 infra**（`scripts/ops/preview/`）。

### Phase C — 切發行版（`SafeZone`，僅在 `validated` 之後）
- **C1.** 確認 freight issue 帶有 `validated` 標籤。
- **C2.** PR `release/0.X.Y`（frozen pin — 不得新增 commits）→ `main`（**merge，非 squash**）+ 標記 `v0.X.Y`。
- **C3.** 該 tag 觸發 `release.yml` → 它在 deploy repo 中開啟 `release: v0.X.Y` issue。

### Phase D — Staging 部署 + Soak（`SafeZone-Deploy`）
- **D1.** 卸除 staging — app + infra（保留外部 / 平台服務）。🟡
- **D2.** 直接 **merge** `preview/0.X.Y` → `staging`（無 promote branch，無 PR）。
- **D3.** 在 `staging`（直接 commits）上：設定 `values-staging` 的 image tag 為正確的目標 `appVersion`（若 App 版本有變更；否則維持 tag 不變）+ 修正環境差異。
- **D4.** `SETUP_INFRA` — 啟動 staging 基礎設施。
- **D5.** 執行 `init-deploy.yml`（env=staging）。
- **D6.** 執行 `/validate-release`。🟡
- **D7.** 人員驗證（UI + 外部連通性）。
- **D8.** 成功後 → 在 `release: v0.X.Y` issue 上確認檢查清單。
- **D9.** 開始 soak（3–5 天）。

### Phase E — 歸檔（`SafeZone-Deploy`）
- **E1.** 執行 `/validate-soak`。🟡
- **E2.** 確認所有 `release: v0.X.Y` 檢查清單項目已完成。
- **E3.** 在 `staging` 上標記 `v0.X.Y-staging` + PR `staging` → `main`（歸檔）。
- **E4.** 關閉 `release: v0.X.Y` issue。

## 3. 例外情況與迭代（偏離快樂路徑）
- **Preview 修正迴圈**：需要修正 → 回到 **A**（新的 `0.X.Y-<sha>`），重新指向 preview，重新驗證。**Tags 不動。**
- **發行版復原**：`main^2` 解決了一個未驗證的 sha → 透過 `workflow_dispatch source_sha=<validated>` 重新執行 `release.yml`。
- **Staging 救援**：線上故障 → 將 ArgoCD `targetRevision` 固定到最後一個好的 `v*-staging`（≥ 樓層）→ forward-fix → 解除固定。*（§8；從未實際執行過。）*
- **快速路徑**：若變更*確實不穿過*部署邊界 → GATE 1 可能就足夠。
- **部署層設定 Hotfix（Staging/Showcase 重新進入）**：如果修正僅涉及環境設定或 values 調整（於 soak/showcase 期間）：
  1. **目標環境路由檢查清單**：
     - *路由 A：必須回到 Preview（GATE 2）*：如果變更修改了 App 程式碼（需要新 image）、資料庫 Schema/DDL 腳本（`safezone-ops-schema`），或 Ingress/網路/安全邊界設定。
     - *路由 B：直接 Staging 修補*：如果是純設定/values 修改，或 staging 專用元件（如 `scheduler` CronJob），且不觸及 App 程式碼、DB schema 或 ingress 閘道。
  2. **稽核 Ticket**：
     - 若在 active soak 期間發現：直接追蹤於既有的開放 `release: v0.X.Y` issue 上。
     - 若在 Showcase 期間發現：追蹤於新的自發設定 issue（例如 `Deploy #12`）。
  3. **限定範圍的重新 Soak（N-Cycles 規則）**：
     - 不重設 3 天的穩定性 soak 計時器。建立一個較短的觀察期，由元件的執行頻率客觀決定：
       - *排程任務*：涵蓋至少 2 個完整的執行週期（N=2），以驗證觸發正確性與冪等性（例如，對於每日排程器為 **48 小時 / 2 天**）。
       - *持續服務*：涵蓋 **6 到 12 小時**，以驗證穩定狀態的資源與記憶體輪廓。
     - 透過 `/validate-soak`（自動化資料新鮮度不變量檢查）驗證。若通過，在 `staging` 上標記 `v0.X.Y-staging`，並 PR staging 至 `main`（歸檔）標記 `v0.X.Y`。

---

**第二部分 — 原理**（為什麼這樣設計）

## 4. 核心原則
1. **Tag 是認證，不是檢查點** — 在變更所觸及的最高風險環境變綠後才切版，絕非「我編輯完了」的標記。
2. **Soak / 真實流量是發行後監控，絕非預先標記的閘門** — 先標記 → 部署 → *然後* soak；soak 失敗 → forward-fix。
3. **閘門與風險成比例** — app 層級變更 → compose + CI（**GATE 1**）；邊界層級變更 → 在叢集中 preview（**GATE 2**，包含真實的瀏覽器測試 + 對 UI 發行版的外部 DNS 探測）。
4. **僅 forward-fix；tags 是不可變的** — 絕不重新標記，絕不取消標記。一個 snapshot 只能在*其平台世代內*作為有效的回滾目標（§8）。
5. **透過雙指標解耦版本** — App 與 Deploy 版本號獨立漂移。App 發行版追蹤功能變更；Deploy 發行版追蹤環境/合約變更。它們透過 Helm chart 中的 `version`（Deploy 設定）與 `appVersion`（App 程式碼）進行對應。
6. **一切都經過 preview 閘門；`hotfix/*` 不得繞過它** — 沒有生產 SLA（僅 showcase），因此沒有急迫性足以證明未經驗證就出貨。

## 5. 部署模型 — 混合式 + 先決條件
*這**不是**純 GitOps。兩半：一個命令式分支提升流程（GitHub Actions + PRs/tags）疊加在 GitOps 調和之上。*

- **ArgoCD 擁有穩定狀態的調和。** 每個 `deploy/<env>/app/*.yaml` 都是一個自動同步的 `Application`（`targetRevision` = 環境分支；`path` = `helm-charts/safezone-<layer>` + `values-<env>.yaml`）。Helm 在 **ArgoCD 內部**渲染，而非作為 CI 的前置步驟。
- **按層排序** — ArgoCD 的健康驅動 sync-waves 無法跨越 Application，也無法可靠地門控 Job：
  - **Infra** → ArgoCD 原生 **sync-waves**（`ApplicationSet`：基礎 `-2` → 安全 `1` → 工作負載 `2` → 初始化 `3`）。
  - **App** → **`init-deploy.yml`** 按順序套用 Application CR，並在階段之間以 rollout/Job 健康狀態進行門控（基礎 → seed-schema → 核心 → **3.5 smoke（硬性閘門）** → seed-cases → ui → scheduler[staging]）。這是一個分階段的*引導程式 + 閘門*，而非一個命令式部署器 — 一旦 CR 存在，ArgoCD 就會調和它。（參見 ADR-9。）
- **Staging 發行版部署 = teardown + rebuild**（非原地滾動更新）。在 0.x 階段，架構在各發行版之間仍可能有實質變化，因此原地路徑需要承載每個發行版的持久資料/遷移邏輯，這不划算；完整重建是**確定性的**且**在 10 分鐘內恢復**。零停機滾動替換是**產品階段的目標**，已推遲。
- **Staging hotfix（僅 deploy 層）不需要 teardown/rebuild**，除非需要資料庫 schema 或狀態重置；純設定變更由 ArgoCD 原地調和，以維持 showcase 正常運行時間。

**先決條件（ runner + 工具存取）**
- 自託管 GitHub runner 透過 **Tailscale mesh** 連接到 K3s API。
- `init-deploy.yml` 透過 `scripts/ops/gen-kubeconfig.sh` 產生一個**2 小時有效、namespace 範圍的 SA token**（`<ns>-ci-sa`）— 沒有長期有效的 admin kubeconfig。
- GHCR push/pull 與跨 repo IssueOps 寫入使用 `GHCR_TOKEN` PAT（*單一 PAT 範圍限制 → GitHub-App 是升級目標*）。
- GATE 2 / `/validate-*` 探測透過 NGF 命中**公開主機**（真實外部路徑）。

## 6. IssueOps 主幹 — freight → release 生命週期
**目的：溯源，而非存取控制。** 這些 issue 使部署成為一個有證據、可追蹤的行為，並防止無根據的部署。它們**不是**防篡改的閘門（標籤可由人為修改；無職責分離）— 它們防止的是*疏漏*，而非蓄意繞過（單人、無攻擊者）。

- **`freight: 0.X.Y-<sha>`**（preview 佇列）：由 `publish-dev` 在合併的 PR 帶有 `freight` 標籤時開啟（選擇加入 — 大多數 dev merge 會累積導向後續的驗證；image 無論如何都會發布）；`init-deploy` 張貼自動化檢查清單（**不會**蓋下 `validated`）；`/validate-freight` 僅在人員簽核時蓋上 `validated`（**證據留言**是正式的認證記錄，標籤只是其機器索引）；`release.yml` 要求 `validated` 標籤，然後在提升時關閉該 issue。
- **`release: v0.X.Y`**（staging/歸檔佇列）：機器在提升時開啟，人員在歸檔 PR merge 時關閉。*（在 `staging` 上的直接 commits（D2/D3）省略了 merge 前的 PR 審查；閘門移到部署後 `/validate-release`，稽核軌跡是這個 issue + merge commit。）* 對於僅 Deploy 的設定 hotfix，開放的設定 issue（例如 `Deploy #12`）作為稽核 ticket，而非建立新的 `release: v0.X.Y` issue。

## 7. Versioning — 解耦演進策略
App 與 Deploy 版本號獨立漂移，以分別反映各自的發行單位：
*   **App Repo（`SafeZone`）**：VERSION 定義在 `/SafeZone/VERSION`。在程式碼變更時更新。Image 使用 `appVersion` 標記（例如 `0.3.6`）。
*   **Deploy Repo（`SafeZone-Deploy`）**：設定版本定義在所有子 chart 的 `Chart.yaml` `version` 欄位中。在任何設定/chart 變更時全域更新所有 chart。`Chart.yaml` 中的 `appVersion` 作為指向目標 App image tag 的指標。
*   **更新矩陣**：
    1.  **共同變更（情境 A）**：App 更新至 `0.3.7`。Deploy 將 `version` 更新至 `0.3.7`，`appVersion` 更新至 `"0.3.7"`。
    2.  **僅 Deploy 修正（情境 B）**：App 凍結在 `0.3.6`（無新的建構/tag）。Deploy 將 `version` 更新至 `0.3.7`，保持 `appVersion` 為 `"0.3.6"`。
    3.  **僅 App 修正（情境 C）**：App 更新至 `0.3.7`。Deploy 將 `version` 更新至 `0.3.8`（因為 `0.3.7` 已被僅 Deploy 修補程式使用）並將 `appVersion` 設為 `"0.3.7"`。
*   **`VERSION` 更新紀律**：對於 App 發行版，在 `dev` 上**每週期開啟時更新一次**（A1）— 它是 dev image 版本前綴。Deploy chart 的 `appVersion` 與之對應。兩個現有的保護措施會讓錯誤變得很明顯：如果 `VERSION` ≠ tag，`release.yml` 會失敗；如果 preview values 固定了多個 image tag，`init-deploy` 會報錯。

## 8. 回滾與復原
> 刻意保持輕量 — 大部分是**設計而未實際執行**；強制機制已推遲。

- **僅 forward-fix**（0.x 無自動回滾）；tags 是快照。
- **`staging` 具有雙重角色**（soak + 持續展示）→ 原地**救援**：將 staging ArgoCD `targetRevision` - 救援基準線，向後）。
- **回滾樓層 = `v0.3.6`**（ADR-8 T0）：NGF 之前的設定會產生已退役的 `Ingress` → 在叢集中無效，因此低於樓層的 tags 已成為歷史，不是救援目標。**「絕不取消標記」是通用的** — 「修剪」會移除回滾*資格*（樓層過濾器 / `rollback/*` 別名），但絕不刪除 tag。**強制機制（T1）已推遲** → `.ai-session-drafts/2026-06-15-platform-rollback-wall.md`。

---

**第三部分 — 狀態**

## 9. 尚未驗證 / 已推遲（項目清除時刪除）
- **A–E 重構尚未實際執行**：v0.3.6 運行了 4 階段、原地 staging 提升。5 階段 / teardown-rebuild staging / frozen-pin 發行版切版 / plain-merge（無 promote branch）是設計上存在，但尚未運行。
- **`/validate-release` + `/validate-soak`**：🟡 已規劃，尚未建置（`/validate-freight` 針對 staging 主機的變體；soak 會加入基於時間的檢查）。
- **ADR-4 版本解耦**：不再推遲；在 `v0.3.6` 時區 hotfix 週期期間成功執行。
- **回滾救援機制 + 樓層 T1**：已設計/宣告，從未執行；在 `v0.3.6-staging` 於 soak 後被切出之前，沒有 NGF 驗證過的救援點；T1 強制機制尚未決定。
- **ADR-6 調度模式**：僅有一輪證據；稍後整合。
- **維護者 SSOT 對齊**：由 Gemini 同儕審查；已對齊至 `Docs/`。

## 10. Next: peer-review → SSOT 對齊
開拓者擁有的正式程序。路徑：架構師 + Gemini 同儕審查（流程已完成；此彙整文件待審）→ 取代 `delivery-workflow.md` → 維護者（Gemini）對齊至 `Docs/` SSOT（合併各 repo 的前置文件）→ 隨著項目清除而修剪 §9。

---

**附錄**

## A. 架構決策記錄（簡明版）

| ADR | 決策 | 狀態 |
| :- | :- | :- |
| 1 | 在 `dev` merge 時發布 dev images `0.X.Y-<sha>`（E1-fix）— 在標記前，preview 驗證真實工件 | 已接受 |
| 2 | 發行版 = **透過 `crane copy` 提升**（digest 相同），而非重新建構 | 已接受 |
| 3 | **在 preview 驗證後**才切 tag，而非 soak 後（E2-fix） | 已接受 |
| 4 | 一個產品版本；僅在需要時解耦 | 已接受 |
| 5 | 跨 repo 驗證記錄 = **IssueOps freight issue**（非 values-grep / Deployments API） | 已接受 |
| 6 | 將版本 **tag** 與**提升**解耦（`workflow_dispatch`/`dry_run`） | 已接受，暫定 |
| 7 | 發行版**開啟** `release: v0.X.Y` staging 工作佇列 issue | 已接受 |
| 8 | 回滾有效性**受限於平台世代**（樓層 = `v0.3.6`） | T0 已接受；T1 已推遲 |
| 9 | **混合部署** — 宣告式調和（ArgoCD/infra）+ 命令式 Job 門控編排（`init-deploy`, app） | 已接受 |
| 10 | **Staging 發行版部署 = teardown + rebuild**（非原地）；滾動替換推遲至產品階段 | 已接受（未實際執行） |
| 11 | **No `promote/<ver>-staging` branch** — plain-merge `preview`→`staging` + 直接 staging 編輯；透過 `release` issue + merge commit 進行稽核 | 已接受 |
| 12 | **Validate 技能保持專注**（非單一分支技能）；`/validate-release`、`/validate-soak` 已規劃 | 已接受 |
| 13 | **客觀環境路由檢查清單** — App 程式碼 / DB schema / Ingress 變更需要 preview GATE 2；純設定變更可直接修補 staging | 已接受 |
| 14 | **Staging Hotfix 限定範圍重新 Soak** — 僅 staging/設定的變更僅觀察影響範圍（N-cycles），而非重設 3 天 soak 時鐘 | 已接受 |

> **ADR-2 備註**：`release.yml` 最初從原始碼重新建構（短暫的 runner 僅在本機快取中保留驗證過的 image）；ADR-1 取消了這一點。`buildx imagetools create` 將單一架構的原始來源重新包裝成新的 OCI index（不同的 digest）→ 改為使用 `crane copy`（保留 digest）。保證「出貨 == 已驗證」，**非**建置可重現性（浮動的基礎 tag）。
> **ADR-9 備註**：純 ArgoCD 路徑（sync-waves + Job hooks）曾被嘗試過（約 2025 年）並失敗了 — wave 進展 + hook 完成都依賴於 ArgoCD 的 Job 健康評估，而該評估在 Jobs 實際完成之前就前進了。持久的理由 = 問題形狀的劃分（宣告式收斂 vs 執行到完成的門控）。**在混合式出現痛點時重新審視，而非因 ArgoCD 發行版而審視。**
