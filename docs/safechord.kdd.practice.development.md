---
title: 'KDD 2.0: Development'
last_updated: '2026-10-23'
status: active
doc_version: 0.4.0
archetype: script
code_paths: []
---

# KDD 2.0 Practice: Two-Engine Development

> **Type**: Script (a mode page: implements the [practice](safechord.kdd.practice.md) §2)
> **Focus**: How a code change gets from a ticket to a merge on the **"Two-Engine"** model: a Pioneer seat for implementation and a Settler seat for review and solidification.
> **Constraint**: Nothing every mode shares: it is in the practice. How to dispatch and review is in the `pioneer-dispatch` skill, and how to write the PR body in the `pr-body` skill (`.claude/skills/` in the workspace harness).

> **⚙️ This page shares the practice's [adjustment period](safechord.kdd.practice.md)**: the two-engine seating, the ticket lifecycle and the templates in §4 have not yet been through a full cycle, and its `doc_version` holds at v0.4.0 while the notice stands.

## Mode Contract {#mode-contract}

- **Work**: a code change that lands in a code repository through a branch, a PR and a merge, on a ticket labelled `kdd:forward` or `kdd:spike`. A session moves into this mode when it picks up such a ticket.
- **Human**: the last gatekeeper, looking once before merge; the merge is the sign-off. Under `exec:settler` the human is also the only reviewer (§3.3).
- **Seats**: the Pioneer and the Settler, each held for a session's lifetime (§1).
- **Ends**: when the ticket closes, after merge and reconciliation (§3.1, Solidification).
- **Landing**: through the ticket's branch, a PR and the human's merge. `Docs/` belongs to the Settler; the Pioneer is read-only there (§1).
- **Protocols**: **extends** the ticket, the commit and the handoff (§2). Its own: the pull request (§2).
- **Carried by**: `pioneer-dispatch` (dispatch, review and the round cap, §3.1 and §3.2) and `pr-body` (the PR). Written only on this page: the requirement tests (§3.1), Solidification (§3.1), review findings (§3.2) and `exec:settler` (§3.3).

---

## 1. The Two-Engine Model {#1-the-two-engine-model}

| Role | Capability Required | Core Responsibility |
| :--- | :--- | :--- |
| **🛡️ Pioneer** | Adequate implementation ability, good value for its cost, fast turnaround; failures are caught by tests | **Implementation & Problem Solving**: code, first-pass debugging. |
| **🧠 Settler** | Full comprehension, long-horizon work, strong review; the human answers for its mistakes | **Document stewardship & task review**. Before the ticket: discuss the design with the human, amend the blueprint, open the ticket. After it: code review, test planning, documentation reconciliation. |

**Capability Required is the contract.** Which carrier and model hold a seat is configuration: the Pioneer's is in `pioneer-dispatch`'s `config.json`, and the Settler is the attended session the human starts. Swap a carrier without touching the seat.

**`Docs/` belongs to the Settler.** The Pioneer writes only to its ticket's branch and its delivery handoff: every other repository, `Docs/` included, and the tickets and PRs are read-only to it. A deviation found during implementation is finished in code first, then written up with its reason for the Settler to review.

**Seats are session-scoped.** One seat per session, held for its lifetime. Changing seat means a new session; carry the context across with a handoff. Code review therefore never shares a session with the implementation it reviews — the session that wrote the code holds Pioneer, and review is the Settler's.

**A Settler session may start a Pioneer session.** The Pioneer session starts from an empty context and is given only the ticket and the handoffs; what passes between the two is still only what the [handoff protocol](safechord.kdd.practice.md#the-handoff-protocol) lists for each direction. What reports back to a session by another route follows [Sessions and seats](safechord.kdd.practice.md#sessions-and-seats).

**Exception: the Settler may carry a task in a single session.** After discussing it, the human and the Settler may have the Settler alone execute a task; the ticket then carries the label `exec:settler`. See [§3.3](#33-choosing-the-executor).

---

## 2. Development Protocols {#2-development-protocols}

### 🎫 The Ticket {#the-ticket}
**Extends** [the ticket](safechord.kdd.practice.md#the-ticket):

*   **Branch**: `<type>/issue-<issue_no>-<slug>`, `<type>` being the commit type of the change. The `refactor/` prefix is reserved for a ticket labelled `mode:refactor`, which the human and the Settler agree on when the ticket is opened: that prefix switches the agents' refactor mode on, under which structural integrity outranks minimal diff while the Scope still binds. A `type:refactor` ticket without the label is cut as `chore/`.
*   **Reconciliation**: only a `kdd:spike` ticket may have its reconciliation item confirmed as not needed. A `kdd:forward` ticket's References link its blueprint (`- Blueprint: [link to the Docs/ page]`).

### 🟢 The Commit {#the-commit}
**Extends** [the commit](safechord.kdd.practice.md#the-commit): `Agent:` is `Pioneer`, `Settler`, `Settler (review fix)` ([§3.2](#32-handling-review-findings)) or `Settler (requirement test)` ([§3.1](#writing-the-requirement-tests), [§3.2](#32-handling-review-findings)).

### 🔴 Handoffs Between the Seats {#handoffs-between-the-seats}
**Extends** [the handoff protocol](safechord.kdd.practice.md#the-handoff-protocol). Between the seats it adds:

*   **Between the seats**: one ticket's back-and-forth uses at most three files, each with a single author.
    - `kickoff` (Settler → Pioneer, at the start): the ticket is the basis for starting; the Settler writes this only when it judges the ticket alone leaves the Pioneer short of context, and writes it once. It names the Done When items the Settler has already completed, so that the Pioneer neither redoes them nor raises them again.
    - `delivery` (Pioneer → Settler, on delivery): describes the branch as it stands. Every round updates it in place instead of adding a file; what has been dealt with is deleted, and the earlier state stays in the harness git history. Its header records which round this is and which commit it describes.
    - `review` (Settler → Pioneer, in review): every round appends a section (`## Round N`) to the same file. Earlier rounds are neither rewritten nor deleted, so it stays visible whether each round's findings narrowed. Every finding has a fixed number (`R<round>-<n>`), and every Blocking finding names its cause; each round opens by settling the findings still open from before, so the Pioneer needs to read only the latest round. Each round closes with its coverage: what the Settler ran, what it probed, and what it left unchecked, so that a round with few findings can be told apart from a round that looked at little.
*   **Naming**: The three files exchanged between the seats also end in their kind: `-kickoff`, `-delivery`, `-review` (e.g. `2026-09-19-safezone-64-worker-offset-commit-review.md`).
*   **Required Content**: [see template](#handoffs-between-the-seats-templates)

### 🟣 The Pull Request {#the-pull-request}
*   **Medium**: a GitHub PR in the repository the work lands in.
*   **Purpose**: the interface through which the human reviews and merges. While the seats iterate they exchange only the branch and handoffs, and no PR is open.
*   **Timing**: the Settler writes and opens it once review passes. For `exec:settler` work it is opened once implementation is done; see [§3.3](#33-choosing-the-executor).
*   **Sorting what was left unverified**: before writing the PR, the Settler takes everything left unverified (the review rounds' "Not checked" lines, the delivery handoff's "Unverified / Uncertain", and under `exec:settler` what it did not verify itself) and sorts each item by the harm it can do:
    - no real harm: dropped
    - harm, and it can be checked within the ticket: checked now
    - harm, and it cannot be checked before merge: stated under **Merge Danger**. A check that can run only once the release is cut or deployed also goes on the release's record of held checks ([Delivery §3](safechord.kdd.practice.delivery.md#what-development-hands-over)), with a link back to this ticket
    - no danger at merge, but worth doing: a follow-up ticket; see [§3.2](#32-handling-review-findings)

    An item whose harm would not land at merge becomes a ticket or is dropped. The PR carries no list of what was not checked.
*   **Required Content**: [see template](#pull-request-template)

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
2. Update the blueprint's Requirements (the section listing the promises tests must hold), and set its `app_version` to the ticket's milestone
3. Discuss with the human whether the decision belongs in the decision log; if it does, append the decision and its reasons
4. **Open the ticket and label it `kdd:forward`**
5. Cut the ticket's branch from the repository's integration branch and commit on it the tests that enforce the changed requirements, each carrying its requirement ID, with the trailer `Agent: Settler (requirement test)`. How to write them is [below](#writing-the-requirement-tests)
6. Write a kickoff handoff if one is needed

The flow goes on as [both paths](#both-paths) share it.

**A ticket that changes no requirement** (documentation, or a refactor that keeps behavior) skips steps 2 and 5 of its Strategic Design, apart from cutting the branch, and its reconciliation checks that the blueprint's wording still matches. If the change forces a requirement test to change all the same, such as a rename the move causes, that change is a commit of its own under the rules of [§3.2](#32-handling-review-findings), and its assertions and inputs stay as they were.

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

**Strategic Design** (Settler):

1. Discuss and define the "Why/What" with the human
2. **Open the ticket and label it `kdd:spike`**, and write a kickoff handoff if one is needed
3. Cut the ticket's branch from the repository's integration branch

### Both paths {#both-paths}

1.  **Implementation** (Pioneer): once the Settler has cut the branch, committed the requirement tests on `kdd:forward`, and handed over
    1. Read the ticket, and the handoff if there is one. On `kdd:forward`, read the blueprint and implement to it, passing the requirement tests on the same branch
    2. Develop the code following TDD, adding tests as the work needs. On `kdd:spike`, a ticket whose Scope states that it adds no test code, because nothing a test could hold is at stake, is the exception: its Done When then names the commands that verify it. The human and the Settler agree on this when the ticket is opened
    3. When implementation is done, push the branch, open no PR, and write the handoff
2.  **Review** (Settler): once the Pioneer has delivered
    1. Read the Pioneer's handoff and review the code: against the blueprint on `kdd:forward`, against the ticket's scope and Done When on `kdd:spike`. How to dispatch and review is in the `pioneer-dispatch` skill (`.claude/skills/pioneer-dispatch/SKILL.md`)
    2. Send any findings back to implementation, up to the round cap; see [§3.2](#32-handling-review-findings)
    3. Once review passes, write the PR
    4. If the CI the PR triggers fails, go back to review. On `kdd:spike`, if CI does not cover the component this task built, discuss with the human whether it should; if so, open a new ticket for it and carry on. Once CI passes, wait for the human to review and merge
3.  **Solidification** (Settler): once the human has merged the PR
    1. On `kdd:forward`, where the code diverged from the blueprint and the divergence was reviewed, bring the blueprint in line. On `kdd:spike`, discuss with the human whether the result needs settling into a document; if it does, write the document of the type that fits the work. On either path, if the PR's SSOT feedback box is ticked, write its entries into `Docs/` as well
    2. Delete the handoffs the task produced
    3. Switch the repo's checkout back to its integration branch and update it, then delete the ticket's local branch and its run directory (`.ai-runs/<repo>-<issue_no>/`, where one exists). The remote branch is deleted on merge
    4. Close the ticket

### 3.2 Handling review findings {#32-handling-review-findings}

Review reads the test diff separately from the code diff. A test changed so that it passes is the first thing to question.

**Findings go back to the Pioneer in a handoff** (see the [handoff protocol](safechord.kdd.practice.md#the-handoff-protocol)).

**Review has a round cap**, set in `pioneer-dispatch`'s `config.json`. A review whose last round at the cap ends Returned stops there: the Settler reports to the human the rounds so far and the Blocking findings still open, with their causes, and does nothing more on the ticket. What follows is the human's decision.

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

**What was left unverified.** With no review file, what the Settler did not verify itself goes through the same sorting as a review's ([§2, the Pull Request](#the-pull-request)) before the PR is written. Whatever can harm and could not be checked before merge is stated under the PR's Merge Danger, where the human, the only reviewer, reads it.

**Merge is the sign-off.** The human merges after reviewing the change, and the merge is what transfers accountability. No agent merges an `exec:settler` PR.

---

## 4. Development Templates {#4-development-templates}

### 🔴 Handoffs Between the Seats {#handoffs-between-the-seats-templates}
A `kickoff` between the seats uses the [handoff template](safechord.kdd.practice.md#handoff-template) as it is. `delivery` and `review` differ as follows.

**`delivery`** (Pioneer, updated in place every round): the handoff template, with two more header lines and two more sections.

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

- **Round** is the review round this delivery answers, and **Head** the commit it describes; a delivery whose Head is not the branch head is stale.
- **Response to Review** answers each finding still open. A disagreement there is an objection the Settler settles in the next round, not a fix.
- **Raised for the Settler** holds what the Pioneer could not settle inside the ticket; the Settler decides each item ([§3.2](#32-handling-review-findings)). `None` means the Pioneer found nothing to raise.

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

- **Verdict** is `Passed` when no Blocking finding is open, and `Returned` otherwise. A Minor finding left open at `Passed` is a decision made in review, and goes to the PR.
- **Blocking** must be resolved before the review can pass; **Minor** need not.
- **Earlier findings** settles every finding still open from before as `Resolved` or `Open`, so the latest round alone says what is open.
- **Coverage** says what the round ran, probed and left unchecked: a round with few findings and a short Coverage looked at little.

Every Blocking finding carries its cause, and may carry more than one:

| Cause | Meaning |
| :--- | :--- |
| `impl` | An error inside the boundary: the ticket, the blueprint or the requirement tests already said what was right, and the implementation did not do it |
| `boundary` | The boundary moved: nobody had anticipated this case before the work began |
| `kickoff` | Traced to what the Settler handed over: the ticket, the kickoff, or a requirement test. Marked whenever it applies, also when the implementation is at fault as well |

The cause records where a round came from, so that tickets can be compared by cause and not only by how many rounds they took.

### 🟣 Pull Request Template {#pull-request-template}
```markdown
[exec:settler only: the header from §3.3]
Ticket: #[issue_no]

## Summary
[The smallest view that makes the change clear]

## Evidence
- [A contrast per behavior: what failed before and passes now]
- [The regression run, one line]

## Merge Danger: [low / medium / high]
[What merging sets off, what a revert would not undo, who is hit if this is wrong]
Deferred to release: [the check] → #[release record ticket]

## SSOT feedback
- **Gap**: [requirement or ADR] says nothing about [what]. This PR chose [what].
- **Requirement test**: [test] added / modified: [what the promise now pins].

- [ ] Tighten the SSOT with the above (unticked at merge: left as is)

## Decisions made in review
- [A decision the human did not see, Minor findings left open included]

## Follow-up tickets
- #[issue_no]
```

The ticket line, Summary, Evidence and Merge Danger are in every PR. The other sections appear only when they have content, and the "Deferred to release" line only when there is such a check. The ticket line uses no closing keyword: the ticket closes after reconciliation, not on merge. Under `exec:settler`, "Decisions made in review" is headed "Decisions made during implementation".

- **Summary** and **Evidence** are the change's shape and the proof that it does what it says: the human reads them to know what merging changes.
- **Deferred to release** is a check moved to the release's record of held checks ([Delivery §3](safechord.kdd.practice.delivery.md#what-development-hands-over)).
- **Decisions made in review** are what was decided without the human, Minor findings left open included; the human can overturn each before merging.
- **Follow-up tickets** are work found outside this ticket; merging does not wait for them.

**Merge Danger** is graded by what it costs if the change is wrong:

| Level | If this is wrong | The human |
| :--- | :--- | :--- |
| `low` | A revert puts everything back | Merges |
| `medium` | A revert puts it back, but someone or something was hit first | Knows where to look after merge |
| `high` | Something a revert does not undo, or a manual step before or after merge | Reads the description before merging |

A check deferred to release does not raise the level: the release's gates hold it.

**SSOT feedback** reports where the SSOT left room. A Gap is a choice the SSOT left open that something outside the service, an operator or the deployment can observe; a choice visible only inside the code is a decision. A requirement test added or modified after pre-work changes the precise form of a promise. Ticking the box means reconciliation writes every entry into `Docs/`; to write only some, the human says which in a PR comment, and the comment wins.

How to fill each section (the forms for Summary and Evidence, the floors for Merge Danger, the prose rules) is in the `pr-body` skill (`.claude/skills/pr-body/SKILL.md`).
