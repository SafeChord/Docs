---
title: 'KDD: Collaboration Model Changelog'
doc_id: safechord.kdd.changelog
status: active
authors:
  - bradyhau
  - Gemini CLI
  - Claude Opus 5
last_updated: '2026-09-13'
summary: Records how the SafeChord collaboration model itself changed — the seating, the workflow, and the protocols. Each entry states the decision, what it replaced, and what was rejected, so that a spec no longer in force is still recoverable.
keywords:
  - KDD
  - Changelog
  - Collaboration Model
  - Seats
  - Design History
logical_path: SafeChord.KDD.Changelog
related_docs:
  - safechord.kdd.practice.md
  - safechord.kdd.introduction.md
parent_doc: safechord.kdd.introduction
doc_version: 0.4.0
---

# KDD Collaboration Model Changelog

`practice.md` is an `archetype: script` and states only the procedure in force. This file
holds what that document structurally cannot: the shape the model used to have, and why it
stopped having it.

## What belongs in an entry

Three things, and nothing else:

*   **Decision** — what the model now does.
*   **Replaces** — the shape that was in force before.
*   **Rejected** — the alternatives weighed, and why they lost.

A diff summary does not belong here. Git already holds the change and the reasoning per
commit; an entry exists for what no single commit can hold — a decision spanning several
files, two repositories, and a conversation that produced neither.

## When an entry is written

**On the version settling, not on the change.** While a version carries an adjustment
notice it is amended a few lines at a time, and an entry per amendment would turn this file
into a churn log. Until the notice comes down, the reasoning lives in the drafts under
`.ai-session-drafts/` and in `git log -- docs/safechord.kdd.practice.md`.

---

## 🔖 [v0.4.0] — in adjustment

**The two-engine model.** No entry yet. The adjustment notice in `practice.md` is still
standing and the model is still moving; this entry lands when the notice comes down.

Sources in the meantime: `.ai-session-drafts/2026-09-12-engine-realignment-and-model-routing.md`,
`.ai-session-drafts/2026-09-12-practice-reconciliation-plan.md`, and the commits from
`14ebec0` onward on `practice.md`.

---

## 🔖 [v0.3.5] - 2026-05-02

### English-First SSOT

*   **Decision**: English becomes the source of truth for the whole knowledge base; the
    Traditional Chinese set becomes a mirror, held at structural parity and carrying the
    KDD 2.0 glossary (Settler → 維護者, Pioneer → 開拓者).
*   **Replaces**: a Chinese-first set with English as a partial secondary.
*   **Rejected**: not recorded at the time.

---

## 🔖 [v0.3.0] - 2026-04-23 → 2026-04-29

### The three-engine model, on split carriers

*   **Decision**: three seats across two vendors. **Architect** held strategy, **Pioneer**
    (Claude Code) held implementation and opened PRs, **Settler** (Gemini CLI) held PR
    review, merging, version tagging, issue closing, and documentation reconciliation.
    Seats were identified by their carrier: the vendor *was* the role.
*   **Replaces**: an undivided agent workflow with no seat boundary.
*   **Rejected**: not recorded at the time. The heterogeneity argument for the split — two
    vendors fail differently, so a reviewer on a different engine does not inherit the
    implementer's blind spots — is reconstructed from the seating, not from a written
    decision.

### Knowledge-Driven over Spec-Driven

*   **Decision**: documents hold Why, What, and ADRs; API schemas, contracts, and test
    cases live in the codebase as executable boundaries. TDD becomes the convergence
    boundary that bounds AI implementation freedom. The knowledge map is physical Markdown
    in a tree.
*   **Replaces**: Spec-Driven development, where documents dictated implementation detail.
*   **Rejected**: a Vector DB / RAG knowledge store, for retrieval loss — probabilistic
    chunk similarity lets an agent rediscover knowledge it already has, or mix unrelated
    modules. A physical tree makes parent-child relationships absolute.

### Design Draft split from the Handoff Protocol

*   **Decision**: two artifacts. A handoff carries work in flight backwards; a draft carries
    a decision forwards, before implementation begins.
*   **Replaces**: one combined protocol covering both.
*   **Rejected**: not recorded at the time.

---

## Before v0.3.0

The v0.1.0 documents survive in full under `archive/kdd/v0.1.0/`. No entries were kept for
that era; `git log` is the only record of why it changed.
