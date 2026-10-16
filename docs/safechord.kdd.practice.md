---
title: 'KDD 2.0: Two-Engine Collaboration'
doc_id: safechord.kdd.practice
last_updated: '2026-10-16'
status: active
authors:
  - bradyhau
  - Gemini CLI
  - Claude Opus 5
  - Claude Opus 5.5
context_scope: Methodology
summary: Defines the Two-Engine collaboration model for SafeChord development, from discussion through merge and ticket close. Specifies the Pioneer and Settler seats and their current carriers, the dual-track workflow and its ticket lifecycle, the Git commit, handoff and pull request protocols, and the operational templates for each artifact.
keywords:
  - Two-Engine
  - Claude Code
  - Git Commit Protocol
  - Legacy Handoff
  - Ticket Lifecycle
  - Pull Request
logical_path: SafeChord.KDD.Practice
related_docs:
  - safechord.kdd.introduction.md
  - safechord.safezone.delivery.workflow.md
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

SafeChord uses agents in several modes, told apart by where the human stands. The protocols in §2 and the templates in §4 are shared by every mode; the seats in §1 and the flow in §3 belong to development alone, and end at merge and ticket close.

| Mode | Where the human stands | How the agents work | Defined in |
| :--- | :--- | :--- | :--- |
| Discussion | Present throughout, deciding together | One agent in conversation with the human; the outcome is a ticket, a design draft, or a change to `Docs/` | This document, §2 |
| Development | The last gatekeeper, looking once before merge | Two seats that check each other | This document, §1 and §3 |
| Release | Present throughout, signing off every gate | One agent working with the human | [Delivery workflow](safechord.safezone.delivery.workflow.md) |
| Live operations | Not yet defined | Not yet defined | — |

---

## 1. The Two-Engine Model

| Role | Capability Required | Current Carrier | Core Responsibility |
| :--- | :--- | :--- | :--- |
| **🛡️ Pioneer** | Adequate implementation ability, good value for its cost, fast turnaround; failures are caught by tests | opencode (headless), through OpenRouter · **GPT-6 Luna / high effort** | **Implementation & Problem Solving**: code, first-pass debugging. |
| **🧠 Settler** | Full comprehension, long-horizon work, strong review; the human answers for its mistakes | Claude Code · **Opus 5.5 / medium (or high) effort** | **Document stewardship & task review**. Before the ticket: discuss the design with the human, amend the blueprint, open the ticket. After it: code review, test planning, documentation reconciliation. |

**Capability Required is the contract; Current Carrier is an implementation detail.** Swap a carrier without touching the seat.

**`Docs/` belongs to the Settler.** Pioneer is read-only there. A deviation found during implementation is finished in code first, then written up with its reason for the Settler to review.

**Seats are session-scoped.** One seat per session, held for its lifetime. Changing seat means a new session; carry the context across with a handoff. Code review therefore never shares a session with the implementation it reviews — the session that wrote the code holds Pioneer, and review is the Settler's.

**A Settler session may start a Pioneer session.** The Pioneer session starts from an empty context and is given only the ticket and the handoffs; what passes between the two is still only what the [handoff protocol](#the-handoff-protocol) lists for each direction. Anything that reports back to the session that started it by another route, such as a subagent, works under that session's seat and holds none of its own.

**Exception: the Settler may carry a task in a single session.** After discussing it, the human and the Settler may have the Settler alone execute a task; the ticket then carries the label `exec:settler`. See [§3.3](#33-choosing-the-executor).

---

## 2. Communication Interface & Protocols

Standardized protocols carry information between agents and across sessions.

### 🎫 The Ticket
A ticket is the head of any implementation, and the anchor everything else is traced back to.

*   **Medium**: a GitHub issue in the repository the work lands in.
*   **Purpose**: the basis for implementation. It is the grain that commits (too fine) and the project docs (end state only) both miss.
*   **Weight**: a ticket is near-permanent, so it holds only what has trace value for a later reader: the problem, the decisions and their reasons, the scope, and Done When. Context that only aligns the seats for this task (inferred mechanisms, investigation detail, design suggestions, unverified items, implementation order) goes in the handoff. Done When lists only what can be verified before merge; what can be verified only after deployment belongs to a gate in the [delivery workflow](safechord.safezone.delivery.workflow.md).
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
*   **Between the seats**: one ticket's back-and-forth uses at most three files, each with a single author.
    - `kickoff` (Settler → Pioneer, at the start): the ticket is the basis for starting; the Settler writes this only when it judges the ticket alone leaves the Pioneer short of context, and writes it once. It names the Done When items the Settler has already completed, so that the Pioneer neither redoes them nor raises them again.
    - `delivery` (Pioneer → Settler, on delivery): describes the branch as it stands. Every round updates it in place instead of adding a file; what has been dealt with is deleted, and the earlier state stays in the harness git history. Its header records which round this is and which commit it describes.
    - `review` (Settler → Pioneer, in review): every round appends a section (`## Round N`) to the same file. Earlier rounds are neither rewritten nor deleted, so it stays visible whether each round's findings narrowed. Every finding has a fixed number (`R<round>-<n>`), and every Blocking finding names its cause; each round opens by settling the findings still open from before, so the Pioneer needs to read only the latest round. Each round closes with its coverage: what the Settler ran, what it probed, and what it left unchecked, so that a round with few findings can be told apart from a round that looked at little.
*   **Lifecycle**: a handoff lives with its task. Delete it once the PR is merged, the ticket is closed, and reconciliation has landed in `Docs/`; the harness git history keeps it recoverable.
*   **Linking**: the handoff points at the ticket, never the reverse. Anyone who can read a handoff can reach the ticket, but a ticket reader may not see the handoff, and a link on a permanent ticket would dangle once the handoff is deleted.
*   **Naming**: when a ticket exists, the filename carries `<repo>-<issue_no>` in lowercase (e.g. `2026-09-19-safezone-64-worker-offset-commit.md`). The three files exchanged between the seats also end in their kind: `-kickoff`, `-delivery`, `-review` (e.g. `2026-09-19-safezone-64-worker-offset-commit-review.md`).
*   **Resuming**: a session handed off on a reactive trigger can be resumed with the note's `Resume:` command, for example to fix review findings. A session handed off for context degradation is retired and not resumed.
*   **Required Content**: [see template](#handoff-template)

### 🟣 The Pull Request
*   **Medium**: a GitHub PR in the repository the work lands in.
*   **Purpose**: the interface through which the human reviews and merges. While the seats iterate they exchange only the branch and handoffs, and no PR is open.
*   **Timing**: the Settler writes and opens it once review passes. For `exec:settler` work it is opened once implementation is done; see [§3.3](#33-choosing-the-executor).
*   **Required Content**: there is no template yet. The Settler decides the wording and structure to suit the work, and a template will be drawn once a few exist. Only the two sections below are required, each under its own heading whenever it has content:
    - **Decisions made in review**: decisions taken during the review rounds that the human did not see.
    - **Follow-up tickets**: new tickets cut out of this one; see [§3.2](#32-handling-review-findings).

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

## 3. Dual-Track Workflow: The KDD Balance

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

1.  **Strategic Design** (Settler):
    1. Discuss and define the "Why/What" with the human
    2. Update the blueprint's Requirements (the section listing the promises tests must hold), and set its `app_version` to the ticket's milestone
    3. Discuss with the human whether the decision belongs in the decision log; if it does, append the decision and its reasons
    4. **Open the ticket and label it `kdd:forward`**
    5. Cut the ticket's branch from `dev` and commit on it the tests that enforce the changed requirements, each carrying its requirement ID, with the trailer `Agent: Settler (requirement test)`. How to write them is [below](#writing-the-requirement-tests)
    6. Write a kickoff handoff if one is needed
2.  **Implementation** (Pioneer): once the Settler has committed the requirement tests and handed over
    1. Read the ticket, the blueprint, and the handoff if there is one
    2. On the same branch, implement code that passes those tests
    3. Add its own tests as the work needs, so that development follows TDD
    4. When implementation is done, push the branch, open no PR, and write the handoff
3.  **Review** (Settler): once the Pioneer has delivered
    1. Read the Pioneer's handoff and review the code against the blueprint. How to dispatch and review, and when to stop, is in the `pioneer-dispatch` skill (`.claude/skills/pioneer-dispatch/SKILL.md`)
    2. Send any findings back to implementation; see [§3.2](#32-handling-review-findings)
    3. Once review passes, write the PR
    4. If the CI the PR triggers fails, go back to review; once it passes, wait for the human to review and merge
4.  **Solidification** (Settler): once the human has merged the PR
    1. Where the code diverged from the blueprint and the divergence was reviewed, bring the blueprint in line
    2. Delete the handoffs the task produced
    3. Switch the repo's checkout back to `dev` and update it, then delete the ticket's local branch and its run directory (`.ai-runs/<repo>-<issue_no>/`, where one exists). The remote branch is deleted on merge
    4. Close the ticket

**A ticket that changes no requirement** (documentation, or a refactor that keeps behavior) skips sub-steps 2 and 5 of step 1, and its reconciliation checks that the blueprint's wording still matches. If the change forces a requirement test to change all the same, such as a rename the move causes, that change is a commit of its own under the rules of [§3.2](#32-handling-review-findings), and its assertions and inputs stay as they were.

#### Writing the requirement tests {#writing-the-requirement-tests}

The Settler writes them before anyone has chosen a mechanism, so a test can only hold the cases the Settler thought of. These checks close the gaps earlier tickets fell through:

1. **A test double fails the way the real dependency fails.** Where reproducing against the real dependency is cheap, such as a database or a broker in a container, reproduce first and model the double on what it showed. Otherwise, consider each shape the failure can take: the call raises, the connection is refused, the call is accepted and never answered, an error status comes back, the whole batch is rejected for one bad item.
2. **Test data has the shape of the real system.** A value that production shares across events, such as a request's trace ID, is shared in the test too; check it against the contracts and the service standards.
3. **A precondition assumes no mechanism.** The GIVEN does not rely on a buffer, a batch boundary or an ordering the implementation is free to choose.
4. **Each test is shown to fail and to pass.** A red that comes only from the guarded thing not existing yet shows neither: mutate it to show the test bites, and where the requirement sets a bound, show that a stub meeting the bound turns the test green.
5. **Calls into code the ticket changes are found first.** Search the requirement tests for the functions and packages the ticket changes. A requirement test that calls one is updated in the same commit, and the kickoff says that this fixes the new signature.

**The two kinds of test have different owners.** A requirement test states a promise the rest of the system relies on, and belongs to the Settler: the Pioneer does not edit, loosen or delete it, though it may raise an objection for the Settler to consider. Every other test is engineering, and belongs to the Pioneer: it adds, changes and replaces those as the implementation needs, and lists in the handoff the tests it added, the existing tests it changed, and why. When review shows that one of the Pioneer's tests guards a promise the rest of the system relies on, the Settler may promote it: the Settler adds the requirement to the blueprint, gives the test the requirement's ID, and commits that with the trailer `Agent: Settler (requirement test)`. From then on the test is the Settler's.

**Some problems cannot be fixed within the ticket.** The Pioneer neither fixes them nor opens a ticket: it writes what it found and why in its handoff to the Settler, and continues with the rest of the work.

### 🔴 Path B: `kdd:spike` (Frontier Mode)
Applied to new tech integrations, unknown bug fixes, or performance stress tests.
**Rule**: "Code before Docs"—prototyping is privileged over documentation.

1.  **Strategic Design** (Settler):
    1. Discuss and define the "Why/What" with the human
    2. **Open the ticket and label it `kdd:spike`**, and write a kickoff handoff if one is needed
    3. Cut the ticket's branch from `dev`
2.  **Spike** (Pioneer): once the Settler has cut the branch and handed over
    1. Read the ticket, and the handoff if there is one
    2. Develop the code following TDD. The exception is a ticket whose Scope states that it adds no test code, because nothing a test could hold is at stake; its Done When then names the commands that verify it. The human and the Settler agree on this when the ticket is opened
    3. When implementation is done, push the branch, open no PR, and write the handoff
3.  **Review** (Settler): once the Pioneer has delivered
    1. Read the Pioneer's handoff and review the code against the ticket's scope and Done When. How to dispatch and review, and when to stop, is in the `pioneer-dispatch` skill (`.claude/skills/pioneer-dispatch/SKILL.md`)
    2. Send any findings back to implementation; see [§3.2](#32-handling-review-findings)
    3. Once review passes, write the PR
    4. If the CI the PR triggers fails, go back to review. If CI does not cover the component this task built, discuss with the human whether it should; if so, open a new ticket for it and carry on. Once CI passes, wait for the human to review and merge
4.  **Solidification** (Settler): once the human has merged the PR
    1. Discuss with the human whether the result needs settling into a document; if it does, write the document of the type that fits the work
    2. Delete the handoffs the task produced
    3. Switch the repo's checkout back to `dev` and update it, then delete the ticket's local branch and its run directory (`.ai-runs/<repo>-<issue_no>/`, where one exists). The remote branch is deleted on merge
    4. Close the ticket

### 3.2 Handling review findings {#32-handling-review-findings}

Review reads the test diff separately from the code diff. A test changed so that it passes is the first thing to question.

**Findings go back to the Pioneer in a handoff** (see the [handoff protocol](#the-handoff-protocol)).

**A requirement test that does not match the blueprint's requirement.** There are two cases:

1. The test is at fault
    1. The test is too loose: the Settler tightens it
    2. The test is too strict: the Settler loosens it, checking with particular care that it still holds the blueprint's requirement

    The Settler commits the change itself under the rules below, then hands back to the Pioneer to pass the tests:

    1. each change is a commit of its own
    2. it carries the trailer `Agent: Settler (requirement test)`
    3. the body states the reason
2. The blueprint is at fault: stop the task and ask the human to judge the situation

**A decision still to be made, or work outside this ticket.** Whether the Settler found it in review or it came from the Pioneer's handoff, the Settler opens a new ticket. It is linked in two places: the new ticket's Background points back at the original, so a later reader of the new ticket knows where it came from; the PR lists these follow-up tickets in a section of their own, so the human sees them before merging. The body of the PR does not need to describe them.

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

**Label and flow.** A ticket the Settler will execute carries the label `exec:settler`, which combines with `kdd:forward` or `kdd:spike`. The flow is the path from [§3.1](#31-choosing-the-path) with the Settler as the implementer: the handoffs between seats and the review in step 3 are skipped, and the Settler opens the PR once implementation is done, for the human to review. Work outside the ticket that turns up during it still goes to a new ticket, as in [§3.2](#32-handling-review-findings), listed in the PR.

**Review responsibility.** Separation exists so the session that did the work never reviews it. Under `exec:settler` that independence is gone, so the human takes over review explicitly and is accountable for it.

**The PR label.** The Settler opens the PR with the label `review:human` and this header:

```markdown
> ⚠️ **Executed by the Settler.** No independent agent review took place; the executor and
> reviewer are the same seat. The human reviewer is the only independent check, and merging
> transfers accountability to them.
```

**What the PR adds.** With no review file, nothing else records what went unexamined, and the human is the only reviewer. The PR therefore carries a **Not checked** section: the paths, conditions and commands the Settler did not verify.

**Merge is the sign-off.** The human merges after reviewing the change, and the merge is what transfers accountability. No agent merges an `exec:settler` PR.

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
Agent: [Pioneer / Settler / Settler (review fix) / Settler (requirement test)]
Legacy: [Pending issues for the next agent]
```

### 🔴 Handoff Template {#handoff-template}
```markdown
# 📝 Legacy Note: [Task Name]

> **Date**: YYYY-MM-DD
> **From**: [Seat] / [Carrier] / [session id]
> **Resume**: [command that resumes this session in its tool]
> **To**: [Seat] / [new session, or blank if not yet known]
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

A `kickoff` between the seats uses the template above as it is. `delivery` and `review` differ as follows.

**`delivery`** (Pioneer, updated in place every round): the template above, with two more header lines and two more sections.

```markdown
> **Round**: [N, counted from 1]
> **Head**: [the commit this note describes]

## Response to Review
[From round 2 on. One line per finding still open in the latest review round.]
- R1-1: [how it was fixed, or why you disagree]

## Raised for the Settler
- [A problem that cannot be fixed inside this ticket: what was found, and why]
- [An objection to a requirement test]
```

**`review`** (Settler, appended every round):

```markdown
# 📝 Review: [Task Name]

> **From**: Settler / [Carrier] / [session id]
> **Resume**: [command that resumes this session in its tool]
> **To**: Pioneer / [session id]
> **Ticket**: [<repo>-<issue_no>]
> **Branch**: [Branch Name]

---

## Round 1 — reviewed [commit]
**Verdict**: [Returned / Passed]

### Findings
- **R1-1** [Blocking] [impl / boundary / kickoff] [what is wrong, where, how to reproduce it]
- **R1-2** [Minor] [...]

### Coverage
- Ran: [the tests the Settler ran itself, and their result]
- Probed: [each throwaway experiment: what it varied, what it showed]
- Not checked: [the paths, conditions and files this round did not examine]

## Round 2 — reviewed [commit]
**Verdict**: [Returned / Passed]

### Earlier findings
- R1-1: Resolved
- R1-2: Open — [what is still missing]

### Findings
- **R2-1** [Blocking] [impl / boundary / kickoff] [...]

### Coverage
- [...]
```

Every Blocking finding carries its cause, and may carry more than one:

| Cause | Meaning |
| :--- | :--- |
| `impl` | An error inside the boundary: the ticket, the blueprint or the requirement tests already said what was right, and the implementation did not do it |
| `boundary` | The boundary moved: nobody had anticipated this case before the work began |
| `kickoff` | Traced to what the Settler handed over: the ticket, the kickoff, or a requirement test |

The cause records where a round came from, so that tickets can be compared by cause and not only by how many rounds they took.

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
