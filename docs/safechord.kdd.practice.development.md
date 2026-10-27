---
title: 'KDD 2.0: Development'
last_updated: '2026-10-27'
status: active
doc_version: 0.4.0
archetype: script
code_paths: []
---

# KDD 2.0 Practice: Two-Engine Development

> **Type**: Script (a mode page: takes the [practice](safechord.kdd.practice.md) as given)
> **Focus**: How a code change gets from a ticket to a merge on the **"Two-Engine"** model: a Pioneer seat for implementation and a Settler seat for review and solidification.
> **Constraint**: Nothing every mode shares: it is in the practice. How to dispatch and review is in the `pioneer-dispatch` skill, and how to write the PR body in the `pr-body` skill (`.claude/skills/` in the workspace harness). No template's skeleton or field meanings: they are in its file under `docs/templates/protocol/`.

> **⚙️ This page shares the practice's [adjustment period](safechord.kdd.practice.md)**: the two-engine seating, the ticket lifecycle and its protocol templates have not yet been through a full cycle, and its `doc_version` holds at v0.4.0 while the notice stands.

## Components {#components}

What this mode is made of. The sections below use them; how a skill carries out its step lives in the skill.

**Seats** (§1): the **Pioneer** implements; the **Settler** works the design out with the human, reviews, and keeps `Docs/`. A session holds one seat.

**Labels**:

| Label | Means | Where |
| :--- | :--- | :--- |
| `kdd:forward` | `Docs/` holds a blueprint for the area; reconciliation verifies the code against it | [§3.1](#31-choosing-the-path) |
| `kdd:spike` | No blueprint yet; reconciliation writes one where needed | [§3.1](#31-choosing-the-path) |
| `exec:settler` | The Settler executes the ticket alone; no agent review | [§3.3](#33-choosing-the-executor) |
| `mode:refactor` | Agreed by the human and the Settler when the ticket is opened. The branch takes the `refactor/` prefix, which switches the agents' refactor mode on: structural integrity outranks minimal diff, while the Scope still binds. A `type:refactor` ticket without the label is cut as `chore/` | — |
| `review:human` | On an `exec:settler` PR: the human is the only reviewer | [§3.3](#33-choosing-the-executor) |

**Protocols**: [the ticket](templates/protocol/ticket.md), [the commit](templates/protocol/commit.md), the handoffs between the seats (§2), and [the pull request](templates/protocol/development/pull-request.md), this mode's own.

**Skills** (`.claude/skills/` in the workspace harness):

| Skill | Who, and when | What it does |
| :--- | :--- | :--- |
| `pioneer-dispatch` | The Settler, once a labelled ticket is ready for the Pioneer | Checks the ticket's blockers and freshness, hands the ticket to the Pioneer (a headless coding-agent CLI, chosen in its `config.json`) on the ticket's branch, reviews what comes back through the handoffs until review passes or the round cap is reached, then opens the PR |
| `requirement-tests` | The Settler, on a `kdd:forward` ticket before dispatch, or on an `exec:settler` ticket that changes a requirement | Writes the tests that enforce the changed requirements, by checks drawn from the gaps earlier tickets fell through |
| `pr` | The Settler, once review passes, or once an `exec:settler` ticket's implementation is done | Writes the PR body from its template, opens the PR and waits for its CI. **Not built yet**: until it is, `pr-body` writes the body and `pioneer-dispatch` step 5 opens the PR |
| `solidification` | The Settler, once the human has merged | Reconciles as the path does (verifies the blueprint on `kdd:forward`, writes the result back on `kdd:spike`), writes the PR's SSOT feedback into `Docs/`, hands the checks deferred to release over to it, deletes the task's handoffs and local branch, checks the `(after merge)` Done When items and closes the ticket. **Not built yet**: until it is, the Settler does these by hand |

Steps no skill carries yet, written only on this page: review findings (§3.2) and `exec:settler` (§3.3).

---

## 1. The Two-Engine Model {#1-the-two-engine-model}

| Role | Capability Required | Core Responsibility |
| :--- | :--- | :--- |
| **🛡️ Pioneer** | Adequate implementation ability, good value for its cost, fast turnaround; failures are caught by tests | **Implementation & Problem Solving**: code, first-pass debugging. |
| **🧠 Settler** | Full comprehension, long-horizon work, strong review; the human answers for its mistakes | **Document stewardship & task review**. Before the ticket: discuss the design with the human, amend the blueprint, open the ticket. After it: code review, test planning, documentation reconciliation. |

**Capability Required is the contract.** Which carrier and model hold a seat is configuration: the Pioneer's is in `pioneer-dispatch`'s `config.json`, and the Settler is the attended session the human starts. Swap a carrier without touching the seat.

**`Docs/` belongs to the Settler.** The Pioneer writes only to its ticket's branch and its delivery handoff: every other repository, `Docs/` included, and the tickets and PRs are read-only to it.

**Seats are session-scoped, so that review never shares a context with the implementation it reviews.** A session takes its seat when it picks up the ticket and keeps it for its lifetime; changing seat means a new session, with a handoff carrying the context across.

**A Settler session may start a Pioneer session.** The Pioneer does not inherit the Settler's conversation; it is given what the task needs, such as the ticket and the handoffs.

**Exception: the Settler may carry a task in a single session.** After discussing it, the human and the Settler may have the Settler alone execute a task; the ticket then carries the label `exec:settler`. See [§3.3](#33-choosing-the-executor).

---

## 2. Handoffs Between the Seats {#handoffs-between-the-seats}

The seats pass the work through three handoff files, each written by one seat:

| File | Template | Written when |
| :--- | :--- | :--- |
| `-kickoff` | [kickoff](templates/protocol/development/kickoff.md) | By the Settler, once, before dispatch, when the ticket alone leaves the Pioneer short of context |
| `-delivery` | [delivery](templates/protocol/development/delivery.md) | By the Pioneer, on every delivery, updated in place |
| `-review` | [review](templates/protocol/development/review.md) | By the Settler, every review round, appended |

---

## 3. Dual-Track Workflow: The KDD Balance {#3-dual-track-workflow}

SafeChord employs a label-based **Dual-Track Workflow** to balance "Docs-First" rigor with "Spike-First" agility.

### 3.1 Choosing the path {#31-choosing-the-path}

The two paths are **not** told apart by how much planning happened up front. They are told apart by one question, answerable when the ticket is opened:

> **Does `Docs/` already hold a blueprint for this area?**

That answer decides what reconciliation *is* — a check, or an act of authorship.

| Path | Blueprint before work starts | Reconciliation is |
| :--- | :--- | :--- |
| `kdd:forward` | Yes | **Verification** — confirm the code matches the spec; amend the spec where it diverged |
| `kdd:spike` | No | **Authorship** — after discussing it with the human, write the result back as a new SSOT node where one is needed |

The label tells the Pioneer where to look: `kdd:forward` → read the blueprint first and implement to it; `kdd:spike` → do not go searching `Docs/`, it comes back empty.

The Settler opens and labels the ticket; the human adjusts it where needed.

### 🟢 Path A: `kdd:forward` (Order Mode)
Applied to optimizations of existing modules and known architecture extensions.
**Rule**: "Docs before Code"—no implementation without an updated blueprint.

**Strategic Design** (Settler):

1. Discuss and define the "Why/What" with the human
2. Update the blueprint, mainly the requirements that change, and ask the human whether the decision belongs in the decision log
3. Open the ticket from the [ticket template](templates/protocol/ticket.md) and label it `kdd:forward`; where the ticket has a milestone, set the blueprint's `app_version` to it
4. Cut the ticket's branch from the repository's integration branch
5. Commit on it, with `requirement-tests`, the tests that enforce the changed requirements, so that they bind the implementation
6. Write a kickoff handoff if one is needed
7. If the ticket is labelled `exec:settler`, implement it yourself ([§3.3](#33-choosing-the-executor)); otherwise hand it to the Pioneer with `pioneer-dispatch`
8. Open the PR with `pr`, and wait for the human to merge
9. Reconcile as the path does, and close the ticket, with `solidification`

**A ticket that changes no requirement** (documentation, or a refactor that keeps behavior) skips steps 2 and 5, and its reconciliation checks that the blueprint's wording still matches.

### 🔴 Path B: `kdd:spike` (Frontier Mode)
Applied to new tech integrations, unknown bug fixes, or performance stress tests.
**Rule**: "Code before Docs"—prototyping is privileged over documentation.

**Strategic Design** (Settler):

1. Discuss and define the "Why/What" with the human
2. Open the ticket from the [ticket template](templates/protocol/ticket.md) and label it `kdd:spike`
3. Cut the ticket's branch from the repository's integration branch
4. Write a kickoff handoff if one is needed
5. If the ticket is labelled `exec:settler`, implement it yourself ([§3.3](#33-choosing-the-executor)); otherwise hand it to the Pioneer with `pioneer-dispatch`
6. Open the PR with `pr`, and wait for the human to merge
7. Reconcile as the path does, and close the ticket, with `solidification`

**Both paths are developed by TDD**, whoever implements. On `kdd:forward` the work starts with the requirement tests already red; on `kdd:spike` the implementer writes the first tests itself.

**Tests on the Pioneer's side.** Beyond the requirement tests, the Pioneer writes whatever tests the work needs. A requirement test is the Settler's: where the Pioneer thinks one should change, it raises the change under Raised for the Settler in its [delivery handoff](templates/protocol/development/delivery.md), and the Settler decides. An accepted change is a test at fault ([§3.2](#32-handling-review-findings)): the Settler makes it, and the Pioneer resumes once it is in.

**Some problems cannot be fixed within the ticket.** The Pioneer neither fixes them nor opens a ticket: it writes what it found and why under Raised for the Settler in its delivery handoff, and continues with the rest of the work.

### 3.2 Handling review findings {#32-handling-review-findings}

**Review has a round cap**, set in `pioneer-dispatch`'s `config.json`. When the last round at the cap ends Returned, the Settler stops and reports; what follows is the human's decision.

**A requirement test that does not match the blueprint's requirement.** There are two cases:

1. The test is at fault
    1. The test is too loose: the Settler tightens it
    2. The test is too strict: the Settler loosens it, checking with particular care that it still holds the blueprint's requirement

    The Settler commits the change itself under the rules below, then hands back to the Pioneer to pass the tests:

    1. each change is a commit of its own
    2. it carries the trailer `Agent: Settler (requirement test)`
    3. the body states the reason
2. The blueprint is at fault: stop the task and ask the human to judge the situation

**A decision still to be made, or work outside this ticket.** Whether the Settler found it in review or it came from the Pioneer's handoff, the Settler opens a new ticket. It is linked in two places: the new ticket's Background points back at the original, so a later reader of the new ticket knows where it came from; the PR lists it under Follow-up tickets.

**Exception: fixes that change no behavior.** If a fix touches only comments or documentation and cannot change what the code does, the Settler commits it directly. If the Settler is not sure, it asks the human. The commit:

1.  stands alone, never folded into a Pioneer commit;
2.  carries the trailer `Agent: Settler (review fix)`;
3.  states in `Impact:` why the change affects no behavior, so it can be audited by reading.

### 3.3 Choosing the executor {#33-choosing-the-executor}

§3.1 decides what form the task takes. A separate question decides **who executes**:

**Almost always, the seats should stay separate.** Exceptions do happen, for reasons such as:

1. The human or the Settler can tell in advance that the Pioneer cannot finish the task, for example because
    1. the task covers too much ground
    2. the Pioneer cannot operate the tools needed to verify it
    3. the Pioneer's ability is judged certain to fall short
2. The task is mostly thinking and little implementation: for example, work that comes down to a few lines of code once the discussion is over

None of these conditions settles the matter on its own. The human and the Settler discuss the case in front of them and decide.

**What turns up during the work.** Under `exec:settler` there is no review, but [§3.2](#32-handling-review-findings) still governs what turns up during implementation: a requirement test that does not match the blueprint, and a decision still to be made or work outside the ticket. Its round cap and its review-fix exception do not apply.

**Review responsibility.** Separation exists so the session that did the work never reviews it. Under `exec:settler` that independence is gone, so the human takes over review explicitly and is accountable for it.

**The PR label.** The Settler opens the PR with the label `review:human` and the `exec:settler` header from the [pull request template](templates/protocol/development/pull-request.md).

**What was left unverified.** With no review file, what the Settler did not verify itself goes through the same sorting as a review's ([the pull request template](templates/protocol/development/pull-request.md)) before the PR is written.
