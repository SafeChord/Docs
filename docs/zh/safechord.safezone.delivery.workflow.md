---
title: 'Script: SafeZone 統一交付工作流程'
doc_id: safechord.safezone.workflow.delivery
doc_version: 0.3.6
app_version: 0.3.6
last_updated: '2026-06-17'
status: active
authors:
  - bradyhau
  - Claude Code
  - Gemini CLI
context_scope: SafeZone App & Deploy Repos
summary: 定義涵蓋 SafeZone (App) 與 SafeZone-Deploy (Deploy) 儲存庫的端到端統一交付管線，採用混合式 GitOps + IssueOps 推廣模型。
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

> **狀態**：正式版（canonical）。取代 `delivery-workflow-final.md`，已整合至 `Docs/`。
> **範圍**：涵蓋 `SafeZone`（App）與 `SafeZone-Deploy`（Deploy）的端到端交付。
> **實際運行測試**：`v0.3.6` 已出貨並提升至 staging（自 2026-06-15 起浸泡中），採用先前的 **4 階段、原地更新** 模型。
> **A–E 重構**（5 階段、staging 拆掉重建、凍結 pin、無 promote 分支）**尚未按本文所述實際執行** — 請參閱 §9。
> **決策負責人**：bradyhau（架構師）· **作者**：Claude Code（開拓者）。流程與回覆由 Gemini（維護者）審閱。

---

**第一部分 — 流程** *(你要做的事)*

## 1. 儲存庫、分支、標籤與 IssueOps 接觸點

**App `SafeZone` — GitFlow**
| 分支 | 角色 / 動作 |
| :- | :- |
| `feature/*` | 功能開發（本地） |
| `dev` | 整合主幹 — CI 考驗 (**GATE 1**) + `publish-dev` 推送 `0.X.Y-<sha>` |
| `release/*` | **釋出版本切割 — 凍結 pin**（在驗證過的 sha 上切割；PR → `main`；不允許新提交） |
| `hotfix/*` | 緊急修復 — **流程待定**（目前：透過正常流程向前修復） |
| `main` | 正式環境主幹 — 標籤 `v*.*.*` → `release.yml` 提升 |

**Deploy `SafeZone-Deploy` — 3 分支（Actions 驅動的提升 + GitOps）**
| 分支 | 階段 | ArgoCD |
| :- | :- | :- |
| `preview/<ver>` | 開發與叢集內驗證（臨時；每個週期從 `staging` 重新切割） | 自動同步，`targetRevision=preview/<ver>` |
| `staging` | 浸泡 + 持久展示 | 自動同步，`targetRevision=staging` |
| `main` | 黃金設定存檔（完整儲存庫快照；不從此同步） | — |

**標籤**：`0.X.Y-<sha>`（開發 / preview）· `0.X.Y`（正式版，crane）· `v0.X.Y`（git）· `v0.X.Y-staging`（救援基準線）。
> `v*-staging` **永不刪除**；回滾 *資格* 由 floor（§8）管理，而非透過取消標籤。

**IssueOps 接觸點**（deploy 儲存庫）：`freight: 0.X.Y-<sha>`（preview 佇列 → 獲得 `validated`）→ `release: v0.X.Y`（staging / 存檔佇列）。

## 2. 管線 — 階段 A–E

### 階段 A — App 整合（`SafeZone`）
- **A1.** 開啟週期：在 `dev` 上執行 `chore(release): open v0.X.Y`（更新 `VERSION`）。
- **A2.** PR → `dev`；CI 考驗（`make ci-all` + `make smoke-test`）= **GATE 1**。
- **A3.** 合併 → `publish-dev` 推送 `0.X.Y-<sha>` **並在 deploy 儲存庫中開啟** `freight: 0.X.Y-<sha>`。

### 階段 B — Preview 驗證（`SafeZone-Deploy`）
- **B1.** 接手 `freight: 0.X.Y-<sha>` issue。
- **B2.** 為 `0.X.Y-<sha>` 撰寫 `preview/0.X.Y` 設定（架構 + 映像標籤）→ **推送分支**。
- **B3.** `SETUP_INFRA` — 啟動 preview 基礎設施。
- **B4.** 執行 `init-deploy.yml`（env=preview）→ 在 freight issue 上張貼自動化檢查清單。
- **B5.** 執行 `/validate-freight`。
- **B6.** 人工簽核（UI 回應 + 外部連線）。
- **B7.** 簽核後 → 蓋上 `validated` 標籤。
- **B8.** 拆除 preview — **先 app，再基礎設施**（`scripts/ops/preview/`）。

### 階段 C — 切割釋出版本（`SafeZone`，僅在 `validated` 之後）
- **C1.** 確認 freight issue 帶有 `validated`。
- **C2.** PR `release/0.X.Y`（凍結 pin — 無新提交）→ `main`（**合併，非 squash**）+ 標籤 `v0.X.Y`。
- **C3.** 標籤觸發 `release.yml` → 在 deploy 儲存庫中開啟 `release: v0.X.Y`。

### 階段 D — Staging 部署 + 浸泡（`SafeZone-Deploy`）
- **D1.** 拆除 staging — app + 基礎設施（保留外部 / 平台服務）。🟡
- **D2.** **直接合併** `preview/0.X.Y` → `staging`（無 promote 分支，無 PR）。
- **D3.** 在 `staging` 上（直接提交）：設定 `values-staging` 為 `:0.X.Y` + 修正環境差異。
- **D4.** `SETUP_INFRA` — 啟動 staging 基礎設施。
- **D5.** 執行 `init-deploy.yml`（env=staging）。
- **D6.** 執行 `/validate-release`。🟡
- **D7.** 人工驗證（UI + 外部連線）。
- **D8.** 成功後 → 在 `release: v0.X.Y` issue 上確認檢查清單。
- **D9.** 開始浸泡（3–5 天）。

### 階段 E — 存檔（`SafeZone-Deploy`）
- **E1.** 執行 `/validate-soak`。🟡
- **E2.** 確認所有 `release: v0.X.Y` 檢查清單項目已完成。
- **E3.** 在 `staging` 上標記 `v0.X.Y-staging` + PR `staging` → `main`（存檔）。
- **E4.** 關閉 `release: v0.X.Y` issue。

## 3. 例外與迭代 *(偏離快樂路徑)*
- **Preview 修復迴圈**：需要修復 → 回到 **A**（新的 `0.X.Y-<sha>`），重新指向 preview，重新驗證。**標籤不移動。**
- **釋出版本復原**：`main^2` 解析了未驗證的 sha → 透過 `workflow_dispatch source_sha=<validated>` 重新執行 `release.yml`。
- **Staging 救援**：即時故障 → 將 ArgoCD `targetRevision` pin 到最後一個良好的 `v*-staging`（≥ floor）→ 向前修復 → 解除 pin。*(§8；從未實際執行。)*
- **快速路徑**：變更 *可證明* 不跨越部署邊界 → GATE 1 可能足夠。
- **Hotfix**：**流程待定** — 目前，透過正常流程向前修復到下一個 patch。

---

**第二部分 — 原理** *(為何如此設計)*

## 4. 核心原則
1. **標籤是認證，不是檢查點** — 在變更所影響的最高風險環境變綠後才切割，絕非「我編輯完了」的標記。
2. **浸泡 / 真實流量是釋出後的監控，絕非標籤前的關卡** — 標籤 → 部署 → *然後* 浸泡；浸泡失敗 → 向前修復。
3. **關卡與風險成比例** — app 層級的變更 → 編譯 + CI（**GATE 1**）；邊界層級的變更 → 叢集內 preview（**GATE 2**，包含真實瀏覽器測試 + UI 版本的 external-DNS 探測）。
4. **僅向前修復；標籤不可變** — 永不重新標記，永不取消標記。快照僅在其*平台世代*內才是有效的回滾目標（§8）。
5. **目前 app + deploy 共用一個產品版本** — 鎖定相等，直到第一次釋出後、app 不變的設定修復（§7）。
6. **所有變更都經過 preview 關卡；`hotfix/*` 不會繞過它** — 無正式環境 SLA（展示用），因此沒有緊急情況可以證明出貨未經驗證的版本是合理的。

## 5. 部署模型 — 混合式 + 先決條件
*這**不是**純 GitOps。兩部分：一個命令式的分支提升流程（GitHub Actions + PR/標籤）疊加在 GitOps 協調之上。*

- **ArgoCD 負責穩定狀態協調。** 每個 `deploy/<env>/app/*.yaml` 都是一個自動同步的 `Application`（`targetRevision` = 環境分支；`path` = `helm-charts/safezone-<layer>` + `values-<env>.yaml`）。Helm 在 **ArgoCD 內部** 渲染，而非作為 CI 前置步驟。
- **按層排序** — ArgoCD 的健康驅動同步波無法跨越 Application 或可靠地閘控 Job：
  - **基礎設施** → ArgoCD 原生 **sync-waves**（`ApplicationSet`：基礎 `-2` → 安全 `1` → 工作負載 `2` → 初始化 `3`）。
  - **App** → **`init-deploy.yml`** 按順序套用 Application CR，並在階段之間根據 rollout/Job健康狀態進行閘控（基礎 → seed-schema → 核心 → **3.5 smoke（硬閘門）** → seed-cases → ui → scheduler[staging]）。一個分階段的*啟動器 + 閘門*，而非命令式部署器 — 一旦 CR 存在，ArgoCD 就會協調它。（參見 ADR-9。）
- **Staging 釋出版本部署 = 拆除 + 重建**（非原地滾動更新）。在 0.x 階段，架構在版本之間仍會有重大變化，因此原地路徑會帶來每個版本的持久資料 / 遷移推理，這不值得；完整重建是**確定性的**，並且**在 < 10 分鐘內恢復**。零停機滾動替換是**產品階段的發展方向**，已推遲。*(尚未按本文所述實際執行 — §9。)*

**先決條件（執行器 + 工具存取）**
- 自託管 GitHub runner 透過 **Tailscale mesh** 連線到 K3s API。
- `init-deploy.yml` 透過 `scripts/ops/gen-kubeconfig.sh` 產生一個 **2 小時、命名空間範圍的 SA token**（`<ns>-ci-sa`）— 無長期有效的管理員 kubeconfig。
- GHCR 推送/拉取 + 跨儲存庫 IssueOps 寫入使用 `GHCR_TOKEN` PAT *（單一 PAT 範圍 → GitHub-App 是未來的演進方向）*。
- GATE 2 / `/validate-*` 探測透過 NGF 打到**公開主機**（真實外部路徑）。

## 6. IssueOps 主幹 — freight → release 生命週期
**目的：來源證明，而非存取控制。** Issue 使部署成為一個有證據、可追溯的行為，並防止無根據的部署。它們**不是**防篡改的關卡（標籤可由人工修改；無職責分離）— 它們防止的是*疏忽*，而非稽意繞過（單人、無對手）。

- **`freight: 0.X.Y-<sha>`**（preview 佇列）：由 `publish-dev` 在合併的 PR 帶有 `freight` 標籤時開啟（選擇加入 — 大多數 dev 合併會累積到後續的驗證；映像無論如何都會發布）；`init-deploy` 張貼自動化檢查清單（**不**蓋上 `validated`）；`/validate-freight` 僅在人工簽核時蓋上 `validated`（**證據評論**是正式的認證記錄，標籤是其機器索引）；`release.yml` 要求 `validated` 標籤，然後在提升時關閉它。
- **`release: v0.X.Y`**（staging/存檔佇列）：機器在提升時開啟，人工在存檔 PR 合併時關閉。*(在 `staging` 上的直接提交（D2/D3）跳過了合併前的 PR 審查；關卡移至部署後的 `/validate-release`，稽核軌跡是此 issue + 合併提交。)*
- **為什麼用 Issue，而不是 GitHub Environments / Deployments API**：那些 API 閘控*執行部署的工作流程*，但部署是 ArgoCD 協調 git（關鍵路徑上無工作流程），而且它們是每個儲存庫的（此交接是跨儲存庫的）。IssueOps 是合適的模式（ChatOps / branch-deploy 的傳承）。較重的原語是**已知但未深入研究** — 研究方向，而非被拒絕的選項。

## 7. 版本管理 — 單一產品版本
- App + Deploy 共用一個版本（`appVersion == chart version`）**目前如此**；鎖步是 0.x 合約變動的症狀。在第一次釋出後、app 不變的設定修復時解耦（ADR-4）。
- **`VERSION` 更新紀律**：在週期開啟時（A1）在 `dev` 上**更新一次** — 它是開發映像版本前綴。Deploy chart 會鏡像它。兩個現有的防護措施會讓錯誤很明顯：如果 `VERSION` ≠ 標籤，`release.yml` 會失敗；如果 preview values 固定了多個映像標籤，`init-deploy` 會報錯。

## 8. 回滾與復原
> 刻意輕量 — 大部分是**設計但未實際執行**；強制執行已推遲。

- **僅向前修復**（0.x 無自動回滾）；標籤是快照。
- **`staging` is 雙重角色**（浸泡 + 持久展示）→ 原地**救援**：將 staging ArgoCD `targetRevision` pin 到最後一個良好的 `v0.X.Y-staging` 標籤，在分支上向前修復，解除 pin。**從未實際執行**（§9）。
- **兩個標籤**：`v0.X.Y`（存檔，向前）· `v0.X.Y-staging`（救援基準線，向後）。
- **回滾 floor = `v0.3.6`**（ADR-8 T0）：NGF 之前的設定會渲染已淘汰的 `Ingress` → 在叢集上失效，因此低於 floor 的標籤是歷史，而非救援目標。**永不取消標籤是普遍原則** — 「清理」會移除回滾*資格*（floor 過濾器 / `rollback/*` 別名），絕非標籤本身。**強制執行（T1）已推遲** → `.ai-session-drafts/2026-06-15-platform-rollback-wall.md`。

---

**第三部分 — 狀態**

## 9. 尚未驗證 / 已推遲 *(項目清除時刪除)*
- **A–E 重構尚未實際執行**：v0.3.6 運行了 4 階段、原地 staging 提升。5 階段 / 拆除重建 staging / 凍結 pin 釋出版本切割 / 直接合併（無 promote 分支）是設計但尚未運行的。
- **`/validate-release` + `/validate-soak`**：🟡 已規劃，尚未建置（`/validate-freight` 針對 staging 主機的變體；浸泡增加了基於時間的檢查）。
- **Hotfix 流程**：待定（目前僅向前修復）。
- **回滾救援機制 + floor T1**：已設計/宣告，從未實際執行；在浸泡後切割 `v0.3.6-staging` 之前，沒有 NGF 驗證的救援點；T1 強制執行尚未決定。
- **ADR-6 dispatch 模式**：僅一個週期的證據；稍後整合。
- **維護者 SSOT 整合**：由 Gemini 同儕審查；尚未整合到 `Docs/`。

## 10. 下一步：同儕審查 → SSOT 整合
開拓者擁有的正式流程。路徑：架構師 + Gemini 同儕審查（流程已完成；此彙整文件待審）→ 取代 `delivery-workflow.md` → 維護者（Gemini）整合到 `Docs/` SSOT（合併每個儲存庫的前身文件）→ 在項目清除時清理 §9。

---

**附錄**

## A. 架構決策記錄（簡潔版）

| ADR | 決策 | 狀態 |
| :- | :- | :- |
| 1 | 在 `dev` 合併時發布開發映像 `0.X.Y-<sha>`（E1 修復）— preview 在標籤前驗證真實工件 | 已接受 |
| 2 | 釋出 = **透過 `crane copy` 提升**（摘要相同），非重建 | 已接受 |
| 3 | 在 **preview 驗證後** 切割標籤，而非浸泡後（E2 修復） | 已接受 |
| 4 | 單一產品版本；即時解耦 | 已接受（觸發條件待定） |
| 5 | 跨儲存庫驗證記錄 = **IssueOps freight issue**（非 values-grep / Deployments API） | 已接受 |
| 6 | 將版本**標籤**與**提升**解耦（`workflow_dispatch`/`dry_run`） | 已接受，暫行 |
| 7 | 釋出**開啟** `release: v0.X.Y` staging 工作佇列 issue | 已接受 |
| 8 | 回滾有效性**受平台世代限制**（floor = `v0.3.6`） | T0 已接受；T1 已推遲 |
| 9 | **混合部署** — 宣告式協調（ArgoCD/基礎設施）+ 命令式 Job 閘控編排（`init-deploy`，app） | 已接受 |
| 10 | **Staging 釋出版本部署 = 拆除 + 重建**（非原地）；滾動替換推遲到產品階段 | 已接受（未實際執行） |
| 11 | **無 `promote/<ver>-staging` 分支** — 直接合併 `preview`→`staging` + 直接 staging 編輯；透過 `release` issue + 合併提交進行稽核 | 已接受 |
| 12 | **驗證技能保持專注**（非單一分支技能）；`/validate-release`、`/validate-soak` 已規劃 | 已接受 |

> **ADR-2 備註**：`release.yml` 最初從原始碼重建（臨時 runner 僅在本地快取中保存驗證過的映像）；ADR-1 解決了這個問題。`buildx imagetools create` 將單一架構來源重新包裝到新的 OCI 索引中（不同的摘要）→ 切換到 `crane copy`（保留摘要）。保證「出貨 == 驗證過」，**非**建置可重現性（浮動基礎標籤）。
> **ADR-9 備註**：純 ArgoCD 路徑（sync-waves + Job hooks）曾嘗試過（約 2025 年）並失敗 — 波進展和 hook 完成都依賴於 ArgoCD 的 Job 健康評估，而這在 Job 實際完成之前就前進了。持久的理由是問題形狀的拆分（宣告式收斂 vs 執行到完成的閘控）。**在混合式出現問題時重新審視，而非在 ArgoCD 版本更新時。**
