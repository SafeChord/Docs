# Delivery Handoff Template

The `delivery` handoff between the seats ([development §2](../../../safechord.kdd.practice.development.md#handoffs-between-the-seats)), written by the Pioneer and updated in place every round. It is the [handoff template](../handoff.md) with two more header lines and two more sections, given here; everything else is as that template writes it.

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
- **Raised for the Settler** holds what the Pioneer could not settle inside the ticket; the Settler decides each item ([development §3.2](../../../safechord.kdd.practice.development.md#32-handling-review-findings)). `None` means the Pioneer found nothing to raise.
