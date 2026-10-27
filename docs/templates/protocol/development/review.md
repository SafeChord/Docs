# Review Template

The `review` handoff between the seats ([development §2](../../../safechord.kdd.practice.development.md#handoffs-between-the-seats)), written by the Settler and appended every round. Earlier rounds are neither rewritten nor deleted, and a finding keeps its number (`R<round>-<n>`) for the life of the ticket.

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
