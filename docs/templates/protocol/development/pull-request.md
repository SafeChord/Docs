# Pull Request Template

The body of the pull request of a [development](../../../safechord.kdd.practice.development.md) ticket. The PR is where the human reviews and merges: the Settler opens it once review passes, or for `exec:settler` work once implementation is done.

```markdown
[exec:settler only, the header:]
> ⚠️ **Executed by the Settler.** No independent agent review took place; the executor and
> reviewer are the same seat. The human reviewer is the only independent check, and merging
> transfers accountability to them.

Ticket: #[issue_no]

## Summary
[The smallest view that makes the change clear]

## Evidence
- [A contrast per behavior: what failed before and passes now]
- [The regression run, one line]

## Merge Danger: [low / medium / high]
[What merging sets off, what a revert would not undo, who is hit if this is wrong]
Deferred to release: [the check]

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
- **Deferred to release** is a check that can run only once the release is cut or deployed; Solidification hands it to the release ([Delivery §3](../../../safechord.kdd.practice.delivery.md#what-development-hands-over)).
- **Decisions made in review** are what was decided without the human, Minor findings left open included; the human can overturn each before merging.
- **Follow-up tickets** are work found outside this ticket; merging does not wait for them.

**Sorting what was left unverified.** The PR carries only what the human must weigh at merge. Before writing it, the Settler takes everything left unverified (the review rounds' "Not checked" lines, the delivery handoff's "Unverified / Uncertain", and under `exec:settler` what it did not verify itself) and sorts each item by the harm it can do:

- no real harm: dropped
- harm, and it can be checked within the ticket: checked now
- harm, and it cannot be checked before merge: stated under **Merge Danger**. A check that can run only once the release is cut or deployed is also listed as Deferred to release
- no danger at merge, but worth doing: a follow-up ticket

An item whose harm would not land at merge becomes a ticket or is dropped. The PR carries no list of what was not checked.

**Merge Danger** is graded by what it costs if the change is wrong:

| Level | If this is wrong | The human |
| :--- | :--- | :--- |
| `low` | A revert puts everything back | Merges |
| `medium` | A revert puts it back, but someone or something was hit first | Knows where to look after merge |
| `high` | Something a revert does not undo, or a manual step before or after merge | Reads the description before merging |

A check deferred to release does not raise the level: the release's gates hold it.

**SSOT feedback** reports where the SSOT left room. A Gap is a choice the SSOT left open that something outside the service, an operator or the deployment can observe; a choice visible only inside the code is a decision. A requirement test added or modified after pre-work changes the precise form of a promise. Ticking the box means reconciliation writes every entry into `Docs/`; to write only some, the human says which in a PR comment, and the comment wins.

How to fill each section (the forms for Summary and Evidence, the floors for Merge Danger, the prose rules) is in the `pr` skill (`.claude/skills/pr/SKILL.md` in the workspace harness).
