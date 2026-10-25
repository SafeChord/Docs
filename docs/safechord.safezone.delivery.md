---
title: 'Script: SafeZone Unified Delivery Workflow'
status: active
archetype: script
code_paths:
  - SafeZone/.github/workflows
  - SafeZone-Deploy
---

# SafeZone Delivery (App + Deploy)

> **Type**: Script (a project implementation page: implements the shared [delivery mode page](safechord.kdd.practice.delivery.md))
> **Focus**: How a SafeZone release is cut, validated in preview, promoted to staging, soaked and archived, across `SafeZone` (App) and `SafeZone-Deploy` (Deploy), and why it is shaped that way.
> **Constraint**: Nothing every project's delivery holds (the gate, floor and focus, what Development hands over): it is on the shared page. What a check runs is in its `validate-*` skill (`.claude/skills/` in the workspace harness); what a pipeline does, and the commands, are in its workflow file and scripts.

## Mode Contract {#mode-contract}

What the shared page leaves to its implementation, and what this page extends.

- **Work** (extends): a SafeZone release: a phase of §2, or a route of §3.
- **Human** (extends): the gates are the freight evidence comment and its `validated` label (B6–B7), the staging check (D7), the soak and the archive (Phase E). bradyhau (Architect) owns the workflow's decisions.
- **Seats**: none yet. Whether a release run needs one is an open decision.
- **Ends**: when the `release: v0.X.Y` issue closes (E4), or the release is superseded by a patch (Route A1-post).
- **Landing**: as each phase states: the release branch's PR and tag in `SafeZone`, the preview and staging branches in `SafeZone-Deploy` (§1–§3). Nothing in this mode writes to `Docs/`: a release's record is SafeZone's `CHANGELOG.md`.
- **Protocols** (extends): the `freight` and `release` issues, which take a ticket's place for a release, and the release record ticket, which holds the checks Development deferred to the release (§5).
- **Carried by**: `validate-freight` (B5), `validate-release` (D6) and `validate-soak` (E1, Route B), on the floor in `.claude/validation/floor.md`; the `publish-candidate`, `init-deploy.yml` and `release.yml` workflows. Written only on this page: every other step of §2–§3.

```mermaid
graph TD
    %% Repos
    subgraph App_Repo [App: SafeZone]
        dev[dev branch]
        rel[release/0.X.Y branch]
        main_app[main branch]
        
        dev -->|A1: Cut release branch| rel
        rel -->|A2: Push triggers build| dev_img[dev-image: 0.X.Y-sha]
        rel -->|C2: PR Merge & Tag v0.X.Y| main_app
        main_app -->|C4: Back-merge| dev
    end

    subgraph Deploy_Repo [Deploy: SafeZone-Deploy]
        prev[preview/0.X.Y branch]
        stag[staging branch]
        main_dep[main branch]

        dev_img -->|B1: Freight Issue| prev
        prev -->|B3-B6: Validate GATE 2| prev
        prev -->|D2: Plain-merge| stag
        stag -->|D9: Soak 3-5 days| stag
        stag -->|E3: PR Merge & Tag staging-tag| main_dep
    end

    %% Syncs
    prev -.->|B4: init-deploy| Preview_Env((Preview Env))
    stag -.->|D5: init-deploy| Staging_Env((Staging Env))
```

---

**PART I — THE FLOW** *(what you do)*

## 1. Repos, branches, tags & IssueOps touchpoints

**App `SafeZone` — GitFlow**
| Branch | Role / Action |
| :- | :- |
| `feature/*` | Feature development (local) |
| `dev` | Integration trunk — runs CI checks (GATE 1) |
| `release/*` | **Release branch — single-use** (cut from dev to isolate release; no new features. Receives hotfix PRs ➡️ runs GATE 1. Frozen/retired after tagging; post-GA defects do not reopen this branch) |
| `main` | Production trunk — merges `release/*` and tags `v*.*.*` |

**Deploy `SafeZone-Deploy` — GitOps Branches**
| Branch | Environment | ArgoCD Sync Target |
| :- | :- | :- |
| `preview/<ver>` | Dev & in-cluster validation (ephemeral; re-cut from staging) | `targetRevision=preview/<ver>` |
| `staging` | Soak + persistent showcase | `targetRevision=staging` |
| `main` | Golden config archive (history only, no sync) | — |

A SafeZone-Deploy ticket opened during a release, such as one triaged from the freight issue, branches from and merges into `preview/<ver>`, not `staging`: `staging` syncs to the live demo, so a merge there reaches the running release before preview has validated it. During 0.3.8 such a change would have restart-looped the live v0.3.7 worker.

**Tags**: `0.X.Y-<sha>` (Preview images) · `0.X.Y` (Official App release image) · `v0.X.Y` (Git release tag) · `v0.X.Y-staging` (Rescue baseline).

**IssueOps Touchpoints** (Deploy Repo):
| Ticket Type / Label | Opened By | Machine Action | Human Action (Sign-off) |
| :- | :- | :- | :- |
| **`freight: 0.X.Y-<sha>`** | Pushing `release/0.X.Y` | Opens preview ticket, posts checklist | Validate GATE 2 ➡️ Comment evidence ➡️ Stamp `validated` |
| **`release: v0.X.Y`** | Tagging `v0.X.Y` on App | Opens staging queue ticket | Verify soak (N-cycles) ➡️ Merge `staging` to `main` ➡️ Close ticket |

## 2. The pipeline — Phase A–E

### Phase A — App integration (`SafeZone`)
- **A1.** Confirm that `main` is an ancestor of `dev`: a release started before the prior version is back-merged would leave its fixes orphaned. Cut `release/0.X.Y` from `dev`, bump the App `VERSION` file to the target version on the release branch, and commit the change (e.g., `chore(release): open v0.X.Y`).
- **A2.** Push `release/0.X.Y` to remote. This push triggers `publish-candidate (GitHub Action)` to build and push the OCI images and automatically opens the `freight: 0.X.Y-<sha>` issue.

### Phase B — Preview validation (`SafeZone-Deploy`)
- **B1.** Pick up the `freight: 0.X.Y-<sha>` issue.
- **B2.** Author configurations on the preview branch. Update target image tags and env values for both `preview` and `staging` charts ➡️ **push the branch**. Staging's values are set here, not when staging comes up, so that they are tested with the release and promoted in the same merge (D2).
- **B3.** Bring up the preview infrastructure.
- **B4.** Trigger the `init-deploy.yml` action (env=preview).
- **B5.** Run preview validation probes.
- **B6.** Manual sign-off check (UI response + external connectivity).
- **B7.** Stamp the `validated` label on the freight issue.
- **B8.** Teardown the preview environment (app first, then infra).

### Phase C — Cut the release (`SafeZone`, only after `validated`)
- **C1.** Confirm the freight issue carries `validated`.
- **C2.** Merge the PR from `release/0.X.Y` to `main` (merge commit only, no squash) and cut the tag `v0.X.Y`.
- **C3.** Tagging triggers the release pipeline (`release.yml`), which copies the verified preview OCI images (tagged `0.X.Y-<sha>`) to the release tags (`0.X.Y`) by digest and opens the `release: v0.X.Y` issue. Copying the digest instead of rebuilding ships exactly what preview validated; a rebuild can pick up a floating base tag or a newer upstream package.
- **C4.** Back-merge `main` back to `dev` to propagate release-stage bug fixes. The release pipeline (`release.yml`) automatically opens a "back-merge v0.X.Y -> dev" PR after tagging to ensure compliance. *Invariant*: Before cutting the next `release/*` branch, `dev` must receive all outstanding release fixes (no orphaned fixes). Any fix identified after tagging (especially during soak/showcase) must be treated as a post-GA patch (Route A1-post) with its own back-merge, and must never reopen the frozen `release/*` branch.

### Phase D — Staging deploy + soak (`SafeZone-Deploy`)
- **D1.** Teardown the existing staging environment (leave external / platform services). A rebuild holds while schemas and platform networking still break between releases: backward-compatible migrations and a rolling update for every release would cost more than a clean rebuild, which recovers in under 10 minutes. Revisit it once migrations stay backward compatible.
- **D2.** Plain-merge `preview/0.X.Y` directly into `staging` (no PR, no staging promotion branch). No PR holds while the project has one developer: GATE 2 has already validated the config in the cluster, a PR would add a step with no second reviewer, and the merge commit and the release issue keep the audit trail.
- **D3.** Adjust staging environment deltas (env deltas) on the `staging` branch ➡️ **push the branch**.
- **D4.** Bring up the staging infrastructure.
- **D5.** Trigger the `init-deploy.yml` action (env=staging).
- **D6.** Run `/validate-release (AI Skill)`. 
- **D7.** Human verifies (UI + external connectivity).
- **D8.** On success → confirm the checklist on the `release: v0.X.Y` issue.
- **D9.** Start soak (3–5 days).

### Phase E — Archive (`SafeZone-Deploy`)
- **E1.** Run `/validate-soak` (soak data freshness check pending design).
- **E2.** Confirm all `release: v0.X.Y` checklist items are done.
- **E3.** Tag `v0.X.Y-staging` on `staging` + PR `staging` → `main` (archive).
- **E4.** Close the `release: v0.X.Y` issue.

## 3. Exceptions & iteration *(off the happy path)*

- **Critical Defect & Border Changes (Route A — Must Return to Preview)**: If an issue is identified during preview validation, staging soak, or showcase, **direct staging commits are strictly forbidden** for resolving it. The change must go through preview validation. If a soak is already running, its 3–5 day timer **must be reset**:
  * **Sub-route A1-pre: Pre-GA Patch (Image-driven, Release Branch Open)**
    - *Scope*: Changes to App business logic or database Schema/DDL scripts (packaged inside `safezone-ops-schema`) discovered before tagging (release branch Y is still open; Y is not yet shipped).
    - *Procedure*:
      1. On the App Repo (`SafeZone`), checkout `hotfix/*` from `release/0.X.Y`, apply the fix, and PR back to `release/0.X.Y` (runs GATE 1).
      2. Merging yet-untagged changes into `release/0.X.Y` triggers the build of a new `0.X.Y-<sha>` image (version prefix `0.X.Y` remains unchanged).
      3. On the Deploy Repo (`SafeZone-Deploy`), checkout `preview/0.X.Y`, update Helm values file to target the new image tag SHA, and push.
      4. Deploy preview (GATE 2) via `init-deploy.yml (GitHub Action)` and verify via `/validate-freight (AI Skill)`.
      5. Once validated, plain-merge `preview/0.X.Y` to `staging`.
  * **Sub-route A1-post: Post-GA Patch (Image-driven, Tagged/Shipped)**
    - *Scope*: Defects discovered after the release has been officially tagged and shipped (during soak or showcase).
    - *Procedure*:
      1. **Do NOT reopen** the retired `release/0.X.Y` branch. Instead, cut a new release branch `release/0.X.(Y+1)` directly from the last GA release tag (e.g., `v0.X.Y`)—never directly from `dev`.
      2. Bump the App `VERSION` file to `0.X.(Y+1)` directly on the new branch, commit, and push.
      3. Apply the hotfix on `release/0.X.(Y+1)` via a `hotfix/*` PR (runs GATE 1). Merging triggers the build of the new `0.X.(Y+1)-<sha>` patch image.
      4. Run preview validation (GATE 2) on `preview/0.X.(Y+1)` in Deploy Repo. Once validated, merge to `staging`, **start the soak timer for Y+1**, and **close the superseded release issue for Y** (marked as `superseded-by v0.X.(Y+1)`) to prevent multiple active staging queues.
      5. Proceed through the standard C-to-E phase (tagging `v0.X.(Y+1)` and executing back-merge to `dev` at C4).
      *Note*: Multiple release branches may briefly coexist (e.g., Y in soak while Y+1 patch is in validation). Version identification and GHA pipeline triggers must leverage glob patterns (e.g., `release/0.X.*`).
  * **Sub-route A2: Config-only Border Changes**
    - *Scope*: Ingress routes, DNS, NetworkPolicy, or firewall rules configurations (no app code or schema changes).
    - *Procedure*:
      1. On the Deploy Repo (`SafeZone-Deploy`), checkout `preview/0.X.Y`, apply configuration edits, and push.
      2. Deploy preview (GATE 2) to verify connectivity and network routing gates.
      3. Once validated, plain-merge `preview/0.X.Y` to `staging`.

- **Low-Risk Configuration Hotfix (Route B — Direct Staging Patch)**: For low-risk fixes involving only environment configurations or values tweaks (e.g., non-critical environment variables, resource limits, or scaling configurations) that do not trigger Route A1 (image changes) or Route A2 (border configurations):
  1. **Procedure**: Patch directly on the `staging` branch (direct commit). ArgoCD will reconcile the change in-place. Preview validation (GATE 2) is bypassed.
  2. **Auditing Ticket**:
     - If found during active soak: Tracked directly on the existing open `release: v0.X.Y` issue.
     - If found during Showcase: Tracked on a new spontaneous configuration issue (e.g., `Deploy #12`).
  3. **Scoped Re-soak (The N-Cycles Rule)**:
     - Do not reset the 3–5 day stability soak timer. Establish a shortened observation window determined objectively by the component's execution frequency:
       - *Scheduled Tasks*: Cover at least 2 complete execution cycles (N=2) to verify trigger correctness and idempotency (e.g., **48 hours / 2 days** for a daily scheduler).
       - *Continuous Services*: Cover **6 to 12 hours** to verify steady-state resource and memory profiles.
     - Validate via `/validate-soak (AI Skill)`. If passed, tag `v0.X.Y-staging` on `staging` and PR `staging` to `main` (archive).

- **Staging Rescue**: In case of staging environment failure, refer to [7. Rollback & recovery](#7-rollback-recovery) for temporary staging rescue and forward-fix procedures.

---

**PART II — THE RATIONALE** *(why it's shaped this way)*
## 4. Deployment model — hybrid + prerequisites
*This is **not** pure GitOps. Two halves: an imperative branch-promotion flow (GitHub Actions + PRs/tags) layered on GitOps reconciliation.*

- **ArgoCD owns steady-state reconcile.** Each `deploy/<env>/app/*.yaml` is an auto-sync `Application` (`targetRevision` = the env branch; `path` = `helm-charts/safezone-<layer>` + `values-<env>.yaml`). Helm renders **inside ArgoCD**, not as a CI pre-step.
- **Ordering, by layer** — ArgoCD's health-driven sync-waves don't span Applications or reliably gate Jobs:
  - **Infra** → ArgoCD-native **sync-waves** on the `ApplicationSet`.
  - **App** → **`init-deploy.yml`** applies the Application CRs in order and gates between phases on rollout and Job health; the order is in the workflow. A phased *bootstrapper + gate*, not an imperative deployer — once a CR exists, ArgoCD reconciles it. A pure ArgoCD path, with sync waves and Job hooks, was tried first: waves and hooks were seen to move on before the Jobs had finished, so schema seeding and smoke tests went ungated. Why ArgoCD took the Jobs as done is not established.


## 5. The IssueOps spine — freight → release lifecycle
**Purpose: provenance, not access control.** The issues make a deploy an evidence-based, traceable act and a poka-yoke against basis-less deploys. They are **not** a tamper-proof gate (labels are human-mutable; no separation of duties) — they guard against the *omission*, not a deliberate bypass (solo, no adversary).

- **`freight: 0.X.Y-<sha>`** (Preview & Validation Queue):
  - **Purpose**: Serves as the tracking ticket and verification record for dev-images during preview validation (GATE 2).
  - **Lifecycle**:
    - *Opened By*: Automatically created by the `publish-candidate (GitHub Action)` pipeline when the `release/0.X.Y` branch is pushed to remote.
    - *Verification*: `init-deploy.yml` posts an automated verification checklist. The human operator runs `/validate-freight (AI Skill)` and posts the verification evidence in the comments, which stamps the `validated` label on the ticket.
    - *Closed By*: Automatically closed by the release pipeline (`release.yml`) once the release branch is promoted.
  - **Audit Policy**: The **evidence comment** posted by the human operator is the official certification of record, while the `validated` label serves as the machine-readable index required by the release pipeline to proceed.

- **`release: v0.X.Y`** (Staging & Archive Work Queue):
  - **Purpose**: Serves as the tracking ticket and audit trail for staging deployment, stability soak, and production archiving.
  - **Lifecycle**:
    - *Opened By*: Automatically created by the release pipeline when the official `v0.X.Y` tag is cut on the App Repo.
    - *Verification*: Tracks the checklists for post-deployment checks via `/validate-release (AI Skill)` and the 3–5 days soak validation. Its soak item records when the soak started, as `(started YYYY-MM-DD HH:MM +08:00)`: `/validate-soak` reads the window from it.
    - *Closed By*: Manually closed by the operator after the `staging` branch is tagged (`v0.X.Y-staging`) and merged into `main` (archive).
  - **Audit Policy**: Since staging promotion bypasses pre-merge Pull Requests (D2), this issue—coupled with the git merge commit—acts as the single source of audit verification. For deploy-only configuration hotfixes during soak, changes are logged directly in the comments of this open release issue (or a spontaneous configuration issue if during Showcase) to avoid issue clutter.

- **Release record ticket** (`chore(release): checks held for the vX.Y.Z release`, one per milestone, in the repository the work was done):
  - **Purpose**: holds the checks Development could not run before merge because they need a release branch or a deployment (the shared page's §3).
  - **Opened by**: the Settler of the first ticket that defers a check to the release, if none exists.
  - **An entry**: `**From #<ticket> (<what it did>, PR #<pr>)**: <the check>, <what passes>, <what to record>. <why it could not run before merge>.` Beside the check, the entry says what it needs of an environment (whether it is invasive; observed once or over days) and the requirement it guards, which sets its lifetime: a blueprint promise is kept as a probe once it passes, a one-off change ends when it passes. A setting the deployment must align goes on it the same way, as a deployment note. The entry does not say where the check runs: the release run places it.
  - **Lifecycle**: open until each check has a result, passed or failed with a fix ticket linked; closed at E2. Its Done When carries no reconciliation item, which no gate before E4 could satisfy.

## 6. Versioning — Decoupled Evolution Strategy
App and Deploy version numbers drift independently to reflect their respective release units:
*   **App Repo (`SafeZone`)**: VERSION is defined in `/SafeZone/VERSION` (governed by the corresponding GitHub Milestone aggregating the target cycle's issues). It bumps on code changes. Images are tagged with `appVersion` (e.g., `0.3.6`).
*   **Deploy Repo (`SafeZone-Deploy`)**: Config version is defined in all sub-charts' `Chart.yaml` `version` fields. It bumps globally across all charts on any config/chart change. `appVersion` in `Chart.yaml` acts as the pointer to the target App image tag. *(Note: The library chart `safezone-common` has its `appVersion` pinned to `"1.0.0"` and does not participate in this image tag drifting.)*
*   **Bumping Matrix** (Assuming starting baseline is App `0.3.6` / Deploy `0.3.6`):
    1.  **Co-change (Scenario A)**: App code changes, releasing `0.3.7`. Deploy config also changes to support this new feature. Deploy bumps its chart `version` to `0.3.7` and updates `appVersion` to `"0.3.7"`.
    2.  **Deploy-only Fix (Scenario B)**: App stays frozen at `0.3.7`. Deploy configuration requires a patch (e.g., env variables). Deploy bumps chart `version` to `0.3.8` while keeping `appVersion` pinned to `"0.3.7"`.
    3.  **App-only Fix (Scenario C)**: App code changes, releasing `0.3.8`. Deploy config has no structural changes. To point to the new image, Deploy bumps chart `version` to `0.3.9` and updates `appVersion` to `"0.3.8"`.
*   **`VERSION` bump discipline**: 
    - At the start of a release cycle (Step A1), the App `VERSION` file is bumped directly on the `release/*` branch to set the target version (e.g., `0.3.7`), ensuring a frozen-pin semantic for the release codebase. All dev images generated during this cycle will use this version as a prefix (`0.3.7-<sha>`).
    - **Guards**: To prevent human error, the release pipeline (`release.yml`) automatically fails if the finalized Git tag (e.g., `v0.3.7`) does not match the content of the App `VERSION` file. Additionally, the release is always cut from a dedicated `release/*` branch (acting as a **frozen pin** for that version's codebase), guaranteeing that no unvalidated changes bypass the release gate.

## 7. Rollback & recovery {#7-rollback-recovery}
*   **Forward-fix only**: The project does not support automated rollback; issues are addressed by shipping forward fixes.
*   **Staging Rescue**: In case of staging environment failure, the ArgoCD `targetRevision` may be temporarily pinned to a known good release tag (`v0.X.Y-staging`) to restore showcasing functionality while a forward-fix is prepared.
