# Draft Template

The required content of [a design draft](../../safechord.kdd.practice.md#protocols).

```markdown
---
title: 'Design Draft: [Topic]'
doc_id: [project id].draft.[slug]
last_updated: 'YYYY-MM-DD'
status: draft
authors: [<the human>, <agent>]
context_scope: [Methodology | Infrastructure | ...]
summary: [one paragraph on what this draft decides]
logical_path: [Project].Draft.[Name]
related_docs: []
archetype: script
doc_version: 0.1.0
---

# Design Draft: [Topic]

## 1. Background
[What is the problem, and what constrains it?]

## 2. Proposed Solution
[The proposal, with mock code or schemas where they help]

## 3. Alternatives Considered
[What else was weighed, and why it lost]

## 4. Trade-offs
[What cost is being accepted]

## 5. Next Steps
1. [ ] [next action]
```

- **`last_updated`** is when the draft last changed; what has landed since may have overtaken it.
- **`authors`** is who wrote the draft as a whole; it does not say who proposed or agreed to any one point in it.
- **Proposed Solution** is what the draft proposes. A draft is no fact's home ([Layers](../../safechord.kdd.practice.md#layers)): where it disagrees with a ticket, a page or a commit, they hold.
- **Alternatives Considered** are the options weighed and rejected, each with why it lost.
- **Trade-offs** are the costs the proposal accepts knowingly.
- **Next Steps** are the actions still open; a ticked box has been done.
