---
title: 'Script: SafeZone Unified Delivery Workflow'
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
summary: Defines the unified, end-to-end delivery pipeline across SafeZone (App) and SafeZone-Deploy (Deploy) repositories, employing a hybrid GitOps + IssueOps promotion model.
keywords:
  - CI/CD
  - GitOps
  - IssueOps
  - Pipeline
  - Promotion
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

# SafeChord Unified Delivery Workflow (App + Deploy)

> **Status**: canonical (formal). Supersedes `delivery-workflow-final.md` on swap; reconciled into `Docs/`.
> **Scope**: end-to-end delivery across `SafeZone` (App) + `SafeZone-Deploy` (Deploy).
> **Run-tested**: `v0.3.6` shipped + promoted to staging (soaking since 2026-06-15) under the **prior 4-phase, in-place** model.
> The **A–E restructure** (5-phase, teardown-rebuild staging, frozen-pin cut, no promote branch) is **not yet exercised as written** — see §9.
> **Decision owner**: bradyhau (Architect) · **Author**: Claude Code (Pioneer). Flow + responses reviewed by Gemini (Settler).

---

**PART I — THE FLOW** *(what you do)*

## 1. Repos, branches, tags & IssueOps touchpoints

**App `SafeZone` — GitFlow**
| Branch | Role / action |
| :- | :- |
| `feature/*` | feature dev (local) |
| `dev` | integration trunk — CI gauntlet (**GATE 1**) + `publish-dev` pushes `0.X.Y-<sha>` |
| `release/*` | **release cut — frozen pin** (cut at the validated sha; PR → `main`; no new commits) |
| `hotfix/*` | emergency — **flow TBD** (today: forward-fix via the normal flow) |
| `main` | production trunk — tag `v*.*.*` → `release.yml` promotes |

**Deploy `SafeZone-Deploy` — 3-branch (Actions-driven promotion + GitOps)**
| Branch | Stage | ArgoCD |
| :- | :- | :- |
| `preview/<ver>` | dev & in-cluster validation (ephemeral; re-cut from `staging` each cycle) | auto-sync, `targetRevision=preview/<ver>` |
| `staging` | soak + persistent demo | auto-sync, `targetRevision=staging` |
| `main` | golden config archive (full-repo snapshot; nothing syncs from it) | — |

**Tags**: `0.X.Y-<sha>` (dev / preview) · `0.X.Y` (official, crane) · `v0.X.Y` (git) · `v0.X.Y-staging` (rescue baseline).
> `v*-staging` is **never deleted**; rollback *eligibility* is curated by the floor (§8), not by un-tagging.

**IssueOps touchpoints** (deploy repo): `freight: 0.X.Y-<sha>` (preview queue → earns `validated`) → `release: v0.X.Y` (staging / archive queue).

## 2. The pipeline — Phase A–E

### Phase A — App integration (`SafeZone`)
- **A1.** Open the cycle: `chore(release): open v0.X.Y` on `dev` (bumps `VERSION`).
- **A2.** PR → `dev`; CI gauntlet (`make ci-all` + `make smoke-test`) = **GATE 1**.
- **A3.** Merge → `publish-dev` pushes `0.X.Y-<sha>` **and opens** `freight: 0.X.Y-<sha>` in the deploy repo.

### Phase B — Preview validation (`SafeZone-Deploy`)
- **B1.** Pick up the `freight: 0.X.Y-<sha>` issue.
- **B2.** Author `preview/0.X.Y` config for `0.X.Y-<sha>` (arch + image tag) → **push the branch**.
- **B3.** `SETUP_INFRA` — bring up the preview infra.
- **B4.** Run `init-deploy.yml` (env=preview) → posts the automated checklist on the freight issue.
- **B5.** Run `/validate-freight`.
- **B6.** Human signs off (UI response + external connectivity).
- **B7.** On sign-off → `validated` label stamped.
- **B8.** Teardown preview — **app first, then infra** (`scripts/ops/preview/`).

### Phase C — Cut the release (`SafeZone`, only after `validated`)
- **C1.** Confirm the freight issue carries `validated`.
- **C2.** PR `release/0.X.Y` (frozen pin — no new commits) → `main` (**merge, not squash**) + tag `v0.X.Y`.
- **C3.** The tag triggers `release.yml` → it opens `release: v0.X.Y` in the deploy repo.

### Phase D — Staging deploy + soak (`SafeZone-Deploy`)
- **D1.** Teardown staging — app + infra (leave external / platform services). 🟡
- **D2.** Plain-**merge** `preview/0.X.Y` → `staging` (no promote branch, no PR).
- **D3.** On `staging` (direct commits): set `values-staging` to `:0.X.Y` + fix env deltas.
- **D4.** `SETUP_INFRA` — bring up the staging infra.
- **D5.** Run `init-deploy.yml` (env=staging).
- **D6.** Run `/validate-release`. 🟡
- **D7.** Human verifies (UI + external connectivity).
- **D8.** On success → confirm the checklist on the `release: v0.X.Y` issue.
- **D9.** Start soak (3–5 days).

### Phase E — Archive (`SafeZone-Deploy`)
- **E1.** Run `/validate-soak`. 🟡
- **E2.** Confirm all `release: v0.X.Y` checklist items are done.
- **E3.** Tag `v0.X.Y-staging` on `staging` + PR `staging` → `main` (archive).
- **E4.** Close the `release: v0.X.Y` issue.

## 3. Exceptions & iteration *(off the happy path)*
- **Preview fix-loop**: a needed fix → back to **A** (new `0.X.Y-<sha>`), repoint preview, re-validate. **No tags move.**
- **Release recovery**: `main^2` resolved an unvalidated sha → re-run `release.yml` via `workflow_dispatch source_sha=<validated>`.
- **Staging rescue**: live breakage → pin ArgoCD `targetRevision` to last-good `v*-staging` (≥ floor) → forward-fix → un-pin. *(§8; never exercised.)*
- **Fast path**: change *provably* doesn't cross the deploy boundary → GATE 1 may suffice.
- **Hotfix**: **flow TBD** — today, forward-fix into the next patch via the normal flow.

---

**PART II — THE RATIONALE** *(why it's shaped this way)*

## 4. Core principles
1. **A tag is a certification, not a checkpoint** — cut after the highest-risk environment the change touches is green, never as an "I finished editing" marker.
2. **Soak / real traffic is post-release monitoring, never a pre-tag gate** — tag → deploy → *then* soak; soak fails → forward-fix.
3. **The gate is risk-proportional** — app-shaped change → compose + CI (**GATE 1**); boundary-shaped change → preview in-cluster (**GATE 2**, incl. a real browser pass + external-DNS probes for UI releases).
4. **Forward-fix only; tags are immutable** — never re-tag, never un-tag. A snapshot is a valid rollback target only *within its platform generation* (§8).
5. **One product version across app + deploy (for now)** — locked equal until the first post-release, app-unchanged config fix (§7).
6. **Everything goes through the preview gate; `hotfix/*` does NOT bypass it** — no prod SLA (showcase), so no urgency justifies shipping unvalidated.

## 5. Deployment model — hybrid + prerequisites
*This is **not** pure GitOps. Two halves: an imperative branch-promotion flow (GitHub Actions + PRs/tags) layered on GitOps reconciliation.*

- **ArgoCD owns steady-state reconcile.** Each `deploy/<env>/app/*.yaml` is an auto-sync `Application` (`targetRevision` = the env branch; `path` = `helm-charts/safezone-<layer>` + `values-<env>.yaml`). Helm renders **inside ArgoCD**, not as a CI pre-step.
- **Ordering, by layer** — ArgoCD's health-driven sync-waves don't span Applications or reliably gate Jobs:
  - **Infra** → ArgoCD-native **sync-waves** (`ApplicationSet`: foundation `-2` → security `1` → workloads `2` → init `3`).
  - **App** → **`init-deploy.yml`** applies the Application CRs in order and gates between phases on rollout/Job health (foundation → seed-schema → core → **3.5 smoke (hard gate)** → seed-cases → ui → scheduler[staging]). A phased *bootstrapper + gate*, not an imperative deployer — once a CR exists, ArgoCD reconciles it. (See ADR-9.)
- **Staging release deploy = teardown + rebuild** (not in-place rolling update). At 0.x the architecture still changes materially between releases, so an in-place path would carry per-release persistent-data / migration reasoning that doesn't pay off; a full rebuild is **deterministic** and **recovers in < 10 min**. Zero-downtime rolling replacement is a **product-phase direction**, deferred. *(Not yet exercised as written — §9.)*

**Prerequisites (runner + tooling access)**
- Self-hosted GitHub runner reaches the K3s API over the **Tailscale mesh**.
- `init-deploy.yml` mints a **2-hour, namespace-scoped SA token** (`<ns>-ci-sa`) via `scripts/ops/gen-kubeconfig.sh` — no long-lived admin kubeconfig.
- GHCR push/pull + cross-repo IssueOps writes use the `GHCR_TOKEN` PAT *(single-PAT scoping → GitHub-App is the graduation)*.
- GATE 2 / `/validate-*` probes hit the **public host** through NGF (real external path).

## 6. The IssueOps spine — freight → release lifecycle
**Purpose: provenance, not access control.** The issues make a deploy an evidence-based, traceable act and a poka-yoke against basis-less deploys. They are **not** a tamper-proof gate (labels are human-mutable; no separation of duties) — they guard against the *omission*, not a deliberate bypass (solo, no adversary).

- **`freight: 0.X.Y-<sha>`** (preview queue): opened by `publish-dev` when the merged PR carries the `freight` label (opt-in — most dev merges bundle toward a later validation; images publish regardless); `init-deploy` posts an automated checklist (does **not** stamp `validated`); `/validate-freight` stamps `validated` only on human sign-off (the **evidence comment** is the certification of record, the label is its machine index); `release.yml` requires the `validated` label, then closes it on promote.
- **`release: v0.X.Y`** (staging/archive queue): machine-opens on promote, human-closes when the archive PR merges. *(Direct commits on `staging` (D2/D3) drop the pre-merge PR review; the gate moves to post-deploy `/validate-release`, the audit trail is this issue + the merge commit.)*
- **Why issues, not GitHub Environments / Deployments API**: those gate *a workflow that deploys*, but the deploy is ArgoCD reconciling git (no workflow on the critical path) and they're per-repo (this handoff is cross-repo). IssueOps is the fitting pattern (ChatOps / branch-deploy lineage). The heavier primitives are **known-of, not studied** — research directions, not rejected options.

## 7. Versioning — one product version
- App + Deploy share one version (`appVersion == chart version`) **for now**; lockstep is a symptom of 0.x contract churn. Decouple at the first post-release, app-unchanged config fix (ADR-4).
- **`VERSION` bump discipline**: bumped **once at cycle open** (A1) on `dev` — it's the dev-image version prefix. The Deploy chart mirrors it. Two existing guards make a slip loud: `release.yml` fails if `VERSION` ≠ the tag; `init-deploy` errors if preview values pin more than one image tag.

## 8. Rollback & recovery
> Light by intent — most of this is **designed, not exercised**; enforcement is deferred.

- **Forward-fix only** (no automated rollback in 0.x); tags are the snapshots.
- **`staging` is dual-role** (soak + persistent demo) → in-place **rescue**: pin the staging ArgoCD `targetRevision` to the last-good `v0.X.Y-staging` tag, forward-fix on the branch, un-pin. **Never exercised** (§9).
- **Two tags**: `v0.X.Y` (archive, forward) · `v0.X.Y-staging` (rescue baseline, backward).
- **Rollback floor = `v0.3.6`** (ADR-8 T0): pre-NGF configs render retired `Ingress` → dead on the cluster, so below-floor tags are history, not rescue targets. **never-un-tag is universal** — "prune" removes rollback *eligibility* (floor filter / `rollback/*` alias), never the tag. **Enforcement (T1) deferred** → `.ai-session-drafts/2026-06-15-platform-rollback-wall.md`.

---

**PART III — STATUS**

## 9. Not yet verified / deferred *(delete as items clear)*
- **A–E restructure not yet exercised**: v0.3.6 ran a 4-phase, in-place staging promotion. The 5-phase / teardown-rebuild staging / frozen-pin release cut / plain-merge (no promote branch) are designed, not yet run.
- **`/validate-release` + `/validate-soak`**: 🟡 Planned, unbuilt (variants of `/validate-freight` against the staging host; soak adds time-based checks).
- **Hotfix flow**: TBD (forward-fix only for now).
- **Rollback rescue mechanic + floor T1**: designed/declared, never exercised; no NGF-valid rescue point until `v0.3.6-staging` is cut post-soak; T1 enforcement undecided.
- **ADR-6 dispatch mode**: only one cycle of evidence; consolidate later.
- **Settler SSOT reconciliation**: peer-reviewed by Gemini; not yet reconciled into `Docs/`.

## 10. Next: peer-review → SSOT reconciliation
Pioneer-owned formal process. Path: Architect + Gemini peer-review (flow done; this assembled doc pending) → swap `delivery-workflow.md` → Settler (Gemini) reconciles into `Docs/` SSOT (folding the per-repo predecessor docs) → prune §9 as items clear.

---

**APPENDIX**

## A. Architectural Decision Records (concise)

| ADR | Decision | Status |
| :- | :- | :- |
| 1 | Publish dev images `0.X.Y-<sha>` on `dev` merge (E1-fix) — preview validates a real artifact pre-tag | Accepted |
| 2 | Release = **promote-by-`crane copy`** (digest-identical), not rebuild | Accepted |
| 3 | Cut the tag **after preview validation**, not after soak (E2-fix) | Accepted |
| 4 | One product version; decouple just-in-time | Accepted (trigger pending) |
| 5 | Cross-repo validation record = **IssueOps freight issue** (not values-grep / Deployments API) | Accepted |
| 6 | Decouple version **tag** from the **promotion** (`workflow_dispatch`/`dry_run`) | Accepted, provisional |
| 7 | Release **opens** the `release: v0.X.Y` staging work-queue issue | Accepted |
| 8 | Rollback validity is **bounded by platform generation** (floor = `v0.3.6`) | T0 accepted; T1 deferred |
| 9 | **Hybrid deploy** — declarative reconcile (ArgoCD/infra) + imperative Job-gated orchestration (`init-deploy`, app) | Accepted |
| 10 | **Staging release deploy = teardown + rebuild** (not in-place); rolling replacement deferred to product phase | Accepted (unexercised) |
| 11 | **No `promote/<ver>-staging` branch** — plain-merge `preview`→`staging` + direct staging edits; audit via the `release` issue + merge commit | Accepted |
| 12 | **Validate skills stay focused** (not one branching skill); `/validate-release`, `/validate-soak` planned | Accepted |

> **ADR-2 note**: `release.yml` originally rebuilt from source (ephemeral runners held the validated image only in a local cache); ADR-1 dissolved that. `buildx imagetools create` re-wrapped single-arch sources in a new OCI index (different digest) → switched to `crane copy` (digest-preserving). Guarantees "shipped == validated", **not** build reproducibility (floating base tags).
> **ADR-9 note**: the pure-ArgoCD path (sync-waves + Job hooks) was tried (~2025) and failed — wave progression + hook completion both keyed off ArgoCD's Job-health assessment, which advanced before Jobs actually completed. Durable rationale = the problem-shape split (declarative convergence vs run-to-completion gating). **Revisit on hybrid pain, not on an ArgoCD release.**
