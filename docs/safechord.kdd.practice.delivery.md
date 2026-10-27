---
title: 'KDD 2.0: Delivery'
status: active
archetype: script
---

# KDD 2.0 Practice: Delivery

> **Type**: Script (a mode page: takes the [practice](safechord.kdd.practice.md) as given)
> **Focus**: What every project's delivery holds: how a release passes its gates, how its checks are layered, and what it takes over from Development.
> **Constraint**: Nothing every mode shares: it is in the practice. Nothing one product's release does (its phases, branches, artifacts and the reasons for them): it is on that product's implementation page.

## Mode Contract {#mode-contract}

- **Work**: cutting, validating and promoting a release of a product, as its implementation page lays the phases out. A session moves into this mode when it starts a phase or a route of one. A fix found during a release leaves the run as a ticket of its own, which is [Development](safechord.kdd.practice.development.md)'s.
- **Human**: present throughout, signing off every gate (§1). The implementation page names the gates.
- **Seats**: declared by the implementation page.
- **Ends**: declared by the implementation page.
- **Landing**: declared by the implementation page. What a shipped ticket changed was reconciled by that ticket; a release does not reconcile it again.
- **Protocols**: the commit and the handoff, as the practice writes them. An implementation adds the issues that take a ticket's place for a release, and the record of the checks Development deferred to it (§3).
- **Carried by**: each implementation's validation skills and pipelines, which its page lists.

## Implementations {#implementations}

| Product | Page |
| :--- | :--- |
| SafeZone (App and Deploy) | [SafeZone Delivery](safechord.safezone.delivery.md) |

A page goes up here when a second implementation shows it holds for both.

## 1. The Gate {#the-gate}

A gate is where a release waits for the human's sign-off.

- The agent gathers the evidence and reduces it to a yes or a no. The human makes the call, and makes the checks only a person can, such as looking at the running product.
- Nothing is stamped before the human's explicit yes, given in the session after seeing the findings.
- When a gating check fails, the agent reports it, recommends the forward fix, and the gate ends there.
- The evidence comment the stamp posts is the record of the sign-off. A label or a ticked item is the index a pipeline reads to let the next phase start. The record guards against an omission, not against a deliberate bypass.

## 2. Floor and Focus {#floor-and-focus}

Each validation stage runs in another environment or at a later time, so each one verifies the present.

- **The floor** is the set of checks every stage re-runs.
- **A stage's focus** is what only that stage can prove: on a candidate, behaviour that needs no time; on the persistent environment, the real platform; over a soak, what only time shows.
- A check that becomes deterministic moves into the script the stage runs; the file that lists the check keeps what it guards and why.

## 3. What Development Hands Over {#what-development-hands-over}

- A check that can run only once a release is cut or deployed is not run in its ticket. Development lists it on the PR ([the pull request template](templates/protocol/development/pull-request.md)) and, at Solidification, enters it in the release's record of held checks, which the implementation page defines. The release runs it where its environment exists.
- A fix found during a release is a ticket of its own, labelled for Development wherever it was found; the release takes it in through the normal flow.
