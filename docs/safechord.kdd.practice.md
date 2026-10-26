---
title: 'KDD 2.0: Practice'
last_updated: '2026-10-26'
status: active
doc_version: 0.4.0
archetype: interface
code_paths: []
---

# KDD 2.0 Practice

> **Type**: Interface (implemented by every mode page)
> **Focus**: Which mode a session is in, what holds in every mode, what each mode page must declare, and the protocols the modes share.
> **Constraint**: No mode's own flow: it is on that mode's page. No standing task's own rules: they are on its page. How a step is carried out lives in the skill or script that runs it (§1.2). No template's skeleton or field meanings: they are in its file under `docs/templates/protocol/`. The reasons the model took its shape are in the [KDD changelog](safechord.kdd.changelog.md).

> **⚙️ This document is in an adjustment period.** The Mode Contract in §2, the ticket lifecycle, and the protocol templates were all introduced in v0.4.0 and have not yet been through a full cycle. Expect rough edges.
>
> **If a template or a step does not fit the work in front of you, say so rather than working around it silently.** A mismatch between this document and what actually happens is a defect in the document until it has been argued otherwise — raise it with the human, and it gets fixed here.
>
> **Do not bump `doc_version` while this notice stands.** The document holds at v0.4.0 until the adjustment period closes. Edits land under `last_updated` alone.

## Modes {#modes}

SafeChord uses agents in several modes, told apart by what the work is and where the human stands. Each mode has a page of its own, which declares what §2 requires and inherits the rest of this page.

| Mode | What it covers | Where the human stands | Page |
| :--- | :--- | :--- | :--- |
| Discussion | Work with no ticket yet, and work that lands in `Docs/` or the harness | Present throughout, deciding together | [Discussion](safechord.kdd.practice.discussion.md) |
| Development | A code change that lands in a code repository through a branch, a PR and a merge, on a ticket labelled `kdd:forward` or `kdd:spike` | The last gatekeeper, looking once before merge | [Development](safechord.kdd.practice.development.md) |
| Delivery | Cutting, validating and promoting a release of a product, phase by phase, as its implementation page lays out | Present throughout, signing off every gate | [Delivery](safechord.kdd.practice.delivery.md) |
| Operations | Running the deployed system: SRE work on the live platform | Not yet defined | — |

### Finding your mode {#finding-your-mode}

A session judges its own mode against the descriptions above; no rule maps a ticket to a mode.

- **State it before acting**: "this is <mode>, because <reason>". The reason names what decided it: the ticket and its labels, the repository the work lands in and how that repository takes changes, what the human asked. The stated mode is what lets the human catch a wrong call.
- **With no ticket in hand, the mode is Discussion.**
- **When no mode fits, or more than one does, ask the human** before acting. Work that fits no mode is not bent into the nearest one.
- **The mode changes with the work.** Opening or picking up a ticket is where it usually changes; state the new mode then.
- **A session started by a script** (`pioneer-dispatch`, a CI job) takes its mode and seat from the prompt that started it, and does not judge.

### Standing tasks {#standing-tasks}

A standing task is work that no ticket and no mode owns. It runs under the mode and seat of the session that starts it ([Sessions and seats](#sessions-and-seats)). Its page states why it exists, what it covers, what it takes as right, and how its changes land.

| Task | What it keeps | Page |
| :--- | :--- | :--- |
| Internal alignment | `Docs/` consistent with itself | [Internal Alignment](safechord.kdd.alignment.md) |
| Discovery | The process's leaks found across runs and put before the human | [Discovery](safechord.kdd.discovery.md) |

---

## 1. What Holds in Every Mode {#1-what-holds-in-every-mode}

A mode page may add to this section, never contradict it. A rule that some mode has to contradict does not belong here: it moves down to the pages where it holds.

### 1.1 Sessions and seats {#sessions-and-seats}

- A mode that has seats defines them on its page, with how long a session holds one. A session that enters such a mode takes the seat its work there needs.
- Whatever reports back to the session that started it, such as a subagent or a tool run, works under that session's mode and seat and holds none of its own.
- Where a template asks for a seat, a session in a mode without seats gives its mode instead (`Agent: Discussion`).

### 1.2 Layers {#layers}

Each kind of fact has one home. Two tests sort a sentence into its home: would it still hold with another carrier, and would it still hold in another project. What holds in another project belongs to the framework; what does not belongs to the project.

| Home | Holds | Read by |
| :--- | :--- | :--- |
| Framework docs (the [introduction](safechord.kdd.introduction.md), the [changelog](safechord.kdd.changelog.md)) | Concepts, reasons, what a run looks like | The human and agents |
| Framework contract (this page, the shared mode pages, their templates under `docs/templates/protocol/`) | What must hold, who decides, and what each template field means | The human and agents |
| Framework skills and scripts (`.claude/skills/` in the workspace harness) | How a step is carried out now: commands, order, parameters | The agent that runs the skill |
| Project implementation pages | A project page that inherits a shared mode page: the project's own flow, its artifacts and the reasons for its choices, with the skills that carry it | The human and agents in that mode |
| Project config (a `config.json` beside the skill that reads it, for now) | Values skills and scripts read: carriers, models, base branches, limits | Skills and scripts |
| A repository's `.ai-rules.md` | How that repository applies the KDD pages: its conventions, commands and paths | Agents working in that repository |
| The context file (`AGENTS.md` in the workspace) | Activation, red lines, workspace facts, the mandatory triggers | Every session |

Below them all, hooks, workflows and code are what runs whether or not an agent remembers it, and what the system actually does.

- **What goes on a KDD page**: a sentence whose change would change a human's or another seat's judgment or action. Anything else belongs to the skill or script that carries it out.
- **A project implementation page inherits.** It states what it takes from its shared mode page as it is, what it **Extends** and what it **Overrides** (§2). A shared mode page holds only what is general now; more moves up to it when a second implementation shows it is general.
- **A skill stays abstract.** It reaches the project through three hooks: a deterministic step calls a named entry point the project implements (a make target or a script, the Makefile doubling as its manual); a value comes from config; a judgment names its question and where its criteria live (a repository's `.ai-rules.md` under a section named for it, the project implementation page, or a Docs page that is SSOT for it).
- **A repository's `.ai-rules.md` applies the KDD pages; it does not restate them.** It maps what a page requires onto that repository, and points at the page for the flow itself. What a command does and when to use it is its own; a skill says at which step it runs the command and what to do with the result.
- **The labels the KDD pages define** (`kdd:forward`, `kdd:spike`, `exec:settler`, `mode:refactor`, `review:human`) are framework vocabulary. A project's own labels are defined on the implementation page that uses them. Config holds no label.
- **A project file points at `~/.ai-agent/kdd.md`; it does not restate it.**
- **The move is gradual.** A step that no skill carries yet is written on its mode page. Once a skill carries it, the page keeps only what the step must achieve. A rule that becomes checkable moves on into a hook or a script.
- **In a conflict, the fact's home holds** and the restatement is fixed: the KDD page for what must hold and who decides, the implementation page for the project's flow, the repository's `.ai-rules.md` for how that repository applies it, the skill for how a step runs, config for a value, the code for what the system does. A requirement test answers to its blueprint the same way ([Development §3.2](safechord.kdd.practice.development.md#32-handling-review-findings)). When the home itself looks wrong, stop and ask the human.

---

## 2. What a Mode Page Declares {#2-what-a-mode-page-declares}

Every mode page opens with a **Mode Contract** that gives each member below, in this order. A page that leaves one out has not implemented its mode; an unknown is written as one (`Open decision`, `Not established`).

| Member | What it says |
| :--- | :--- |
| **Work** | What work the mode covers, and what moves a session into it or out of it |
| **Human** | Where the human stands, and which of the human's acts is the sign-off |
| **Seats** | The seats, what each holds and how long a session holds one; or that the mode has none |
| **Ends** | What ends a task in the mode. The handoffs the task produced are deleted then ([the handoff protocol](#the-handoff-protocol)) |
| **Landing** | How the mode's changes reach `main`, and who may write to `Docs/` |
| **Protocols** | Which protocols of §3 the mode uses, what it changes in each, and any protocol of its own |
| **Carried by** | The skills and scripts that carry its steps, and the steps still written only on the page (§1.2) |

**Changing a protocol.** A protocol the mode page does not mention applies as §3 writes it. A change is marked as one of two kinds:

- **Extends** *protocol*: adds to it; everything §3 writes still holds.
- **Overrides** *protocol*: replaces the part it names.

Neither may contradict §1.

---

## 3. Shared Protocols {#3-shared-protocols}

Standardized protocols carry information between agents and across sessions.

### 🎫 The Ticket {#the-ticket}
A ticket is the head of any implementation, and the anchor everything else is traced back to.

*   **Medium**: a GitHub issue in the repository the work lands in.
*   **Purpose**: the basis for implementation. It is the grain that commits (too fine) and the project docs (end state only) both miss.
*   **Weight**: a ticket is near-permanent, so it holds only what has trace value for a later reader: the problem, the decisions and their reasons, the scope, and Done When. Context that only aligns the seats for this task (inferred mechanisms, investigation detail, design suggestions, unverified items, implementation order) goes in the handoff. Done When lists what can be verified without a deployment: before the work lands, or, marked `(after merge)`, once it has landed and before the ticket closes. A check that can run only after deployment belongs to a gate of the [delivery mode](safechord.kdd.practice.delivery.md).
*   **Done When states intent, not shape**: write what must hold of the result ("the logger's output is unchanged except for `worker_id`", "no assertion or test input changes"), not what the diff or the names look like ("field names are unchanged", "the diff touches only imports"). A condition written as a shape is met by the wrong change and broken by the right one, and contradicts the Scope the first time it allows a rename.
*   **Freshness**: a ticket opened before the work starts is checked again before it does, against the pages and the code as they now stand. A reference to a section since rewritten, or a current state that later tickets have changed, is corrected on the ticket first. It also asks what the tickets it depends on have decided since it was opened (an ADR, a blueprint change), and what its merge will touch that is running now (a release gate, a soak, a live sync).
*   **Blockers**: recorded as the issue's blocked-by relation on GitHub, where a flow can read them; a blocker named only in the body goes unseen.
*   **Required Content**: [the ticket template](templates/protocol/ticket.md)

### 🟢 Basic Communication: Git Commit Protocol {#the-commit}
*   **Medium**: git
*   **Purpose**: the fine-grained carrier during implementation.
*   **Format**: strict [Conventional Commits](https://www.conventionalcommits.org/).
*   **Required Content**: [the commit template](templates/protocol/commit.md)

### 🔴 The Handoff Protocol {#the-handoff-protocol}
*   **Medium**: Markdown files in the project's handoff directory, which the context file names.
*   **Purpose**: the carrier across AI tool sessions. The counterparty may be the next session or another agent.
*   **Triggers**: reactive or deliberate, as `~/.ai-agent/kdd.md` §2 defines them.
*   **Lifecycle**: a handoff lives with its task. Delete it when the task ends, as the mode page defines the end (§2, **Ends**); the harness git history keeps it recoverable.
*   **Linking**: the handoff points at the ticket, never the reverse. Anyone who can read a handoff can reach the ticket, but a ticket reader may not see the handoff, and a link on a permanent ticket would dangle once the handoff is deleted.
*   **Naming**: when a ticket exists, the filename carries `<repo>-<issue_no>` in lowercase (e.g. `2026-09-19-safezone-64-worker-offset-commit.md`).
*   **Required Content**: [the handoff template](templates/protocol/handoff.md)

### ⚪ Design Drafts {#design-drafts}
*   **Medium**: Markdown files in the project's draft directory, one subdirectory per domain; the context file names both.
*   **Purpose**: continuity for forward-looking discussion that does not touch the codebase directly. Usually precedes opening a ticket.
*   **Required Content**: [the draft template](templates/protocol/draft.md)
