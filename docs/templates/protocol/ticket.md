# Ticket Template

The required content of [the ticket](../../safechord.kdd.practice.md#the-ticket): the body of its GitHub issue.

```markdown
## Background
[Why is this needed? What does the current state look like?]

## Scope
- In: [what this ticket touches]
- Out: [what is explicitly excluded]

## Done When
- [ ] [verifiable condition 1]
- [ ] [verifiable condition 2]
- [ ] Reconciliation complete (or confirmed with the human that none is needed)

## References
- [the pages, drafts or tickets this one builds on]
```

- **Background** is why the work is needed and the state it starts from, as of when the ticket was written or last checked for freshness. A decision recorded there with its reason binds the work as the Scope does.
- **Scope** bounds the work: **In** is what it changes, **Out** what it leaves alone though it might look included. Work outside In is not done under this ticket.
- **Done When** is what the result is checked against before it lands. A ticked item has been verified, not only worked on.
- **The reconciliation item** is ticked after the work lands, as the flow's last step; it is not a condition the change itself can show. Ticked as not needed, it records that the human confirmed so.
- **References** are what the ticket builds on, read before the work starts.
