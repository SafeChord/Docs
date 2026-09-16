---
title: 'KDD 2.0: Two-Engine Collaboration'
doc_id: safechord.kdd.practice
last_updated: '2026-09-16'
status: active
authors:
  - bradyhau
  - Gemini CLI
  - Claude Opus 5
context_scope: Methodology
summary: Defines the Two-Engine collaboration model for SafeChord. Specifies the Pioneer and Settler seats and their current carriers, the dual-track workflow and its ticket lifecycle, the Git commit and handoff protocols, and the operational templates for each artifact.
keywords:
  - Two-Engine
  - Claude Code
  - Git Commit Protocol
  - Legacy Handoff
  - Ticket Lifecycle
logical_path: SafeChord.KDD.Practice
related_docs:
  - safechord.kdd.introduction.md
parent_doc: safechord.kdd.introduction
doc_version: 0.4.0
archetype: script
code_paths: []
---

# KDD 2.0 Practice: Two-Engine Development

SafeChord development runs on a **"Two-Engine"** model: a Pioneer seat for implementation and a Settler seat for review and solidification.

> **⚙️ This document is in an adjustment period.** The two-engine seating, the ticket lifecycle, and the templates in §4 were all introduced in v0.4.0 and have not yet been through a full cycle. Expect rough edges.
>
> **If a template or a step does not fit the work in front of you, say so rather than working around it silently.** A mismatch between this document and what actually happens is a defect in the document until it has been argued otherwise — raise it with the human, and it gets fixed here.
>
> **Do not bump `doc_version` while this notice stands.** The document holds at v0.4.0 until the adjustment period closes. Edits land under `last_updated` alone.

---

## 1. The Two-Engine Model

| Role | Capability Required | Current Carrier | Core Responsibility |
| :--- | :--- | :--- | :--- |
| **🛡️ Pioneer** | Implementation throughput; failures are caught by tests | Claude Code · **Opus 5 / medium effort** | **Implementation & Problem Solving**: code, spikes, complex debugging. |
| **🧠 Settler** | Repo comprehension and long-horizon focus; nothing else catches its mistakes | Claude Code · **Opus 5 / high effort** | **Owner of `Docs/`**, in both directions. Before the ticket: author the blueprint or draft, then open and label the ticket. After it: code review, test planning, documentation reconciliation, and driving the [delivery workflow](safechord.safezone.delivery.workflow.md). |

**Capability Required is the contract; Current Carrier is an implementation detail.** Swap a carrier without touching the seat.

**`Docs/` belongs to the Settler.** Pioneer is read-only there. A deviation found during implementation is finished in code first, then handed off for reconciliation.

**Seats are session-scoped.** One seat per session, held for its lifetime. Changing seat means a new session; carry the context across with a handoff. Code review therefore never shares a session with the implementation it reviews — the session that wrote the code holds Pioneer, and review is the Settler's.

**The default seat is Settler.** Pioneer is declared by the human at session start. An undeclared session does not write implementation code — ask first.

---

## 2. Communication Interface & Protocols

Standardized protocols carry information between agents and across sessions.

### 🎫 The Ticket
A ticket is the head of any implementation, and the anchor everything else is traced back to.
*   **Medium**: a GitHub issue in the repository the work lands in.
*   **Purpose**: the basis for implementation. It is the grain that commits (too fine) and the project docs (end state only) both miss.
*   **Required Content**: [see template](#-github-issue-template)

### 🟢 Basic Communication: Git Commit Protocol
*   **Medium**: git
*   **Purpose**: the fine-grained carrier during implementation.
*   **Format**: strict [Conventional Commits](https://www.conventionalcommits.org/).
*   **Required Content**: [see template](#-git-commit-template)

### 🔴 The Handoff Protocol
*   **Medium**: Markdown files stored in `.ai-session-handoffs/`.
*   **Purpose**: the carrier across AI tool sessions. The counterparty may be the next session or another agent.
*   **Example triggers**:
    - Pioneer completes a spike or phase of development.
    - An agent hits errors outside its operational scope.
    - Human intervention calls for a handover (usually once context has grown long enough to degrade).
*   **Required Content**: [see template](#-handoff-template)

### ⚪ Design Drafts
*   **Medium**: Markdown files stored in `.ai-session-drafts/`.
*   **Purpose**: continuity for forward-looking discussion that does not touch the codebase directly. Usually precedes opening a ticket.
*   **Required Content**: [see template](#-draft-template)

---

## 3. Dual-Track Workflow: The KDD Balance

SafeChord employs a label-based **Dual-Track Workflow** to balance "Docs-First" rigor with "Spike-First" agility.

### 3.1 Choosing the path

The two paths are **not** told apart by how much planning happened up front. They are told apart by one question, answerable when the ticket is opened:

> **Does `Docs/` already hold a blueprint for this area?**

That answer decides what reconciliation *is* — a check, or an act of authorship.

| Path | Blueprint before work starts | Reconciliation is |
| :--- | :--- | :--- |
| `kdd:forward` | Yes | **Verification** — confirm the code matches the spec; amend the spec where it diverged |
| `kdd:spike` | No | **Authorship** — write the result back as a new SSOT node |

The label tells the Pioneer where to look: `kdd:forward` → read the blueprint first and implement to it; `kdd:spike` → do not go searching `Docs/`, it comes back empty.

The Settler opens and labels the ticket; the human adjusts it where needed.

### 🟢 Path A: `kdd:forward` (Order Mode)
Applied to optimizations of existing modules and known architecture extensions.
**Rule**: "Docs before Code"—no implementation without an updated blueprint.

1.  **Strategic Design**: The human defines the "Why/What"; Settler updates the Markdown Knowledge Map (Blueprints/ADRs), then **opens the ticket and labels it `kdd:forward`**.
2.  **Implementation**: Pioneer reads the blueprint, then implements code and tests strictly within the defined boundaries.
3.  **Completion**: Pioneer submits PR and generates a Legacy Note.
4.  **Solidification**: Settler reviews the code against the pre-defined docs and merges. **Reconciliation is a verification pass; amend the blueprint if the code diverged, then close the ticket.**

### 🔴 Path B: `kdd:spike` (Frontier Mode)
Applied to new tech integrations, unknown bug fixes, or performance stress tests.
**Rule**: "Code before Docs"—prototyping is privileged over documentation.

1.  **Strategic Design**: The human discusses feasibility; Settler creates a Design Draft if codebase state is required, then **opens the ticket and labels it `kdd:spike`**.
2.  **Spike**: Pioneer implements a Demo/Spike without a blueprint to conform to.
3.  **Completion**: Pioneer submits PR and generates a detailed Legacy Note.
4.  **Solidification**: **Critical Phase.** Settler performs the PR review and executes **Documentation Reconciliation**, reverse-engineering the spike results back into the SSOT in `Docs/`. **Settle the ticket into a new project document and close it.**

---

### 3.2 Routing a review finding

Step 4 of both paths ends in review and then in merge. What happens in between is decided by one question:

> **Does fixing this require knowing why the code was written that way?**

| Route | Condition | Who acts |
| :--- | :--- | :--- |
| **Settler fixes it** | The file is byte-identical outside comment and documentation text | Settler commits on the PR branch |
| **Back to Pioneer** | Anything that condition excludes | Pioneer — how far back is below |
| **Deferred** | Not a defect: a decision, or work outside this ticket's scope | Open a ticket, link it, merge proceeds |

The first route's condition is mechanical, not a judgment call. If one byte that ansible, the kernel, or a runtime reads has changed, the finding is not on that route. Checking it takes the shape it took on `Chorde` PR #14: parse both versions and compare structure, then compare the sources with comments stripped.

Three obligations attach to that route, so a misroute is cheap to catch and cheap to undo:

1.  Review fixes are their own commit, never folded into a Pioneer commit.
2.  The trailer reads `Agent: Settler (review fix)`.
3.  The commit's `Impact:` and `Test:` fields carry the verification, so the human audits by reading rather than by re-running.

Once a finding is Pioneer's, how far back it goes depends on what the fix touches:

| The fix touches | Route |
| :--- | :--- |
| No test | Pioneer fixes it; no report needed |
| A test no page in `Docs/` points at | Pioneer fixes it; no report needed |
| A test that enforces a statement in `Docs/` | Scope change — back to the ticket |
| The blueprint itself | Open a new ticket |

**Delegating a fix to a subagent does not change the seat.** The human declares the seat at session start, so spawning one to write implementation code launders the seat rather than changing it. The same holds in the other direction: a subagent a Pioneer session spawns to read its own diff is a self-check, not review, because it cannot hold merge. Either seat may use subagents to organize its own work; neither can use one to stand in for the other party.

### 3.3 What `Docs/` owns, and what tests follow from it

A test either traces to a statement in `Docs/` or it does not, and that is the only distinction this workflow draws. **Tests are not assigned an owner.**

*   **Traces to `Docs/`** — loosening or deleting it is a change to the specification, and goes back to the ticket.
*   **Traces to nothing** — engineering's own. Whoever is working the code adds, changes and removes it freely.

What rises to `Docs/` as specification is what a product owner would hand an engineer: what the system must do, in the language of the product. Boundary cases, exception handling, defensive checks and refactor safety nets are engineering's own and are not itemized here.

**The correspondence is declared from the document, not from the test.** The page holding a specification lists the enforcing tests in its `code_paths`. A test no page points at is engineering's own by default, and needs no marker of its own.

This makes the two paths differ in timing without needing a separate rule for each:

*   `kdd:forward` — the specification exists before work starts, so the Settler writes its tests before the code does. It can only write them against the document, and that forced black box is the point.
*   `kdd:spike` — there is no specification yet, so the Pioneer writes every test. At reconciliation the Settler decides which of them encode a real constraint; those are adopted **as they are** and added to the page's `code_paths`, not rewritten.

A test adopted that way was written by its own author, so it carries none of the black-box property on the round that produced it. It gains it on the next one: from then on, loosening it is a change to the document.

**Deciding that something does _not_ rise to `Docs/` requires a reason. Deciding that it does, does not.** Promotion adds a red wall and costs the Settler the work of maintaining its test, so the standing incentive is to promote too little. The asymmetry is the counterweight, and the accumulated reasons are where the project's actual threshold becomes visible.

For a test that traces to `Docs/`, changing it is likewise not symmetric:

| Action | Stated in the commit |
| :--- | :--- |
| Adding a test | No |
| Tightening a condition | No |
| Loosening or deleting one | **Yes** |

Moving toward strictness carries no incentive to cheat; moving toward looseness does. The failure mode worth guarding against is not a plainly wrong condition — that exposes itself — but a roughly-right one loosened slightly and repeatedly, with no single step large enough to feel worth recording.

Separately, and for **any** test traced or not: **changing a test so that it passes is the review's first question.** Review reads the test diff apart from the code diff, which is the whole mechanism this needs.

---

## 4. Operational Templates (Appendices)

### 🎫 GitHub Issue Template
```markdown
## Background
[Why is this needed? What does the current state look like?]

## Scope
- In: [what this ticket touches]
- Out: [what is explicitly excluded]

## Done When
- [ ] [verifiable condition 1]
- [ ] [verifiable condition 2]
- [ ] Reconciliation complete

## References
- Blueprint: [`kdd:forward` only — link to the Docs/ page]
```

### 🟢 Git Commit Template
```text
<type>(<scope>): <subject> (50 chars max)

[Body: Why was this change needed?]
Explain the motivation and logic. Focus on "Why" rather than "How."
Describe the impact on project architecture or long-term decisions.

Context: [Ticket ID, or link to the Blueprint]
Impact: [Specific impact on API contracts or infra]
Test: [Verification executed] (e.g., make test-data-ingestor)
Agent: [Pioneer / Settler / Settler (review fix)]
Legacy: [Pending issues for the next agent]
```

### 🔴 Handoff Template
```markdown
# 📝 Legacy Note: [Task Name]

> **Date**: YYYY-MM-DD
> **From**: [Seat] / [session id or descriptor]
> **To**: [Seat] / [new session]
> **Trigger**: [Reactive: milestone | blocked | human handover] or [Deliberate: context degradation]
> **Ticket**: [Ticket ID]
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

### ⚪ Draft Template
```markdown
---
title: 'Design Draft: [Topic]'
doc_id: safechord.draft.[slug]
last_updated: 'YYYY-MM-DD'
status: draft
authors: [bradyhau, <agent>]
context_scope: [Methodology | Infrastructure | ...]
summary: [one paragraph on what this draft decides]
logical_path: SafeChord.Draft.[Name]
related_docs: []
archetype: script
doc_version: 0.1.0
---

# Design Draft: [Topic]

## 1. Background
[What is the problem, and what constrains it?]

## 2. Proposed Solution
[The proposal, with mock code or schemas where they help]

## 3. Alternatives Considered
[What else was weighed, and why it lost]

## 4. Trade-offs
[What cost is being accepted]

## 5. Next Steps
1. [ ] [next action]
```
