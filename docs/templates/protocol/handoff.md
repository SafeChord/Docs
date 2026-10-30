# Handoff Template

The required content of [a handoff](../../safechord.kdd.practice.md#protocols).

A handoff lives with its task: delete it when the task ends, as the mode's page defines the end; the harness git history keeps it recoverable. It points at the ticket, never the reverse: a reader of the ticket may not see the handoff, and a link on the ticket would dangle once the handoff is deleted.

```markdown
# 📝 Legacy Note: [Task Name]

> **Date**: YYYY-MM-DD
> **From**: [Seat, or the mode where it has none; blank outside every mode] / [Carrier] / [session id]
> **Resume**: [command that resumes this session in its tool]
> **To**: [Seat, or the mode where it has none; blank outside every mode] / [new session, or blank if not yet known]
> **Trigger**: [Reactive: milestone | blocked | human handover] or [Deliberate: context degradation]
> **Ticket**: [<repo>-<issue_no>, e.g. safezone-64; default "None"]
> **Branch**: [Branch Name; default "None"]
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

- **Resume** reopens the writing session, and is used only when the Trigger is Reactive.
- **Trigger** says whether the writing session goes on. **Reactive** (a milestone, a block, the human handing over): it can be resumed with Resume. **Deliberate** (context degradation): the session is retired; continue from this note, and never resume it.
- **Ticket** is the ticket the work is on, which holds its Scope and Done When; `None` means the work has none.
- **Action Required** is the first thing the receiver does; Next Actions holds the rest.
- **Status / Summary** is where the work stands. **Partially Complete** leaves work in Next Actions; **Deadlock** means the work cannot go on without something the writer could not get, which Next Actions names.
- **Verified Path**: a ticked line is proven and need not be proven again; an unticked line is a dead end or a blocker found, not a step still to take. The section is optional, and left out it claims nothing.
- **Unverified / Uncertain** is what the writer assumed without checking or is unsure of; the receiver checks a line before relying on it. `None` states that everything else in the note was checked.
- **Next Actions** are the receiver's steps, in order, each with how to tell it succeeded.
