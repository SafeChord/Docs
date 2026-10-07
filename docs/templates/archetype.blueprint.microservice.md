---
title: "Service: [Service Name]"
doc_id: safechord.safezone.service.[name]
doc_version: [Document Version — bump on every edit]
app_version: [First application version this revision of the spec applies to]
status: draft
authors:
  - [Author Name]
last_updated: "YYYY-MM-DD"
summary: "[One sentence: core role, data flow position, key characteristic]"
keywords:
  - [keyword1]
  - [keyword2]
logical_path: "SafeChord.SafeZone.Service.[Name]"
related_docs:
  - "safechord.safezone.service.standards.md"
  - "safechord.safezone.decisions.md"
parent_doc: "safechord.safezone"
archetype: blueprint
code_paths:
  - "SafeZone/services/[service-name]"
---

# [Service Name] (Service Blueprint)

> **Type**: Blueprint (Service)
> **Focus**: What this service promises to the rest of the system, and what it relies on.
> **Constraint**: Current state only. No file structure, libraries, or implementation
> (codebase). No field-level shape (contract files). No reasons
> ([decision log](../safechord.safezone.decisions.md)). No history
> ([changelog](../safechord.safezone.changelog.md)).

> [!IMPORTANT]
> **Template Cleanup**: Delete every helper instruction and `*(Required)*` marker once
> this blueprint is populated. Fix the two relative links above to sibling links.

## 1. Responsibility
*(Required)*
*   **Role**: [Producer / Consumer / Aggregator / Gateway]
*   **Core Objective**: [What problem does this service solve, in one or two sentences?]

## 2. Requirements
*(Required)*

Each requirement is a promise other parts of the system rely on. A test that enforces
one carries its ID. Requirements shared by every service live in the
[service standards](../safechord.safezone.service.standards.md) and are not repeated here.

Write one requirement per promise:

*   **ID**: `[PREFIX]-R[n]`. IDs are stable: never renumber, never reuse a retired ID.
*   **Sentence**: one normative sentence with `SHALL`, stating a result someone outside
    the service can observe.
*   **Scenarios**: one or more Given/When/Then cases. Each is the seed of a test.

Check the grain in both directions. Too coarse: a test cannot be written from it without
asking the author. Too fine: of two reasonable implementations, only one would pass.

### [PREFIX]-R1: [Short name]
The [service] SHALL [observable result].

#### Scenario: [case]
- GIVEN [state]
- WHEN [trigger]
- THEN [observable outcome]

## 3. Dependencies
*(Required)*

List only what this service actually connects to: a topic, a table, an API it serves or
calls. Do not name the service at the other end of a topic or a table.

| Channel | Direction | Contract | Also assumed |
| :--- | :--- | :--- | :--- |
| [Topic / table / API] | [Serves / Calls / Consumes / Produces / Reads / Writes] | [Path to the contract file] | [What the contract file cannot express, or "None."] |

*   **Contract** points at a file, never restates it. A contract used from more than one
    language must be a language-neutral file (see the service standards). Where none
    exists yet, say so and name the ticket that tracks it.
*   **Also assumed** carries only semantics the contract file cannot express, such as
    ordering or partitioning.
