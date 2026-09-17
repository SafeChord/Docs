---
title: 'KDD 2.0: Two-Engine Collaboration'
doc_id: safechord.kdd.practice
last_updated: '2026-09-17'
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
| **🛡️ Pioneer** | Implementation throughput; failures are caught by tests | Antigravity CLI · **Gemini Flash / high effort** | **Implementation & Problem Solving**: code, spikes, complex debugging. |
| **🧠 Settler** | Repo comprehension and long-horizon focus; nothing else catches its mistakes | Claude Code · **Opus / high effort** | **Owner of `Docs/`**, in both directions. Before the ticket: author the blueprint or draft, then open and label the ticket. After it: code review, test planning, documentation reconciliation, and driving the [delivery workflow](safechord.safezone.delivery.workflow.md). |

**Capability Required is the contract; Current Carrier is an implementation detail.** Swap a carrier without touching the seat.

**The Pioneer leans toward working on its own; the Settler leans toward working with the human in the loop.** A Pioneer usually carries a ticket through without the human. A Settler brings a decision to the human whenever it is not clearly its own to make.

**`Docs/` belongs to the Settler.** Pioneer is read-only there. A deviation found during implementation is finished in code first, then handed off for reconciliation.

**Seats are session-scoped.** One seat per session, held for its lifetime. Changing seat means a new session; carry the context across with a handoff. Code review therefore never shares a session with the implementation it reviews — the session that wrote the code holds Pioneer, and review is the Settler's.

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
*   **Both directions**: GitHub carries the summary and the handoff carries the detail.
    - Pioneer → Settler: the PR description, plus a handoff every time.
    - Settler → Pioneer: a PR review comment. Add a handoff only when the Pioneer session cannot be resumed and a new session has to start without its context.
*   **Resuming**: a session handed off on a reactive trigger can be resumed with the note's `Resume:` command, for example to fix review findings. A session handed off for context degradation is retired and not resumed.
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

1.  **Strategic Design**: The human defines the "Why/What"; Settler updates the Markdown Knowledge Map (Blueprints/ADRs) and writes the tests that enforce the blueprint's TDD Convergence Boundaries (the section listing the constraints tests must hold), then **opens the ticket and labels it `kdd:forward`**.
2.  **Implementation**: Pioneer reads the blueprint and implements code that passes those tests, adding its own tests as the work needs, strictly within the defined boundaries.
3.  **Completion**: Pioneer submits PR and generates a Legacy Note.
4.  **Solidification**: Settler reviews the code against the pre-defined docs and merges. **Reconciliation is a verification pass; amend the blueprint if the code diverged, then close the ticket.**

### 🔴 Path B: `kdd:spike` (Frontier Mode)
Applied to new tech integrations, unknown bug fixes, or performance stress tests.
**Rule**: "Code before Docs"—prototyping is privileged over documentation.

1.  **Strategic Design**: The human discusses feasibility; Settler creates a Design Draft if codebase state is required, then **opens the ticket and labels it `kdd:spike`**.
2.  **Spike**: Pioneer implements a Demo/Spike without a blueprint to conform to, and writes all of its tests.
3.  **Completion**: Pioneer submits PR and generates a detailed Legacy Note.
4.  **Solidification**: **Critical Phase.** Settler performs the PR review and executes **Documentation Reconciliation**, reverse-engineering the spike results back into the SSOT in `Docs/`. Constraints worth keeping become the new document's TDD Convergence Boundaries; spike tests that already enforce them are kept as written. **Settle the ticket into a new project document and close it.**

### 3.2 Handling review findings

Review reads the test diff separately from the code diff. A test changed so that it passes is the first thing to question.

**Findings go back to the Pioneer** as a PR review comment (see the [handoff protocol](#-the-handoff-protocol)). The Pioneer fixes them on the PR branch, including any tests the fix needs, and the Settler reviews again before merging.

**Some findings cannot be fixed within the ticket.** The Pioneer does not edit or open tickets: it comments on the current ticket with what it found and why, and continues with the rest of the work. The Settler handles the ticket side:

| The finding | Settler |
| :--- | :--- |
| The fix requires loosening a constraint in the blueprint's TDD Convergence Boundaries, or a test that enforces one | Takes it to the human before any fix |
| The blueprint itself is wrong | Opens a new ticket for the blueprint |
| It is a decision still to be made, or work outside this ticket | Opens a new ticket, links it, and merges the PR without it |

**Exception: fixes that change no behavior.** If a fix touches only comments or documentation and cannot change what the code does, the Settler commits it directly. If the Settler is not sure, it asks the human. The commit:

1.  stands alone, never folded into a Pioneer commit;
2.  carries the trailer `Agent: Settler (review fix)`;
3.  states in `Impact:` why the change affects no behavior, so it can be audited by reading.

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
> **From**: [Seat] / [Carrier] / [session id]
> **Resume**: [command that resumes this session in its tool]
> **To**: [Seat] / [new session, or blank if not yet known]
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
