---
title: 'KDD 2.0: Two-Engine CLI & Headless Collaboration'
doc_id: safechord.kdd.practice
last_updated: '2026-09-12'
status: active
authors:
  - bradyhau
  - Gemini CLI
  - Claude Opus 5
context_scope: Methodology
summary: Defines the Two-Engine collaboration model for SafeChord. Seats are assigned by whether failure announces itself: implementation is fenced by TDD and runs at lower effort, while review and reconciliation have no executable oracle and take the strongest model in an isolated session. Covers the dual-track workflow, ticket lifecycle, and handoff protocols.
keywords:
  - Two-Engine
  - Claude Code
  - Git Commit Protocol
  - Headless Development
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

# KDD 2.0 Practice: Two-Engine & Headless Development

SafeChord development runs on a **"Two-Engine"** model: the human holds the Architect seat, and two AI seats split the work by whether their failures announce themselves.

---

## 1. The Two-Engine Model

### 1.1 Seats

| Role | Capability Required | Current Carrier | Core Responsibility |
| :--- | :--- | :--- | :--- |
| **🏛️ Architect** | — | **Human** | **Strategy & Trade-offs**: priorities, tech stack, what gets built and why. |
| **🛡️ Pioneer** | Implementation throughput; failures are caught by tests | Claude Code · **Opus 5 / medium effort** | **Implementation & Problem Solving**: code, spikes, complex debugging. |
| **🧠 Settler** | Repo comprehension and long-horizon focus; nothing else catches its mistakes | Claude Code · **Opus 5 / high effort** | **Review & Solidification**: test planning, code review, documentation reconciliation. |

**Capability Required is the contract; Current Carrier is an implementation detail.** A carrier can be swapped without touching the seat. The previous revision bound seats to product names, and when one product was discontinued the role definition had no field that turned red — the outage went unnoticed for three months.

### 1.2 Why the seats split this way

Review draws the stronger configuration, not implementation. This inverts the intuition that implementation is the hard part.

| | Executable oracle | Failure mode | Consequence |
| :--- | :--- | :--- | :--- |
| **Implementation** | Yes — tests, the thing runs or does not | Loud, immediate | A weaker configuration is survivable; errors self-report |
| **Review / reconciliation** | None | Silent, surfaces weeks later | Requires the strongest configuration available |

Implementation errors hit the **Physical Red Walls** that `safechord.kdd.introduction.md` §3 describes. Review has no equivalent wall — the model is the only line of defence.

> **The dichotomy is a simplification.** An oracle catches "does it run"; it does not catch architecture drift, a re-implemented utility, or a cross-repo contract quietly altered. Implementation has silent failures too, and they cluster in repo comprehension — which is why the Pioneer seat lowers effort rather than model tier.

### 1.3 The Settler runs in its own session

Even when both seats run on the same product, **the Settler must be a separate session.**

The reason has nothing to do with model strength: a review sharing context with the implementation inherits the implementer's blind spots. A session that just finished writing a piece of code is the session least qualified to review it.

This makes deliberate session rotation a protocol requirement rather than personal hygiene — see §2's handoff triggers.

---

## 2. Communication Interface & Protocols

In a headless environment, standardized protocols are essential for information exchange between agents.

### 🟢 Basic Communication: Git Commit Protocol
For routine iterations without formal handoffs, the **Git Commit Message** is the bridge between agents and humans.
*   **Principle**: Messages must include "Intent" and "Architectural Impact."
*   **Format**: Strict adherence to [Conventional Commits](https://www.conventionalcommits.org/).
*   **Agent Obligation**: Settler reviews the commits filed under a ticket. Before tickets existed this was an inference from commit history; it is now a query.

### 🔴 The Handoff Protocol (Legacy Notes)
*   **Medium**: Markdown files stored in `.ai-session-handoffs/`.
*   **Counterparty**: The next session, or another agent. **Both are the same act** — work continues in a context that does not contain the current one.
*   **Trigger Conditions**: two kinds, and both must be honoured.

    **Reactive** — something external forces the transfer:
    - Pioneer completes a spike or phase of development.
    - An agent hits errors outside its operational scope.
    - Human intervention requires a task handover.

    **Deliberate** — the session is ended on purpose:
    - Context has grown long enough to degrade, and a fresh session should continue. **This is the most frequent trigger in practice**, and it usually means the same agent in a new session, not a different agent.

*   **Sufficiency test**: the note must carry enough that discarding the current context is safe. Not a complete record — a sufficient one.
*   **Required Content**:
    1.  **Status/Summary**: Date, direction (From/To), branch status, and progress.
    2.  **What Changed**: File paths and core structural changes.
    3.  **Verified Path**: What has been proven to work? (Crucial for deadlock handoffs).
    4.  **Unverified / Uncertain**: What was not checked, and what the author is unsure of.
    5.  **Next Actions**: Clear instructions and verification criteria for the next agent.

> **⚠️ Who writes the note.** A Legacy Note is lossy compression — an entire session squeezed into a few hundred words. When the trigger is context degradation, the note is authored by the session in its worst state, and what it omits is never discovered. That is the textbook shape of a silent failure.
>
> Three mitigations, cheapest first: (1) the **Unverified / Uncertain** field above, which forces blind spots to be named — it fills the gap between "proven" and "known dead end"; (2) checkpoint on a schedule rather than on hitting a wall; (3) have a clean session reconstruct state from the ticket's commits and diffs instead of trusting the old session's self-report. The third only became practical once tickets bounded *which* commits to read.

> **Quota note**: context growth raises input tokens every turn and is the quietest drain on the weekly allowance. Rotating sessions is a cost control, not only a quality one.

### ⚪ Design Drafts
For strategic decisions or complex refactoring, a **Design Draft** serves as the blueprint for the Pioneer.
*   **Medium**: Markdown files stored in `.ai-session-drafts/`.
*   **Required Content**: Background, Proposed Solution, Blueprint (mock code/schemas), Trade-offs, and Next Steps.

---

## 3. Dual-Track Workflow: The KDD Balance

SafeChord employs a label-based **Dual-Track Workflow** to balance "Docs-First" rigor with "Spike-First" agility.

### 3.1 The discriminator sits at the back end

The two paths are **not** told apart by how much planning happened up front. They are told apart by one question, answerable when the ticket is opened:

> **Does `Docs/` already hold a blueprint for this area?**

That answer decides what reconciliation *is* — a check, or an act of authorship.

| Path | Blueprint before work starts | Reconciliation is |
| :--- | :--- | :--- |
| `kdd:forward` | Yes | **Verification** — confirm the code matches the spec; amend the spec where it diverged |
| `kdd:spike` | No | **Authorship** — write the result back as a new SSOT node |

> **A Design Draft does not make a task `kdd:forward`.** Path B step 1 explicitly produces one. A draft holds *a decision not yet made* — a hypothesis, not a contract. "Without documentation constraints" means no `Docs/` blueprint the code must conform to; it has never meant "write nothing down first."

### 3.2 The ticket

**Both paths open a ticket**, before implementation starts. It serves three purposes:

1.  **Provisional identity**: a spike explores a node that does not exist on the knowledge tree yet, so there is no `doc_id` to anchor to. The ticket fills that vacuum until reconciliation settles it into one.
2.  **Traceability**: `doc_id` records the end state, ADRs record only the path that worked, commits are too granular, and a Legacy Note fires only on exceptions. Nothing else holds *one thing from start to finish*. `safechord.kdd.introduction.md` §4 promises that every adjustment leaves a trace; this is the missing grain.
3.  **Agent boundary**: a stable container that spans sessions. A ticket may collect many Legacy Notes — the ticket is the container, a handoff is the baton.

**Close condition, uniform across both paths: reconciliation complete.** A ticket's lifetime therefore equals one unit of knowledge travelling from undefined to settled.

Changes with no documentation impact — CI bumps, path fixes, dependency chores — carry no `kdd:` label, skip reconciliation, and close on merge.

> **The label's job is to tell the Pioneer whether a spec exists to conform to**, not to predict difficulty. `kdd:forward` → read the blueprint first and implement to it. `kdd:spike` → do not go looking in `Docs/`; the search would come back empty.
>
> The label applied at ticket-open is a guess. The Settler learns the truth during reconciliation, and a `kdd:forward` ticket whose blueprint had to be rewritten was really a spike. **The flip rate is itself a measurement** — of how mature the knowledge tree actually is. The label earns its keep by being falsifiable, not by being right.

### 🟢 Path A: `kdd:forward` (Order Mode)
Applied to optimizations of existing modules and known architecture extensions.
**Rule**: "Docs before Code"—no implementation without an updated blueprint.

1.  **Strategic Design**: Architect defines the "Why/What"; Settler updates the Markdown Knowledge Map (Blueprints/ADRs). **Ticket opened and labelled `kdd:forward`.**
2.  **Implementation**: Pioneer reads the blueprint, then implements code and tests strictly within the defined boundaries.
3.  **Completion**: Pioneer submits PR and generates a Legacy Note.
4.  **Solidification**: Settler reviews the code against the pre-defined docs, merges, and tags the version. **Reconciliation is a verification pass; amend the blueprint if the code diverged, then close the ticket.**

### 🔴 Path B: `kdd:spike` (Frontier Mode)
Applied to new tech integrations, unknown bug fixes, or performance stress tests.
**Rule**: "Code before Docs"—prototyping is privileged over documentation.

1.  **Strategic Design**: Architect discusses feasibility; Settler creates a Design Draft if codebase state is required. **Ticket opened and labelled `kdd:spike`.**
2.  **Spike**: Pioneer implements a Demo/Spike without a blueprint to conform to.
3.  **Completion**: Pioneer submits PR and generates a detailed Legacy Note.
4.  **Solidification**: **Critical Phase.** Settler performs the PR review and executes **Documentation Reconciliation**, reverse-engineering the spike results back into the SSOT in `Docs/`. **Settle the ticket into a `doc_id` and close it.**

> **⚠️ No enforcement point exists yet.** Nothing requires the label to be applied, and nothing requires an agent to read it. Per the KDD layer, a constraint with no trigger does not execute. The labels were created to be exercised first and instrumented second — if a cycle passes with no observable effect, the finding is that this signal needs wiring into `.ai-rules.md`, not that the signal is worthless.

---

## 4. Headless Collaboration Rules

*   **Terminal as SSOT**: All development and testing are completed in the CLI. IDEs are for visual review only.
*   **Review is Documentation**: Settler's review approval implicitly signals that documentation reconciliation is synchronized. A ticket that cannot be closed is therefore a visible measure of documentation debt — the drift stops being silent.
*   **Context Efficiency**: Agents must leverage their massive context windows for cross-service impact analysis to prevent API contract breakage.

---

## 5. Operational Templates (Appendices)

### 🟢 Git Commit Template
```text
<type>(<scope>): <subject> (50 chars max)

[Body: Why was this change needed?]
Explain the motivation and logic. Focus on "Why" rather than "How."
Describe the impact on project architecture or long-term decisions.

Context: [Ticket ID, or link to the Blueprint]
Impact: [Specific impact on API contracts or infra]
Test: [Verification executed] (e.g., make test-data-ingestor)
Agent: [Pioneer / Settler — name the carrier if it is not the default]
Legacy: [Pending issues for the next agent]
```

### 🔴 Handoff Template (Legacy Note)

`From` / `To` carry **both** the seat and the session. The most common handoff is same seat, new session — the template must be able to say so.
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
