---
title: "Policy: [Infrastructure Component Name]"
doc_id: safechord.chorde.[component]
doc_version: [Document Version]
app_version: [Target Platform Version]
status: draft
authors:
  - [Author Name]
last_updated: "YYYY-MM-DD"
summary: "[One sentence: what infrastructure concern this addresses and the core design constraint.]"
keywords:
  - [keyword1]
  - [keyword2]
logical_path: "SafeChord.Chorde.[Component]"
related_docs:
  - "[Related Infra/Platform Doc]"
parent_doc: "[Parent Doc ID]"
archetype: brain
code_paths:
  - "Chorde/gitops/k3han/manifests/[component]"
tech_stack:
  - [Technology]
---

# [Component Name] (Brain)

> Inherits from `archetype.brain.md`. Specialized for declarative infrastructure
> components managed via GitOps.
>
> **Key distinction from App-layer blueprints**: In declarative infrastructure,
> manifests themselves express desired state. This document defines the
> **design constraints and architectural rationale** — the red walls within
> which manifests must operate. It does NOT duplicate manifest values.

---

## 1. Design Constraints (Red Walls)
*(Required)*
Hard boundaries that all implementation (manifests, configs) must satisfy.
Express as targets or ceilings, not current values.

*   **[Constraint Category]**: [Constraint statement with threshold]
*   **[Constraint Category]**: [Constraint statement with threshold]

> Example: "Cross-border latency must remain below 100ms",
> "Monthly cost must not exceed NT$800"

## 2. Strategy / Policy Definition
*(Required)*
The architectural approach chosen to satisfy the constraints above.
Explain the **Why** and **How** at a design level.

### [Strategy Aspect A]
*   **Approach**: [What pattern or architecture was chosen]
*   **Rationale**: [Why this satisfies the constraints]

### [Strategy Aspect B]
*   **Approach**: [What pattern or architecture was chosen]
*   **Rationale**: [Why this satisfies the constraints]

## 3. Reference Snapshots
*(Optional — point-in-time observations, NOT SSOT)*
Measured values or configuration summaries that validated the design constraints
at a specific point in time. These will drift; always verify against the
codebase or monitoring tools for current state.

> Label clearly: "as of vX.Y", "verified YYYY-MM-DD"

| Observation | Value | Constraint Validated |
| :--- | :--- | :--- |
| [What was measured] | [Measured value] | [Which red wall this proves] |

> *Current values live in manifests under `code_paths`, or in monitoring dashboards.*

## 4. Trade-offs & Consequences
*(Recommended)*

| Pros | Cons | Mitigation |
| :--- | :--- | :--- |
| [Gain from this strategy] | [Cost or risk introduced] | [How we manage the downside] |

## 5. References
*(Optional)*
*   **Manifests**: `code_paths` in frontmatter
*   **Related Policies**: [Links to sibling infra docs]
*   **External**: [Vendor docs, architecture references]
