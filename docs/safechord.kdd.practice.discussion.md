---
title: 'KDD 2.0: Discussion'
status: active
archetype: script
---

# KDD 2.0 Practice: Discussion

> **Type**: Script (a mode page: implements the [practice](safechord.kdd.practice.md) §2)
> **Focus**: Work the human and one agent do together in conversation, and the changes to `Docs/` and the harness that come out of it.
> **Constraint**: Nothing every mode shares: it is in the practice. No rule for writing a Docs page (`Docs/.ai-rules.md` §3) or for committing through the harness (the workspace `CLAUDE.md` §5).

## Mode Contract {#mode-contract}

- **Work**: work with no ticket yet, and work that lands in `Docs/` or the harness, with a ticket or without one. Picking up a ticket whose change lands in a code repository through a PR moves the session to [Development](safechord.kdd.practice.development.md); starting a phase of a release moves it to [Delivery](safechord.kdd.practice.delivery.md).
- **Human**: present throughout, deciding together. A change is reviewed through the conversation or the ticket behind it, and the human's agreement there is the sign-off.
- **Seats**: none. Where a template asks for a seat, write `Discussion`.
- **Ends**: when its outcome exists: a ticket opened, a draft written, or a change committed. Work on a ticket ends when the ticket closes.
- **Landing**: committed straight to `main` of `Docs/` or the harness, and pushed. The agent writes to `Docs/` what the conversation decided. A [standing task](safechord.kdd.practice.md#standing-tasks) started from this mode lands as its own page says.
- **Protocols**: the ticket, the commit, the handoff and the draft, as the practice writes them. The draft is this mode's own outcome: forward-looking discussion is recorded there before a ticket is opened.
- **Carried by**: no skill. The conversation is the flow.
