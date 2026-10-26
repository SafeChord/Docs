# Commit Template

The required content of [the commit](../../safechord.kdd.practice.md#the-commit) message, in strict [Conventional Commits](https://www.conventionalcommits.org/).

```text
<type>(<scope>): <subject> (50 chars max)

[Body: Why was this change needed?]
Explain the motivation and logic. Focus on "Why" rather than "How."
Describe the impact on project architecture or long-term decisions.

Context: [Ticket ID, or link to the Blueprint]
Impact: [Specific impact on API contracts or infra]
Test: [Verification executed: the command and its result]
Agent: [the seat, with a qualifier where its mode page defines one, or the mode where it has no seats]
Legacy: [Pending issues for the next agent]
```

- **Context** is what the change traces back to: its ticket, or what else decided it, such as a blueprint or a draft.
- **Impact** is what the change affects outside its own files: an API contract, the infrastructure, another repository. `none` states that it affects nothing outside them.
- **Test** is the verification actually run, as a command and its result, which a reader can run again. `none` with its reason means nothing was run.
- **Agent** is the seat, with its qualifier, or the mode the change was made under; the page that defines it says what that seat or qualifier may change.
- **Legacy** is what the change leaves open for whoever continues. `none` means it leaves nothing open.
