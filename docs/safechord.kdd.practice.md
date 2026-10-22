---
title: 'KDD 2.0: Practice'
last_updated: '2026-10-22'
status: active
doc_version: 0.4.0
archetype: script
code_paths: []
---

# KDD 2.0 Practice

> **⚙️ This document is in an adjustment period.** The two-engine seating, the ticket lifecycle, and the templates in §4 were all introduced in v0.4.0 and have not yet been through a full cycle. Expect rough edges.
>
> **If a template or a step does not fit the work in front of you, say so rather than working around it silently.** A mismatch between this document and what actually happens is a defect in the document until it has been argued otherwise — raise it with the human, and it gets fixed here.
>
> **Do not bump `doc_version` while this notice stands.** The document holds at v0.4.0 until the adjustment period closes. Edits land under `last_updated` alone.

## Modes {#modes}

SafeChord uses agents in several modes, told apart by what the work is and where the human stands. The protocols in §2 and the templates in §4 are shared by every mode; a mode's own seats and flow are on the page the table names.

| Mode | What it covers | Where the human stands | How the agents work | Defined in |
| :--- | :--- | :--- | :--- | :--- |
| Discussion | Work with no ticket yet, and work on `Docs/` and the harness, which commit straight to `main` | Present throughout, deciding together | One agent in conversation with the human; the outcome is a ticket, a design draft, or a change to `Docs/` or the harness | This document |
| Development | A code change that lands in SafeZone, SafeZone-Deploy or Chorde through a branch, a PR and a merge, on a ticket labelled `kdd:forward` or `kdd:spike` | The last gatekeeper, looking once before merge | Two seats that check each other | [Development](safechord.kdd.practice.development.md) |
| Delivery | Cutting, validating and promoting a SafeZone release: a phase or route of the delivery workflow | Present throughout, signing off every gate | One agent working with the human | [Delivery](safechord.kdd.practice.delivery.md) |
| Operations | Not yet defined | Not yet defined | Not yet defined | — |

### Finding your mode {#finding-your-mode}

A session judges its own mode against the descriptions above; no rule maps a ticket to a mode.

- **State it before acting**: "this is <mode>, because <reason>". The reason names what decided it: the ticket and its labels, the repository the work lands in and how that repository takes changes, what the human asked. The stated mode is what lets the human catch a wrong call.
- **With no ticket in hand, the mode is Discussion.**
- **When no mode fits, or more than one does, ask the human** before acting. Work that fits no mode is not bent into the nearest one.
- **The mode changes with the work.** Opening or picking up a ticket is where it usually changes; state the new mode then.
- **A session started by a script** (`pioneer-dispatch`, a CI job) takes its mode and seat from the prompt that started it, and does not judge.

### Sessions and seats {#sessions-and-seats}

- A mode that has seats defines them on its page, with how long a session holds one. A session that enters such a mode takes the seat its work there needs.
- Whatever reports back to the session that started it, such as a subagent or a tool run, works under that session's mode and seat and holds none of its own.
- Where a template asks for a seat, a session in a mode without seats gives its mode instead (`Agent: Discussion`).

---

## 1. The Two-Engine Model {#1-the-two-engine-model}

Moved to [Development §1](safechord.kdd.practice.development.md#1-the-two-engine-model).

---

## 2. Communication Interface & Protocols

Standardized protocols carry information between agents and across sessions.

### 🎫 The Ticket
A ticket is the head of any implementation, and the anchor everything else is traced back to.

*   **Medium**: a GitHub issue in the repository the work lands in.
*   **Purpose**: the basis for implementation. It is the grain that commits (too fine) and the project docs (end state only) both miss.
*   **Weight**: a ticket is near-permanent, so it holds only what has trace value for a later reader: the problem, the decisions and their reasons, the scope, and Done When. Context that only aligns the seats for this task (inferred mechanisms, investigation detail, design suggestions, unverified items, implementation order) goes in the handoff. Done When lists only what can be verified before merge; what can be verified only after deployment belongs to a gate in the [delivery workflow](safechord.kdd.practice.delivery.md).
*   **Done When states intent, not shape**: write what must hold of the result ("the logger's output is unchanged except for `worker_id`", "no assertion or test input changes"), not what the diff or the names look like ("field names are unchanged", "the diff touches only imports"). A condition written as a shape is met by the wrong change and broken by the right one, and contradicts the Scope the first time it allows a rename.
*   **Freshness**: a ticket opened before the work starts is checked again before it does, against the blueprint and the code as they now stand. A reference to a section since rewritten, or a current state that later tickets have changed, is corrected on the ticket first.
*   **Branch**: `<type>/issue-<issue_no>-<slug>`, `<type>` being the commit type of the change. The `refactor/` prefix is reserved for a ticket labelled `mode:refactor`, which the human and the Settler agree on when the ticket is opened: that prefix switches the agents' refactor mode on, under which structural integrity outranks minimal diff while the Scope still binds. A `type:refactor` ticket without the label is cut as `chore/`.
*   **Required Content**: [see template](#github-issue-template)

### 🟢 Basic Communication: Git Commit Protocol
*   **Medium**: git
*   **Purpose**: the fine-grained carrier during implementation.
*   **Format**: strict [Conventional Commits](https://www.conventionalcommits.org/).
*   **Required Content**: [see template](#git-commit-template)

### 🔴 The Handoff Protocol {#the-handoff-protocol}
*   **Medium**: Markdown files stored in `.ai-session-handoffs/`.
*   **Purpose**: the carrier across AI tool sessions. The counterparty may be the next session or another agent.
*   **Example triggers**:
    - Pioneer completes a spike or phase of development.
    - An agent hits errors outside its operational scope.
    - Human intervention calls for a handover (usually once context has grown long enough to degrade).
*   **Between the seats**: development's three files are in [Development §2](safechord.kdd.practice.development.md#handoffs-between-the-seats).
*   **Lifecycle**: a handoff lives with its task. Delete it once the PR is merged, the ticket is closed, and reconciliation has landed in `Docs/`; the harness git history keeps it recoverable.
*   **Linking**: the handoff points at the ticket, never the reverse. Anyone who can read a handoff can reach the ticket, but a ticket reader may not see the handoff, and a link on a permanent ticket would dangle once the handoff is deleted.
*   **Naming**: when a ticket exists, the filename carries `<repo>-<issue_no>` in lowercase (e.g. `2026-09-19-safezone-64-worker-offset-commit.md`).
*   **Resuming**: a session handed off on a reactive trigger can be resumed with the note's `Resume:` command, for example to fix review findings. A session handed off for context degradation is retired and not resumed.
*   **Required Content**: [see template](#handoff-template)

### 🟣 The Pull Request {#the-pull-request}
Moved to [Development §2](safechord.kdd.practice.development.md#the-pull-request).

### ⚪ Design Drafts
*   **Medium**: Markdown files stored in `.ai-session-drafts/<domain>/`.
*   **Purpose**: continuity for forward-looking discussion that does not touch the codebase directly. Usually precedes opening a ticket.
*   **Domains**:
    - `kdd/` (practice, seats, review flow)
    - `delivery/` (release workflow, gates, soak)
    - `platform/` (networking, ingress, security, observability)
    - `app/` (SafeZone code: debugging and improvement)
*   **Required Content**: [see template](#draft-template)

---

## 3. Dual-Track Workflow: The KDD Balance {#3-dual-track-workflow}

Moved to [Development §3](safechord.kdd.practice.development.md#3-dual-track-workflow), with its subsection numbers and ids unchanged.

---

## 4. Operational Templates (Appendices)

### 🎫 GitHub Issue Template {#github-issue-template}
```markdown
## Background
[Why is this needed? What does the current state look like?]

## Scope
- In: [what this ticket touches]
- Out: [what is explicitly excluded]

## Done When
- [ ] [verifiable condition 1]
- [ ] [verifiable condition 2]
- [ ] Reconciliation complete (`kdd:spike`: or confirmed with the human that none is needed)

## References
- Blueprint: [`kdd:forward` only — link to the Docs/ page]
```

The reconciliation item is the one Done When ticked after merge: it is the last step of the flow, not a condition the PR can show.

### 🟢 Git Commit Template {#git-commit-template}
```text
<type>(<scope>): <subject> (50 chars max)

[Body: Why was this change needed?]
Explain the motivation and logic. Focus on "Why" rather than "How."
Describe the impact on project architecture or long-term decisions.

Context: [Ticket ID, or link to the Blueprint]
Impact: [Specific impact on API contracts or infra]
Test: [Verification executed] (e.g., make test-data-ingestor)
Agent: [Pioneer / Settler / Settler (review fix) / Settler (requirement test), or the mode where it has no seats]
Legacy: [Pending issues for the next agent]
```

### 🔴 Handoff Template {#handoff-template}
```markdown
# 📝 Legacy Note: [Task Name]

> **Date**: YYYY-MM-DD
> **From**: [Seat, or the mode where it has none] / [Carrier] / [session id]
> **Resume**: [command that resumes this session in its tool]
> **To**: [Seat, or the mode where it has none] / [new session, or blank if not yet known]
> **Trigger**: [Reactive: milestone | blocked | human handover] or [Deliberate: context degradation]
> **Ticket**: [<repo>-<issue_no>, e.g. safezone-64; blank if none]
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

Development's templates, for the handoffs between the seats and for the pull request, are in [Development §4](safechord.kdd.practice.development.md#4-development-templates).

### ⚪ Draft Template {#draft-template}
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
