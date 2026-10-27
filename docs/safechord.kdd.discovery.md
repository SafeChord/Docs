---
title: 'KDD 2.0: Discovery'
status: active
archetype: script
---

# KDD 2.0: Discovery

> **Type**: Script (a standing task: work no mode owns)
> **Focus**: Finding where the KDD process lets defects through, by reading what its runs recorded and left behind across tickets and releases: why the task exists, what it covers, what it takes as right, and how its outcome lands.
> **Constraint**: No steps, commands, thresholds, tag mechanics or classification criteria. They are in the `discover` skill (`.claude/skills/` in the workspace harness) and in its reminder, `scripts/discover-trigger.sh`.

## Why it exists {#why-it-exists}

Inside a run, the session records what it sees and does not judge its own process: the session that did the work is the one least placed to see where the process let it down, and an agent asked what was missing will always find something. Its events are recorded as facts only (`.ai-metrics/README.md` in the workspace harness, `events.jsonl`). Finding where the process leaks is left to a later reading.

That reading has to cross runs. A run sees its own ticket, and the fix one ticket's record suggests is often corrected by the next: the same defect seen in three runs of two flows, with three different fixes proposed, is one finding, and only a reading across them shows its shape. The defects that matter most are often the ones nobody running the ticket noticed, caught later by the human or a release gate, so the reading goes to each run's own artifacts and not to the event log alone.

## Scope {#scope}

- **Every flow that runs a ticket or a release**: dispatch to the Pioneer and `exec:settler` ([Development](safechord.kdd.practice.development.md)), and release runs ([Delivery](safechord.kdd.practice.delivery.md)), over the tickets and releases recorded since the last review.
- **The records and the artifacts.** The event log, and each run's artifacts: its handoffs between the seats as harness history keeps them, its PR with its comments and CI runs, its release record. How each ticket ended is reconstructed from these; nothing logs it.
- **The process, not the product.** A finding is about a step, a template, a skill, a script, a check or a page of the process. A defect in the code counts only for the gate that let it through; the code is fixed by a ticket of its own.
- **Not cost.** What a carrier or a model costs is read from the cost logs on their own; discovery reads them only for how a ticket went.
- **Not Docs against Docs**: that is [Internal Alignment](safechord.kdd.alignment.md).
- **Handoffs without a ticket, and drafts left to age**: Open decision whether a discovery run covers them.

## What it takes as right {#what-it-takes-as-right}

- **The artifacts, as what happened.** An event line, a review round, a PR comment and a CI run are taken as facts. Where an event line and an artifact disagree, the artifact holds, and the disagreement is reported.
- **Nothing about the process.** The pages, skills and scripts are what is under review: a run that departed from a page may mean that the run was wrong or that the page was. The reading does not settle which; it puts the finding before the human with its evidence.
- **Evidence, for a finding's weight.** A finding ranks by how many runs show it and how far its defect got before it was caught, not by how sure the reading session is.

## Runs {#runs}

A run has two halves, in two sessions.

| | Reading | Deciding |
| :--- | :--- | :--- |
| **Who** | A session of its own, with no human present | The human, with a session of their own |
| **Does** | Reads the records and artifacts since the last review; finds what recurs across them; classifies each escape by the gate it came from, the gate that caught it and the gate that should have; proposes a fix for each finding, with the home the fix would have ([Layers](safechord.kdd.practice.md#layers)) | Goes through the draft and decides each finding: a ticket, a change made in conversation, or dropped |
| **Leaves** | One draft in the harness's draft directory, and nothing else changed | The decisions, each landed as its own mode lands it |

The reading is long, and holding it in a session of its own keeps the judgment out of the sessions whose work is judged; deciding needs the human, who owns the process. A fix for a mechanical defect goes into a script, a hook or a check, since a written rule holds only while someone remembers it; a fix that needs judgment goes into the wording of a skill or a page.

**When it runs.** When the human starts it. Once enough tickets and releases have been recorded since the last review (counted, not timed), the session that pushed the harness reminds the human that a run is due, and starts nothing itself: the reading costs a strong model a long context, and its draft waits until the human has time to decide, so starting it unasked would only spend the cost sooner.

The last reviewed point is the tag `discover/last` on the harness, moved once the deciding half has landed.
