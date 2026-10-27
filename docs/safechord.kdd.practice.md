---
title: 'KDD 2.0: Practice'
last_updated: '2026-10-27'
status: active
doc_version: 0.4.0
archetype: practice
code_paths: []
---

# KDD 2.0 Practice

> **Type**: Practice (the base every mode page takes as given)
> **Focus**: The modes, where each kind of fact lives, and the protocols the modes share.
> **Constraint**: No mode's own flow: it is on that mode's page. How a step is carried out lives in the skill or script that runs it. No template's skeleton or field meanings: they are in its file under `docs/templates/protocol/`. The reasons the model took its shape are in the [KDD changelog](safechord.kdd.changelog.md).

> **⚙️ This document is in an adjustment period.** The ticket lifecycle and the protocol templates were introduced in v0.4.0 and have not yet been through a full cycle. Expect rough edges.
>
> **If a template or a step does not fit the work in front of you, say so rather than working around it silently.** A mismatch between this document and what actually happens is a defect in the document until it has been argued otherwise — raise it with the human, and it gets fixed here.
>
> **Do not bump `doc_version` while this notice stands.** The document holds at v0.4.0 until the adjustment period closes. Edits land under `last_updated` alone.

## Modes {#modes}

Agents work in modes, told apart by what the work is. This page is the base every mode page takes as given: a mode page does not restate it, and what else it writes is its own call.

- A **session** is one agent conversation, from its start to its end.
- A **seat** is a role a mode splits its work into. A mode that has seats defines them on its page.

Work that matches no mode below runs on this page alone.

| Mode | Work that moves a session into it | Page |
| :--- | :--- | :--- |
| Development | A code change that lands in a code repository through a branch, a PR and a merge, on a ticket labelled `kdd:forward` or `kdd:spike` | [Development](safechord.kdd.practice.development.md) |
| Delivery | Cutting, validating and promoting a release of a product | [Delivery](safechord.kdd.practice.delivery.md) |
| Operations | Running the deployed system: SRE work on the live platform | [Operations](safechord.kdd.practice.operations.md) (placeholder) |

A mode page either gives a complete flow that a project uses as it is (Development), or gives the concepts and components that a project assembles into its own flow (Delivery). Development looks much the same everywhere up to the merge; delivery rests on each project's infrastructure and carriers, and no two release flows are likely to match.

## Layers {#layers}

Each fact has one home, so that no two files hold conflicting versions of it. Where a restatement disagrees with the home, the home holds and the restatement is fixed. When the home itself looks wrong, stop and ask the human.

The generic files hold what any project working under KDD shares:

| File | Usage |
| :--- | :--- |
| The [introduction](safechord.kdd.introduction.md) and the [changelog](safechord.kdd.changelog.md) | Concepts, and the reasons the model took its shape |
| This page | What every mode shares |
| A mode page | One mode: a complete flow, or the components a project assembles |
| [Internal Alignment](safechord.kdd.alignment.md), [Discovery](safechord.kdd.discovery.md) | Work no mode owns: keeping `Docs/` consistent with itself, and finding the process's leaks across runs |
| The protocol templates (`docs/templates/protocol/`) | Each protocol's skeleton, what its fields mean, and the rules of its artifact |
| Skills and scripts (`.claude/skills/` in the workspace harness) | How a step is carried out: commands, order, parameters |

The custom files hold one project's choices; SafeChord's are the example:

| File | Usage |
| :--- | :--- |
| [SafeZone Delivery](safechord.safezone.delivery.md) | SafeZone's release flow: how it assembles the delivery components, and the skills that carry it |
| The `config.json` beside a skill | The values the skill reads: carriers, models, base branches, limits |
| A repository's `.ai-rules.md` | How that repository applies the KDD pages: its conventions, commands and paths. It points at a page for the flow rather than restating it |
| The workspace `AGENTS.md` | Activation, red lines, workspace facts, the mandatory triggers |

## Protocols {#protocols}

Sessions and agents do not pass their whole context to one another; what passes between them goes through these protocols. How a mode uses each one is on its page.

- [The ticket](templates/protocol/ticket.md): a GitHub issue in the repository the work lands in.
- [The commit](templates/protocol/commit.md): the message of a git commit.
- [The handoff](templates/protocol/handoff.md): a Markdown file in the handoff directory the context file names.
- [The design draft](templates/protocol/draft.md): a Markdown file in the draft directory the context file names, one subdirectory per domain.
