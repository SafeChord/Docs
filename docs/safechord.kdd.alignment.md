---
title: 'KDD 2.0: Internal Alignment'
status: active
archetype: script
---

# KDD 2.0: Internal Alignment

> **Type**: Script (a [standing task](safechord.kdd.practice.md#standing-tasks))
> **Focus**: Keeping the en pages of `Docs/` consistent with each other and with the rules in `Docs/.ai-rules.md`: why the task exists, what it covers, what it takes as right, and how its changes land.
> **Constraint**: No steps, commands, thresholds or tag mechanics. They are in the `align-incremental` and `align-full` skills (`.claude/skills/` in the workspace harness) and in the trigger, `scripts/align-trigger.sh`.

## Why it exists {#why-it-exists}

A ticket's reconciliation updates the pages that ticket touches. Nothing else looks for the other pages that restate a fact it changed, so a fact corrected on one page stays wrong on the others until something goes looking for them.

## Scope {#scope}

- **Page against page, en only.** Alignment compares en pages with each other and with the rules in `Docs/.ai-rules.md`. zh pages trail en and are brought up to date on their own (`Docs/.ai-rules.md` §2.3).
- **Not Docs against the code.** A change in the code makes no Docs commit, so it never starts a run. A run reads the code only to settle a conflict between two pages. A fact stated on a single page and wrong against the code is found by neither run: drift from the code stays with a ticket's reconciliation ([Development](safechord.kdd.practice.development.md)) and with the release ([Delivery](safechord.kdd.practice.delivery.md)).

## Two runs {#two-runs}

The two runs are told apart by what they take as right.

| | Incremental | Full |
| :--- | :--- | :--- |
| **Covers** | The Docs commits since the last aligned commit, and every en page that restates what they changed | Every en page |
| **Takes as right** | The diff, since a ticket or a decision stands behind it | Nothing by default: a newer page is not therefore right |
| **Settles a conflict** | By propagating the diff. A diff that contradicts the decision log or a requirement stops the run, which asks the human. A diff that changes a rule covers every page the rule applies to | By Docs first (a decision still accepted, a requirement, a rule, a changelog entry recording the change), then, for a fact the code owns, by the code as it stands. Every other conflict goes to the human |
| **Runs** | When the human starts it. Once enough Docs commits have accumulated since the last aligned commit (counted, not timed), the session that pushed reminds the human that a run is due, and starts nothing itself: Docs is not always in a state to align, and a page edited ahead of a rewrite still to come would have a state about to change spread to every page that restates it. It runs in the background | When the human asks: the first time, and whenever incremental runs were skipped or have not run for long |

The last aligned commit is the tag `align/last` on the Docs repository.

## Landing {#landing}

A run edits pages that no human looks at one by one, and `main` is what every session reads and what the site deploys. A run therefore lands through a PR from its own branch, and the human's merge is the sign-off. What the run could not settle is listed in the PR for the human to decide.
